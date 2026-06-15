# -*- coding: utf-8 -*-
import logging
import os
import traceback
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import UniqueConstraint

from models import (
    db,
    SkillInfo,
    SkillCurriculum,
    TextbookExample,
    SkillFamilyBridge,
    SkillPrerequisites,
)

logger = logging.getLogger(__name__)

CORE_TABLES = [
    "skills_info",
    "skill_curriculum",
    "textbook_examples",
    "skill_family_bridge",
    "skill_prerequisites",
]

SYSTEM_TABLES = [
    "prompt_templates",
    "system_settings",
    "users",
    "classes",
    "class_students",
    "student_abilities",
    "progress",
    "quiz_attempts",
    "adaptive_learning_logs",
    "mistake_logs",
    "mistake_notebook_entries",
    "experiment_log",
    "experiment_runs",
    "ablation_settings",
    "ablation_summary",
    "healer_events",
    "execution_samples",
    "evaluation_items",
    "exam_analysis",
    "questions",
    "student_uploaded_questions",
    "node_competency",
    "skill_gencode_prompt",
    "sqlite_sequence",
]

FULL_CONFIRM_TOKEN = "YES_DELETE_ALL"


def _get_primary_key_columns(model):
    return [column.name for column in model.__mapper__.primary_key]


def _find_existing_instance(model, data):
    pk_columns = _get_primary_key_columns(model)
    if pk_columns and all(data.get(column) is not None for column in pk_columns):
        identity = tuple(data[column] for column in pk_columns)
        existing = db.session.get(model, identity[0] if len(identity) == 1 else identity)
        if existing is not None:
            return existing

    unique_constraints = [
        constraint
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    with db.session.no_autoflush:
        for constraint in unique_constraints:
            unique_columns = [column.name for column in constraint.columns]
            if not unique_columns:
                continue
            if any(data.get(column) is None for column in unique_columns):
                continue

            query = db.session.query(model)
            for column in unique_columns:
                query = query.filter(getattr(model, column) == data[column])
            existing = query.first()
            if existing is not None:
                return existing

    return None


def _apply_data_to_instance(instance, data, preserve_existing_primary_key=False):
    pk_columns = set(_get_primary_key_columns(type(instance)))
    for key, value in data.items():
        if preserve_existing_primary_key and key in pk_columns and getattr(instance, key) is not None:
            continue
        setattr(instance, key, value)


def get_model_mapping():
    mapping = {}
    try:
        if hasattr(db.Model, "registry"):
            for mapper in db.Model.registry.mappers:
                cls = mapper.class_
                if hasattr(cls, "__tablename__"):
                    mapping[cls.__tablename__] = cls

        if not mapping:
            def get_all_subclasses(cls):
                all_subclasses = []
                for subclass in cls.__subclasses__():
                    all_subclasses.append(subclass)
                    all_subclasses.extend(get_all_subclasses(subclass))
                return all_subclasses

            for cls in get_all_subclasses(db.Model):
                if hasattr(cls, "__tablename__"):
                    mapping[cls.__tablename__] = cls
    except Exception as e:
        logger.error(f"Error generating model mapping: {e}")

    # Explicit fallback mapping for core tables.
    mapping["skills_info"] = SkillInfo
    mapping["skill_curriculum"] = SkillCurriculum
    mapping["textbook_examples"] = TextbookExample
    mapping["skill_family_bridge"] = SkillFamilyBridge
    mapping["skill_prerequisites"] = SkillPrerequisites

    return mapping


def clean_excel_row(row_dict):
    cleaned = {}
    date_columns = [
        "timestamp",
        "created_at",
        "updated_at",
        "last_practiced",
        "review_date",
        "login_time",
    ]

    for key, value in row_dict.items():
        if pd.isna(value) or value == "":
            cleaned[key] = None
            continue

        if key in date_columns:
            if value is None:
                cleaned[key] = None
                continue
            if isinstance(value, bool):
                cleaned[key] = datetime.now()
                continue
            try:
                if isinstance(value, (float, int)):
                    base_date = datetime(1899, 12, 30)
                    cleaned[key] = base_date + timedelta(days=value)
                elif isinstance(value, datetime):
                    cleaned[key] = value
                elif isinstance(value, str):
                    value = value.strip()
                    try:
                        cleaned[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        try:
                            cleaned[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                cleaned[key] = datetime.strptime(value, "%Y-%m-%d")
                            except Exception:
                                cleaned[key] = None
                else:
                    cleaned[key] = datetime.now()
            except Exception:
                cleaned[key] = None
        else:
            cleaned[key] = value

    return cleaned


def _is_blank_value(val):
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def _to_db_int_bool(val, default=1):
    if _is_blank_value(val):
        return int(default)
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return 1 if int(val) != 0 else 0
    s = str(val).strip().lower()
    if s in {"true", "t", "yes", "y", "1"}:
        return 1
    if s in {"false", "f", "no", "n", "0"}:
        return 0
    return int(default)


def _normalize_skills_info_defaults(data):
    out = dict(data or {})
    if _is_blank_value(out.get("gemini_prompt")):
        out["gemini_prompt"] = ""
    if _is_blank_value(out.get("input_type")):
        out["input_type"] = "text"
    if _is_blank_value(out.get("consecutive_correct_required")):
        out["consecutive_correct_required"] = 3
    if _is_blank_value(out.get("order_index")):
        out["order_index"] = 0
    if _is_blank_value(out.get("importance")):
        out["importance"] = 1
    out["is_active"] = _to_db_int_bool(out.get("is_active"), default=1)

    desc_col = SkillInfo.__table__.columns.get("description")
    if desc_col is not None and not getattr(desc_col, "nullable", True) and _is_blank_value(out.get("description")):
        out["description"] = ""
    for name in ("suggested_prompt_1", "suggested_prompt_2", "suggested_prompt_3"):
        col = SkillInfo.__table__.columns.get(name)
        if col is not None and not getattr(col, "nullable", True) and _is_blank_value(out.get(name)):
            out[name] = ""
    return out


def _match_model_for_sheet(sheet_name_clean, mapping):
    if sheet_name_clean in mapping:
        return sheet_name_clean, mapping[sheet_name_clean]
    for tbl_name, model_cls in mapping.items():
        if tbl_name.lower() == sheet_name_clean.lower():
            return tbl_name, model_cls
    return None, None


def _extract_identity_hint(data):
    for key in ("skill_id", "id", "example_id"):
        if key in data and data.get(key) is not None:
            return f"{key}={data.get(key)!r}"
    return "pk=unknown"


def _validate_core_restore_after_import(xls, row_stats, strict_mode=False):
    ok = True
    lines = []
    warning_count = 0
    fatal_error_count = 0
    orphan_count = 0

    si_count = db.session.query(SkillInfo).count()
    sc_count = db.session.query(SkillCurriculum).count()
    lines.append(f"DB counts: skills_info={si_count}, skill_curriculum={sc_count}")

    b1_count = db.session.query(SkillInfo).filter(
        (SkillInfo.skill_id.like("vh_數學B1_%"))
        | (SkillInfo.skill_id.like("outline_vocational_數學B1_%"))
    ).count()
    b4_count = db.session.query(SkillInfo).filter(SkillInfo.skill_id.like("vh_數學B4_%")).count()
    lines.append(f"skills_info by prefix: B1={b1_count}, B4={b4_count}")

    backup_b1_rows = 0
    if "skills_info" in xls:
        df = xls["skills_info"].where(pd.notnull(xls["skills_info"]), None)
        if "skill_id" in df.columns:
            backup_b1_rows = int(
                df["skill_id"]
                .astype(str)
                .str.startswith(("vh_數學B1_", "outline_vocational_數學B1_"))
                .sum()
            )
    if backup_b1_rows > 0 and b1_count == 0:
        ok = False
        fatal_error_count += 1
        lines.append("❌ skills_info restore incomplete: backup has B1 rows but DB has 0 B1 rows.")

    orphan_q = (
        db.session.query(
            SkillCurriculum.skill_id,
            SkillCurriculum.volume,
            SkillCurriculum.chapter,
            SkillCurriculum.section,
        )
        .outerjoin(SkillInfo, SkillInfo.skill_id == SkillCurriculum.skill_id)
        .filter(SkillInfo.skill_id.is_(None))
    )
    orphan_count = orphan_q.count()
    lines.append(f"orphan skill_curriculum rows: {orphan_count}")
    if orphan_count > 0:
        warning_count += orphan_count
        lines.append(f"WARNING: orphan skill_curriculum rows: {orphan_count}")
        if strict_mode:
            ok = False
            fatal_error_count += 1
            lines.append("FATAL: strict mode treats orphan skill_curriculum rows as fatal.")
        for row in orphan_q.limit(20).all():
            lines.append(
                f"orphan: skill_id={row.skill_id!r}, volume={row.volume!r}, chapter={row.chapter!r}, section={row.section!r}"
            )

    for table in ("skills_info", "skill_curriculum", "textbook_examples"):
        st = row_stats.get(table, {})
        if st.get("failed", 0) > 0:
            ok = False
            fatal_error_count += int(st.get("failed", 0) or 0)
            lines.append(f"❌ Table {table}: failed rows = {st.get('failed', 0)}")

    return ok, lines, {
        "warning_count": warning_count,
        "fatal_error_count": fatal_error_count,
        "orphan_skill_curriculum_count": orphan_count,
    }


def _append_import_final_status(
    lines,
    *,
    row_stats=None,
    warning_count=0,
    fatal_error_count=0,
    orphan_skill_curriculum_count=0,
    fatal_reason="",
):
    row_stats = row_stats or {}
    failed_rows = sum(int((st or {}).get("failed", 0) or 0) for st in row_stats.values())
    if fatal_reason and fatal_error_count == 0:
        fatal_error_count = 1

    if failed_rows > 0 or fatal_error_count > 0:
        final_status = "failed"
        final_status_reason = fatal_reason or "row_import_failures"
    elif int(warning_count or 0) > 0:
        final_status = "completed_with_warnings"
        final_status_reason = "post_import_warnings"
    else:
        final_status = "completed"
        final_status_reason = "all_rows_imported_without_warnings"

    lines.append(f"final_status: {final_status}")
    lines.append(f"final_status_reason: {final_status_reason}")
    lines.append(f"warning_count: {int(warning_count or 0)}")
    lines.append(f"fatal_errors: {int(fatal_error_count or 0)}")
    lines.append(f"orphan_skill_curriculum_count: {int(orphan_skill_curriculum_count or 0)}")
    return final_status


def import_excel_to_db(filepath, mode="core", confirm_full_clear="", strict_mode=False):
    if not os.path.exists(filepath):
        return False, "找不到備份檔案"

    try:
        xls = pd.read_excel(filepath, sheet_name=None, engine="openpyxl")
        mapping = get_model_mapping()
        if not mapping:
            return False, "無法建立 SQLAlchemy model mapping"

        mode = str(mode or "core").strip().lower()
        if mode not in ("core", "full"):
            mode = "core"
        if mode == "full" and str(confirm_full_clear or "").strip() != FULL_CONFIRM_TOKEN:
            return False, "full 模式需要 confirm token: YES_DELETE_ALL"

        allowed_tables = set(CORE_TABLES) if mode == "core" else None
        results = []
        row_stats = {}
        row_errors = {}

        results.append(f"偵測到 models: {len(mapping)}")
        results.append(f"import mode: {mode}")

        excel_sheet_names = {name.strip() for name in xls.keys()}
        required_core = {"skills_info", "skill_curriculum", "textbook_examples"}
        optional_core = {"skill_family_bridge", "skill_prerequisites"}

        if mode == "core":
            missing_required = sorted(required_core - excel_sheet_names)
            if missing_required:
                return False, "❌ core restore failed: missing required sheet(s): " + ", ".join(missing_required)

            for missing_name in sorted(optional_core - excel_sheet_names):
                results.append(f"⚠️ optional core sheet missing: {missing_name}")

            for sheet_name_clean in sorted(excel_sheet_names & (required_core | optional_core)):
                table_name, model = _match_model_for_sheet(sheet_name_clean, mapping)
                if not model:
                    return False, "\n".join(results)

        for sheet_name, df in xls.items():
            sheet_name_clean = sheet_name.strip()
            if allowed_tables is not None and sheet_name_clean not in allowed_tables:
                results.append(f"INFO: ignored non-core sheet {sheet_name_clean}")
                continue

            table_name, model = _match_model_for_sheet(sheet_name_clean, mapping)
            if not model:
                if mode == "core" and sheet_name_clean in set(CORE_TABLES):
                    results.append(f"core restore failed: sheet {sheet_name_clean} exists but no SQLAlchemy model mapping")
                    _append_import_final_status(
                        results,
                        row_stats=row_stats,
                        fatal_error_count=1,
                        fatal_reason="missing_model_mapping",
                    )
                    return False, f"❌ core restore failed: sheet {sheet_name_clean} exists but no SQLAlchemy model mapping"
                results.append(f"⚠️ skip sheet {sheet_name}: no model mapping")
                continue

            df = df.where(pd.notnull(df), None)
            model_columns = model.__table__.columns.keys()
            pk_columns = set(_get_primary_key_columns(model))

            source_rows = len(df)
            imported_count = 0
            failed_count = 0
            skipped_count = 0
            row_errors.setdefault(table_name, [])

            for index, row in df.iterrows():
                data = {}
                try:
                    for col in model_columns:
                        if col in row:
                            val = row[col]
                            if isinstance(val, str):
                                lv = val.lower()
                                if lv == "true":
                                    val = True
                                elif lv == "false":
                                    val = False
                            data[col] = val

                    if not data:
                        skipped_count += 1
                        continue

                    data = clean_excel_row(data)
                    if table_name == "skills_info":
                        data = _normalize_skills_info_defaults(data)
                    existing = _find_existing_instance(model, data)
                    if existing is not None:
                        _apply_data_to_instance(existing, data, preserve_existing_primary_key=bool(pk_columns))
                    else:
                        instance = model()
                        _apply_data_to_instance(instance, data)
                        db.session.add(instance)

                    db.session.commit()
                    imported_count += 1
                except Exception as e:
                    db.session.rollback()
                    failed_count += 1
                    row_errors[table_name].append(
                        {
                            "sheet_name": sheet_name,
                            "row_index": int(index),
                            "identity": _extract_identity_hint(data),
                            "error": str(e),
                        }
                    )

            row_stats[table_name] = {
                "source_rows": source_rows,
                "imported": imported_count,
                "failed": failed_count,
                "skipped": skipped_count,
            }
            results.append(
                f"Table {table_name}: source_rows={source_rows}, imported={imported_count}, failed={failed_count}, skipped={skipped_count}"
            )
            for item in row_errors[table_name][:20]:
                results.append(
                    f"❌ row_error sheet={item['sheet_name']} row={item['row_index']} {item['identity']} error={item['error']}"
                )

            if mode == "core" and table_name == "skills_info" and imported_count < source_rows:
                results.append(f"❌ Table skills_info imported_count < source_rows ({imported_count} < {source_rows})")

        if mode == "core":
            core_failed_rows = any(
                row_stats.get(t, {}).get("failed", 0) > 0
                for t in ("skills_info", "skill_curriculum", "textbook_examples")
            )
            if core_failed_rows:
                _append_import_final_status(results, row_stats=row_stats)
                return False, "\n".join(results)

            si_stat = row_stats.get("skills_info", {})
            if si_stat and si_stat.get("imported", 0) < si_stat.get("source_rows", 0):
                _append_import_final_status(
                    results,
                    row_stats=row_stats,
                    fatal_error_count=1,
                    fatal_reason="skills_info_import_incomplete",
                )
                return False, "\n".join(results)

            ok, validation, validation_meta = _validate_core_restore_after_import(
                xls,
                row_stats,
                strict_mode=bool(strict_mode),
            )
            results.extend(validation)
            warning_count = int(validation_meta.get("warning_count", 0) or 0)
            fatal_error_count = int(validation_meta.get("fatal_error_count", 0) or 0)
            orphan_count = int(validation_meta.get("orphan_skill_curriculum_count", 0) or 0)
            if not ok:
                _append_import_final_status(
                    results,
                    row_stats=row_stats,
                    warning_count=warning_count,
                    fatal_error_count=fatal_error_count,
                    orphan_skill_curriculum_count=orphan_count,
                    fatal_reason="post_import_validation_failed",
                )
                return False, "\n".join(results)
            _append_import_final_status(
                results,
                row_stats=row_stats,
                warning_count=warning_count,
                fatal_error_count=fatal_error_count,
                orphan_skill_curriculum_count=orphan_count,
            )
        else:
            _append_import_final_status(results, row_stats=row_stats)

        return True, "\n".join(results)

    except Exception as e:
        db.session.rollback()
        error_msg = f"匯入失敗: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        lines = [f"匯入失敗: {str(e)}"]
        _append_import_final_status(lines, fatal_error_count=1, fatal_reason="fatal_exception")
        return False, "\n".join(lines)
