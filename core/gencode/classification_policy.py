from __future__ import annotations

from collections import Counter
from typing import Any

from core.gencode.ai_semantic_classifier import (
    SemanticClassification,
    categorize_ai_unavailability,
    classify_example_semantics_with_ai,
)
from core.gencode.classification_candidates import (
    NEEDS_REVIEW_ID,
    build_skill_scoped_candidates,
    rule_fallback_candidate_selection,
)
from core.gencode.example_feature_extractor import extract_example_feature_rule_only
from core.gencode.source_structure_context import (
    apply_structure_confidence_adjustment,
    check_linked_example_consistency,
    detect_possible_mixed_source_context,
)
from core.gencode.task_families import task_family_for_task

AI_HIGH_CONFIDENCE = 0.75
AI_MED_CONFIDENCE = 0.45
RULE_LOW_CONFIDENCE = 0.40

AI_FIRST_MODES = frozenset(
    {
        "ai_first_induce_from_sources",
        "hybrid_ai_rule_validate",
    }
)
RULE_FIRST_MODES = frozenset({"rule_first_induce_from_sources", "induce_from_sources"})


def effective_classification_fields(feat: dict[str, Any]) -> tuple[str, str]:
    """Read final task/family from semantic trace when present."""
    sc = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
    task = str(sc.get("final_target_task") or feat.get("target_task") or "").strip()
    family = str(
        sc.get("final_task_family")
        or feat.get("task_family")
        or task_family_for_task(task)
    ).strip()
    return task, family


def apply_final_classification_to_feature(feat: dict[str, Any]) -> dict[str, Any]:
    row = dict(feat)
    task, family = effective_classification_fields(row)
    if task:
        row["target_task"] = task
        row["target"] = task
    if family:
        row["task_family"] = family
    return row


def apply_final_classification_to_features(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [apply_final_classification_to_feature(f) for f in features if isinstance(f, dict)]


def build_classification_diagnostic(
    feat: dict[str, Any],
    trace: dict[str, Any],
    main_skill_anchor: dict[str, Any],
    *,
    ai_semantic_status: str = "",
    alignment_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    align = alignment_row if isinstance(alignment_row, dict) else {}
    ai_reason = str(trace.get("ai_unavailable_reason") or categorize_ai_unavailability(str(trace.get("ai_error", "")))).strip()
    ai_status = str(trace.get("ai_semantic_status", "")).strip()
    if not ai_status:
        if trace.get("ai_available"):
            ai_status = "ok"
        elif ai_reason:
            ai_status = "unavailable"
        elif str(trace.get("ai_invalid_response_reason", "")).strip():
            ai_status = "invalid_response"
    return {
        "example_id": feat.get("source_example_id"),
        "rule_target_task": trace.get("rule_target_task", ""),
        "rule_task_family": trace.get("rule_task_family", ""),
        "rule_confidence": trace.get("rule_confidence", ""),
        "ai_target_task": trace.get("ai_target_task", ""),
        "ai_task_family": trace.get("ai_task_family", ""),
        "ai_confidence": trace.get("ai_confidence", ""),
        "ai_semantic_status": ai_semantic_status or ai_status,
        "ai_available": trace.get("ai_available", False),
        "ai_error": trace.get("ai_error", ""),
        "ai_unavailable_reason": ai_reason,
        "ai_invalid_response_reason": trace.get("ai_invalid_response_reason", ""),
        "parser_error": trace.get("parser_error", ""),
        "raw_response_preview": str(trace.get("raw_response_preview", "")),
        "sanitized_response_preview": str(trace.get("sanitized_response_preview", "")),
        "failed_stage": trace.get("failed_stage", ""),
        "classifier_source": trace.get("classifier_source", ""),
        "classification_decision": trace.get("classification_decision", ""),
        "final_target_task": trace.get("final_target_task", feat.get("target_task", "")),
        "final_task_family": trace.get("final_task_family", feat.get("task_family", "")),
        "expected_task_families": list(anchor.get("expected_task_families") or []),
        "expected_subskill_candidates": list(anchor.get("expected_subskill_candidates") or []),
        "structure_context_used": trace.get("structure_context_used", False),
        "sequence_context_used": trace.get("sequence_context_used", False),
        "alignment_kind": align.get("alignment_kind", ""),
        "exclude_reason": align.get("exclude_reason", ""),
        "included_in_phase1": align.get("included_in_phase1", True),
        "conflict_reason": trace.get("conflict_reason", ""),
        "source_mapping_warning": trace.get("source_mapping_warning", ""),
        "skill_anchor_scope": anchor.get("skill_anchor_scope", ""),
        "skill_scoped_candidates": trace.get("skill_scoped_candidates", []),
        "ai_best_candidate_id": trace.get("ai_best_candidate_id", ""),
        "selected_subskill": trace.get("selected_subskill", trace.get("final_target_task", "")),
        "selected_problem_type": trace.get("selected_problem_type", trace.get("final_target_task", "")),
        "candidate_source": trace.get("candidate_source", ""),
        "outsider_candidates": trace.get("outsider_candidates", []),
        "selected_generator_contract": trace.get("selected_generator_contract", {}),
        "parameter_schema": trace.get("parameter_schema", {}),
        "variable_randomization_notes": trace.get("variable_randomization_notes", []),
    }


def uses_ai_first_classification(spec_mode: str) -> bool:
    mode = str(spec_mode or "ai_first_induce_from_sources").strip()
    if mode in RULE_FIRST_MODES:
        return False
    return mode in AI_FIRST_MODES or mode == "" or mode == "ai_first_induce_from_sources"


def _rule_confidence(rule_feat: dict[str, Any]) -> float:
    task = str(rule_feat.get("target_task", "")).strip()
    text = str(rule_feat.get("question_text", "")).strip()
    if not task or task == "compute_numeric":
        return 0.2
    if task in {
        "compute_centroid_coordinates",
        "compute_midpoint_coordinates",
        "compute_internal_division_point_coordinates",
        "compute_external_division_point_coordinates",
        "solve_point_from_section_ratio",
    }:
        if any(k in text for k in ("重心", "中點", "中点", "內分", "内分", "外分", "AP", "PB", "分點")):
            return 0.55
        return 0.35
    if task in {"compute_distance_between_two_points", "solve_unknown_coordinate_from_two_point_distance"}:
        if any(k in text for k in ("距離", "距离", "長度", "长度", "\\overline")):
            return 0.55
        return 0.35
    if task == "classify_quadrant":
        return 0.7
    return 0.5


def _ai_to_rule_shape(ai: SemanticClassification) -> dict[str, Any]:
    return {
        "target_task": str(ai.get("target_task", "")).strip(),
        "task_family": str(ai.get("task_family", "")).strip(),
        "math_objects": list(ai.get("math_objects", []) or []),
        "answer_type": str(ai.get("answer_type", "")).strip(),
        "answer_shape": str(ai.get("answer_shape", "")).strip(),
        "confidence": float(ai.get("confidence", 0.0) or 0.0),
    }


def merge_skill_scoped_classification(
    ai_result: SemanticClassification,
    rule_result: dict[str, Any],
    main_skill_anchor: dict[str, Any] | None = None,
    *,
    skill_scoped_candidates: list[dict[str, Any]] | None = None,
    ex: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Skill-scoped merge: AI picks candidate_id within anchor; rule never overrides anchor AI.
    """
    # 1. Universal Self-Pollution Guard BEFORE merging traces
    pt_id_ai = ai_result.get("target_task") or ""
    pt_id_rule = rule_result.get("target_task") or ""
    problem_type_id = pt_id_ai or pt_id_rule

    if problem_type_id:
        for res in (ai_result, rule_result):
            if isinstance(res, dict):
                for eq_key in ("equivalence_type", "equivalence", "equivalence_type_proposal", "equivalence_proposal"):
                    if res.get(eq_key) == problem_type_id:
                        res[eq_key] = ""

    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    expected_families = set(anchor.get("expected_task_families") or [])
    candidates = skill_scoped_candidates or list(ai_result.get("skill_scoped_candidates") or [])
    outsider_ids = [
        str(c.get("candidate_id", ""))
        for c in candidates
        if isinstance(c, dict) and c.get("candidate_source") == "outsider"
    ]

    ai_semantic_status = str(ai_result.get("ai_semantic_status", "")).strip()
    ai_invalid_reason = str(ai_result.get("ai_invalid_response_reason", "")).strip()
    ai_available = bool(ai_result.get("available", False)) and not str(ai_result.get("error", "")).strip()
    ai_conf = float(ai_result.get("confidence", 0.0) or 0.0) if ai_available else 0.0
    cand_src = str(ai_result.get("candidate_source", "")).strip()
    ai_task = str(ai_result.get("target_task", "")).strip() if ai_available else ""
    ai_family = str(ai_result.get("task_family", "")).strip() or task_family_for_task(ai_task) if ai_task else ""
    best_cid = str(ai_result.get("best_candidate_id", "")).strip()

    rule_task = str(rule_result.get("target_task", "")).strip()
    rule_family = str(rule_result.get("task_family", "")).strip() or task_family_for_task(rule_task)
    rule_conf = _rule_confidence(rule_result)

    conflict_reason = ""
    requires_human_action = bool(ai_result.get("requires_human_action", False))
    classifier_source = ""
    classification_decision = ""
    source_mapping_warning = ""

    # Determine if there's a severe defect
    has_severe_defect = False
    for k in ["broken_latex", "missing_answer"]:
        if (
            (ex and bool(ex.get(k))) or
            bool(ai_result.get(k)) or
            bool(rule_result.get(k))
        ):
            has_severe_defect = True
            break

    expected_subskills = set(anchor.get("expected_subskill_candidates") or [])
    is_valid_task = (rule_task in expected_subskills) or (rule_family in expected_families)
    exact_legal_rule_match = bool(rule_task and is_valid_task and ai_task == rule_task)

    def _final_from_ai() -> dict[str, Any]:
        return {
            "target_task": ai_task,
            "task_family": ai_family,
            "math_objects": list(ai_result.get("math_objects") or rule_result.get("math_objects") or []),
            "answer_type": str(ai_result.get("answer_type") or rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(ai_result.get("answer_shape") or rule_result.get("answer_shape", "")).strip(),
        }

    if ai_semantic_status == "invalid_response" or ai_invalid_reason:
        classifier_source = "ai_invalid_response_needs_review"
        final = {
            "target_task": rule_task,
            "task_family": rule_family,
            "math_objects": list(rule_result.get("math_objects") or []),
            "answer_type": str(rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(rule_result.get("answer_shape", "")).strip(),
        }
        if rule_task and is_valid_task:
            classifier_source = "registry_rule"
            if not has_severe_defect:
                requires_human_action = False
                best_cid = rule_task
                cand_src = "rule"
            else:
                requires_human_action = True
                best_cid = NEEDS_REVIEW_ID
                cand_src = "needs_review"
        else:
            requires_human_action = True
            best_cid = NEEDS_REVIEW_ID
            cand_src = "needs_review"
        conflict_reason = ai_invalid_reason or str(ai_result.get("error", "invalid_response"))

    elif best_cid == NEEDS_REVIEW_ID or cand_src == "needs_review":
        final = _final_from_ai() if ai_task else {
            "target_task": rule_task,
            "task_family": rule_family,
            "math_objects": list(rule_result.get("math_objects") or []),
            "answer_type": str(rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(rule_result.get("answer_shape", "")).strip(),
        }
        classifier_source = "ai_needs_review"
        if not ai_task and rule_task and is_valid_task:
            classifier_source = "registry_rule"
            if not has_severe_defect:
                requires_human_action = False
                best_cid = rule_task
                cand_src = "rule"
            else:
                requires_human_action = True
        else:
            requires_human_action = True
        conflict_reason = "needs_review"

    elif not ai_available:
        fb = rule_fallback_candidate_selection(
            candidates,
            rule_result,
            ai_unavailable=True,
            ai_error=str(ai_result.get("error", "")),
        )
        classifier_source = "rule_fallback_ai_unavailable"
        fb_task = str(fb.get("target_task", "")).strip()
        fb_family = str(fb.get("task_family", "")).strip()
        final = {
            "target_task": fb_task or rule_task,
            "task_family": fb_family or rule_family,
            "math_objects": list(fb.get("math_objects") or rule_result.get("math_objects") or []),
            "answer_type": str(fb.get("answer_type", "")).strip() or str(rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(fb.get("answer_shape", "")).strip() or str(rule_result.get("answer_shape", "")).strip(),
        }
        if not fb_task and rule_task and is_valid_task:
            classifier_source = "registry_rule"

        cand_src = str(fb.get("candidate_source", "")).strip()
        best_cid = str(fb.get("best_candidate_id", "")).strip()
        ai_conf = float(fb.get("confidence", 0.0) or 0.0)

        # Honor Rulepack Authority
        is_rule = classifier_source in ("registry_rule", "rule_fallback_ai_unavailable")
        if is_rule and classifier_source == "registry_rule" and not has_severe_defect:
            requires_human_action = False
            if best_cid == NEEDS_REVIEW_ID:
                best_cid = final["target_task"]
                cand_src = "rule"
        else:
            if fb.get("requires_human_action"):
                requires_human_action = True

        conflict_reason = str(ai_result.get("error", "ai_unavailable"))

    elif cand_src == "outsider":
        classifier_source = "ai_outsider_candidate"
        final = _final_from_ai()
        source_mapping_warning = "outsider_candidate_within_confirmed_skill"
        requires_human_action = True
        if rule_family and rule_family != ai_family and rule_conf >= 0.35:
            conflict_reason = f"rule_family={rule_family}; ai_outsider={ai_family}"

    elif exact_legal_rule_match:
        final = {
            "target_task": rule_task,
            "task_family": rule_family,
            "math_objects": list(rule_result.get("math_objects") or ai_result.get("math_objects") or []),
            "answer_type": str(rule_result.get("answer_type") or ai_result.get("answer_type", "")).strip(),
            "answer_shape": str(rule_result.get("answer_shape") or ai_result.get("answer_shape", "")).strip(),
        }
        classifier_source = "registry_rule"
        classification_decision = "accepted_by_rule"
        requires_human_action = has_severe_defect
        best_cid = rule_task
        cand_src = "rule"

    elif ai_conf >= AI_HIGH_CONFIDENCE:
        final = _final_from_ai()
        classifier_source = "ai"
        if rule_family and ai_family and rule_family != ai_family and rule_conf >= 0.35:
            classifier_source = "ai_overrode_rule"
            conflict_reason = f"rule_family={rule_family}; ai_subskill={ai_task}"

    elif ai_conf >= AI_MED_CONFIDENCE and cand_src in {"anchor", "structure", "rule"}:
        final = _final_from_ai()
        classifier_source = "ai_rule_agree_family" if ai_family == rule_family else "ai_subskill_selected"
        if ai_task and rule_task and ai_task == rule_task:
            classifier_source = "hybrid_resolved"
        if ai_family and rule_family and ai_family != rule_family:
            conflict_reason = f"rule_family={rule_family}; ai_subskill={ai_task}"

    else:
        fb = rule_fallback_candidate_selection(candidates, rule_result, ai_unavailable=False, ai_error="low_ai_confidence")
        if fb.get("in_anchor_scope") and float(fb.get("confidence", 0) or 0) >= RULE_LOW_CONFIDENCE:
            classifier_source = "rule_fallback_low_ai_confidence"
            fb_task = str(fb.get("target_task", "")).strip()
            fb_family = str(fb.get("task_family", "")).strip()
            final = {
                "target_task": fb_task or rule_task,
                "task_family": fb_family or rule_family,
                "math_objects": list(fb.get("math_objects") or rule_result.get("math_objects") or []),
                "answer_type": str(fb.get("answer_type", "")).strip() or str(rule_result.get("answer_type", "")).strip(),
                "answer_shape": str(fb.get("answer_shape", "")).strip() or str(rule_result.get("answer_shape", "")).strip(),
            }
            if not fb_task and rule_task and is_valid_task:
                classifier_source = "registry_rule"
            cand_src = str(fb.get("candidate_source", "")).strip()
            best_cid = str(fb.get("best_candidate_id", "")).strip()

            # Honor Rulepack Authority
            is_rule = classifier_source in ("registry_rule", "rule_fallback_low_ai_confidence")
            if is_rule and classifier_source == "registry_rule" and not has_severe_defect:
                requires_human_action = False
                if best_cid == NEEDS_REVIEW_ID:
                    best_cid = final["target_task"]
                    cand_src = "rule"

        else:
            if rule_task and is_valid_task:
                classifier_source = "registry_rule"
                final = {
                    "target_task": rule_task,
                    "task_family": rule_family,
                    "math_objects": list(rule_result.get("math_objects") or []),
                    "answer_type": str(rule_result.get("answer_type", "")).strip(),
                    "answer_shape": str(rule_result.get("answer_shape", "")).strip(),
                }
                if not has_severe_defect:
                    requires_human_action = False
                    best_cid = rule_task
                    cand_src = "rule"
                else:
                    requires_human_action = True
                    best_cid = NEEDS_REVIEW_ID
                    cand_src = "needs_review"
            else:
                final = _final_from_ai() if ai_task else {
                    "target_task": str(fb.get("target_task", "")).strip(),
                    "task_family": str(fb.get("task_family", "")).strip(),
                    "math_objects": list(fb.get("math_objects") or []),
                    "answer_type": str(fb.get("answer_type", "")).strip(),
                    "answer_shape": str(fb.get("answer_shape", "")).strip(),
                }
                classifier_source = "ai_low_confidence_review"
                requires_human_action = True
                conflict_reason = "low_ai_confidence"

    # 2. Honor Rulepack Authority (Fix over-blocking leaks)
    is_rule_source = (classifier_source == "registry_rule")
    if is_rule_source:
        if not has_severe_defect:
            requires_human_action = False
            conflict_reason = ""
            if best_cid == NEEDS_REVIEW_ID or best_cid == "":
                best_cid = final["target_task"]
            if cand_src == "needs_review" or cand_src == "":
                cand_src = "rule"

    gc = dict(ai_result.get("generator_contract") or {})
    param_schema = dict(ai_result.get("parameter_schema") or {})
    var_notes = list(gc.get("variable_randomization_notes") or param_schema.get("variable_randomization_notes") or [])

    trace = {
        "ai_target_task": ai_task,
        "ai_task_family": ai_family,
        "ai_confidence": round(ai_conf, 4),
        "ai_best_candidate_id": best_cid,
        "ai_evidence": list(ai_result.get("evidence") or []),
        "ai_rejected_candidates": dict(ai_result.get("rejected_candidates") or {}),
        "ai_available": ai_available,
        "ai_error": str(ai_result.get("error", "")).strip(),
        "ai_unavailable_reason": (
            ""
            if classifier_source == "ai_invalid_response_needs_review"
            else str(
                ai_result.get("ai_unavailable_reason")
                or categorize_ai_unavailability(str(ai_result.get("error", "")))
            ).strip()
        ),
        "ai_semantic_status": ai_semantic_status
        or ("ok" if ai_available else ("invalid_response" if classifier_source == "ai_invalid_response_needs_review" else "")),
        "ai_invalid_response_reason": ai_invalid_reason,
        "parser_error": str(ai_result.get("parser_error", "")),
        "raw_response_preview": str(ai_result.get("raw_response_preview", "")),
        "sanitized_response_preview": str(ai_result.get("sanitized_response_preview", "")),
        "failed_stage": str(ai_result.get("failed_stage", "")),
        "rule_target_task": rule_task,
        "rule_task_family": rule_family,
        "rule_confidence": round(rule_conf, 4),
        "final_target_task": final["target_task"],
        "final_task_family": final["task_family"],
        "classifier_source": classifier_source,
        "classification_decision": classification_decision,
        "conflict_reason": conflict_reason,
        "source_mapping_warning": source_mapping_warning,
        "requires_human_action": requires_human_action,
        "ai_notes": str(ai_result.get("notes", "")).strip(),
        "skill_scoped_candidates": candidates,
        "outsider_candidates": outsider_ids,
        "selected_subskill": final["target_task"],
        "selected_problem_type": final["target_task"],
        "candidate_source": cand_src,
        "selected_generator_contract": gc,
        "parameter_schema": param_schema,
        "variable_randomization_notes": var_notes,
        "checker_key": str(ai_result.get("checker_key", "")).strip(),
        "equivalence_type": str(ai_result.get("equivalence_type", "")).strip(),
        "skill_scope_trusted": True,
    }
    return {**trace, **final}


def merge_ai_and_rule_classification(
    ai_result: SemanticClassification,
    rule_result: dict[str, Any],
    main_skill_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge AI and rule classifications. Rule never overrides high-confidence AI.
    Returns trace fields for Phase 1 summary plus final feature fields.
    """
    # Universal Self-Pollution Guard BEFORE merging traces
    pt_id_ai = ai_result.get("target_task") or ""
    pt_id_rule = rule_result.get("target_task") or ""
    problem_type_id = pt_id_ai or pt_id_rule

    if problem_type_id:
        for res in (ai_result, rule_result):
            if isinstance(res, dict):
                for eq_key in ("equivalence_type", "equivalence", "equivalence_type_proposal", "equivalence_proposal"):
                    if res.get(eq_key) == problem_type_id:
                        res[eq_key] = ""

    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    expected_families = set(anchor.get("expected_task_families") or [])

    ai_available = bool(ai_result.get("available", False)) and not str(ai_result.get("error", "")).strip()
    ai_conf = float(ai_result.get("confidence", 0.0) or 0.0) if ai_available else 0.0
    ai_task = str(ai_result.get("target_task", "")).strip() if ai_available else ""
    ai_family = str(ai_result.get("task_family", "")).strip() or task_family_for_task(ai_task) if ai_task else ""

    rule_task = str(rule_result.get("target_task", "")).strip()
    rule_family = str(rule_result.get("task_family", "")).strip() or task_family_for_task(rule_task)
    rule_conf = _rule_confidence(rule_result)

    conflict_reason = ""
    requires_human_action = bool(ai_result.get("requires_human_action", False))
    classifier_source = ""
    source_mapping_warning = ""

    # Determine if there's a severe defect
    has_severe_defect = False
    for k in ["broken_latex", "missing_answer"]:
        if (
            bool(ai_result.get(k)) or
            bool(rule_result.get(k))
        ):
            has_severe_defect = True
            break

    def _final_from_ai() -> dict[str, Any]:
        return {
            "target_task": ai_task,
            "task_family": ai_family,
            "math_objects": list(ai_result.get("math_objects") or rule_result.get("math_objects") or []),
            "answer_type": str(ai_result.get("answer_type") or rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(ai_result.get("answer_shape") or rule_result.get("answer_shape", "")).strip(),
        }

    def _final_from_rule() -> dict[str, Any]:
        return {
            "target_task": rule_task,
            "task_family": rule_family,
            "math_objects": list(rule_result.get("math_objects") or []),
            "answer_type": str(rule_result.get("answer_type", "")).strip(),
            "answer_shape": str(rule_result.get("answer_shape", "")).strip(),
        }

    if not ai_available:
        classifier_source = "rule_fallback_ai_unavailable"
        final = _final_from_rule()
        if rule_conf < RULE_LOW_CONFIDENCE:
            requires_human_action = True
            conflict_reason = str(ai_result.get("error", "ai_unavailable"))
    elif ai_conf >= AI_HIGH_CONFIDENCE:
        final = _final_from_ai()
        classifier_source = "ai"
        if rule_family and ai_family and rule_family != ai_family and rule_conf >= 0.35:
            classifier_source = "ai_overrode_rule"
            conflict_reason = f"rule_family={rule_family}; ai_family={ai_family}"
    elif ai_conf >= AI_MED_CONFIDENCE:
        final = _final_from_ai()
        if ai_family and rule_family and ai_family == rule_family:
            classifier_source = "ai_rule_agree_family"
        else:
            classifier_source = "ai_rule_conflict_review"
            requires_human_action = True
            conflict_reason = f"rule_family={rule_family}; ai_family={ai_family}"
    else:
        classifier_source = "rule_fallback_low_ai_confidence"
        final = _final_from_rule()
        if rule_conf < RULE_LOW_CONFIDENCE:
            requires_human_action = True
            conflict_reason = "low_ai_and_rule_confidence"

    # 2. Honor Rulepack Authority (Fix over-blocking leaks)
    expected_subskills = set(anchor.get("expected_subskill_candidates") or [])
    is_valid_task = (rule_task in expected_subskills) or (rule_family in expected_families)
    if rule_task and is_valid_task:
        classifier_source = "registry_rule"
    is_rule_source = (classifier_source == "registry_rule")

    if is_rule_source and not has_severe_defect:
        requires_human_action = False
        conflict_reason = ""

    if expected_families and final.get("task_family") and final["task_family"] not in expected_families:
        source_mapping_warning = "expected_family_mismatch"
        if ai_conf >= AI_HIGH_CONFIDENCE:
            requires_human_action = True
            if not conflict_reason:
                conflict_reason = source_mapping_warning

    trace = {
        "ai_target_task": ai_task,
        "ai_task_family": ai_family,
        "ai_confidence": round(ai_conf, 4),
        "ai_evidence": list(ai_result.get("evidence") or []),
        "ai_negative_evidence": dict(ai_result.get("negative_evidence") or {}),
        "ai_available": ai_available,
        "ai_error": str(ai_result.get("error", "")).strip(),
        "ai_unavailable_reason": str(
            ai_result.get("ai_unavailable_reason") or categorize_ai_unavailability(str(ai_result.get("error", "")))
        ).strip(),
        "rule_target_task": rule_task,
        "rule_task_family": rule_family,
        "rule_confidence": round(rule_conf, 4),
        "final_target_task": final["target_task"],
        "final_task_family": final["task_family"],
        "classifier_source": classifier_source,
        "conflict_reason": conflict_reason,
        "source_mapping_warning": source_mapping_warning,
        "requires_human_action": requires_human_action,
        "ai_notes": str(ai_result.get("notes", "")).strip(),
    }
    return {**trace, **final}


def _attach_structure_fields(
    trace: dict[str, Any],
    ex: dict[str, Any],
    ai_result: SemanticClassification,
    *,
    classifications_by_id: dict[int, dict[str, Any]] | None = None,
    main_skill_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ctx = ex.get("source_structure_context") if isinstance(ex.get("source_structure_context"), dict) else {}
    seq_used = bool(ctx.get("same_section_sequence") or ctx.get("linked_worked_example"))
    struct_used = bool(
        ctx.get("linked_example")
        or ctx.get("example_label")
        or ctx.get("practice_label")
        or ctx.get("nearby_worked_examples")
    )
    linked_id = None
    linked_row = ctx.get("linked_worked_example")
    if isinstance(linked_row, dict):
        linked_id = linked_row.get("example_id")
    linked_family = ""
    if linked_id is not None and classifications_by_id:
        linked_family = str((classifications_by_id.get(int(linked_id)) or {}).get("final_task_family", "")).strip()

    consistency = check_linked_example_consistency(
        structure_ctx=ctx,
        current_task_family=str(trace.get("final_task_family", "")),
        linked_task_family=linked_family,
    )
    section_counts: Counter[str] = Counter()
    if classifications_by_id:
        for row in classifications_by_id.values():
            fam = str(row.get("final_task_family", "")).strip()
            if fam:
                section_counts[fam] += 1
    possible_mixed = detect_possible_mixed_source_context(
        current_task_family=str(trace.get("final_task_family", "")),
        structure_ctx=ctx,
        section_family_counts=section_counts,
    ) or bool(ai_result.get("possible_structure_mismatch"))

    adj_conf, conf_reason = apply_structure_confidence_adjustment(
        ai_result,
        ctx,
        structure_consistency=str(consistency.get("structure_consistency", "unknown")),
        possible_structure_mismatch=possible_mixed,
    )
    if trace.get("ai_available"):
        trace["ai_confidence"] = round(adj_conf, 4)

    requires_human = bool(trace.get("requires_human_action"))
    if consistency.get("requires_human_action"):
        requires_human = True
    if possible_mixed and not requires_human and float(trace.get("ai_confidence", 0) or 0) < AI_HIGH_CONFIDENCE:
        requires_human = True

    # Honor Rulepack Authority: do not force requires_human to True
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    expected_families = set(anchor.get("expected_task_families") or [])
    expected_subskills = set(anchor.get("expected_subskill_candidates") or [])
    
    final_task = str(trace.get("final_target_task", "")).strip()
    final_family = str(trace.get("final_task_family", "")).strip()
    is_valid_task = (final_task in expected_subskills) or (final_family in expected_families)

    is_rule_source = (trace.get("classifier_source") == "registry_rule") and is_valid_task
    if is_rule_source and trace.get("final_target_task"):
        has_severe_defect = False
        for k in ["broken_latex", "missing_answer"]:
            if (
                bool(ex.get(k)) or
                bool(ai_result.get(k)) or
                bool(trace.get(k))
            ):
                has_severe_defect = True
                break
        if not has_severe_defect:
            requires_human = False

    trace.update(
        {
            "source_type": ctx.get("source_type", ""),
            "example_label": ctx.get("example_label", ""),
            "practice_label": ctx.get("practice_label", ""),
            "linked_example": ctx.get("linked_example", ""),
            "linked_example_id": consistency.get("linked_example_id"),
            "linked_example_task_family": consistency.get("linked_example_task_family", ""),
            "structure_consistency": consistency.get("structure_consistency", "unknown"),
            "sequence_context_used": seq_used,
            "structure_context_used": struct_used,
            "confidence_adjustment_reason": conf_reason,
            "possible_structure_mismatch": possible_mixed,
            "possible_mixed_source_context": possible_mixed,
            "requires_human_action": requires_human,
        }
    )
    return trace


def build_classified_example_feature(
    ex: dict[str, Any],
    main_skill_anchor: dict[str, Any],
    *,
    spec_mode: str = "ai_first_induce_from_sources",
    ai_classify_fn: Any = None,
    classifications_by_id: dict[int, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Build example feature dict plus semantic classification trace for Phase 1.
    """
    rule_feat = extract_example_feature_rule_only(ex)
    rule_snapshot = {
        "target_task": rule_feat.get("target_task"),
        "task_family": rule_feat.get("task_family"),
        "math_objects": rule_feat.get("math_objects"),
        "answer_type": rule_feat.get("answer_type"),
        "answer_shape": rule_feat.get("answer_shape"),
        "question_text": rule_feat.get("question_text"),
    }

    if not uses_ai_first_classification(spec_mode):
        trace = merge_ai_and_rule_classification(
            {
                "available": False,
                "error": "rule_first_mode",
                "confidence": 0.0,
                "target_task": "",
                "task_family": "",
            },
            rule_snapshot,
            main_skill_anchor,
        )
        trace["classifier_source"] = "rule_first_mode"
        trace = _attach_structure_fields(trace, ex, {}, classifications_by_id=classifications_by_id, main_skill_anchor=main_skill_anchor)
        feat = dict(rule_feat)
        feat["classifier_source"] = trace["classifier_source"]
        feat["semantic_classification"] = trace
        feat["source_structure_context"] = ex.get("source_structure_context", {})
        return feat, trace

    candidates = build_skill_scoped_candidates(
        main_skill_anchor,
        ex,
        rule_snapshot,
        classifications_by_id=classifications_by_id,
    )
    ex_run = dict(ex)
    ex_run["_skill_scoped_candidates"] = candidates

    classify = ai_classify_fn or classify_example_semantics_with_ai
    ai_result = dict(
        classify(ex_run, main_skill_anchor, skill_scoped_candidates=candidates)
    )
    if str(ai_result.get("best_candidate_id", "")).strip() and ai_result.get("best_candidate_id") != NEEDS_REVIEW_ID:
        if not str(ai_result.get("error", "")).strip():
            ai_result["available"] = True
    elif str(ai_result.get("target_task", "")).strip() and not str(ai_result.get("error", "")).strip():
        ai_result["available"] = True
    else:
        ai_result["available"] = bool(ai_result.get("available")) and bool(ai_result.get("target_task"))
    if (
        not ai_result.get("ai_unavailable_reason")
        and not ai_result.get("available")
        and str(ai_result.get("ai_semantic_status", "")) != "invalid_response"
    ):
        ai_result["ai_unavailable_reason"] = categorize_ai_unavailability(str(ai_result.get("error", "")))
    ai_result["skill_scoped_candidates"] = candidates

    merged = merge_skill_scoped_classification(
        ai_result,
        rule_snapshot,
        main_skill_anchor,
        skill_scoped_candidates=candidates,
        ex=ex,
    )
    merged = _attach_structure_fields(
        merged,
        ex,
        ai_result,
        classifications_by_id=classifications_by_id,
        main_skill_anchor=main_skill_anchor,
    )
    feat = dict(rule_feat)
    feat["target_task"] = merged["final_target_task"]
    feat["task_family"] = merged["final_task_family"]
    feat["target"] = merged["final_target_task"]
    if merged.get("math_objects"):
        feat["math_objects"] = merged["math_objects"]
    if merged.get("answer_type"):
        feat["answer_type"] = merged["answer_type"]
    if merged.get("answer_shape"):
        feat["answer_shape"] = merged["answer_shape"]
    feat["classifier_source"] = merged["classifier_source"]
    feat["semantic_classification"] = merged
    feat["source_structure_context"] = ex.get("source_structure_context", {})

    # 3. Multi-Modal Signature Splitting Guard
    ans_type = str(merged.get("answer_type") or feat.get("answer_type", "")).strip().lower()
    is_numeric_sig = ans_type in ("numeric", "integer", "rational", "decimal_tolerance", "percentage_equivalent")
    is_symbolic_sig = ans_type in ("expression", "text_short", "exact_string", "case_insensitive_string", "manual_review_or_ai_judged")

    curr_task = str(merged.get("final_target_task") or feat.get("target_task", "")).strip()
    if curr_task:
        if is_numeric_sig:
            # Numeric evaluation signature
            if "interpret" in curr_task:
                new_task = curr_task.replace("interpret", "evaluate")
                if "numeric" not in new_task:
                    new_task = "numeric_" + new_task
                merged["final_target_task"] = new_task
                feat["target_task"] = new_task
                feat["target"] = new_task
            elif "symbolic" in curr_task:
                new_task = curr_task.replace("symbolic", "numeric")
                merged["final_target_task"] = new_task
                feat["target_task"] = new_task
                feat["target"] = new_task
        elif is_symbolic_sig:
            # Symbolic notation signature
            if "numeric" in curr_task:
                new_task = curr_task.replace("numeric_", "").replace("numeric", "")
                if "symbolic" not in new_task:
                    new_task = "symbolic_" + new_task
                merged["final_target_task"] = new_task
                feat["target_task"] = new_task
                feat["target"] = new_task
            elif "evaluate" in curr_task:
                new_task = curr_task.replace("evaluate", "interpret")
                if "symbolic" not in new_task:
                    new_task = "symbolic_" + new_task
                merged["final_target_task"] = new_task
                feat["target_task"] = new_task
                feat["target"] = new_task

    feat = apply_final_classification_to_feature(feat)
    ex_id = feat.get("source_example_id")
    if classifications_by_id is not None and ex_id is not None:
        try:
            classifications_by_id[int(ex_id)] = merged
        except (TypeError, ValueError):
            pass
    return feat, merged
