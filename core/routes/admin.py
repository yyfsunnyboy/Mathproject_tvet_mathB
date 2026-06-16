# -*- coding: utf-8 -*-
"""
=============================================================================
?????? (Module Name): core/routes/admin.py
?賹??方? (Description): ?綽?潸????閰??????????謕??砍?憸?蹓??謆??穿?蹓??鞈??蹓曄???蹓賣??蹓??選???蹍ompt ???????菜??鞈???
????止等? (Usage): ?璇??舀０???
??秧?? (Version): V2.0
?皝??鈭? (Date): 2026-01-13
?砍?憸?謢? (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template, flash, session, send_file, Response, stream_with_context
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import distinct, text, MetaData, Table, select, func, or_, and_, inspect
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import uuid
import queue
import threading
import traceback
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import pandas as pd
import io
import re
import importlib
import json
from core.gencode.pipeline_orchestrator import (
    run_gencode_auto_pipeline,
    run_gencode_phase1,
    run_gencode_phase2,
    run_gencode_phase3_package,
    run_gencode_publish_check,
    publish_gencode_draft_skill,
    register_classifier_rulepack_from_draft,
)
from core.services.prompt_sync_service import (
    PromptSyncError,
    compare_prompt_db_vs_yaml,
    export_single_prompt_to_yaml,
    import_single_prompt_from_yaml,
)

from . import core_bp
from core.globals import TASK_QUEUES
from core import textbook_processor
from core.textbook_filename_parser import (
    parse_textbook_filename_metadata,
    resolve_upload_filenames,
)
from core.textbook_structure_parser import get_structure_map
from core.ai_wrapper import resolve_gemini_api_key, mask_api_key
from core.session_safety import (
    get_large_result_from_server_store,
    put_large_result_in_server_store,
    safe_flash_message,
    summarize_import_result,
)
from core.utils import handle_curriculum_filters
from core.ai_settings import (
    AI_ROLE_KEYS,
    SETTING_AI_CLOUD_MODEL,
    SETTING_AI_DEFAULT_PROVIDER,
    SETTING_AI_ENABLE_HIGH_PRECISION_VISION,
    SETTING_AI_ENABLE_TUTOR_RESPONSE,
    SETTING_GEMINI_API_KEY,
    SETTING_AI_GLOBAL_STRATEGY,
    SETTING_AI_MODEL_ROLES,
    SETTING_AI_RAG_NAIVE_THRESHOLD,
    apply_ai_runtime_settings,
    get_ai_settings_snapshot,
    get_available_model_presets,
    get_google_model_options,
    normalize_google_model_id,
    set_system_setting_value,
)

# [Fix] ?????賤?堊城?????鞈??橫???ImportError
from core.data_importer import import_excel_to_db, CORE_TABLES, FULL_CONFIRM_TOKEN

from config import Config
# [Fix] 蝞? SkillPrerequisites ?⊥???
from models import db, SkillInfo, SkillCurriculum, User, TextbookExample, Progress, SkillGenCodePrompt, SkillPrerequisites, init_db, StudentUploadedQuestion
from core.models.prompt_template import PromptTemplate

CORE_CLEAR_CONFIRM_TOKEN = "DELETE_CORE"
CORE_TEXTBOOK_ONLY_TABLES = ("textbook_examples", "skill_curriculum", "skills_info")
OUTLINE_SKILL_PREFIX = "outline_"
VOCATIONAL_MATH_B_CONFIRM_TOKEN = "CLEAR_VOCATIONAL_MATH_B"
VOCATIONAL_MATH_B_PREFIX = "vh_數學B%"
VOCATIONAL_MATH_B_OUTLINE_PREFIX = "outline_vocational_數學B%"


def _is_outline_skill_id(skill_id):
    return str(skill_id or "").startswith(OUTLINE_SKILL_PREFIX)


def _coerce_progress_message(msg):
    """Normalize queue/SSE messages to UTF-8-safe text."""
    if isinstance(msg, dict):
        return json.dumps(msg, ensure_ascii=False)
    if isinstance(msg, (list, tuple)):
        return json.dumps(msg, ensure_ascii=False)
    if isinstance(msg, bytes):
        return msg.decode("utf-8", errors="replace")
    return str(msg)


def _format_sse_data(msg):
    text = _coerce_progress_message(msg).replace("\r\n", "\n").replace("\r", "\n")
    return "".join(f"data: {line}\n" for line in text.split("\n")) + "\n"


def _derive_formula_status(*, formula_assets_count, has_formula_image_placeholder, has_formula_missing_placeholder, needs_formula_review):
    """Derive formula status for admin examples page."""
    if has_formula_image_placeholder and formula_assets_count > 0:
        return "asset_attached", "?砍???撌脫?頛?敺?OCR/銴", "info"
    if has_formula_missing_placeholder and formula_assets_count > 0:
        return "asset_attached_but_text_missing", "??蝻箏撘?雿歇?撘????ｇ?敺?OCR/銴", "warning"
    if has_formula_image_placeholder and formula_assets_count == 0:
        return "image_placeholder_no_asset", "???撘???閮?雿?曉撠?鞈", "danger"
    if has_formula_missing_placeholder and formula_assets_count == 0:
        return "missing_no_asset", "?砍?蝻箏仃嚗?舐鞈", "danger"
    if not has_formula_image_placeholder and not has_formula_missing_placeholder and not needs_formula_review:
        return "ok", "甇?虜", "secondary"
    return "ok", "甇?虜", "secondary"


def _resolve_admin_project_root() -> Path:
    from core.gencode.services.gencode_status_query_service import resolve_admin_project_root

    return resolve_admin_project_root(current_app.root_path)


def _load_examples_gencode_status_map(examples) -> dict[int, dict[str, object]]:
    from core.gencode.services.gencode_status_query_service import (
        build_admin_examples_gencode_status_map,
    )

    if not examples:
        return {}
    raw_conn = db.engine.raw_connection()
    try:
        return build_admin_examples_gencode_status_map(
            raw_conn,
            [(int(ex.id), str(ex.skill_id)) for ex in examples],
            project_root=_resolve_admin_project_root(),
        )
    except Exception:
        return {}
    finally:
        raw_conn.close()


def _load_skills_v3_gencode_status_map(skill_ids: list[str]) -> dict[str, dict[str, object]]:
    from core.gencode.services.gencode_status_query_service import (
        build_admin_skills_gencode_status_map,
    )

    if not skill_ids:
        return {}
    raw_conn = db.engine.raw_connection()
    try:
        return build_admin_skills_gencode_status_map(
            raw_conn,
            [str(skill_id) for skill_id in skill_ids if str(skill_id or "").strip()],
            project_root=_resolve_admin_project_root(),
        )
    except Exception:
        return {}
    finally:
        raw_conn.close()


def _normalize_core_option_value(raw):
    val = str(raw or "").strip()
    return "" if val in ("", "all", "None", "null") else val


def _collect_core_scope_options(filters=None):
    filters = dict(filters or {})
    curriculum = _normalize_core_option_value(filters.get("curriculum"))
    grade_raw = _normalize_core_option_value(filters.get("grade"))
    volume = _normalize_core_option_value(filters.get("volume"))
    chapter = _normalize_core_option_value(filters.get("chapter"))
    grade = int(grade_raw) if str(grade_raw).isdigit() else None

    q_curr = db.session.query(SkillCurriculum.curriculum).distinct()
    curricula = sorted({str(r[0]) for r in q_curr.all() if r[0] is not None})

    q_grade = db.session.query(SkillCurriculum.grade)
    if curriculum:
        q_grade = q_grade.filter(SkillCurriculum.curriculum == curriculum)
    grades = sorted({int(r[0]) for r in q_grade.distinct().all() if r[0] is not None})

    q_volume = db.session.query(SkillCurriculum.volume)
    if curriculum:
        q_volume = q_volume.filter(SkillCurriculum.curriculum == curriculum)
    if grade is not None:
        q_volume = q_volume.filter(SkillCurriculum.grade == grade)
    volumes = sorted({str(r[0]) for r in q_volume.distinct().all() if r[0] is not None})

    q_chapter = db.session.query(SkillCurriculum.chapter)
    if curriculum:
        q_chapter = q_chapter.filter(SkillCurriculum.curriculum == curriculum)
    if grade is not None:
        q_chapter = q_chapter.filter(SkillCurriculum.grade == grade)
    if volume:
        q_chapter = q_chapter.filter(SkillCurriculum.volume == volume)
    chapters = sorted({str(r[0]) for r in q_chapter.distinct().all() if r[0] is not None})

    q_section = db.session.query(SkillCurriculum.section)
    if curriculum:
        q_section = q_section.filter(SkillCurriculum.curriculum == curriculum)
    if grade is not None:
        q_section = q_section.filter(SkillCurriculum.grade == grade)
    if volume:
        q_section = q_section.filter(SkillCurriculum.volume == volume)
    if chapter:
        q_section = q_section.filter(SkillCurriculum.chapter == chapter)
    sections = sorted({str(r[0]) for r in q_section.distinct().all() if r[0] is not None})

    return {
        "curricula": curricula,
        "grades": grades,
        "volumes": volumes,
        "chapters": chapters,
        "sections": sections,
    }


def _normalize_core_scope_filters(form_data):
    mode = str(form_data.get("core_scope_mode", "all") or "all").strip().lower()
    if mode not in ("all", "filtered"):
        mode = "all"

    def _pick(name):
        val = str(form_data.get(name, "") or "").strip()
        return "" if val in ("", "all", "None") else val

    grade_raw = _pick("core_grade")
    grade = int(grade_raw) if grade_raw.isdigit() else None
    return {
        "scope_mode": mode,
        "curriculum": _pick("core_curriculum"),
        "grade": grade,
        "volume": _pick("core_volume"),
        "chapter": _pick("core_chapter"),
        "section": _pick("core_section"),
    }


def _core_scope_has_any_filter(filters):
    if not isinstance(filters, dict):
        return False
    return any(
        [
            bool(filters.get("curriculum")),
            filters.get("grade") is not None,
            bool(filters.get("volume")),
            bool(filters.get("chapter")),
            bool(filters.get("section")),
        ]
    )


def _core_scope_summary(filters):
    mode = str((filters or {}).get("scope_mode", "all") or "all").strip().lower()
    if mode == "all":
        return "mode=all"
    parts = []
    for k in ("curriculum", "grade", "volume", "chapter", "section"):
        v = (filters or {}).get(k)
        if v is None or v == "":
            continue
        parts.append(f"{k}={v}")
    if not parts:
        return "mode=filtered (no_filters)"
    return "mode=filtered " + " / ".join(parts)


def _core_scope_form_state(filters):
    f = filters or {}
    return {
        "core_scope_mode": str(f.get("scope_mode", "all") or "all"),
        "core_curriculum": str(f.get("curriculum", "") or "all"),
        "core_grade": str(f.get("grade")) if f.get("grade") is not None else "all",
        "core_volume": str(f.get("volume", "") or "all"),
        "core_chapter": str(f.get("chapter", "") or "all"),
        "core_section": str(f.get("section", "") or "all"),
    }


def _clear_core_textbook_data(filters):
    query = SkillCurriculum.query
    if filters.get("scope_mode") == "filtered":
        if filters.get("curriculum"):
            query = query.filter(SkillCurriculum.curriculum == filters["curriculum"])
        if filters.get("grade") is not None:
            query = query.filter(SkillCurriculum.grade == filters["grade"])
        if filters.get("volume"):
            query = query.filter(SkillCurriculum.volume == filters["volume"])
        if filters.get("chapter"):
            query = query.filter(SkillCurriculum.chapter == filters["chapter"])
        if filters.get("section"):
            query = query.filter(SkillCurriculum.section == filters["section"])

    target_rows = query.all()
    outline_rows = [r for r in target_rows if _is_outline_skill_id(r.skill_id)]
    if filters.get("scope_mode") == "filtered":
        deletable_rows = [r for r in target_rows if not _is_outline_skill_id(r.skill_id)]
    else:
        deletable_rows = list(target_rows)
        outline_rows = []
    target_row_ids = [r.id for r in deletable_rows]
    target_skill_ids = sorted({str(r.skill_id) for r in deletable_rows if r.skill_id})
    stats = {
        "deleted_textbook_examples": 0,
        "deleted_skill_curriculum": 0,
        "deleted_orphan_skills_info": 0,
        "target_skill_count": len(target_skill_ids),
        "skipped_shared_skill_ids": [],
        "preserved_outline_curriculum": len(outline_rows),
    }
    if not target_row_ids:
        return stats

    shared_rows = (
        db.session.query(SkillCurriculum.skill_id)
        .filter(
            SkillCurriculum.skill_id.in_(target_skill_ids),
            ~SkillCurriculum.id.in_(target_row_ids),
        )
        .distinct()
        .all()
    )
    skipped_shared = sorted({str(r[0]) for r in shared_rows if r and r[0]})
    stats["skipped_shared_skill_ids"] = skipped_shared
    deletable_example_skills = [sid for sid in target_skill_ids if sid not in skipped_shared and not _is_outline_skill_id(sid)]

    try:
        if deletable_example_skills:
            stats["deleted_textbook_examples"] = (
                TextbookExample.query.filter(TextbookExample.skill_id.in_(deletable_example_skills))
                .delete(synchronize_session=False)
            )

        stats["deleted_skill_curriculum"] = (
            SkillCurriculum.query.filter(SkillCurriculum.id.in_(target_row_ids))
            .delete(synchronize_session=False)
        )

        orphan_skills = []
        for sid in target_skill_ids:
            if _is_outline_skill_id(sid):
                continue
            still_in_curriculum = db.session.query(SkillCurriculum.id).filter_by(skill_id=sid).first() is not None
            still_in_examples = db.session.query(TextbookExample.id).filter_by(skill_id=sid).first() is not None
            if not still_in_curriculum and not still_in_examples:
                orphan_skills.append(sid)
        if orphan_skills:
            stats["deleted_orphan_skills_info"] = (
                SkillInfo.query.filter(SkillInfo.skill_id.in_(orphan_skills))
                .delete(synchronize_session=False)
            )
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return stats


def _preview_core_textbook_data(filters):
    query = SkillCurriculum.query
    if filters.get("scope_mode") == "filtered":
        if filters.get("curriculum"):
            query = query.filter(SkillCurriculum.curriculum == filters["curriculum"])
        if filters.get("grade") is not None:
            query = query.filter(SkillCurriculum.grade == filters["grade"])
        if filters.get("volume"):
            query = query.filter(SkillCurriculum.volume == filters["volume"])
        if filters.get("chapter"):
            query = query.filter(SkillCurriculum.chapter == filters["chapter"])
        if filters.get("section"):
            query = query.filter(SkillCurriculum.section == filters["section"])

    target_rows = query.all()
    outline_rows = [r for r in target_rows if _is_outline_skill_id(r.skill_id)]
    if filters.get("scope_mode") == "filtered":
        deletable_rows = [r for r in target_rows if not _is_outline_skill_id(r.skill_id)]
    else:
        deletable_rows = list(target_rows)
        outline_rows = []
    target_row_ids = [r.id for r in deletable_rows]
    target_skill_ids = sorted({str(r.skill_id) for r in deletable_rows if r.skill_id})
    if not target_row_ids:
        return {
            "deleted_textbook_examples": 0,
            "deleted_skill_curriculum": 0,
            "deleted_orphan_skills_info": 0,
            "target_skill_count": 0,
            "skipped_shared_skill_ids": [],
            "preserved_outline_curriculum": len(outline_rows),
        }
    shared_rows = (
        db.session.query(SkillCurriculum.skill_id)
        .filter(
            SkillCurriculum.skill_id.in_(target_skill_ids),
            ~SkillCurriculum.id.in_(target_row_ids),
        )
        .distinct()
        .all()
    )
    skipped_shared = sorted({str(r[0]) for r in shared_rows if r and r[0]})
    deletable_example_skills = [sid for sid in target_skill_ids if sid not in skipped_shared and not _is_outline_skill_id(sid)]
    preview_deleted_examples = 0
    if deletable_example_skills:
        preview_deleted_examples = (
            db.session.query(TextbookExample.id)
            .filter(TextbookExample.skill_id.in_(deletable_example_skills))
            .count()
        )
    preview_deleted_curriculum = len(target_row_ids)
    preview_deleted_orphan_skills = 0
    for sid in target_skill_ids:
        if _is_outline_skill_id(sid):
            continue
        has_other_curriculum = (
            db.session.query(SkillCurriculum.id)
            .filter(
                SkillCurriculum.skill_id == sid,
                ~SkillCurriculum.id.in_(target_row_ids),
            )
            .first()
            is not None
        )
        if has_other_curriculum:
            continue
        has_examples = db.session.query(TextbookExample.id).filter_by(skill_id=sid).first() is not None
        if not has_examples:
            preview_deleted_orphan_skills += 1
    return {
        "deleted_textbook_examples": preview_deleted_examples,
        "deleted_skill_curriculum": preview_deleted_curriculum,
        "deleted_orphan_skills_info": preview_deleted_orphan_skills,
        "target_skill_count": len(target_skill_ids),
        "skipped_shared_skill_ids": skipped_shared,
        "preserved_outline_curriculum": len(outline_rows),
    }


def _is_admin_or_teacher():
    return bool(current_user.is_admin or current_user.role == "teacher")


def _table_exists(table_name: str) -> bool:
    return table_name in inspect(db.engine).get_table_names()


def _columns_of(table_name: str) -> set[str]:
    if not _table_exists(table_name):
        return set()
    return {c["name"] for c in inspect(db.engine).get_columns(table_name)}


def _count_sql(sql: str, params: dict | None = None) -> int:
    return int(db.session.execute(text(sql), params or {}).scalar() or 0)


def _delete_sql(sql: str, params: dict | None = None) -> int:
    result = db.session.execute(text(sql), params or {})
    return int(result.rowcount or 0)


def _build_like_conditions(columns: set[str], field_names: list[str], alias: str = "") -> list[str]:
    out = []
    for f in field_names:
        if f in columns:
            col = f"{alias}{f}" if alias else f
            out.append(f"{col} LIKE :vh_prefix")
            out.append(f"{col} LIKE :outline_prefix")
    return out


def _hard_clear_vocational_math_b_core(*, execute: bool = False) -> dict:
    params = {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX}
    deleted: dict[str, int] = {}
    missing_columns: dict[str, list[str]] = {}

    dependent_tables = [
        "progress",
        "student_progress",
        "student_answers",
        "practice_records",
        "wrong_questions",
        "mistake_logs",
        "mistake_notebook_entries",
        "adaptive_sessions",
        "adaptive_records",
        "adaptive_review_state",
        "generated_questions",
        "questions",
        "question_bank",
        "student_abilities",
        "exam_analysis",
    ]
    skill_ref_fields = ["skill_id", "source_skill_id", "target_skill_id", "current_skill_id", "next_skill_id", "predicted_skill_id"]

    plan: list[tuple[str, str]] = []

    for table_name in dependent_tables:
        if not _table_exists(table_name):
            continue
        cols = _columns_of(table_name)
        missing_columns[table_name] = [x for x in skill_ref_fields + ["volume", "source_volume", "curriculum", "source_curriculum"] if x not in cols]
        conds = _build_like_conditions(cols, skill_ref_fields)
        if "volume" in cols:
            conds.append("volume LIKE '數學B%'")
        if "source_volume" in cols:
            conds.append("source_volume LIKE '數學B%'")
        # Do not use curriculum/source_curriculum alone for dependent tables.
        if not conds:
            continue
        plan.append((table_name, " OR ".join(conds)))

    if _table_exists("textbook_examples"):
        missing_columns["textbook_examples"] = [x for x in ["source_curriculum", "source_volume", "skill_id"] if x not in _columns_of("textbook_examples")]
        plan.append((
            "textbook_examples",
            "source_curriculum = 'vocational' OR source_volume LIKE '數學B%' OR skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
        ))

    if _table_exists("skill_prerequisites"):
        missing_columns["skill_prerequisites"] = [x for x in ["skill_id", "prerequisite_id"] if x not in _columns_of("skill_prerequisites")]
        plan.append((
            "skill_prerequisites",
            "skill_id LIKE :vh_prefix OR prerequisite_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix OR prerequisite_id LIKE :outline_prefix",
        ))

    if _table_exists("skill_family_bridge"):
        cols = _columns_of("skill_family_bridge")
        missing_columns["skill_family_bridge"] = [x for x in ["skill_id", "source_skill_id", "target_skill_id"] if x not in cols]
        bridge_conds = _build_like_conditions(cols, ["skill_id", "source_skill_id", "target_skill_id"])
        if bridge_conds:
            plan.append(("skill_family_bridge", " OR ".join(bridge_conds)))

    if _table_exists("skill_curriculum"):
        missing_columns["skill_curriculum"] = [x for x in ["curriculum", "volume", "skill_id"] if x not in _columns_of("skill_curriculum")]
        plan.append((
            "skill_curriculum",
            "curriculum = 'vocational' OR volume LIKE '數學B%' OR skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
        ))

    if _table_exists("skills_info"):
        missing_columns["skills_info"] = [x for x in ["skill_id"] if x not in _columns_of("skills_info")]
        plan.append((
            "skills_info",
            "skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
        ))

    for table_name, where_sql in plan:
        deleted[table_name] = _count_sql(f"SELECT COUNT(*) FROM {table_name} WHERE {where_sql}", params)

    if not execute:
        return {"deleted": deleted, "missing_columns": missing_columns, "plan": [x[0] for x in plan]}

    try:
        db.session.execute(text("PRAGMA foreign_keys = OFF"))
        for table_name, where_sql in plan:
            deleted[table_name] = _delete_sql(f"DELETE FROM {table_name} WHERE {where_sql}", params)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        try:
            db.session.execute(text("PRAGMA foreign_keys = ON"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    return {"deleted": deleted, "missing_columns": missing_columns, "plan": [x[0] for x in plan]}


def _vocational_math_b_remaining_check():
    checks = {
        "skills_info_vh_mathB": 0,
        "textbook_examples_mathB": 0,
        "skill_curriculum_mathB": 0,
        "skill_prerequisites_mathB": 0,
        "skill_family_bridge_mathB": 0,
    }

    if _table_exists("skills_info"):
        checks["skills_info_vh_mathB"] = _count_sql(
            "SELECT COUNT(*) FROM skills_info WHERE skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
            {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX},
        )
    if _table_exists("textbook_examples"):
        checks["textbook_examples_mathB"] = _count_sql(
            "SELECT COUNT(*) FROM textbook_examples "
            "WHERE source_curriculum = 'vocational' OR source_volume LIKE '數學B%' "
            "OR skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
            {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX},
        )
    if _table_exists("skill_curriculum"):
        checks["skill_curriculum_mathB"] = _count_sql(
            "SELECT COUNT(*) FROM skill_curriculum "
            "WHERE curriculum = 'vocational' OR volume LIKE '數學B%' "
            "OR skill_id LIKE :vh_prefix OR skill_id LIKE :outline_prefix",
            {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX},
        )
    if _table_exists("skill_prerequisites"):
        checks["skill_prerequisites_mathB"] = _count_sql(
            "SELECT COUNT(*) FROM skill_prerequisites "
            "WHERE skill_id LIKE :vh_prefix OR prerequisite_id LIKE :vh_prefix "
            "OR skill_id LIKE :outline_prefix OR prerequisite_id LIKE :outline_prefix",
            {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX},
        )
    if _table_exists("skill_family_bridge"):
        cols = _columns_of("skill_family_bridge")
        conds = _build_like_conditions(cols, ["skill_id", "source_skill_id", "target_skill_id"])
        if conds:
            checks["skill_family_bridge_mathB"] = _count_sql(
                f"SELECT COUNT(*) FROM skill_family_bridge WHERE {' OR '.join(conds)}",
                {"vh_prefix": VOCATIONAL_MATH_B_PREFIX, "outline_prefix": VOCATIONAL_MATH_B_OUTLINE_PREFIX},
            )
    return checks

# ==========================================
# Background Tasks (??魂????)
# ==========================================

@core_bp.route('/admin/rag_settings/update', methods=['POST'])
@login_required
def admin_update_rag_settings():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        data = request.get_json()
        threshold = float(data.get('threshold', 0.40))
        target_type = data.get('target_type', 'practice')
        enable_ai_chat = bool(data.get('enable_ai_chat', True))
        
        rag_path = os.path.join(current_app.root_path, '..', 'configs', 'rag_settings.json')
        os.makedirs(os.path.dirname(rag_path), exist_ok=True)
        with open(rag_path, 'w', encoding='utf-8') as f:
            json.dump({'threshold': threshold, 'target_type': target_type, 'enable_ai_chat': enable_ai_chat}, f, ensure_ascii=False)
            
        # Update memory
        current_app.config['ADVANCED_RAG_NAIVE_THRESHOLD'] = threshold
        current_app.config['ADVANCED_RAG_ENABLE_AI_CHAT'] = enable_ai_chat
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def background_processing(file_paths, task_queue, app_context, curriculum_info, skip_code_gen, **kwargs):
    """Background textbook processing worker."""
    def _safe_report_token(value):
        token = re.sub(r"\s+", "_", str(value or "").strip())
        token = re.sub(r"[^\w\-\u4e00-\u9fff]+", "_", token, flags=re.UNICODE)
        token = re.sub(r"_+", "_", token).strip("_")
        return token or "unknown"

    def _resolve_canonical_section_title(filename):
        filename_meta = parse_textbook_filename_metadata(filename)
        section_code = str((filename_meta or {}).get("section_code") or "").strip()
        if not section_code:
            return ""

        curriculum = str(curriculum_info.get("curriculum") or "").strip()
        volume = str(curriculum_info.get("volume") or "").strip()
        publisher = str(curriculum_info.get("publisher") or "longteng").strip()

        # Priority 1: anchor section aligned in DB (import result anchor).
        existing_anchor = SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.section.like(f"{section_code} %"),
        ).first()
        if existing_anchor and existing_anchor.section:
            return str(existing_anchor.section).strip()

        # Priority 2: textbook structure map canonical section_title.
        struct_map = get_structure_map(curriculum, volume, publisher=publisher)
        if struct_map:
            section_meta = struct_map.get_metadata(section_code)
            if section_meta and section_meta.get("section_title"):
                return str(section_meta["section_title"]).strip()

        # Priority 3: fallback DB matching section_code (non-anchor query).
        fallback_row = (
            db.session.query(SkillCurriculum.section)
            .filter(
                SkillCurriculum.curriculum == curriculum,
                SkillCurriculum.volume == volume,
                SkillCurriculum.section.like(f"{section_code}%"),
            )
            .order_by(SkillCurriculum.id.asc())
            .first()
        )
        if fallback_row and fallback_row[0]:
            return str(fallback_row[0]).strip()
        return ""

    def _is_invalid_section_title(section_title):
        sec = str(section_title or "").strip()
        if not sec:
            return True
        # Example invalid value from filename parse: "1-1_-"
        if re.fullmatch(r"\d+\s*-\s*\d+[_\-\s]*", sec):
            return True
        return False

    def _write_postprocess_skip_report(report_path, *, volume, section, mode, reason, script_name):
        lines = [
            "# DOCX Formula Asset Postprocess Skipped Report",
            f"- volume: `{volume}`",
            f"- section: `{section}`",
            f"- mode: `{mode}`",
            "- dry_run: `True`",
            f"- postprocess_script: `{script_name}`",
            f"- postprocess_skipped_reason: `{reason}`",
            "",
            "Summary:",
            "- processed_records=0",
            "- formula_assets_total=0",
            "- auto_applied_records=0",
            "",
        ]
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _group_docx_with_optional_pdf(paths):
        grouped = []
        by_stem = defaultdict(list)
        for p in paths:
            stem = os.path.splitext(os.path.basename(str(p or "")))[0].lower()
            by_stem[stem].append(p)
        consumed = set()
        for stem, items in by_stem.items():
            docx = [x for x in items if str(x).lower().endswith((".docx", ".doc"))]
            pdfs = [x for x in items if str(x).lower().endswith(".pdf")]
            if docx:
                for d in docx:
                    enrich_pdf = pdfs[0] if pdfs else None
                    grouped.append((d, enrich_pdf))
                    consumed.add(d)
                    if enrich_pdf:
                        consumed.add(enrich_pdf)
        for p in paths:
            if p in consumed:
                continue
            grouped.append((p, None))
        return grouped

    import_policy = dict(kwargs.pop("import_policy", {}) or {})
    enable_formula_postprocess = bool(import_policy.get("enable_formula_postprocess", False))
    enable_formula_auto_apply = bool(import_policy.get("enable_formula_auto_apply", False))
    formula_postprocess_mode = str(import_policy.get("formula_postprocess_mode", "convert_only") or "convert_only").strip()
    docx_formula_source_mode = str(import_policy.get("docx_formula_source_mode", "auto_detect") or "auto_detect").strip()
    enable_formula_detailed_report = bool(import_policy.get("enable_formula_detailed_report", False))
    confidence_threshold = float(import_policy.get("auto_fill_confidence_threshold", 0.85) or 0.85)
    with app_context:
        try:
            grouped_files = _group_docx_with_optional_pdf(file_paths)
            total_files = len(grouped_files)
            task_queue.put(f"INFO: ????隞餃?嚗 {total_files} ??亙雿?..")

            for idx, (file_path, optional_pdf_path) in enumerate(grouped_files, 1):
                filename = os.path.basename(file_path)
                if filename.startswith('~$') or filename.startswith('.'):
                    continue

                task_queue.put(f"INFO: [{idx}/{total_files}] 甇???: {filename} ...")
                if optional_pdf_path:
                    task_queue.put(
                        f"INFO: [{idx}/{total_files}] Optional enrich PDF detected and will be used."
                    )
                try:
                    textbook_processor.process_textbook_file(
                        file_path, 
                        curriculum_info=curriculum_info, 
                        queue=task_queue, 
                        skip_code_gen=skip_code_gen,
                        import_policy=import_policy,
                        optional_enrich_pdf_path=optional_pdf_path,
                        **kwargs
                    )
                    if docx_formula_source_mode == "converted_docx_latex":
                        task_queue.put("INFO: docx_formula_source_mode=converted_docx_latex, skipping formula asset OCR/pix2tex postprocess.")
                    elif enable_formula_postprocess:
                        try:
                            is_docx = str(file_path or "").lower().endswith((".docx", ".doc"))
                            canonical_volume = str(curriculum_info.get("volume") or "").strip()
                            canonical_section = _resolve_canonical_section_title(filename) if is_docx else ""
                            report_dir = os.path.join("reports", "import_debug")
                            os.makedirs(report_dir, exist_ok=True)
                            safe_vol = _safe_report_token(canonical_volume or "unknown")
                            safe_sec = _safe_report_token(canonical_section or "unknown_section")
                            run_mode = "write" if enable_formula_auto_apply else "dry_run"
                            report_path = os.path.join(
                                report_dir,
                                f"{safe_vol}_{safe_sec}_docx_formula_asset_pool_{run_mode}_report.md",
                            )

                            if is_docx and formula_postprocess_mode == "convert_only":
                                task_queue.put("INFO: formula_postprocess_mode=convert_only, skipping OCR postprocess.")
                            elif is_docx and formula_postprocess_mode in ("local_ocr", "local_first_gemini_fallback"):
                                if _is_invalid_section_title(canonical_section):
                                    _write_postprocess_skip_report(
                                        report_path,
                                        volume=canonical_volume,
                                        section=str(canonical_section or ""),
                                        mode=formula_postprocess_mode,
                                        reason="missing_canonical_section",
                                        script_name="docx_formula_asset_pix2tex_backfill.py",
                                    )
                                    task_queue.put(
                                        f"WARN: 蝻箏? canonical section嚗歇?仿??臬敺撘????eport={report_path}"
                                    )
                                else:
                                    script_path = os.path.join(
                                        current_app.root_path,
                                        "scripts",
                                        "docx_formula_asset_pix2tex_backfill.py",
                                    )
                                    cmd = [
                                        sys.executable,
                                        script_path,
                                        "--volume",
                                        canonical_volume,
                                        "--section",
                                        canonical_section,
                                        "--formula-ocr-backend",
                                        "pix2tex",
                                        "--confidence-threshold",
                                        str(confidence_threshold),
                                        "--report",
                                        report_path,
                                    ]
                                    if enable_formula_auto_apply:
                                        cmd.append("--write")
                                    else:
                                        cmd.append("--dry-run")
                                    task_queue.put("INFO: ?? DOCX ?臬敺撘???...")
                                    run = subprocess.run(
                                        cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        cwd=current_app.root_path,
                                        check=False,
                                    )
                                    if run.returncode == 0:
                                        task_queue.put(f"INFO: ?砍?敺?????report={report_path}")
                                    else:
                                        task_queue.put("WARN: Formula postprocess failed for this file; continuing.")
                            else:
                                task_queue.put("INFO: DOCX source mode does not require formula OCR postprocess.")
                        except Exception as post_err:
                            task_queue.put(f"WARN: ?砍?敺????仃?? {post_err}")
                except Exception as e:
                    task_queue.put(f"ERROR: 瑼? {filename} ??憭望?: {e}")
                
                if 'uploads' in file_path and os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass

            task_queue.put("SUCCESS: ???璆剖???")
        except Exception as e:
            task_queue.put(f"ERROR: 隞餃????潛??芷??隤? {str(e)}")
        finally:
            task_queue.put("END_OF_STREAM")

# ==========================================
# Textbook Importer
# ==========================================

MATH_B_FORCED_VOLUMES = frozenset({"數學B1", "數學B2", "數學B3", "數學B4"})


def is_vocational_mathb_volume(volume: str) -> bool:
    v = str(volume or "").strip()
    if not v:
        return False
    v = re.sub(r"\s+", "", v)
    if v in MATH_B_FORCED_VOLUMES:
        return True
    return bool(
        re.fullmatch(r"數學B[1-4]", v, flags=re.IGNORECASE)
        or re.fullmatch(r"MathB[1-4]", v, flags=re.IGNORECASE)
    )


def apply_mathb_import_policy(curriculum_info: dict, import_policy: dict, *, filenames=None, logger=None) -> bool:
    """Force converted_docx_latex import policy for ?擃摮?B1?4."""
    volume = str((curriculum_info or {}).get("volume", "") or "").strip()
    if not is_vocational_mathb_volume(volume):
        return False
    curriculum_info["curriculum"] = "vocational"
    import_policy["docx_formula_source_mode"] = "converted_docx_latex"
    import_policy["enable_formula_postprocess"] = False
    import_policy["enable_formula_auto_apply"] = False
    import_policy["enable_formula_detailed_report"] = False
    import_policy["formula_postprocess_mode"] = "convert_only"
    log = logger.info if logger is not None else (lambda *_a, **_k: None)
    log("[IMPORT POLICY] mathB_forced_converted_docx_latex=true")
    log("[IMPORT POLICY] mathB_forced_curriculum=vocational")
    log("[IMPORT POLICY] formula_assets_ocr_pix2tex_disabled=true")
    for fn in filenames or []:
        name = os.path.basename(str(fn or ""))
        if name and not name.lower().endswith("_latex.docx"):
            warn_msg = f"[IMPORT WARNING] converted_docx_latex_expected_latex_suffix=true filename={name}"
            if logger is not None:
                logger.warning(warn_msg)
            else:
                log(warn_msg)
    return True


@core_bp.route('/textbook_importer', methods=['GET', 'POST'])
@login_required
def admin_textbook_importer():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('Permission denied', 'error')
        return redirect(url_for('dashboard'))

    api_key, key_source = resolve_gemini_api_key()
    has_gemini_api_key = bool(api_key)
    current_app.logger.info(f"[AI KEY] source={key_source or 'none'}")

    if request.method == 'POST':
        if not has_gemini_api_key:
            flash("Please configure Gemini API Key before importing.", "danger")
            return redirect(url_for('core.admin_textbook_importer'))

        target_files = []
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        single_file = request.files.get('textbook_pdf')
        batch_files = request.files.getlist('textbook_folder')
        
        if single_file and single_file.filename != '':
            path = os.path.join(upload_dir, secure_filename(single_file.filename))
            single_file.save(path)
            target_files.append(path)
        elif batch_files and len(batch_files) > 0 and batch_files[0].filename != '':
            for f in batch_files:
                if f.filename != '' and (f.filename.endswith('.pdf') or f.filename.endswith('.docx')):
                    path = os.path.join(upload_dir, secure_filename(os.path.basename(f.filename)))
                    f.save(path)
                    target_files.append(path)

        if target_files:
            task_id = str(uuid.uuid4())
            q = queue.Queue()
            TASK_QUEUES[task_id] = q

            curriculum_info = {
                'curriculum': request.form.get('curriculum'),
                'publisher': request.form.get('publisher'),
                'grade': request.form.get('grade'),
                'volume': request.form.get('volume')
            }
            skip_code = request.form.get('skip_code_gen') == 'on'
            outline_only = request.form.get('outline_only') == 'true'
            toc_pages = int(request.form.get('toc_pages', 5))
            execution_arch = str(request.form.get('execution_arch', 'native') or 'native').strip().lower()
            confidence_threshold_raw = request.form.get('auto_fill_confidence_threshold', '0.85')
            try:
                confidence_threshold = float(confidence_threshold_raw)
            except Exception:
                confidence_threshold = 0.85
            confidence_threshold = max(0.0, min(1.0, confidence_threshold))
            import_policy = {
                "execution_arch": execution_arch,
                "docx_primary": True,
                "pdf_optional_enrich": True,
                "auto_post_ocr_ai": True,
                "auto_backfill_high_confidence": True,
                "review_low_confidence": True,
                "auto_fill_confidence_threshold": confidence_threshold,
                "preserve_rollback_metadata": True,
                "enable_formula_postprocess": request.form.get("enable_formula_postprocess") in ("on", "true"),
                "enable_formula_auto_apply": request.form.get("enable_formula_auto_apply") in ("on", "true"),
                "enable_formula_detailed_report": request.form.get("enable_formula_detailed_report") in ("on", "true"),
                "formula_postprocess_mode": str(
                    request.form.get("formula_postprocess_mode", "convert_only") or "convert_only"
                ).strip(),
                "docx_formula_source_mode": str(
                    request.form.get("docx_formula_source_mode", "converted_docx_latex") or "converted_docx_latex"
                ).strip(),
            }
            if import_policy["docx_formula_source_mode"] == "converted_docx_latex":
                import_policy["enable_formula_postprocess"] = False
                import_policy["enable_formula_auto_apply"] = False
                import_policy["enable_formula_detailed_report"] = False
                import_policy["formula_postprocess_mode"] = "convert_only"
                current_app.logger.info("[IMPORT POLICY] converted_docx_latex_forced_skip_formula_postprocess=true")

            apply_mathb_import_policy(
                curriculum_info,
                import_policy,
                filenames=[os.path.basename(p) for p in target_files],
                logger=current_app.logger,
            )

            app = current_app._get_current_object()
            threading.Thread(
                target=background_processing,
                args=(target_files, q, app.app_context(), curriculum_info, skip_code),
                kwargs={
                    'outline_only': outline_only,
                    'toc_pages': toc_pages,
                    'import_policy': import_policy,
                }
            ).start()

            return redirect(url_for('core.importer_status', task_id=task_id))
        else:
            flash('Only PDF or DOCX files are allowed.', 'warning')

    return render_template(
        'textbook_importer.html',
        has_gemini_api_key=has_gemini_api_key,
        ai_settings_url='/admin/ai_prompt_settings'
    )


def background_processing_v2(file_path, task_queue, app_context, curriculum_info):
    """Antigravity V2: converted_docx_latex only, no OCR/PDF/pix2tex."""
    with app_context:
        try:
            from core.textbook_processor_v2 import process_textbook_file_v2

            filename = os.path.basename(file_path)
            task_queue.put(f"INFO: [antigravity] 開始處理 DOCX 題目檔：{filename}")
            result = process_textbook_file_v2(file_path, curriculum_info, task_queue)
            if result.get("success"):
                task_queue.put(
                    "INFO: [antigravity] DOCX 題目匯入完成 "
                    f"inserted={result.get('inserted', 0)} "
                    f"updated={result.get('updated', 0)} "
                    f"total={result.get('total', 0)} "
                    f"blocks={result.get('blocks', 0)} "
                    f"self_assessment={result.get('self_assessment_imported', 0)} "
                    f"skills=0 curriculums=0 "
                    f"needs_review={result.get('needs_review', 0)}"
                )
            else:
                task_queue.put(f"ERROR: [antigravity] DOCX 題目匯入失敗：{result.get('error', 'unknown')}")
        except Exception as exc:
            err_type = type(exc).__name__
            task_queue.put(f"ERROR: [antigravity] {err_type}: {exc}")
            current_app.logger.error(
                f"[antigravity] background_processing_v2 failed: {exc}\n{traceback.format_exc()}"
            )
        finally:
            task_queue.put("END_OF_STREAM")


def background_processing_v2_pdf_outline(
    file_path, task_queue, app_context, curriculum_info, *, toc_pages: int = 5
):
    """Antigravity V2: parse PDF outline and sync SkillCurriculum via V2 pipeline."""
    with app_context:
        try:
            from core.textbook_processor_v2 import process_pdf_outline_v2

            filename = os.path.basename(file_path)
            task_queue.put(
                f"INFO: [antigravity] Starting PDF outline parse with toc_pages={toc_pages}"
            )
            task_queue.put(f"INFO: [antigravity] 開始處理 PDF 大綱檔：{filename}")
            result = process_pdf_outline_v2(
                file_path,
                curriculum_info,
                task_queue,
                toc_pages=toc_pages,
            )
            if result.get("success"):
                task_queue.put(
                    "INFO: [antigravity] PDF 大綱同步完成 "
                    f"sections_created={result.get('sections_created', 0)} "
                    f"sections_updated={result.get('sections_updated', 0)}"
                )
            else:
                task_queue.put(
                    f"ERROR: [antigravity] PDF 大綱同步失敗：{result.get('error', 'unknown')}"
                )
        except Exception as exc:
            err_type = type(exc).__name__
            task_queue.put(f"ERROR: [antigravity] {err_type}: {exc}")
            current_app.logger.error(
                f"[antigravity] background_processing_v2_pdf_outline failed: {exc}\n"
                f"{traceback.format_exc()}"
            )
        finally:
            task_queue.put("END_OF_STREAM")


@core_bp.route('/textbook_importer_v2', methods=['GET', 'POST'])
@login_required
def admin_textbook_importer_v2():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('甈?銝雲', 'error')
        return redirect(url_for('dashboard'))

    api_key, key_source = resolve_gemini_api_key()
    has_gemini_api_key = bool(api_key)
    current_app.logger.info(f"[AI KEY] source={key_source or 'none'}")

    if request.method == 'POST':
        if not has_gemini_api_key:
            flash("Please configure Gemini API Key before importing.", "danger")
            return redirect(url_for('core.admin_textbook_importer_v2'))

        import_mode = str(request.form.get('import_mode', 'docx_problems') or 'docx_problems').strip()
        if import_mode not in ('docx_problems', 'pdf_outline'):
            import_mode = 'docx_problems'

        upload_file = request.files.get('textbook_file') or request.files.get('textbook_docx')
        if not upload_file or not upload_file.filename:
            if import_mode == 'pdf_outline':
                flash('Only PDF files (.pdf) are allowed.', 'warning')
            else:
                flash('Only Word files (.docx) are allowed for LaTeX conversion.', 'warning')
            return redirect(url_for('core.admin_textbook_importer_v2'))

        filename_lower = str(upload_file.filename).lower()
        if import_mode == 'pdf_outline':
            if not filename_lower.endswith('.pdf'):
                flash('Please upload a valid .pdf file.', 'warning')
                return redirect(url_for('core.admin_textbook_importer_v2'))
        elif not filename_lower.endswith('.docx'):
            flash('Please upload a valid .docx file.', 'warning')
            return redirect(url_for('core.admin_textbook_importer_v2'))

        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        original_filename = str(upload_file.filename or "").strip()
        _, ext = os.path.splitext(original_filename.lower())
        if import_mode == 'pdf_outline':
            if ext != '.pdf':
                if '.pdf' in original_filename.lower():
                    ext = '.pdf'
                else:
                    flash(
                        '錯誤：解析大綱樹模式 (pdf_outline) 必須上傳真實的 PDF 檔案。',
                        'danger',
                    )
                    return redirect(url_for('core.admin_textbook_importer_v2'))
        elif ext != '.docx':
            ext = '.docx'

        saved_filename = f"{uuid.uuid4().hex}{ext}"
        saved_path = os.path.join(upload_dir, saved_filename)
        upload_file.save(saved_path)
        current_app.logger.info(
            f"[UPLOAD_SAVE] import_mode={import_mode!r} ext={ext!r} saved_path={saved_path!r}"
        )

        upload_names = resolve_upload_filenames(original_filename, saved_filename)
        current_app.logger.info(
            f"[UPLOAD_FILENAME] original_filename={upload_names['original_filename']}"
        )
        current_app.logger.info(
            f"[UPLOAD_FILENAME] saved_filename={upload_names['saved_filename']}"
        )
        current_app.logger.info(
            f"[UPLOAD_FILENAME] parse_filename={upload_names['parse_filename']}"
        )

        filename_meta = parse_textbook_filename_metadata(upload_names['parse_filename'])
        section_code = str((filename_meta or {}).get('section_code') or '').strip()
        if str((filename_meta or {}).get('source_scope') or '') == 'chapter_self_assessment':
            section_code = ''

        try:
            grade_val = int(request.form.get('grade', 10))
        except (TypeError, ValueError):
            grade_val = 10

        curriculum_info = {
            'curriculum': request.form.get('curriculum', 'vocational') or 'vocational',
            'publisher': request.form.get('publisher', 'longteng') or 'longteng',
            'grade': grade_val,
            'volume': request.form.get('volume', '數學B1') or '數學B1',
            'section_code': section_code,
            'import_mode': import_mode,
            'original_filename': upload_names['original_filename'],
            'saved_filename': upload_names['saved_filename'],
            'parse_filename': upload_names['parse_filename'],
            'chapter_index': (filename_meta or {}).get('chapter_index'),
            'source_scope': (filename_meta or {}).get('source_scope'),
        }

        task_id = str(uuid.uuid4())
        q = queue.Queue()
        TASK_QUEUES[task_id] = q
        app = current_app._get_current_object()

        if import_mode == 'pdf_outline':
            try:
                toc_pages = int(request.form.get('toc_pages', 5))
            except (TypeError, ValueError):
                toc_pages = 5
            toc_pages = max(1, min(10, toc_pages))
            current_app.logger.info(
                f"[antigravity] import_mode=pdf_outline toc_pages={toc_pages} file={saved_path}"
            )
            threading.Thread(
                target=background_processing_v2_pdf_outline,
                args=(saved_path, q, app.app_context(), curriculum_info),
                kwargs={'toc_pages': toc_pages},
            ).start()
        else:
            apply_mathb_import_policy(
                curriculum_info,
                {},
                filenames=[upload_names['parse_filename']],
                logger=current_app.logger,
            )
            skip_code_gen = request.form.get('skip_code_gen') == 'on'
            if skip_code_gen:
                current_app.logger.info("[antigravity] skip_code_gen=true (V2 蝺楝銝孛?澆憿Ⅳ??)")
            current_app.logger.info(f"[antigravity] import_mode=docx_problems file={saved_path}")
            threading.Thread(
                target=background_processing_v2,
                args=(saved_path, q, app.app_context(), curriculum_info),
            ).start()

        return redirect(
            url_for('core.importer_status', task_id=task_id, import_mode=import_mode)
        )

    return render_template(
        'textbook_importer_v2.html',
        has_gemini_api_key=has_gemini_api_key,
        ai_settings_url='/admin/ai_prompt_settings',
    )


@core_bp.route('/importer/status/<task_id>')
@login_required
def importer_status(task_id):
    if task_id not in TASK_QUEUES:
        flash('Import completed with warnings. Please review logs.', 'warning')
        return redirect(url_for('core.admin_textbook_importer'))
    import_mode = str(request.args.get('import_mode', 'docx_problems') or 'docx_problems').strip()
    if import_mode not in ('docx_problems', 'pdf_outline'):
        import_mode = 'docx_problems'
    return render_template(
        'importer_status.html',
        task_id=task_id,
        import_mode=import_mode,
    )

@core_bp.route('/importer/stream/<task_id>')
@login_required
def importer_stream(task_id):
    def event_stream():
        q = TASK_QUEUES.get(task_id)
        if not q:
            yield _format_sse_data("END_OF_STREAM")
            return
        while True:
            msg = q.get()
            normalized = _coerce_progress_message(msg)
            yield _format_sse_data(normalized)
            if normalized == "END_OF_STREAM":
                TASK_QUEUES.pop(task_id, None)
                break
    return Response(
        stream_with_context(event_stream()),
        content_type="text/event-stream; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ==========================================
# Database Maintenance (??????
# ==========================================

@core_bp.route('/db_maintenance', methods=['GET', 'POST'])
@login_required
def db_maintenance():
    def sanitize_dataframe_for_excel(df):
        if df is None:
            return pd.DataFrame()

        # ??NaN/NaT ?改????????頦??綽??殉??????剜??
        df = df.copy()
        df = df.where(pd.notnull(df), "")

        # object ????改?????選????int/float/bool ????賹?
        for col in df.columns:
            if str(df[col].dtype) == "object":
                df[col] = df[col].apply(lambda x: "" if x is None else str(x))

        return df

    def safe_sheet_name(name):
        name = str(name)
        name = re.sub(r'[\[\]\:\*\?\/\\]', '_', name)
        return name[:31]

    if not (current_user.is_admin or current_user.role == "teacher"):
        return redirect(url_for('dashboard'))

    core_scope_form_state = _core_scope_form_state({"scope_mode": "all"})
    core_scope_options = _collect_core_scope_options()
    import_job_id = session.get("last_import_job_id")
    import_job_payload = get_large_result_from_server_store(import_job_id, kind="import") if import_job_id else None
    import_result_missing = bool(import_job_id and import_job_payload is None)
    import_summary = None
    if import_job_payload:
        stored_result = import_job_payload.get("result", {})
        import_summary = summarize_import_result(stored_result)

    if request.method == 'POST':
        action = request.form.get('action')
        table_name = request.form.get('table_name')
        mode = str(request.form.get('mode', 'core')).strip().lower()
        if mode not in ('core', 'full'):
            mode = 'core'
        core_scope_filters = _normalize_core_scope_filters(request.form)
        core_scope_form_state = _core_scope_form_state(core_scope_filters)
        core_scope_options = _collect_core_scope_options(
            {
                "curriculum": core_scope_filters.get("curriculum", ""),
                "grade": str(core_scope_filters.get("grade")) if core_scope_filters.get("grade") is not None else "",
                "volume": core_scope_filters.get("volume", ""),
                "chapter": core_scope_filters.get("chapter", ""),
            }
        )
        confirm_full_clear = str(request.form.get('confirm_full_clear', '')).strip()
        core_clear_confirm = str(request.form.get('core_clear_confirm', '')).strip()

        if action == 'export_db':
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            inspector = inspect(db.engine)
            detected_tables = inspector.get_table_names()
            current_app.logger.info(f"INFO: CORE_TABLES_EXPORT = {list(CORE_TABLES)}")
            # core ?????頛魂??蝞??閰??萄???頦???inspector ?荒???穿???謘曇????
            if mode == 'core':
                export_tables = list(CORE_TABLES)
            else:
                export_tables = list(dict.fromkeys(CORE_TABLES + detected_tables))

            for table in export_tables:
                try:
                    # ??? read_sql_table謜??剜???壇???read_sql_query?橫?????萄??謘橫?????謚?????
                    try:
                        df = pd.read_sql_table(table, db.engine)
                    except Exception:
                        try:
                            df = pd.read_sql_query(f"SELECT * FROM {table}", db.engine)
                        except Exception:
                            # ????踐???閰??萄???謒?Sheet?橫?????鞈剛??萄??剜???
                            df = pd.DataFrame()
                            current_app.logger.warning(f"??穿???萄??謘潔??謅??撖⊥??蝞???Sheet: {table}")
                    df = sanitize_dataframe_for_excel(df)
                    # ?????object ????????對??殉???橫???float/bool ????怨?謒?re.sub ???芰???
                    for col in df.columns:
                        if str(df[col].dtype) == "object":
                            df[col] = df[col].apply(lambda x: re.sub(r'[\x00-\x1f\x7f-\x9f]', '', x))

                    sheet = safe_sheet_name(table)
                    df.to_excel(writer, sheet_name=sheet, index=False)
                    current_app.logger.info(f"INFO: exporting {mode} table {table} ({len(df)} rows)")
                except Exception as e:
                    current_app.logger.exception(f"Export failed for table {table}")
                    if mode == 'core':
                        try:
                            pd.DataFrame().to_excel(writer, sheet_name=safe_sheet_name(table), index=False)
                            current_app.logger.warning(f"INFO: core export fallback to empty sheet {table}")
                        except Exception:
                            current_app.logger.exception(f"Export fallback failed for table {table}")
            writer.close()
            output.seek(0)
            return send_file(output, download_name=f"kumon_math_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", as_attachment=True)

        elif action == 'clear_all_data':
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            if mode == 'full':
                if confirm_full_clear != FULL_CONFIRM_TOKEN:
                    flash('Full clear requires confirmation token YES_DELETE_ALL.', 'danger')
                    return redirect(url_for('core.db_maintenance'))
                system_tables = {"sqlite_sequence"}
                clear_tables = [t for t in all_tables if t not in system_tables and not str(t).startswith("sqlite_")]
                failed_tables = []
                try:
                    # SQLite frequently enforces FK ordering; disable checks during full wipe.
                    db.session.execute(text("PRAGMA foreign_keys = OFF"))
                    for table_name_to_clear in clear_tables:
                        try:
                            db.session.execute(text(f"DELETE FROM \"{table_name_to_clear}\""))
                            current_app.logger.info(f"INFO: clearing full table {table_name_to_clear}")
                        except Exception as e:
                            failed_tables.append((table_name_to_clear, str(e)))
                            current_app.logger.warning(
                                f"FULL_CLEAR_FAIL table={table_name_to_clear} error={e}"
                            )
                    # Reset autoincrement counters when present.
                    if "sqlite_sequence" in all_tables:
                        db.session.execute(text("DELETE FROM sqlite_sequence"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise
                finally:
                    try:
                        db.session.execute(text("PRAGMA foreign_keys = ON"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()

                if failed_tables:
                    job_id = put_large_result_in_server_store(
                        {
                            "action": "clear_all_data",
                            "mode": "full",
                            "failed_tables": failed_tables,
                            "cleared_table_count": len(clear_tables) - len(failed_tables),
                        },
                        kind="maintenance",
                    )
                    session["last_db_maintenance_job_id"] = job_id
                    safe_flash_message(
                        f"full clear partially failed: {len(failed_tables)} table(s). See maintenance job {job_id}.",
                        "danger",
                    )
                else:
                    flash(f"資料庫已完成 full 清空 ({len(clear_tables)} tables)", "warning")
            else:
                if core_scope_filters.get("scope_mode") != "all":
                    flash("高職數學 B 硬清除僅支援『全部教材資料』範圍。", "warning")
                    return render_template(
                        'db_maintenance.html',
                        tables=sorted(inspector.get_table_names()),
                        core_scope_options=core_scope_options,
                        core_scope_form_state=core_scope_form_state,
                        core_scope_summary_text=_core_scope_summary(core_scope_filters),
                        core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
                    )
                if core_clear_confirm != CORE_CLEAR_CONFIRM_TOKEN:
                    flash(f"請輸入確認字串 {CORE_CLEAR_CONFIRM_TOKEN} 才能執行清除。", "danger")
                    return render_template(
                        'db_maintenance.html',
                        tables=sorted(inspector.get_table_names()),
                        core_scope_options=core_scope_options,
                        core_scope_form_state=core_scope_form_state,
                        core_scope_summary_text=_core_scope_summary(core_scope_filters),
                        core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
                    )
                if core_scope_filters.get("scope_mode") == "filtered" and not _core_scope_has_any_filter(core_scope_filters):
                    flash(
                        "Filtered mode requires at least one filter; otherwise switch to all scope.",
                        "danger",
                    )
                    return render_template(
                        'db_maintenance.html',
                        tables=sorted(inspector.get_table_names()),
                        core_scope_options=core_scope_options,
                        core_scope_form_state=core_scope_form_state,
                        core_scope_summary_text=_core_scope_summary(core_scope_filters),
                        core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
                    )
                result = _hard_clear_vocational_math_b_core(execute=True)
                deleted = result.get("deleted", {})
                remaining = _vocational_math_b_remaining_check()
                all_clean = all(int(v or 0) == 0 for v in remaining.values())
                if all_clean:
                    flash(
                        "高職數學 B 核心教材資料已清空："
                        f"textbook_examples={deleted.get('textbook_examples', 0)}, "
                        f"skills_info={deleted.get('skills_info', 0)}, "
                        f"skill_curriculum={deleted.get('skill_curriculum', 0)}, "
                        f"skill_prerequisites={deleted.get('skill_prerequisites', 0)}, "
                        f"skill_family_bridge={deleted.get('skill_family_bridge', 0)}",
                        "success",
                    )
                else:
                    flash(f"高職數學 B 清除後仍有殘留：{remaining}", "danger")
        elif action == 'preview_core_clear':
            if core_scope_filters.get("scope_mode") != "all":
                flash("高職數學 B 硬清除預覽僅支援『全部教材資料』範圍。", "warning")
                return render_template(
                    'db_maintenance.html',
                    tables=sorted(inspect(db.engine).get_table_names()),
                    core_scope_options=core_scope_options,
                    core_scope_form_state=core_scope_form_state,
                    core_scope_summary_text=_core_scope_summary(core_scope_filters),
                    core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
                )
            if core_scope_filters.get("scope_mode") == "filtered" and not _core_scope_has_any_filter(core_scope_filters):
                flash(
                    "Filtered mode requires at least one filter for preview.",
                    "warning",
                )
                return render_template(
                    'db_maintenance.html',
                    tables=sorted(inspect(db.engine).get_table_names()),
                    core_scope_options=core_scope_options,
                    core_scope_form_state=core_scope_form_state,
                    core_scope_summary_text=_core_scope_summary(core_scope_filters),
                    core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
                )
            result = _hard_clear_vocational_math_b_core(execute=False)
            deleted = result.get("deleted", {})
            remaining = _vocational_math_b_remaining_check()
            all_clean_before = all(int(v or 0) == 0 for v in remaining.values())
            flash(
                (
                    "高職數學 B 硬清除預覽："
                    f"textbook_examples={deleted.get('textbook_examples', 0)}, "
                    f"skills_info={deleted.get('skills_info', 0)}, "
                    f"skill_curriculum={deleted.get('skill_curriculum', 0)}, "
                    f"skill_prerequisites={deleted.get('skill_prerequisites', 0)}, "
                    f"skill_family_bridge={deleted.get('skill_family_bridge', 0)}, "
                    f"all_clean_before={str(all_clean_before).lower()}"
                ),
                'warning'
            )
            return render_template(
                'db_maintenance.html',
                tables=sorted(inspect(db.engine).get_table_names()),
                core_scope_options=core_scope_options,
                core_scope_form_state=core_scope_form_state,
                core_scope_summary_text=_core_scope_summary(core_scope_filters),
                core_preview_stats=deleted,
                core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
            )

        elif action == 'batch_import_folder':
            files = request.files.getlist('files')
            success_count, error_count = 0, 0
            for file in files:
                if file and file.filename.endswith(('.csv', '.xlsx', '.xls')):
                    try:
                        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
                        df.columns = [str(c).lower().strip() for c in df.columns]
                        for _, row in df.iterrows():
                            if pd.isna(row.get('skill_id')): continue
                            item = SkillCurriculum(
                                curriculum=row.get('curriculum', 'general'),
                                grade=int(row.get('grade', 10)),
                                volume=row.get('volume', ''),
                                chapter=row.get('chapter', ''),
                                section=row.get('section', ''),
                                skill_id=str(row['skill_id']).strip(),
                                display_order=int(row.get('display_order', 0)) if 'display_order' in row else 0,
                                difficulty_level=int(row.get('difficulty_level', 1)) if 'difficulty_level' in row else 1
                            )
                            db.session.add(item)
                        success_count += 1
                    except: error_count += 1
            db.session.commit()
            flash(f'Batch import completed. success={success_count}, error={error_count}', 'success')
        
        elif table_name and action == 'clear_data':
             try:
                 db.session.execute(text(f"DELETE FROM {table_name}"))
                 db.session.commit()
                 flash(f'Table {table_name} cleared.', 'success')
             except Exception as e:
                 db.session.rollback()
                 flash(f'??芰?: {e}', 'danger')

        return redirect(url_for('core.db_maintenance'))

    return render_template(
        'db_maintenance.html',
        tables=sorted(inspect(db.engine).get_table_names()),
        core_scope_options=core_scope_options,
        core_scope_form_state=core_scope_form_state,
        core_scope_summary_text=_core_scope_summary(_normalize_core_scope_filters(core_scope_form_state)),
        last_import_job_id=import_job_id,
        last_import_summary=import_summary,
        import_result_missing=import_result_missing,
        core_clear_confirm_token=CORE_CLEAR_CONFIRM_TOKEN,
    )


@core_bp.route('/db_maintenance/core_scope_options', methods=['GET'])
@login_required
def db_maintenance_core_scope_options():
    if not (current_user.is_admin or current_user.role == "teacher"):
        return jsonify({"error": "forbidden"}), 403
    filters = {
        "curriculum": request.args.get("curriculum", ""),
        "grade": request.args.get("grade", ""),
        "volume": request.args.get("volume", ""),
        "chapter": request.args.get("chapter", ""),
    }
    return jsonify(_collect_core_scope_options(filters))


def _flash_import_status(summary, job_id):
    status = (summary or {}).get("status") or (summary or {}).get("final_status") or "failed"
    imported_rows = int((summary or {}).get("imported_rows", 0) or 0)
    failed_rows = int((summary or {}).get("failed_rows", 0) or 0)
    warning_count = int((summary or {}).get("warning_count", 0) or 0)
    if status == "completed":
        safe_flash_message(
            f"Import completed successfully. imported={imported_rows}, failed={failed_rows}. See job {job_id}.",
            "success",
        )
    elif status == "completed_with_warnings":
        safe_flash_message(
            f"Import completed with warnings. imported={imported_rows}, failed={failed_rows}, warnings={warning_count}. See job {job_id}.",
            "warning",
        )
    else:
        safe_flash_message(
            f"Import failed. failed={failed_rows}. See job {job_id}.",
            "danger",
        )


@core_bp.route('/admin/maintenance/clear_vocational_math_core', methods=['POST'])
@login_required
def clear_vocational_math_core():
    if not _is_admin_or_teacher():
        return jsonify({"ok": False, "error": "forbidden"}), 403

    payload = request.get_json(silent=True) or request.form
    mode = str((payload or {}).get("mode", "dry_run")).strip().lower()
    if mode not in ("dry_run", "execute"):
        mode = "dry_run"

    confirm_token = str((payload or {}).get("confirm_token", "") or "").strip()
    if mode == "execute" and confirm_token != VOCATIONAL_MATH_B_CONFIRM_TOKEN:
        return jsonify(
            {
                "ok": False,
                "mode": mode,
                "error": "invalid_confirm_token",
                "required_confirm_token": VOCATIONAL_MATH_B_CONFIRM_TOKEN,
            }
        ), 400

    cleanup_result = _hard_clear_vocational_math_b_core(execute=(mode == "execute"))
    remaining = _vocational_math_b_remaining_check()
    all_clean = all(int(v or 0) == 0 for v in remaining.values())
    return jsonify(
        {
            "ok": True,
            "mode": mode,
            "deleted": cleanup_result["deleted"],
            "remaining_check": remaining,
            "planned_tables": cleanup_result["plan"],
            "missing_columns": cleanup_result["missing_columns"],
            "confirm_token_required": VOCATIONAL_MATH_B_CONFIRM_TOKEN,
            "all_clean": all_clean,
        }
    )


@core_bp.route('/admin/maintenance/verify_vocational_math_clean', methods=['GET'])
@login_required
def verify_vocational_math_clean():
    if not _is_admin_or_teacher():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    checks = _vocational_math_b_remaining_check()
    return jsonify(
        {
            "ok": True,
            "all_zero": all(int(v or 0) == 0 for v in checks.values()),
            "remaining_check": checks,
        }
    )

@core_bp.route('/upload_db', methods=['POST'])
@login_required
def upload_db():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('Permission denied', 'danger')
        return redirect(url_for('core.db_maintenance'))

    if 'file' not in request.files:
        flash('????澗??', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Please select a file to upload.', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if file and (file.filename.endswith('.xlsx')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        mode = str(request.form.get('mode', 'core')).strip().lower()
        if mode not in ('core', 'full'):
            mode = 'core'
        confirm_full_clear = str(request.form.get('confirm_full_clear', '')).strip()
        
        try:
            success, message = import_excel_to_db(
                filepath,
                mode=mode,
                confirm_full_clear=confirm_full_clear
            )
            summary = summarize_import_result((success, message))
            job_id = put_large_result_in_server_store(
                {
                    "route": "upload_db",
                    "filename": filename,
                    "mode": mode,
                    "success": success,
                    "message": message,
                    "summary": summary,
                },
                kind="import",
            )
            session["last_import_job_id"] = job_id
            _flash_import_status(summary, job_id)
        except Exception as e:
            job_id = put_large_result_in_server_store(
                {
                    "route": "upload_db",
                    "filename": filename,
                    "mode": mode,
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "summary": summarize_import_result((False, str(e))),
                },
                kind="import",
            )
            session["last_import_job_id"] = job_id
            safe_flash_message(f"Import failed. See job {job_id}.", 'danger')
            
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return redirect(url_for('core.db_maintenance'))
    else:
        flash('?瞉???芰?????蹌?.xlsx', 'danger')
        return redirect(url_for('core.db_maintenance'))

@core_bp.route('/admin/import_textbook_examples', methods=['POST'])
@login_required
def import_textbook_examples():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('Permission denied', 'danger')
        return redirect(url_for('core.db_maintenance'))
    
    if 'file' not in request.files: return redirect(url_for('core.db_maintenance'))
    file = request.files['file']
    if file.filename == '': return redirect(url_for('core.db_maintenance'))
        
    if file:
        try:
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_dir): os.makedirs(upload_dir)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            mode = str(request.form.get('mode', 'core')).strip().lower()
            if mode not in ('core', 'full'):
                mode = 'core'
            confirm_full_clear = str(request.form.get('confirm_full_clear', '')).strip()
            success, message = import_excel_to_db(
                filepath,
                mode=mode,
                confirm_full_clear=confirm_full_clear
            )
            if os.path.exists(filepath): os.remove(filepath)

            summary = summarize_import_result((success, message))
            job_id = put_large_result_in_server_store(
                {
                    "route": "import_textbook_examples",
                    "filename": filename,
                    "mode": mode,
                    "success": success,
                    "message": message,
                    "summary": summary,
                },
                kind="import",
            )
            session["last_import_job_id"] = job_id
            _flash_import_status(summary, job_id)
        except Exception as e:
            job_id = put_large_result_in_server_store(
                {
                    "route": "import_textbook_examples",
                    "filename": secure_filename(file.filename) if file and file.filename else "",
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "summary": summarize_import_result((False, str(e))),
                },
                kind="import",
            )
            session["last_import_job_id"] = job_id
            safe_flash_message(f"Import failed. See job {job_id}.", 'error')
            
    return redirect(url_for('core.db_maintenance'))

# ==========================================
# Curriculum Management (?方??祆０????)
# ==========================================

@core_bp.route('/curriculum', methods=['GET', 'POST'])
@login_required
def admin_curriculum():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            new_curr = SkillCurriculum(
                skill_id=request.form.get('skill_id'),
                curriculum=request.form.get('curriculum'),
                grade=int(request.form.get('grade')) if request.form.get('grade') else 0,
                volume=request.form.get('volume'),
                chapter=request.form.get('chapter'),
                section=request.form.get('section'),
                paragraph=request.form.get('paragraph'),
                difficulty_level=int(request.form.get('difficulty_level', 1)),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(new_curr)
            db.session.commit()
            flash('??????', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'????剜??: {str(e)}', 'error')
        return redirect(url_for('core.admin_curriculum'))

    # ??蛛隤冽???????50 ?蛛?????????????
    selected, filters_data = handle_curriculum_filters(request)
    
    # ??貔嚗嗉???selected ?????
    query = SkillCurriculum.query.join(SkillInfo)
    if selected['f_curriculum'] != 'all': 
        query = query.filter(SkillCurriculum.curriculum == selected['f_curriculum'])
    
    if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit():
        query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
        
    if selected['f_volume'] != 'all':
        query = query.filter(SkillCurriculum.volume == selected['f_volume'])

    if selected['f_chapter'] != 'all':
        query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])

    if selected['f_section'] != 'all':
        query = query.filter(SkillCurriculum.section == selected['f_section'])

    items = query.order_by(SkillCurriculum.grade, SkillCurriculum.volume, SkillCurriculum.display_order).limit(200).all()

    curriculum_map = {
        'junior_high': 'junior_high',
        'general': 'general',
        'technical': 'technical',
        'elementary': 'elementary',
    }
    grade_map = {str(g): str(g) for g in filters_data['grades']}

    return render_template('admin_curriculum.html', 
                           items=items,
                           filters=filters_data,
                           selected_filters=selected,
                           curriculum_map=curriculum_map,
                           grade_map=grade_map,
                           skills=SkillInfo.query.all())

@core_bp.route('/curriculum/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_curriculum(id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False}), 403
    try:
        curr = SkillCurriculum.query.get_or_404(id)
        curr.curriculum = request.form.get('curriculum')
        curr.grade = request.form.get('grade')
        curr.volume = request.form.get('volume')
        curr.chapter = request.form.get('chapter')
        curr.section = request.form.get('section')
        curr.skill_id = request.form.get('skill_id')
        curr.display_order = request.form.get('display_order')
        curr.difficulty_level = request.form.get('difficulty_level')
        db.session.commit()
        flash('?皝????', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'?皝??剜??: {e}', 'error')
    return redirect(url_for('core.admin_curriculum'))

@core_bp.route('/curriculum/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_curriculum(id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False}), 403
    try:
        curr = SkillCurriculum.query.get_or_404(id)
        db.session.delete(curr)
        db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500

# ==========================================
# Skills Management (???鞈??
# ==========================================

@core_bp.route('/skills')
@login_required
def admin_skills():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    # ?方撒??V2.0 ????謘??叟??????
    selected, filters_data = handle_curriculum_filters(request)
    
    # 關聯 JOIN 查詢，投影 SkillInfo 與 SkillCurriculum 兩個 model
    query = db.session.query(SkillInfo, SkillCurriculum).join(
        SkillCurriculum,
        SkillInfo.skill_id == SkillCurriculum.skill_id
    )
    
    # --- 篩選條件過濾器 ---
    if selected['f_curriculum'] != 'all': 
        query = query.filter(SkillCurriculum.curriculum == selected['f_curriculum'])
    if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit(): 
        query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
    if selected['f_volume'] != 'all':
        query = query.filter(SkillCurriculum.volume == selected['f_volume'])
    if selected['f_chapter'] != 'all': 
        query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])
    if selected['f_section'] != 'all': 
        query = query.filter(SkillCurriculum.section == selected['f_section'])
    
    # 依 display_order 排序
    skills_data = (
        query
        .distinct()
        .order_by(
            SkillCurriculum.display_order.asc(),
            SkillInfo.skill_id.asc()
        )
        .all()
    )
    
    # 只讀檢查
    print(f"=== [admin_skills DEBUG] ===")
    print(f"skills_data length: {len(skills_data)}")
    if len(skills_data) > 0:
        first_item = skills_data[0]
        print(f"First item type: {type(first_item)}")
        print(f"First item is tuple: {isinstance(first_item, tuple)}")
        if isinstance(first_item, tuple):
            print(f"First item length: {len(first_item)}")
            if len(first_item) >= 2:
                print(f"first_item[0] is SkillInfo: {isinstance(first_item[0], SkillInfo)}")
                print(f"first_item[1] is SkillCurriculum: {isinstance(first_item[1], SkillCurriculum)}")
                print(f"first_item[0].skill_id: {first_item[0].skill_id}")
                print(f"first_item[1].display_order: {first_item[1].display_order}")
    print(f"============================")

    skills = [item[0] for item in skills_data]
    gencode_status_map = {}
    root_candidates = [
        Path(current_app.root_path),
        Path(current_app.root_path).parent,
        Path(current_app.root_path).parent.parent,
    ]
    project_root = next(
        (p for p in root_candidates if (p / "skills").exists()),
        Path(current_app.root_path),
    )
    skills_dir = project_root / "skills"
    drafts_dir = project_root / "reports" / "gencode_closed_loop" / "drafts"
    for s in skills:
        sid = str(s.skill_id)
        formal_rel = f"skills/{sid}.py"
        draft_rel = f"reports/gencode_closed_loop/drafts/{sid}.py"
        formal_abs = skills_dir / f"{sid}.py"
        draft_abs = drafts_dir / f"{sid}.py"
        formal_exists = formal_abs.exists()
        draft_exists = draft_abs.exists()
        if formal_exists:
            gencode_status_map[sid] = {
                "status": "generated",
                "label": "已產生",
                "button_label": "重新產生",
                "formal_exists": True,
                "draft_exists": draft_exists,
                "formal_path": formal_rel,
                "draft_path": draft_rel if draft_exists else "",
                "formal_abs_path": str(formal_abs),
                "draft_abs_path": str(draft_abs) if draft_exists else "",
            }
        elif draft_exists:
            gencode_status_map[sid] = {
                "status": "draft",
                "label": "草稿中",
                "button_label": "繼續",
                "formal_exists": False,
                "draft_exists": True,
                "formal_path": formal_rel,
                "draft_path": draft_rel,
                "formal_abs_path": str(formal_abs),
                "draft_abs_path": str(draft_abs),
            }
        else:
            gencode_status_map[sid] = {
                "status": "missing",
                "label": "未產生",
                "button_label": "AI 產生",
                "formal_exists": False,
                "draft_exists": False,
                "formal_path": formal_rel,
                "draft_path": draft_rel,
                "formal_abs_path": str(formal_abs),
                "draft_abs_path": str(draft_abs),
            }

    v3_gencode_status_map = _load_skills_v3_gencode_status_map(
        [str(s.skill_id) for s in skills]
    )

    from core.gencode.v3_production_publish_service import V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS
    return render_template('admin_skills.html', 
                           skills_data=skills_data,
                           skills=skills_data,
                           gencode_status_map=gencode_status_map,
                           v3_gencode_status_map=v3_gencode_status_map,
                           v3_publish_allowed_skill_ids=V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS,
                           filters=filters_data,
                           selected_filters=selected,
                           grade_map={str(g):str(g) for g in filters_data['grades']},
                           curriculum_map={'junior_high': '國中', 'general': '普高'},
                           username=current_user.username)

@core_bp.route('/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    data = request.form
    if db.session.get(SkillInfo, data['skill_id']):
        flash('Invalid skill ID.', 'danger')
        return redirect(url_for('core.admin_skills'))
    try:
        new_skill = SkillInfo(
            skill_id=data['skill_id'],
            skill_en_name=data['skill_en_name'],
            skill_ch_name=data['skill_ch_name'],
            category=data['category'],
            description=data['description'],
            input_type=data.get('input_type', 'text'),
            gemini_prompt=data['gemini_prompt'],
            consecutive_correct_required=int(data['consecutive_correct_required']),
            is_active=data.get('is_active') == 'on',
            order_index=int(data.get('order_index', 999))
        )
        db.session.add(new_skill)
        db.session.commit()
        flash('??????', 'success')
    except Exception as e:
        flash(f'??芰?: {e}', 'danger')
    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/edit/<skill_id>', methods=['POST'])
@login_required
def admin_edit_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    data = request.form
    try:
        skill.skill_en_name = data['skill_en_name']
        skill.skill_ch_name = data['skill_ch_name']
        skill.category = data['category']
        skill.description = data['description']
        skill.input_type = data.get('input_type', 'text')
        skill.gemini_prompt = data['gemini_prompt']
        skill.consecutive_correct_required = int(data['consecutive_correct_required'])
        skill.is_active = data.get('is_active') == 'on'
        skill.suggested_prompt_1 = data.get('suggested_prompt_1', '')
        skill.suggested_prompt_2 = data.get('suggested_prompt_2', '')
        skill.suggested_prompt_3 = data.get('suggested_prompt_3', '')
        db.session.commit()
        flash('?皝????', 'success')
    except Exception as e:
        flash(f'??芰?: {e}', 'danger')
    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/delete/<skill_id>', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    try:
        db.session.delete(skill)
        db.session.commit()
        flash('??畸????', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'??畸??剜?? (??迎?????????: {e}', 'danger')
    return redirect(url_for('core.admin_skills'))


@core_bp.route('/skills/toggle/<skill_id>', methods=['POST'])
@login_required
def admin_toggle_skill(skill_id):
    skill = db.get_or_404(SkillInfo, skill_id)
    skill.is_active = not skill.is_active
    db.session.commit()
    flash(f'???鞈Ｘ?{"?賹?" if skill.is_active else "?謚秋?"}', 'success')
    return redirect(url_for('core.admin_skills'))

@core_bp.route('/skills/<skill_id>/regenerate', methods=['POST'])
@login_required
def admin_regenerate_skill_code(skill_id):
    try:
        from core.code_generator import auto_generate_skill_code
        # [?賣? ?綜竣??????綜筐??梁捂??箸?????Architect?潑?踐???????Prompt
        result = auto_generate_skill_code(skill_id, queue=None, force_architect_refresh=True)
        success = result[0] if isinstance(result, tuple) else result
        return jsonify({"success": success, "message": "?賹????" if success else "?剜??"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/skills/<skill_id>/details', methods=['GET'])
@login_required
def admin_get_skill_details(skill_id):
    skill = db.session.get(SkillInfo, skill_id)
    if not skill: return jsonify({'success': False}), 404
    return jsonify({
        'success': True,
        'data': {
            'skill_id': skill.skill_id,
            'skill_ch_name': skill.skill_ch_name,
            'skill_en_name': skill.skill_en_name,
            'category': skill.category,
            'description': skill.description,
            'input_type': skill.input_type,
            'consecutive_correct_required': skill.consecutive_correct_required,
            'gemini_prompt': skill.gemini_prompt,
            'suggested_prompt_1': skill.suggested_prompt_1,
            'suggested_prompt_2': skill.suggested_prompt_2,
            'suggested_prompt_3': skill.suggested_prompt_3
        }
    })


@core_bp.route('/admin/gencode/skills/<skill_id>/run-auto-pipeline', methods=['POST'])
@login_required
def admin_run_gencode_auto_pipeline(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", True))
    allow_runtime_ready = bool(payload.get("allow_runtime_ready", False))
    try:
        result = run_gencode_auto_pipeline(
            skill_id=skill_id,
            dry_run=dry_run,
            allow_runtime_ready=allow_runtime_ready,
            write_pending_files=True,
        )
        result["ok"] = bool(result.get("ok", True))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "skill_id": skill_id, "error": str(e)}), 500


@core_bp.route('/admin/gencode/skills/<skill_id>/phase1', methods=['POST'])
@login_required
def admin_run_gencode_phase1(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", True))
    spec_mode = str(payload.get("spec_mode", "ai_first_induce_from_sources")).strip() or "ai_first_induce_from_sources"
    try:
        apply_ai_runtime_settings()
        result = run_gencode_phase1(skill_id=skill_id, dry_run=dry_run, spec_mode=spec_mode)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "phase": "phase1", "skill_id": skill_id, "error": str(e)}), 500


@core_bp.route('/admin/gencode/skills/<skill_id>/phase2', methods=['POST'])
@login_required
def admin_run_gencode_phase2(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", True))
    accepted_problem_types = payload.get("accepted_problem_types", [])
    excluded_example_ids = payload.get("excluded_example_ids", [])
    try:
        result = run_gencode_phase2(
            skill_id=skill_id,
            accepted_problem_types=accepted_problem_types if isinstance(accepted_problem_types, list) else [],
            excluded_example_ids=excluded_example_ids if isinstance(excluded_example_ids, list) else [],
            dry_run=dry_run,
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "phase": "phase2", "skill_id": skill_id, "error": str(e)}), 500


@core_bp.route('/admin/gencode/skills/<skill_id>/phase3', methods=['POST'])
@login_required
def admin_run_gencode_phase3(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", True))
    accepted_generator_keys = payload.get("accepted_generator_keys", [])
    try:
        result = run_gencode_phase3_package(
            skill_id=skill_id,
            accepted_generator_keys=accepted_generator_keys if isinstance(accepted_generator_keys, list) else [],
            dry_run=dry_run,
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "phase": "phase3", "skill_id": skill_id, "error": str(e)}), 200


@core_bp.route('/admin/gencode/skills/<skill_id>/publish-check', methods=['POST'])
@login_required
def admin_run_gencode_publish_check(skill_id):
    # Debug-only endpoint. Official workflow remains Phase 1/2/3 and
    # publish-check is embedded inside Phase 3 response.
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", True))
    try:
        result = run_gencode_publish_check(skill_id=skill_id, dry_run=dry_run)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "phase": "publish_check", "skill_id": skill_id, "error": str(e)}), 500


@core_bp.route('/admin/gencode/skills/<skill_id>/publish-draft', methods=['POST'])
@login_required
def admin_publish_gencode_draft(skill_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    confirm = bool(payload.get("confirm", False))
    allow_runtime_ready = bool(payload.get("allow_runtime_ready", False))
    try:
        result = publish_gencode_draft_skill(
            skill_id=skill_id,
            confirm=confirm,
            allow_runtime_ready=allow_runtime_ready,
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "phase": "publish", "skill_id": skill_id, "error": str(e)}), 500


@core_bp.route('/admin/gencode/classifier/register', methods=['POST'])
@login_required
def admin_register_gencode_classifier_rulepack():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({"success": False, "register_status": "failed", "error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    skill_id = str(payload.get("skill_id", "")).strip()
    confirm = bool(payload.get("confirm", False))
    if not skill_id:
        return jsonify({
            "success": False,
            "register_status": "failed",
            "skill_id": "",
            "summary_message": "缺少 skill_id。",
            "warnings": [],
            "blockers": ["missing_skill_id"],
            "validation_errors": ["missing_skill_id"],
        }), 400
    try:
        result = register_classifier_rulepack_from_draft(skill_id=skill_id, confirm=confirm)
        ok = bool(result.get("ok", False))
        status = str(result.get("status", "failed"))
        success = ok and status in {"preview", "registered"}
        summary = ""
        if status == "preview" and success:
            summary = "預覽完成：可以註冊 classifier rule pack。尚未覆寫正式 YAML。"
        elif status == "registered" and success:
            summary = "註冊成功：classifier rule pack 已更新。下次 Phase 1 將使用 rule_pack。"
        else:
            summary = str(result.get("error", "")).strip() or "註冊失敗。"
        return jsonify({
            "success": success,
            "register_status": "registered" if status == "registered" and success else ("preview" if status == "preview" and success else "failed"),
            "skill_id": skill_id,
            "draft_path": str(result.get("draft_path", "")).strip(),
            "formal_yaml_path": str(result.get("formal_rulepack_path", "")).strip(),
            "backup_path": str(result.get("backup_path", "")).strip(),
            "summary_message": summary,
            "warnings": [],
            "blockers": [] if success else [str(result.get("error", "register_failed")).strip() or "register_failed"],
            "validation_errors": [] if success else [str(result.get("error", "register_failed")).strip() or "register_failed"],
            "classifier_source_after_register": "rule_pack" if (success and status == "registered") else None,
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            "success": False,
            "register_status": "failed",
            "skill_id": skill_id,
            "summary_message": "註冊失敗。",
            "warnings": [],
            "blockers": [str(e)],
            "validation_errors": [str(e)],
            "classifier_source_after_register": None,
        }), 500

@core_bp.route('/api/promote_question', methods=['POST'])
@login_required
def admin_promote_question():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    try:
        data = request.get_json()
        question_id = data.get('question_id')
        skill_id = data.get('skill_id')

        # 1. ?鈭歹??蹌阡謢?
        upload_entry = db.session.get(StudentUploadedQuestion, question_id)
        if not upload_entry:
            return jsonify({'success': False, 'message': 'Target skill not found'}), 404

        # 2. ?梁???????
        new_example = TextbookExample(
            skill_id=skill_id,
            source_curriculum="StudentUpload",
            source_volume="N/A",
            source_chapter="N/A",
            source_section="N/A",
            source_description=f"Student Upload (ID: {upload_entry.student_id})",
            problem_text=upload_entry.ocr_content,
            correct_answer=upload_entry.ai_solution, # Using ai_solution as rough draft for correct answer
            difficulty_level=1
        )
        db.session.add(new_example)

        # 3. ?皝?????
        upload_entry.status = 'approved'
        upload_entry.predicted_skill_id = skill_id

        db.session.commit()

        # 4. ?怨?謒?????
        try:
            # [STEP 1] Force Architect to re-analyze examples and update SkillInfo.gemini_prompt
            print(f"Triggering Architect for {skill_id}...")
            from core.prompt_architect import generate_v9_spec
            generate_v9_spec(skill_id, model_tag='cloud_pro')

            # [STEP 2] Now call Coder -> Uses NEW Prompt
            from core.code_generator import auto_generate_skill_code
            # Run in background ideally, but here synchronous for feedback
            auto_generate_skill_code(skill_id, queue=None)
        except Exception as e:
            print(f"Auto-generate failed: {e}") 
            # We don't fail the promotion if generation fails, just log it.

        return jsonify({'success': True, 'message': 'Prerequisites updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Examples Management (?????)
# ==========================================

@core_bp.route('/examples', methods=['GET'])
@login_required
def admin_examples():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))
    
    # ?方撒??V2.0 ????
    selected, filters_data = handle_curriculum_filters(request)
    page = request.args.get('page', 1, type=int)
    
    # ?梁??????SkillCurriculum ????堆撰隤?????
    query = db.session.query(TextbookExample).outerjoin(SkillInfo, TextbookExample.skill_id == SkillInfo.skill_id).join(SkillCurriculum, TextbookExample.skill_id == SkillCurriculum.skill_id)
    
    if selected['f_curriculum'] != 'all': 
        query = query.filter(SkillCurriculum.curriculum == selected['f_curriculum'])
    if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit(): 
        query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
    if selected['f_volume'] != 'all':
        query = query.filter(SkillCurriculum.volume == selected['f_volume'])
    if selected['f_chapter'] != 'all':
        query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])
    if selected['f_section'] != 'all':
        query = query.filter(SkillCurriculum.section == selected['f_section'])
    
    pagination = query.order_by(
        SkillCurriculum.display_order.asc(), 
        TextbookExample.id.asc()
    ).paginate(page=page, per_page=50, error_out=False)
    page_formula_stats = {
        "total": len(pagination.items),
        "with_formula_assets": 0,
        "with_formula_image_placeholder": 0,
        "with_formula_missing": 0,
        "missing_no_asset": 0,
        "image_placeholder_no_asset": 0,
    }
    for ex in pagination.items:
        meta = {}
        try:
            if getattr(ex, "notes", None):
                meta = json.loads(ex.notes)
        except Exception:
            meta = {}
        ex._image_assets = meta.get("image_assets", []) if isinstance(meta, dict) else []
        ex._has_image = bool(meta.get("has_image")) if isinstance(meta, dict) else False
        ex._needs_image_conversion = any(bool(a.get("needs_image_conversion")) for a in ex._image_assets if isinstance(a, dict))
        ex._has_real_image_asset = any(
            isinstance(a, dict) and bool(a.get("display_path") or (a.get("path") and str(a.get("path")).lower().endswith((".png", ".jpg", ".jpeg", ".webp"))))
            for a in ex._image_assets
        )
        ex._missing_image_asset = ex._has_image and not ex._has_real_image_asset
        ex._formula_assets = meta.get("formula_assets", []) if isinstance(meta, dict) and isinstance(meta.get("formula_assets"), list) else []
        ex._formula_assets_count = len(ex._formula_assets)
        ptxt = str(getattr(ex, "problem_text", "") or "")
        ex._has_formula_image_placeholder = bool(re.search(r"\[FORMULA_IMAGE_\d+\]", ptxt))
        ex._has_formula_missing_placeholder = "[FORMULA_MISSING]" in ptxt
        ex._needs_formula_review = bool(meta.get("needs_formula_review")) if isinstance(meta, dict) else False
        ex._formula_missing = bool(meta.get("formula_missing")) if isinstance(meta, dict) else False
        ex._needs_review = bool(meta.get("needs_review")) if isinstance(meta, dict) else False
        ex._formula_status, ex._formula_status_label, ex._formula_status_badge = _derive_formula_status(
            formula_assets_count=ex._formula_assets_count,
            has_formula_image_placeholder=ex._has_formula_image_placeholder,
            has_formula_missing_placeholder=ex._has_formula_missing_placeholder,
            needs_formula_review=ex._needs_formula_review,
        )

        if ex._formula_assets_count > 0:
            page_formula_stats["with_formula_assets"] += 1
        if ex._has_formula_image_placeholder:
            page_formula_stats["with_formula_image_placeholder"] += 1
        if ex._has_formula_missing_placeholder:
            page_formula_stats["with_formula_missing"] += 1
        if ex._formula_status == "missing_no_asset":
            page_formula_stats["missing_no_asset"] += 1
        if ex._formula_status == "image_placeholder_no_asset":
            page_formula_stats["image_placeholder_no_asset"] += 1

    gencode_status_map = _load_examples_gencode_status_map(pagination.items)
    
    return render_template('admin_examples.html', 
                           pagination=pagination, 
                           filters=filters_data,
                           selected_filters=selected,
                           page_formula_stats=page_formula_stats,
                           gencode_status_map=gencode_status_map,
                           curriculum_map={'junior_high': '???', 'general': '?獢?'},
                           grade_map={str(g):str(g) for g in filters_data['grades']}, 
                           skills=SkillInfo.query.all(), 
                           username=current_user.username)


@core_bp.route('/admin/examples/<int:textbook_example_id>/gencode_v3_dryrun', methods=['POST'])
@login_required
def admin_run_example_v3_dryrun(textbook_example_id: int):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    redirect_query = str(request.form.get("redirect_query", "") or "").strip()
    redirect_target = url_for("core.admin_examples")
    if redirect_query:
        redirect_target = f"{redirect_target}?{redirect_query.lstrip('?')}"

    try:
        skill_id = str(request.form.get("skill_id", "") or "").strip()
        if not skill_id:
            textbook_example = db.session.get(TextbookExample, textbook_example_id)
            if textbook_example is None:
                raise ValueError("textbook_example_not_found")
            skill_id = str(textbook_example.skill_id or "").strip()
        if not skill_id:
            raise ValueError("missing_skill_id")

        from core.gencode.services.admin_gencode_action_service import (
            run_admin_v3_dryrun_for_example,
        )

        raw_conn = db.engine.raw_connection()
        try:
            run_admin_v3_dryrun_for_example(
                conn=raw_conn,
                textbook_example_id=textbook_example_id,
                skill_id=skill_id,
            )
        finally:
            raw_conn.close()

        flash("V3 自動出題草稿已產生", "success")
    except Exception as e:
        flash(f"失敗原因: {e}", "danger")
    return redirect(redirect_target)


@core_bp.route('/admin/examples/<int:textbook_example_id>/gencode_v3_smoke', methods=['POST'])
@login_required
def admin_run_example_v3_smoke(textbook_example_id: int):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    redirect_query = str(request.form.get("redirect_query", "") or "").strip()
    redirect_target = url_for("core.admin_examples")
    if redirect_query:
        redirect_target = f"{redirect_target}?{redirect_query.lstrip('?')}"

    try:
        skill_id = str(request.form.get("skill_id", "") or "").strip()
        if not skill_id:
            textbook_example = db.session.get(TextbookExample, textbook_example_id)
            if textbook_example is None:
                raise ValueError("textbook_example_not_found")
            skill_id = str(textbook_example.skill_id or "").strip()
        if not skill_id:
            raise ValueError("missing_skill_id")

        from core.gencode.services.admin_gencode_action_service import (
            run_admin_v3_smoke_for_example,
        )

        raw_conn = db.engine.raw_connection()
        try:
            run_admin_v3_smoke_for_example(
                conn=raw_conn,
                textbook_example_id=textbook_example_id,
                skill_id=skill_id,
            )
        finally:
            raw_conn.close()

        flash("V3 Smoke 測試通過", "success")
    except ValueError as e:
        flash(f"失敗原因: {e}", "danger")
    except Exception as e:
        flash(f"失敗原因: {e}", "danger")
    return redirect(redirect_target)


@core_bp.route('/admin/examples/<int:textbook_example_id>/gencode_v3_verify', methods=['POST'])
@login_required
def admin_run_example_v3_verify(textbook_example_id: int):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    redirect_query = str(request.form.get("redirect_query", "") or "").strip()
    redirect_target = url_for("core.admin_examples")
    if redirect_query:
        redirect_target = f"{redirect_target}?{redirect_query.lstrip('?')}"

    try:
        skill_id = str(request.form.get("skill_id", "") or "").strip()
        if not skill_id:
            textbook_example = db.session.get(TextbookExample, textbook_example_id)
            if textbook_example is None:
                raise ValueError("textbook_example_not_found")
            skill_id = str(textbook_example.skill_id or "").strip()
        if not skill_id:
            raise ValueError("missing_skill_id")

        from core.gencode.services.admin_gencode_action_service import (
            mark_admin_v3_example_verified,
        )

        raw_conn = db.engine.raw_connection()
        try:
            mark_admin_v3_example_verified(
                conn=raw_conn,
                textbook_example_id=textbook_example_id,
                skill_id=skill_id,
            )
        finally:
            raw_conn.close()

        flash("V3 元件已標記為 verified", "success")
    except ValueError as e:
        flash(f"失敗原因: {e}", "danger")
    except Exception as e:
        flash(f"失敗原因: {e}", "danger")
    return redirect(redirect_target)


def _parse_admin_force_publish_flag(raw) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes"}


def _resolve_admin_v3_publish_roots() -> tuple[str, str]:
    project_root = str(request.form.get("project_root", "") or "").strip()
    staging_root = str(request.form.get("staging_root", "") or "").strip()
    if not project_root:
        project_root = str(current_app.config.get("GENCODE_V3_PUBLISH_PROJECT_ROOT", "") or "").strip()
    if not staging_root:
        staging_root = str(current_app.config.get("GENCODE_V3_PUBLISH_STAGING_ROOT", "") or "").strip()
    if not project_root or not staging_root:
        raise ValueError("unsafe_publish_roots_not_configured")
    return project_root, staging_root


@core_bp.route('/admin/skills/<skill_id>/gencode_v3_publish', methods=['POST'])
@login_required
def admin_run_skill_v3_publish(skill_id: str):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return redirect(url_for('dashboard'))

    redirect_query = str(request.form.get("redirect_query", "") or "").strip()
    redirect_target = url_for("core.admin_skills")
    if redirect_query:
        redirect_target = f"{redirect_target}?{redirect_query.lstrip('?')}"

    try:
        if not _parse_admin_force_publish_flag(request.form.get("force_publish")):
            flash("正式發布需要明確確認", "danger")
            return redirect(redirect_target)

        skill_key = str(skill_id or "").strip()
        if not skill_key:
            raise ValueError("missing_skill_id")

        project_root, staging_root = _resolve_admin_v3_publish_roots()

        from core.gencode.services.admin_gencode_action_service import (
            run_admin_v3_publish_for_skill,
        )

        raw_conn = db.engine.raw_connection()
        try:
            result = run_admin_v3_publish_for_skill(
                conn=raw_conn,
                skill_id=skill_key,
                project_root=project_root,
                staging_root=staging_root,
                force_publish=True,
            )
        finally:
            raw_conn.close()

        if str(result.get("status", "")).strip() == "production_published":
            flash("V3 技能已正式發布", "success")
        elif str(result.get("status", "")).strip() == "rolled_back_after_failed_production_smoke":
            flash(
                f"正式發布失敗並已自動回滾: {result.get('production_smoke_error', 'production smoke failed')}",
                "danger",
            )
        else:
            flash(f"正式發布未完成: {result.get('status', 'unknown')}", "warning")
    except ValueError as e:
        flash(f"失敗原因: {e}", "danger")
    except Exception as e:
        flash(f"失敗原因: {e}", "danger")
    return redirect(redirect_target)


@core_bp.route('/examples/add', methods=['POST'])
@login_required
def admin_add_example():
    try:
        new_ex = TextbookExample(
            skill_id=request.form.get('skill_id'),
            problem_text=request.form.get('problem_text'),
            correct_answer=request.form.get('correct_answer', ''),
            detailed_solution=request.form.get('detailed_solution', ''),
            difficulty_level=int(request.form.get('difficulty_level', 1))
        )
        db.session.add(new_ex)
        db.session.commit()
        flash('????????', 'success')
    except Exception as e:
        flash(f'????剜??: {e}', 'danger')
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/delete/<int:example_id>', methods=['POST'])
@login_required
def admin_delete_example(example_id):
    ex = db.session.get(TextbookExample, example_id)
    if ex:
        db.session.delete(ex)
        db.session.commit()
        flash('??畸????', 'success')
    return redirect(url_for('core.admin_examples'))

@core_bp.route('/examples/<int:example_id>/details', methods=['GET'])
@login_required
def admin_get_example_details(example_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        ex = db.session.get(TextbookExample, example_id)
        if not ex:
            return jsonify({'success': False, 'message': 'Target unit not found'}), 404
        return jsonify({
            'success': True,
            'data': {
                'id': ex.id,
                'skill_id': ex.skill_id,
                'problem_text': ex.problem_text or '',
                'correct_answer': ex.correct_answer or '',
                'detailed_solution': ex.detailed_solution or '',
                'difficulty_level': ex.difficulty_level or 1,
                'notes': ex.notes or ''
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/examples/edit/<int:example_id>', methods=['POST'])
@login_required
def admin_edit_example(example_id):
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('Permission denied', 'error')
        return redirect(url_for('core.admin_examples'))
    try:
        ex = db.session.get(TextbookExample, example_id)
        if ex:
            ex.skill_id = request.form.get('skill_id')
            ex.problem_text = request.form.get('problem_text')
            ex.correct_answer = request.form.get('correct_answer', '')
            ex.detailed_solution = request.form.get('detailed_solution', '')
            ex.difficulty_level = int(request.form.get('difficulty_level', 1))
            db.session.commit()
            flash('?皝????', 'success')
    except Exception as e:
        flash(f'?皝??剜??: {e}', 'danger')
    return redirect(url_for('core.admin_examples'))

# ==========================================
# Prompt Management (Prompt ?桀??)
# ==========================================

@core_bp.route('/api/skills/<skill_id>/prompts', methods=['GET'])
@login_required
def api_get_skill_prompts(skill_id):
    prompts = SkillGenCodePrompt.query.filter_by(skill_id=skill_id).all()
    data = [{'id': p.id, 'model_tag': p.model_tag, 'system_prompt': p.system_prompt, 'user_prompt_template': p.user_prompt_template} for p in prompts]
    return jsonify({'success': True, 'data': data})

@core_bp.route('/api/skills/<skill_id>/prompts/save', methods=['POST'])
@login_required
def api_save_skill_prompt(skill_id):
    try:
        data = request.get_json()
        model_tag = data.get('model_tag')
        prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, model_tag=model_tag).first()
        
        if prompt:
            prompt.user_prompt_template = data.get('user_prompt_template')
            prompt.system_prompt = data.get('system_prompt')
            prompt.version += 1
        else:
            prompt = SkillGenCodePrompt(
                skill_id=skill_id, model_tag=model_tag,
                user_prompt_template=data.get('user_prompt_template'),
                system_prompt=data.get('system_prompt'), version=1
            )
            db.session.add(prompt)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Prompt saved'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@core_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
@login_required
def api_delete_skill_prompt(prompt_id):
    try:
        prompt = db.session.get(SkillGenCodePrompt, prompt_id)
        if prompt:
            db.session.delete(prompt)
            db.session.commit()
        return jsonify({'success': True, 'message': '??畸????'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --------------------------------------------------------
# ???鼎????瞏叟???api_delete_skill_prompt ???
# --------------------------------------------------------

# ==========================================
# Prerequisites Management (?????鞈??
# ==========================================

@core_bp.route('/admin/prerequisites')
@login_required
def admin_prerequisites():
    if not (current_user.is_admin or current_user.role == "teacher"):
        flash('Permission denied', 'error')
        return redirect(url_for('dashboard'))
    
    # --- A. ?瞉 V2.0 ????謘潭扔??---
    # ?????????? Session ?殉朵??蹍L ??塗?蹓?????閰制??嚗?
    selected, filters_data = handle_curriculum_filters(request)
    
    # --- B. ?梁?????鈭亙眺 ---
    query = db.session.query(SkillInfo, SkillCurriculum).join(
        SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id
    ).filter(SkillInfo.is_active.is_(True))
    
    # --- ?乾??????????---
    if selected['f_curriculum'] != 'all': 
        query = query.filter(SkillCurriculum.curriculum == selected['f_curriculum'])
    if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit(): 
        query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
    if selected['f_volume'] != 'all': 
        query = query.filter(SkillCurriculum.volume == selected['f_volume'])
    if selected['f_chapter'] != 'all': 
        query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])
    if selected['f_section'] != 'all': # ?乾?謕?
        query = query.filter(SkillCurriculum.section == selected['f_section'])
    
    results = query.order_by(SkillCurriculum.display_order).all()
    
    # (?????? skills_list ??湔???...)
    skills_list = []
    seen_skill_ids = set()
    for skill_info, skill_curriculum in results:
        if skill_info.skill_id in seen_skill_ids: continue
        seen_skill_ids.add(skill_info.skill_id)
        skill_info.grade = skill_curriculum.grade
        skill_info.volume = skill_curriculum.volume
        skill_info.chapter = skill_curriculum.chapter
        skill_info.prereq_count = len(skill_info.prerequisites)
        skills_list.append(skill_info)

    # --- C. ?????????皜??????? ---
    return render_template('admin_prerequisites.html',
                           skills=skills_list,
                           filters=filters_data,             # ?舀????
                           selected_filters=selected,        # ????UndefinedError
                           curriculum_map={'junior_high': '???', 'general': '?獢?'},
                           grade_map={str(g):str(g) for g in filters_data['grades']},
                           username=current_user.username)

@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['GET'])
@login_required
def api_get_prerequisites(skill_id):
    try:
        skill = db.session.get(SkillInfo, skill_id)
        if not skill: return jsonify({"success": False, "message": "Skill not found"}), 404
        data = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in skill.prerequisites]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/<string:skill_id>/prerequisites', methods=['POST'])
@login_required
def api_add_prerequisite(skill_id):
    if not (current_user.is_admin or current_user.role == "teacher"): return jsonify({"success": False}), 403
    try:
        data = request.get_json()
        prereq_id = data.get('prereq_id')
        target = db.session.get(SkillInfo, skill_id)
        prereq = db.session.get(SkillInfo, prereq_id)
        
        if not target or not prereq: return jsonify({"success": False, "message": "Skill not found"}), 404
        if skill_id == prereq_id: return jsonify({"success": False, "message": "????閮???豢?"}), 400
        
        if prereq not in target.prerequisites:
            target.prerequisites.append(prereq)
            db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/<string:skill_id>/prerequisites/<string:prereq_id>', methods=['DELETE'])
@login_required
def api_remove_prerequisite(skill_id, prereq_id):
    if not (current_user.is_admin or current_user.role == "teacher"): return jsonify({"success": False}), 403
    try:
        target = db.session.get(SkillInfo, skill_id)
        prereq = db.session.get(SkillInfo, prereq_id)
        
        if target and prereq and prereq in target.prerequisites:
            target.prerequisites.remove(prereq)
            db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/skills/search', methods=['GET'])
@login_required
def api_search_skills():
    term = request.args.get('term', '').strip()
    if not term: return jsonify({"results": []})
    
    query = db.session.query(SkillInfo).filter(
        SkillInfo.is_active.is_(True),
        db.or_(
            SkillInfo.skill_id.like(f'%{term}%'),
            SkillInfo.skill_ch_name.like(f'%{term}%')
        )
    ).limit(20)
    
    results = [{'id': s.skill_id, 'text': f"{s.skill_ch_name} ({s.skill_id})"} for s in query.all()]
    return jsonify({"results": results})

@core_bp.route('/admin/init_db', methods=['POST'])
@login_required
def init_db_route():
    try:
        # ?輯撒??models ??? init_db
        init_db(db.engine)
        flash('?????迎?????', 'success')
    except Exception as e:
        flash(f'?豲??謘潔??? {e}', 'error')
    return redirect(url_for('core.db_maintenance'))

@core_bp.route('/admin/import_skills', methods=['POST'])
@login_required
def import_skills():
    if not current_user.is_admin: return jsonify({"success": False}), 403
    try:
        from core.data_importer import import_skills_from_json
        count = import_skills_from_json()
        return jsonify({"success": True, "message": f"Imported {count} skills."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/admin/import_curriculum', methods=['POST'])
@login_required
def import_curriculum():
    if not current_user.is_admin: return jsonify({"success": False}), 403
    try:
        from core.data_importer import import_curriculum_from_json
        count = import_curriculum_from_json()
        return jsonify({"success": True, "message": f"Imported {count} curriculum rows."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==========================================
# Dropdown APIs (????閰制????)
# ==========================================

@core_bp.route('/api/get_grades')
@login_required
def api_get_grades():
    curriculum = request.args.get('curriculum')
    if not curriculum: return jsonify([])
    query = db.session.query(distinct(SkillCurriculum.grade)).filter_by(curriculum=curriculum)
    grades = sorted([row[0] for row in query.filter(SkillCurriculum.grade != None).all()])
    return jsonify(grades)

@core_bp.route('/api/get_volumes')
@login_required
def api_get_volumes():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    if not curriculum or not grade: return jsonify([])
    try:
        grade = int(grade)
    except:
        return jsonify([])
        
    query = db.session.query(distinct(SkillCurriculum.volume)).filter_by(curriculum=curriculum, grade=grade)
    volumes = [row[0] for row in query.all()]
    return jsonify(volumes)

@core_bp.route('/api/get_chapters')
@login_required
def api_get_chapters():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    if not all([curriculum, grade, volume]): return jsonify([])
    try:
        grade = int(grade)
    except:
        return jsonify([])

    query = db.session.query(distinct(SkillCurriculum.chapter)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume
    )
    chapters = [row[0] for row in query.all()]
    return jsonify(chapters)

@core_bp.route('/api/get_sections')
@login_required
def api_get_sections():
    curriculum = request.args.get('curriculum')
    grade = request.args.get('grade')
    volume = request.args.get('volume')
    chapter = request.args.get('chapter')
    if not all([curriculum, grade, volume, chapter]): return jsonify([])
    try:
        grade = int(grade)
    except:
        return jsonify([])

    query = db.session.query(distinct(SkillCurriculum.section)).filter_by(
        curriculum=curriculum, grade=grade, volume=volume, chapter=chapter
    )
    sections = [row[0] for row in query.all()]
    return jsonify(sections)

# API: ?潘撓貔?鞈????鞈???
@core_bp.route('/api/check_ghost_skills', methods=['GET'])
@login_required
def api_check_ghost_skills():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'error': 'Permission denied'}), 403
    try:
        skills_dir = os.path.join(current_app.root_path, 'skills')
        if not os.path.exists(skills_dir): return jsonify([])
        py_files = [f[:-3] for f in os.listdir(skills_dir) if f.endswith('.py') and f != '__init__.py']
        db_skills = [s.skill_id for s in SkillInfo.query.all()]
        ghost_skills = [f for f in py_files if f not in db_skills]
        return jsonify(ghost_skills)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# AI Prompt Settings (??? AI Prompt ??塗?桀??)
# ==========================================

@core_bp.route('/admin/ai_prompt_settings')
@login_required
def ai_prompt_settings_page():
    """Show AI settings page."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        flash('Permission denied', 'error')
        return redirect(url_for('dashboard'))
    snapshot = get_ai_settings_snapshot()
    return render_template(
        'ai_prompt_settings.html',
        username=current_user.username,
        cloud_model=snapshot.get("ai_cloud_model", Config.DEFAULT_CLOUD_MODEL),
        supported_cloud_models=list(Config.SUPPORTED_CLOUD_MODELS),
        google_model_options=get_google_model_options(),
    )


def _sanitize_role_overrides(raw_roles):
    if not isinstance(raw_roles, dict):
        return {}
    valid_presets = set(Config.CODER_PRESETS.keys())
    cleaned = {}
    for role in AI_ROLE_KEYS:
        value = raw_roles.get(role)
        if isinstance(value, str) and value in valid_presets:
            cleaned[role] = value
    return cleaned


def _to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text_value = str(value).strip().lower()
    if text_value in ('true', '1', 'yes', 'on'):
        return True
    if text_value in ('false', '0', 'no', 'off'):
        return False
    return default


def _normalize_cloud_model(model_name):
    return normalize_google_model_id(model_name, allow_fallback=True)


def _cloud_preset_key_from_model(cloud_model):
    cloud_model = _normalize_cloud_model(cloud_model)
    return cloud_model if cloud_model in Config.CODER_PRESETS else Config.DEFAULT_CLOUD_MODEL


def _generate_model_roles(ai_mode, available_models, cloud_model=None):
    roles = {}
    ROLE_LIST = ['vision_analyzer', 'coder', 'tutor', 'classifier', 'system_coder', 'default']
    selected_cloud_preset = _cloud_preset_key_from_model(cloud_model)
    
    def pick_gemini_model():
        keys = [m['key'] for m in available_models]
        if selected_cloud_preset in keys:
            return selected_cloud_preset
        if selected_cloud_preset in Config.CODER_PRESETS:
            return selected_cloud_preset
        if Config.DEFAULT_CLOUD_MODEL in keys:
            return Config.DEFAULT_CLOUD_MODEL
        if 'gemini-3.1-flash-lite-preview' in keys:
            return 'gemini-3.1-flash-lite-preview'
        for k in keys:
            if 'gemini' in k.lower():
                return k
        return selected_cloud_preset
        
    def pick_edge_model():
        if not available_models: return ''
        keys = [m['key'] for m in available_models]
        if 'qwen3-vl-8b' in keys: return 'qwen3-vl-8b'
        for k in keys:
            if 'qwen3-vl-8b' in k.lower(): return k
        for k in keys:
            lk = k.lower()
            if 'qwen' in lk and 'vl' in lk: return k
        for k in keys:
            if 'qwen3-8b' in k.lower(): return k
        for k in keys:
            if 'qwen' in k.lower(): return k
        return keys[0]
        
    def pick_qwen_text_model():
        if not available_models: return ''
        keys = [m['key'] for m in available_models]
        if 'qwen3-8b' in keys: return 'qwen3-8b'
        for k in keys:
            lk = k.lower()
            if 'qwen3-8b' in lk and 'vl' not in lk: return k
        for k in keys:
            if 'qwen3' in k.lower(): return k
        for k in keys:
            if 'qwen' in k.lower(): return k
        return keys[0]

    if ai_mode == 'cloud':
        g_model = pick_gemini_model()
        for r in ROLE_LIST:
            roles[r] = g_model
    elif ai_mode == 'edge':
        e_model = pick_edge_model()
        for r in ROLE_LIST:
            roles[r] = e_model
    else: # hybrid
        g_model = pick_gemini_model()
        q_model = pick_qwen_text_model()
        roles['vision_analyzer'] = g_model
        roles['coder'] = q_model
        roles['tutor'] = g_model
        roles['classifier'] = q_model
        roles['system_coder'] = q_model
        roles['default'] = q_model

    return roles


def _build_ai_settings_payload(prompt, updated_at):
    from models import SystemSetting
    ai_mode_setting = SystemSetting.query.filter_by(key='ai_mode').first()
    ai_mode = ai_mode_setting.value if ai_mode_setting else 'cloud'
    cloud_model_setting = SystemSetting.query.filter_by(key=SETTING_AI_CLOUD_MODEL).first()
    cloud_model = _normalize_cloud_model(cloud_model_setting.value if cloud_model_setting else Config.DEFAULT_CLOUD_MODEL)

    available_models = get_available_model_presets()
    model_roles = _generate_model_roles(ai_mode, available_models, cloud_model=cloud_model)
    gemini_key_row = SystemSetting.query.filter_by(key=SETTING_GEMINI_API_KEY).first()
    has_gemini_api_key = bool(gemini_key_row and str(gemini_key_row.value or "").strip())

    return {
        'success': True,
        'prompt': prompt,
        'updated_at': updated_at,
        'ai_mode': ai_mode,
        'cloud_model': cloud_model,
        'supported_cloud_models': list(Config.SUPPORTED_CLOUD_MODELS),
        'google_model_options': get_google_model_options(),
        'ai_model_roles': model_roles,
        'available_models': available_models,
        'has_gemini_api_key': has_gemini_api_key,
    }


def _parse_required_variables(raw_value):
    if not raw_value:
        return []
    val_str = str(raw_value).strip()
    if val_str == '[]':
        return []
    import json
    try:
        if val_str.startswith('[') and val_str.endswith(']'):
            parsed = json.loads(val_str)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item and str(item).strip()]
    except Exception:
        pass
    return [item.strip() for item in val_str.split(',') if item and item.strip()]


@core_bp.route('/admin/ai_prompt_settings/list')
@login_required
def list_prompt_templates():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        templates = (
            PromptTemplate.query.order_by(PromptTemplate.prompt_key.asc()).all()
        )
        rows = []
        from datetime import timezone, timedelta
        tw_tz = timezone(timedelta(hours=8))
        
        for item in templates:
            updated_str = None
            if item.updated_at:
                try:
                    utc_dt = item.updated_at.replace(tzinfo=timezone.utc)
                    tw_dt = utc_dt.astimezone(tw_tz)
                    updated_str = tw_dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    updated_str = item.updated_at.strftime('%Y-%m-%d %H:%M:%S')

            rows.append({
                'prompt_key': item.prompt_key,
                'title': item.title,
                'category': item.category,
                'description': item.description,
                'usage_context': item.usage_context,
                'used_in': item.used_in,
                'example_trigger': item.example_trigger,
                'content': item.content,
                'default_content': item.default_content,
                'required_variables': item.required_variables or '',
                'is_active': bool(item.is_active),
                'updated_at': updated_str,
            })
        return jsonify({'success': True, 'prompts': rows, 'items': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/prompt/update', methods=['POST'])
@login_required
def update_prompt_template_content():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        import logging
        logger = logging.getLogger(__name__)

        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()
            if not data:
                logger.error("[admin debug] /prompt/update 400: Payload is completely missing or unparseable")
                return jsonify({'success': False, 'message': 'Payload is missing or unparseable. Did you forget application/json?'}), 400

        prompt_key = str(data.get('prompt_key', '')).strip()
        content = str(data.get('content', '')).strip()
        
        logger.info(f"[admin debug] /prompt/update received: key='{prompt_key}', content length={len(content)}")

        if not prompt_key:
            logger.error("[admin debug] /prompt/update 400: prompt_key is missing")
            return jsonify({'success': False, 'message': 'prompt_key is required'}), 400
        if not content:
            logger.error("[admin debug] /prompt/update 400: content is empty")
            return jsonify({'success': False, 'message': 'content cannot be empty'}), 400

        template = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
        is_new = False
        if not template:
            logger.warning(f"[admin debug] /prompt/update: '{prompt_key}' not found in DB. Creating new entry.")
            template = PromptTemplate(prompt_key=prompt_key, is_active=True, title=prompt_key)
            db.session.add(template)
            is_new = True

        required_vars = []
        if template.required_variables:
            required_vars = _parse_required_variables(template.required_variables)
            
        if not required_vars:
            logger.info("[admin debug] /prompt/update skip required variable validation (empty list)")
        else:
            missing = [var_name for var_name in required_vars if f'{{{var_name}}}' not in content]
            if missing:
                err_msg = f"Missing required variables in prompt: {', '.join(missing)}"
                logger.error(f"[admin debug] /prompt/update 400: {err_msg}")
                return jsonify({'success': False, 'message': err_msg}), 400

        template.content = content
        template.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info(f"[admin debug] /prompt/update success: {'Created' if is_new else 'Updated'} key='{prompt_key}', category='{template.category}', commit success")
        return jsonify({'success': True, 'message': f'Prompt template {"created" if is_new else "updated"}'})
    except Exception as e:
        db.session.rollback()
        import traceback
        import logging
        logging.getLogger(__name__).error(f"[admin debug] /prompt/update 500: {e}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/prompt/reset', methods=['POST'])
@login_required
def reset_prompt_template_content():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        data = request.get_json(silent=True) or {}
        prompt_key = str(data.get('prompt_key', '')).strip()
        if not prompt_key:
            return jsonify({'success': False, 'message': 'prompt_key is required'}), 400

        template = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
        if not template:
            return jsonify({'success': False, 'message': f'Prompt not found: {prompt_key}'}), 404

        template.content = template.default_content
        template.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Prompt template reset',
            'content': template.content,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


def _validate_existing_prompt_key(prompt_key: str):
    if not prompt_key:
        return None, (jsonify({'success': False, 'message': 'prompt_key is required'}), 400)
    template = PromptTemplate.query.filter_by(prompt_key=prompt_key).first()
    if template:
        return template, None
    # ?蹓曇???ML ??¯蹎劉 ?垮謓舀蝞?????獢???駁??皝?
    try:
        diff = compare_prompt_db_vs_yaml(prompt_key)
        if diff.get("yaml_exists"):
            return None, None
    except Exception:
        pass
    return None, (jsonify({'success': False, 'message': f'?曆???prompt_key: {prompt_key}'}), 404)


@core_bp.route('/admin/ai_prompt_settings/publish_to_yaml', methods=['POST'])
@login_required
def publish_single_prompt_to_yaml():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        data = request.get_json(silent=True) or {}
        prompt_key = str(data.get('prompt_key', '')).strip()
        _, err = _validate_existing_prompt_key(prompt_key)
        if err:
            return err
        result = export_single_prompt_to_yaml(prompt_key)
        return jsonify(result)
    except (PromptSyncError, FileNotFoundError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/sync_from_yaml', methods=['POST'])
@login_required
def sync_single_prompt_from_yaml():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        data = request.get_json(silent=True) or {}
        prompt_key = str(data.get('prompt_key', '')).strip()
        _, err = _validate_existing_prompt_key(prompt_key)
        if err:
            return err
        result = import_single_prompt_from_yaml(prompt_key)
        return jsonify(result)
    except (PromptSyncError, FileNotFoundError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/version_check')
@login_required
def ai_prompt_version_check():
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        prompt_key = str(request.args.get('prompt_key', '')).strip()
        if not prompt_key:
            return jsonify({'success': False, 'message': 'prompt_key is required'}), 400
        result = compare_prompt_db_vs_yaml(prompt_key)
        return jsonify({'success': True, **result})
    except PromptSyncError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except FileNotFoundError:
        # YAML ?澗???殉朱謓?蹇???200???豯止鼓 yaml_exists=False
        return jsonify({
            'success': True,
            'prompt_key': prompt_key,
            'db_exists': bool(PromptTemplate.query.filter_by(prompt_key=prompt_key).first()),
            'yaml_exists': False,
            'db_updated_at': None,
            'yaml_updated_at': None,
            'has_yaml_update': False,
            'has_db_update': False,
            'is_different': bool(PromptTemplate.query.filter_by(prompt_key=prompt_key).first()),
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/get')
@login_required
def get_ai_prompt_setting():
    """API: Return prompt + AI control center settings."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        from core.prompts.registry import get_prompt_with_source
        apply_ai_runtime_settings()
        content, source = get_prompt_with_source("handwriting_feedback_prompt", "ai_analyzer_prompt")
        return jsonify(_build_ai_settings_payload(
            prompt=content, 
            updated_at=None
        ))
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/check_api_key', methods=['GET'])
@login_required
def check_gemini_api_key_status():
    """API: Return Gemini API key availability without exposing key content."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        api_key, source = resolve_gemini_api_key()
        has_api_key = bool(api_key)
        return jsonify({
            'has_api_key': has_api_key,
            'source': source,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/check_api_key', methods=['GET'])
@login_required
def admin_check_api_key():
    """API: Return API key status with masked key for safe verification."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        api_key, source = resolve_gemini_api_key()
        return jsonify({
            "has_api_key": bool(api_key),
            "masked_key": mask_api_key(api_key),
            "source": source,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/check_api_key_masked', methods=['GET'])
@login_required
def check_gemini_api_key_masked_status():
    """API: Return masked Gemini API key for safe verification."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        api_key, source = resolve_gemini_api_key()
        has_api_key = bool(api_key)
        masked_key = mask_api_key(api_key)

        return jsonify({
            'has_api_key': has_api_key,
            'source': source,
            'masked_key': masked_key,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/update', methods=['POST'])
@login_required
def update_ai_prompt_setting():
    """API: Update prompt + AI control center settings."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        from models import SystemSetting
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}
        form_data = request.form if request.form else {}

        if 'prompt' in data:
            new_prompt = str(data.get('prompt', '')).strip()
            if not new_prompt:
                return jsonify({'success': False, 'message': 'Prompt cannot be empty'}), 400
            if '{context}' not in new_prompt or '{prereq_text}' not in new_prompt:
                return jsonify({'success': False, 'message': 'Prompt must include {context} and {prereq_text}'}), 400
            set_system_setting_value('ai_analyzer_prompt', new_prompt, 'AI analyzer prompt')

        raw_api_key = data.get('api_key')
        if raw_api_key is None:
            raw_api_key = data.get('gemini_api_key')
        if raw_api_key is None:
            raw_api_key = form_data.get('api_key')
        if raw_api_key is None:
            raw_api_key = form_data.get('gemini_api_key')
        if raw_api_key is None:
            raw_api_key = session.get("GEMINI_API_KEY")
        if raw_api_key is not None:
            api_key_value = str(raw_api_key).strip()
            if api_key_value:
                set_system_setting_value(
                    SETTING_GEMINI_API_KEY,
                    api_key_value,
                    'Gemini API key for cloud runtime'
                )
                current_app.logger.info("[AI KEY] source=db")

        cloud_model_input = data.get('cloud_model')
        if cloud_model_input is None:
            cloud_model_input = form_data.get('cloud_model')
        if ('cloud_model' in data) or ('cloud_model' in form_data):
            try:
                cloud_model = normalize_google_model_id(cloud_model_input)
            except ValueError:
                return jsonify({'success': False, 'message': 'Unknown or unsupported Gemini model id'}), 400
            set_system_setting_value(SETTING_AI_CLOUD_MODEL, cloud_model, 'Cloud Gemini model for cloud/hybrid runtime')
        else:
            cloud_model = _normalize_cloud_model(cloud_model_input or Config.DEFAULT_CLOUD_MODEL)

        ai_mode_raw = data.get('ai_mode')
        if ai_mode_raw is None:
            ai_mode_raw = form_data.get('ai_mode')
        ai_mode = str(ai_mode_raw or '').strip()
        if ai_mode:
            if ai_mode not in ('cloud', 'edge', 'hybrid'):
                return jsonify({'success': False, 'message': 'Invalid ai_mode'}), 400
            set_system_setting_value('ai_mode', ai_mode, 'Global AI Mode')

            # Backwards compatibility / map updates
            if ai_mode == 'cloud':
                set_system_setting_value(SETTING_AI_GLOBAL_STRATEGY, 'cloud_first', 'Global AI strategy')
            elif ai_mode == 'edge':
                set_system_setting_value(SETTING_AI_GLOBAL_STRATEGY, 'local_first', 'Global AI strategy')
            elif ai_mode == 'hybrid':
                set_system_setting_value(SETTING_AI_GLOBAL_STRATEGY, 'hybrid_balanced', 'Global AI strategy')

            model_roles = _generate_model_roles(ai_mode, get_available_model_presets(), cloud_model=cloud_model)
            cleaned_roles = _sanitize_role_overrides(model_roles)
            set_system_setting_value(SETTING_AI_MODEL_ROLES, cleaned_roles, 'AI role model map (JSON)')

        db.session.commit()
        apply_ai_runtime_settings()
        return jsonify({'success': True, 'message': 'AI settings updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@core_bp.route('/admin/ai_prompt_settings/reset', methods=['POST'])
@login_required
def reset_ai_prompt_setting():
    """API: Reset prompt only or all AI settings."""
    if not (current_user.is_admin or current_user.role == 'teacher'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    try:
        from models import SystemSetting
        from core.ai_analyzer import DEFAULT_PROMPT

        data = request.get_json(silent=True) or {}
        reset_scope = str(data.get('scope', 'prompt_only')).strip().lower()
        if reset_scope not in ('prompt_only', 'all'):
            return jsonify({'success': False, 'message': 'Invalid reset scope'}), 400

        setting = SystemSetting.query.filter_by(key='ai_analyzer_prompt').first()
        if setting:
            setting.value = DEFAULT_PROMPT
            setting.updated_at = datetime.utcnow()
        else:
            db.session.add(SystemSetting(
                key='ai_analyzer_prompt',
                value=DEFAULT_PROMPT,
                description='AI analyzer prompt',
            ))

        if reset_scope == 'all':
            set_system_setting_value('ai_mode', 'cloud', 'Global AI Mode')
            set_system_setting_value(SETTING_AI_GLOBAL_STRATEGY, 'cloud_first', 'Global AI strategy')
            set_system_setting_value(SETTING_AI_CLOUD_MODEL, Config.DEFAULT_CLOUD_MODEL, 'Cloud Gemini model for cloud/hybrid runtime')
            model_roles = _generate_model_roles('cloud', get_available_model_presets(), cloud_model=Config.DEFAULT_CLOUD_MODEL)
            set_system_setting_value(SETTING_AI_MODEL_ROLES, _sanitize_role_overrides(model_roles), 'AI role model map')

        db.session.commit()
        apply_ai_runtime_settings()
        if reset_scope == 'all':
            return jsonify({'success': True, 'message': 'Prompt and AI settings reset'})
        return jsonify({'success': True, 'message': 'Prompt reset'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

