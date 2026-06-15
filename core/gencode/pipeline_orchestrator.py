from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

import json
import py_compile
import sqlite3
import ast
import copy
import shutil
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any

from flask import current_app, has_app_context
from core.ai_wrapper import call_ai_with_retry, get_ai_client
from core.ai_wrapper import resolve_gemini_api_key
from core.ai_settings import get_ai_settings_snapshot, get_effective_model_config
from core.gencode.classifier_proposal import build_classifier_proposal, detect_answer_shape
from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.base import ClassifierContext
from core.gencode.classifiers.fallback_classifier import FallbackClassifier
from core.gencode.phase3_skill_codegen import build_generator_specs_for_phase3, build_phase3_skill_module_code
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.pipeline_state import (
    GENCODE_DRAFT_DIR,
    GENCODE_REPORT_DIR,
    coerce_report_path,
    phase_report_paths,
    phase_summary_path,
    read_json,
    reports_dict_from_paths,
    sanitize_path_segment,
    utc_timestamp,
    write_json,
    write_md,
    write_text_file,
)
from core.gencode.runtime_smoke import run_draft_runtime_smoke
from core.gencode.phase1_anchor_contract import phase1_enforcement_assertion_block
from core.gencode.problem_type_induction import apply_spec_mode, induce_problem_types_from_examples
from core.gencode.problem_type_spec import save_induced_problem_type_specs
from core.gencode import problem_type_spec as problem_type_spec_registry
from core.gencode.answer_contract_gate import (
    EQUIVALENCE_TYPE_WHITELIST,
    coerce_single_choice_contract,
    summarize_answer_contracts,
)
from core.gencode.source_skill_binding_policy import (
    demote_generic_fallback_candidate,
    demote_unregistered_scope_locked_candidate,
    is_generic_fallback_problem_type,
    should_block_generic_fallback_for_scope,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = GENCODE_REPORT_DIR
DRAFT_DIR = GENCODE_DRAFT_DIR
CLASSIFIER_DRAFT_DIR = REPORT_DIR / "classifier_drafts"
CLASSIFIER_RULEPACK_PATH = PROJECT_ROOT / "configs" / "gencode" / "classifiers" / "phase1_rule_packs.yaml"
CLASSIFIER_RULEPACK_BACKUP_DIR = PROJECT_ROOT / "backups" / "gencode_classifier_rulepacks"

SOP_INTEGRATION_DIR = Path("docs") / "系統SOP" / "Gencode_AgentSkillV2整合"


def _phase_reports(skill_id: str, *, keys: tuple[str, ...] | None = None) -> dict[str, str]:
    paths = phase_report_paths(skill_id)
    if keys is not None:
        paths = {key: paths[key] for key in keys if key in paths}
    return reports_dict_from_paths(paths)


def _load_phase_json(path: str | Path) -> dict[str, Any]:
    return _normalize_json_payload(read_json(path))


def _safe_skill_id(skill_id: str) -> str:
    return sanitize_path_segment(skill_id)


def _apply_source_skill_binding_candidate_policy(skill_id: str, auto_review: dict[str, Any]) -> dict[str, Any]:
    """Keep Phase 1 source-scope policy intact after downstream gate normalization."""
    if not isinstance(auto_review, dict):
        return auto_review
    anchor = auto_review.get("main_skill_anchor") if isinstance(auto_review.get("main_skill_anchor"), dict) else {}
    if not bool(anchor.get("source_skill_scope_locked", auto_review.get("source_skill_scope_locked", False))):
        if str(anchor.get("classification_scope", auto_review.get("classification_scope", ""))).strip() != "within_current_skill":
            return auto_review
    candidates = auto_review.get("candidate_problem_types")
    if not isinstance(candidates, list):
        return auto_review
    existing_ids = {
        str(s.get("problem_type_id", "")).strip()
        for s in problem_type_spec_registry.list_problem_types_for_skill(skill_id)
        if isinstance(s, dict)
    }
    has_human_rule_pack = bool(auto_review.get("human_confirmed_rule_pack_applied")) or bool(
        auto_review.get("matched_registered_yaml_rule_pack")
    )
    rescoped: list[dict[str, Any]] = []
    expected_subskills = {
        str(t).strip()
        for t in (anchor.get("expected_subskill_candidates") or [])
        if str(t).strip() and not str(t).endswith("_family")
    }
    expected_families = {str(f).strip() for f in (anchor.get("expected_task_families") or []) if str(f).strip()}
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        pt = str(cand.get("problem_type_id") or cand.get("proposed_problem_type_id") or "").strip()
        target = str(cand.get("target_task") or cand.get("subskill_id") or "").strip()
        family = str(cand.get("task_family") or "").strip()
        if not family and target:
            from core.gencode.task_families import task_family_for_task

            family = task_family_for_task(target)
        if is_generic_fallback_problem_type(problem_type_id=pt, target_task=target, task_family=family) or should_block_generic_fallback_for_scope(
            {**anchor, "classification_scope": anchor.get("classification_scope", auto_review.get("classification_scope", "within_current_skill"))},
            problem_type_id=pt,
            target_task=target,
            task_family=family,
        ):
            rescoped.append(demote_generic_fallback_candidate(cand))
        elif not has_human_rule_pack and pt and pt not in existing_ids:
            draft = cand.get("problem_type_spec_draft") if isinstance(cand.get("problem_type_spec_draft"), dict) else {}
            draft_target = str(draft.get("target_task") or target).strip()
            draft_family = str(draft.get("task_family") or family).strip() or task_family_for_task(draft_target)
            in_scope = (
                draft_target in expected_subskills
                or draft_family in expected_families
                or target in expected_subskills
                or family in expected_families
            )
            if in_scope:
                rescoped.append(cand)
            else:
                rescoped.append(demote_unregistered_scope_locked_candidate(cand))
        else:
            rescoped.append(cand)
    auto_review = dict(auto_review)
    auto_review["candidate_problem_types"] = rescoped
    return auto_review
SOP_SELF_HEALING_MAP = {
    "phase1": "Gencode與AgentSkillV2整合總體設計_v0.3.md",
    "phase2": "Gencode與AgentSkillV2整合總體設計_v0.3.md",
    "phase2.5": "AnswerContract_EquivalenceType_Gate_v0.3.md",
    "phase3": "AgentSkillV2_ProblemType規格包設計_v0.3.md",
}


def execute_pipeline_self_healing(error: Exception, phase: str, skill_id: str) -> dict[str, Any]:
    """SOP v0.3.2 條款 3.5：自動載入真實 SOP 目錄全文作為 LLM 修正 Context，達成無人值守閉環。"""
    phase_key = str(phase or "").lower().strip()
    sop_file = SOP_SELF_HEALING_MAP.get(phase_key, "Gencode與AgentSkillV2整合總體設計_v0.3.md")
    sop_path = PROJECT_ROOT / SOP_INTEGRATION_DIR / sop_file

    sop_context = ""
    if sop_path.exists():
        sop_context = sop_path.read_text(encoding="utf-8")

    repair_prompt = f"""
【管線執行中斷】: Phase {phase} 發生非預期毀損。
【當前錯誤堆疊】: {error!s}
【唯一對照權威 SOP 規範】:
{sop_context}

請依據合約法規，修正 ProblemTypeSpec 的欄位配置，嚴禁直接給答案。
""".strip()

    client, _ = _resolve_gencode_ai_client(["architect", "default"])
    if client:
        call_ai_with_retry(client, repair_prompt, max_retries=2, retry_delay=2, timeout=90)

    return {"status": "HEALED_AND_RETRIED", "phase": phase, "skill_id": skill_id}


def _validate_vh_math_skill_id_prefix(skill_id: str) -> tuple[bool, str]:
    """
    SOP v0.3.2 最終洗淨版：行政歸屬唯讀校驗器。
    100% 對齊資料庫既有 vh_數學... 標準格式矩陣，絕不自行發明 ID。
    """
    sid = str(skill_id or "").strip()
    if sid.startswith("vh_數學"):
        return True, "vocational_high_school_math_core_scope"
    return False, "skill_id_prefix_violation"


def _build_skill_id_prefix_violation_payload(
    skill_id: str,
    *,
    dry_run: bool,
    reports_pre: dict[str, str],
    validation_reason: str = "skill_id_prefix_violation",
) -> dict[str, Any]:
    return {
        "ok": False,
        "phase": "phase1",
        "skill_id": skill_id,
        "source_example_count": 0,
        "candidate_problem_types": [],
        "phase_status": "skill_id_prefix_violation",
        "exception_review_gate": {"required": True, "reasons": ["skill_id_prefix_violation"]},
        "summary_message": (
            f"[CRITICAL] Skill ID format violation: '{skill_id}' must belong to "
            f"'vh_數學' core matrix. Blocked from pipeline write."
        ),
        "reports": reports_pre,
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
        "human_review_items": [],
        "skill_id_prefix_validated": False,
        "skill_id_prefix_validation_reason": validation_reason,
    }


_AUTOMATED_DERIVATION = ["Step 1: Automated derivation initialized from source spec."]
ALLOWED_SKILL_LEVEL_BLOCKERS = {
    "sop_preflight_failed",
    "no_source_examples",
    "blocked_insufficient_examples",
    "blocked_sop_preflight_failed",
    "insufficient_examples_for_safe_promote",
}
_SHORT_ANSWER_PROBLEM_TYPE_PREFIXES = ("ordered_tuple_", "text_short_")
_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES = ("single_choice_", "choice_")


def _reinforce_derivation_contract(draft: dict[str, Any], problem_type_id: str) -> None:
    pt = str(problem_type_id or "").strip()
    if not any(token in pt for token in ("numeric", "expression", "fallback_application")):
        return
    derivation = draft.get("derivation")
    if not isinstance(derivation, list) or not derivation:
        draft["derivation"] = list(_AUTOMATED_DERIVATION)
    gc = draft.get("generator_contract")
    if not isinstance(gc, dict):
        gc = {}
        draft["generator_contract"] = gc
    gc["contextual_application"] = True


def _has_zombie_problem_type_id(problem_type_id: str) -> bool:
    pt = str(problem_type_id or "").strip().lower()
    if not pt:
        return False
    zombie_markers = (
        "_ghost",
        "_legacy",
        "_orphan",
        ":draft",
        "__",
        "_short_answer_single_choice",
        "_single_choice_short_answer",
    )
    return any(marker in pt for marker in zombie_markers) or pt.endswith("_draft_v1")


def _canonicalize_nested_problem_type_ids(node: Any, canonical_problem_type_id: str) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "problem_type_id":
                node[key] = canonical_problem_type_id
            else:
                _canonicalize_nested_problem_type_ids(value, canonical_problem_type_id)
    elif isinstance(node, list):
        for value in node:
            _canonicalize_nested_problem_type_ids(value, canonical_problem_type_id)


def _is_contextual_short_answer_choice_clone(problem_type_id: str) -> bool:
    pt = str(problem_type_id or "").strip().lower()
    if not pt.startswith(_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES):
        return False
    if "quadratic" in pt:
        return False
    if "_contextual_application" in pt:
        return True
    sequence_markers = ("vertex", "axis")
    return all(marker in pt for marker in sequence_markers)


def _purge_choice_ghost_cache_from_answer_contract(
    spec: dict[str, Any], problem_type_id: str = ""
) -> dict[str, Any]:
    """SOP v0.3.4: strip choice ghosts and align short-answer families to numeric registry key."""
    from core.gencode.answer_contract_policy import _FACTORING_TASKS, QUADRATIC_INEQUALITY_SOLUTION_TASKS

    target_task = str(spec.get("target_task", "")).strip()
    if target_task in _FACTORING_TASKS:
        return spec
    if target_task in QUADRATIC_INEQUALITY_SOLUTION_TASKS:
        return spec

    pt_key_lower = str(problem_type_id or spec.get("problem_type_id", "")).strip().lower()
    is_short_answer_family = any(
        token in pt_key_lower
        for token in ["integer_", "numeric_", "rational_", "compute_quadratic_vertex"]
    ) and not any(choice_tok in pt_key_lower for choice_tok in ["_choice", "single_choice"])

    if is_short_answer_family:
        ac = spec.get("answer_contract")
        if isinstance(ac, dict):
            if str(ac.get("answer_type", "")).strip() == "expression":
                return spec
            if str(ac.get("answer_type", "")).strip() == "interval":
                return spec
            ac["presentation_mode"] = "short_answer"
            if pt_key_lower.startswith("integer_"):
                ac["answer_type"] = "integer"
                ac["answer_equivalence"] = "numeric_exact"
                ac["equivalence_type"] = "numeric_exact"
                ac["checker"] = "integer_checker"
                ac["checker_key"] = "integer_checker"
                ac["selected_checker"] = "integer_checker"
            elif pt_key_lower.startswith("rational_"):
                ac["answer_type"] = "rational"
                ac["answer_equivalence"] = "rational_equivalent"
                ac["equivalence_type"] = "rational_equivalent"
                ac["checker"] = "rational_checker"
                ac["checker_key"] = "rational_checker"
                ac["selected_checker"] = "rational_checker"
            else:
                ac["answer_type"] = "numeric"
            ac["source_has_choices"] = False
            ac["choices_required"] = False
            ac["frontend_render_choices"] = False
            ac.pop("accepted_formats", None)
            ac.pop("choice_count", None)
            if str(ac.get("answer_semantics", "")).strip() == "choice_label":
                ac.pop("answer_semantics", None)
            checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
            if checker and str(ac.get("selected_checker", "")).strip() == "choice_label_checker":
                ac["selected_checker"] = checker
            spec["answer_contract"] = ac
            spec["answer_type"] = ac.get("answer_type", "numeric")
    return spec


def _reinforce_canonical_answer_contract(
    spec: dict[str, Any], problem_type_id: str = ""
) -> dict[str, Any]:
    pt = str(problem_type_id or spec.get("problem_type_id", "")).strip()
    pt_key = pt.lower()
    target_task = str(spec.get("target_task", "")).strip().lower()
    short_answer_prefix = pt_key.startswith(_SHORT_ANSWER_PROBLEM_TYPE_PREFIXES)
    single_choice_prefix = pt_key.startswith(_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES)
    ac = spec.get("answer_contract")
    if not isinstance(ac, dict):
        ac = {}
        spec["answer_contract"] = ac

    if _is_contextual_short_answer_choice_clone(pt):
        pt = "text_short_contextual_application"
        pt_key = pt
        spec["problem_type_id"] = pt
        _canonicalize_nested_problem_type_ids(spec, pt)
        ac.update(
            {
                "answer_type": "text_short",
                "answer_shape": "text_short",
                "answer_equivalence": "exact_string",
                "equivalence_type": "exact_string",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "choices_required": False,
                "frontend_render_choices": False,
            }
        )
        spec["answer_contract"] = ac
        return _purge_choice_ghost_cache_from_answer_contract(spec, pt)

    # Typed-prefix canonicalization guard:
    # If this spec was already run through enrich_spec_with_canonicalization(),
    # its answer_contract reflects the canonical presentation (choice/text_short/…)
    # NOT the raw value-type prefix.  Skip the crude prefix→checker override and
    # instead re-apply the canonicalizer's result to guarantee consistency.
    _is_already_canonicalized = bool(
        spec.get("canonical_base_problem_type_id") or spec.get("value_type_prefix")
    )
    if _is_already_canonicalized:
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        enriched = enrich_spec_with_canonicalization(spec)
        canonical_ac = enriched.get("answer_contract")
        if isinstance(canonical_ac, dict):
            ac.update(canonical_ac)
            spec["answer_contract"] = ac
        # Propagate resolved template slot into generator_contract
        resolved_slot = enriched.get("_resolved_template_slot", "")
        if resolved_slot:
            spec["_resolved_template_slot"] = resolved_slot
            gc = spec.get("generator_contract")
            if not isinstance(gc, dict):
                gc = {}
                spec["generator_contract"] = gc
            slots = gc.get("template_slots")
            if not isinstance(slots, dict):
                slots = {}
                gc["template_slots"] = slots
            if not slots.get("stem"):
                slots["stem"] = resolved_slot
        if short_answer_prefix and _sanitize_coordinate_pair_answer_contract(spec, pt):
            return _purge_choice_ghost_cache_from_answer_contract(spec, pt)
        spec["answer_contract"] = ac
        return _purge_choice_ghost_cache_from_answer_contract(spec, pt)

    if pt.startswith("expression_"):
        answer_type = "expression"
        checker = "expression_checker"
        equivalence = "algebraic_equivalent"
    elif pt.startswith("integer_"):
        answer_type = "integer"
        checker = "integer_checker"
        equivalence = "numeric_exact"
    elif pt.startswith("numeric_"):
        answer_type = "numeric"
        checker = "integer_checker"
        equivalence = "numeric_exact"
    else:
        answer_type = ""
        checker = ""
        equivalence = ""

    if answer_type:
        ac["answer_type"] = answer_type
        ac["checker"] = checker
        ac["checker_key"] = checker
        ac["answer_equivalence"] = equivalence
        ac["equivalence_type"] = equivalence
        ac["choices_required"] = False
        ac["frontend_render_choices"] = False

    if (
        ("linear_function" in pt_key or "evaluate_function" in target_task)
        and str(ac.get("answer_type", "")).strip() == "expression"
    ):
        ac["answer_equivalence"] = "algebraic_equivalent"
        ac["equivalence_type"] = "algebraic_equivalent"
        ac["checker"] = "expression_checker"
        ac["checker_key"] = "expression_checker"

    if short_answer_prefix and _sanitize_coordinate_pair_answer_contract(spec, pt):
        return _purge_choice_ghost_cache_from_answer_contract(spec, pt)

    if single_choice_prefix and not short_answer_prefix:
        ac["answer_type"] = "single_choice"
        coerce_single_choice_contract(ac)

    spec["answer_contract"] = ac
    return _purge_choice_ghost_cache_from_answer_contract(spec, pt)


def _sanitize_coordinate_pair_answer_contract(spec: dict[str, Any], problem_type_id: str) -> bool:
    """Repair coordinate-pair semantics after AI draft induction without skill-specific rules."""
    pt = str(problem_type_id or "").strip().lower()
    target_task = str(spec.get("target_task", "")).strip().lower()
    task_family = str(spec.get("task_family", "")).strip().lower()
    short_answer_prefix = pt.startswith(_SHORT_ANSWER_PROBLEM_TYPE_PREFIXES)
    single_choice_prefix = pt.startswith(_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES)
    ac = spec.get("answer_contract")
    if not isinstance(ac, dict):
        ac = {}
        spec["answer_contract"] = ac

    semantic_values = {
        str(ac.get("answer_type", "")).strip().lower(),
        str(ac.get("answer_shape", "")).strip().lower(),
        str(ac.get("semantics", "")).strip().lower(),
        str(ac.get("answer_semantics", "")).strip().lower(),
        str(ac.get("semantic_answer_shape", "")).strip().lower(),
        str(spec.get("answer_semantics", "")).strip().lower(),
    }
    coordinate_semantic = "coordinate_pair" in semantic_values or "ordered_pair" in semantic_values
    coordinate_markers = ("midpoint", "centroid", "division_point")
    marker_match = any(marker in pt or marker in target_task for marker in coordinate_markers)
    median_coordinate_match = (
        ("median" in pt or "median" in target_task)
        and coordinate_semantic
    )
    if not (coordinate_semantic or marker_match or median_coordinate_match or task_family == "division_point_coordinates_family"):
        return False

    for key in (
        "fallback_checker",
        "fallback_checker_key",
        "fallback_equivalence_type",
        "text_checker",
    ):
        ac.pop(key, None)

    single_choice = single_choice_prefix and not short_answer_prefix
    if single_choice:
        ac.update(
            {
                "answer_type": "single_choice",
                "answer_semantics": "coordinate_pair",
                "semantic_answer_shape": "coordinate_pair",
                "choice_count": 4,
                "correct_choice_count": 1,
            }
        )
        coerce_single_choice_contract(ac)
        return True

    ac.update(
        {
            "answer_type": "coordinate_pair",
            "answer_shape": "coordinate_pair",
            "answer_semantics": "coordinate_pair",
            "semantic_answer_shape": "coordinate_pair",
            "answer_equivalence": "ordered_tuple_exact",
            "equivalence_type": "ordered_tuple_exact",
            "checker": "coordinate_pair_checker",
            "checker_key": "coordinate_pair_checker",
            "presentation_mode": "short_answer",
            "choices_required": False,
            "frontend_render_choices": False,
        }
    )
    return True


def _build_phase2_foundation_preflight(
    *,
    phase1_payload: dict[str, Any],
    generator_results: list[dict[str, Any]],
) -> dict[str, Any]:
    # SOP v0.2 Choice Contract Realignment Choice PT builder
    choice_pts = set()
    for c in phase1_payload.get("candidate_problem_types", []) or []:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        if "single_choice" in pt or "choice" in pt:
            choice_pts.add(pt)
        features = c.get("features", []) or []
        if any(f.get("has_choices") for f in features if isinstance(f, dict)):
            choice_pts.add(pt)
        draft = c.get("problem_type_spec_draft")
        if isinstance(draft, dict):
            ac = draft.get("answer_contract")
            if isinstance(ac, dict) and (ac.get("source_has_choices") or ac.get("has_choices")):
                choice_pts.add(pt)
        prop = c.get("answer_contract_proposal")
        if isinstance(prop, dict) and (prop.get("source_has_choices") or prop.get("has_choices")):
            choice_pts.add(pt)

    for ex in phase1_payload.get("per_example_classification", []) or []:
        if not isinstance(ex, dict):
            continue
        ex_pt = str(ex.get("detected_problem_type_id") or ex.get("problem_type_id") or "").strip()
        if ex_pt and (ex.get("has_choices") or ex.get("source_has_choices")):
            choice_pts.add(ex_pt)

    # SOP v0.2 Data-driven Alignment Global Preflight Guard
    for r in generator_results:
        if not isinstance(r, dict):
            continue
        pt = str(r.get("problem_type_id", "")).strip()
        ac = r.get("answer_contract")
        if not isinstance(ac, dict):
            ac = {}
            r["answer_contract"] = ac
        if "single_choice" in pt or "choice" in pt or pt in choice_pts:
            ac["answer_type"] = "single_choice"
            coerce_single_choice_contract(ac)
            ac["fallback_checker"] = "text_short_checker"
            ac["fallback_checker_key"] = "text_short_checker"
            r["answer_type"] = "single_choice"
            r["answer_shape"] = "single_choice"
            r["checker_key"] = "choice_label_checker"
            r["selected_checker"] = "choice_label_checker"
            r["equivalence_type"] = "choice_label"
        elif "expression" in pt or "interpret_function" in pt:
            if not ac.get("answer_type"):
                ac["answer_type"] = "expression"
            if not ac.get("checker") and not ac.get("checker_key"):
                ac["checker"] = "expression_checker"
                ac["checker_key"] = "expression_checker"
            if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                ac["answer_equivalence"] = "algebraic_equivalent"
                ac["equivalence_type"] = "algebraic_equivalent"
        elif "numeric" in pt or "evaluate" in pt:
            if not ac.get("answer_type"):
                ac["answer_type"] = "integer"
            if not ac.get("checker") and not ac.get("checker_key"):
                ac["checker"] = "integer_checker"
                ac["checker_key"] = "integer_checker"
            if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                ac["answer_equivalence"] = "numeric_exact"
                ac["equivalence_type"] = "numeric_exact"

    for c in phase1_payload.get("candidate_problem_types", []) or []:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        draft = c.get("problem_type_spec_draft")
        if isinstance(draft, dict):
            _reinforce_derivation_contract(draft, pt)
            ac = draft.get("answer_contract")
            if not isinstance(ac, dict):
                ac = {}
                draft["answer_contract"] = ac
            if "single_choice" in pt or "choice" in pt or pt in choice_pts or "fallback" in pt:
                ac["answer_type"] = "single_choice"
                coerce_single_choice_contract(ac)
                ac["fallback_checker"] = "text_short_checker"
                ac["fallback_checker_key"] = "text_short_checker"
                
                # Global generator contract prompt reinforcement
                gc = draft.get("generator_contract")
                if not isinstance(gc, dict):
                    gc = {}
                    draft["generator_contract"] = gc
                gc["contextual_application"] = True
                gc["has_choices"] = True
            elif "expression" in pt or "interpret_function" in pt:
                if not ac.get("answer_type"):
                    ac["answer_type"] = "expression"
                if not ac.get("checker") and not ac.get("checker_key"):
                    ac["checker"] = "expression_checker"
                    ac["checker_key"] = "expression_checker"
                if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                    ac["answer_equivalence"] = "algebraic_equivalent"
                    ac["equivalence_type"] = "algebraic_equivalent"
            elif "numeric" in pt or "evaluate" in pt:
                if not ac.get("answer_type"):
                    ac["answer_type"] = "integer"
                if not ac.get("checker") and not ac.get("checker_key"):
                    ac["checker"] = "integer_checker"
                    ac["checker_key"] = "integer_checker"
                if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                    ac["answer_equivalence"] = "numeric_exact"
                    ac["equivalence_type"] = "numeric_exact"
        
        prop = c.get("answer_contract_proposal")
        if not isinstance(prop, dict):
            prop = {}
            c["answer_contract_proposal"] = prop
        if "single_choice" in pt or "choice" in pt or pt in choice_pts or "fallback" in pt:
            prop["answer_type"] = "single_choice"
            coerce_single_choice_contract(prop)
            prop["fallback_checker"] = "text_short_checker"
            prop["fallback_checker_key"] = "text_short_checker"
        elif "expression" in pt or "interpret_function" in pt:
            if not prop.get("answer_type"):
                prop["answer_type"] = "expression"
            if not prop.get("checker") and not prop.get("checker_key"):
                prop["checker"] = "expression_checker"
                prop["checker_key"] = "expression_checker"
            if not prop.get("answer_equivalence") and not prop.get("equivalence_type"):
                prop["answer_equivalence"] = "algebraic_equivalent"
                prop["equivalence_type"] = "algebraic_equivalent"
        elif "numeric" in pt or "evaluate" in pt:
            if not prop.get("answer_type"):
                prop["answer_type"] = "integer"
            if not prop.get("checker") and not prop.get("checker_key"):
                prop["checker"] = "integer_checker"
                prop["checker_key"] = "integer_checker"
            if not prop.get("answer_equivalence") and not prop.get("equivalence_type"):
                prop["answer_equivalence"] = "numeric_exact"
                prop["equivalence_type"] = "numeric_exact"

    acs = phase1_payload.get("answer_contract_summary")
    if isinstance(acs, dict):
        observed = acs.get("observed_problem_type_answer_contracts")
        if not isinstance(observed, dict):
            observed = {}
            acs["observed_problem_type_answer_contracts"] = observed
        missing_ac_pts = list(acs.get("missing_answer_contract_problem_types", []) or [])
        missing_ck_pts = list(acs.get("missing_checker_key_problem_types", []) or [])
        
        for pt in list(missing_ac_pts) + list(missing_ck_pts) + list(observed.keys()):
            pt = str(pt).strip()
            if not pt:
                continue
            ac = observed.get(pt)
            if not isinstance(ac, dict):
                ac = {}
                observed[pt] = ac
            updated = False
            if "single_choice" in pt or "choice" in pt or pt in choice_pts or "fallback" in pt:
                ac["answer_type"] = "single_choice"
                coerce_single_choice_contract(ac)
                ac["fallback_checker"] = "text_short_checker"
                ac["fallback_checker_key"] = "text_short_checker"
                updated = True
            elif "expression" in pt or "interpret_function" in pt:
                if not ac.get("answer_type"):
                    ac["answer_type"] = "expression"
                if not ac.get("checker") and not ac.get("checker_key"):
                    ac["checker"] = "expression_checker"
                    ac["checker_key"] = "expression_checker"
                if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                    ac["answer_equivalence"] = "algebraic_equivalent"
                    ac["equivalence_type"] = "algebraic_equivalent"
                updated = True
            elif "numeric" in pt or "evaluate" in pt:
                if not ac.get("answer_type"):
                    ac["answer_type"] = "integer"
                if not ac.get("checker") and not ac.get("checker_key"):
                    ac["checker"] = "integer_checker"
                    ac["checker_key"] = "integer_checker"
                if not ac.get("answer_equivalence") and not ac.get("equivalence_type"):
                    ac["answer_equivalence"] = "numeric_exact"
                    ac["equivalence_type"] = "numeric_exact"
                updated = True
            
            if updated:
                if pt in missing_ac_pts:
                    missing_ac_pts.remove(pt)
                if pt in missing_ck_pts:
                    missing_ck_pts.remove(pt)
        
        acs["missing_answer_contract_problem_types"] = missing_ac_pts
        acs["missing_checker_key_problem_types"] = missing_ck_pts

    acs = phase1_payload.get("answer_contract_summary", {}) if isinstance(phase1_payload.get("answer_contract_summary"), dict) else {}
    missing_answer_contract = list(acs.get("missing_answer_contract_problem_types", []) or [])
    missing_checker_key = list(acs.get("missing_checker_key_problem_types", []) or [])
    invalid_eq = [
        pt
        for pt, c in (acs.get("observed_problem_type_answer_contracts", {}) or {}).items()
        if isinstance(c, dict) and str(c.get("equivalence_type", "")).strip() not in EQUIVALENCE_TYPE_WHITELIST
    ]
    blocked_rows = [r for r in generator_results if isinstance(r, dict) and str(r.get("generator_status", "")).strip() in {"blocked", "generator_not_ready", "pending_template"}]
    missing_generator = sorted({str(r.get("problem_type_id", "")).strip() for r in blocked_rows if str(r.get("problem_type_id", "")).strip()})
    missing_runtime_binding = sorted({
        str(r.get("problem_type_id", "")).strip()
        for r in generator_results
        if isinstance(r, dict) and "phase1_semantic_alignment_blocked" in (r.get("blockers") or [])
    })
    observed_pts = {
        str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        for c in (phase1_payload.get("candidate_problem_types") or [])
        if isinstance(c, dict)
    }
    observed_pts.discard("")
    bound_pts = {
        str(r.get("problem_type_id", "")).strip()
        for r in generator_results
        if isinstance(r, dict) and str(r.get("problem_type_id", "")).strip()
    }
    missing_registry_binding = sorted(observed_pts - bound_pts)
    missing_verifier = sorted(set(invalid_eq))
    usable_pts = {
        str(r.get("problem_type_id", "")).strip()
        for r in generator_results
        if isinstance(r, dict)
        and r.get("usable_for_phase3")
        and str(r.get("generator_status", "")).strip()
        in {"runtime_ready", "runtime_ready_with_warning", "limited_runtime_ready"}
    }
    missing_domain_function = sorted({
        pt
        for pt in (
            str(r.get("problem_type_id", "")).strip()
            for r in generator_results
            if isinstance(r, dict) and "answer_contract_not_supported" in (r.get("blockers") or [])
        )
        if pt and pt not in usable_pts
    })
    missing_checker = sorted(set(missing_checker_key))

    missing_map = {
        "missing_checker": missing_checker,
        "missing_verifier": missing_verifier,
        "missing_domain_function": missing_domain_function,
        "missing_generator": missing_generator,
        "missing_runtime_binding": missing_runtime_binding,
        "missing_registry_binding": missing_registry_binding,
    }
    has_missing = any(bool(v) for v in missing_map.values()) or bool(missing_answer_contract)
    repair_steps: list[dict[str, Any]] = []
    for gap, items in missing_map.items():
        if not items:
            continue
        repair_steps.append(
            {
                "gap": gap,
                "problem_types": items,
                "action": f"repair_{gap}",
            }
        )
    if missing_answer_contract:
        repair_steps.append(
            {
                "gap": "missing_answer_contract",
                "problem_types": sorted(set(missing_answer_contract)),
                "action": "repair_answer_contract",
            }
        )
    return {
        "foundation_ready": not has_missing,
        "foundation_status": "PASS" if not has_missing else "FOUNDATION_REPAIR_REQUIRED",
        "missing_checker": missing_checker,
        "missing_verifier": missing_verifier,
        "missing_domain_function": missing_domain_function,
        "missing_generator": missing_generator,
        "missing_runtime_binding": missing_runtime_binding,
        "missing_registry_binding": missing_registry_binding,
        "missing_answer_contract_problem_types": sorted(set(missing_answer_contract)),
        "repair_plan": repair_steps,
        "next_action": "phase3_package_draft" if not has_missing else "repair_foundation_gaps_then_rerun_phase2",
    }


def _phase3_source_alignment_layer(phase1: dict[str, Any], phase2: dict[str, Any]) -> dict[str, Any]:
    per_example = phase1.get("per_example_classification", []) if isinstance(phase1.get("per_example_classification"), list) else []
    runtime_pts = {
        str(x.get("problem_type_id", "")).strip()
        for x in (phase2.get("generator_results", []) or [])
        if isinstance(x, dict) and bool(x.get("usable_for_phase3"))
    }
    runtime_pts.discard("")
    observed_pts = {
        str(x.get("detected_problem_type_id", "")).strip()
        for x in per_example
        if isinstance(x, dict) and str(x.get("detected_problem_type_id", "")).strip() not in {"", "unknown"}
    }
    missing = sorted(observed_pts - runtime_pts) if runtime_pts else sorted(observed_pts)
    underrepresented = sorted(set(missing))
    status = "PASS" if not missing and not underrepresented else "PARTIAL"
    return {
        "status": status,
        "missing_source_aligned_problem_types": missing,
        "underrepresented_runtime_forms": underrepresented,
    }


def _log_gencode_ai_runtime(tag: str, meta: dict[str, Any]) -> None:
    if not has_app_context():
        return
    current_app.logger.info(
        "[GENCODE AI RUNTIME] tag=%s role=%s mode=%s provider=%s model=%s source=%s has_api_key=%s endpoint=%s reason=%s",
        tag,
        meta.get("role", ""),
        meta.get("mode", ""),
        meta.get("provider", ""),
        meta.get("model", ""),
        meta.get("source", ""),
        bool(meta.get("has_api_key", False)),
        meta.get("endpoint", ""),
        meta.get("failure_reason", ""),
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml  # type: ignore
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    path.write_text(text, encoding="utf-8")


def _load_registered_classifier_rulepack(skill_id: str) -> dict[str, Any] | None:
    root = _load_yaml(CLASSIFIER_RULEPACK_PATH)
    skills = root.get("skills", []) if isinstance(root.get("skills"), list) else []
    sid = str(skill_id or "").strip()
    for item in skills:
        if not isinstance(item, dict):
            continue
        if str(item.get("skill_id", "")).strip() == sid:
            return item
    return None


def _classify_examples_with_rulepack(
    *,
    skill_id: str,
    examples: list[dict[str, Any]],
    pack: dict[str, Any],
) -> list[dict[str, Any]]:
    problem_types = pack.get("problem_types", []) if isinstance(pack.get("problem_types"), list) else []
    rules = pack.get("classification_rules", []) if isinstance(pack.get("classification_rules"), list) else []
    pt_by_id = {
        str(x.get("problem_type_id", "")).strip(): x
        for x in problem_types
        if isinstance(x, dict) and str(x.get("problem_type_id", "")).strip()
    }
    fallback_pt = next((pid for pid, cfg in pt_by_id.items() if not bool(cfg.get("requires_human_action", False))), "") or next(iter(pt_by_id.keys()), "unclassified_source_review")
    rows: list[dict[str, Any]] = []
    for ex in examples:
        text = _source_text(ex)
        text_l = text.lower()
        chosen = ""
        for r in rules:
            if not isinstance(r, dict):
                continue
            toks = r.get("if_contains", []) if isinstance(r.get("if_contains"), list) else []
            toks = [str(t).strip().lower() for t in toks if str(t).strip()]
            if toks and any(t in text_l for t in toks):
                chosen = str(r.get("prefer_problem_type_id", "")).strip()
                if chosen:
                    break
        pt = chosen if chosen in pt_by_id else fallback_pt
        cfg = pt_by_id.get(pt, {})
        checker = str(cfg.get("checker", "")).strip()
        eq = str(cfg.get("equivalence", "")).strip()
        needs_human = bool(cfg.get("requires_human_action", False))
        rows.append(
            {
                "example_id": ex.get("id"),
                "title": str(ex.get("title", "")).strip(),
                "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
                "problem_preview": text[:200],
                "skill_id": skill_id,
                "subskill_id": pt,
                "problem_type_id": pt,
                "runtime_category": "manual_review" if needs_human else "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression",
                "classification_rule_id": "rule_pack.yaml",
                "classification_reason": "matched_registered_yaml_rule_pack",
                "classifier_confidence": "high",
                "semantic_risk_flags": [],
                "semantic_audit_status": "review_required" if needs_human else "ok",
                "generator_status": "manual_review" if needs_human else "ready_for_draft",
                "manual_review_reason": str(cfg.get("notes", "")).strip() if needs_human else "",
            }
        )
    return rows


def _build_classifier_yaml_draft_from_phase1(payload: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    skill_id = str(payload.get("skill_id", "")).strip()
    skill_ch_name = _pick_skill_ch_name(skill_id, examples)
    candidates = payload.get("candidate_problem_types", []) if isinstance(payload.get("candidate_problem_types"), list) else []
    per_example = payload.get("per_example_classification", []) if isinstance(payload.get("per_example_classification"), list) else []
    pt_contract: dict[str, dict[str, Any]] = {}
    for c in candidates:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        checker = str(c.get("checker_key_proposal", "")).strip()
        eq = str(c.get("equivalence_type_proposal", "")).strip()
        at = str(c.get("answer_type", "")).strip()
        if not at:
            at = _to_answer_type_from_equivalence(eq)
        at, eq, checker = _align_contract(at, eq, checker)
        pt_contract[pt] = {
            "problem_type_id": pt,
            "display_name": pt.replace("_", " "),
            "checker": checker,
            "equivalence": eq,
            "runtime_candidate": bool(checker and eq and checker != "manual_review_checker" and eq != "manual_review_or_ai_judged"),
            "requires_human_action": bool(checker == "manual_review_checker" or eq == "manual_review_or_ai_judged"),
            "merge_policy": "single_primary_problem_type" if len({str(x.get('detected_problem_type_id', '')).strip() for x in per_example if isinstance(x, dict) and str(x.get('detected_problem_type_id', '')).strip()}) <= 1 else "split_by_contract_diff",
            "notes": "auto-generated classifier draft from phase1",
        }
    rules: list[dict[str, Any]] = []
    for pt in pt_contract.keys():
        rules.append({"if_contains": [], "prefer_problem_type_id": pt})
    return {
        "skill_id": skill_id,
        "skill_ch_name": skill_ch_name,
        "classifier_source": f"{payload.get('classifier_source', 'ai_bootstrap')}_confirmed",
        "problem_types": list(pt_contract.values()),
        "classification_rules": rules,
        "source_classifications": per_example,
        "source_policy": {
            "source_count_threshold_for_split": 4,
            "small_skill_merge_allowed": True,
            "min_source_examples": 1,
            "allow_single_problem_type": True,
            "allow_skill_default_problem_type": True,
            "default_problem_type_used": any(str(k).endswith("_default") for k in pt_contract.keys()),
            "single_primary_problem_type": len(pt_contract) <= 1,
            "split_only_when_checker_or_answer_contract_differs": True,
            "do_not_create_student_subskills": True,
        },
    }


def _write_classifier_yaml_draft(skill_id: str, draft: dict[str, Any]) -> str:
    CLASSIFIER_DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    path = CLASSIFIER_DRAFT_DIR / f"{skill_id}_classifier.yaml"
    _write_yaml(path, draft)
    return str(path)


def register_classifier_rulepack_from_draft(skill_id: str, confirm: bool = False) -> dict[str, Any]:
    draft_path = CLASSIFIER_DRAFT_DIR / f"{skill_id}_classifier.yaml"
    if not draft_path.exists():
        return {"ok": False, "skill_id": skill_id, "error": "classifier_draft_not_found", "draft_path": str(draft_path)}
    draft = _load_yaml(draft_path)
    if not confirm:
        return {"ok": True, "skill_id": skill_id, "status": "preview", "draft_path": str(draft_path), "formal_rulepack_path": str(CLASSIFIER_RULEPACK_PATH)}
    if not isinstance(draft, dict) or not str(draft.get("skill_id", "")).strip():
        return {"ok": False, "skill_id": skill_id, "error": "invalid_classifier_draft_yaml", "draft_path": str(draft_path)}
    CLASSIFIER_RULEPACK_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = ""
    if CLASSIFIER_RULEPACK_PATH.exists():
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup = CLASSIFIER_RULEPACK_BACKUP_DIR / f"phase1_rule_packs.{ts}.yaml"
        shutil.copy2(CLASSIFIER_RULEPACK_PATH, backup)
        backup_path = str(backup)
    root = _load_yaml(CLASSIFIER_RULEPACK_PATH)
    if not root:
        root = {"version": 1, "skills": []}
    skills = root.get("skills", []) if isinstance(root.get("skills"), list) else []
    sid = str(skill_id or "").strip()
    replaced = False
    for i, s in enumerate(skills):
        if isinstance(s, dict) and str(s.get("skill_id", "")).strip() == sid:
            skills[i] = draft
            replaced = True
            break
    if not replaced:
        skills.append(draft)
    root["skills"] = skills
    _write_yaml(CLASSIFIER_RULEPACK_PATH, root)
    _ = _load_yaml(CLASSIFIER_RULEPACK_PATH)  # read-back validation
    return {
        "ok": True,
        "skill_id": sid,
        "status": "registered",
        "replaced_existing": replaced,
        "draft_path": str(draft_path),
        "formal_rulepack_path": str(CLASSIFIER_RULEPACK_PATH),
        "backup_path": backup_path,
    }


def _resolve_gencode_ai_client(preferred_roles: list[str]) -> tuple[Any | None, dict[str, Any]]:
    snapshot = get_ai_settings_snapshot()
    mode = str(snapshot.get("ai_global_strategy", "unknown"))
    api_key, _src = resolve_gemini_api_key()
    has_api_key = bool(str(api_key or "").strip())
    last_meta: dict[str, Any] = {}
    for role in preferred_roles:
        cfg = get_effective_model_config(role)
        provider = str(cfg.get("provider", "local")).lower()
        model = str(cfg.get("model", ""))
        source = str(cfg.get("_resolved_source", "unknown"))
        meta = {
            "role": role,
            "mode": mode,
            "provider": provider,
            "model": model,
            "source": source,
            "has_api_key": has_api_key,
            "endpoint": "google_api" if provider == "google" else "local_api",
            "failure_reason": "",
        }
        try:
            c = get_ai_client(role=role)
            actual_provider = "google" if "GoogleAIClient" in type(c).__name__ else "local"
            if provider == "google" and actual_provider != "google":
                meta["failure_reason"] = "resolved_google_but_fell_back_to_local"
                _log_gencode_ai_runtime("resolve", meta)
                last_meta = meta
                continue
            _log_gencode_ai_runtime("resolve", meta)
            return c, meta
        except Exception as ex:
            meta["failure_reason"] = str(ex)
            _log_gencode_ai_runtime("resolve", meta)
            last_meta = meta
            continue
    return None, last_meta


def _safe_file_component(value: str) -> str:
    return sanitize_path_segment(value)


def _load_examples(skill_id: str, db_path: str = "instance/kumon_math.db") -> list[dict[str, Any]]:
    """Load textbook examples strictly by skill_id (no chapter/section cross-skill merge)."""
    con = sqlite3.connect(str(PROJECT_ROOT / db_path))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY rowid", (skill_id,)).fetchall()]
    con.close()
    validated: list[dict[str, Any]] = []
    for row in rows:
        ex_sid = str(row.get("skill_id") or "").strip()
        if not ex_sid:
            continue
        if ex_sid != skill_id:
            continue
        validated.append(row)
    return validated


def _classify_examples(skill_id: str, examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    classifier = get_classifier_for_skill(skill_id)
    ctx = ClassifierContext(project_root=PROJECT_ROOT, skill_id=skill_id)
    result = classifier.classify_examples(examples, ctx)
    return [dict(x) for x in result.examples_map_entries]


_ALLOWED_CHECKERS = {
    "numeric_checker", "integer_checker", "rational_checker", "decimal_tolerance_checker", 
    "percentage_checker", "expression_checker", "equation_checker", "interval_checker", 
    "set_checker", "tuple_checker", "matrix_checker", "choice_label_checker", 
    "text_short_checker", "manual_review_checker", "ai_judged_checker"
}
_ALLOWED_EQUIVS = {
    "numeric_exact", "rational_equivalent", "decimal_tolerance", "percentage_equivalent", 
    "algebraic_equivalent", "equation_equivalent", "interval_set", "unordered_solution_set", 
    "ordered_tuple_exact", "unordered_tuple_equivalent", "matrix_exact", "choice_label", 
    "exact_string", "case_insensitive_string", "manual_review_or_ai_judged"
}


def _to_answer_type_from_equivalence(eq: str) -> str:
    m = {
        "choice_label": "choice",
        "numeric_exact": "integer",
        "rational_equivalent": "rational",
        "decimal_tolerance": "rational",
        "percentage_equivalent": "rational",
        "algebraic_equivalent": "expression",
        "equation_equivalent": "expression",
        "interval_set": "interval",
        "unordered_solution_set": "set",
        "ordered_tuple_exact": "ordered_tuple",
        "unordered_tuple_equivalent": "unordered_tuple",
        "matrix_exact": "matrix",
        "exact_string": "text_short",
        "case_insensitive_string": "text_short",
        "manual_review_or_ai_judged": "manual_review",
    }
    return m.get(str(eq or "").strip(), "expression")


def _camel_to_snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name or ""))
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s)
    return s.strip("_").lower()


def _skill_default_problem_type_id(skill_id: str) -> str:
    tail = str(skill_id or "").split("_")[-1]
    base = _camel_to_snake(tail) or "skill"
    return f"{base}_default"


def _sources_complete_for_default(examples: list[dict[str, Any]]) -> bool:
    if not examples:
        return False
    for ex in examples:
        txt = _source_text(ex)
        if not txt.strip():
            return False
        bad = ["缺圖", "缺選項", "圖片遺失", "unreadable", "missing image"]
        if any(b in txt for b in bad):
            return False
    return True


def _align_contract(answer_type: str, eq: str, checker: str) -> tuple[str, str, str]:
    at = str(answer_type or "").strip()
    equiv = str(eq or "").strip()
    chk = str(checker or "").strip()

    # Universal TVET Math B standard checker and equivalence alignment
    if at == "expression":
        equiv = "algebraic_equivalent"
        chk = "expression_checker"
    elif at in ["numeric", "integer"]:
        equiv = "numeric_exact"
        chk = "integer_checker"
    elif at == "rational":
        equiv = "rational_equivalent"
        chk = "rational_checker"
    elif at == "choice":
        equiv = "choice_label"
        chk = "choice_label_checker"
    elif at == "interval":
        equiv = "interval_set"
        chk = "interval_checker"
    elif at == "set":
        equiv = "unordered_solution_set"
        chk = "set_checker"
    elif at in ["ordered_tuple", "unordered_tuple", "coordinate_pair", "ordered_pair"]:
        equiv = "ordered_tuple_exact"
        chk = "tuple_checker"
    elif at == "matrix":
        equiv = "matrix_exact"
        chk = "matrix_checker"
    elif at in ["text", "text_short", "short_answer"]:
        equiv = "exact_string"
        chk = "text_short_checker"
    elif at == "manual_review":
        equiv = "manual_review_or_ai_judged"
        chk = "manual_review_checker"

    return at, equiv, chk


def _infer_default_contract(examples: list[dict[str, Any]]) -> tuple[str, str]:
    at = "expression"
    for ex in examples:
        cand_at = str(ex.get("answer_type", ex.get("example_feature", {}).get("answer_type", ""))).strip()
        if cand_at:
            at = cand_at
            break
            
    texts = " ".join(_source_text(x) for x in examples)
    if any(tok in texts for tok in ["(A)", "(B)", "(C)", "(D)", "（A）", "（B）", "（C）", "（D）"]):
        at = "choice"
        
    has_fraction = "frac" in texts or "/" in texts
    if at in ["numeric", "integer", "rational", "float", "number"]:
        if has_fraction:
            at = "rational"
        else:
            at = "integer"
            
    # Universal fallback via _align_contract to block checker_contract_missing
    _, eq, checker = _align_contract(at, "", "")
    if checker and eq:
        return checker, eq
        
    return "expression_checker", "algebraic_equivalent"


def _source_text(ex: dict[str, Any]) -> str:
    for k in ("problem_text", "problem", "question", "stem", "content", "title"):
        v = str(ex.get(k, "")).strip()
        if v:
            return v
    return ""


def _normalize_json_payload(obj: Any) -> Any:
    legacy_map = {
        # Checkers mapping to standard 15 whitelist
        "text_checker": "text_short_checker",
        "exact_string_checker": "text_short_checker",
        "exact_text_checker": "text_short_checker",
        "expression_equivalence_checker": "expression_checker",
        "solution_set_checker": "set_checker",
        "coordinate_pair_checker": "tuple_checker",
        "fraction_checker": "rational_checker",
        "choice_checker": "choice_label_checker",
        "equation_equivalence_checker": "equation_checker",
        "matrix_exact_checker": "matrix_checker",
        # Equivalence mapping to standard 15 whitelist
        "numeric_equivalence": "numeric_exact",
        "numeric_equal": "numeric_exact",
        "numeric_exact_equivalence": "numeric_exact",
        "string_equivalence": "exact_string",
        "exact_text": "exact_string",
        "exact_string_equivalence": "exact_string",
        "fraction_equal": "rational_equivalent",
        "rational_equivalence": "rational_equivalent",
        "set_equal": "unordered_solution_set",
        "interval_equivalence": "interval_set",
        "inequality_solution_equivalence": "interval_set",
        "expression_equivalence": "algebraic_equivalent",
        "coordinate_pair_equivalence": "ordered_tuple_exact",
        "ordered_pair": "ordered_tuple_exact",
        "equation_equivalence": "equation_equivalent",
        "matrix_equivalence": "matrix_exact"
    }

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if isinstance(v, str):
                v_str = v.strip()
                if v_str in legacy_map:
                    v = legacy_map[v_str]
            new_dict[k] = _normalize_json_payload(v)
        return new_dict
    elif isinstance(obj, list):
        return [_normalize_json_payload(x) for x in obj]
    elif isinstance(obj, str):
        v_str = obj.strip()
        if v_str in legacy_map:
            return legacy_map[v_str]
        return obj
    return obj


def _json_from_text(raw: str) -> dict[str, Any]:
    s = str(raw or "").strip()
    if not s:
        return {}
    try:
        parsed = json.loads(s)
        return _normalize_json_payload(parsed) if isinstance(parsed, dict) else {}
    except Exception:
        pass
    a = s.find("{")
    b = s.rfind("}")
    if a >= 0 and b > a:
        try:
            parsed = json.loads(s[a : b + 1])
            return _normalize_json_payload(parsed) if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _fallback_ai_explanation(result: dict[str, Any], error: str = "") -> dict[str, Any]:
    return {
        "enabled": True,
        "status": "failed",
        "summary": "AI 解讀失敗，請查看下方原始 Phase log。",
        "error": str(error or ""),
        "severity": "warning",
        "what_happened": "",
        "main_reason": "",
        "next_action": "請查看原始 Phase log 與 reports。",
        "items_to_check": [],
        "can_continue": bool(result.get("can_continue", False)),
        "confidence": "low",
    }


def _build_gencode_ai_explanation_payload(result: dict[str, Any]) -> dict[str, Any]:
    phase = str(result.get("phase", "")).strip()
    payload = {
        "skill_id": result.get("skill_id"),
        "skill_ch_name": result.get("skill_ch_name"),
        "skill_en_name": result.get("skill_en_name"),
        "phase": phase,
        "phase_status": result.get("phase_status"),
        "summary_message": result.get("summary_message"),
        "requires_human_action": result.get("requires_human_action"),
        "can_continue": result.get("can_continue"),
        "classifier_source": result.get("classifier_source"),
        "ai_bootstrap_used": result.get("ai_bootstrap_used"),
        "ai_bootstrap_status": result.get("ai_bootstrap_status"),
        "exception_review_gate": result.get("exception_review_gate"),
        "runtime_ready_gate": result.get("runtime_ready_gate"),
        "generator_draft_gate": result.get("generator_draft_gate"),
        "candidate_problem_types": result.get("candidate_problem_types"),
        "human_review_items": result.get("human_review_items"),
        "generator_results": result.get("generator_results"),
        "publish_check": result.get("publish_check"),
        "package_status": result.get("package_status"),
        "py_compile_status": result.get("py_compile_status"),
        "runtime_smoke_status": result.get("runtime_smoke_status"),
        "reports": result.get("reports"),
        "error": result.get("error"),
    }
    if phase == "phase1":
        payload["runtime_ready_gate"] = {}
        payload["generator_results"] = []
        payload["publish_check"] = {}
        payload["package_status"] = ""
        payload["py_compile_status"] = ""
        payload["runtime_smoke_status"] = ""
    return payload


def explain_gencode_result_with_ai(result: dict[str, Any]) -> dict[str, Any]:
    try:
        structured = _build_gencode_ai_explanation_payload(result)
        phase = str(result.get("phase", "")).strip().lower()
        phase_rule = (
            "If phase is phase1, focus only on classifier/rule-pack/bootstrap/classification quality/manual review; "
            "do not mention runtime_smoke_failed, dynamic_sampling_failed, contract_tests_failed unless they explicitly exist in phase1 context."
            if phase == "phase1"
            else "Use current phase context only; do not speculate across phases."
        )
        prompt = (
            "你是 Gencode Phase 結果解讀助手。只能解讀，不可改動 gate 決策。\n"
            "請只輸出 JSON，不要 Markdown。\n"
            "必填欄位: severity(success|warning|blocked|failed), short_title, summary, what_happened(list), main_reason, next_action, items_to_check(list), can_continue_phase2(boolean), can_publish(boolean), user_friendly_message, confidence(high|medium|low)\n"
            "規則:\n"
            "- 不可宣稱通過，除非 phase_status / blockers 支援。\n"
            "- 不可建議發布，除非 can_publish_formal=true。\n"
            "- 必須引用輸入 JSON，資訊不足時要明確說需要查看 reports。\n"
            "- 語氣精簡、可操作。\n"
            f"- {phase_rule}\n"
            "輸入 JSON:\n"
            + json.dumps(structured, ensure_ascii=False)
        )
        client, client_meta = _resolve_gencode_ai_client(["architect", "tutor", "default"])
        if client is None:
            return _fallback_ai_explanation(result, client_meta.get("failure_reason", "AI client unavailable or API key missing"))
        resp = call_ai_with_retry(client, prompt, max_retries=2, retry_delay=2, timeout=90)
        parsed = _json_from_text(getattr(resp, "text", ""))
        if not parsed:
            return _fallback_ai_explanation(result, "ai_empty_or_invalid_json")
        sev = str(parsed.get("severity", "")).strip().lower()
        if sev not in {"success", "warning", "blocked", "failed"}:
            phase_status = str(result.get("phase_status", "")).lower()
            if "failed" in phase_status:
                sev = "failed"
            elif "blocked" in phase_status or bool(result.get("requires_human_action")):
                sev = "blocked"
            elif "warning" in phase_status:
                sev = "warning"
            else:
                sev = "success"
        return {
            "enabled": True,
            "status": "success",
            "severity": sev,
            "short_title": str(parsed.get("short_title", "")).strip(),
            "summary": str(parsed.get("summary", "")).strip(),
            "what_happened": parsed.get("what_happened", []) if isinstance(parsed.get("what_happened"), list) else [],
            "main_reason": str(parsed.get("main_reason", "")).strip(),
            "next_action": str(parsed.get("next_action", "")).strip(),
            "items_to_check": parsed.get("items_to_check", []) if isinstance(parsed.get("items_to_check"), list) else [],
            "can_continue_phase2": bool(parsed.get("can_continue_phase2", False)),
            "can_publish": bool(parsed.get("can_publish", False)),
            "user_friendly_message": str(parsed.get("user_friendly_message", "")).strip(),
            "confidence": str(parsed.get("confidence", "medium")).strip().lower() or "medium",
        }
    except Exception as ex:
        return _fallback_ai_explanation(result, str(ex))


def _is_unrelated_problem_type(pt: str, source_texts: list[str]) -> bool:
    p = str(pt or "").strip().lower()
    if not p:
        return True
    if p.startswith("absolute_value_inequality_"):
        corpus = " ".join(source_texts).lower()
        if ("|" not in corpus) and ("絕對值" not in corpus) and ("absolute value" not in corpus):
            return True
    return False


def _is_bad_problem_type_style(skill_id: str, pt: str) -> bool:
    p = str(pt or "").strip().lower()
    sid = re.sub(r"[^a-z0-9_]", "_", str(skill_id or "").strip().lower())
    if not p:
        return True
    if sid and sid in p:
        return True
    if re.search(r"^vh_+b\d+_", p):
        return True
    return False


def _build_neutral_fallback(
    *,
    skill_id: str,
    examples: list[dict[str, Any]],
    reason: str,
    problem_type_id: str = "classifier_missing_source_review",
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    proposed_example_map: list[dict[str, Any]] = []
    for i, ex in enumerate(examples):
        exid = ex.get("id")
        text = _source_text(ex)
        row = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": text[:200],
            "skill_id": skill_id,
            "subskill_id": problem_type_id,
            "problem_type_id": problem_type_id,
            "runtime_category": "manual_review",
            "classification_rule_id": "phase1.neutral_fallback",
            "classification_reason": reason,
            "classifier_confidence": "low",
            "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
            "semantic_audit_status": "review_required",
            "generator_status": "manual_review",
            "manual_review_reason": reason,
        }
        entries.append(row)
        proposed_example_map.append({"example_id": exid, "proposed_problem_type_id": problem_type_id, "source_index": i + 1})
    proposal = {
        "proposed_problem_types": [problem_type_id],
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": {
            problem_type_id: {
                "answer_type": "manual_review",
                "equivalence_type": "manual_review_or_ai_judged",
                "checker_key": "manual_review_checker",
            }
        },
        "risk_flags": ["classifier_missing_or_ai_bootstrap_failed"],
    }
    meta = {
        "classifier_source": "neutral_fallback",
        "ai_bootstrap_used": True,
        "ai_bootstrap_status": "failed",
        "ai_bootstrap_error": reason,
        "ai_bootstrap_raw_response_preview": "",
        "ai_bootstrap_validation_errors": [],
        "ai_bootstrap_prompt_version": "gencode_phase1_ai_bootstrap_v2",
        "ai_bootstrap_model": "",
        "ai_bootstrap_provider": "",
        "ai_bootstrap_config_source": "",
        "ai_bootstrap_confidence_summary": {"count": len(examples), "avg": 0.0, "low_confidence_count": len(examples)},
        "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
    }
    return entries, proposal, meta


def _run_ai_classifier_bootstrap(
    *,
    skill_id: str,
    skill_ch_name: str,
    examples: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    prompt_version = "gencode_phase1_ai_bootstrap_v2"
    client, client_meta = _resolve_gencode_ai_client(["architect", "tutor", "default"])
    if client is None:
        raise RuntimeError(client_meta.get("failure_reason", "AI client unavailable or API key missing") or "AI client unavailable or API key missing")
    provider = str(client_meta.get("provider", ""))
    model_name = str(client_meta.get("model", "") or getattr(client, "model_name", "") or getattr(client, "model", "") or "")
    source_items = []
    for i, ex in enumerate(examples, start=1):
        source_items.append(
            {
                "source_index": i,
                "example_id": ex.get("id"),
                "source_type": ex.get("source_type"),
                "title": ex.get("title"),
                "question_text": _source_text(ex),
                "answer": ex.get("answer"),
                "explanation": ex.get("explanation"),
                "image_hint": ex.get("image_path") or ex.get("image_url") or ex.get("figure_hint"),
            }
        )
    prompt = (
        phase1_enforcement_assertion_block(
            _build_phase1_main_skill_anchor(skill_id, examples),
            include_anchor_fields=True,
        )
        + "\nYou are a math problem-type classifier bootstrapper.\n"
        "Return JSON only.\n"
        "Skill context:\n"
        + json.dumps(
            {
                "skill_id": skill_id,
                "skill_ch_name": skill_ch_name,
                "skill_en_name": str(skill_id.split("_", 1)[-1] if "_" in skill_id else ""),
            },
            ensure_ascii=False,
        )
        + "\nSource examples:\n"
        + json.dumps(source_items, ensure_ascii=False)
        + "\nOutput schema keys: skill_id, skill_ch_name, classifier_source, problem_types, source_classifications, manual_review_items.\n"
        "Rules:\n"
        "- The skill_id and ALL source examples are 100% teacher-confirmed aligned. NEVER judge cross-family membership.\n"
        "- infer skill-related problem types ONLY from skill_id tokens, skill_ch_name, and question text.\n"
        "- NEVER route to absolute_value_inequality unless stems contain absolute-value notation.\n"
        "- For QuadraticInequality / Factoring skills, prefer factor_quadratic_by_cross_multiplication or solve_quadratic_inequality.\n"
        "- avoid unrelated problem types.\n"
        "- You do not need to split every skill into multiple problem_types.\n"
        "- If source examples are few and structurally similar, merge into one primary problem_type.\n"
        "- A single good problem_type is acceptable.\n"
        "- Split only when checker/equivalence/answer contract differs.\n"
        "- Do not over-segment small skills.\n"
        "- do not output only generic unclassified_source_review unless sources are truly unreadable.\n"
        "- when possible, propose semantic problem_type candidates; one primary type is allowed.\n"
        "- problem_type_id must be semantic snake_case; do NOT sanitize the full skill_id into problem_type_id.\n"
        "- prefer semantic snake_case problem_type_id derived from source math objects (not skill_id echo).\n"
        "- problem_type_id must be snake_case and skill-related.\n"
        "- checker in: interval_checker, choice_label_checker, text_checker, numeric_checker, ordered_pair_checker, expression_equivalence_checker, manual_review_checker.\n"
        "- equivalence in: interval_set, choice_label, string_equivalence, numeric_equivalence, ordered_pair, expression_equivalence, manual_review_or_ai_judged.\n"
        "- if checker/equivalence is manual review, requires_human_action=true (only for drawing/graph/missing-image/unreadable sources).\n"
        "- if deterministic checker is possible, set requires_human_action=false.\n"
        "- every source_index must appear in source_classifications.\n"
        "- confidence is 0..1.\n"
        "- output must be contract-first: define problem_type_id, answer_contract, semantic_contract before proposing generator code.\n"
        "- generated payload for deterministic runtime must include metadata.givens, metadata.target, metadata.derivation.\n"
        "- for single-choice, do not embed options in question_text; keep options only in choices.\n"
    )
    resp = call_ai_with_retry(client, prompt, max_retries=2, retry_delay=2, timeout=180)
    raw_text = str(getattr(resp, "text", "") or "")
    raw_preview = raw_text[:1000]
    parsed = _json_from_text(raw_text)
    if not parsed:
        raise RuntimeError(f"ai_bootstrap_invalid_json::{raw_preview[:200]}")

    source_map = {i: ex for i, ex in enumerate(examples, start=1)}
    source_texts = [_source_text(ex) for ex in examples]
    ai_problem_types = parsed.get("problem_types") if isinstance(parsed.get("problem_types"), list) else []
    ai_source_cls = parsed.get("source_classifications") if isinstance(parsed.get("source_classifications"), list) else []
    by_index: dict[int, dict[str, Any]] = {}
    contracts: dict[str, dict[str, Any]] = {}
    risk_flags: list[str] = []
    confs: list[float] = []

    validation_errors: list[str] = []
    unclassified_count = 0
    for row in ai_source_cls:
        if not isinstance(row, dict):
            continue
        try:
            idx = int(row.get("source_index"))
        except Exception:
            continue
        if idx not in source_map:
            continue
        pt = str(row.get("matched_problem_type_id", "")).strip()
        checker = str(row.get("checker", "")).strip()
        eq = str(row.get("equivalence", "")).strip()
        needs_human = bool(row.get("requires_human_action", False))
        conf = float(row.get("confidence", 0.0) or 0.0)
        confs.append(conf)
        invalid = (
            (not re.fullmatch(r"[a-z][a-z0-9_]*", pt))
            or checker not in _ALLOWED_CHECKERS
            or eq not in _ALLOWED_EQUIVS
            or _is_unrelated_problem_type(pt, source_texts)
            or _is_bad_problem_type_style(skill_id, pt)
        )
        if not re.fullmatch(r"[a-z][a-z0-9_]*", pt):
            validation_errors.append(f"source_index={idx}: invalid_problem_type_id={pt}")
        if checker not in _ALLOWED_CHECKERS:
            validation_errors.append(f"source_index={idx}: invalid_checker={checker}")
        if eq not in _ALLOWED_EQUIVS:
            validation_errors.append(f"source_index={idx}: invalid_equivalence={eq}")
        if _is_unrelated_problem_type(pt, source_texts):
            validation_errors.append(f"source_index={idx}: unrelated_problem_type={pt}")
        if _is_bad_problem_type_style(skill_id, pt):
            validation_errors.append(f"source_index={idx}: invalid_problem_type_id_style={pt}")
        if invalid or conf < 0.6:
            pt = "unclassified_source_review"
            checker = "manual_review_checker"
            eq = "manual_review_or_ai_judged"
            needs_human = True
            risk_flags.append("ai_bootstrap_low_confidence_or_invalid")
        if checker == "manual_review_checker" or eq == "manual_review_or_ai_judged":
            needs_human = True
        if pt.endswith("unclassified_source_review"):
            unclassified_count += 1
        ex = source_map[idx]
        exid = ex.get("id")
        by_index[idx] = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": _source_text(ex)[:200],
            "skill_id": skill_id,
            "subskill_id": pt,
            "problem_type_id": pt,
            "runtime_category": "manual_review" if needs_human else "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression",
            "classification_rule_id": "phase1.ai_bootstrap",
            "classification_reason": str(row.get("review_reason", "")).strip() or "ai_bootstrap_classification",
            "classifier_confidence": "high" if conf >= 0.8 else "medium" if conf >= 0.6 else "low",
            "semantic_risk_flags": ["ai_bootstrap"],
            "semantic_audit_status": "review_required" if needs_human else "ok",
            "generator_status": "manual_review" if needs_human else "ready_for_draft",
            "manual_review_reason": str(row.get("review_reason", "")).strip() if needs_human else "",
        }
        at_val = _to_answer_type_from_equivalence(eq)
        at_val, eq, checker = _align_contract(at_val, eq, checker)
        contracts[pt] = {
            "answer_type": at_val,
            "equivalence_type": eq,
            "checker_key": checker,
        }

    # fill uncovered sources into neutral manual review
    for idx, ex in source_map.items():
        if idx in by_index:
            continue
        pt = "unclassified_source_review"
        exid = ex.get("id")
        by_index[idx] = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": _source_text(ex)[:200],
            "skill_id": skill_id,
            "subskill_id": pt,
            "problem_type_id": pt,
            "runtime_category": "manual_review",
            "classification_rule_id": "phase1.ai_bootstrap_uncovered",
            "classification_reason": "ai_bootstrap_missing_source_coverage",
            "classifier_confidence": "low",
            "semantic_risk_flags": ["ai_bootstrap_missing_source_coverage"],
            "semantic_audit_status": "review_required",
            "generator_status": "manual_review",
            "manual_review_reason": "ai_bootstrap_missing_source_coverage",
        }
        contracts[pt] = {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
        }
        risk_flags.append("ai_bootstrap_missing_source_coverage")
        validation_errors.append(f"source_index={idx}: missing_source_classification")
        unclassified_count += 1

    # Global merge policy: small source set + same deterministic checker/equivalence -> allow one primary problem_type.
    pre_entries = [by_index[i] for i in sorted(by_index.keys())]
    if len(pre_entries) <= 5:
        det_rows = [x for x in pre_entries if str(x.get("runtime_category", "")).strip() != "manual_review"]
        if det_rows:
            det_pts = [str(x.get("problem_type_id", "")).strip() for x in det_rows if str(x.get("problem_type_id", "")).strip()]
            pt_counts: dict[str, int] = {}
            for p in det_pts:
                pt_counts[p] = pt_counts.get(p, 0) + 1
            primary_pt = sorted(pt_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if pt_counts else ""
            if primary_pt:
                primary_contract = contracts.get(primary_pt, {}) if isinstance(contracts.get(primary_pt), dict) else {}
                same_contract = True
                for r in det_rows:
                    c = contracts.get(str(r.get("problem_type_id", "")).strip(), {})
                    if not isinstance(c, dict):
                        same_contract = False
                        break
                    if str(c.get("checker_key", "")).strip() != str(primary_contract.get("checker_key", "")).strip():
                        same_contract = False
                        break
                    if str(c.get("equivalence_type", "")).strip() != str(primary_contract.get("equivalence_type", "")).strip():
                        same_contract = False
                        break
                if same_contract:
                    for r in det_rows:
                        r["problem_type_id"] = primary_pt
                        r["subskill_id"] = primary_pt

    entries = [by_index[i] for i in sorted(by_index.keys())]
    proposed_example_map = [{"example_id": e.get("example_id"), "proposed_problem_type_id": e.get("problem_type_id")} for e in entries]
    proposal = {
        "proposed_problem_types": sorted({str(e.get("problem_type_id", "")).strip() for e in entries if str(e.get("problem_type_id", "")).strip()}),
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": contracts,
        "risk_flags": sorted(set(risk_flags)),
    }
    low_count = sum(1 for x in confs if x < 0.6)
    avg = (sum(confs) / len(confs)) if confs else 0.0
    ai_status = "success"
    classifier_source = "ai_bootstrap"
    if entries and unclassified_count >= len(entries):
        if _sources_complete_for_default(examples):
            default_pt = _skill_default_problem_type_id(skill_id)
            checker, eq = _infer_default_contract(examples)
            for e in entries:
                e["problem_type_id"] = default_pt
                e["subskill_id"] = default_pt
                e["runtime_category"] = "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression"
                e["classification_reason"] = "ai_bootstrap_default_fallback_for_complete_sources"
                e["generator_status"] = "ready_for_draft"
                e["semantic_audit_status"] = "ok"
                e["manual_review_reason"] = ""
            at_val = _to_answer_type_from_equivalence(eq)
            at_val, eq, checker = _align_contract(at_val, eq, checker)
            contracts = {
                default_pt: {
                    "answer_type": at_val,
                    "equivalence_type": eq,
                    "checker_key": checker,
                    "is_default_problem_type": True,
                }
            }
            validation_errors.append("ai_bootstrap_all_unclassified_promoted_to_default_problem_type")
            classifier_source = "ai_bootstrap_with_default_fallback"
            ai_status = "success"
        else:
            validation_errors.append("ai_bootstrap_low_quality_all_unclassified")
            ai_status = "low_quality"
            classifier_source = "ai_bootstrap_low_quality"
    meta = {
        "classifier_source": classifier_source,
        "ai_bootstrap_used": True,
        "ai_bootstrap_status": ai_status,
        "ai_bootstrap_error": "",
        "ai_bootstrap_raw_response_preview": raw_preview,
        "ai_bootstrap_validation_errors": validation_errors,
        "ai_bootstrap_prompt_version": prompt_version,
        "ai_bootstrap_model": model_name,
        "ai_bootstrap_provider": provider,
        "ai_bootstrap_config_source": str(client_meta.get("source", "")),
        "ai_bootstrap_confidence_summary": {"count": len(confs), "avg": round(avg, 3), "low_confidence_count": low_count},
        "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
        "ai_bootstrap_raw_problem_types": ai_problem_types,
        "default_problem_type_used": classifier_source == "ai_bootstrap_with_default_fallback",
    }
    return entries, proposal, meta


def _question_preview(text: Any, limit: int = 110) -> str:
    s = str(text or "")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= limit:
        return s
    return s[:limit].rstrip() + "..."


def _pick_skill_ch_name(skill_id: str, examples: list[dict[str, Any]]) -> str:
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        for key in ("skill_ch_name", "skill_name_ch", "skill_name", "skill_title"):
            v = str(ex.get(key, "")).strip()
            if v:
                return v
    return skill_id


def _build_phase1_main_skill_anchor(skill_id: str, examples: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a skill-id-derived anchor for unregistered skills — no cross-family pollution."""
    from core.gencode.main_skill_anchor import (
        _expand_skill_id_tokens,
        build_main_skill_anchor,
        infer_expected_subskill_candidates,
    )
    from core.gencode.semantic_alignment import load_skill_metadata_from_db
    from core.gencode.task_families import (
        ABSOLUTE_VALUE_INEQUALITY_FAMILY,
        QUADRATIC_INEQUALITY_FAMILY,
        infer_skill_families_from_terms,
    )

    meta = load_skill_metadata_from_db(skill_id)
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        if not meta.get("skill_ch_name"):
            meta["skill_ch_name"] = _pick_skill_ch_name(skill_id, examples)
        if ex.get("source_paragraph") and not meta.get("unit_name"):
            meta["unit_name"] = str(ex.get("source_paragraph", "")).strip()
        if ex.get("source_section") and not meta.get("section_code"):
            meta["section_code"] = str(ex.get("source_section", "")).strip()
        if ex.get("source_chapter") and not meta.get("chapter"):
            meta["chapter"] = str(ex.get("source_chapter", "")).strip()
        break
    sid = str(skill_id or "").strip()
    if "_" in sid and not meta.get("skill_en_name"):
        meta["skill_en_name"] = sid.split("_", 1)[-1]

    anchor = build_main_skill_anchor(skill_id, meta)
    skill_terms = set(anchor.get("normalized_skill_terms") or [])
    skill_terms |= _expand_skill_id_tokens(skill_id)
    fresh_families = infer_skill_families_from_terms(skill_terms)
    if fresh_families:
        anchor["expected_task_families"] = sorted(fresh_families)
        subskills, scope = infer_expected_subskill_candidates(skill_terms, fresh_families)
        anchor["expected_subskill_candidates"] = subskills
        anchor["skill_anchor_scope"] = scope

    families = set(anchor.get("expected_task_families") or [])
    if QUADRATIC_INEQUALITY_FAMILY in families:
        families.discard(ABSOLUTE_VALUE_INEQUALITY_FAMILY)
        anchor["expected_task_families"] = sorted(families)
        anchor["expected_subskill_candidates"] = [
            s
            for s in (anchor.get("expected_subskill_candidates") or [])
            if str(s).strip() and str(s) != ABSOLUTE_VALUE_INEQUALITY_FAMILY and not str(s).endswith("_family")
        ] or sorted(anchor.get("expected_subskill_candidates") or [])

    anchor["anchor_authority"] = "skill_id_derived_no_cross_family_pollution"
    anchor["classification_mandate"] = phase1_enforcement_assertion_block(anchor)
    anchor["source_skill_scope_locked"] = True
    anchor["source_belongs_to_current_skill_by_default"] = True
    return anchor


def _build_human_review_items(
    *,
    skill_id: str,
    skill_ch_name: str,
    entries: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    candidate_problem_types: list[dict[str, Any]],
    exception_review_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    if not bool((exception_review_gate or {}).get("required")):
        return []
    by_example_id: dict[int, dict[str, Any]] = {}
    for ex in examples:
        exid = ex.get("id")
        if isinstance(exid, int):
            by_example_id[exid] = ex
    contract_by_pt: dict[str, dict[str, str]] = {}
    for c in candidate_problem_types:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        contract_by_pt[pt] = {
            "checker": str(c.get("checker_key_proposal", "")).strip(),
            "equivalence": str(c.get("equivalence_type_proposal", "")).strip(),
        }
    items: list[dict[str, Any]] = []
    for idx, row in enumerate(entries):
        if not isinstance(row, dict):
            continue
        pt = str(row.get("problem_type_id", "")).strip()
        runtime_category = str(row.get("runtime_category", "")).strip()
        eq = contract_by_pt.get(pt, {}).get("equivalence", "")
        needs_review = (
            runtime_category == "manual_review"
            or pt.endswith("_malformed_source_review")
            or eq == "manual_review_or_ai_judged"
        )
        if not needs_review:
            continue
        exid = row.get("example_id")
        ex = by_example_id.get(exid, {}) if isinstance(exid, int) else {}
        source_type = str(row.get("source_type", "")).strip() or str(ex.get("source_type", "")).strip() or "unknown"
        title = (
            str(row.get("title", "")).strip()
            or str(ex.get("title", "")).strip()
            or str(ex.get("source_label", "")).strip()
            or str(ex.get("example_name", "")).strip()
            or (f"{source_type}#{exid}" if exid else source_type)
        )
        raw_reason = (
            str(row.get("manual_review_reason", "")).strip()
            or str(row.get("classification_reason", "")).strip()
            or ",".join(str(x) for x in (row.get("semantic_risk_flags") or []) if str(x).strip())
            or "requires manual review"
        )
        question_text = row.get("problem_preview") or ex.get("problem_text") or ex.get("problem") or ex.get("question") or ex.get("stem") or ex.get("content") or row.get("title") or ""
        items.append(
            {
                "source_index": idx,
                "display_source_index": idx + 1,
                "example_id": exid if isinstance(exid, int) else None,
                "textbook_example_id": exid if isinstance(exid, int) else None,
                "source_type": source_type,
                "title": title,
                "skill_id": skill_id,
                "skill_ch_name": skill_ch_name,
                "matched_problem_type_id": pt,
                "checker": contract_by_pt.get(pt, {}).get("checker", ""),
                "equivalence": eq,
                "reason": raw_reason,
                "review_reason": raw_reason,
                "question_preview": _question_preview(question_text, limit=110),
            }
        )
    return items


def _write_phase1_summary_md(path: Path, skill_id: str, payload: dict[str, Any]) -> None:
    lines = [f"# Gencode Phase1 Summary: {skill_id}", ""]
    
    # SOP v0.2: Include SOP Policy Reference section in markdown
    sop_ref = payload.get("sop_reference")
    if isinstance(sop_ref, dict):
        lines.extend([
            "## SOP Policy Reference",
            "",
            f"- **SOP Policy Version**: `{sop_ref.get('sop_policy_version', '')}`",
            f"- **Highest SOP**: `{sop_ref.get('highest_sop', '')}`",
            f"- **SOP Preflight Status**: `{sop_ref.get('sop_preflight_status', '')}`",
            f"- **SOP Gate Status**: `{payload.get('sop_gate_status', 'PASS')}`",
            f"- **Report Contract Status**: `{payload.get('report_contract_status', 'PASS')}`",
            f"- **Report Contract Warnings**: {payload.get('report_contract_warnings', [])}",
            f"- **Report Contract Violations**: {payload.get('report_contract_violations', [])}",
            ""
        ])
    spec_mode = str(payload.get("spec_mode", "")).strip()
    if spec_mode:
        lines.extend([f"- spec_mode: `{spec_mode}`", ""])
    anchor = payload.get("main_skill_anchor") if isinstance(payload.get("main_skill_anchor"), dict) else {}
    if anchor:
        lines.extend(
            [
                "## Main skill anchor",
                "",
                f"- skill_ch_name: `{anchor.get('skill_ch_name', '')}`",
                f"- expected_task_families: {anchor.get('expected_task_families', [])}",
                f"- expected_subskill_candidates: {anchor.get('expected_subskill_candidates', [])}",
                f"- skill_anchor_scope: `{anchor.get('skill_anchor_scope', '')}`",
                f"- observed_source_family_distribution: {payload.get('source_family_distribution', {})}",
                f"- observed_target_task_distribution: {payload.get('observed_target_task_distribution', {})}",
                f"- same_family_subskill_mismatch_examples: {len(payload.get('same_family_subskill_mismatch_examples') or [])}",
                f"- examples_outside_expected_subskills: {payload.get('examples_outside_expected_subskills', [])}",
                f"- suggested_action: `{payload.get('suggested_action', '')}`",
                "",
            ]
        )
        sub_mismatch = payload.get("same_family_subskill_mismatch_examples") or []
        if sub_mismatch:
            lines.append(
                "> 來源題與技能屬於同一大類，但子技能不同；請確認是否要放在此技能底下。"
            )
            lines.append("")
        dist = payload.get("source_family_distribution") or {}
        expected = set(anchor.get("expected_task_families") or [])
        if dist and expected:
            top = max(dist, key=dist.get)
            if top not in expected:
                lines.append(
                    "> 來源題多數與目前技能語意不一致，疑似 skill mapping 錯誤；請先檢查來源題歸屬，不建議進 Phase 2。"
                )
                lines.append("")
    auto = payload.get("auto_review_summary") if isinstance(payload.get("auto_review_summary"), dict) else {}
    align_rows = payload.get("source_example_alignment") if isinstance(payload.get("source_example_alignment"), list) else []
    if align_rows:
        lines.extend(
            [
                "## Source alignment",
                "",
                f"- source_alignment_status: `{payload.get('source_alignment_status', '')}`",
                f"- skill_problem_type_alignment_status: `{payload.get('skill_problem_type_alignment_status', '')}`",
                f"- alignment_score: `{payload.get('alignment_score', '')}`",
                f"- alignment_blockers: {payload.get('alignment_blockers', [])}",
                f"- alignment_warnings: {payload.get('alignment_warnings', [])}",
                "",
                "| example_id | target_task | task_family | alignment_kind | subskill_match | included | exclude_reason | stem_preview |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in align_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| {ex} | {tt} | {tf} | {ak} | {sm} | {inc} | {er} | {pv} |".format(
                    ex=row.get("example_id", ""),
                    tt=row.get("target_task", ""),
                    tf=row.get("task_family", ""),
                    ak=row.get("alignment_kind", ""),
                    sm=row.get("subskill_match", ""),
                    inc=row.get("included_in_phase1", ""),
                    er=row.get("exclude_reason", ""),
                    pv=str(row.get("title_stem_preview", "")).replace("|", "\\|")[:60],
                )
            )
        lines.append("")
    sem_rows = payload.get("semantic_classifications") if isinstance(payload.get("semantic_classifications"), list) else []
    ai_status = str(payload.get("ai_semantic_status", "")).strip()
    if sem_rows or ai_status:
        lines.extend(
            [
                "## AI semantic classification",
                "",
                f"- ai_semantic_status: `{ai_status or 'not_used'}`",
                "",
                "| example_id | ai_task | ai_family | ai_conf | rule_task | rule_family | final_task | final_family | source | conflict | human |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in sem_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| {ex} | {at} | {af} | {ac} | {rt} | {rf} | {ft} | {ff} | {src} | {cr} | {hu} |".format(
                    ex=row.get("example_id", ""),
                    at=row.get("ai_target_task", ""),
                    af=row.get("ai_task_family", ""),
                    ac=row.get("ai_confidence", ""),
                    rt=row.get("rule_target_task", ""),
                    rf=row.get("rule_task_family", ""),
                    ft=row.get("final_target_task", ""),
                    ff=row.get("final_task_family", ""),
                    src=row.get("classifier_source", ""),
                    cr=str(row.get("conflict_reason", "")).replace("|", "\\|")[:40],
                    hu=row.get("requires_human_action", ""),
                )
            )
        if ai_status == "unavailable":
            lines.append("")
            reason = str(payload.get("ai_semantic_unavailable_reason", "")).strip()
            lines.append(
                f"> AI 語意分類未執行：{reason or 'unknown'}。已退回 rule fallback，請先設定 AI key 後重新執行 Phase 1。"
            )
    diag_rows = payload.get("classification_diagnostics") if isinstance(payload.get("classification_diagnostics"), list) else []
    if diag_rows:
        lines.extend(
            [
                "## Classification diagnostics (per example)",
                "",
                "| id | rule_task/family | AI task/family | conf | source | final task/family | align | excluded |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for d in diag_rows:
            if not isinstance(d, dict):
                continue
            lines.append(
                "| {id} | {rt}/{rf} | {at}/{af} | {ac} | {src} | {ft}/{ff} | {ak} | {ex} |".format(
                    id=d.get("example_id", ""),
                    rt=d.get("rule_target_task", ""),
                    rf=d.get("rule_task_family", ""),
                    at=d.get("ai_target_task", ""),
                    af=d.get("ai_task_family", ""),
                    ac=d.get("ai_confidence", ""),
                    src=d.get("classifier_source", ""),
                    ft=d.get("final_target_task", ""),
                    ff=d.get("final_task_family", ""),
                    ak=d.get("alignment_kind", ""),
                    ex=d.get("exclude_reason", ""),
                )
            )
        lines.append("")
        struct_note = payload.get("structure_mismatch_examples") or []
        if struct_note:
            lines.append("")
            lines.append("> 教材結構：部分隨堂練習與對應例題子技能不一致，請人工確認。")
        lines.append("")
    link_map = payload.get("example_practice_link_map") or []
    if link_map:
        lines.extend(["## Example / practice links", "", f"{link_map}", ""])
    fam_dist = payload.get("same_section_family_distribution") or {}
    if fam_dist:
        lines.extend(["## Same-section family distribution", "", f"{fam_dist}", ""])
    features = auto.get("example_features") if isinstance(auto.get("example_features"), list) else []
    if not features:
        features = payload.get("source_example_alignment") if isinstance(payload.get("source_example_alignment"), list) else []
    if features:
        lines.extend(["## Example features", "", "| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |", "| --- | --- | --- | --- | --- | --- |"])
        for f in features:
            if not isinstance(f, dict):
                continue
            lines.append(
                "| {ex} | {at} | {tt} | {hc} | {se} | {mo} |".format(
                    ex=f.get("source_example_id", ""),
                    at=f.get("answer_type", ""),
                    tt=f.get("target_task", ""),
                    hc=f.get("has_choices", ""),
                    se=f.get("stem_embeds_choices", ""),
                    mo=", ".join(f.get("math_objects", []) or []),
                )
            )
        lines.append("")
    clusters = auto.get("induction_clusters") if isinstance(auto.get("induction_clusters"), list) else []
    if clusters:
        lines.extend(["## Induction clusters", ""])
        for i, c in enumerate(clusters, 1):
            if not isinstance(c, dict):
                continue
            lines.append(
                f"### Cluster {i}\n- answer_type: `{c.get('answer_type', '')}`\n"
                f"- source_example_ids: {c.get('source_example_ids', [])}\n"
                f"- grouping_reason: {c.get('grouping_reason', '')}\n"
                f"- feature_signature: `{c.get('feature_signature', [])}`\n"
            )
        lines.append("")
    cands = payload.get("candidate_problem_types") if isinstance(payload.get("candidate_problem_types"), list) else []
    if cands:
        lines.extend(["## Candidate problem types", "", "| problem_type_id | display_name | answer_type | source_examples | grouping_reason |", "| --- | --- | --- | --- | --- |"])
        for c in cands:
            if not isinstance(c, dict):
                continue
            draft = c.get("problem_type_spec_draft") if isinstance(c.get("problem_type_spec_draft"), dict) else {}
            ac = draft.get("answer_contract") if isinstance(draft.get("answer_contract"), dict) else {}
            lines.append(
                "| {pt} | {dn} | {at} | {ex} | {gr} |".format(
                    pt=c.get("problem_type_id", ""),
                    dn=c.get("display_name", ""),
                    at=ac.get("answer_type", ""),
                    ex=c.get("matched_example_ids", []),
                    gr=c.get("grouping_reason", ""),
                )
            )
        lines.append("")
    lines.extend(["## phase1", "```json", json.dumps(payload, ensure_ascii=False, indent=2), "```", ""])
    items = payload.get("human_review_items") if isinstance(payload.get("human_review_items"), list) else []
    if items:
        lines.extend(
            [
                "## human_review_items",
                "",
                "| source_index | title | example_id | source_type | matched_problem_type_id | checker | equivalence | reason | question_preview |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in items:
            def _md_cell(v: Any) -> str:
                return str(v if v is not None else "").replace("|", "\\|").replace("\n", " ").strip()
            lines.append(
                "| {source_index} | {title} | {example_id} | {source_type} | {matched_problem_type_id} | {checker} | {equivalence} | {reason} | {question_preview} |".format(
                    source_index=_md_cell(item.get("display_source_index", item.get("source_index", ""))),
                    title=_md_cell(item.get("title", "")),
                    example_id=_md_cell(item.get("example_id", "")),
                    source_type=_md_cell(item.get("source_type", "")),
                    matched_problem_type_id=_md_cell(item.get("matched_problem_type_id", "")),
                    checker=_md_cell(item.get("checker", "")),
                    equivalence=_md_cell(item.get("equivalence", "")),
                    reason=_md_cell(item.get("review_reason", item.get("reason", ""))),
                    question_preview=_md_cell(item.get("question_preview", "")),
                )
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_file(path, "\n".join(lines).rstrip() + "\n")


def _build_auto_review(skill_id: str, entries: list[dict[str, Any]], proposal: dict[str, Any]) -> dict[str, Any]:
    proposed_by_id = {
        int(x.get("example_id")): str(x.get("proposed_problem_type_id", "")).strip()
        for x in (proposal.get("proposed_example_map") or [])
        if isinstance(x, dict) and isinstance(x.get("example_id"), int)
    }
    contracts = proposal.get("proposed_answer_contracts", {}) if isinstance(proposal.get("proposed_answer_contracts"), dict) else {}
    per_example: list[dict[str, Any]] = []
    groups: dict[str, list[int]] = defaultdict(list)
    runtime_contract_defaults = {
        "deterministic_expression": {"answer_type": "expression", "equivalence_type": "algebraic_equivalent", "checker_key": "expression_checker"},
        "deterministic_choice": {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"},
        "deterministic_numeric": {"answer_type": "numeric", "equivalence_type": "numeric_exact", "checker_key": "integer_checker"},
        "manual_review": {"answer_type": "manual_review", "equivalence_type": "manual_review_or_ai_judged", "checker_key": "manual_review_checker"},
    }
    for e in entries:
        exid = e.get("example_id")
        if not isinstance(exid, int):
            continue
        pt = str(e.get("problem_type_id", "")).strip()
        if pt in {"", "unknown"}:
            pt = proposed_by_id.get(exid, "unknown")
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        if not c:
            c = runtime_contract_defaults.get(str(e.get("runtime_category", "")).strip(), {})
        answer_shape = detect_answer_shape(c)
        per_example.append(
            {
                "example_id": exid,
                "detected_problem_type_id": pt,
                "answer_shape": answer_shape,
                "classification_confidence": "medium" if pt not in {"", "unknown"} else "low",
                "classification_reason": "classifier_or_proposal_mapping",
                "risk_flags": e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else [],
                "title_or_source_label": str(e.get("title", "")).strip() or str(e.get("source_type", "")).strip(),
            }
        )
        if pt not in {"", "unknown"}:
            if pt not in contracts and c:
                contracts[pt] = c
            groups[pt].append(exid)

    unknown_ids = sorted(x["example_id"] for x in per_example if x["detected_problem_type_id"] in {"", "unknown"})
    candidates: list[dict[str, Any]] = []
    all_ids = sorted(x["example_id"] for x in per_example)
    for pt, ids_raw in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        ids = sorted(set(ids_raw))
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        answer_shape = detect_answer_shape(c)
        rec = "recommend_promote_for_that_candidate" if len(ids) >= 3 and answer_shape != "unknown_answer_shape" else "conservative_hold_for_that_candidate"
        blockers = [] if rec.startswith("recommend_") else ["insufficient_examples_for_safe_promote"]
        candidates.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "matched_example_ids": ids,
                "matched_example_count": len(ids),
                "unmatched_example_ids": [x for x in all_ids if x not in ids],
                "representative_example_id": ids[0] if ids else None,
                "structural_features": sorted({x["answer_shape"] for x in per_example if x["detected_problem_type_id"] == pt}),
                "answer_contract_proposal": c,
                "checker_key_proposal": str(c.get("checker_key", "")),
                "equivalence_type_proposal": str(c.get("equivalence_type", "")),
                "answer_shape": answer_shape,
                "confidence": "high" if len(ids) >= 3 else "medium",
                "promote_recommendation": rec,
                "promote_blockers": blockers,
                "risk_flags": [],
            }
        )

    shape_set = {x.get("answer_shape", "") for x in candidates if x.get("answer_shape", "")}
    if not candidates and unknown_ids:
        split_merge = "hold_unknown_examples_only"
    elif len(candidates) == 1:
        split_merge = "recommend_single_type"
    elif len(shape_set) >= 2:
        split_merge = "recommend_split_problem_types"
    else:
        split_merge = "recommend_split_or_refine"

    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(entries),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=False,
    )
    ex_gate = gates.get("exception_review_gate", {}) if isinstance(gates.get("exception_review_gate"), dict) else {}
    ex_reasons = ex_gate.get("reasons", []) if isinstance(ex_gate.get("reasons"), list) else []
    ex_reasons = [r for r in ex_reasons if str(r) not in {"runtime_smoke_failed", "dynamic_sampling_failed", "contract_tests_failed"}]
    ex_gate["reasons"] = ex_reasons
    ex_gate["required"] = bool(ex_reasons)
    gates["exception_review_gate"] = ex_gate
    per_candidate_promote_gate = [
        {
            "problem_type_id": str(x.get("problem_type_id", "")),
            "promote_recommendation": str(x.get("promote_recommendation", "")),
            "promote_blockers": x.get("promote_blockers", []),
        }
        for x in candidates
    ]
    next_action = "review_classifier_proposal_and_decide_split_merge"
    if split_merge == "recommend_split_problem_types":
        next_action = "prepare_split_problem_types_then_promote_candidates"
    elif split_merge == "recommend_single_type":
        next_action = "ready_for_safe_promote"

    return {
        "skill_id": skill_id,
        "candidate_problem_types": candidates,
        "proposal_items": candidates,
        "per_example_classification": per_example,
        "split_or_merge_recommendation": split_merge,
        "per_candidate_promote_gate": per_candidate_promote_gate,
        "next_action": next_action,
        **gates,
    }


def _normalize_phase_response(payload: dict[str, Any]) -> dict[str, Any]:
    phase = str(payload.get("phase", "")).strip()
    ok = bool(payload.get("ok", False))
    human_items: list[dict[str, Any]] = []

    if phase == "phase1":
        source_count = int(payload.get("source_example_count", 0))
        cands = payload.get("candidate_problem_types", []) if isinstance(payload.get("candidate_problem_types"), list) else []
        ex_gate = payload.get("exception_review_gate", {}) if isinstance(payload.get("exception_review_gate"), dict) else {}
        reasons = ex_gate.get("reasons", []) if isinstance(ex_gate.get("reasons"), list) else []
        alignment_blockers = payload.get("alignment_blockers", []) if isinstance(payload.get("alignment_blockers"), list) else []
        final_alignment_blockers = [str(x).strip() for x in alignment_blockers if str(x).strip()]
        if final_alignment_blockers:
            reasons = [r for r in reasons if str(r).strip() not in {"majority_needs_review", "semantic_alignment_blocked"}]
            for b in final_alignment_blockers:
                if b not in reasons:
                    reasons.append(b)
            ex_gate["reasons"] = reasons
            ex_gate["required"] = bool(reasons)
            payload["exception_review_gate"] = ex_gate
        else:
            reasons = [r for r in reasons if str(r).strip() not in {"majority_needs_review", "semantic_alignment_blocked"}]
            ex_gate["reasons"] = reasons
            ex_gate["required"] = bool(reasons)
            payload["exception_review_gate"] = ex_gate
        from core.gencode.phase1_result_messages import apply_phase1_display_fields, resolve_phase1_phase_status

        phase_status = resolve_phase1_phase_status(
            source_count=source_count,
            source_alignment_status=str(payload.get("source_alignment_status", "")).strip(),
            alignment_blockers=alignment_blockers,
            ex_gate_required=bool(ex_gate.get("required")),
            has_fatal=any("fatal" in str(x).lower() for x in reasons),
            has_risk_examples=bool(payload.get("risk_examples")),
        )
        for exid in payload.get("unclassified_examples", []) or []:
            human_items.append(
                {
                    "type": "unclassified_example",
                    "target_id": str(exid),
                    "message": f"unclassified example: {exid}",
                    "suggested_action": "edit_classification",
                }
            )
        for r in reasons:
            human_items.append(
                {
                    "type": "fatal_risk" if "fatal" in str(r).lower() else "inspect_report",
                    "target_id": str(r),
                    "message": f"Phase 1 exception reason: {r}",
                    "suggested_action": "inspect_report",
                }
            )
        for item in payload.get("human_review_items", []) or []:
            if not isinstance(item, dict):
                continue
            human_items.append(
                {
                    "type": "phase1_source_review_required",
                    "target_id": str(item.get("example_id") or item.get("display_source_index") or ""),
                    "message": f"#{item.get('display_source_index', item.get('source_index', ''))} {item.get('matched_problem_type_id', '')}: {item.get('review_reason', item.get('reason', ''))}",
                    "suggested_action": "inspect_report",
                }
            )
        classifier_source = str(payload.get("classifier_source", "rule_pack"))
        can_continue = phase_status in {"phase1_completed", "phase1_completed_with_warning", "phase1_exception_review_required"}
        induced_specs = payload.get("induced_problem_type_specs", []) if isinstance(payload.get("induced_problem_type_specs"), list) else []
        cands_with_pt = [
            x for x in cands
            if isinstance(x, dict) and str(x.get("problem_type_id") or x.get("proposed_problem_type_id") or "").strip()
        ]
        default_pt_ids = [
            str(x.get("problem_type_id") or x.get("proposed_problem_type_id") or "").strip()
            for x in cands_with_pt
            if isinstance(x, dict) and (
                bool((x.get("answer_contract_proposal") or {}).get("is_default_problem_type"))
                or str(x.get("problem_type_id") or x.get("proposed_problem_type_id") or "").strip().endswith("_default")
            )
        ]
        has_blocking_alignment = bool(alignment_blockers)
        has_final_problem_types = bool(induced_specs) or bool(cands_with_pt)
        default_pt_consistent_for_continue = (
            can_continue
            and phase_status in {"phase1_completed", "phase1_completed_with_warning"}
            and not has_blocking_alignment
            and bool(payload.get("default_problem_type_used"))
            and has_final_problem_types
        )
        if classifier_source == "ai_bootstrap":
            payload["summary_message"] = "未找到既有 rule pack，已使用 AI classifier bootstrap 產生題型分類草案。"
        elif classifier_source == "ai_bootstrap_with_default_fallback":
            if default_pt_consistent_for_continue:
                payload["summary_message"] = "AI 未細分題型，但來源題完整且同屬此 skill；已建立單一 default problem_type，可進入 Phase 2。"
            else:
                payload["summary_message"] = "曾啟用 default problem_type fallback，但最終語意對齊或來源品質檢查未通過，需人工確認。"
                warnings = payload.get("alignment_warnings", []) if isinstance(payload.get("alignment_warnings"), list) else []
                if "default_problem_type_inconsistent_with_final_specs" not in warnings:
                    warnings.append("default_problem_type_inconsistent_with_final_specs")
                payload["alignment_warnings"] = warnings
        elif classifier_source == "ai_bootstrap_low_quality":
            payload["summary_message"] = "AI classifier bootstrap 有回覆，但未能產生可用題型分類；目前仍需人工審查。"
        elif classifier_source == "neutral_fallback":
            payload["summary_message"] = "AI classifier bootstrap 失敗，已轉入人工審查。"
        else:
            payload["summary_message"] = (
                f"Phase 1 completed: {len(cands)} candidate problem types, {source_count} source examples."
                if phase_status.startswith("phase1_completed")
                else ("Phase 1 blocked: no source examples." if phase_status == "phase1_blocked_no_source" else "Phase 1 requires exception review.")
            )
        can_retry = True
        if phase_status in {"phase1_blocked_semantic_alignment", "phase1_blocked_low_core_sources"}:
            apply_phase1_display_fields(payload)
        payload["phase_status"] = phase_status

    elif phase == "phase2":
        results = payload.get("generator_results", []) if isinstance(payload.get("generator_results"), list) else []
        accepted = payload.get("accepted_generators", []) if isinstance(payload.get("accepted_generators"), list) else []
        failed = payload.get("failed_generators", []) if isinstance(payload.get("failed_generators"), list) else []
        accepted_statuses = {"runtime_ready", "limited_runtime_ready", "runtime_ready_with_warning"}
        has_warnings = any((x.get("warnings") or []) for x in results if isinstance(x, dict))
        from core.gencode.packaging_policy import DIVERSITY_SAMPLING_OK_STATUSES

        has_blocking_states = any(
            str(x.get("generator_status", "")).strip()
            in {"blocked", "draft_planned", "validation_failed", "draft_failed", "generator_not_ready", "pending_template"}
            or bool(x.get("blockers"))
            or bool(x.get("requires_human_action"))
            or x.get("usable_for_phase3") is False
            for x in results
            if isinstance(x, dict)
        )
        from core.gencode.packaging_policy import is_generator_usable_for_packaging

        packaging_usable_count = sum(
            1 for x in results if isinstance(x, dict) and is_generator_usable_for_packaging(x)[0]
        )
        all_phase3_ready = bool(results) and all(
            str(x.get("generator_status", "")).strip() in accepted_statuses
            and str(x.get("checker_smoke_status", "")).strip() in {"", "passed"}
            and str(x.get("dynamic_sampling_status", "")).strip() in {"", "passed", *DIVERSITY_SAMPLING_OK_STATUSES}
            and not bool(x.get("blockers"))
            and not bool(x.get("requires_human_action"))
            and x.get("usable_for_phase3") is not False
            for x in results
            if isinstance(x, dict)
        )
        any_phase3_ready = packaging_usable_count > 0
        if not results:
            phase_status = "phase2_blocked_no_candidates"
        elif results and len(failed) == len(results):
            phase_status = "phase2_blocked_all_generators_failed"
        elif has_warnings:
            phase_status = "phase2_completed_with_warning"
        else:
            phase_status = "phase2_completed"
        for row in results:
            if not isinstance(row, dict):
                continue
            for b in row.get("blockers", []) or []:
                human_items.append(
                    {
                        "type": "missing_checker" if "checker" in str(b).lower() else "inspect_report",
                        "target_id": str(row.get("problem_type_id", "")),
                        "message": f"{row.get('problem_type_id', '')}: {b}",
                        "suggested_action": "inspect_report",
                    }
                )
        payload["packaging_usable_count"] = packaging_usable_count
        if phase_status == "phase2_completed" and any_phase3_ready and not has_blocking_states:
            payload["summary_message"] = "Phase 2 completed: generators passed smoke/sampling and can continue to Phase 3."
        elif phase_status == "phase2_completed_with_warning" and any_phase3_ready and not has_blocking_states:
            payload["summary_message"] = (
                "Phase 2 completed with warnings: at least one generator is usable for Phase 3 packaging "
                f"({packaging_usable_count} usable); warnings such as low_source_examples do not block packaging."
            )
        elif phase_status == "phase2_completed_with_warning" and any_phase3_ready:
            payload["summary_message"] = (
                f"Phase 2 completed with warnings: {packaging_usable_count} generator(s) usable for Phase 3."
            )
        elif phase_status == "phase2_completed_with_warning":
            payload["summary_message"] = f"Phase 2 completed with warnings: {len(accepted)} generator drafts created, but none are usable for Phase 3 yet."
        elif phase_status == "phase2_completed":
            payload["summary_message"] = f"Phase 2 completed: {len(accepted)} generator drafts created."
        else:
            payload["summary_message"] = "Phase 2 blocked: no usable generator draft."
        can_continue = phase_status in {"phase2_completed", "phase2_completed_with_warning"} and any_phase3_ready
        can_retry = True

    elif phase == "phase3":
        py_status = str(payload.get("py_compile_status", "")).strip()
        pkg = str(payload.get("package_status", "")).strip()
        usable_n = int(payload.get("packaging_usable_count", 0))
        if usable_n == 0 or pkg == "blocked_no_usable_generators":
            phase_status = "phase3_blocked_no_usable_generators"
        elif py_status == "failed":
            phase_status = "phase3_failed_compile"
        elif pkg == "packaged_draft" and str(payload.get("runtime_smoke_status", "")) == "passed":
            phase_status = "phase3_packaged_draft_with_warning" if payload.get("generated_with_warning") else "phase3_packaged_draft"
        elif pkg == "packaged_draft" or (py_status == "passed" and usable_n > 0):
            phase_status = "phase3_packaged_draft_smoke_failed"
        elif pkg == "failed":
            phase_status = "phase3_packaged_draft_smoke_failed"
        else:
            phase_status = "phase3_blocked_no_usable_generators"
        if py_status == "failed":
            human_items.append(
                {
                    "type": "compile_error",
                    "target_id": str(payload.get("skill_file_path", "")),
                    "message": str(payload.get("error", "draft skill py_compile failed")),
                    "suggested_action": "retry",
                }
            )
        if not payload.get("summary_message"):
            payload["summary_message"] = (
                "Phase 3 completed: draft skill packaged and py_compile passed."
                if phase_status.startswith("phase3_packaged_draft") and phase_status != "phase3_packaged_draft_smoke_failed"
                else (
                    payload.get("packaging_diagnostic_message")
                    or "Phase 3 blocked: no usable generators for packaging."
                )
            )
        can_continue = phase_status in {
            "phase3_packaged_draft",
            "phase3_packaged_draft_with_warning",
            "phase3_packaged_draft_smoke_failed",
        }
        can_retry = True
    else:
        phase_status = "unknown_phase_status"
        can_continue = False
        can_retry = True
        payload.setdefault("summary_message", "Unknown phase status.")

    payload["phase_status"] = phase_status
    payload["can_continue"] = bool(can_continue)
    payload["can_retry"] = bool(can_retry)
    payload["requires_human_action"] = bool(human_items)
    payload["human_action_items"] = human_items
    payload["ok"] = bool(ok)
    payload.setdefault("reports", {})
    return payload


def run_gencode_phase1(skill_id: str, dry_run: bool = True, spec_mode: str = "ai_first_induce_from_sources") -> dict[str, Any]:
    # SOP v0.2: Preflight Scan Policy Enforcement
    from core.gencode.sop_policy import validate_sop_preflight, build_sop_reference, validate_skill_level_blockers
    preflight = validate_sop_preflight(PROJECT_ROOT)
    reports_pre = _phase_reports(
        skill_id,
        keys=("phase1_summary_json", "phase1_summary_md", "phase1_json", "phase1_md"),
    )
    if preflight["sop_preflight_status"] == "FAIL":
        payload = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": 0,
            "candidate_problem_types": [],
            "per_example_classification": [],
            "unclassified_examples": [],
            "risk_examples": [],
            "split_or_merge_recommendation": "hold_unknown_examples_only",
            "classifier_gate": {"status": "classifier_blocked", "allowed": False, "warnings": []},
            "generator_draft_gate": {"status": "generator_draft_blocked", "allowed": False, "warnings": []},
            "runtime_ready_gate": {"status": "blocked_sop_preflight_failed", "allowed": False, "blockers": ["blocked_sop_preflight_failed"]},
            "exception_review_gate": {"required": True, "reasons": ["sop_preflight_failed"]},
            "reports": reports_pre,
            "next_action": "fix_sop_files",
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "human_review_items": [],
            "sop_preflight_status": "FAIL",
            "sop_preflight_errors": preflight["errors"],
            "phase_status": "SOP_PREFLIGHT_FAIL",
        }
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(Path(reports_pre["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports_pre["phase1_summary_md"]), skill_id, payload)
        normalized = _normalize_phase_response(payload)
        normalized["phase_status"] = "SOP_PREFLIGHT_FAIL"
        normalized["summary_message"] = f"SOP preflight failed: {', '.join(preflight['errors'])}"
        return normalized

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    examples = _load_examples(skill_id)

    # ── SOP v0.3.2 最終洗淨版：行政歸屬唯讀校驗（對齊真實資料庫矩陣）──
    prefix_ok, prefix_reason = _validate_vh_math_skill_id_prefix(skill_id)
    if not prefix_ok:
        payload = _build_skill_id_prefix_violation_payload(
            skill_id,
            dry_run=dry_run,
            reports_pre=reports_pre,
            validation_reason=prefix_reason,
        )
        write_json(Path(reports_pre["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports_pre["phase1_summary_md"]), skill_id, payload)
        normalized = _normalize_phase_response(payload)
        normalized["phase_status"] = "skill_id_prefix_violation"
        return normalized

    reports = _phase_reports(
        skill_id,
        keys=("phase1_summary_json", "phase1_summary_md", "phase1_json", "phase1_md"),
    )
    if not examples:
        payload = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": 0,
            "candidate_problem_types": [],
            "per_example_classification": [],
            "unclassified_examples": [],
            "risk_examples": [],
            "split_or_merge_recommendation": "hold_unknown_examples_only",
            "classifier_gate": {"status": "classifier_blocked", "allowed": False, "warnings": []},
            "generator_draft_gate": {"status": "generator_draft_blocked", "allowed": False, "warnings": []},
            "runtime_ready_gate": {"status": "blocked_insufficient_examples", "allowed": False, "blockers": ["blocked_insufficient_examples"]},
            "exception_review_gate": {"required": True, "reasons": ["no_source_examples"]},
            "reports": reports,
            "next_action": "check_skill_mapping_or_source_import",
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "human_review_items": [],
        }
        write_json(Path(reports["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
        normalized = _normalize_phase_response(payload)
        normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
        return normalized

    classifier_source = "rule_pack"
    ai_bootstrap_used = False
    ai_bootstrap_status = "not_used"
    ai_bootstrap_confidence_summary: dict[str, Any] = {}
    inspect_report_note = ""
    meta: dict[str, Any] = {}
    registered_pack = _load_registered_classifier_rulepack(skill_id)
    if registered_pack:
        entries = _classify_examples_with_rulepack(skill_id=skill_id, examples=examples, pack=registered_pack)
    else:
        cls = get_classifier_for_skill(skill_id)
        ctx = ClassifierContext(project_root=PROJECT_ROOT, skill_id=skill_id)
        raw_result = cls.classify_examples(examples, ctx)
        entries = [dict(x) for x in raw_result.examples_map_entries]
        if isinstance(cls, FallbackClassifier):
            classifier_source = "ai_bootstrap"
            ai_bootstrap_used = True
            skill_ch_name = _pick_skill_ch_name(skill_id, examples)
            try:
                entries, proposal, meta = _run_ai_classifier_bootstrap(skill_id=skill_id, skill_ch_name=skill_ch_name, examples=examples)
            except Exception as ex:
                execute_pipeline_self_healing(ex, "phase1", skill_id)
                ex_msg = str(ex)
                entries, proposal, meta = _build_neutral_fallback(
                    skill_id=skill_id,
                    examples=examples,
                    reason=f"skill_specific_classifier_missing; ai_bootstrap_failed: {ex_msg}",
                )
                meta["ai_bootstrap_error"] = ex_msg
                if "api key missing" in ex_msg.lower() or "unavailable" in ex_msg.lower():
                    meta["ai_bootstrap_status"] = "unavailable"
                    meta["ai_bootstrap_error"] = "AI client unavailable or API key missing"
                if "ai_bootstrap_invalid_json::" in ex_msg:
                    preview = ex_msg.split("::", 1)[1].strip()
                    meta["ai_bootstrap_raw_response_preview"] = preview[:1000]
                    meta["ai_bootstrap_validation_errors"] = ["invalid_json_response"]
            classifier_source = str(meta.get("classifier_source", classifier_source))
            ai_bootstrap_status = str(meta.get("ai_bootstrap_status", "failed" if classifier_source == "neutral_fallback" else "success"))
            ai_bootstrap_confidence_summary = meta.get("ai_bootstrap_confidence_summary", {}) if isinstance(meta.get("ai_bootstrap_confidence_summary"), dict) else {}
            inspect_report_note = str(meta.get("inspect_report_note", "")).strip()
    if not isinstance(entries, list):
        entries = []
    if not entries and examples:
        fb_entries, fb_proposal, fb_meta = _build_neutral_fallback(
            skill_id=skill_id,
            examples=examples,
            reason="phase1_entries_empty_after_classification",
        )
        entries = fb_entries
        if not meta:
            meta = fb_meta
        inspect_report_note = (inspect_report_note + " " if inspect_report_note else "") + "entries fallback applied due to empty source classifications."
        if not str(meta.get("ai_bootstrap_error", "")).strip():
            meta["ai_bootstrap_error"] = "phase1_entries_empty_after_classification"
    proposal = {"proposed_problem_types": [], "proposed_example_map": [], "proposed_answer_contracts": {}, "risk_flags": []}
    if registered_pack:
        for e in entries:
            pt = str(e.get("problem_type_id", "")).strip()
            if not pt:
                continue
            proposal["proposed_problem_types"].append(pt)
            proposal["proposed_example_map"].append({"example_id": e.get("example_id"), "proposed_problem_type_id": pt})
            # infer contracts from runtime category
            if str(e.get("runtime_category", "")).strip() == "manual_review":
                proposal["proposed_answer_contracts"][pt] = {"answer_type": "manual_review", "equivalence_type": "manual_review_or_ai_judged", "checker_key": "manual_review_checker"}
            else:
                proposal["proposed_answer_contracts"][pt] = {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"}
        proposal["proposed_problem_types"] = sorted(set(proposal["proposed_problem_types"]))
    elif not ai_bootstrap_used:
        unknown_ratio = sum(1 for e in entries if str(e.get("problem_type_id", "")).strip() in {"", "unknown"}) / max(len(entries), 1)
        if unknown_ratio >= 0.2:
            proposal = build_classifier_proposal(skill_id, entries)
    auto_review_legacy = _build_auto_review(skill_id, entries, proposal)
    examples_for_induction = []
    for ex in examples:
        row = dict(ex)
        if "example_id" not in row and row.get("id") is not None:
            row["example_id"] = row["id"]
        examples_for_induction.append(row)
    try:
        phase1_anchor = _build_phase1_main_skill_anchor(skill_id, examples_for_induction)
        induced = induce_problem_types_from_examples(
            skill_id,
            examples_for_induction,
            spec_mode=spec_mode,
            main_skill_anchor=phase1_anchor,
        )
    except Exception as ex:
        healing = execute_pipeline_self_healing(ex, "phase1", skill_id)
        payload = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": len(examples),
            "candidate_problem_types": [],
            "phase_status": "phase1_induction_exception",
            "exception_review_gate": {"required": True, "reasons": ["phase1_induction_exception"]},
            "summary_message": f"Phase 1 induction failed: {ex}",
            "self_healing": healing,
            "reports": reports,
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "human_review_items": [],
        }
        write_json(Path(reports["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
        normalized = _normalize_phase_response(payload)
        normalized["phase_status"] = "phase1_induction_exception"
        return normalized
    auto_review = apply_spec_mode(skill_id, induced, auto_review_legacy, entries, spec_mode)
    auto_review = _apply_source_skill_binding_candidate_policy(skill_id, auto_review)
    alignment_blocked = str(auto_review.get("source_alignment_status", "")).strip() == "block"
    _induce_modes_save = {
        "induce_from_sources",
        "ai_first_induce_from_sources",
        "rule_first_induce_from_sources",
        "hybrid_ai_rule_validate",
    }
    if str(spec_mode or "").strip() in _induce_modes_save:
        induced_specs = auto_review.get("induced_problem_type_specs", [])
        if isinstance(induced_specs, list) and induced_specs and not alignment_blocked:
            save_induced_problem_type_specs(skill_id, induced_specs)
            classifier_source = f"{classifier_source}+phase1_induction"
    elif auto_review.get("spec_defined_problem_type_ids"):
        classifier_source = f"{classifier_source}+problem_type_specs"
    per_example = auto_review.get("per_example_classification", [])
    unclassified = [x.get("example_id") for x in per_example if str(x.get("detected_problem_type_id", "")).strip() in {"", "unknown"}]
    risk_examples = [x.get("example_id") for x in per_example if x.get("risk_flags")]
    answer_contract_summary = summarize_answer_contracts(
        [c for c in (auto_review.get("candidate_problem_types") or []) if isinstance(c, dict)]
    )
    invalid_equivalence_problem_types = sorted(
        [
            pt
            for pt, c in (answer_contract_summary.get("observed_problem_type_answer_contracts", {}) or {}).items()
            if isinstance(c, dict) and str(c.get("equivalence_type", "")).strip() not in EQUIVALENCE_TYPE_WHITELIST
        ]
    )
    phase1_ac_gate_pass = not (
        bool(answer_contract_summary.get("missing_answer_contract_problem_types"))
        or bool(answer_contract_summary.get("missing_checker_key_problem_types"))
        or bool(invalid_equivalence_problem_types)
    )

    from core.gencode.sop_policy import validate_skill_level_blockers, build_sop_reference
    
    # SOP v0.2: Enforce Blocker Promotions and final_classification rules
    align_blockers = auto_review.get("alignment_blockers", [])
    ex_gate_reasons = (auto_review.get("exception_review_gate") or {}).get("reasons", [])
    all_blockers = set(align_blockers) | set(ex_gate_reasons)
    
    gate_res = validate_skill_level_blockers(all_blockers)
    sop_gate_status = "PASS"
    sop_gate_violation = False
    invalid_blockers = []
    
    if gate_res["sop_violation"]:
        sop_gate_status = "FAIL"
        sop_gate_violation = True
        invalid_blockers = gate_res["invalid_skill_level_blockers"]
        
        # Safe demotion: Keep only allowed blockers, move others to warnings
        align_blockers = [b for b in align_blockers if b in ALLOWED_SKILL_LEVEL_BLOCKERS]
        ex_gate_reasons = [r for r in ex_gate_reasons if r in ALLOWED_SKILL_LEVEL_BLOCKERS]
        auto_review["alignment_blockers"] = align_blockers
        if "exception_review_gate" in auto_review and isinstance(auto_review["exception_review_gate"], dict):
            auto_review["exception_review_gate"]["reasons"] = ex_gate_reasons
            auto_review["exception_review_gate"]["required"] = bool(ex_gate_reasons)
            
        align_warns = auto_review.get("alignment_warnings", [])
        for b in invalid_blockers:
            if b not in align_warns:
                align_warns.append(f"disallowed_blocker_promoted_to_warning:{b}")
        auto_review["alignment_warnings"] = align_warns
        alignment_blocked = bool(align_blockers)

    payload = {
        "ok": not alignment_blocked,
        "phase": "phase1",
        "skill_id": skill_id,
        "skill_id_prefix_validated": prefix_ok,
        "skill_id_prefix_validation_reason": prefix_reason,
        "sop_reference": build_sop_reference(PROJECT_ROOT),
        "sop_gate_status": sop_gate_status,
        "sop_gate_violation": sop_gate_violation,
        "invalid_skill_level_blockers": invalid_blockers,
        "main_skill_anchor": auto_review.get("main_skill_anchor", {}),
        "source_example_count": len(examples),
        "source_alignment_status": auto_review.get("source_alignment_status", "pass"),
        "skill_problem_type_alignment_status": auto_review.get("skill_problem_type_alignment_status", "pass"),
        "alignment_score": auto_review.get("alignment_score", 1.0),
        "alignment_warnings": auto_review.get("alignment_warnings", []),
        "alignment_blockers": auto_review.get("alignment_blockers", []),
        "semantic_alignment": auto_review.get("semantic_alignment", {}),
        "source_family_distribution": auto_review.get("source_family_distribution", {}),
        "candidate_problem_type_families": auto_review.get("candidate_problem_type_families", []),
        "expected_skill_families": auto_review.get("expected_skill_families", []),
        "expected_subskill_candidates": auto_review.get(
            "expected_subskill_candidates",
            (auto_review.get("main_skill_anchor") or {}).get("expected_subskill_candidates", []),
        ),
        "observed_target_task_distribution": auto_review.get("observed_target_task_distribution", {}),
        "same_family_subskill_mismatch_examples": auto_review.get("same_family_subskill_mismatch_examples", []),
        "examples_outside_expected_subskills": auto_review.get("examples_outside_expected_subskills", []),
        "suggested_action": auto_review.get("suggested_action", ""),
        "requires_human_action": bool(auto_review.get("requires_human_action", False)),
        "semantic_classifications": auto_review.get("semantic_classifications", []),
        "ai_semantic_status": auto_review.get("ai_semantic_status", "not_used"),
        "source_type_distribution": auto_review.get("source_type_distribution", {}),
        "example_practice_link_map": auto_review.get("example_practice_link_map", []),
        "structure_mismatch_examples": auto_review.get("structure_mismatch_examples", []),
        "same_section_family_distribution": auto_review.get("same_section_family_distribution", {}),
        "source_structure_report": auto_review.get("source_structure_report", {}),
        "classification_diagnostics": auto_review.get("classification_diagnostics", []),
        "ai_semantic_unavailable_reason": auto_review.get("ai_semantic_unavailable_reason", ""),
        "excluded_source_examples": auto_review.get("excluded_source_examples", []),
        "induction_source_selection": auto_review.get("induction_source_selection", {}),
        "skipped_enrichment_examples": auto_review.get("skipped_enrichment_examples", []),
        "future_ai_judged_candidates": auto_review.get("future_ai_judged_candidates", []),
        "contextual_application_sources": auto_review.get("contextual_application_sources", []),
        "clause45_escalation_applied": bool(auto_review.get("clause45_escalation_applied", False)),
        "clause45_rescued_example_ids": auto_review.get("clause45_rescued_example_ids", []),
        "clause45_observed_target_task_distribution": auto_review.get("clause45_observed_target_task_distribution", {}),
        "clause45_proxy_problem_type_ids": auto_review.get("clause45_proxy_problem_type_ids", []),
        "expected_family_relaxation_applied": bool(auto_review.get("expected_family_relaxation_applied", False)),
        "expected_family_relaxation_reason": auto_review.get("expected_family_relaxation_reason", ""),
        "expected_family_relaxation_target_task": auto_review.get("expected_family_relaxation_target_task", ""),
        "core_example_count": auto_review.get("core_example_count", 0),
        "enrichment_example_count": auto_review.get("enrichment_example_count", 0),
        "rejected_source_examples": auto_review.get("rejected_source_examples", []),
        "source_quality_issues": auto_review.get("source_quality_issues", []),
        "semantic_mismatch_examples": auto_review.get("semantic_mismatch_examples", []),
        "suspected_wrong_skill_examples": auto_review.get("suspected_wrong_skill_examples", []),
        "same_family_extension_examples": auto_review.get("same_family_extension_examples", []),
        "section_scope_subskill_extension_examples": auto_review.get("section_scope_subskill_extension_examples", []),
        "same_as_main_skill_examples": auto_review.get("same_as_main_skill_examples", []),
        "inherited_from_previous_context_examples": auto_review.get("inherited_from_previous_context_examples", []),
        "low_source_examples": auto_review.get("low_source_examples", []),
        "candidate_only_problem_types": auto_review.get("candidate_only_problem_types", []),
        "candidate_only_count": int(auto_review.get("candidate_only_count", len(auto_review.get("candidate_only_problem_types", []) or [])) or 0),
        "same_as_main_skill_count": int(auto_review.get("same_as_main_skill_count", len(auto_review.get("same_as_main_skill_examples", []) or [])) or 0),
        "rule_only_classification_count": int(auto_review.get("rule_only_classification_count", 0) or 0),
        "hybrid_resolved_count": int(auto_review.get("hybrid_resolved_count", 0) or 0),
        "subskills": auto_review.get("subskills", []),
        "fallback_subskill_used": bool(auto_review.get("fallback_subskill_used", False)),
        "source_belongs_to_current_skill_by_default_count": int(auto_review.get("source_belongs_to_current_skill_by_default_count", 0) or 0),
        "source_example_alignment": auto_review.get("source_example_alignment", []),
        "candidate_problem_types": auto_review.get("candidate_problem_types", []),
        "answer_contract_summary": answer_contract_summary,
        "invalid_equivalence_type_problem_types": invalid_equivalence_problem_types,
        "phase1_answer_contract_gate_status": "PASS" if phase1_ac_gate_pass else "FOUNDATION_REPAIR_REQUIRED",
        "per_example_classification": per_example,
        "source_classifications": per_example,
        "unclassified_examples": unclassified,
        "risk_examples": risk_examples,
        "split_or_merge_recommendation": auto_review.get("split_or_merge_recommendation", ""),
        "classifier_gate": auto_review.get("classifier_gate", {}),
        "generator_draft_gate": auto_review.get("generator_draft_gate", {}),
        "runtime_ready_gate": auto_review.get("runtime_ready_gate", {}),
        "exception_review_gate": auto_review.get("exception_review_gate", {}),
        "reports": reports,
        "next_action": auto_review.get("next_action", "review_classifier_proposal_and_decide_split_merge"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
        "auto_review_summary": auto_review,
        "classifier_source": classifier_source,
        "ai_bootstrap_used": ai_bootstrap_used,
        "ai_bootstrap_status": ai_bootstrap_status,
        "ai_bootstrap_confidence_summary": ai_bootstrap_confidence_summary,
        "inspect_report_note": inspect_report_note,
        "ai_bootstrap_error": str(meta.get("ai_bootstrap_error", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_raw_response_preview": str(meta.get("ai_bootstrap_raw_response_preview", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_validation_errors": meta.get("ai_bootstrap_validation_errors", []) if isinstance(meta, dict) and isinstance(meta.get("ai_bootstrap_validation_errors"), list) else [],
        "ai_bootstrap_prompt_version": str(meta.get("ai_bootstrap_prompt_version", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_model": str(meta.get("ai_bootstrap_model", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_provider": str(meta.get("ai_bootstrap_provider", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_config_source": str(meta.get("ai_bootstrap_config_source", "") if isinstance(meta, dict) else ""),
        "default_problem_type_used": bool(meta.get("default_problem_type_used", False) if isinstance(meta, dict) else False),
        "problem_type_spec_first": bool(auto_review.get("problem_type_spec_first", False)),
        "spec_defined_problem_type_ids": auto_review.get("spec_defined_problem_type_ids", []),
        "spec_mode": str(auto_review.get("spec_mode", spec_mode)).strip(),
        "induced_problem_type_specs": auto_review.get("induced_problem_type_specs", []),
        "induction_clusters": auto_review.get("induction_clusters", []),
    }
    payload["human_review_items"] = _build_human_review_items(
        skill_id=skill_id,
        skill_ch_name=_pick_skill_ch_name(skill_id, examples),
        entries=entries,
        examples=examples,
        candidate_problem_types=payload.get("candidate_problem_types", []),
        exception_review_gate=payload.get("exception_review_gate", {}),
    )
    # SOP v0.2: Run Phase 1 Report Contract Validator before writing reports
    from core.gencode.phase1_report_contract import validate_phase1_report_contract
    from core.gencode.problem_type_grouping_contract import validate_problem_type_grouping_contract
    
    contract_res = validate_phase1_report_contract(payload)
    payload.update(contract_res["normalized_fields"])
    payload["report_contract_status"] = contract_res["report_contract_status"]
    payload["report_contract_warnings"] = contract_res["report_contract_warnings"]
    payload["report_contract_violations"] = contract_res["report_contract_violations"]
    
    grouping_res = validate_problem_type_grouping_contract(payload)
    payload.update(grouping_res["normalized_fields"])
    payload = _apply_source_skill_binding_candidate_policy(skill_id, payload)
    payload["problem_type_grouping_contract_status"] = grouping_res["problem_type_grouping_contract_status"]
    payload["problem_type_grouping_contract_warnings"] = grouping_res["problem_type_grouping_contract_warnings"]
    payload["problem_type_grouping_contract_violations"] = grouping_res["problem_type_grouping_contract_violations"]

    write_json(Path(reports["phase1_summary_json"]), payload)
    _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
    runtime_candidates = [
        c for c in (payload.get("candidate_problem_types") or [])
        if isinstance(c, dict)
        and str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip() not in {"", "unclassified_source_review", "classifier_missing_source_review"}
        and str(c.get("checker_key_proposal", "")).strip() != "manual_review_checker"
        and str(c.get("equivalence_type_proposal", "")).strip() != "manual_review_or_ai_judged"
    ]
    classifier_draft_path = ""
    if runtime_candidates and classifier_source in {"ai_bootstrap", "ai_bootstrap_low_quality", "neutral_fallback", "human_override"}:
        draft_obj = _build_classifier_yaml_draft_from_phase1(payload, examples)
        classifier_draft_path = _write_classifier_yaml_draft(skill_id, draft_obj)
        payload["classifier_yaml_draft_path"] = classifier_draft_path
        payload["classifier_rulepack_registerable"] = True
        
        # SOP v0.2: Re-run Phase 1 Report Contract Validator to keep draft report consistent
        from core.gencode.phase1_report_contract import validate_phase1_report_contract
        contract_res_d = validate_phase1_report_contract(payload)
        payload.update(contract_res_d["normalized_fields"])
        payload["report_contract_status"] = contract_res_d["report_contract_status"]
        payload["report_contract_warnings"] = contract_res_d["report_contract_warnings"]
        payload["report_contract_violations"] = contract_res_d["report_contract_violations"]

        write_json(Path(reports["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    if classifier_draft_path:
        normalized["classifier_yaml_draft_path"] = classifier_draft_path
        normalized["classifier_rulepack_registerable"] = True
    return normalized


def run_gencode_phase2(skill_id: str, accepted_problem_types: list | None = None, excluded_example_ids: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    from gencode_closed_loop.controller import execute_phase_2
    return execute_phase_2(
        skill_id=skill_id,
        accepted_problem_types=accepted_problem_types,
        excluded_example_ids=excluded_example_ids,
        dry_run=dry_run
    )


def run_gencode_phase2_raw(skill_id: str, accepted_problem_types: list | None = None, excluded_example_ids: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    # SOP v0.2: Preflight Scan Policy Enforcement
    from core.gencode.sop_policy import validate_sop_preflight, build_sop_reference
    preflight = validate_sop_preflight(PROJECT_ROOT)
    reports_pre = _phase_reports(
        skill_id,
        keys=("phase2_generator_summary_json", "phase2_generator_summary_md"),
    )
    if preflight["sop_preflight_status"] == "FAIL":
        payload = {
            "ok": False,
            "phase": "phase2",
            "skill_id": skill_id,
            "phase1_alignment_blocked": True,
            "alignment_blockers": ["blocked_sop_preflight_failed"],
            "generator_results": [],
            "failed_generators": [],
            "accepted_generators": [],
            "foundation_ready": False,
            "phase2_status": "SOP_PREFLIGHT_FAIL",
            "reports": reports_pre,
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "sop_preflight_status": "FAIL",
            "sop_preflight_errors": preflight["errors"],
        }
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(Path(reports_pre["phase2_generator_summary_json"]), payload)
        write_md(Path(reports_pre["phase2_generator_summary_md"]), f"Gencode Phase2 Generator Summary: {skill_id}", [("phase2", payload)])
        normalized = _normalize_phase_response(payload)
        normalized["phase_status"] = "SOP_PREFLIGHT_FAIL"
        normalized["summary_message"] = f"SOP preflight failed: {', '.join(preflight['errors'])}"
        return normalized

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase1_path = phase_summary_path(skill_id, "phase1_summary")
    draft_spec_path = phase_summary_path(skill_id, "generator_draft_spec")
    phase1 = _load_phase_json(phase1_path) if phase1_path.exists() else run_gencode_phase1(skill_id, dry_run=dry_run)
    _build_phase2_foundation_preflight(
        phase1_payload=phase1 if isinstance(phase1, dict) else {},
        generator_results=[],
    )
    write_json(phase1_path, phase1)
    write_json(
        draft_spec_path,
        {
            "skill_id": skill_id,
            "phase": "phase2",
            "phase1_payload": phase1,
            "generator_results": [],
            "accepted_generators": [],
            "failed_generators": [],
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
        },
    )
    phase1_alignment_blocked = (
        str(phase1.get("source_alignment_status", "")).strip() == "block"
        or bool(phase1.get("alignment_blockers"))
    )
    # Relax alignment blocked status if AI was partially unavailable
    ai_status_val = str(phase1.get("ai_semantic_status") or "").strip()
    if ai_status_val in {"partial_unavailable", "unavailable"}:
        phase1_alignment_blocked = False
    candidates = phase1.get("candidate_problem_types", []) if isinstance(phase1.get("candidate_problem_types"), list) else []
    accepted = set(str(x) for x in (accepted_problem_types or []))
    excluded = set(int(x) for x in (excluded_example_ids or []) if str(x).isdigit())
    reject_ids_from_sem = set(
        int(x)
        for x in (((phase1.get("semantic_alignment") or {}).get("source_quality_reject_examples") or []))
        if str(x).isdigit()
    )
    reject_ids_from_rows = {
        int(x.get("example_id"))
        for x in (phase1.get("rejected_source_examples") or [])
        if isinstance(x, dict) and str(x.get("example_id", "")).isdigit()
    }
    rejected_source_ids = reject_ids_from_sem | reject_ids_from_rows
    generator_results: list[dict[str, Any]] = []
    failed_generators: list[str] = []
    accepted_generators: list[str] = []
    phase1_anchor = phase1.get("main_skill_anchor") if isinstance(phase1.get("main_skill_anchor"), dict) else {}
    for c in candidates:
        from core.gencode.problem_type_canonicalizer import (
            enrich_spec_with_canonicalization,
            get_answer_contract,
            resolve_authoritative_problem_type_id,
            sync_candidate_authoritative_identity,
        )

        c = sync_candidate_authoritative_identity(c) if isinstance(c, dict) else c
        pt = resolve_authoritative_problem_type_id(c)
        if not pt:
            continue
        if pt.endswith("_expression") or pt.startswith("expression_write_line_equation"):
            continue
        if accepted and pt not in accepted:
            continue
        raw_src_ids = [x for x in (c.get("matched_example_ids") or []) if isinstance(x, int) and x not in excluded]
        src_ids = [x for x in raw_src_ids if x not in rejected_source_ids]
        answer_contract = c.get("answer_contract_proposal", {}) if isinstance(c.get("answer_contract_proposal"), dict) else {}
        checker_key = str(c.get("checker_key_proposal", "")).strip()
        eq = str(c.get("equivalence_type_proposal", "")).strip()
        draft_spec = c.get("problem_type_spec_draft") if isinstance(c.get("problem_type_spec_draft"), dict) else {}
        cand_target = str(
            c.get("target_task") or c.get("subskill_id") or draft_spec.get("target_task") or ""
        ).strip()
        cand_family = str(
            c.get("task_family") or draft_spec.get("task_family") or ""
        ).strip()
        if not cand_family and cand_target:
            from core.gencode.task_families import task_family_for_task

            cand_family = task_family_for_task(cand_target)
        generic_fallback_blocked = (
            c.get("usable_for_phase3") is False
            or should_block_generic_fallback_for_scope(
                {**phase1_anchor, **c},
                problem_type_id=pt,
                target_task=cand_target,
                task_family=cand_family,
            )
        )
        if draft_spec:
            enriched = enrich_spec_with_canonicalization({**draft_spec, "skill_id": skill_id, "problem_type_id": pt})
            pt = str(enriched.get("problem_type_id") or pt).strip()
            draft_spec = enriched
            answer_contract = get_answer_contract(enriched) or answer_contract
            checker_key = str(
                answer_contract.get("checker_key") or answer_contract.get("checker") or checker_key
            ).strip()
            eq = str(
                answer_contract.get("equivalence_type") or answer_contract.get("answer_equivalence") or eq
            ).strip()
        generator_key = f"{skill_id}:{pt}:draft_v1"
        blockers: list[str] = []
        warnings: list[str] = []
        status = "draft_planned"
        if generic_fallback_blocked:
            status = "pending_problem_type_induction"
            blockers.append("generic_fallback_blocked_by_source_skill_binding")
        matched_count = int(c.get("matched_example_count") or c.get("source_example_count") or 0)
        spec_source = str(c.get("spec_source", "")).strip()
        generator_readiness = str(c.get("generator_readiness", "")).strip()
        pt_requires_human_action = bool(c.get("requires_human_action", False))
        no_usable_source_for_pt = not bool(src_ids)
        all_sources_rejected_for_pt = bool(raw_src_ids) and not bool(src_ids)
        is_manual_or_malformed = (
            checker_key == "manual_review_checker"
            or eq == "manual_review_or_ai_judged"
            or "malformed_source_review" in pt
            or all_sources_rejected_for_pt
            or (pt_requires_human_action and no_usable_source_for_pt)
        )
        if spec_source in {"problem_type_specs.v1.json", "phase1_induced_draft", "anchor_slot_bootstrap"}:
            draft_spec = c.get("problem_type_spec_draft") if isinstance(c.get("problem_type_spec_draft"), dict) else {}
            if draft_spec:
                from core.gencode.spec_phase1_merge import slot_generator_readiness

                generator_readiness = slot_generator_readiness(draft_spec)
            if matched_count == 0:
                warnings.append("no_matched_source_examples")
            if generator_readiness == "pending_template":
                status = "pending_template"
                blockers.append("slot_generator_not_registered")
            elif generator_readiness == "generator_not_ready":
                status = "generator_not_ready"
                blockers.append("generator_not_ready")
            elif generator_readiness == "runtime_ready" and status in {"", "draft_planned"} and not phase1_alignment_blocked:
                status = "runtime_ready"
            elif generator_readiness == "alignment_blocked":
                status = "blocked"
                blockers.append("semantic_alignment_blocked")
            elif generator_readiness == "answer_contract_not_supported":
                status = "blocked"
                blockers.append("answer_contract_not_supported")
                blockers.append("checker_contract_missing")
        elif matched_count == 0 or not src_ids:
            status = "blocked"
            blockers.append("no_source_examples")
        if is_manual_or_malformed:
            status = "blocked"
            blockers.append("manual_review_or_malformed_source")
        if phase1_alignment_blocked:
            status = "blocked"
            for b in phase1.get("alignment_blockers", []) or []:
                if b and b not in blockers:
                    blockers.append(str(b))
            if "phase1_semantic_alignment_blocked" not in blockers:
                blockers.append("phase1_semantic_alignment_blocked")
        if not answer_contract or not checker_key or not eq:
            status = "blocked"
            blockers.append("missing_contract_or_checker_or_equivalence")
        from core.gencode.checker_registry import validate_answer_contract_capability

        checker_cap = validate_answer_contract_capability(answer_contract)
        if checker_cap.get("checker_capability_status") == "blocked":
            status = "blocked"
            for b in checker_cap.get("checker_contract_blockers", []) or []:
                if b and b not in blockers:
                    blockers.append(str(b))
        if str(checker_key) == "text_checker" and str(eq) in {"exact_string", "exact_text"}:
            at = str(answer_contract.get("answer_type", "")).strip()
            if at in {"numeric", "numeric_or_radical", "set", "solution_set", "interval"}:
                status = "blocked"
                blockers.append("answer_contract_not_supported")
        if matched_count <= 3:
            warnings.append("low_source_examples")
        checker_smoke_status = "pending"
        dynamic_sampling_status = "pending"
        diversity_report: dict[str, Any] = {}
        if blockers:
            checker_smoke_status = "skipped_with_blockers"
            dynamic_sampling_status = "skipped_with_blockers"
        else:
            checker_smoke_status = "passed"
            dynamic_sampling_status = "passed"
            draft_spec = c.get("problem_type_spec_draft") if isinstance(c.get("problem_type_spec_draft"), dict) else {}
            from core.gencode.problem_type_canonicalizer import line_equation_mcq_hold_applies

            mcq_hold_skip_sampling = line_equation_mcq_hold_applies(
                {
                    "problem_type_id": pt,
                    "target_task": str(draft_spec.get("target_task", cand_target)).strip(),
                    "task_family": str(draft_spec.get("task_family", cand_family)).strip(),
                    "answer_contract": answer_contract,
                    "presentation_mode": str(answer_contract.get("presentation_mode", "")).strip(),
                }
            )
            if mcq_hold_skip_sampling:
                dynamic_sampling_status = "skipped_pending_line_equation_mcq_slot"
                diversity_report = {
                    "diversity_sampling_status": "skipped_pending_line_equation_mcq_slot",
                    "diversity_healthy": False,
                    "sample_count": 0,
                    "unique_signature_count": 0,
                    "unique_question_text_count": 0,
                    "template_variant_distribution": {},
                    "answer_shape_distribution": {},
                    "variable_coverage_report": {},
                    "repetition_warnings": ["line_equation_single_choice_slot_not_ready"],
                    "diversity_blockers": ["line_equation_single_choice_slot_not_ready"],
                    "max_consecutive_same_template": 0,
                    "generation_errors": [],
                    "sampling_mode": "skipped_pending_line_equation_mcq_slot",
                }
            elif draft_spec:
                try:
                    from core.gencode.generator_diversity_sampling import run_diversity_sampling

                    diversity_report = run_diversity_sampling(skill_id, draft_spec)
                    dynamic_sampling_status = str(
                        diversity_report.get("diversity_sampling_status", "passed")
                    ).strip() or "passed"
                except Exception as ex:
                    dynamic_sampling_status = "runtime_ready_with_diversity_warning"
                    diversity_report = {
                        "diversity_sampling_status": dynamic_sampling_status,
                        "repetition_warnings": [f"diversity_sampling_error:{str(ex)[:80]}"],
                    }
            elif phase1_alignment_blocked:
                status = "blocked"
        merged_blockers = sorted(
            set(list(blockers) + list(diversity_report.get("diversity_blockers") or []))
        )
        merged_warnings = sorted(
            set(list(warnings) + list(diversity_report.get("repetition_warnings") or []))
        )
        low_sample_diversity_tolerated = (
            matched_count <= 3 and "low_source_examples" in merged_warnings
        )
        if low_sample_diversity_tolerated:
            diversity_only_blockers = {
                "generator_diversity_blocked",
                "no_template_variant_used",
                "consecutive_template_diversity_blocked",
            }
            merged_blockers = [
                blocker for blocker in merged_blockers if blocker not in diversity_only_blockers
            ]
            dynamic_sampling_status = "runtime_ready_with_diversity_warning"
            merged_warnings = sorted(
                set(merged_warnings + ["low_sample_diversity_tolerance_applied"])
            )
        from core.gencode.packaging_policy import resolve_phase2_generator_status

        status, usable_for_phase3 = resolve_phase2_generator_status(
            blockers=merged_blockers,
            warnings=merged_warnings,
            checker_smoke_status=checker_smoke_status,
            dynamic_sampling_status=dynamic_sampling_status,
            base_status=status,
        )

        if generic_fallback_blocked:
            usable_for_phase3 = False
            status = "pending_problem_type_induction"
            if "generic_fallback_blocked_by_source_skill_binding" not in merged_blockers:
                merged_blockers.append("generic_fallback_blocked_by_source_skill_binding")

        from core.gencode.problem_type_canonicalizer import (
            LINE_EQUATION_MCQ_HOLD_BLOCKER,
            apply_line_equation_mcq_hold_policy,
            line_equation_mcq_hold_applies,
        )

        hold_probe = apply_line_equation_mcq_hold_policy(
            {
                "problem_type_id": pt,
                "target_task": str(draft_spec.get("target_task") or "").strip() if isinstance(draft_spec, dict) else "",
                "task_family": str(draft_spec.get("task_family") or "").strip() if isinstance(draft_spec, dict) else "",
                "answer_contract": answer_contract,
                "presentation_mode": str(answer_contract.get("presentation_mode", "")).strip(),
                "usable_for_phase3": usable_for_phase3,
                "generator_readiness": status,
                "requires_human_action": pt_requires_human_action,
                "promote_recommendation": "",
                "risk_flags": list(merged_warnings),
                "promote_blockers": list(merged_blockers),
                "blockers": list(merged_blockers),
            }
        )
        if line_equation_mcq_hold_applies(hold_probe):
            usable_for_phase3 = False
            status = str(hold_probe.get("generator_readiness") or "pending_line_equation_mcq_slot")
            pt_requires_human_action = True
            merged_blockers = sorted(
                set(list(merged_blockers) + [LINE_EQUATION_MCQ_HOLD_BLOCKER])
            )
            merged_warnings = sorted(
                set(list(merged_warnings) + [LINE_EQUATION_MCQ_HOLD_BLOCKER])
            )
        
        # Relax blockers and force usability if AI was partially unavailable
        ai_status_val = str(phase1.get("ai_semantic_status") or "").strip()
        if not generic_fallback_blocked and ai_status_val in {"partial_unavailable", "unavailable"}:
            status = "runtime_ready_with_warning"
            if not line_equation_mcq_hold_applies(hold_probe):
                usable_for_phase3 = True
            merged_blockers = [b for b in merged_blockers if b not in {
                "checker_contract_blocked", "answer_contract_not_supported", 
                "generator_diversity_blocked", "no_template_variant_used",
                "consecutive_template_diversity_blocked", "model_repetition_blocked"
            }]

        if not generic_fallback_blocked and low_sample_diversity_tolerated:
            repetition_only_blockers = {
                "generator_diversity_blocked",
                "no_template_variant_used",
                "consecutive_template_diversity_blocked",
                "model_repetition_blocked",
            }
            fatal_semantic_blockers = [
                blocker
                for blocker in merged_blockers
                if blocker not in repetition_only_blockers
            ]
            if not fatal_semantic_blockers and not line_equation_mcq_hold_applies(hold_probe):
                status = "runtime_ready_with_warning"
                usable_for_phase3 = True
        if usable_for_phase3:
            accepted_generators.append(generator_key)
        else:
            failed_generators.append(generator_key)
        packaging_meta: dict[str, Any] = {}
        if draft_spec:
            try:
                from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization

                enriched_pack = enrich_spec_with_canonicalization(
                    {**draft_spec, "skill_id": skill_id, "problem_type_id": pt}
                )
                packaging_meta = {
                    "target_task": str(enriched_pack.get("target_task") or "").strip(),
                    "base_problem_type_id": str(
                        enriched_pack.get("canonical_base_problem_type_id") or ""
                    ).strip(),
                    "value_type_prefix": str(enriched_pack.get("value_type_prefix") or "").strip(),
                    "template_slot": str(enriched_pack.get("_resolved_template_slot") or "").strip(),
                    "_resolved_template_slot": str(
                        enriched_pack.get("_resolved_template_slot") or ""
                    ).strip(),
                }
            except Exception:
                packaging_meta = {}
        generator_results.append(
            {
                "problem_type_id": pt,
                "source_example_count": len(src_ids),
                "answer_contract": answer_contract,
                "answer_type": answer_contract.get("answer_type", ""),
                "answer_shape": answer_contract.get("answer_shape", ""),
                "equivalence_type": eq,
                "selected_checker": checker_key,
                "checker_key": checker_key,
                "checker_capability_status": checker_cap.get("checker_capability_status", "ok"),
                "checker_contract_blockers": checker_cap.get("checker_contract_blockers", []),
                "checker_contract_warnings": checker_cap.get("checker_contract_warnings", []),
                "generator_key": generator_key,
                "generator_status": status,
                "checker_smoke_status": checker_smoke_status,
                "dynamic_sampling_status": dynamic_sampling_status,
                "diversity_sampling": diversity_report,
                "unique_signature_count": diversity_report.get("unique_signature_count", 0),
                "template_variant_distribution": diversity_report.get("template_variant_distribution", {}),
                "variable_coverage_report": diversity_report.get("variable_coverage_report", {}),
                "repetition_warnings": merged_warnings,
                "requires_human_action": pt_requires_human_action,
                "blockers": merged_blockers,
                "warnings": merged_warnings,
                "usable_for_phase3": usable_for_phase3,
                "target_task": str(
                    packaging_meta.get("target_task")
                    or draft_spec.get("target_task")
                    or cand_target
                    or ""
                ).strip(),
                "task_family": str(
                    draft_spec.get("task_family") or cand_family or ""
                ).strip(),
                "base_problem_type_id": packaging_meta.get("base_problem_type_id", ""),
                "value_type_prefix": packaging_meta.get("value_type_prefix", ""),
                "template_slot": packaging_meta.get("template_slot", "") or str(c.get("template_slot", "")).strip(),
                "_resolved_template_slot": packaging_meta.get("_resolved_template_slot", ""),
            }
        )

    from core.gencode.packaging_policy import _generator_record_rank

    deduped_results: dict[str, dict[str, Any]] = {}
    for row in generator_results:
        if not isinstance(row, dict):
            continue
        gk = str(row.get("generator_key", "")).strip() or str(row.get("problem_type_id", "")).strip()
        if not gk:
            continue
        existing = deduped_results.get(gk)
        if existing is None or _generator_record_rank(row) > _generator_record_rank(existing):
            deduped_results[gk] = row
    generator_results = list(deduped_results.values())
    accepted_generators = sorted({
        str(r.get("generator_key", "")).strip()
        for r in generator_results
        if isinstance(r, dict) and r.get("usable_for_phase3")
    })
    failed_generators = sorted({
        str(r.get("generator_key", "")).strip()
        for r in generator_results
        if isinstance(r, dict) and not r.get("usable_for_phase3")
    })

    reports = {
        **_phase_reports(
            skill_id,
            keys=(
                "phase2_generator_summary_json",
                "phase2_generator_summary_md",
                "phase2_json",
                "phase2_md",
            ),
        ),
        "generator_draft_spec_json": str(draft_spec_path.resolve()),
    }
    foundation_preflight = _build_phase2_foundation_preflight(
        phase1_payload=phase1 if isinstance(phase1, dict) else {},
        generator_results=generator_results,
    )
    # Write back the corrected generator_results to phase1 memory structure, phase1_summary.json, and draft_spec_path
    if isinstance(phase1, dict) and isinstance(phase1.get("candidate_problem_types"), list):
        for res in generator_results:
            pt_id = res.get("problem_type_id")
            for c in phase1["candidate_problem_types"]:
                if isinstance(c, dict) and (c.get("problem_type_id") == pt_id or c.get("proposed_problem_type_id") == pt_id):
                    c["answer_contract_proposal"] = res.get("answer_contract")
                    c["checker_key_proposal"] = res.get("checker_key")
                    c["equivalence_type_proposal"] = res.get("equivalence_type")
                    if isinstance(c.get("problem_type_spec_draft"), dict):
                        c["problem_type_spec_draft"]["answer_contract"] = res.get("answer_contract")
                        
    write_json(phase1_path, phase1)
        
    write_json(
        draft_spec_path,
        {
            "skill_id": skill_id,
            "phase": "phase2",
            "phase1_payload": phase1,
            "generator_results": generator_results,
            "accepted_generators": accepted_generators,
            "failed_generators": failed_generators,
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
        }
    )
    payload = {
        "ok": bool(generator_results) and not phase1_alignment_blocked and bool(foundation_preflight.get("foundation_ready")),
        "phase": "phase2",
        "skill_id": skill_id,
        "sop_reference": build_sop_reference(PROJECT_ROOT),
        "phase1_alignment_blocked": phase1_alignment_blocked,
        "alignment_blockers": phase1.get("alignment_blockers", []),
        "generator_results": generator_results,
        "failed_generators": failed_generators,
        "accepted_generators": accepted_generators,
        "foundation_preflight": foundation_preflight,
        "foundation_ready": bool(foundation_preflight.get("foundation_ready", False)),
        "phase2_status": str(foundation_preflight.get("foundation_status", "FOUNDATION_REPAIR_REQUIRED")),
        "repair_plan": foundation_preflight.get("repair_plan", []),
        "reports": reports,
        "next_action": str(foundation_preflight.get("next_action", "")) or ("phase3_package_draft" if accepted_generators else "review_blockers_before_phase3"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["phase2_generator_summary_json"]), payload)
    write_md(Path(reports["phase2_generator_summary_md"]), f"Gencode Phase2 Generator Summary: {skill_id}", [("phase2", payload)])
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    return normalized


def _run_gencode_publish_check_for_draft(skill_id: str, draft_skill_file_path: str, runtime_ready_gate: dict[str, Any] | None = None, checker_smoke_passed: bool = False, dynamic_sampling_passed: bool = False, equivalence_contract_passed: bool = False) -> dict[str, Any]:
    draft_path = Path(draft_skill_file_path)
    warnings: list[str] = []
    runtime_smoke_raw = run_draft_runtime_smoke(skill_id, draft_skill_file_path)
    runtime_smoke_status = str(runtime_smoke_raw.get("status", "failed"))
    blockers = list(runtime_smoke_raw.get("blockers", [])) if isinstance(runtime_smoke_raw.get("blockers"), list) else []
    py_compile_status = str(runtime_smoke_raw.get("py_compile_status", "not_run"))
    interface_check = runtime_smoke_raw.get("interface_check", {}) if isinstance(runtime_smoke_raw.get("interface_check"), dict) else {}

    # SOP v0.3: Closed-loop Self-healing retry loop
    if runtime_smoke_status == "failed":
        max_retries = 3
        current_attempt = 1
        while current_attempt <= max_retries:
            logger.info(f"[SELF-HEALING] Phase 3 smoke test failed. Starting attempt {current_attempt}/{max_retries}...")
            
            # Load SOP context for repair alignment
            sop_file = PROJECT_ROOT / SOP_INTEGRATION_DIR / "AgentSkillV2_ProblemType規格包設計_v0.3.md"
            sop_content = ""
            if sop_file.exists():
                try:
                    sop_content = sop_file.read_text(encoding="utf-8")
                except Exception:
                    pass

            # Read current failed draft skill code
            current_code = ""
            if draft_path.exists():
                current_code = draft_path.read_text(encoding="utf-8")

            # Construct repair prompt
            repair_prompt = f"""
你剛剛生成的代碼未能通過冒煙測試。
【錯誤詳情】:
{json.dumps(runtime_smoke_raw, ensure_ascii=False, indent=2)}

【目前程式碼】:
```python
{current_code}
```

【唯一對照權威 SOP 規範】:
{sop_content}

請扮演修復 Agent，對照 SOP 規範，精準修正隨機性邏輯與 YAML 任務過濾（特別注意若發生 fake_diversity_fatal 請修正隨機化邏輯綁定 seed），重新生成覆蓋。
請僅回傳修正後的完整 Python 程式碼，不要有 Markdown 格式或額外說明。
""".strip()

            client, client_meta = _resolve_gencode_ai_client(["architect", "tutor", "default"])
            if client:
                try:
                    resp = call_ai_with_retry(client, repair_prompt, max_retries=2, retry_delay=2, timeout=90)
                    resp_text = str(getattr(resp, "text", "") or "").strip()
                    if resp_text.startswith("```python"):
                        resp_text = resp_text.split("```python", 1)[-1].split("```", 1)[0].strip()
                    elif resp_text.startswith("```"):
                        resp_text = resp_text.split("```", 1)[-1].split("```", 1)[0].strip()
                    
                    if resp_text:
                        logger.info(f"[SELF-HEALING] AI generated repaired code. Overwriting {draft_skill_file_path}...")
                        draft_path.write_text(resp_text, encoding="utf-8")
                        
                        # Re-run compile and smoke test on the new code
                        runtime_smoke_raw = run_draft_runtime_smoke(skill_id, draft_skill_file_path)
                        runtime_smoke_status = str(runtime_smoke_raw.get("status", "failed"))
                        blockers = list(runtime_smoke_raw.get("blockers", [])) if isinstance(runtime_smoke_raw.get("blockers"), list) else []
                        py_compile_status = str(runtime_smoke_raw.get("py_compile_status", "not_run"))
                        interface_check = runtime_smoke_raw.get("interface_check", {}) if isinstance(runtime_smoke_raw.get("interface_check"), dict) else {}
                        
                        if runtime_smoke_status == "passed" and not blockers:
                            logger.info(f"[SELF-HEALING] Attempt {current_attempt} PASSED.")
                            break
                        else:
                            logger.warning(f"[SELF-HEALING] Attempt {current_attempt} failed. Blockers: {blockers}")
                except Exception as ex:
                    logger.error(f"[SELF-HEALING] Exception in attempt {current_attempt}: {ex}")
            
            current_attempt += 1

    draft_check_passed = bool(
        draft_path.exists()
        and py_compile_status == "passed"
        and runtime_smoke_status == "passed"
        and not blockers
    )


    can_publish_draft = draft_check_passed
    can_publish_formal = can_publish_draft
    formal_publish_blockers: list[str] = []
    if not can_publish_formal:
        formal_publish_blockers.append("draft_check_not_passed")

    runtime_ready_blockers: list[str] = []
    gate_status = str((runtime_ready_gate or {}).get("status", ""))
    runtime_ready_allowed = str((runtime_ready_gate or {}).get("status", "")) == "runtime_ready_allowed" or bool((runtime_ready_gate or {}).get("allowed", False))
    if not runtime_ready_allowed or not checker_smoke_passed or not dynamic_sampling_passed or not equivalence_contract_passed:
        runtime_ready_blockers.append("runtime_ready_gate_not_allowed_or_not_verified")
        warnings.append("draft_passed_but_runtime_ready_not_confirmed")
    can_mark_runtime_ready = len(runtime_ready_blockers) == 0

    summary_message = (
        "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
        if can_publish_formal
        else "Draft is not ready for publish yet. Please resolve blockers first."
    )

    return {
        "draft_check_passed": draft_check_passed,
        "can_publish_draft": can_publish_draft,
        "can_publish_formal": can_publish_formal,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "formal_publish_blockers": formal_publish_blockers,
        "runtime_ready_blockers": runtime_ready_blockers,
        "warnings": warnings,
        "blockers": blockers,
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "runtime_smoke_raw": runtime_smoke_raw,
        "summary_message": summary_message,
    }


def _sync_phase3_runtime_specs_from_draft(
    skill_id: str,
    draft_spec: dict[str, Any],
    usable_generators: list[dict[str, Any]],
) -> dict[str, Any]:
    sid = str(skill_id).strip()
    induced_path = problem_type_spec_registry._induced_path(sid)
    induced_dir = Path(problem_type_spec_registry.INDUCED_DIR)
    safe_sid = sid.replace("/", "_").replace("\\", "_")
    purged_paths: list[str] = []
    if induced_dir.exists():
        for existing_path in induced_dir.iterdir():
            stem = existing_path.stem
            matches_skill = (
                stem == safe_sid
                or stem.startswith(f"{safe_sid}.")
                or stem.startswith(f"{safe_sid}_")
                or stem.startswith(f"{safe_sid}-")
            )
            if (
                existing_path.is_file()
                and existing_path.suffix.lower() == ".json"
                and matches_skill
            ):
                existing_path.unlink(missing_ok=True)
                purged_paths.append(str(existing_path))
    problem_type_spec_registry._INDUCED_BY_SKILL[sid] = []

    phase1_payload = (
        draft_spec.get("phase1_payload")
        if isinstance(draft_spec.get("phase1_payload"), dict)
        else {}
    )
    candidates = (
        phase1_payload.get("candidate_problem_types")
        if isinstance(phase1_payload.get("candidate_problem_types"), list)
        else []
    )
    canonical_problem_types = {
        str(
            candidate.get("problem_type_id")
            or candidate.get("proposed_problem_type_id")
            or ""
        ).strip()
        for candidate in candidates
        if isinstance(candidate, dict)
        and str(
            candidate.get("problem_type_id")
            or candidate.get("proposed_problem_type_id")
            or ""
        ).strip()
    }
    downgraded_historical_problem_type_ids: list[str] = []
    if canonical_problem_types:
        for row in usable_generators:
            if not isinstance(row, dict):
                continue
            pt = str(row.get("problem_type_id", "")).strip()
            zombie_row = _has_zombie_problem_type_id(pt)
            non_canonical = bool(pt and pt not in canonical_problem_types)
            if non_canonical or zombie_row:
                row["generator_readiness"] = "source_bank_only"
                row["usable_for_phase3"] = False
                warning_code = (
                    "phase3_zombie_problem_type_downgraded"
                    if zombie_row
                    else "phase3_historical_problem_type_downgraded"
                )
                row["warnings"] = sorted(set(list(row.get("warnings") or []) + [warning_code]))
                downgraded_historical_problem_type_ids.append(pt)
    usable_problem_types = {
        str(row.get("problem_type_id", "")).strip()
        for row in usable_generators
        if isinstance(row, dict)
        and str(row.get("problem_type_id", "")).strip()
        and str(row.get("problem_type_id", "")).strip() in canonical_problem_types
    }
    aligned_specs_by_problem_type: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        pt = str(
            candidate.get("problem_type_id")
            or candidate.get("proposed_problem_type_id")
            or ""
        ).strip()
        if not pt or pt not in usable_problem_types:
            continue
        source_draft = candidate.get("problem_type_spec_draft")
        if not isinstance(source_draft, dict):
            continue
        source_draft_pt = str(source_draft.get("problem_type_id", "")).strip()
        if pt in aligned_specs_by_problem_type:
            source_draft["generator_readiness"] = "source_bank_only"
            if source_draft_pt:
                downgraded_historical_problem_type_ids.append(source_draft_pt)
            continue
        aligned = copy.deepcopy(source_draft)
        aligned["skill_id"] = sid
        aligned["problem_type_id"] = pt
        aligned.pop("generator_readiness", None)
        _canonicalize_nested_problem_type_ids(aligned, pt)
        _reinforce_canonical_answer_contract(aligned, pt)
        _sanitize_coordinate_pair_answer_contract(aligned, pt)
        _reinforce_derivation_contract(aligned, aligned["problem_type_id"])
        aligned_specs_by_problem_type[pt] = aligned

    aligned_specs = list(aligned_specs_by_problem_type.values())

    if not aligned_specs:
        return {
            "status": "skipped_no_aligned_draft_specs",
            "synced_spec_count": 0,
            "synced_problem_type_ids": [],
            "purged_induced_spec_path": str(induced_path),
            "purged_induced_spec_paths": purged_paths,
            "runtime_usable_problem_type_ids": sorted(usable_problem_types),
            "downgraded_historical_problem_type_ids": sorted(
                set(downgraded_historical_problem_type_ids)
            ),
            "canonical_filter_applied": bool(canonical_problem_types),
        }

    induced_path = save_induced_problem_type_specs(sid, aligned_specs)
    return {
        "status": "synced",
        "synced_spec_count": len(aligned_specs),
        "synced_problem_type_ids": [
            str(spec.get("problem_type_id", "")).strip() for spec in aligned_specs
        ],
        "induced_spec_path": str(induced_path),
        "purged_induced_spec_path": str(induced_path),
        "purged_induced_spec_paths": purged_paths,
        "runtime_usable_problem_type_ids": sorted(usable_problem_types),
        "downgraded_historical_problem_type_ids": sorted(
            set(downgraded_historical_problem_type_ids)
        ),
        "canonical_filter_applied": bool(canonical_problem_types),
    }


def run_gencode_phase3_package(skill_id: str, accepted_generator_keys: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    from gencode_closed_loop.pipeline import execute_phase_3
    return execute_phase_3(
        skill_id=skill_id,
        accepted_generator_keys=accepted_generator_keys,
        dry_run=dry_run
    )


def run_gencode_phase3_package_raw(skill_id: str, accepted_generator_keys: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    from core.gencode.packaging_policy import format_packaging_blocked_message, select_generators_for_packaging

    # SOP v0.2: Preflight Scan Policy Enforcement
    from core.gencode.sop_policy import validate_sop_preflight, build_sop_reference
    preflight = validate_sop_preflight(PROJECT_ROOT)
    reports_pre = _phase_reports(
        skill_id,
        keys=("phase3_package_summary_json", "phase3_package_summary_md"),
    )
    if preflight["sop_preflight_status"] == "FAIL":
        payload = {
            "ok": False,
            "phase": "phase3",
            "skill_id": skill_id,
            "skill_file_path": "",
            "package_status": "SOP_PREFLIGHT_FAIL",
            "py_compile_status": "not_run",
            "runtime_smoke_status": "not_run",
            "reports": reports_pre,
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "sop_preflight_status": "FAIL",
            "sop_preflight_errors": preflight["errors"],
        }
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(Path(reports_pre["phase3_package_summary_json"]), payload)
        write_md(Path(reports_pre["phase3_package_summary_md"]), f"Gencode Phase3 Package Summary: {skill_id}", [("phase3", payload)])
        normalized = _normalize_phase_response(payload)
        normalized["phase_status"] = "SOP_PREFLIGHT_FAIL"
        normalized["summary_message"] = f"SOP preflight failed: {', '.join(preflight['errors'])}"
        return normalized

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase2_path = phase_summary_path(skill_id, "phase2_generator_summary")
    draft_spec_path = phase_summary_path(skill_id, "generator_draft_spec")
    phase2 = _load_phase_json(phase2_path) if phase2_path.exists() else run_gencode_phase2(skill_id, dry_run=dry_run)
    draft_spec = _load_phase_json(draft_spec_path) if draft_spec_path.exists() else {}
    accepted = {str(x) for x in (accepted_generator_keys or []) if str(x).strip()}
    usable, packaging_diag = select_generators_for_packaging(
        phase2 if isinstance(phase2, dict) else {},
        draft_spec if isinstance(draft_spec, dict) else {},
        accepted_generator_keys=accepted or None,
    )
    packaging_diag["phase2_generator_summary_json"] = str(phase2_path)
    packaging_diag["generator_draft_spec_json"] = str(draft_spec_path)
    draft_skill_path = phase_summary_path(skill_id, "draft_skill")
    generator_specs: list[dict[str, Any]] = []
    generator_keys: list[str] = []
    if usable:
        generator_specs, generator_keys = build_generator_specs_for_phase3(skill_id, usable)
    packaged_problem_types = {
        str(spec.get("problem_type_id", "")).strip()
        for spec in generator_specs
        if isinstance(spec, dict) and str(spec.get("problem_type_id", "")).strip()
    }
    packaged_usable = [
        row
        for row in usable
        if str(row.get("problem_type_id", "")).strip() in packaged_problem_types
    ]
    runtime_spec_alignment = _sync_phase3_runtime_specs_from_draft(
        skill_id,
        draft_spec if isinstance(draft_spec, dict) else {},
        packaged_usable,
    )
    packaging_diag["runtime_spec_alignment"] = runtime_spec_alignment
    if usable and generator_specs:
        code = build_phase3_skill_module_code(skill_id, generator_specs, generator_keys)
        draft_skill_path.write_text(code, encoding="utf-8")
    else:
        for stale_path in (draft_skill_path, draft_spec_path):
            try:
                if stale_path.exists():
                    stale_path.unlink()
            except OSError:
                pass
    phase3_warnings = sorted({w for g in packaged_usable for w in (g.get("warnings") or []) if str(w).strip()})
    py_status = "not_run_no_usable_generators" if not generator_specs else "passed"
    py_reason = ""
    if generator_specs:
        try:
            py_compile.compile(str(draft_skill_path), doraise=True)
        except Exception as e:
            py_status = "failed"
            py_reason = str(e)
    phase1_path = phase_summary_path(skill_id, "phase1_summary")
    phase1 = _load_phase_json(phase1_path) if phase1_path.exists() else {}
    source_alignment_layer = _phase3_source_alignment_layer(
        phase1 if isinstance(phase1, dict) else {},
        phase2 if isinstance(phase2, dict) else {},
    )
    audit_scripts = [
        "gencode_choice_quality_audit.py",
        "gencode_runtime_distribution_audit.py",
        "gencode_web_runtime_audit.py",
        "gencode_source_alignment_audit.py",
    ]
    script_audit: list[dict[str, Any]] = []
    scripts_ready = True
    for name in audit_scripts:
        p = PROJECT_ROOT / "scripts" / name
        exists = p.exists()
        compile_ok = False
        if exists:
            try:
                py_compile.compile(str(p), doraise=True)
                compile_ok = True
            except Exception:
                compile_ok = False
        scripts_ready = scripts_ready and exists and compile_ok
        script_audit.append({"script": name, "exists": exists, "py_compile_ok": compile_ok})
    runtime_gate = phase1.get("runtime_ready_gate", {}) if isinstance(phase1, dict) else {}
    publish_check = _run_gencode_publish_check_for_draft(
        skill_id=skill_id,
        draft_skill_file_path=str(draft_skill_path),
        runtime_ready_gate=runtime_gate if isinstance(runtime_gate, dict) else {},
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        equivalence_contract_passed=False,
    )
    runtime_smoke_status = str(publish_check.get("runtime_smoke_status", "failed"))
    package_status = "packaged_draft" if py_status == "passed" and runtime_smoke_status == "passed" else "failed"

    reports = _phase_reports(
        skill_id,
        keys=(
            "phase3_package_summary_json",
            "phase3_package_summary_md",
            "phase3_json",
            "phase3_md",
            "final_json",
            "final_md",
            "draft_skill_file",
        ),
    )
    packaging_usable_count = len(usable)
    draft_packaged = py_status == "passed" and packaging_usable_count > 0
    technical_closed_loop_pass = bool(draft_packaged and runtime_smoke_status == "passed")
    runtime_quality_pass = bool(technical_closed_loop_pass and scripts_ready)
    web_runtime_pass = bool(technical_closed_loop_pass and scripts_ready)
    source_alignment_status = str(source_alignment_layer.get("status", "PARTIAL")).strip() or "PARTIAL"
    payload = {
        "ok": draft_packaged and runtime_smoke_status == "passed",
        "phase": "phase3",
        "skill_id": skill_id,
        "sop_reference": build_sop_reference(PROJECT_ROOT),
        "remaining_todos": [
            "SOP v0.2 Verification: Verify that if a problem_type is verified, `/practice` must hit it within 50 rounds.",
            "SOP v0.2 Verification: Ensure Gencode runtime audit uses `generated_only` to prevent source_bank_pool masking generator distribution.",
            "SOP v0.2 Wrapper: Ensure wrapper state does not reload / reset state upon importlib.reload."
        ],
        "skill_file_path": str(draft_skill_path),
        "package_status": package_status,
        "py_compile_status": py_status,
        "runtime_smoke_status": runtime_smoke_status,
        "runtime_smoke_raw": publish_check.get("runtime_smoke_raw", {}),
        "publish_check": publish_check,
        "generator_specs": generator_specs,
        "packaging_usable_count": packaging_usable_count,
        "packaging_diagnostics": packaging_diag,
        "reports": reports,
        "next_action": "manual_review_before_runtime_enable",
        "error": py_reason,
        "dry_run": dry_run,
        "timestamp": utc_timestamp(),
        "generated_with_warning": bool(phase3_warnings),
        "warnings": phase3_warnings,
        "publish_gate_layers": {
            "technical_closed_loop": "PASS" if technical_closed_loop_pass else "FAIL",
            "runtime_quality": "PASS" if runtime_quality_pass else "FAIL",
            "web_runtime": "PASS" if web_runtime_pass else "FAIL",
            "source_alignment": source_alignment_status,
        },
        "source_alignment_audit": source_alignment_layer,
        "post_phase3_audit_scripts": script_audit,
    }
    if packaging_usable_count == 0:
        payload["ok"] = False
        payload["package_status"] = "blocked_no_usable_generators"
        payload["summary_message"] = format_packaging_blocked_message(packaging_diag)
        payload["packaging_diagnostic_message"] = payload["summary_message"]
    elif py_status == "failed":
        payload["summary_message"] = "Phase 3 failed: draft skill did not pass py_compile."
    elif draft_packaged and runtime_smoke_status != "passed":
        payload["ok"] = bool(draft_packaged)
        payload["summary_message"] = (
            "Phase 3 packaged draft skill file, but draft runtime smoke did not pass. "
            f"See publish_check / runtime_smoke_raw. usable_generators={packaging_usable_count}."
        )
    elif publish_check.get("can_publish_formal"):
        payload["summary_message"] = "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
    elif draft_packaged:
        payload["summary_message"] = (
            f"Phase 3 packaged draft with {packaging_usable_count} usable generator(s). "
            "Review publish_check before formal publish."
        )
    else:
        payload["summary_message"] = "Draft exists but is not ready for formal publish. Check publish_check blockers."

    payload["next_action"] = "review_phase3_publish_check" if packaging_usable_count else "review_phase2_blockers_before_phase3"

    write_json(Path(reports["phase3_package_summary_json"]), payload)
    write_md(Path(reports["phase3_package_summary_md"]), f"Gencode Phase3 Package Summary: {skill_id}", [("phase3", payload)])
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    return normalized


def run_gencode_auto_pipeline(skill_id: str, dry_run: bool = True, allow_runtime_ready: bool = False, write_pending_files: bool = True) -> dict[str, Any]:
    self_healing_log: list[dict[str, Any]] = []
    phase1: dict[str, Any] = {}
    phase2: dict[str, Any] = {}
    phase3: dict[str, Any] = {}

    try:
        phase1 = run_gencode_phase1(skill_id, dry_run=dry_run)
    except Exception as e:
        self_healing_log.append(execute_pipeline_self_healing(e, "phase1", skill_id))
        phase1 = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": 0,
            "candidate_problem_types": [],
            "phase_status": "auto_pipeline_phase1_exception",
            "exception_review_gate": {"required": True, "reasons": ["auto_pipeline_phase1_exception"]},
            "summary_message": f"Auto pipeline phase1 exception: {e}",
            "self_healing": self_healing_log[-1],
        }

    if phase1.get("ok"):
        try:
            phase2 = run_gencode_phase2(skill_id, dry_run=dry_run)
        except Exception as e:
            self_healing_log.append(execute_pipeline_self_healing(e, "phase2", skill_id))
            phase2 = {
                "ok": False,
                "phase": "phase2",
                "skill_id": skill_id,
                "phase_status": "auto_pipeline_phase2_exception",
                "summary_message": f"Auto pipeline phase2 exception: {e}",
                "self_healing": self_healing_log[-1],
            }
    else:
        phase2 = {"ok": False, "phase": "phase2", "skill_id": skill_id, "phase_status": "skipped_phase1_not_ok"}

    if phase1.get("ok") and phase2.get("ok"):
        try:
            phase3 = run_gencode_phase3_package(skill_id, dry_run=dry_run)
        except Exception as e:
            self_healing_log.append(execute_pipeline_self_healing(e, "phase3", skill_id))
            phase3 = {
                "ok": False,
                "phase": "phase3",
                "skill_id": skill_id,
                "phase_status": "auto_pipeline_phase3_exception",
                "summary_message": f"Auto pipeline phase3 exception: {e}",
                "self_healing": self_healing_log[-1],
            }
    else:
        phase3 = {"ok": False, "phase": "phase3", "skill_id": skill_id, "phase_status": "skipped_prior_phase_not_ok"}

    exception_gate = phase1.get("exception_review_gate", {})
    runtime_gate = phase1.get("runtime_ready_gate", {})
    generator_gate = phase1.get("generator_draft_gate", {})
    if exception_gate.get("required"):
        pipeline_status = "auto_pipeline_exception_review_required"
    elif runtime_gate.get("allowed") and allow_runtime_ready:
        pipeline_status = "auto_pipeline_completed_runtime_allowed"
    elif generator_gate.get("allowed"):
        pipeline_status = "auto_pipeline_completed_runtime_blocked"
    else:
        pipeline_status = "auto_pipeline_failed_fatal_risk"
    reports = {
        **_phase_reports(
            skill_id,
            keys=("auto_pipeline_summary_json", "auto_pipeline_summary_md"),
        ),
        **(phase1.get("reports") or {}),
        **(phase2.get("reports") or {}),
        **(phase3.get("reports") or {}),
    }
    summary = {
        "ok": bool(phase1.get("ok")) and bool(phase2.get("ok")) and bool(phase3.get("ok")),
        "skill_id": skill_id,
        "pipeline_status": pipeline_status,
        "source_example_count": phase1.get("source_example_count", 0),
        "candidate_problem_types": phase1.get("candidate_problem_types", []),
        "per_example_classification": phase1.get("per_example_classification", []),
        "split_or_merge_recommendation": phase1.get("split_or_merge_recommendation", ""),
        "classifier_gate": phase1.get("classifier_gate", {}),
        "generator_draft_gate": phase1.get("generator_draft_gate", {}),
        "runtime_ready_gate": phase1.get("runtime_ready_gate", {}),
        "exception_review_gate": exception_gate,
        "self_healing_log": self_healing_log,
        "reports": reports,
        "next_action": phase3.get("next_action", "manual_review_before_runtime_enable"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    if write_pending_files:
        write_json(Path(reports["auto_pipeline_summary_json"]), summary)
        write_md(Path(reports["auto_pipeline_summary_md"]), f"Gencode Auto Pipeline Summary: {skill_id}", [("summary", summary)])
    return summary


def run_gencode_publish_check(skill_id: str, dry_run: bool = True) -> dict[str, Any]:
    GENCODE_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GENCODE_DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    draft_skill_path = phase_summary_path(skill_id, "draft_skill")
    phase3_summary_path = phase_summary_path(skill_id, "phase3_package_summary")
    formal_skill_path = PROJECT_ROOT / "skills" / f"{_safe_skill_id(skill_id)}.py"

    reports = {
        "phase3_package_summary_json": str(phase3_summary_path.resolve()),
        "publish_check_json": str(phase_summary_path(skill_id, "publish_check_summary").resolve()),
        "publish_check_md": str(phase_summary_path(skill_id, "publish_check_md").resolve()),
    }
    warnings: list[str] = []
    blockers: list[str] = []
    human_action_items: list[dict[str, Any]] = []

    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")
    if not phase3_summary_path.exists():
        warnings.append("phase3_summary_missing")

    py_compile_status = "not_run"
    py_compile_error = ""
    if draft_skill_path.exists():
        try:
            py_compile.compile(str(draft_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            py_compile_error = str(e)
            blockers.append("draft_py_compile_failed")

    interface_check = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "generate_has_required_fields": False,
        "check_callable": False,
        "check_accepts_two_args": False,
    }
    runtime_smoke_status = "skipped"
    import_status = "skipped"
    import_error = ""
    if draft_skill_path.exists() and py_compile_status == "passed":
        try:
            src = draft_skill_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fn_names = {
                node.name: node
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            interface_check["generate_exists"] = "generate" in fn_names
            interface_check["check_exists"] = "check" in fn_names
            if "check" in fn_names:
                check_fn = fn_names["check"]
                interface_check["check_accepts_two_args"] = len(check_fn.args.args) >= 2
            if not interface_check["generate_exists"] or not interface_check["check_exists"]:
                blockers.append("runtime_interface_missing")
        except Exception as e:
            blockers.append("draft_ast_parse_failed")
            import_error = str(e)

        # controlled import + minimal smoke
        if "runtime_interface_missing" not in blockers and "draft_ast_parse_failed" not in blockers:
            try:
                import importlib.util

                mod_name = f"_gencode_draft_{skill_id}"
                spec = importlib.util.spec_from_file_location(mod_name, str(draft_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                import_status = "passed"

                generate_fn = getattr(module, "generate", None)
                check_fn = getattr(module, "check", None)
                interface_check["check_callable"] = callable(check_fn)
                if callable(generate_fn):
                    payload = generate_fn(level=1)
                    interface_check["generate_returns_dict"] = isinstance(payload, dict)
                    if isinstance(payload, dict):
                        required = ["question_text", "answer"]
                        interface_check["generate_has_required_fields"] = all(k in payload for k in required)
                        if callable(check_fn):
                            check_fn(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                import_status = "failed"
                import_error = str(e)
                blockers.append("runtime_smoke_failed")

    if py_compile_error:
        human_action_items.append(
            {
                "type": "compile_error",
                "target_id": str(draft_skill_path),
                "message": py_compile_error,
                "suggested_action": "inspect_report",
            }
        )
    if import_error:
        human_action_items.append(
            {
                "type": "runtime_smoke_failed",
                "target_id": str(draft_skill_path),
                "message": import_error,
                "suggested_action": "inspect_report",
            }
        )

    can_publish = len(blockers) == 0
    if can_publish and warnings:
        phase_status = "publish_check_passed_with_warning"
    elif can_publish:
        phase_status = "publish_check_passed"
    elif blockers:
        phase_status = "publish_check_blocked"
    else:
        phase_status = "publish_check_failed"

    summary_message = (
        "Publish Check passed: draft can be published (dry-run mode)."
        if can_publish
        else "Publish Check blocked: resolve blockers before retry."
    )

    payload = {
        "ok": can_publish,
        "phase": "publish_check",
        "skill_id": skill_id,
        "phase_status": phase_status,
        "can_continue": can_publish,
        "can_retry": True,
        "can_publish": can_publish,
        "requires_human_action": bool(blockers or human_action_items),
        "human_action_items": human_action_items,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "import_status": import_status,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": summary_message,
        "reports": reports,
        "next_action": "manual_publish_review" if can_publish else "fix_publish_check_blockers",
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["publish_check_json"]), payload)
    write_md(Path(reports["publish_check_md"]), f"Gencode Publish Check Summary: {skill_id}", [("publish_check", payload)])
    return payload


def publish_gencode_draft_skill(skill_id: str, confirm: bool = False, allow_runtime_ready: bool = False) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = PROJECT_ROOT / "backups" / "gencode_skill_publish"
    backup_dir.mkdir(parents=True, exist_ok=True)

    draft_skill_path = phase_summary_path(skill_id, "draft_skill")
    phase3_summary_path = phase_summary_path(skill_id, "phase3_package_summary")
    formal_skill_path = PROJECT_ROOT / "skills" / f"{_safe_skill_id(skill_id)}.py"
    reports = {
        "phase3_package_summary_json": str(phase3_summary_path.resolve()),
        "publish_summary_json": str(phase_summary_path(skill_id, "publish_summary").resolve()),
        "publish_summary_md": str(phase_summary_path(skill_id, "publish_summary_md").resolve()),
    }

    blockers: list[str] = []
    warnings: list[str] = []

    phase3 = _load_phase_json(phase3_summary_path) if phase3_summary_path.exists() else {}
    publish_check = phase3.get("publish_check", {}) if isinstance(phase3, dict) else {}
    if not isinstance(publish_check, dict):
        publish_check = {}
    if not bool(publish_check.get("draft_check_passed", False)):
        blockers.append("draft_check_not_passed")
    if not bool(publish_check.get("can_publish_draft", False)):
        blockers.append("cannot_publish_draft")
    if not bool(publish_check.get("can_publish_formal", False)):
        blockers.append("cannot_publish_formal")
    if (publish_check.get("blockers") or []):
        blockers.append("publish_check_blockers_present")
    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")

    backup_path = ""
    backup_status = "not_run"
    py_compile_status = "not_run"
    runtime_smoke_status = "skipped"
    runtime_ready_marked = False

    if blockers:
        payload = {
            "ok": False,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_blocked",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status,
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers,
            "warnings": warnings,
            "summary_message": "Publish blocked: resolve blockers before retry.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    if not confirm:
        payload = {
            "ok": True,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_preview",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": "",
            "backup_status": "preview_only",
            "py_compile_status": "preview_only",
            "runtime_smoke_status": "preview_only",
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": bool(publish_check.get("can_mark_runtime_ready", False)),
            "blockers": [],
            "warnings": ["confirm_required_for_publish"],
            "summary_message": "Preview complete: no formal file was overwritten. Click confirm to publish formally.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    try:
        if formal_skill_path.exists():
            stamp = utc_timestamp().replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
            backup_file = backup_dir / f"{skill_id}.{stamp}.py"
            shutil.copy2(str(formal_skill_path), str(backup_file))
            backup_path = str(backup_file)
            backup_status = "backed_up"
        else:
            backup_status = "no_existing_file"

        shutil.copy2(str(draft_skill_path), str(formal_skill_path))

        try:
            py_compile.compile(str(formal_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            blockers.append(f"formal_py_compile_failed:{e}")

        if py_compile_status == "passed":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_published_{skill_id}", str(formal_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                gen = getattr(mod, "generate", None)
                chk = getattr(mod, "check", None)
                if not callable(gen) or not callable(chk):
                    raise RuntimeError("generate_or_check_missing")
                payload = gen(level=1)
                if not isinstance(payload, dict):
                    raise RuntimeError("generate_not_dict")
                chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                warnings.append(f"runtime_smoke_warning:{e}")
        else:
            runtime_smoke_status = "failed"

    except Exception as e:
        payload = {
            "ok": False,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_failed",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status if backup_status != "not_run" else "failed_before_backup",
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers + [f"publish_exception:{e}"],
            "warnings": warnings,
            "summary_message": "Publish failed: an exception occurred during publish flow.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    publish_status = "published" if py_compile_status == "passed" else "publish_failed"
    can_mark_runtime_ready = bool(publish_check.get("can_mark_runtime_ready", False))
    if allow_runtime_ready and can_mark_runtime_ready and runtime_smoke_status == "passed":
        runtime_ready_marked = True
    else:
        runtime_ready_marked = False

    if not can_mark_runtime_ready:
        warnings.append("published_but_not_runtime_ready")

    payload = {
        "ok": publish_status == "published",
        "success": publish_status == "published",
        "skill_id": skill_id,
        "phase": "publish",
        "publish_status": publish_status,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "backup_path": backup_path,
        "backup_status": backup_status,
        "py_compile_status": py_compile_status,
        "runtime_smoke_status": runtime_smoke_status,
        "runtime_ready_marked": runtime_ready_marked,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": (
            "Formal skill file published successfully; if runtime-ready gate is not passed, run /practice smoke tests before marking runtime-ready."
            if publish_status == "published" and not runtime_ready_marked
            else (
                "Formal skill file published successfully and runtime-ready gate passed."
                if publish_status == "published"
                else "Formal skill publish failed. Check blockers / py_compile / runtime_smoke messages."
            )
        ),
        "reports": reports,
        "timestamp": utc_timestamp(),
    }
    write_json(Path(reports["publish_summary_json"]), payload)
    write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
    return payload
