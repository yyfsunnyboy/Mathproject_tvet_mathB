# -*- coding: utf-8 -*-
"""Skill-scoped subskill / problem_type candidates for Phase 1 classification."""

from __future__ import annotations

from typing import Any

from core.gencode.generator_contract_schema import enrich_generator_contract
from core.gencode.main_skill_anchor import example_skill_id_mismatch
from core.gencode.task_families import (
    DIVISION_POINT_COORDINATES_FAMILY,
    DIVISION_POINT_COORDINATES_TASKS,
    task_family_for_task,
)

NEEDS_REVIEW_ID = "needs_review"

_CHECKER_BY_ANSWER_TYPE: dict[str, tuple[str, str]] = {
    "ordered_pair": ("coordinate_pair_checker", "coordinate_pair_equivalence"),
    "coordinate_pair": ("coordinate_pair_checker", "coordinate_pair_equivalence"),
    "numeric": ("numeric_checker", "numeric_equivalence"),
    "single_choice": ("choice_label_checker", "choice_label"),
    "expression": ("expression_equivalence_checker", "expression_equivalence"),
    "interval": ("interval_checker", "interval_set"),
    "text": ("text_checker", "string_equivalence"),
}


def build_generator_contract_for_task(
    target_task: str,
    *,
    answer_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Task-driven generator_contract blueprint (see generator_contract_schema)."""
    return enrich_generator_contract(target_task, None, answer_contract=answer_contract)


def build_parameter_schema(generator_contract: dict[str, Any]) -> dict[str, Any]:
    gc = generator_contract if isinstance(generator_contract, dict) else {}
    ps = gc.get("parameter_schema")
    if isinstance(ps, dict) and ps:
        return dict(ps)
    schema: dict[str, Any] = {"randomizable_fields": [], "constraints": []}
    for key in ("point_names", "ratio", "coordinate_range", "point_count", "distance_result_type"):
        if key in gc:
            schema["randomizable_fields"].append(key)
    vc = gc.get("validity_constraints")
    if isinstance(vc, list):
        schema["constraints"].extend([str(v) for v in vc if str(v).strip()])
    return schema


def _default_answer_fields(target_task: str) -> tuple[str, str, list[str]]:
    task = str(target_task or "").strip()
    if task == "compute_centroid_coordinates":
        return "ordered_pair", "coordinate_pair", ["three_coordinate_points", "triangle_vertices", "coordinate_average_reasoning"]
    if task == "compute_midpoint_coordinates":
        return "ordered_pair", "coordinate_pair", ["two_coordinate_points", "midpoint"]
    if task in DIVISION_POINT_COORDINATES_TASKS or task_family_for_task(task) == DIVISION_POINT_COORDINATES_FAMILY:
        return "ordered_pair", "coordinate_pair", ["two_coordinate_points", "section_ratio"]
    if task == "classify_quadrant":
        return "single_choice", "choice_label", ["coordinate_point"]
    if task in {"quadratic_vertex_form_properties", "quadratic_standard_to_vertex_properties"}:
        return "single_choice", "choice_label", ["quadratic_equation", "quadratic_vertex_form"]
    if task == "quadratic_vertex_or_parameter_computation":
        return "numeric", "numeric", ["quadratic_equation", "quadratic_vertex_form", "parameter"]
    if task in {"quadratic_vertex_form_translation_to_new_function", "quadratic_graph_translation_fill_blank"}:
        return "text", "text_short", ["quadratic_equation", "quadratic_vertex_form", "quadratic_translation"]
    return "numeric", "numeric", []


def _checker_fields(answer_type: str) -> tuple[str, str]:
    return _CHECKER_BY_ANSWER_TYPE.get(answer_type, ("text_checker", "string_equivalence"))


def _candidate_record(
    candidate_id: str,
    target_task: str,
    *,
    candidate_source: str,
    in_anchor_scope: bool,
    label: str = "",
) -> dict[str, Any]:
    task = str(target_task or "").strip()
    family = task_family_for_task(task) if task and task != NEEDS_REVIEW_ID else ""
    if task == NEEDS_REVIEW_ID:
        return {
            "candidate_id": NEEDS_REVIEW_ID,
            "target_task": "",
            "task_family": "",
            "problem_type_id": NEEDS_REVIEW_ID,
            "label": label or "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": False,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {},
        }
    answer_type, answer_shape, math_objects = _default_answer_fields(task)
    checker_key, equivalence_type = _checker_fields(answer_type)
    gc = build_generator_contract_for_task(task, answer_contract=None)
    return {
        "candidate_id": candidate_id,
        "target_task": task,
        "task_family": family,
        "problem_type_id": task,
        "label": label or task,
        "candidate_source": candidate_source,
        "in_anchor_scope": in_anchor_scope,
        "answer_type": answer_type,
        "answer_shape": answer_shape,
        "math_objects": math_objects,
        "checker_key": checker_key,
        "equivalence_type": equivalence_type,
        "generator_contract": gc,
        "parameter_schema": build_parameter_schema(gc),
    }


def _task_in_anchor(task: str, anchor: dict[str, Any]) -> bool:
    t = str(task or "").strip()
    if not t:
        return False
    expected_subskills = {str(x).strip() for x in (anchor.get("expected_subskill_candidates") or []) if str(x).strip()}
    if t in expected_subskills:
        return True
    expected_families = set(anchor.get("expected_task_families") or [])
    fam = task_family_for_task(t)
    return bool(fam and fam in expected_families)


def build_skill_scoped_candidates(
    main_skill_anchor: dict[str, Any],
    example: dict[str, Any],
    rule_feature: dict[str, Any] | None = None,
    *,
    classifications_by_id: dict[int, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Build ordered skill-scoped candidates for AI selection.
    Priority: anchor subskills → structure-linked → rule (anchor or outsider) → needs_review.
    """
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    rule = rule_feature if isinstance(rule_feature, dict) else {}
    expected_subskills = [
        str(t).strip()
        for t in (anchor.get("expected_subskill_candidates") or [])
        if str(t).strip() and not str(t).endswith("_family")
    ]
    seen_tasks: set[str] = set()
    candidates: list[dict[str, Any]] = []
    idx = 1

    def _add(task: str, source: str, in_scope: bool | None = None) -> None:
        nonlocal idx
        t = str(task or "").strip()
        if not t or t in seen_tasks:
            return
        scope = _task_in_anchor(t, anchor) if in_scope is None else bool(in_scope)
        cid = f"C{idx}"
        idx += 1
        seen_tasks.add(t)
        candidates.append(_candidate_record(cid, t, candidate_source=source, in_anchor_scope=scope))

    for task in expected_subskills:
        _add(task, "anchor", True)

    ctx = example.get("source_structure_context") if isinstance(example.get("source_structure_context"), dict) else {}
    linked = ctx.get("linked_worked_example")
    if isinstance(linked, dict) and classifications_by_id:
        linked_id = linked.get("example_id")
        try:
            lid = int(linked_id)
        except (TypeError, ValueError):
            lid = None
        if lid is not None:
            row = classifications_by_id.get(lid) or {}
            linked_task = str(row.get("final_target_task") or row.get("target_task") or "").strip()
            if linked_task:
                _add(linked_task, "structure", _task_in_anchor(linked_task, anchor))

    for row in ctx.get("nearby_worked_examples") or []:
        if not isinstance(row, dict):
            continue
        n_id = row.get("example_id")
        try:
            nid = int(n_id)
        except (TypeError, ValueError):
            continue
        if classifications_by_id and nid in classifications_by_id:
            n_task = str(
                (classifications_by_id[nid] or {}).get("final_target_task")
                or (classifications_by_id[nid] or {}).get("target_task")
                or ""
            ).strip()
            if n_task:
                _add(n_task, "structure", _task_in_anchor(n_task, anchor))

    rule_task = str(rule.get("target_task") or "").strip()
    if rule_task:
        if _task_in_anchor(rule_task, anchor):
            _add(rule_task, "rule", True)
        else:
            _add(rule_task, "outsider", False)

    candidates.append(_candidate_record(NEEDS_REVIEW_ID, NEEDS_REVIEW_ID, candidate_source="needs_review", in_anchor_scope=False))
    return candidates


def find_candidate_by_id(candidates: list[dict[str, Any]], candidate_id: str) -> dict[str, Any] | None:
    cid = str(candidate_id or "").strip()
    for row in candidates:
        if isinstance(row, dict) and str(row.get("candidate_id", "")).strip() == cid:
            return row
    if cid == NEEDS_REVIEW_ID:
        for row in candidates:
            if isinstance(row, dict) and row.get("candidate_id") == NEEDS_REVIEW_ID:
                return row
    return None


def find_candidate_by_task(candidates: list[dict[str, Any]], target_task: str) -> dict[str, Any] | None:
    task = str(target_task or "").strip()
    anchor_first = [c for c in candidates if isinstance(c, dict) and c.get("candidate_source") == "anchor"]
    for row in anchor_first + candidates:
        if isinstance(row, dict) and str(row.get("target_task", "")).strip() == task:
            return row
    return None


def classification_from_candidate(
    candidate: dict[str, Any],
    *,
    confidence: float = 0.0,
    evidence: list[str] | None = None,
    rejected_candidates: dict[str, str] | None = None,
    requires_human_action: bool = False,
    notes: str = "",
    available: bool = True,
    error: str = "",
    ai_unavailable_reason: str = "",
) -> dict[str, Any]:
    cand = candidate if isinstance(candidate, dict) else {}
    cid = str(cand.get("candidate_id", "")).strip()
    is_review = cid == NEEDS_REVIEW_ID
    return {
        "best_candidate_id": cid,
        "target_task": str(cand.get("target_task", "")).strip(),
        "task_family": str(cand.get("task_family", "")).strip(),
        "problem_type_id": str(cand.get("problem_type_id") or cand.get("target_task", "")).strip(),
        "math_objects": list(cand.get("math_objects") or []),
        "answer_type": str(cand.get("answer_type", "")).strip(),
        "answer_shape": str(cand.get("answer_shape", "")).strip(),
        "checker_key": str(cand.get("checker_key", "")).strip(),
        "equivalence_type": str(cand.get("equivalence_type", "")).strip(),
        "generator_contract": dict(cand.get("generator_contract") or {}),
        "parameter_schema": dict(cand.get("parameter_schema") or {}),
        "candidate_source": str(cand.get("candidate_source", "")).strip(),
        "in_anchor_scope": bool(cand.get("in_anchor_scope")),
        "selected_subskill": str(cand.get("target_task", "")).strip(),
        "confidence": max(0.0, min(1.0, float(confidence or 0.0))),
        "evidence": list(evidence or []),
        "rejected_candidates": dict(rejected_candidates or {}),
        "requires_human_action": requires_human_action or is_review,
        "notes": notes,
        "available": available and not is_review and bool(cand.get("target_task")),
        "error": error,
        "ai_unavailable_reason": ai_unavailable_reason,
    }


def apply_ai_candidate_selection(
    ai_raw: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Map AI best_candidate_id (or legacy target_task) to a full classification."""
    raw = ai_raw if isinstance(ai_raw, dict) else {}
    cid = str(raw.get("best_candidate_id", "")).strip()
    cand = find_candidate_by_id(candidates, cid) if cid else None
    if cand is None:
        legacy_task = str(raw.get("target_task", "")).strip()
        if legacy_task:
            cand = find_candidate_by_task(candidates, legacy_task)
    if cand is None:
        return classification_from_candidate(
            find_candidate_by_id(candidates, NEEDS_REVIEW_ID) or _candidate_record(NEEDS_REVIEW_ID, NEEDS_REVIEW_ID, candidate_source="needs_review", in_anchor_scope=False),
            confidence=float(raw.get("confidence", 0.0) or 0.0),
            evidence=list(raw.get("evidence") or []),
            rejected_candidates=dict(raw.get("rejected_candidates") or {}),
            requires_human_action=True,
            notes=str(raw.get("notes", "unknown_candidate_id")),
            available=False,
            error="unknown_candidate_id",
        )
    try:
        conf = float(raw.get("confidence", 0.0) or 0.0)
    except Exception:
        conf = 0.0
    rejected = raw.get("rejected_candidates", {})
    if not isinstance(rejected, dict):
        rejected = {}
    out = classification_from_candidate(
        cand,
        confidence=conf,
        evidence=list(raw.get("evidence") or []),
        rejected_candidates={str(k): str(v) for k, v in rejected.items()},
        requires_human_action=bool(raw.get("requires_human_action", False)),
        notes=str(raw.get("notes", "")).strip(),
        available=cid != NEEDS_REVIEW_ID,
    )
    out["skill_scoped_candidates"] = candidates
    return out


def rule_fallback_candidate_selection(
    candidates: list[dict[str, Any]],
    rule_feature: dict[str, Any],
    *,
    ai_unavailable: bool = True,
    ai_error: str = "",
) -> dict[str, Any]:
    """Pick best anchor-scoped rule match; never promote outsider as final when anchor options exist."""
    rule_task = str((rule_feature or {}).get("target_task", "")).strip()
    anchor_candidates = [c for c in candidates if isinstance(c, dict) and c.get("in_anchor_scope") and c.get("candidate_id") != NEEDS_REVIEW_ID]
    cand = find_candidate_by_task(candidates, rule_task) if rule_task else None
    if cand and cand.get("in_anchor_scope"):
        conf = 0.45 if ai_unavailable else 0.35
        out = classification_from_candidate(
            cand,
            confidence=conf,
            evidence=["rule_fallback_anchor_match"],
            notes="rule_fallback_within_skill_scope",
            available=True,
        )
        out["ai_unavailable_reason"] = "missing_api_key" if ai_unavailable and "api_key" in ai_error.lower() else ""
        return out
    if anchor_candidates:
        review = find_candidate_by_id(candidates, NEEDS_REVIEW_ID)
        return classification_from_candidate(
            review or _candidate_record(NEEDS_REVIEW_ID, NEEDS_REVIEW_ID, candidate_source="needs_review", in_anchor_scope=False),
            confidence=0.0,
            evidence=["rule_fallback_no_anchor_match"],
            requires_human_action=True,
            notes="rule could not map to anchor candidate; needs_review (no first-candidate default)",
            available=False,
            error=ai_error or "rule_fallback_needs_review",
            ai_unavailable_reason=categorize_fallback_reason(ai_error) if ai_unavailable else "",
        )
    review = find_candidate_by_id(candidates, NEEDS_REVIEW_ID)
    return classification_from_candidate(
        review or _candidate_record(NEEDS_REVIEW_ID, NEEDS_REVIEW_ID, candidate_source="needs_review", in_anchor_scope=False),
        confidence=0.0,
        requires_human_action=True,
        notes="rule_fallback_needs_review",
        available=False,
        error=ai_error or "ai_unavailable",
        ai_unavailable_reason=categorize_fallback_reason(ai_error),
    )


def categorize_fallback_reason(ai_error: str) -> str:
    msg = str(ai_error or "").strip().lower()
    if "api_key" in msg or "missing" in msg:
        return "missing_api_key"
    if "timeout" in msg:
        return "timeout"
    if msg:
        return "ai_wrapper_error"
    return "missing_api_key"


def example_trusts_skill_scope(example: dict[str, Any], skill_id: str) -> bool:
    """Human-confirmed mapping: example.skill_id matches Phase 1 skill."""
    return not example_skill_id_mismatch(example, skill_id)
