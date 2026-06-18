"""Read-only Gencode status query helpers for admin views."""

from __future__ import annotations

import sqlite3
import json
import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]

NOT_CREATED_STATUS: dict[str, object] = {
    "status": "not_created",
    "component_id": None,
    "textbook_example_id": None,
    "presentation_mode": None,
    "problem_type_id": None,
    "has_payload": False,
    "error_log": None,
    "updated_at": None,
}

GENCODE_STATUS_LABELS: dict[str, str] = {
    "not_created": "未建立",
    "generating": "生成中",
    "draft_written": "草稿已寫入",
    "smoke_passed": "Smoke 通過",
    "verified": "已驗證",
    "failed": "失敗",
    "pending": "pending",
    "usable": "usable",
}

_STATUS_PRIORITY: dict[str, int] = {
    "not_created": 0,
    "pending": 1,
    "usable": 2,
    "generating": 3,
    "failed": 4,
    "draft_written": 5,
    "smoke_passed": 6,
    "verified": 7,
}


def format_gencode_status_label(status: str) -> str:
    return GENCODE_STATUS_LABELS.get(str(status or "").strip(), str(status or "").strip() or "未建立")


def _tracker_table_exists(conn: sqlite3.Connection) -> bool:
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='gencode_component_tracker'"
        ).fetchone()
        return row is not None
    except Exception:
        return False


def _row_value(row: Any, key: str, index: int) -> Any:
    if hasattr(row, "keys"):
        return row[key]
    return row[index]


def _normalize_example_ids(textbook_example_ids: list[int]) -> list[int]:
    normalized: list[int] = []
    seen: set[int] = set()
    for raw_id in textbook_example_ids:
        if isinstance(raw_id, bool) or not isinstance(raw_id, int):
            continue
        if raw_id in seen:
            continue
        seen.add(raw_id)
        normalized.append(raw_id)
    return sorted(normalized)


def _extract_payload_summary(payload_raw: Any) -> dict[str, object]:
    if payload_raw is None or str(payload_raw).strip() == "":
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    try:
        payload = json.loads(str(payload_raw))
    except Exception:
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    if not isinstance(payload, dict):
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    return {
        "presentation_mode": (
            payload.get("presentation_mode")
            or metadata.get("presentation_mode")
            or payload.get("mode")
        ),
        "problem_type_id": (
            payload.get("problem_type_id")
            or metadata.get("problem_type_id")
            or payload.get("problem_type")
        ),
    }


def get_gencode_status_for_examples(
    conn: sqlite3.Connection,
    textbook_example_ids: list[int],
) -> dict[int, dict[str, object]]:
    """Read tracker rows for textbook examples without mutating the database."""
    example_ids = _normalize_example_ids(textbook_example_ids)
    result: dict[int, dict[str, object]] = {
        example_id: dict(NOT_CREATED_STATUS) for example_id in example_ids
    }
    if not example_ids or not _tracker_table_exists(conn):
        return result

    placeholders = ",".join("?" for _ in example_ids)
    rows = conn.execute(
        f"""
        SELECT textbook_example_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE textbook_example_id IN ({placeholders})
        ORDER BY textbook_example_id ASC, component_id ASC
        """,
        example_ids,
    ).fetchall()

    for row in rows:
        example_id = int(_row_value(row, "textbook_example_id", 0))
        payload_raw = _row_value(row, "induced_spec_payload", 3)
        payload_summary = _extract_payload_summary(payload_raw)
        result[example_id] = {
            "status": str(_row_value(row, "gencode_status", 2)),
            "component_id": str(_row_value(row, "component_id", 1)),
            "textbook_example_id": example_id,
            **payload_summary,
            "has_payload": payload_raw is not None and str(payload_raw).strip() != "",
            "error_log": _row_value(row, "gencode_error_log", 4),
            "updated_at": _row_value(row, "updated_at", 5),
        }
    return result


def _resolve_base_path(base_dir: str, project_root: str | Path | None) -> Path:
    base_path = Path(str(base_dir or "").strip())
    if base_path.is_absolute():
        return base_path
    if project_root is not None and str(project_root).strip():
        return Path(project_root) / base_path
    return PROJECT_ROOT / base_path


def inspect_gencode_files(
    *,
    skill_id: str,
    component_id: str | None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> dict[str, object]:
    """Read-only filesystem probes for dryrun and production component artifacts."""
    skill_key = str(skill_id or "").strip()
    component_key = str(component_id or "").strip()

    dryrun_root = _resolve_base_path(dryrun_base_dir, project_root)
    production_root = _resolve_base_path(production_base_dir, project_root)

    dryrun_component_dir = (
        dryrun_root / skill_key / "components" / component_key if component_key else None
    )
    production_component_dir = (
        production_root / skill_key / "components" / component_key if component_key else None
    )

    return {
        "dryrun_component_exists": bool(dryrun_component_dir and dryrun_component_dir.is_dir()),
        "dryrun_generate_exists": bool(
            dryrun_component_dir and (dryrun_component_dir / "generate.py").is_file()
        ),
        "dryrun_manifest_exists": (dryrun_root / skill_key / "component_manifest.json").is_file(),
        "production_component_exists": bool(
            production_component_dir and production_component_dir.is_dir()
        ),
        "production_generate_exists": bool(
            production_component_dir and (production_component_dir / "generate.py").is_file()
        ),
        "production_manifest_exists": (
            production_root / skill_key / "component_manifest.json"
        ).is_file(),
    }


def inspect_skill_production_files(
    *,
    skill_id: str,
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> dict[str, object]:
    """Read-only skill-level production probes for admin status summaries."""
    skill_key = str(skill_id or "").strip()
    root = Path(project_root) if project_root is not None and str(project_root).strip() else PROJECT_ROOT
    wrapper_path = root / "skills" / f"{skill_key}.py"
    v3_skill_dir = _resolve_base_path(production_base_dir, project_root) / skill_key
    components_dir = v3_skill_dir / "components"
    generator_specs_count = 0
    production_component_count = 0

    if components_dir.is_dir():
        production_component_count = sum(
            1 for component_dir in components_dir.iterdir()
            if component_dir.is_dir() and (component_dir / "generate.py").is_file()
        )

    init_path = v3_skill_dir / "__init__.py"
    if init_path.is_file():
        try:
            text = init_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text)
            for node in tree.body:
                if (
                    isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "GENERATOR_SPECS" for target in node.targets)
                    and isinstance(node.value, (ast.List, ast.Tuple))
                ):
                    generator_specs_count = len(node.value.elts)
                    break
        except Exception:
            generator_specs_count = 0

    return {
        "production_wrapper_exists": wrapper_path.is_file(),
        "v3_package_exists": v3_skill_dir.is_dir() and init_path.is_file(),
        "generator_specs_count": generator_specs_count,
        "production_component_count": production_component_count,
    }


def _bool_label(value: bool) -> str:
    return "是" if value else "否"


def build_admin_example_gencode_status_view(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[str, object]:
    tracker_status = get_gencode_status_for_examples(conn, [textbook_example_id]).get(
        textbook_example_id,
        dict(NOT_CREATED_STATUS),
    )
    file_status = inspect_gencode_files(
        skill_id=skill_id,
        component_id=str(tracker_status.get("component_id") or "") or None,
        dryrun_base_dir=dryrun_base_dir,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    status = str(tracker_status.get("status", "not_created"))
    has_payload = bool(tracker_status.get("has_payload"))
    return {
        **tracker_status,
        **file_status,
        "status_label": format_gencode_status_label(status),
        "has_payload_label": "有" if has_payload else "無",
        "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
        "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
    }


def build_admin_examples_gencode_status_map(
    conn: sqlite3.Connection,
    examples: list[tuple[int, str]],
    *,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[int, dict[str, object]]:
    example_ids = [example_id for example_id, _skill_id in examples]
    base_map = get_gencode_status_for_examples(conn, example_ids)
    status_map: dict[int, dict[str, object]] = {}
    for example_id, skill_id in examples:
        tracker_status = base_map.get(example_id, dict(NOT_CREATED_STATUS))
        file_status = inspect_gencode_files(
            skill_id=skill_id,
            component_id=str(tracker_status.get("component_id") or "") or None,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        status = str(tracker_status.get("status", "not_created"))
        has_payload = bool(tracker_status.get("has_payload"))
        status_map[example_id] = {
            **tracker_status,
            **file_status,
            "status_label": format_gencode_status_label(status),
            "has_payload_label": "有" if has_payload else "無",
            "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
            "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
        }
    return status_map


def _get_tracker_rows_for_skill(conn: sqlite3.Connection, skill_id: str) -> list[dict[str, object]]:
    if not _tracker_table_exists(conn):
        return []
    rows = conn.execute(
        """
        SELECT textbook_example_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE skill_id = ?
        ORDER BY textbook_example_id ASC, component_id ASC
        """,
        (str(skill_id or "").strip(),),
    ).fetchall()
    parsed: list[dict[str, object]] = []
    for row in rows:
        payload_raw = _row_value(row, "induced_spec_payload", 3)
        payload_summary = _extract_payload_summary(payload_raw)
        parsed.append(
            {
                "textbook_example_id": int(_row_value(row, "textbook_example_id", 0)),
                "component_id": str(_row_value(row, "component_id", 1)),
                "status": str(_row_value(row, "gencode_status", 2)),
                **payload_summary,
                "has_payload": payload_raw is not None and str(payload_raw).strip() != "",
                "error_log": _row_value(row, "gencode_error_log", 4),
                "updated_at": _row_value(row, "updated_at", 5),
            }
        )
    return parsed


def build_admin_skill_gencode_status_view(
    conn: sqlite3.Connection,
    *,
    skill_id: str,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[str, object]:
    from core.gencode.services.v3_skill_coverage_service import (
        build_coverage_warnings,
        get_v3_skill_component_coverage,
    )

    coverage = get_v3_skill_component_coverage(conn, skill_id)
    coverage_warnings = build_coverage_warnings(coverage)
    rows = _get_tracker_rows_for_skill(conn, skill_id)
    if not rows:
        view = dict(NOT_CREATED_STATUS)
        file_status = inspect_gencode_files(
            skill_id=skill_id,
            component_id=None,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        status = "not_created"
        has_payload = False
        component_id = None
        error_log = None
        updated_at = None
        component_count = 0
    else:
        primary = max(rows, key=lambda row: _STATUS_PRIORITY.get(str(row["status"]), 0))
        status = str(primary["status"])
        component_id = ", ".join(str(row["component_id"]) for row in rows)
        has_payload = any(bool(row["has_payload"]) for row in rows)
        error_logs = [str(row["error_log"]) for row in rows if row.get("error_log")]
        error_log = error_logs[0] if error_logs else None
        updated_values = [str(row["updated_at"]) for row in rows if row.get("updated_at")]
        updated_at = max(updated_values) if updated_values else None
        component_count = len(rows)
        file_status = {
            "dryrun_component_exists": False,
            "dryrun_generate_exists": False,
            "dryrun_manifest_exists": inspect_gencode_files(
                skill_id=skill_id,
                component_id=None,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )["dryrun_manifest_exists"],
            "production_component_exists": False,
            "production_generate_exists": False,
            "production_manifest_exists": inspect_gencode_files(
                skill_id=skill_id,
                component_id=None,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )["production_manifest_exists"],
        }
        for row in rows:
            probes = inspect_gencode_files(
                skill_id=skill_id,
                component_id=str(row["component_id"]),
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )
            for key in (
                "dryrun_component_exists",
                "dryrun_generate_exists",
                "production_component_exists",
                "production_generate_exists",
            ):
                file_status[key] = bool(file_status[key]) or bool(probes[key])

    missing_tracker_ids = [
        row["textbook_example_id"]
        for row in coverage.get("examples", [])
        if isinstance(row, dict) and row.get("status") == "missing_tracker"
    ]

    prod_info = inspect_skill_production_files(
        skill_id=skill_id,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    has_production = prod_info.get("production_wrapper_exists")
    source_type = "production" if has_production else "dryrun"
    verified_count = int(coverage.get("verified_count") or 0)

    variation_report = {}
    if verified_count > 0:
        from core.gencode.services.v3_variation_audit_service import audit_skill_variation
        try:
            variation_report = audit_skill_variation(
                skill_id=skill_id,
                source=source_type,
                project_root=project_root,
                conn=conn,
            )
        except Exception:
            pass

    return {
        "status": status,
        "status_label": format_gencode_status_label(status),
        "component_id": component_id,
        "component_count": component_count,
        "has_payload": has_payload,
        "has_payload_label": "有" if has_payload else "無",
        "error_log": error_log,
        "updated_at": updated_at,
        "coverage": coverage,
        "coverage_summary": (
            f"V3: {coverage.get('verified_count', 0)}/{coverage.get('total_examples', 0)} verified"
        ),
        "total_examples": int(coverage.get("total_examples") or 0),
        "verified_count": verified_count,
        "failed_count": sum(1 for row in rows if str(row.get("status")) == "failed" or row.get("error_log")),
        "unsupported_count": int(coverage.get("unsupported_count") or 0),
        "missing_tracker_count": len(missing_tracker_ids),
        "coverage_missing_ids": missing_tracker_ids,
        "coverage_warnings": coverage_warnings,
        "publish_ready": bool(coverage.get("publish_ready")),
        **file_status,
        **prod_info,
        "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
        "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
        "variation_status": variation_report.get("status"),
        "dynamic_count": variation_report.get("dynamic_count", 0),
        "static_count": variation_report.get("static_count", 0),
        "partially_dynamic_count": variation_report.get("partially_dynamic_count", 0),
        "variation_warning": variation_report.get("variation_warning", ""),
    }


def build_admin_skills_gencode_status_map(
    conn: sqlite3.Connection,
    skill_ids: list[str],
    *,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[str, dict[str, object]]:
    return {
        str(skill_id): build_admin_skill_gencode_status_view(
            conn,
            skill_id=str(skill_id),
            project_root=project_root,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
        )
        for skill_id in skill_ids
        if str(skill_id or "").strip()
    }


def resolve_admin_project_root(app_root_path: str | Path | None = None) -> Path:
    root_candidates = [
        Path(app_root_path) if app_root_path else PROJECT_ROOT,
        Path(app_root_path).parent if app_root_path else PROJECT_ROOT.parent,
        PROJECT_ROOT,
    ]
    for candidate in root_candidates:
        if (candidate / "skills").exists():
            return candidate
    return PROJECT_ROOT
