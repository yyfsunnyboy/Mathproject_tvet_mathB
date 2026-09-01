"""Export workbook validation and backup manifest for db_maintenance Excel backups."""

from __future__ import annotations

import io
import re
import sqlite3
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from sqlalchemy import inspect, text

from core.backup.backup_registry import (
    get_account_ref_checks,
    get_core_table_names,
    get_table_spec,
)

BACKUP_FORMAT_VERSION = 2
SUPPORTED_BACKUP_FORMAT_VERSION = 2
APP_SCHEMA_VERSION = "v9.0"
MANIFEST_SHEET = "__manifest__"
METADATA_SHEET_PREFIX = "__"
COLUMNS_DELIM = "|"

# Minimum columns that must appear in exported sheets (ORM-aligned).
TABLE_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "users": ("id", "username", "role", "real_name"),
    "classes": ("id", "name", "teacher_id"),
    "class_students": ("class_id", "student_id", "seat_no"),
    "practice_attempts": (
        "id",
        "student_id",
        "class_id",
        "skill_id",
        "problem_type_id",
        "question_uid",
        "question_text",
        "user_answer",
        "expected_answer",
        "is_correct",
        "source",
        "session_id",
        "difficulty",
        "created_at",
    ),
}


class ExportValidationError(Exception):
    """Raised when an export workbook fails post-write validation."""

    def __init__(self, message: str, *, report: dict[str, Any] | None = None):
        super().__init__(message)
        self.report = report or {}


@dataclass
class ValidationReport:
    valid: bool = True
    missing_sheets: list[str] = field(default_factory=list)
    unexpected_sheets: list[str] = field(default_factory=list)
    column_errors: dict[str, list[str]] = field(default_factory=dict)
    row_count_errors: dict[str, dict[str, int]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    table_count: int = 0
    total_rows: int = 0
    integrity_check: str | None = None
    foreign_key_check_rows: int | None = None
    legacy_backup: bool = False
    manifest_present: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "missing_sheets": list(self.missing_sheets),
            "unexpected_sheets": list(self.unexpected_sheets),
            "column_errors": dict(self.column_errors),
            "row_count_errors": dict(self.row_count_errors),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "table_count": self.table_count,
            "total_rows": self.total_rows,
            "integrity_check": self.integrity_check,
            "foreign_key_check_rows": self.foreign_key_check_rows,
            "legacy_backup": self.legacy_backup,
            "manifest_present": self.manifest_present,
        }

    def primary_error(self) -> str:
        if self.errors:
            return self.errors[0]
        if self.missing_sheets:
            return f"缺少 sheet：{self.missing_sheets[0]}"
        if self.column_errors:
            table, cols = next(iter(self.column_errors.items()))
            return f"{table} 缺少欄位：{', '.join(cols)}"
        if self.row_count_errors:
            table, counts = next(iter(self.row_count_errors.items()))
            return (
                f"{table} 筆數不一致：DB={counts.get('expected')} "
                f"Excel={counts.get('actual')}"
            )
        return "備份驗證失敗"


def is_metadata_sheet(sheet_name: str) -> bool:
    return str(sheet_name or "").strip().startswith(METADATA_SHEET_PREFIX)


def safe_sheet_name(name: str) -> str:
    name = str(name)
    name = re.sub(r"[\[\]\:\*\?\/\\]", "_", name)
    return name[:31]


def count_dataframe_rows(df: pd.DataFrame) -> int:
    if df is None or df.empty:
        return 0
    work = df.copy()
    work = work.dropna(how="all")
    if work.empty:
        return 0
    return int(len(work))


def normalize_column_names(columns) -> list[str]:
    return [str(c).strip() for c in columns]


def get_model_columns(table_name: str) -> list[str]:
    from core.data_importer import get_model_mapping

    mapping = get_model_mapping()
    model = mapping.get(table_name)
    if model is None:
        return []
    return [col.name for col in model.__table__.columns]


def get_expected_columns(table_name: str, engine) -> list[str]:
    model_cols = get_model_columns(table_name)
    if model_cols:
        return model_cols
    try:
        inspector = inspect(engine)
        return [c["name"] for c in inspector.get_columns(table_name)]
    except Exception:
        return []


def ensure_dataframe_columns(table_name: str, df: pd.DataFrame, engine) -> pd.DataFrame:
    if df is not None and len(df.columns) > 0:
        return df
    cols = get_expected_columns(table_name, engine)
    return pd.DataFrame(columns=cols)


def check_source_db_integrity(engine) -> tuple[str, int, list[str]]:
    warnings: list[str] = []
    integrity = "unknown"
    fk_rows = -1
    try:
        url = str(engine.url)
        if not url.startswith("sqlite"):
            return integrity, fk_rows, warnings
        db_path = engine.url.database
        if not db_path or db_path == ":memory:":
            return integrity, fk_rows, warnings
        conn = sqlite3.connect(db_path)
        try:
            integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
            if integrity != "ok":
                warnings.append(f"source integrity_check={integrity}")
            fk_rows = len(conn.execute("PRAGMA foreign_key_check").fetchall())
            if fk_rows:
                warnings.append(f"source foreign_key_check rows={fk_rows}")
        finally:
            conn.close()
    except Exception as exc:
        warnings.append(f"source pragma check failed: {exc}")
    return integrity, fk_rows, warnings


def collect_source_counts(engine, table_names: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in table_names:
        qtable = f'"{table}"'
        try:
            with engine.connect() as conn:
                row = conn.execute(text(f"SELECT COUNT(*) FROM {qtable}")).fetchone()
                counts[table] = int(row[0] if row else 0)
        except Exception:
            counts[table] = 0
    return counts


def build_manifest_dataframe(
    *,
    export_mode: str,
    expected_tables: list[str],
    source_counts: dict[str, int],
    exported_frames: dict[str, pd.DataFrame],
    source_database_name: str,
    integrity_check: str | None,
    foreign_key_check_rows: int | None,
) -> pd.DataFrame:
    meta_rows = [
        {"section": "meta", "key": "backup_format_version", "value": str(BACKUP_FORMAT_VERSION)},
        {"section": "meta", "key": "export_mode", "value": export_mode},
        {
            "section": "meta",
            "key": "created_at",
            "value": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
        {"section": "meta", "key": "app_schema_version", "value": APP_SCHEMA_VERSION},
        {"section": "meta", "key": "table_count", "value": str(len(expected_tables))},
        {"section": "meta", "key": "source_database_name", "value": source_database_name},
        {
            "section": "meta",
            "key": "integrity_check",
            "value": str(integrity_check or "unknown"),
        },
        {
            "section": "meta",
            "key": "foreign_key_check_rows",
            "value": str(foreign_key_check_rows if foreign_key_check_rows is not None else -1),
        },
    ]
    table_rows: list[dict[str, Any]] = []
    for table_name in expected_tables:
        df = exported_frames.get(table_name, pd.DataFrame())
        cols = normalize_column_names(df.columns)
        spec = get_table_spec(table_name)
        table_rows.append(
            {
                "section": "table",
                "table_name": table_name,
                "row_count": str(source_counts.get(table_name, count_dataframe_rows(df))),
                "column_count": str(len(cols)),
                "columns": COLUMNS_DELIM.join(cols),
                "exported": "true",
                "required": "true" if spec and spec.required else "false",
                "restore_order": str(spec.restore_order if spec else ""),
            }
        )
    return pd.DataFrame(meta_rows + table_rows)


def parse_manifest_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    manifest: dict[str, Any] = {"tables": {}}
    if df is None or df.empty:
        return manifest
    work = df.copy()
    work.columns = [str(c).strip().lower() for c in work.columns]
    for _, row in work.iterrows():
        section = str(row.get("section", "")).strip().lower()
        if section == "meta":
            key = str(row.get("key", "")).strip()
            if key:
                manifest[key] = row.get("value")
        elif section == "table":
            name = str(row.get("table_name", "")).strip()
            if not name:
                continue
            manifest["tables"][name] = {
                "row_count": row.get("row_count"),
                "column_count": row.get("column_count"),
                "columns": row.get("columns"),
                "exported": row.get("exported"),
                "required": row.get("required"),
                "restore_order": row.get("restore_order"),
            }
    return manifest


def parse_manifest_from_workbook(sheets: dict[str, pd.DataFrame]) -> dict[str, Any]:
    for key, df in sheets.items():
        if str(key).strip() == MANIFEST_SHEET:
            return parse_manifest_dataframe(df)
    return {}


def check_manifest_import_allowed(manifest: dict[str, Any]) -> tuple[bool, str]:
    if not manifest:
        return True, ""
    raw_version = manifest.get("backup_format_version")
    try:
        version = int(str(raw_version).strip())
    except (TypeError, ValueError):
        return True, ""
    if version > SUPPORTED_BACKUP_FORMAT_VERSION:
        return (
            False,
            f"此備份由較新版本系統產生（backup_format_version={version}），"
            f"目前程式最高支援 {SUPPORTED_BACKUP_FORMAT_VERSION}，請先更新程式。",
        )
    return True, ""


def _validate_required_columns(
    table_name: str,
    actual_columns: list[str],
    report: ValidationReport,
) -> None:
    required = TABLE_REQUIRED_COLUMNS.get(table_name)
    if not required:
        return
    actual_set = set(actual_columns)
    missing = [col for col in required if col not in actual_set]
    if missing:
        report.column_errors[table_name] = missing
        report.errors.append(f"{table_name} 缺少欄位：{', '.join(missing)}")
        report.valid = False


def _validate_fk_sanity(frames: dict[str, pd.DataFrame], report: ValidationReport) -> None:
    users_df = frames.get("users")
    classes_df = frames.get("classes")
    user_ids: set[int] = set()
    class_ids: set[int] = set()
    if users_df is not None and "id" in users_df.columns:
        user_ids = set(pd.to_numeric(users_df["id"], errors="coerce").dropna().astype(int).tolist())
    if classes_df is not None and "id" in classes_df.columns:
        class_ids = set(pd.to_numeric(classes_df["id"], errors="coerce").dropna().astype(int).tolist())

    for table, fk_col, parent_table, parent_col, nullable_ok in get_account_ref_checks():
        df = frames.get(table)
        if df is None or fk_col not in df.columns:
            continue
        if parent_table == "users" and parent_col == "id":
            parent_ids = user_ids
        elif parent_table == "classes" and parent_col == "id":
            parent_ids = class_ids
        else:
            parent_df = frames.get(parent_table)
            if parent_df is None or parent_col not in parent_df.columns:
                continue
            parent_ids = set(
                pd.to_numeric(parent_df[parent_col], errors="coerce").dropna().astype(int).tolist()
            )
        values = pd.to_numeric(df[fk_col], errors="coerce")
        if nullable_ok:
            values = values.dropna()
        else:
            values = values.dropna()
        orphan = sorted({int(v) for v in values.tolist() if int(v) not in parent_ids})
        if orphan:
            preview = orphan[:5]
            report.warnings.append(
                f"FK orphan {table}.{fk_col} -> {parent_table}.{parent_col}: {preview}"
                + ("..." if len(orphan) > 5 else "")
            )


def validate_export_workbook(
    workbook_source: str | Path | bytes | io.BytesIO,
    *,
    expected_tables: list[str],
    source_counts: dict[str, int],
    export_mode: str,
    require_manifest: bool = True,
) -> ValidationReport:
    report = ValidationReport()
    if isinstance(workbook_source, (bytes, bytearray)):
        workbook_source = io.BytesIO(workbook_source)
    sheets = pd.read_excel(workbook_source, sheet_name=None, engine="openpyxl")
    actual_sheet_names = [str(name).strip() for name in sheets.keys()]
    actual_data_sheets = [name for name in actual_sheet_names if not is_metadata_sheet(name)]
    report.manifest_present = MANIFEST_SHEET in actual_sheet_names
    report.legacy_backup = not report.manifest_present

    if require_manifest and not report.manifest_present:
        report.valid = False
        report.errors.append("缺少 __manifest__ sheet")
    elif report.manifest_present:
        manifest = parse_manifest_from_workbook(sheets)
        raw_version = manifest.get("backup_format_version")
        if raw_version is not None:
            try:
                if int(str(raw_version)) != BACKUP_FORMAT_VERSION:
                    report.warnings.append(
                        f"manifest backup_format_version={raw_version} "
                        f"(expected {BACKUP_FORMAT_VERSION})"
                    )
            except ValueError:
                report.warnings.append(f"manifest backup_format_version invalid: {raw_version}")

    expected_set = set(expected_tables)
    actual_set = set(actual_data_sheets)
    report.missing_sheets = sorted(expected_set - actual_set)
    if report.missing_sheets:
        report.valid = False
        report.errors.append(f"缺少 sheet：{', '.join(report.missing_sheets)}")

    allowed_extra = {MANIFEST_SHEET}
    if export_mode == "core":
        unexpected = sorted(actual_set - expected_set)
    else:
        unexpected = sorted(actual_set - expected_set)
    report.unexpected_sheets = [name for name in unexpected if name not in allowed_extra]
    if export_mode == "core" and report.unexpected_sheets:
        report.warnings.append(f"core export unexpected sheets: {', '.join(report.unexpected_sheets)}")

    total_rows = 0
    for table_name in expected_tables:
        sheet_key = None
        for candidate in (table_name, safe_sheet_name(table_name)):
            if candidate in sheets:
                sheet_key = candidate
                break
        if sheet_key is None:
            continue
        df = sheets[sheet_key]
        actual_columns = normalize_column_names(df.columns)
        _validate_required_columns(table_name, actual_columns, report)
        actual_rows = count_dataframe_rows(df)
        expected_rows = int(source_counts.get(table_name, actual_rows))
        total_rows += actual_rows
        if actual_rows != expected_rows:
            report.row_count_errors[table_name] = {
                "expected": expected_rows,
                "actual": actual_rows,
            }
            report.valid = False
            report.errors.append(
                f"{table_name} 筆數不一致：DB={expected_rows} Excel={actual_rows}"
            )

    report.table_count = len(expected_tables)
    report.total_rows = total_rows
    _validate_fk_sanity({name: sheets.get(name, sheets.get(safe_sheet_name(name), pd.DataFrame())) for name in expected_tables}, report)
    return report


def validate_legacy_workbook_structure(
    workbook_source: str | Path | bytes | io.BytesIO,
    *,
    expected_tables: list[str],
    source_counts: dict[str, int] | None = None,
) -> ValidationReport:
    """Structural validation for pre-manifest backups."""
    return validate_export_workbook(
        workbook_source,
        expected_tables=expected_tables,
        source_counts=source_counts or {},
        export_mode="core",
        require_manifest=False,
    )


def write_workbook_bytes(
    frames: dict[str, pd.DataFrame],
    manifest_df: pd.DataFrame,
) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for table_name, df in frames.items():
            sheet = safe_sheet_name(table_name)
            df.to_excel(writer, sheet_name=sheet, index=False)
        manifest_df.to_excel(writer, sheet_name=MANIFEST_SHEET, index=False)
    buffer.seek(0)
    return buffer.getvalue()


def build_and_validate_export(
    *,
    mode: str,
    engine,
    frames: dict[str, pd.DataFrame],
    expected_tables: list[str],
    source_counts: dict[str, int],
    source_database_name: str,
    logger: Callable[..., Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    integrity_check, fk_rows, pragma_warnings = check_source_db_integrity(engine)
    for note in pragma_warnings:
        if logger:
            logger.warning(note)

    manifest_df = build_manifest_dataframe(
        export_mode=mode,
        expected_tables=expected_tables,
        source_counts=source_counts,
        exported_frames=frames,
        source_database_name=source_database_name,
        integrity_check=integrity_check,
        foreign_key_check_rows=fk_rows,
    )
    payload = write_workbook_bytes(frames, manifest_df)
    report = validate_export_workbook(
        payload,
        expected_tables=expected_tables,
        source_counts=source_counts,
        export_mode=mode,
        require_manifest=True,
    )
    report.integrity_check = integrity_check
    report.foreign_key_check_rows = fk_rows
    for note in pragma_warnings:
        report.warnings.append(note)

    if integrity_check not in (None, "ok", "unknown"):
        report.valid = False
        report.errors.append(f"source integrity_check={integrity_check}")

    if not report.valid:
        debug_path = None
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_path = reports_dir / f"backup_validation_failed_{stamp}.xlsx"
            debug_path.write_bytes(payload)
            report.warnings.append(f"debug artifact: {debug_path}")
        except Exception:
            pass
        raise ExportValidationError(report.primary_error(), report=report.to_dict())

    summary = {
        "table_count": report.table_count,
        "total_rows": report.total_rows,
        "integrity_check": integrity_check,
        "foreign_key_check_rows": fk_rows,
        "warnings": report.warnings,
    }
    if logger:
        logger.info(
            "INFO: export validation passed tables=%s rows=%s integrity=%s",
            summary["table_count"],
            summary["total_rows"],
            integrity_check,
        )
    return payload, summary
