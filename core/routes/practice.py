# -*- coding: utf-8 -*-
"""
=============================================================================
璅∠??迂 (Module Name): core/routes/practice.py
?隤芣? (Description): 摮貊?蝺渡???詨?頝舐璅∠?嚗????桃???(Generator)??獢??(Checker) ??Matplotlib 蝜芸?頛嚗蒂蝞∠?蝺渡? Session??
?瑁?隤? (Usage): ?梁頂蝯梯矽??
?鞈? (Version): V2.0
?湔?交? (Date): 2026-01-13
蝬剛風?? (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import Blueprint, request, jsonify, current_app, render_template, session, url_for, redirect
from urllib.parse import unquote as _url_unquote
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import importlib
import sys # [靽格迤 2] 撠 sys 隞乩噶瑼Ｘ璅∠????
import numpy as np
import matplotlib
# [CRITICAL] 閮剖? Matplotlib ?粹?鈭?璅∪?嚗??Server 蝡?GUI ?航炊
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import re
import uuid
import os
import random
import hashlib
from datetime import datetime
from typing import Any

# 撘 Blueprint
from . import practice_bp

# 鞈?摨急芋??
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum, Progress, MistakeNotebookEntry
from core.utils import get_skill_info
from core.session import get_current, set_current
from core.practice_question_store import (
    clear_practice_display_state_for_skill_switch,
    clear_practice_state,
    estimate_session_cookie_bytes,
    mark_question_answered,
    prune_practice_session,
    resolve_check_context,
    preview_question_text,
)
from core.adaptive_engine import recommend_question, update_student_ability, apply_error_penalty, get_all_prerequisites
from core.ai_analyzer import diagnose_error
from core.irt_engine import update_node_competencies
from core.ai_settings import get_effective_model_config
from config import Config

from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    allowlisted_b4_candidates,
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    filter_skill_pool_for_b4_chapter1_deterministic_adaptive,
    format_adaptive_question_audit_dict,
    get_b4_chapter1_curriculum_progression,
    is_pure_b4_allowlisted_adaptive_pool,
    starter_b4_candidates,
    validate_b4_deterministic_adaptive_generator_payload,
)

# Phase 6C-1R: Chap2 deterministic probability integration
from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
    is_b4_chapter2_phase6c1_deterministic_skill,
    is_b4_chapter2_skill_not_enabled_in_phase6c1,
    is_b4_chapter2_excluded_problem_type,
    validate_b4_chap2_phase6c1_generator_payload,
)
# Phase 7B: Chap3 deterministic integration
from core.vocational_math_b4.adaptive.b4_chapter3_phase7b_allowlist import (
    is_b4_chapter3_phase7b_deterministic_skill,
    is_b4_chapter3_phase7b_runtime_skill,
    is_b4_chapter3_skill_not_enabled,
    validate_b4_chap3_phase7b_generator_payload,
)
from core.vocational_math_b4.services.question_router import generate_for_chap2_skill, generate_for_chap3_skill
from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
    persist_b4_chap2_deterministic_answer_event,
    persist_b4_chap2_gated_event,
)
# Phase 6N: Chap2 chapter mode integration
from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
    B4_CHAP2_CHAPTER_SKILL_IDS,
    B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
)
from core.vocational_math_b4.domain.b4_validators import (
    check_rational_answer,
    check_integer_answer,
    check_expected_value_answer,
)

# Phase 6G-0: Chap2 skill / problem-type gates ??user-facing messages (SOP 禮8.1).
# JSON `error` must not expose internal phase codes, legacy import traces, or URL-encoded skill_id.
B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR = (
    "This Chap2 skill is not enabled in the current deterministic runtime."
)
B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR = (
    "This problem type is reserved for handwriting/free-response review."
)

# Phase 7B: Chap3 skill gate
B4_CHAP3_SKILL_NOT_ENABLED_PUBLIC_ERROR = (
    "This Chap3 skill is not enabled in the current deterministic runtime."
)
B4_CHAP3_REQUIRES_EXPLICIT_PROBLEM_TYPE_SKILLS = set()


@practice_bp.after_request
def _auto_prune_practice_session(response):
    """Keep client-side practice cookies small on practice runtime endpoints."""
    try:
        if request.path in {"/practice", "/get_next_question", "/check_answer"} or request.path.startswith("/practice/"):
            prune_practice_session()
    except Exception:
        try:
            current_app.logger.exception("[PRACTICE session prune] after_request_failed")
        except Exception:
            pass
    return response


def _b4_chap2_public_payload_validation_message(deny_reason: str | None) -> str:
    """Map internal Chap2 allowlist validator codes to student-safe error text."""
    dr = str(deny_reason or "").strip()
    if dr.startswith("excluded_handwriting_problem_type:"):
        return B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR
    if dr.startswith("not_in_phase6c1_allowlist:"):
        return (
            "This problem type is not enabled in the current deterministic runtime."
        )
    if dr.startswith("skill_not_in_phase6c1_allowlist:"):
        return (
            "This skill/problem combination is not enabled in the current deterministic runtime."
        )
    if dr == "missing_or_invalid_problem_type_id":
        return "Question type metadata is incomplete."
    if dr == "payload_not_dict":
        return "Invalid question payload."
    return (
        "This question does not match the current deterministic runtime scope."
    )

def _b4_chap3_public_payload_validation_message(deny_reason: str | None) -> str:
    """Map internal Chap3 allowlist validator codes to student-safe error text."""
    dr = str(deny_reason or "").strip()
    if dr == "missing_or_invalid_problem_type_id":
        return "Question type metadata is incomplete."
    if dr == "payload_not_dict":
        return "Invalid question payload."
    return (
        "This question does not match the current deterministic runtime scope."
    )


MANUAL_REVIEW_SKILLS = {
    "vh_?詨飛B4_PascalTriangle": {
        "display_name": "撌湔?∩?閫耦",
        "reason": "Pascal triangle items require handwriting/free-response review and are excluded from deterministic int-answer runtime.",
        "future_path": "future_ai_judged / teacher review / structured derivation",
    },
}

B4_TREE_DIAGRAM_FREE_RESPONSE_SKILL_ID = "vh_?詨飛B4_TreeDiagramCounting"
B4_TREE_DIAGRAM_PROBLEM_TYPE = "tree_diagram_listing"
B4_TREE_DIAGRAM_DEFAULT_VARIANT = "early_stopping_game"
B4_TREE_DIAGRAM_VARIANTS = ("early_stopping_game", "fixed_stage_binary_tree")
B4_PASCAL_TRIANGLE_FREE_RESPONSE_SKILL_ID = "vh_?詨飛B4_PascalTriangle"
B4_PASCAL_TRIANGLE_PROBLEM_TYPE = "pascal_triangle_handwriting"
B4_PASCAL_TRIANGLE_VARIANTS = ("pascal_row_listing", "pascal_binomial_expansion")

# ==========================================
# Helper Functions (頛?賢?)
# ==========================================

def get_skill(skill_id, *, reload_module: bool = False):
    """??頛??賣芋蝯?(skills/xxx.py)"""
    if skill_id in {"vh_?詨飛B4_TreeDiagramCounting", "vh_?詨飛B4_PascalTriangle"}:
        return None
    try:
        module_path = f"skills.{skill_id}"
        if reload_module and module_path in sys.modules:
            return importlib.reload(sys.modules[module_path])
        return importlib.import_module(module_path)
    except Exception:
        return None

def _has_runtime_skill_module(skill_id):
    """Return True when a runtime skill module can be imported from skills/<skill_id>.py."""
    return get_skill(skill_id) is not None


def _normalize_gencode_runtime_payload(data: dict, *, skill_id: str = "") -> dict:
    """Ensure coordinate_pair answers stay string pairs for practice grading feedback."""
    if not isinstance(data, dict):
        return data
    from core.gencode.answer_payload import refresh_runtime_question_session

    return refresh_runtime_question_session(data, skill_id=skill_id)


def _extract_canonical_question_stem(data: dict[str, Any]) -> str:
    """Return the canonical question stem for API / frontend display."""
    if not isinstance(data, dict):
        return ""
    for key in ("question_text", "new_question_text", "question", "prompt"):
        val = str(data.get(key) or "").strip()
        if val:
            return val
    return ""


def _canonicalize_answer_contract_for_api(data: dict[str, Any]) -> dict[str, Any]:
    """Align top-level answer_contract with runtime checker; demote stale nested shapes."""
    ac = dict(data.get("answer_contract") or {}) if isinstance(data.get("answer_contract"), dict) else {}
    top_shape = str(
        ac.get("answer_shape")
        or data.get("answer_shape")
        or ac.get("answer_type")
        or data.get("answer_type")
        or ""
    ).strip()
    top_checker = str(
        ac.get("checker_key")
        or ac.get("checker")
        or data.get("checker")
        or data.get("checker_type")
        or ""
    ).strip()
    if top_shape:
        ac["answer_shape"] = top_shape
        ac.setdefault("answer_type", top_shape)
    if top_checker:
        ac["checker"] = top_checker
        ac["checker_key"] = top_checker
    is_drawing_contract = (
        top_checker == "free_response_drawing_checker"
        or str(ac.get("answer_type") or "").strip() == "drawing"
        or str(ac.get("answer_shape") or "").strip() == "drawing"
    )
    if is_drawing_contract and not isinstance(ac.get("ui_contract"), dict):
        ac["ui_contract"] = {
            "response_mode": "drawing",
            "text_input_enabled": False,
            "normal_submit_enabled": False,
            "ai_check_required": True,
            "canvas_required": True,
            "allow_image_upload": True,
            "allow_text_answer": False,
        }

    gc = ac.get("generator_contract")
    if isinstance(gc, dict):
        gc_copy = dict(gc)
        nested_shape = gc_copy.get("answer_shape")
        if nested_shape and top_shape and str(nested_shape).strip() != top_shape:
            gc_copy["raw_generator_answer_shape"] = nested_shape
            gc_copy["answer_shape"] = top_shape
        ac["generator_contract"] = gc_copy

    return ac


def _finalize_practice_question_api_fields(data: dict[str, Any], *, skill_id: str = "") -> dict[str, Any]:
    """Ensure question_text/new_question_text parity and canonical answer_contract for API consumers."""
    out = dict(data)
    if skill_id:
        out["skill_id"] = skill_id
    stem = _extract_canonical_question_stem(out)
    out["question_text"] = stem
    out["new_question_text"] = stem
    out["answer_contract"] = _canonicalize_answer_contract_for_api(out)
    from core.gencode.choice_math_display import normalize_choice_displays

    if isinstance(out.get("choices"), list) and out["choices"]:
        out["choices"] = normalize_choice_displays(out["choices"])
        out["choices_display"] = list(out["choices"])
    return out


def _v3_runtime_contract_api_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Expose V3 generator contract fields on practice API responses."""
    meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    return {
        "presentation_mode": data.get("presentation_mode") or meta.get("presentation_mode"),
        "answer_type": data.get("answer_type") or meta.get("answer_type"),
        "problem_type_id": data.get("problem_type_id") or meta.get("problem_type_id"),
        "answer_contract": data.get("answer_contract", {}),
        "metadata": meta,
        "choices": data.get("choices", []),
        "choices_display": data.get("choices_display", data.get("choices", [])),
        "subquestions": data.get("subquestions", []),
        "table_data": data.get("table_data", {}),
        "table_question": data.get("table_question", {}),
        "semantic_answer": data.get("semantic_answer") or meta.get("semantic_answer"),
        "display_answer": data.get("display_answer"),
        "component_id": data.get("component_id") or meta.get("component_id"),
        "textbook_example_id": data.get("textbook_example_id") or meta.get("textbook_example_id"),
        "generator_key": data.get("generator_key") or data.get("component_id"),
        "source_kind": data.get("source_kind") or meta.get("source_kind"),
        "ui_contract": data.get("ui_contract") or (data.get("answer_contract") or {}).get("ui_contract", {}),
    }


def _log_get_next_question_response(payload: dict[str, Any]) -> None:
    stem = str(payload.get("question_text") or "")
    current_app.logger.info(
        "[PRACTICE get_next_question] question_text_preview=%s",
        preview_question_text(stem),
    )
    current_app.logger.info(
        "[PRACTICE get_next_question] response_fields includes question_text=%s new_question_text=%s",
        bool(payload.get("question_text")),
        bool(payload.get("new_question_text")),
    )


def _runtime_reload_skill_modules() -> bool:
    try:
        return bool(current_app.debug)
    except Exception:
        return False


def _prepare_skill_switch(skill_id: str) -> dict[str, Any]:
    """On cross-skill navigation, clear stale question display session keys."""
    info = clear_practice_display_state_for_skill_switch(skill_id)
    if info.get("did_clear"):
        current_app.logger.info(
            "[PRACTICE skill_switch] requested=%s previous_skill=%s previous_uid=%s cleared=%s",
            info.get("requested_skill_id"),
            info.get("previous_skill_id"),
            info.get("previous_question_uid"),
            info.get("cleared_keys"),
        )
    prune_practice_session()
    return info


def _log_practice_page_entry(skill_id: str, switch_info: dict[str, Any]) -> None:
    current_app.logger.info(
        "[PRACTICE page] frontend_requested_skill_id=%s session_skill_before=%s session_uid_before=%s",
        skill_id,
        switch_info.get("previous_skill_id"),
        switch_info.get("previous_question_uid"),
    )
    current_app.logger.info(
        "[PRACTICE page] session_skill_after=%s session_uid_after=%s cleared=%s",
        switch_info.get("current_skill_id_after"),
        switch_info.get("current_question_uid_after"),
        switch_info.get("cleared_keys"),
    )


def _emit_check_result(
    question_uid: str,
    skill_id: str,
    result: dict[str, Any],
    *,
    record_progress: bool = True,
) -> Any:
    uid = str(question_uid or session.get("current_question_uid", "")).strip()
    # Only mark the question as answered in the store when the result carries a
    # definitive verdict (correct / incorrect). parse_error and system_error are
    # not genuine student answers and must not pollute the question store.
    _status = str(result.get("status", "")).strip() if isinstance(result, dict) else ""
    _is_gradable = _status in ("correct", "incorrect") or (
        _status == "" and not result.get("system_error") and not result.get("invalid_input")
    )
    if uid and _is_gradable:
        mark_question_answered(uid, result)
    out = dict(result)
    if uid:
        out["question_uid"] = uid
    if record_progress and _is_gradable:
        try:
            update_progress(current_user.id, skill_id, bool(out.get("correct", False)))
        except Exception:
            pass
    return jsonify(out)


def _record_compact_practice_progress(skill_id: str, is_correct: bool) -> None:
    """Keep adaptive review hints small enough for Flask's cookie session."""
    import time

    sid = str(skill_id or "").strip()
    if not sid:
        return
    history = session.get("review_history")
    if not isinstance(history, list):
        history = []
    history.append({"skill_id": sid[:80], "correct": bool(is_correct), "timestamp": int(time.time())})
    session["review_history"] = history[-3:]

    stats = session.get("skill_stats")
    if not isinstance(stats, dict):
        stats = {}
    st = stats.get(sid)
    if not isinstance(st, dict):
        st = {"attempts": 0, "correct": 0, "wrong": 0, "fail_streak": 0}
    st = {
        "attempts": int(st.get("attempts", st.get("a", 0)) or 0) + 1,
        "correct": int(st.get("correct", st.get("c", 0)) or 0),
        "wrong": int(st.get("wrong", st.get("w", 0)) or 0),
        "fail_streak": int(st.get("fail_streak", st.get("f", 0)) or 0),
    }
    if is_correct:
        st["correct"] += 1
        st["fail_streak"] = 0
    else:
        st["wrong"] += 1
        st["fail_streak"] += 1
    stats[sid] = st
    if len(stats) > 8:
        keep = set(x.get("skill_id") for x in session["review_history"] if isinstance(x, dict))
        for key in list(stats.keys()):
            if len(stats) <= 8:
                break
            if key not in keep:
                stats.pop(key, None)
    session["skill_stats"] = stats
    for key in ("current_data", "current_question", "correct_answer"):
        session.pop(key, None)
    session.modified = True


def _log_runtime_generate_payload(skill_id: str, payload: dict[str, Any], *, module_file: str = "") -> None:
    from flask import session as flask_session

    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    cookie_ref = flask_session.get("practice_ref") if isinstance(flask_session.get("practice_ref"), dict) else {}
    current_app.logger.info("[PRACTICE RUNTIME generate] response.skill_id=%s", skill_id)
    current_app.logger.info("[PRACTICE RUNTIME generate] response.question_uid=%s", payload.get("question_uid"))
    current_app.logger.info("[PRACTICE RUNTIME generate] stored.skill_id=%s", cookie_ref.get("skill_id"))
    current_app.logger.info("[PRACTICE RUNTIME generate] stored.question_uid=%s", cookie_ref.get("question_uid"))
    current_app.logger.info(
        "[PRACTICE RUNTIME generate] cookie_session_size_estimate=%s",
        estimate_session_cookie_bytes(),
    )
    current_app.logger.info("[PRACTICE RUNTIME generate] skill_id=%s", skill_id)
    current_app.logger.info("[PRACTICE RUNTIME generate] module_file=%s", module_file or "")
    current_app.logger.info("[PRACTICE RUNTIME generate] problem_type_id=%s", payload.get("problem_type_id"))
    current_app.logger.info("[PRACTICE RUNTIME generate] question_text=%s", payload.get("question_text"))
    current_app.logger.info("[PRACTICE RUNTIME generate] answer=%r type=%s", payload.get("answer"), type(payload.get("answer")).__name__)
    current_app.logger.info(
        "[PRACTICE RUNTIME generate] correct_answer=%r type=%s",
        payload.get("correct_answer"),
        type(payload.get("correct_answer")).__name__,
    )
    current_app.logger.info("[PRACTICE RUNTIME generate] display_answer=%s", payload.get("display_answer"))
    current_app.logger.info("[PRACTICE RUNTIME generate] answer_contract=%s", ac)
    current_app.logger.info("[PRACTICE RUNTIME generate] checker=%s equivalence=%s", payload.get("checker"), payload.get("equivalence"))
    current_app.logger.info(
        "[PRACTICE RUNTIME generate] metadata.presentation_mode=%s metadata.semantic_answer=%s",
        meta.get("presentation_mode"),
        meta.get("semantic_answer"),
    )


def _log_runtime_check_session(
    skill_id: str,
    user_answer: Any,
    current: dict[str, Any],
    *,
    selected_checker: str = "",
    checker_result: bool | None = None,
    feedback_display: str = "",
) -> None:
    meta = current.get("metadata") if isinstance(current.get("metadata"), dict) else {}
    ac = current.get("answer_contract") if isinstance(current.get("answer_contract"), dict) else {}
    current_app.logger.info("[PRACTICE RUNTIME check] skill_id=%s", skill_id)
    current_app.logger.info("[PRACTICE RUNTIME check] user_answer=%r", user_answer)
    current_app.logger.info("[PRACTICE RUNTIME check] question_text=%s", current.get("question_text"))
    current_app.logger.info("[PRACTICE RUNTIME check] answer=%r type=%s", current.get("answer"), type(current.get("answer")).__name__)
    current_app.logger.info(
        "[PRACTICE RUNTIME check] correct_answer=%r type=%s",
        current.get("correct_answer"),
        type(current.get("correct_answer")).__name__,
    )
    current_app.logger.info("[PRACTICE RUNTIME check] display_answer=%s", current.get("display_answer"))
    current_app.logger.info("[PRACTICE RUNTIME check] answer_contract=%s", ac)
    current_app.logger.info("[PRACTICE RUNTIME check] checker=%s equivalence=%s", current.get("checker"), current.get("equivalence"))
    current_app.logger.info(
        "[PRACTICE RUNTIME check] metadata.presentation_mode=%s metadata.semantic_answer=%s",
        meta.get("presentation_mode"),
        meta.get("semantic_answer"),
    )
    current_app.logger.info(
        "[PRACTICE RUNTIME check] selected_checker=%s checker_result=%s feedback_display_answer=%s",
        selected_checker,
        checker_result,
        feedback_display,
    )


def _resolve_adaptive_unit_name(skill_id, requested_unit_name=""):
    requested = str(requested_unit_name or "").strip()
    if requested and requested != "?砍??拇?摮貊?嚗蜇蝯扯那?瘀?":
        return requested
    skill_map = {
        "jh_?詨飛1銝FourArithmeticOperationsOfIntegers": "?湔????",
        "jh_?詨飛1銝FourArithmeticOperationsOfNumbers": "?????",
        "jh_?詨飛2銝FourOperationsOfRadicals": "?孵?????",
        "jh_?詨飛1銝OperationsOnLinearExpressions": "銝??甈∪?",
        "jh_?詨飛2銝FourArithmeticOperationsOfPolynomial": "憭?撘???蝞?",
    }
    return skill_map.get(str(skill_id or "").strip(), requested or "?芣?摰??")


def _resolve_b4_chapter_adaptive_entry(
    *,
    mode: str,
    curriculum: str,
    volume: str,
    chapter_id: str,
    skill_ids: str,
) -> tuple[dict[str, object], bool]:
    """
    Phase 5B-Fix-A bridge (extended in Phase 6N for Chap2):
    Resolve B4 Chapter 1/2 chapter-mode entry to deterministic adaptive pool.
    """
    normalized_mode = str(mode or "").strip().lower()
    normalized_curriculum = str(curriculum or "").strip().lower()
    normalized_volume = str(volume or "").strip()
    normalized_chapter_id = str(chapter_id or "").strip()
    normalized_skill_ids = str(skill_ids or "").strip()

    # --- B4 Chapter 1 (??蝯?) ---
    legacy_hit = normalized_mode == "single" and normalized_skill_ids == "1 ??蝯?"
    chapter1_hit = (
        normalized_mode == "chapter"
        and normalized_curriculum == "vocational"
        and normalized_volume == "?詨飛B4"
        and normalized_chapter_id == "1"
    )
    if legacy_hit or chapter1_hit:
        unit_skill_ids = get_b4_chapter1_curriculum_progression(include_free_response=False)
        starter_pool = starter_b4_candidates(unit_skill_ids) or unit_skill_ids
        starter_skill_id = starter_pool[0] if starter_pool else ""
        return (
            {
                "entry_mode": "chapter",
                "compat_path_used": legacy_hit,
                "unit_name": "?桀?蝺渡?嚗? ??蝯?",
                "unit_skill_ids": unit_skill_ids,
                "bootstrap_unit_skill_ids": starter_pool,
                "starter_skill_id": starter_skill_id,
                "chapter_id": "1",
                "volume": "?詨飛B4",
                "curriculum": "vocational",
            },
            True,
        )

    # --- B4 Chapter 2 (璈?) ??Phase 6N ---
    chapter2_hit = (
        normalized_mode == "chapter"
        and normalized_curriculum == "vocational"
        and normalized_volume == "?詨飛B4"
        and normalized_chapter_id == "2"
    )
    if chapter2_hit:
        unit_skill_ids = list(B4_CHAP2_CHAPTER_SKILL_IDS)
        starter_skill_id = unit_skill_ids[0] if unit_skill_ids else ""
        return (
            {
                "entry_mode": "chapter",
                "compat_path_used": False,
                "unit_name": "?桀?蝺渡?嚗? 璈?",
                "unit_skill_ids": unit_skill_ids,
                "bootstrap_unit_skill_ids": unit_skill_ids,
                "starter_skill_id": starter_skill_id,
                "chapter_id": "2",
                "volume": "?詨飛B4",
                "curriculum": "vocational",
                "b4_chap2_chapter_mode": True,
                "diagnostic_total_steps": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
            },
            True,
        )

    return {}, False


def _stable_b4_inner_seed(skill_id: str, gen_seed: int) -> int:
    """Derive a deterministic inner seed for B4 router selection."""
    raw = f"b4-router::{skill_id}::{int(gen_seed)}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    # Keep seed bounded to avoid pathological long sampling loops in some generators.
    return (int(digest[:8], 16) % 1_000_000) + 1


def _is_b4_tree_diagram_request(skill_id: str | None = None, problem_type: str | None = None) -> bool:
    return (
        str(skill_id or "").strip() == B4_TREE_DIAGRAM_FREE_RESPONSE_SKILL_ID
        or str(problem_type or "").strip() == B4_TREE_DIAGRAM_PROBLEM_TYPE
    )


def _is_b4_pascal_triangle_request(skill_id: str | None = None, problem_type: str | None = None) -> bool:
    return (
        str(skill_id or "").strip() == B4_PASCAL_TRIANGLE_FREE_RESPONSE_SKILL_ID
        or str(problem_type or "").strip() == B4_PASCAL_TRIANGLE_PROBLEM_TYPE
    )


def _resolve_b4_tree_diagram_variant(variant: str | None = None, tree_diagram_index: int | None = None) -> str:
    if tree_diagram_index is not None:
        return B4_TREE_DIAGRAM_VARIANTS[tree_diagram_index % len(B4_TREE_DIAGRAM_VARIANTS)]
    selected_variant = (variant or B4_TREE_DIAGRAM_DEFAULT_VARIANT).strip() or B4_TREE_DIAGRAM_DEFAULT_VARIANT
    return selected_variant


def _resolve_b4_pascal_triangle_variant(pascal_triangle_index: int | None = None) -> str:
    idx = int(pascal_triangle_index or 0)
    return B4_PASCAL_TRIANGLE_VARIANTS[idx % len(B4_PASCAL_TRIANGLE_VARIANTS)]


def _build_b4_tree_diagram_runtime_payload(
    variant: str | None = None,
    tree_diagram_index: int | None = None,
) -> dict:
    from core.vocational_math_b4.free_response.tree_diagram_judge import build_tree_diagram_listing_payload

    selected_variant = _resolve_b4_tree_diagram_variant(variant, tree_diagram_index)
    payload_index = tree_diagram_index // len(B4_TREE_DIAGRAM_VARIANTS) if tree_diagram_index is not None else None
    if payload_index is None:
        previous_current = get_current() or {}
        previous_question_text = str(previous_current.get("question_text") or "")
        previous_scenario_id = str(previous_current.get("scenario_id") or "")
        previous_family = str(previous_current.get("scenario_family") or "")
        previous_param_sig = str(previous_current.get("parameter_signature") or "")
        previous_outcome_sig = str(previous_current.get("outcome_set_signature") or "")
        retry_count = 0
        retry_limit = 3
        payload = build_tree_diagram_listing_payload(
            selected_variant,
            index=random.randint(0, 199),
        )
        while retry_count < retry_limit:
            duplicate_hit = (
                (str(payload.get("question_text") or "") and str(payload.get("question_text") or "") == previous_question_text)
                or (str(payload.get("scenario_id") or "") and str(payload.get("scenario_id") or "") == previous_scenario_id)
                or (str(payload.get("scenario_family") or "") and str(payload.get("scenario_family") or "") == previous_family)
                or (str(payload.get("parameter_signature") or "") and str(payload.get("parameter_signature") or "") == previous_param_sig)
                or (str(payload.get("outcome_set_signature") or "") and str(payload.get("outcome_set_signature") or "") == previous_outcome_sig)
            )
            if not duplicate_hit:
                break
            retry_count += 1
            payload = build_tree_diagram_listing_payload(
                selected_variant,
                index=random.randint(0, 199),
            )
    else:
        payload = build_tree_diagram_listing_payload(selected_variant, index=payload_index)
    return {
        "question_text": payload["question_text"],
        "correct_answer": "",
        "answer_type": "handwriting",
        "answer_input_type": "handwriting",
        "answer": "",
        "problem_type": payload["problem_type_id"],
        "problem_type_id": payload["problem_type_id"],
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "handwriting_ai_checked",
        "grading_mode": "ai_judged_free_response",
        "variant": payload["variant"],
        "expected_count": payload["expected_count"],
        "expected_paths": payload["expected_paths"],
        "path_labels": payload.get("path_labels", []),
        "requires_listing_or_tree": payload.get("requires_listing_or_tree", True),
        "requires_handwriting": True,
        "scenario_family": payload.get("scenario_family", "tree_diagram_counting"),
        "scenario_id": payload.get("scenario_id", ""),
        "parameter_signature": payload.get("parameter_signature", ""),
        "outcome_set_signature": payload.get("outcome_set_signature", ""),
        "tree_depth": payload.get("tree_depth"),
        "branch_counts": payload.get("branch_counts", []),
        "context_signature": payload.get("context_signature", ""),
        "expected_answer_schema": payload.get("expected_answer_schema", {}),
        "rubric": payload.get("rubric", []),
        "textbook_alignment_note": payload.get("textbook_alignment_note", ""),
        "visual_backed": True,
        "visual_asset_type": "tree_diagram_template",
        "context_string": "",
    }


def _build_b4_pascal_triangle_runtime_payload(
    pascal_triangle_index: int | None = None,
) -> dict:
    from core.vocational_math_b4.free_response.pascal_triangle_judge import build_pascal_triangle_payload

    idx = int(pascal_triangle_index or 0)
    selected_variant = _resolve_b4_pascal_triangle_variant(idx)
    payload_index = idx // len(B4_PASCAL_TRIANGLE_VARIANTS)
    payload = build_pascal_triangle_payload(selected_variant, index=payload_index)
    return {
        "question_text": payload["question_text"],
        "correct_answer": "",
        "answer_type": "handwriting",
        "answer_input_type": "handwriting",
        "answer": "",
        "problem_type": payload["problem_type_id"],
        "problem_type_id": payload["problem_type_id"],
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "handwriting_ai_checked",
        "grading_mode": "ai_assisted_review",
        "variant": payload["variant"],
        "n": payload.get("n"),
        "expected_row": payload.get("expected_row", []),
        "expected_terms": payload.get("expected_terms", []),
        "expected_expansion": payload.get("expected_expansion", ""),
        "requires_handwriting": True,
        "requires_teacher_review": True,
        "visual_backed": True,
        "visual_asset_type": "pascal_triangle_template",
        "context_string": "",
    }

def _is_choice_question(current_question: dict) -> bool:
    answer_input_type = str(current_question.get("answer_input_type", "")).strip().lower()
    answer_type = str(current_question.get("answer_type", "")).strip().lower()
    checker_type = str(current_question.get("checker_type", "")).strip().lower()
    question_type = str(current_question.get("question_type", "")).strip().lower()
    choices = current_question.get("choices") or current_question.get("options") or []
    return bool(choices) or answer_input_type == "choice" or answer_type == "choice" or ("choice" in checker_type) or question_type == "multiple_choice"


def _strip_choice_leading_label(text: str) -> str:
    s = str(text or "").strip()
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"^\s*\(\s*([A-Za-z])\s*\)\s*", "", s)
    s = re.sub(r"^\s*([A-Za-z])\s*[.)]\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _choice_item_label_text(choice: object, index: int) -> tuple[str, str]:
    if isinstance(choice, dict):
        label = str(choice.get("label", "")).strip().upper() or chr(ord("A") + index)
        text = str(choice.get("text") or choice.get("content") or choice.get("value") or "").strip()
        return label, text
    return chr(ord("A") + index), str(choice or "").strip()


def _choice_alias_to_index(token: str) -> int | None:
    t = str(token or "").strip()
    if not t:
        return None
    t = t.replace("（", "(").replace("）", ")")
    m = re.match(r"^\(?\s*([A-Za-z])\s*\)?[.)]?$", t)
    if m:
        idx = ord(m.group(1).upper()) - ord("A")
        return idx if 0 <= idx <= 25 else None
    m = re.match(r"^([1-9]\d*)$", t)
    if m:
        return int(m.group(1)) - 1
    return None


def _normalize_choice_for_compare(value: object, choices: list) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    idx = _choice_alias_to_index(raw)
    if idx is not None and 0 <= idx < len(choices):
        _, choice_text = _choice_item_label_text(choices[idx], idx)
        return _strip_choice_leading_label(choice_text)
    raw_no_label = _strip_choice_leading_label(raw)
    for i, ch in enumerate(choices):
        _, choice_text = _choice_item_label_text(ch, i)
        ch_text = _strip_choice_leading_label(choice_text)
        if raw_no_label == ch_text:
            return ch_text
        label, _ = _choice_item_label_text(ch, i)
        if raw_no_label.upper() == label:
            return ch_text
        if raw_no_label == str(i + 1):
            return ch_text
    return raw_no_label


def _choice_value_to_label(value: object, choices: list) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    idx = _choice_alias_to_index(raw)
    if idx is not None and 0 <= idx < len(choices):
        label, _ = _choice_item_label_text(choices[idx], idx)
        return label
    normalized = _normalize_choice_for_compare(raw, choices)
    for i, ch in enumerate(choices):
        label, choice_text = _choice_item_label_text(ch, i)
        if _strip_choice_leading_label(choice_text) == normalized:
            return label
    return ""


def _normalize_choice_alias_answer(value: str, current_question: dict) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    choices = current_question.get("choices") or current_question.get("options") or []
    label = _choice_value_to_label(raw, choices if isinstance(choices, list) else [])
    return label or raw


def _choice_display_label_and_text(correct_value: object, choices: list) -> str:
    label = _choice_value_to_label(correct_value, choices)
    if label:
        for i, ch in enumerate(choices):
            ch_label, ch_text_raw = _choice_item_label_text(ch, i)
            if ch_label == label:
                ch_text = _strip_choice_leading_label(ch_text_raw)
                return f"({label}) {ch_text}"
    return str(correct_value or "").strip()

def update_progress(user_id, skill_id, is_correct):
    """
    ?湔?冽?脣漲 (Progress)
    V2.0 ?湔嚗????矽?渡?蝝??????蝑?/?舀活?貉?蝺渡???
    """
    progress = db.session.query(Progress).filter_by(user_id=user_id, skill_id=skill_id).first()
    now_time = datetime.now()

    if not progress:
        progress = Progress(
            user_id=user_id,
            skill_id=skill_id,
            consecutive_correct=1 if is_correct else 0,
            consecutive_wrong=0 if is_correct else 1,
            questions_solved=1,
            current_level=1,
            last_practiced=now_time
        )
        db.session.add(progress)
    else:
        progress.questions_solved += 1
        progress.last_practiced = now_time
        if is_correct:
            progress.consecutive_correct += 1
            progress.consecutive_wrong = 0
        else:
            progress.consecutive_correct = 0
            progress.consecutive_wrong += 1
    
    db.session.commit()

# ==========================================
# Routes (頝舐)
# ==========================================

@practice_bp.route('/adaptive_selection')
@login_required
def adaptive_selection_page():
    """Adaptive selection page."""
    curriculum = request.args.get('curriculum', 'general')
    curriculum_map = {'general': 'general', 'vocational': 'vocational', 'junior_high': 'junior_high'}
    
    # ?亥岷閰脣飛蝔?????蝭
    chapters = db.session.query(SkillCurriculum.chapter).filter_by(curriculum=curriculum).distinct().order_by(SkillCurriculum.chapter).all()
    chapter_list = [c[0] for c in chapters]

    return render_template('adaptive_selection.html', 
                           chapters=chapter_list, 
                           curriculum=curriculum,
                           curriculum_name=curriculum_map.get(curriculum, '?芰'))

@practice_bp.route('/adaptive_practice')
@login_required
def adaptive_practice_page():
    """Adaptive practice page."""
    mode = request.args.get('mode', 'single')
    skill_ids = request.args.get('skill_ids', '')
    skill_id = request.args.get('skill_id') or skill_ids
    curriculum = request.args.get('curriculum', '')
    volume = request.args.get('volume', '')
    chapter_id = request.args.get('chapter_id', '')
    learning_mode = request.args.get('learning_mode', '')
    practice_kind = request.args.get('practice_kind', '')

    chapter_bridge, chapter_bridge_hit = _resolve_b4_chapter_adaptive_entry(
        mode=mode,
        curriculum=curriculum,
        volume=volume,
        chapter_id=chapter_id,
        skill_ids=skill_ids,
    )
    if chapter_bridge_hit:
        mode = str(chapter_bridge.get("entry_mode") or mode)
        curriculum = str(chapter_bridge.get("curriculum") or curriculum)
        volume = str(chapter_bridge.get("volume") or volume)
        chapter_id = str(chapter_bridge.get("chapter_id") or chapter_id)
        skill_id = str(chapter_bridge.get("starter_skill_id") or skill_id)
        if not learning_mode:
            learning_mode = "teaching"
        if not practice_kind:
            practice_kind = "unit_practice"
    
    unit_name = "?芷?毀蝧?"
    if mode == 'single':
        # ?典銝璅∪?銝?skill_ids 撠望蝡??迂
        unit_name = f"?桀?蝺渡?嚗{skill_ids}"
    elif mode == 'chapter':
        unit_name = str(chapter_bridge.get("unit_name") or "蝡??芷?毀蝧?")
    elif mode == 'multiple':
        unit_name = "?芷蝯?蝺渡?"
    elif mode == 'review':
        curriculum_map = {'general': '?桅?', 'vocational': '?擃?', 'junior_high': '?葉'}
        unit_name = f"{curriculum_map.get(curriculum, '')} 蝮質?蝧?"

    current_app.logger.info(
        "[Phase5B-FixA][adaptive_practice_entry] raw_params=%s detected_mode=%s curriculum=%s volume=%s chapter_id=%s compat_used=%s resolved_target_skill_count=%s starter_skill=%s",
        dict(request.args),
        mode,
        curriculum,
        volume,
        chapter_id,
        bool(chapter_bridge.get("compat_path_used", False)),
        len(chapter_bridge.get("unit_skill_ids", [])) if chapter_bridge_hit else 0,
        chapter_bridge.get("starter_skill_id", "") if chapter_bridge_hit else "",
    )

    return render_template('adaptive_practice_v2.html', 
                           unit_name=unit_name,
                           mode=mode,
                           skill_ids=skill_ids,
                           skill_id=skill_id,
                           starter_skill_id=str(chapter_bridge.get("starter_skill_id") or "") if chapter_bridge_hit else "",
                           curriculum=curriculum,
                           chapter_id=chapter_id,
                           volume=volume,
                           learning_mode=learning_mode,
                           practice_kind=practice_kind,
                           unit_skill_ids=chapter_bridge.get("unit_skill_ids", []) if chapter_bridge_hit else [],
                           bootstrap_unit_skill_ids=chapter_bridge.get("bootstrap_unit_skill_ids", []) if chapter_bridge_hit else [],
                           chapter_bridge_compat_used=bool(chapter_bridge.get("compat_path_used", False)) if chapter_bridge_hit else False)


@practice_bp.route('/adaptive_summative')
@login_required
def adaptive_summative_page():
    """
    v1.1 PoC entrance for paper-aligned summative adaptive diagnosis.
    """
    skill_id = request.args.get('skill_id', '').strip()
    mode = request.args.get('mode', 'teaching').strip().lower()
    if mode not in {'assessment', 'teaching'}:
        mode = 'teaching'
    unit_name = _resolve_adaptive_unit_name(
        skill_id,
        request.args.get('unit_name', '?砍??拇?摮貊?嚗蜇蝯扯那?瘀?').strip(),
    )
    return render_template(
        'adaptive_practice_v2.html',
        unit_name=unit_name,
        skill_id=skill_id,
        mode=mode,
        student_id=current_user.id,
    )


@practice_bp.route('/adaptive_learning_entry')
@login_required
def adaptive_learning_entry_page():
    """Adaptive learning entry page."""
    units = [
        {"label": "?湔????", "skill_id": "jh_?詨飛1銝FourArithmeticOperationsOfIntegers"},
        {"label": "?????", "skill_id": "jh_?詨飛1銝FourArithmeticOperationsOfNumbers"},
        {"label": "?孵?????", "skill_id": "jh_?詨飛2銝FourOperationsOfRadicals"},
        {"label": "銝??甈∪?", "skill_id": "jh_?詨飛1銝OperationsOnLinearExpressions"},
        {"label": "憭?撘???蝞?", "skill_id": "jh_?詨飛2銝FourArithmeticOperationsOfPolynomial"},
    ]
    return render_template('adaptive_learning_entry.html', units=units)


@practice_bp.route('/practice')
def practice_query_entry():
    # Phase 6C-1R: URL-decode skill_id so that
    # vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition ??vh_?詨飛B4_ProbabilityDefinition
    # Already-decoded IDs pass through unchanged (unquote is idempotent).
    skill_id = _url_unquote((request.args.get("skill") or "").strip())
    if not skill_id:
        return redirect(url_for("dashboard"))
    return practice(skill_id)


@practice_bp.route('/practice/<path:skill_id>')
def practice(skill_id):
    # Phase 6C-1R: URL-decode path segment (Flask may or may not decode it
    # depending on the URL_MAP_STRICT_SLASHES setting; be explicit).
    skill_id = _url_unquote(skill_id)
    """?脣?孵???賜?蝺渡??"""
    switch_info = _prepare_skill_switch(skill_id)
    _log_practice_page_entry(skill_id, switch_info)
    requested_problem_type = (request.args.get("problem_type") or "").strip()
    is_pascal_runtime_request = _is_b4_pascal_triangle_request(skill_id, requested_problem_type)
    manual_review_info = None if is_pascal_runtime_request else MANUAL_REVIEW_SKILLS.get(skill_id)
    skill_info = db.session.get(SkillInfo, skill_id)
    if skill_id == B4_TREE_DIAGRAM_FREE_RESPONSE_SKILL_ID:
        skill_ch_name = skill_info.skill_ch_name if skill_info else "璅寧???"
    elif manual_review_info:
        skill_ch_name = manual_review_info["display_name"]
    else:
        skill_ch_name = skill_info.skill_ch_name if skill_info else "?芰???"

    # ?亥岷?蔭???
    prerequisites = db.session.query(SkillInfo).join(
        SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
    ).filter(
        SkillPrerequisites.skill_id == skill_id,
        SkillInfo.is_active.is_(True)
    ).order_by(SkillInfo.skill_ch_name).all()

    prereq_skills = [{'skill_id': p.skill_id, 'skill_ch_name': p.skill_ch_name} for p in prerequisites]
    tutor_config = get_effective_model_config('tutor')
    tutor_model_name = tutor_config.get('model', 'unknown')

    return render_template('index.html', 
                           skill_id=skill_id,
                           skill_ch_name=skill_ch_name,
                           prereq_skills=prereq_skills,
                           tutor_model_name=tutor_model_name,
                           practice_mode='standard',
                           manual_review_unavailable=manual_review_info)


@practice_bp.route('/practice/similar_questions')
@login_required
def similar_questions():
    """Render similar questions practice page."""
    tutor_config = get_effective_model_config('tutor')
    tutor_model_name = tutor_config.get('model', 'unknown')

    return render_template(
        'index.html',
        skill_id='similar_questions',
        skill_ch_name='憿?蝺渡?',
        prereq_skills=[],
        tutor_model_name=tutor_model_name,
        practice_mode='similar_practice',
    )

@practice_bp.route('/api/runtime_ai_status', methods=['GET'])
@login_required
def runtime_ai_status():
    """
    API: ??撖阡? runtime tutor model ????
    """
    from core.ai_settings import get_ai_settings_snapshot, get_google_model_label
    
    tutor_config = get_effective_model_config('tutor')
    architect_config = get_effective_model_config('architect')
    vision_config = get_effective_model_config('vision_analyzer')
    provider = tutor_config.get('provider', 'unknown')
    tutor_model = tutor_config.get('model', 'unknown')
    architect_model = architect_config.get('model', 'unknown')
    vision_model = vision_config.get('model', 'unknown')
    
    settings = get_ai_settings_snapshot()
    ai_mode_raw = settings.get("ai_global_strategy", "unknown")
    
    mode_map = {
        "cloud_first": "cloud",
        "local_first": "edge",
        "hybrid_balanced": "hybrid"
    }
    ai_mode = mode_map.get(ai_mode_raw, ai_mode_raw)
    
    display_name = get_google_model_label(tutor_model) if provider == "google" else tutor_model
    if tutor_model == 'unknown':
        display_name = 'unknown'
    
    # 蝪⊥? log
    current_app.logger.info(
        f"[RUNTIME AI STATUS] mode={ai_mode} provider={provider} "
        f"tutor_model={tutor_model} architect_model={architect_model} vision_analyzer_model={vision_model}"
    )
    
    return jsonify({
        "success": True,
        "ai_mode": ai_mode,
        "tutor_provider": provider,
        "tutor_model": tutor_model,
        "tutor_display_name": display_name,
        "architect_model": architect_model,
        "vision_analyzer_model": vision_model
    })

@practice_bp.route('/get_adaptive_question', methods=['GET'])
@login_required
def get_adaptive_question():
    """Return adaptive question payload for single/multiple/review modes."""
    mode = request.args.get('mode', 'single')
    
    # ?寞?銝?璅∪??脣???賢?銵?
    target_skill_ids = []
    # Review 璅∪?銝?weakness routing ?? target_skill_ids 蝮格??桐???踝?B4 generator fallback 隞?靘??蝧??? allowlisted B4??
    filtered_review_pool_for_generator_fallback = None
    
    # 隤輯岫靽⊥
    current_app.logger.info(f"[Adaptive Question] Mode: {mode}")
    current_app.logger.info(f"[Adaptive Question] Request args: {request.args}")
    
    try:
        if mode == 'review':
            # Phase 8: 蝮質?蝧芋撘?撘梢??芸????臬???RAG Skill Routing
            curriculum = request.args.get('curriculum')
            if not curriculum:
                return jsonify({"error": "蝮質?蝧芋撘?閬?curriculum ?"}), 400
            
            if 'review_skill_pool' not in session or not session['review_skill_pool']:
                current_app.logger.info(f"[Review Mode] Initializing skill pool for Curriculum: {curriculum}")
                from models import SkillCurriculum
                skills = db.session.query(SkillCurriculum.skill_id).filter_by(
                    curriculum=curriculum
                ).distinct().all()
                session['review_skill_pool'] = [s.skill_id for s in skills]
                session.modified = True

            pool = session.get('review_skill_pool', [])
            pool, review_audits = filter_skill_pool_for_b4_chapter1_deterministic_adaptive(pool)
            filtered_review_pool_for_generator_fallback = pool
            if review_audits:
                current_app.logger.info("[B4 Adaptive Preflight] review_pool_audit=%s", review_audits)

            stats = session.get('skill_stats', {})
            history = session.get('review_history', [])
            last_skill = history[-1]['skill_id'] if history else None

            from core.adaptive_engine import select_review_skill
            selected_skill = select_review_skill(pool, stats, last_skill)
            
            target_skill_ids = [selected_skill] if selected_skill else pool
            current_app.logger.info(f"[Review Mode] Selected Skill via Weakness Routing: {selected_skill}")
            
        elif mode in ['single', 'multiple']:
            # ?桐???蝡?璅∪?嚗??蝭?迂?脣????
            skill_ids_param = request.args.get('skill_ids', '')
            if not skill_ids_param:
                return jsonify({"error": f"{mode} 璅∪??閬?skill_ids ?"}), 400
            
            # skill_ids ?航?臬銝蝡?????????蝭?”
            chapter_names = [ch.strip() for ch in skill_ids_param.split(',')]
            current_app.logger.info(f"[{mode.upper()} Mode] Chapter names: {chapter_names}")
            
            from models import SkillCurriculum
            skills = db.session.query(SkillCurriculum.skill_id).filter(
                SkillCurriculum.chapter.in_(chapter_names)
            ).distinct().all()
            target_skill_ids = [s.skill_id for s in skills]
            current_app.logger.info(f"[{mode.upper()} Mode] Found {len(target_skill_ids)} skills: {target_skill_ids[:5]}")
        
        else:
            return jsonify({"error": f"銝?渡?璅∪?: {mode}"}), 400

        target_skill_ids, adaptive_audits = filter_skill_pool_for_b4_chapter1_deterministic_adaptive(target_skill_ids)
        if adaptive_audits:
            current_app.logger.info("[B4 Adaptive Preflight] adaptive_target_skill_audit=%s", adaptive_audits)

        if not target_skill_ids:
            current_app.logger.error(f"[Adaptive Question] No skills found for mode={mode}")
            return jsonify({"error": "?曆??啁泵??隞嗥???賢??"}), 404

        # --- Phase 4F-Main-A: B4 Chapter 1 generator-first / generator fallback ---
        # Pure allowlisted B4 pools skip DB TextbookExample entirely (generator-first).
        # Mixed pools keep DB-first (RS recommend_question); empty DB falls back to allowlisted B4 generators.
        # Review mode: fallback candidates come from the full filtered review_skill_pool (not the weakness-narrowed singleton).
        gen_seed = request.args.get("gen_seed", type=int)
        pick_rng = random.Random(gen_seed) if gen_seed is not None else random.Random()

        pure_b4 = is_pure_b4_allowlisted_adaptive_pool(target_skill_ids)
        candidate_pool_for_b4_fallback = (
            filtered_review_pool_for_generator_fallback
            if mode == "review" and filtered_review_pool_for_generator_fallback is not None
            else target_skill_ids
        )
        b4_only_candidates = allowlisted_b4_candidates(candidate_pool_for_b4_fallback)

        question_template = None
        skill_id_for_generate: str | None = None
        difficulty_level = request.args.get("level", type=int) or 1
        source_type: str | None = None

        if pure_b4:
            skill_id_for_generate = pick_rng.choice(target_skill_ids)
            source_type = "generator_first"
            current_app.logger.info(
                "[B4 Adaptive Main-A] generator-first pool=%s skill=%s",
                target_skill_ids,
                skill_id_for_generate,
            )
        else:
            question_template = recommend_question(current_user.id, target_skill_ids)
            if question_template is None and b4_only_candidates:
                skill_id_for_generate = pick_rng.choice(b4_only_candidates)
                source_type = "generator_fallback"
                current_app.logger.info(
                    "[B4 Adaptive Main-A] generator-fallback after empty DB pool skill=%s",
                    skill_id_for_generate,
                )
            elif question_template is not None:
                skill_id_for_generate = question_template.skill_id
                if getattr(question_template, "difficulty_level", None) is not None:
                    difficulty_level = question_template.difficulty_level
                source_type = "db_textbook_example"
            else:
                return jsonify({"error": "憿澈銝剖歇?∪??拍?憿?臭??刻??"}), 404

        if is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id_for_generate):
            persist_b4_chap2_gated_event(
                gated_event_type="not_enabled_skill",
                skill_id=str(skill_id_for_generate),
                problem_type_id=None,
                public_message=B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR,
            )
            return jsonify({"error": B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR}), 422

        inner_router_seed = gen_seed
        seed_derivation = "identity"
        if pure_b4 and gen_seed is not None:
            inner_router_seed = _stable_b4_inner_seed(skill_id_for_generate, gen_seed)
            seed_derivation = "b4_stable_inner_seed"

        gen_kwargs: dict = {"level": difficulty_level}
        if gen_seed is not None:
            gen_kwargs["seed"] = inner_router_seed

        if is_b4_chapter2_phase6c1_deterministic_skill(skill_id_for_generate):
            chap2_seed = inner_router_seed if gen_seed is not None else None
            chap2_payload = generate_for_chap2_skill(
                skill_id=skill_id_for_generate,
                level=difficulty_level,
                seed=chap2_seed,
                problem_type_id=None,
            )
            ok_p2, deny_p2 = validate_b4_chap2_phase6c1_generator_payload(
                skill_id_for_generate,
                chap2_payload,
            )
            if not ok_p2:
                return jsonify(
                    {"error": _b4_chap2_public_payload_validation_message(deny_p2)}
                ), 422
            data = chap2_payload
            if "correct_answer" not in data and "answer" in data:
                data["correct_answer"] = data["answer"]
        else:
            mod = get_skill(skill_id_for_generate)
            if not mod:
                return jsonify({
                    "success": False,
                    "error_code": "SKILL_MODULE_NOT_FOUND",
                    "skill_id": skill_id_for_generate,
                    "message": "題目載入失敗，請通知教師檢查此技能。"
                }), 404
            from core.legacy_generator_adapter import invoke_skill_generate, normalize_runtime_value
            data = invoke_skill_generate(
                mod,
                level=difficulty_level,
                seed=inner_router_seed if gen_seed is not None else None,
                skill_id=skill_id_for_generate
            )
            data = normalize_runtime_value(data)

        ok_payload, deny_reason = validate_b4_deterministic_adaptive_generator_payload(
            skill_id_for_generate,
            data,
        )
        if not ok_payload:
            audit_blob = format_adaptive_question_audit_dict(
                skill_id_for_generate,
                data,
                source_type="rejected_excluded_problem_type",
            )
            if gen_seed is not None:
                audit_blob["outer_gen_seed"] = gen_seed
                audit_blob["inner_router_seed"] = inner_router_seed
                audit_blob["seed_derivation"] = seed_derivation
            audit_blob["reject_detail"] = deny_reason
            current_app.logger.error(
                "[B4 Adaptive Preflight] blocked_generated_payload skill=%s reason=%s",
                skill_id_for_generate,
                deny_reason,
            )
            body = {
                "error": "Generated question is outside deterministic adaptive scope.",
                "detail": deny_reason,
            }
            if request.args.get("adaptive_audit") == "1":
                body["adaptive_audit"] = audit_blob
            return jsonify(body), 422

        audit_blob = format_adaptive_question_audit_dict(
            skill_id_for_generate,
            data,
            source_type=source_type,
        )
        if gen_seed is not None:
            audit_blob["outer_gen_seed"] = gen_seed
            audit_blob["inner_router_seed"] = inner_router_seed
            audit_blob["seed_derivation"] = seed_derivation
        current_app.logger.info("[B4 Adaptive Preflight] question_audit=%s", audit_blob)

        # 皞? Session 鞈? (??next_question ?摩憿撮)
        session_data = _normalize_gencode_runtime_payload(data.copy(), skill_id=skill_id_for_generate)
        for k in ['image', 'fig', 'figure', 'image_base64', 'visuals']:
            if k in session_data: del session_data[k]

        set_current(skill_id_for_generate, session_data)
        stored_adaptive = get_current()

        question_db_id = question_template.id if question_template else 0

        payload_out = _finalize_practice_question_api_fields(
            {
                "question_id": question_db_id,
                "skill_id": skill_id_for_generate,
                "question_uid": stored_adaptive.get("question_uid", ""),
                "question_text_hash": stored_adaptive.get("question_text_hash", ""),
                "mode": "adaptive",
                "new_question_text": data.get("question_text"),
                "correct_answer": data.get("correct_answer"),
                "context_string": data.get("context_string", ""),
                "image_base64": data.get("image_base64", ""),
                "visual_spec": data.get("visual_spec", {}),
                "visual_aids": data.get("visual_aids", []),
                "answer_type": data.get("answer_type", "text"),
                "problem_type_id": data.get("problem_type_id") or data.get("problem_type"),
                "scenario_id": data.get("scenario_id", ""),
                "scenario_family": data.get("scenario_family", ""),
            },
            skill_id=skill_id_for_generate,
        )
        if request.args.get("adaptive_audit") == "1":
            payload_out["adaptive_audit"] = audit_blob
        return jsonify(payload_out)
    except Exception as e:
        current_app.logger.error(f"???芷???桀仃?? {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"???芷???格??潛??折?航炊: {str(e)}"}), 500


def _materialize_question_image(raw_image: str) -> str:
    if not raw_image or not isinstance(raw_image, str):
        return raw_image
    
    val = raw_image.strip()
    if not val:
        return raw_image
        
    if val.startswith("/") or val.startswith("http://") or val.startswith("https://"):
        return raw_image
        
    b64_data = val
    if b64_data.startswith("data:"):
        parts = b64_data.split(",", 1)
        if len(parts) == 2:
            b64_data = parts[1]
        else:
            return raw_image
            
    try:
        import base64
        import hashlib
        import os
        from flask import current_app
        
        decoded_bytes = base64.b64decode(b64_data)
        if not decoded_bytes:
            return raw_image
            
        sha256_hash = hashlib.sha256(decoded_bytes).hexdigest()
        filename = f"{sha256_hash}.png"
        
        rel_dir = "uploads/question_assets/generated_cache"
        abs_dir = os.path.join(current_app.root_path, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        
        file_path = os.path.join(abs_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(decoded_bytes)
                
        return f"/{rel_dir}/{filename}"
    except Exception:
        return raw_image


@practice_bp.route('/get_next_question')
@login_required
def next_question():
    """API: ??銝?憿?
    
    ?舀 mode ?嚗?
    - ?芸葆 mode ??mode?nit嚗窒?刻?銵嚗kill ???桐? skill_id ?粹?
    - mode=unit嚗誑?桀??粹?嚗? (curriculum, volume, chapter) ?豢? pattern skill 敺憿?
      ???chapter嚗??volume?urriculum嚗撩?? curriculum ??session嚗olume ?舐蝛箏?銝脩 selector ?冽??
    """
    prune_practice_session()
    mode = request.args.get('mode', '')
    # Phase 6C-1R: URL-decode so encoded CJK skill_ids are resolved correctly.
    skill_id = _url_unquote(request.args.get('skill', 'remainder'))
    switch_info = _prepare_skill_switch(skill_id)
    current_app.logger.info(
        "[PRACTICE get_next_question] frontend_requested_skill_id=%s session_uid_before=%s cleared=%s",
        skill_id,
        switch_info.get("previous_question_uid"),
        switch_info.get("cleared_keys"),
    )
    current_app.logger.info("[GENCODE WEB RUNTIME] skill_id=%s", request.args.get('skill', ''))
    current_app.logger.info("[GENCODE WEB RUNTIME] decoded_skill_id=%s", skill_id)
    problem_type = request.args.get('problem_type', '')
    requested_component_id = (
        request.args.get('component_id') or request.args.get('component') or ''
    ).strip() or None
    variant = request.args.get('variant', B4_TREE_DIAGRAM_DEFAULT_VARIANT)
    tree_diagram_index = request.args.get('tree_diagram_index', type=int)
    pascal_triangle_index = request.args.get('pascal_triangle_index', type=int)
    requested_level = request.args.get('level', type=int)

    # [?桀??粹?] mode=unit嚗??桀???pattern skill
    if mode == 'unit':
        chapter = request.args.get('chapter', '').strip()
        volume = request.args.get('volume', '').strip()
        curriculum = request.args.get('curriculum') or session.get('current_curriculum', 'junior_high')
        if not chapter:
            return jsonify({"error": "?桀?璅∪????chapter ?"}), 400
        if not volume:
            vols = db.session.query(SkillCurriculum.volume).filter(
                SkillCurriculum.curriculum == curriculum,
                SkillCurriculum.chapter == chapter
            ).distinct().all()
            vols = [v[0] for v in vols if v[0]]
            if len(vols) != 1:
                return jsonify({"error": "?桀?璅∪????volume ?嚗府 chapter 撠?憭???volume嚗?"}), 400
            volume = vols[0]
        try:
            from core.unit_selector import select_pattern_skill_for_unit
            skill_id = select_pattern_skill_for_unit(curriculum, volume, chapter)
        except Exception as e:
            current_app.logger.error(f"?桀? selector 憭望?: {e}")
            return jsonify({"error": f"?⊥???閰脣??憿?: {str(e)}"}), 500
        if not skill_id:
            return jsonify({"error": "閰脣???∪?函?憿????"}), 404

    manual_review_info = None if _is_b4_pascal_triangle_request(skill_id, problem_type) else MANUAL_REVIEW_SKILLS.get(skill_id)
    if manual_review_info:
        review_stem = (
            f"<strong>{manual_review_info['display_name']}：暫緩 / 尚未開放一般自動判分練習</strong><br>"
            f"{manual_review_info['reason']}<br><br>"
            "此題型目前屬於 AI 手寫判分 / 教師審閱候選題型，尚未開放一般自動判分練習。<br>"
            "未來可透過手寫作答、OCR / Vision、AI 助教判斷 correct / partially_correct / needs_review。"
        )
        return jsonify(_finalize_practice_question_api_fields({
            "manual_review_unavailable": True,
            "new_question_text": review_stem,
            "context_string": "",
            "inequality_string": "",
            "consecutive_correct": 0,
            "current_level": "暫緩",
            "image_base64": "",
            "visual_aids": [],
            "answer_type": "unavailable",
            "reason": manual_review_info["reason"],
            "future_path": manual_review_info["future_path"],
        }, skill_id=skill_id))

    # Phase 6C-1R2: gated Chap2 skills ??clear gate error instead of importing missing skills.<id>
    if is_b4_chapter2_skill_not_enabled_in_phase6c1(skill_id):
        persist_b4_chap2_gated_event(
            gated_event_type="not_enabled_skill",
            skill_id=str(skill_id),
            problem_type_id=str(problem_type).strip() if problem_type else None,
            public_message=B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR,
        )
        return jsonify({"error": B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR}), 422

    # Phase 7B: gated Chap3 skills
    if is_b4_chapter3_skill_not_enabled(skill_id):
        return jsonify({"error": B4_CHAP3_SKILL_NOT_ENABLED_PUBLIC_ERROR}), 422
    if skill_id in B4_CHAP3_REQUIRES_EXPLICIT_PROBLEM_TYPE_SKILLS and not str(problem_type or "").strip():
        return jsonify({"error": B4_CHAP3_SKILL_NOT_ENABLED_PUBLIC_ERROR}), 422

    skill_info = get_skill_info(skill_id)
    # [?桀?璅∪?] ?迂 pattern skill ??瑼?????DB 閮餃????臬憿?
    if not skill_info and skill_id != 'instant_upload':
        if _is_b4_tree_diagram_request(skill_id, problem_type):
            skill_info = {"input_type": "handwriting", "skill_id": B4_TREE_DIAGRAM_FREE_RESPONSE_SKILL_ID}
        elif _is_b4_pascal_triangle_request(skill_id, problem_type):
            skill_info = {"input_type": "handwriting", "skill_id": B4_PASCAL_TRIANGLE_FREE_RESPONSE_SKILL_ID}
        elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
            # Phase 6C-1R: Chap2 P0 skills may not have a DB SkillInfo row.
            # Bypass DB lookup; generator handles everything.
            skill_info = {"input_type": "text", "skill_id": skill_id}
        elif is_b4_chapter3_phase7b_runtime_skill(skill_id):
            skill_info = {"input_type": "text", "skill_id": skill_id}
        elif mode == 'unit':
            skill_info = {"input_type": "text", "skill_id": skill_id}
        elif _has_runtime_skill_module(skill_id):
            # Gencode-published skills may be available before a SkillInfo row is provisioned.
            skill_info = {"input_type": "text", "skill_id": skill_id}
        else:
            return jsonify({"error": f"???{skill_id} 銝??冽??芸???"}), 404
        
    # [Feature] Instant Practice Mode (Short Loop)
    if skill_id == 'instant_upload':
        current = get_current()
        if not current or 'is_instant_upload' not in current:
             return jsonify({"error": "No instant upload session found"}), 404
        
        # Return either base64 or URL path. Frontend handles both in the 'image_base64' field logic (simplification)
        # or we add a specific field. Let's use image_base64 field as a generic image source carrier for now or add image_url.
        img_src = current.get("image_path") if current.get("image_path") else current.get("image_base64", "")
        
        instant_stem = str(current.get("question_text", "") or "")
        return jsonify(_finalize_practice_question_api_fields({
            "new_question_text": instant_stem,
            "context_string": "",
            "inequality_string": "",
            "consecutive_correct": 0,
            "current_level": 1,
            "image_base64": img_src,
            "visual_aids": [],
            "answer_type": "text",
            "is_instant_upload": True,
        }, skill_id=skill_id))
    try:
        # 1. Resolve runtime route with published V3 facade precedence.
        from core.generator_route_resolver import resolve_runtime_route_decision
        from core.legacy_generator_adapter import invoke_legacy_generator, normalize_legacy_payload

        # Load skill module
        reload_runtime = False
        if _is_b4_tree_diagram_request(skill_id, problem_type) or _is_b4_pascal_triangle_request(skill_id, problem_type):
            route_decision = None
        elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
            route_decision = None
        else:
            reload_runtime = _runtime_reload_skill_modules()
            route_decision = resolve_runtime_route_decision(
                skill_id=skill_id,
                reload_module=reload_runtime,
                is_b4_phase7b_runtime_skill=is_b4_chapter3_phase7b_runtime_skill(skill_id),
                legacy_module_loader=get_skill,
            )

        mod = route_decision.module if route_decision is not None else None

        wrapper_loaded = bool(mod is not None and hasattr(mod, "generate"))
        wrapper_path = f"skills.{skill_id}"
        route_mode = route_decision.mode if route_decision is not None else "special_b4"
        route_reason = route_decision.reason if route_decision is not None else "special_b4_runtime"
        legacy_fallback_used = bool(route_decision.legacy_fallback_used) if route_decision is not None else False
        legacy_fallback_reason = route_decision.legacy_fallback_reason if route_decision is not None else ""
        route_source = "gencode_wrapper" if route_mode == "v3" else "legacy"
        module_file = ""
        if mod is not None:
            module_file = str(getattr(mod, "__file__", "") or "")

        current_app.logger.info("[GENCODE WEB RUNTIME] wrapper_loaded=%s", str(wrapper_loaded).lower())
        current_app.logger.info("[GENCODE WEB RUNTIME] wrapper_path=%s", wrapper_path)
        current_app.logger.info("[GENCODE WEB RUNTIME] module_file=%s reload=%s", module_file, reload_runtime)
        current_app.logger.info("[GENCODE WEB RUNTIME] route_source=%s", route_source)
        current_app.logger.info(
            "[GENCODE WEB RUNTIME] route_mode=%s route_reason=%s legacy_fallback_used=%s legacy_fallback_reason=%s",
            route_mode,
            route_reason,
            str(legacy_fallback_used).lower(),
            legacy_fallback_reason,
        )
        if wrapper_loaded and hasattr(mod, "GENERATOR_SPECS"):
            current_app.logger.info("[GENCODE WEB RUNTIME] generator_specs=%s", getattr(mod, "GENERATOR_SPECS", []))

        # Determine difficulty level
        current_curriculum_context = session.get('current_curriculum', 'general')
        curriculum_entry = db.session.query(SkillCurriculum).filter_by(
            skill_id=skill_id,
            curriculum=current_curriculum_context
        ).first()

        if requested_level: 
            difficulty_level = requested_level
        elif curriculum_entry and curriculum_entry.difficulty_level: 
            difficulty_level = curriculum_entry.difficulty_level
        else:
            difficulty_level = 1 

        progress = db.session.query(Progress).filter_by(user_id=current_user.id, skill_id=skill_id).first()
        consecutive = progress.consecutive_correct if progress else 0

        # AI prereq query
        prereq_query = db.session.query(SkillInfo).join(
            SkillPrerequisites, SkillInfo.skill_id == SkillPrerequisites.prerequisite_id
        ).filter(
            SkillPrerequisites.skill_id == skill_id,
            SkillInfo.is_active.is_(True)
        ).order_by(SkillInfo.skill_ch_name).all()
        
        prereq_info_for_ai = [{'id': p.skill_id, 'name': p.skill_ch_name} for p in prereq_query]

        resolved_mode = route_mode
        resolved_route_source = route_reason

        # Handle legacy route separately (strictly no retry loop, single call, only pass level)
        if resolved_mode == "legacy":
            # final route log
            current_app.logger.info(
                "[GENERATOR ROUTE FINAL]\n"
                "skill_id=%s\n"
                "module_file=%s\n"
                "initial_route_source=%s\n"
                "resolved_mode=legacy\n"
                "resolved_route_source=legacy_skill\n"
                "reason=%s\n"
                "passed_params=['level']",
                skill_id,
                module_file,
                route_source,
                route_reason
            )
            data = invoke_legacy_generator(
                mod,
                skill_id=skill_id,
                level=difficulty_level,
            )
            route_source = "legacy_skill"
        else:
            # Modern generator path (includes retry loops)
            max_retries = 5
            data = None
            
            for attempt in range(max_retries):
                try:
                    if _is_b4_tree_diagram_request(skill_id, problem_type):
                        data = _build_b4_tree_diagram_runtime_payload(variant, tree_diagram_index)
                    elif _is_b4_pascal_triangle_request(skill_id, problem_type):
                        data = _build_b4_pascal_triangle_runtime_payload(pascal_triangle_index)
                    elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
                        if problem_type and is_b4_chapter2_excluded_problem_type(problem_type):
                            persist_b4_chap2_gated_event(
                                gated_event_type="reserved_problem_type",
                                skill_id=str(skill_id),
                                problem_type_id=str(problem_type),
                                public_message=B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR,
                            )
                            return jsonify(
                                {"error": B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR}
                            ), 422
                        gen_seed = request.args.get("gen_seed", type=int)
                        chap2_payload = generate_for_chap2_skill(
                            skill_id=skill_id,
                            level=difficulty_level,
                            seed=gen_seed,
                            problem_type_id=problem_type or None,
                        )
                        ok_p, deny_r = validate_b4_chap2_phase6c1_generator_payload(skill_id, chap2_payload)
                        if not ok_p:
                            current_app.logger.error(
                                "[Chap2 Phase6C1R] payload blocked skill=%s reason=%s", skill_id, deny_r
                            )
                            return jsonify(
                                {"error": _b4_chap2_public_payload_validation_message(deny_r)}
                            ), 422
                        data = chap2_payload
                    elif resolved_mode == "b4_phase7b":
                        gen_seed = request.args.get("gen_seed", type=int)
                        previous_current = get_current() or {}
                        previous_scenario_id = str(previous_current.get("scenario_id") or "")
                        previous_question_text = str(previous_current.get("question_text") or "")
                        previous_parameter_signature = str(previous_current.get("parameter_signature") or "")
                        previous_scenario_family = str(previous_current.get("scenario_family") or "")
                        previous_outcome_set_signature = str(previous_current.get("outcome_set_signature") or "")
                        chap3_payload = generate_for_chap3_skill(
                            skill_id=skill_id,
                            level=difficulty_level,
                            seed=gen_seed,
                            problem_type_id=problem_type or None,
                        )
                        if difficulty_level <= 1 and not str(problem_type or "").strip():
                            deterministic_mixed_suffixes = {
                                "StatisticalBasicConcepts",
                                "SamplingSurvey",
                                "SamplingMethods",
                                "DataOrganizationAndCharts",
                                "StatisticalChartReading",
                                "CumulativeFrequencyTablesAndGraphs",
                                "FrequencyDistributionTableConstruction",
                                "HistogramsAndFrequencyPolygons",
                                "CentralTendencyMeasures",
                                "DispersionMeasures",
                                "WeightedMean",
                                "VarianceAndStandardDeviation",
                                "LinearTransformationOfData",
                                "NormalDistributionAndEmpiricalRule",
                            }
                            if any(str(skill_id).endswith(sfx) for sfx in deterministic_mixed_suffixes):
                                retry_count = 0
                                retry_limit = 3
                                open_ended_tokens = ["請", "說明", "理由", "解釋", "作答", "回答", "證明", "計算過程"]
                                while retry_count < retry_limit:
                                    current_question_text = str(chap3_payload.get("question_text") or "")
                                    current_scenario_id = str(chap3_payload.get("scenario_id") or "")
                                    current_parameter_signature = str(chap3_payload.get("parameter_signature") or "")
                                    current_scenario_family = str(chap3_payload.get("scenario_family") or "")
                                    current_outcome_set_signature = str(chap3_payload.get("outcome_set_signature") or "")
                                    current_pattern_id = str(chap3_payload.get("question_pattern_id") or "")
                                    current_table_hash = str(chap3_payload.get("table_spec_hash") or "")
                                    current_chart_hash = str(chap3_payload.get("chart_spec_hash") or "")
                                    current_visual_hash = str(chap3_payload.get("visual_asset_hash") or "")
                                    previous_pattern_id = str(previous_current.get("question_pattern_id") or "")
                                    previous_table_hash = str(previous_current.get("table_spec_hash") or "")
                                    previous_chart_hash = str(previous_current.get("chart_spec_hash") or "")
                                    previous_visual_hash = str(previous_current.get("visual_asset_hash") or "")

                                    duplicate_hit = (
                                        (current_question_text and current_question_text == previous_question_text)
                                        or (current_scenario_id and current_scenario_id == previous_scenario_id)
                                        or (current_parameter_signature and current_parameter_signature == previous_parameter_signature)
                                        or (current_scenario_family and current_scenario_family == previous_scenario_family)
                                        or (
                                            current_outcome_set_signature
                                            and current_outcome_set_signature == previous_outcome_set_signature
                                        )
                                        or (current_pattern_id and current_pattern_id == previous_pattern_id)
                                        or (current_table_hash and current_table_hash == previous_table_hash)
                                        or (current_chart_hash and current_chart_hash == previous_chart_hash)
                                        or (current_visual_hash and current_visual_hash == previous_visual_hash)
                                    )
                                    open_ended_hit = any(tok in current_question_text for tok in open_ended_tokens)
                                    if not duplicate_hit and not open_ended_hit:
                                        break
                                    retry_count += 1
                                    retry_seed = (
                                        (gen_seed + retry_count + 7000)
                                        if gen_seed is not None
                                        else random.randint(1, 10_000_000)
                                    )
                                    chap3_payload = generate_for_chap3_skill(
                                        skill_id=skill_id,
                                        level=difficulty_level,
                                        seed=retry_seed,
                                        problem_type_id=problem_type or None,
                                    )

                                rt = chap3_payload.get("router_trace") or {}
                                final_question_text = str(chap3_payload.get("question_text") or "")
                                final_duplicate = (
                                    (final_question_text and final_question_text == previous_question_text)
                                    or (str(chap3_payload.get("scenario_id") or "") and str(chap3_payload.get("scenario_id") or "") == previous_scenario_id)
                                    or (str(chap3_payload.get("parameter_signature") or "") and str(chap3_payload.get("parameter_signature") or "") == previous_parameter_signature)
                                    or (str(chap3_payload.get("scenario_family") or "") and str(chap3_payload.get("scenario_family") or "") == previous_scenario_family)
                                    or (str(chap3_payload.get("outcome_set_signature") or "") and str(chap3_payload.get("outcome_set_signature") or "") == previous_outcome_set_signature)
                                )
                                rt["duplicate_guard_attempted"] = True
                                rt["duplicate_guard_retry_count"] = retry_count
                                rt["duplicate_guard_fallback_reason"] = (
                                    "retry_limit_reached" if final_duplicate else ""
                                )
                                chap3_payload["router_trace"] = rt
                        ok_p, deny_r = validate_b4_chap3_phase7b_generator_payload(skill_id, chap3_payload)
                        if not ok_p:
                            current_app.logger.error(
                                "[Chap3 Phase7B] payload blocked skill=%s reason=%s", skill_id, deny_r
                            )
                            return jsonify(
                                {"error": _b4_chap3_public_payload_validation_message(deny_r)}
                            ), 422
                        data = chap3_payload
                    else:
                        gen_seed = request.args.get("gen_seed", type=int)
                        if gen_seed is None:
                            gen_seed = random.randint(0, 10_000_000)

                        # Determine selection mode: default to curriculum_sequence
                        p_mode = request.args.get("mode", "").strip()
                        if not p_mode:
                            p_mode = "curriculum_sequence"

                        picked_component_id = None
                        if wrapper_loaded and hasattr(mod, "GENERATOR_KEYS") and p_mode == "curriculum_sequence":
                            from core.gencode.services.v3_curriculum_ordering_service import get_sorted_component_ids_for_skill
                            raw_conn = db.engine.raw_connection()
                            try:
                                sorted_keys = get_sorted_component_ids_for_skill(raw_conn, skill_id, list(mod.GENERATOR_KEYS))
                            finally:
                                raw_conn.close()

                            if sorted_keys:
                                session_key = f"v3_sequence_{skill_id}"
                                seq_data = session.get(session_key)
                                if not isinstance(seq_data, dict) or seq_data.get("ordered_component_ids") != sorted_keys:
                                    seq_data = {
                                        "skill_id": skill_id,
                                        "current_round": 1,
                                        "ordered_component_ids": sorted_keys,
                                        "current_component_index": 0,
                                        "completed_component_ids": [],
                                    }

                                idx = seq_data.get("current_component_index", 0)
                                if idx >= len(sorted_keys):
                                    idx = 0
                                    seq_data["current_round"] = seq_data.get("current_round", 1) + 1
                                    seq_data["completed_component_ids"] = []

                                picked_component_id = sorted_keys[idx]
                                seq_data["current_component_index"] = idx + 1
                                if picked_component_id not in seq_data["completed_component_ids"]:
                                    seq_data["completed_component_ids"].append(picked_component_id)

                                session[session_key] = seq_data
                                session.modified = True

                        # final route log for modern
                        current_app.logger.info(
                            "[GENERATOR ROUTE FINAL]\n"
                            "skill_id=%s\n"
                            "module_file=%s\n"
                            "initial_route_source=%s\n"
                            "resolved_mode=modern\n"
                            "resolved_route_source=gencode_wrapper\n"
                            "reason=%s\n"
                            "passed_params=['level','seed','component_id']",
                            skill_id,
                            module_file,
                            route_source,
                            route_reason
                        )

                        try:
                            from core.legacy_generator_adapter import invoke_skill_generate, normalize_runtime_value
                            effective_component_id = requested_component_id or picked_component_id
                            data = invoke_skill_generate(
                                mod,
                                level=difficulty_level,
                                seed=gen_seed,
                                component_id=effective_component_id,
                                problem_type_id=problem_type or None,
                                skill_id=skill_id
                            )
                            data = normalize_runtime_value(data)
                        except Exception as generate_exc:
                            from core.gencode.services.component_tracker_service import save_tracker_record
                            if picked_component_id:
                                try:
                                    raw_conn = db.engine.raw_connection()
                                    try:
                                        eid = int(picked_component_id.split("_")[1])
                                        save_tracker_record(
                                            raw_conn,
                                            textbook_example_id=eid,
                                            skill_id=skill_id,
                                            gencode_status="failed",
                                            gencode_error_log=f"runtime_generation_error: {str(generate_exc)}",
                                        )
                                        raw_conn.commit()
                                    finally:
                                        raw_conn.close()
                                except Exception:
                                    pass
                            raise generate_exc

                        route_source = "gencode_wrapper" if wrapper_loaded else "legacy"

                    # Normalize question fields if needed
                    if "question" in data and "question_text" not in data:
                        data["question_text"] = data["question"]
                    if "answer" in data and "correct_answer" not in data:
                        data["correct_answer"] = data["answer"]

                    if data and "question_text" in data and "correct_answer" in data:
                        break
                except Exception as e:
                    current_app.logger.warning(f"憿???岫 ({attempt+1}/{max_retries}): {e}")
                    if attempt == max_retries - 1: raise e
        
        # 皞? Session 鞈?
        data['context_string'] = data.get('context_string', data.get('inequality_string', ''))
        data['prereq_skills'] = prereq_info_for_ai
        
        # [?詨??脩戌] 皜? Session嚗Ⅱ靽????亙摰寧???JSON 摨???
        session_data = _normalize_gencode_runtime_payload(data.copy(), skill_id=skill_id)
        # ??? 'image' ??'Figure' ?賊??萄?
        for k in ['image', 'fig', 'figure', 'image_base64', 'visuals']:
            if k in session_data: del session_data[k]
        
        set_current(skill_id, session_data)
        stored_current = get_current()
        session_data["question_uid"] = stored_current.get("question_uid", "")
        session_data["question_text_hash"] = stored_current.get("question_text_hash", "")
        session_data["skill_id"] = skill_id
        _log_runtime_generate_payload(skill_id, session_data, module_file=module_file if wrapper_loaded else "")

        response_payload = _finalize_practice_question_api_fields({
            "skill_id": skill_id,
            "question_uid": session_data.get("question_uid", ""),
            "question_text_hash": session_data.get("question_text_hash", ""),
            "question_text": session_data.get("question_text", ""),
            "new_question_text": session_data.get("question_text", ""),
            "message": session_data.get("message", ""),
            "choices": session_data.get("choices", []),
            "choices_display": session_data.get("choices", []),
            "context_string": session_data.get("context_string", ""),
            "inequality_string": session_data.get("inequality_string", ""),
            "consecutive_correct": consecutive,
            "current_level": difficulty_level,
            "image_base64": _materialize_question_image(data.get("image_base64", "")),
            "visual_spec": data.get("visual_spec", {}),
            "visual_aids": session_data.get("visual_aids", data.get("visual_aids", [])),
            "table_data": session_data.get("table_data", data.get("table_data", {})),
            "table_question": session_data.get("table_question", data.get("table_question", {})),
            "subquestions": session_data.get("subquestions", data.get("subquestions", [])),
            "table": session_data.get("table", {}),
            "table_title": session_data.get("table_title", ""),
            "answer_type": session_data.get("answer_type", (skill_info.get("input_type", "text") if isinstance(skill_info, dict) else getattr(skill_info, "input_type", "text"))),
            "answer_input_type": session_data.get("answer_input_type", session_data.get("answer_type", (skill_info.get("input_type", "text") if isinstance(skill_info, dict) else getattr(skill_info, "input_type", "text")))),
            "question_type": session_data.get("question_type", ""),
            "checker": session_data.get("checker", session_data.get("checker_type", "")),
            "checker_type": session_data.get("checker_type", session_data.get("checker", "")),
            "answer_contract": session_data.get("answer_contract", {}),
            "equivalence": session_data.get("equivalence", ""),
            "display_answer": session_data.get("display_answer", ""),
            "answer": session_data.get("answer", session_data.get("correct_answer")),
            "correct_answer": session_data.get("correct_answer", session_data.get("answer")),
            "problem_type_id": session_data.get("problem_type_id") or session_data.get("problem_type"),
            "source": session_data.get("source", route_source),
            "route_source": route_source,
            "route_mode": route_mode,
            "route_reason": route_reason,
            "wrapper_path": wrapper_path,
            "module_file": module_file,
            "wrapper_loaded": wrapper_loaded,
            "legacy_fallback_used": legacy_fallback_used,
            "legacy_fallback_reason": legacy_fallback_reason,
            "question_source": session_data.get("question_source", route_source),
            "generator_mode": session_data.get("generator_mode"),
            **_v3_runtime_contract_api_fields(session_data),
            "scenario_id": data.get("scenario_id", ""),
            "scenario_family": data.get("scenario_family", ""),
            "parameter_signature": data.get("parameter_signature", ""),
            "grading_mode": data.get("grading_mode", ""),
            "check_mode": data.get("check_mode", ""),
            "runtime_mode": data.get("runtime_mode", ""),
            "visual_backed": bool(
                data.get("visual_backed")
                or data.get("image_base64")
                or data.get("visual_aids")
            ),
            "visual_asset_type": data.get("visual_asset_type", ""),
            "variant": data.get("variant", ""),
            "expected_count": data.get("expected_count"),
            "path_labels": data.get("path_labels", []),
            "requires_listing_or_tree": data.get("requires_listing_or_tree", False),
            "requires_handwriting": bool(data.get("requires_handwriting", False)),
            "requires_teacher_review": bool(data.get("requires_teacher_review", False)),
            "n": data.get("n"),
            "expected_row": data.get("expected_row", []),
            "expected_terms": data.get("expected_terms", []),
            "expected_expansion": data.get("expected_expansion", ""),
        }, skill_id=skill_id)
        _log_get_next_question_response(response_payload)
        current_app.logger.info(
            "[PRACTICE get_next_question] response.skill_id=%s response.question_uid=%s",
            skill_id,
            response_payload.get("question_uid", ""),
        )
        return jsonify(response_payload)
    except Exception as e:
        import traceback
        current_app.logger.error(f"[RUNTIME ERROR] skill_id={skill_id} exception={str(e)}\ntraceback={traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error_code": "GENERATE_EXECUTION_FAILED",
            "skill_id": skill_id,
            "message": "題目載入失敗，請通知教師檢查此技能。"
        }), 500

@practice_bp.route('/check_answer', methods=['POST'])
def check_answer():
    """API: 瑼Ｘ蝑?"""
    body = dict(request.json) if isinstance(request.json, dict) else {}
    user_ans = body.get("answers", body.get("answer", ""))
    if isinstance(user_ans, str):
        user_ans = user_ans.strip()
        if user_ans.startswith("[") and user_ans.endswith("]"):
            try:
                import json as _json
                parsed = _json.loads(user_ans)
                if isinstance(parsed, list):
                    user_ans = parsed
            except Exception:
                pass
    req_skill = str(body.get("skill_id", "")).strip()
    req_uid = str(body.get("question_uid", "")).strip()
    session_skill = str(session.get("current_skill_id", "")).strip()
    session_uid = str(session.get("current_question_uid", "")).strip()
    current_app.logger.info(
        "[PRACTICE check_answer] request.skill_id=%s request.question_uid=%s session.skill_id=%s session.question_uid=%s",
        req_skill,
        req_uid,
        session_skill,
        session_uid,
    )
    ref = session.get('practice_ref') if isinstance(session.get('practice_ref'), dict) else {}
    if ref.get('question_uid') and not str(body.get('question_uid', '')).strip() and not str(body.get('skill_id', '')).strip():
        body.setdefault('question_uid', str(ref.get('question_uid', '')))
        body.setdefault('skill_id', str(ref.get('skill_id', '')))
        body.setdefault('question_text_hash', str(ref.get('question_text_hash', '')))
        body.setdefault('problem_type_id', str(ref.get('problem_type_id', '')))
    current, stale = resolve_check_context(body)
    if stale:
        return jsonify(stale), 409

    if not current or not str(current.get('skill', current.get('skill_id', ''))).strip():
        return jsonify({
            "correct": False,
            "result": "Session state lost. Please reload and try again.",
            "state_lost": True,
            "stale_question_requires_reload": True,
        }), 400

    skill_id = str(current.get('skill_id', current.get('skill', ''))).strip()
    question_uid = str(current.get('question_uid', body.get('question_uid', ''))).strip()
    for _image_key in ("composite_image_data_url", "student_strokes_image_data_url", "image_data_url", "image_base64", "canvas_image", "drawing_image", "handwriting_image"):
        if body.get(_image_key):
            current[_image_key] = body.get(_image_key)
    current = _normalize_gencode_runtime_payload(current, skill_id=skill_id)
    if isinstance(user_ans, dict):
        from core.gencode.table_question_contract import normalize_table_student_answer

        user_ans = normalize_table_student_answer(user_ans, current)
    if not isinstance(user_ans, (list, tuple, dict)):
        user_ans = _normalize_choice_alias_answer(user_ans, current)
    check_mode = str(
        current.get("check_mode") or current.get("grading_mode") or ""
    ).strip().lower()
    if check_mode in {
        "ai_judged_free_response",
        "visual_ai_checked",
        "handwriting_ai_checked",
        "review_mode",
    }:
        skill_specific_message = "This item is in AI/Review mode and cannot be checked by deterministic grading."
        if skill_id == "vh_?詨飛B4_StatisticalChartReading":
            skill_specific_message = (
                "This chart-reading item requires AI/Review workflow for checking."
            )
        elif skill_id == "vh_?詨飛B4_CumulativeFrequencyTablesAndGraphs":
            skill_specific_message = "This cumulative-frequency item requires AI/Review workflow for checking."
        return jsonify(
            {
                "correct": False,
                "result": skill_specific_message,
                "check_mode": check_mode,
            }
        )

    # Choice questions are graded by normalized label (A/B/C/...), not raw string.
    if _is_choice_question(current):
        choices = current.get("choices") or current.get("options") or []
        choices = choices if isinstance(choices, list) else []
        expected_answer = str(current.get("answer", "")).strip()
        user_label = _choice_value_to_label(user_ans, choices)
        correct_raw = current.get("correct_answer") or current.get("answer") or expected_answer
        correct_label = _choice_value_to_label(correct_raw, choices)
        is_correct_choice = (
            user_label is not None
            and correct_label is not None
            and user_label != ""
            and correct_label != ""
            and user_label == correct_label
        )
        correct_display = _choice_display_label_and_text(correct_raw, choices)
        if not correct_display:
            correct_display = correct_label or str(correct_raw or "").strip()
        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": is_correct_choice,
                "result": "答對了！" if is_correct_choice else f"答錯了，正確答案是 {correct_display}",
            },
        )

    # Deterministic auto-checked route (including Chap3 runtime skills with mixed review entries).
    if check_mode == "deterministic_auto_checked":
        correct_ans = str(current.get("correct_answer", current.get("answer", ""))).strip()
        is_correct_det = False
        try:
            answer_input_type = str(current.get("answer_input_type", "")).strip().lower()
            if answer_input_type == "choice":
                is_correct_det = str(user_ans).strip() == correct_ans
            elif current.get("answer_type") == "integer":
                is_correct_det = check_integer_answer(user_ans, int(correct_ans))
            else:
                if "/" in correct_ans:
                    num_str, den_str = correct_ans.split("/", 1)
                    exp_num, exp_den = int(num_str), int(den_str)
                else:
                    exp_num, exp_den = int(correct_ans), 1
                is_correct_det = check_rational_answer(
                    user_ans, exp_num, exp_den,
                    allow_decimal=True, allow_percentage=True,
                    validate_probability_range=False,
                )
        except Exception as _det_err:
            current_app.logger.warning("[DeterministicAutoChecked] check_answer error skill=%s err=%s", skill_id, _det_err)
            is_correct_det = False

        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": is_correct_det,
                "result": "答對了！" if is_correct_det else f"答錯了，正確答案是 {correct_ans}",
            },
        )
    
    # [Fix] Instant Upload Special Handling
    if skill_id == 'instant_upload':
        # Simple string comparison for instant upload
        correct_ans = str(current.get('correct_answer', '')).strip()
        user_ans_clean = user_ans.strip()
        is_correct = (user_ans_clean == correct_ans)
        
        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": is_correct,
                "result": "答對了！" if is_correct else f"答錯了，正確答案是 {correct_ans}",
            },
        )

    from core.checkers.free_response_drawing_checker import is_drawing_answer_contract
    from core.gencode.answer_payload import answer_type_family, resolve_answer_contract_for_runtime

    _drawing_ac = resolve_answer_contract_for_runtime(current, skill_id=skill_id)
    if is_drawing_answer_contract(_drawing_ac, current) or answer_type_family(str(_drawing_ac.get("answer_type", ""))) == "drawing":
        from core.gencode.answer_grading import grade_answer_for_current_question

        current_app.logger.info(
            "[PRACTICE check_answer] drawing dispatch skill_id=%s component_id=%s problem_type_id=%s checker_key=%s",
            skill_id,
            current.get("component_id", ""),
            current.get("problem_type_id", ""),
            _drawing_ac.get("checker") or _drawing_ac.get("checker_key") or current.get("checker", ""),
        )
        drawing_user_answer = {
            "image_data_url": body.get("image_data_url"),
            "composite_image_data_url": body.get("composite_image_data_url"),
            "student_strokes_image_data_url": body.get("student_strokes_image_data_url"),
            "image_base64": body.get("image_base64"),
            "canvas_image": body.get("canvas_image"),
            "drawing_image": body.get("drawing_image"),
            "handwriting_image": body.get("handwriting_image"),
        }
        contract_result = grade_answer_for_current_question(
            drawing_user_answer, current, skill_id, log=current_app.logger
        )
        if contract_result is not None:
            is_correct_value = contract_result.get("correct")
            _cr_status = str(contract_result.get("status", "")).strip()
            # Only record progress for genuine correct/incorrect verdicts.
            # parse_error and system_error must not affect mastery, fail_streak or
            # student records.
            should_record = _cr_status in ("correct", "incorrect") or (
                _cr_status == ""
                and is_correct_value is not None
                and not contract_result.get("system_error")
                and not contract_result.get("invalid_input")
            )
            if should_record:
                _record_compact_practice_progress(skill_id, bool(is_correct_value))
            return _emit_check_result(
                question_uid,
                skill_id,
                contract_result,
                record_progress=should_record,
            )

    # Phase 7B: Chap3 deterministic checker logic
    if is_b4_chapter3_phase7b_deterministic_skill(skill_id):
        correct_ans = str(current.get("correct_answer", current.get("answer", ""))).strip()
        is_correct_chap3 = False
        try:
            if current.get("answer_type") == "integer":
                is_correct_chap3 = check_integer_answer(user_ans, int(correct_ans))
            else:
                if "/" in correct_ans:
                    num_str, den_str = correct_ans.split("/", 1)
                    exp_num, exp_den = int(num_str), int(den_str)
                else:
                    exp_num, exp_den = int(correct_ans), 1
                is_correct_chap3 = check_rational_answer(
                    user_ans, exp_num, exp_den,
                    allow_decimal=True, allow_percentage=True,
                    validate_probability_range=False,
                )
        except Exception as _err:
            current_app.logger.warning("[Chap3 Phase7B] check_answer error skill=%s err=%s", skill_id, _err)
            is_correct_chap3 = False
            
        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": is_correct_chap3,
                "result": "答對了！" if is_correct_chap3 else f"答錯了，正確答案是 {correct_ans}",
            },
        )

    # Phase 6C-1R2: deterministic Chap2 BEFORE legacy skills.<id> import (get_skill loads module).
    if is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
        correct_ans = str(current.get("correct_answer", current.get("answer", ""))).strip()
        is_correct_chap2 = False
        chap2_checker_name = "check_rational_answer"
        try:
            if current.get("answer_type") == "integer":
                chap2_checker_name = "check_integer_answer"
                is_correct_chap2 = check_integer_answer(user_ans, int(correct_ans))
            elif current.get("answer_type") == "expected_value":
                chap2_checker_name = "check_expected_value_answer"
                is_correct_chap2 = check_expected_value_answer(user_ans, correct_ans)
            else:
                chap2_checker_name = "check_rational_answer"
                if "/" in correct_ans:
                    num_str, den_str = correct_ans.split("/", 1)
                    exp_num, exp_den = int(num_str), int(den_str)
                elif correct_ans in ("0", "1"):
                    exp_num, exp_den = int(correct_ans), 1
                else:
                    exp_num, exp_den = int(correct_ans), 1
                is_correct_chap2 = check_rational_answer(
                    user_ans, exp_num, exp_den,
                    allow_decimal=True, allow_percentage=True,
                    validate_probability_range=True,
                )
        except Exception as _chap2_check_err:
            current_app.logger.warning(
                "[Chap2 Phase6C1R2] check_answer error skill=%s err=%s",
                skill_id,
                _chap2_check_err,
            )
            is_correct_chap2 = False
            chap2_checker_name = "checker_exception"

        try:
            persist_b4_chap2_deterministic_answer_event(
                skill_id=skill_id,
                current_question=current,
                user_answer=user_ans,
                is_correct=is_correct_chap2,
                checker_name=chap2_checker_name,
            )
        except Exception:
            pass

        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": is_correct_chap2,
                "result": "答對了！" if is_correct_chap2 else f"答錯了，正確答案是 {correct_ans}",
            },
        )

    # ?寞???嚗?敶ａ?
    if current.get('correct_answer') == "graph":
        return _emit_check_result(
            question_uid,
            skill_id,
            {
                "correct": False,
                "result": "Graph answers require AI-based checking.",
                "next_question": False,
            },
            record_progress=False,
        )

    from core.gencode.answer_grading import grade_answer_for_current_question

    contract_result = grade_answer_for_current_question(
        user_ans, current, skill_id, log=current_app.logger
    )
    if contract_result is not None:
        result = contract_result
        is_correct = bool(result.get("correct", False))
        _res_status = str(result.get("status", "")).strip()
        # Only record progress for genuine correct/incorrect verdicts.
        # parse_error and system_error must not affect mastery, fail_streak or
        # student records.
        should_record = _res_status in ("correct", "incorrect") or (
            _res_status == ""
            and not result.get("system_error")
            and not result.get("invalid_input")
        )
        _log_runtime_check_session(
            skill_id,
            user_ans,
            current,
            selected_checker=str(current.get("checker", current.get("checker_type", ""))),
            checker_result=is_correct,
            feedback_display=str(result.get("result", "")),
        )
        if should_record:
            _record_compact_practice_progress(skill_id, is_correct)
        return _emit_check_result(
            question_uid,
            skill_id,
            result,
            record_progress=should_record,
        )

    mod = get_skill(skill_id)

    if not mod:
        return _emit_check_result(
            question_uid,
            skill_id,
            {"correct": False, "result": "模組載入錯誤"},
            record_progress=False,
        )

    from core.gencode.answer_grading import normalize_grading_result, validate_answer_input

    # --- [Legacy Guard] Pre-flight: classify user_ans before calling mod.check() ---
    # Structurally invalid input → parse_error (not a student mistake)
    _legacy_parse_fail = validate_answer_input(user_ans)
    if _legacy_parse_fail is not None:
        current_app.logger.info(
            "[PRACTICE legacy check] parse_error skill_id=%s error_code=%s",
            skill_id,
            _legacy_parse_fail.get("error_code"),
        )
        return _emit_check_result(
            question_uid, skill_id, _legacy_parse_fail, record_progress=False
        )

    correct_for_check = current.get("correct_answer", current.get("answer"))
    grading_payload = {
        "skill_id": skill_id,
        "problem_type_id": current.get("problem_type_id", ""),
        "answer_contract": current.get("answer_contract"),
        "checker": current.get("checker", current.get("checker_type", "")),
        "equivalence": current.get("equivalence", current.get("equivalence_type", "")),
        "answer_type": current.get("answer_type", ""),
    }

    # --- [Legacy Guard] Invoke mod.check() and catch ALL exceptions → system_error ---
    _legacy_checker_exc: Exception | None = None
    try:
        try:
            result = mod.check(user_ans, correct_for_check, question_payload=grading_payload)
        except TypeError:
            result = mod.check(user_ans, correct_for_check)
    except Exception as _exc:
        _legacy_checker_exc = _exc
        current_app.logger.error(
            "[PRACTICE legacy check] checker exception skill_id=%s err=%s",
            skill_id,
            _exc,
            exc_info=True,
        )
        result = normalize_grading_result({
            "correct": False,
            "system_error": True,
            "error_code": "CHECKER_EXECUTION_FAILED",
            "result": f"批改系統錯誤：{_exc}",
        })

    # [V10.1 Repair] bool → dict
    if isinstance(result, bool):
        result = {
            "correct": result,
            "result": "Correct!" if result else "Incorrect.",
        }

    # Normalize to ensure 'status' is always present
    if isinstance(result, dict) and "status" not in result:
        result = normalize_grading_result(result)

    # --- [Legacy Guard] Single gradability gate for all downstream persistence ---
    # Only status="correct" / "incorrect" (or legacy results without error flags)
    # may write to student records.  parse_error and system_error are silently
    # returned to the caller without touching any persistence layer.
    _legacy_status = str(result.get("status", "")).strip() if isinstance(result, dict) else ""
    _legacy_gradable = _legacy_status in ("correct", "incorrect") or (
        _legacy_status == ""
        and not result.get("system_error")
        and not result.get("invalid_input")
    )

    if not _legacy_gradable:
        current_app.logger.info(
            "[PRACTICE legacy check] non-gradable result – skipping all persistence "
            "skill_id=%s status=%s error_code=%s",
            skill_id,
            result.get("status"),
            result.get("error_code"),
        )
        return _emit_check_result(question_uid, skill_id, result, record_progress=False)

    is_correct = bool(result.get("correct", False))

    # --- [Phase 8] Update compact review hints and stats ---
    _record_compact_practice_progress(skill_id, is_correct)

    # --- [Phase 2 & 5] ?芷?飛蝧芋撘??---
    is_adaptive_mode = request.json.get('mode') == 'adaptive'
    if is_adaptive_mode:
        try:
            question_id = request.json.get('question_id')
            time_taken = request.json.get('time_taken', 60.0) # ?身 60 蝘?
            
            if question_id:
                # 銝?撠嚗??湔?賢?嚗?撠???嚗??臬甇日?畾萎?霈?
                update_student_ability(
                    user_id=current_user.id,
                    skill_id=skill_id,
                    question_id=question_id,
                    is_correct=is_correct,
                    time_taken_seconds=float(time_taken)
                )

                # 憒?蝑嚗??隤文????脩蔑嚗???拇?璅∪?嚗?
                if not is_correct:
                    question_text = current.get('question_text', '')
                    correct_answer = current.get('correct_answer', '')
                    
                    # ?園??蔭?桀?鞈?
                    from models import SkillInfo
                    skill_info = db.session.get(SkillInfo, skill_id)
                    prerequisite_units = []
                    if skill_info and skill_info.prerequisites:
                        prerequisite_units = [
                            {"id": prereq.skill_id, "name": prereq.skill_ch_name}
                            for prereq in skill_info.prerequisites
                        ]
                    
                    # ?園?撠店甇瑕嚗????店嚗?
                    conversation_history = session.get('conversation_history', [])
                    
                    # ?澆憓撥??AI 閮箸
                    error_diagnosis = diagnose_error(
                        question_text, 
                        correct_answer, 
                        user_ans,
                        prerequisite_units=prerequisite_units,
                        conversation_history=conversation_history
                    )
                    
                    error_type = error_diagnosis.get("error_type", "unknown")
                    
                    # ??脩蔑嚗??芷?芋撘?
                    if error_type != "unknown":
                        apply_error_penalty(
                            user_id=current_user.id,
                            skill_id=skill_id,
                            question_id=question_id,
                            error_type=error_type
                        )
                    
                    # [Phase 6] 憒?????蔭?桀??刻嚗??亙??葉
                    if error_diagnosis.get("related_prerequisite_id"):
                        prereq_id = error_diagnosis["related_prerequisite_id"]
                        prereq_skill = db.session.get(SkillInfo, prereq_id)
                        if prereq_skill:
                            result["suggested_prerequisite"] = {
                                "id": prereq_id,
                                "name": prereq_skill.skill_ch_name,
                                "reason": error_diagnosis.get("prerequisite_explanation", "請先補強前置概念。")
                            }

        except Exception as e:
            current_app.logger.error(f"?芷?????仃?? {e}")
    
    # [Phase 6] ?桅芋撘??航炊閮箸??蝵桀???
    if not is_adaptive_mode and not is_correct:
        try:
            question_text = current.get('question_text', '')
            correct_answer = current.get('correct_answer', '')
            
            current_app.logger.info(f"[?蔭?桀??刻] ??閮箸 - ??? {skill_id}")
            
            # ?園??蔭?桀?鞈?
            from models import SkillInfo
            skill_info = db.session.get(SkillInfo, skill_id)
            prerequisite_units = []
            if skill_info and skill_info.prerequisites:
                prerequisite_units = [
                    {"id": prereq.skill_id, "name": prereq.skill_ch_name}
                    for prereq in skill_info.prerequisites
                ]
            
            current_app.logger.info(f"[Prerequisite Suggestion] found {len(prerequisite_units)} units")
            
            # ?芣??嗆??蔭?桀????脰?閮箸嚗???API ?嚗?
            if prerequisite_units:
                # ?園?撠店甇瑕
                conversation_history = session.get('conversation_history', [])
                
                current_app.logger.info(f"[?蔭?桀??刻] ?澆 AI 閮箸...")
                
                # ?澆 AI 閮箸
                error_diagnosis = diagnose_error(
                    question_text, 
                    correct_answer, 
                    user_ans,
                    prerequisite_units=prerequisite_units,
                    conversation_history=conversation_history
                )
                
                current_app.logger.info(f"[?蔭?桀??刻] AI 閮箸蝯?: {error_diagnosis}")
                
                # 憒?????蔭?桀??刻嚗??亙??葉
                if error_diagnosis.get("related_prerequisite_id"):
                    prereq_id = error_diagnosis["related_prerequisite_id"]
                    prereq_skill = db.session.get(SkillInfo, prereq_id)
                    if prereq_skill:
                        result["suggested_prerequisite"] = {
                            "id": prereq_id,
                            "name": prereq_skill.skill_ch_name,
                            "reason": error_diagnosis.get("prerequisite_explanation", "請先補強前置概念。")
                        }
                        current_app.logger.info(f"[?蔭?桀??刻] ?刻?桀?: {prereq_skill.skill_ch_name}")
                    else:
                        current_app.logger.warning(f"[?蔭?桀??刻] ?曆??啣?蝵桀?? {prereq_id}")
                else:
                    current_app.logger.info("[Prerequisite Suggestion] AI did not return a prerequisite.")
            else:
                current_app.logger.info("[Prerequisite Suggestion] no prerequisite units available.")
        except Exception as e:
            current_app.logger.error(f"?蔭?桀??刻憭望?: {e}")
            import traceback
            traceback.print_exc()
    
    # [IRT] ???湔撠??亥???敺桃?暺?釭
    try:
        difficulty = current.get('current_level', 1)
        q_text = current.get('question_text', '')
        update_node_competencies(current_user.id, skill_id, q_text, is_correct, difficulty)
    except Exception as e:
        current_app.logger.error(f"IRT ?湔蝭暺?仃?? {e}")

    # ?亦??荔??芸?閮??圈憿
    if not is_correct:
        try:
            q_text = current.get('question_text')
            existing_entry = db.session.query(MistakeNotebookEntry).filter_by(
                student_id=current_user.id,
                skill_id=skill_id
            ).filter(MistakeNotebookEntry.question_data.contains(q_text)).first()

            if not existing_entry and q_text:
                new_entry = MistakeNotebookEntry(
                    student_id=current_user.id,
                    skill_id=skill_id,
                    question_data={'type': 'system_question', 'text': q_text},
                    notes='蝟餌絞蝺渡?憿????'
                )
                db.session.add(new_entry)
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"?芸?閮??舫?憭望?: {e}")
            db.session.rollback()

    return _emit_check_result(question_uid, skill_id, result)


@practice_bp.route('/debug/clear_practice_state', methods=['POST', 'GET'])
def debug_clear_practice_state():
    """Development-only: reset practice pointers and server-side question store."""
    if not current_app.debug and not current_app.config.get("TESTING"):
        return jsonify({"error": "not_available"}), 404
    clear_practice_state()
    return jsonify({"ok": True, "message": "practice state cleared"})


@practice_bp.route('/draw_diagram', methods=['POST'])
def draw_diagram():
    """Draw a diagram with AI and return image data."""
    try:
        import google.generativeai as genai
        data = request.get_json()
        question_text = data.get('question_text')

        if not question_text:
            return jsonify({"success": False, "message": "Missing question_text."}), 400

        # 1. ?澆 Gemini ???寧?撘?
        api_key = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(current_app.config.get('GEMINI_MODEL_NAME', 'gemini-1.5-flash'))
        
        prompt = (
            "Extract a 2D equation from this math question. "
            "Return only a Python-friendly equation string, or 'No equation found'.\n"
            f"Question: {question_text}"
        )
        
        response = model.generate_content(prompt)
        equations_text = response.text.strip()

        if "No equation found" in equations_text or not equations_text:
            return jsonify({"success": False, "message": "AI could not extract an equation."}), 400

        # 2. ??蝜芸? (Thread-Safe Pattern)
        # ?嚗?蝣箏遣蝡?figure ?拐辣嚗?雿輻?典? plt
        fig = plt.figure(figsize=(6, 6))
        
        x = np.linspace(-10, 10, 400)
        y = np.linspace(-10, 10, 400)
        x, y = np.meshgrid(x, y)

        eval_context = {
            'np': np, 'x': x, 'y': y,
            'a': 2, 'b': 3, 'c': 4 # ?身??踹??梢
        }

        has_plot = False
        for line in equations_text.splitlines():
            line = line.strip()
            if not line: continue
            
            # 蝪⊥?皜?
            line = line.strip('$').replace('sqrt', 'np.sqrt').replace('^', '**')
            
            try:
                # 蝑???
                if '=' in line and '==' not in line and '>' not in line and '<' not in line:
                    parts = line.split('=')
                    expr = f"({parts[0].strip()}) - ({parts[1].strip()})"
                    plt.contour(x, y, eval(expr, eval_context), levels=[0], colors='b')
                    has_plot = True
                # 銝?撘???
                elif '>' in line or '<' in line:
                    plt.contourf(x, y, eval(line, eval_context), levels=[0, np.inf], colors=['#3498db'], alpha=0.3)
                    has_plot = True
            except Exception as e:
                continue
        
        if not has_plot:
            plt.close(fig) # ?鞈?
            return jsonify({"success": False, "message": "No valid equation could be plotted."}), 400

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.gca().set_aspect('equal')

        # 3. ?脣???
        static_dir = os.path.join(current_app.static_folder)
        if not os.path.exists(static_dir): os.makedirs(static_dir)
            
        unique_filename = f"diagram_{uuid.uuid4().hex}.svg"
        image_path = os.path.join(static_dir, unique_filename)
        
        plt.savefig(image_path, format='svg')
        plt.close(fig) # [CRITICAL] ???? figure 隞仿??曇??園?

        return jsonify({
            "success": True,
            "image_path": url_for('static', filename=unique_filename)
        })

    except Exception as e:
        plt.close('all') # ?潛??航炊??靽璈
        current_app.logger.error(f"蝜芸??航炊: {e}")
        return jsonify({"success": False, "message": f"隡箸??券隤? {e}"}), 500

# ==========================================
# [?箸?鋆?] Advanced Practice Features (?脤?蝺渡??)
# ==========================================

@practice_bp.route('/similar-questions-page')
@login_required
def similar_questions_page():
    return render_template('similar_questions.html')

@practice_bp.route('/generate-similar-questions', methods=['POST'])
@login_required
def generate_similar_questions():
    data = request.get_json()
    problem_text = data.get('problem_text')
    if not problem_text: return jsonify({"error": "Missing problem_text"}), 400

    from core.ai_analyzer import identify_skills_from_problem
    skill_ids = identify_skills_from_problem(problem_text)

    if not skill_ids:
        return jsonify({"questions": [], "message": "AI could not identify target skills."})

    generated_questions = []
    for skill_id in skill_ids:
        try:
            mod = importlib.import_module(f"skills.{skill_id}")
            from core.legacy_generator_adapter import invoke_skill_generate, normalize_runtime_value
            new_question = invoke_skill_generate(mod, level=1, skill_id=skill_id)
            new_question = normalize_runtime_value(new_question)
            skill_info = get_skill_info(skill_id)
            new_question['skill_id'] = skill_id
            new_question['skill_ch_name'] = skill_info.skill_ch_name if skill_info else "?芰"
            generated_questions.append(new_question)
        except: pass

    return jsonify({"questions": generated_questions})

@practice_bp.route('/image-quiz-generator')
@login_required
def image_quiz_generator():
    return render_template('image_quiz_generator.html')

@practice_bp.route('/generate-quiz-from-image', methods=['POST'])
@login_required
def generate_quiz_from_image():
    if 'image_file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['image_file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    try:
        from core.ai_analyzer import generate_quiz_from_image as ai_gen_quiz
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        description = request.form.get('description', '')
        questions = ai_gen_quiz(filepath, description)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@practice_bp.route('/get_suggested_prompts/<skill_id>')
@login_required
def get_suggested_prompts(skill_id):
    """????賜?撱箄降?? (Suggested Prompts)"""
    skill_info = db.session.get(SkillInfo, skill_id)
    prompts = []
    if skill_info:
        prompts = [p for p in [skill_info.suggested_prompt_1, skill_info.suggested_prompt_2, skill_info.suggested_prompt_3] if p]
    return jsonify(prompts)


@practice_bp.route('/practice/upload_instant', methods=['POST'])
@login_required # Login required for now, or could be open?
def upload_instant():
    """
    Handle instant image upload for immediate practice (Short Loop).
    Stores result in session, does NOT save to DB.
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    try:
        from core.ai_analyzer import analyze_question_image
        
        # 1. Save temp file (optional, or pass stream directly if supported)
        # static/temp_uploads structure
        upload_dir = os.path.join(current_app.static_folder, 'temp_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = secure_filename(f"instant_{uuid.uuid4().hex}.png") # Force png or keep extension
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 2. Analyze with AI
        # Re-open file to read for AI
        with open(filepath, 'rb') as f_img:
             # Mock a FileStorage object structure or adjust analyze_question_image to take path/bytes
             # actually analyze_question_image takes a FileStorage object usually.
             # Let's adjust usage to pass the file object or just re-create a mock
             from werkzeug.datastructures import FileStorage
             f_mock = FileStorage(stream=f_img, filename=filename)
             result = analyze_question_image(f_mock)
             
        if "error" in result:
             return jsonify({'success': False, 'message': result['error']}), 500
             
        # 3. Store in Session
        session_data = {
            'skill': 'instant_upload',
            'question_text': result.get('question_text', ''),
            'correct_answer': result.get('correct_answer', ''),
            'predicted_topic': result.get('predicted_topic', 'Unclassified'),
            'image_base64': result.get('image_base64', ''), # If AI returns b64, or constructed below
            'image_path': url_for('static', filename=f'temp_uploads/{filename}'), # Use path for display
            'is_instant_upload': True
        }
        
        # If AI didn't return base64 (likely), we use the path url for frontend display
        # But for 'image_base64' field in next_question response, we might want it? 
        # Actually frontend can handle URL. Let's use image_path mainly.
        
        # CRITICAL: set_current for session management
        set_current('instant_upload', session_data)
        
        return jsonify({'success': True, 'redirect_url': url_for('practice.practice', skill_id='instant_upload')})

    except Exception as e:
        current_app.logger.error(f"Instant upload failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
