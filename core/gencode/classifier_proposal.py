from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


def _norm_text(text: object) -> str:
    s = str(text or "").strip()
    s = s.replace("\\left|", "|").replace("\\right|", "|")
    s = s.replace("\\le", "<=").replace("\\ge", ">=")
    s = s.replace("≤", "<=").replace("≥", ">=")
    return s


def _is_choice_text(s: str) -> bool:
    return any(token in s for token in ["(A)", "(B)", "(C)", "(D)", "（A）", "（B）", "（C）", "（D）"])


def _is_count_question(s: str) -> bool:
    return "共有多少個" in s or "有多少個" in s


def _is_geometric_meaning_choice(s: str) -> bool:
    return ("象限" in s and "(A)" in s and "(B)" in s) or ("點" in s and "屬於哪一象限" in s)


def _is_malformed_abs_inequality(s: str) -> bool:
    # e.g. "|x|3" without comparator
    if "|x|3" in s:
        return True
    if re.search(r"\|\s*x\s*\|\s*\$?\s*\d", s):
        return True
    return "|x|" in s and not any(op in s for op in ["<", ">", "<=", ">="])


def _is_zero_center_abs_inequality(s: str) -> bool:
    return bool(re.search(r"\|\s*x\s*\|", s)) and any(op in s for op in ["<", ">", "<=", ">="])


def _is_shifted_abs_inequality(s: str) -> bool:
    return bool(re.search(r"\|\s*x\s*[\+\-]\s*\d+\s*\|", s))


def _is_linear_abs_inequality(s: str) -> bool:
    # |ax+b| with a != 0
    return bool(re.search(r"\|\s*[1-9]\d*\s*x\s*[\+\-]\s*\d+\s*\|", s))


def _proposed_contracts() -> dict[str, dict[str, Any]]:
    return {
        "absolute_value_inequality_geometric_meaning": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": True,
            "accepted_format_notes": ["A/B/C/D labels"],
            "canonical_answer_schema": {"type": "choice_label"},
        },
        "absolute_value_inequality_zero_center_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_shifted_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_linear_expression_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_integer_solution_count_choice": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": True,
            "accepted_format_notes": ["A/B/C/D labels"],
            "canonical_answer_schema": {"type": "choice_label"},
        },
        "absolute_value_inequality_malformed_source_review": {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
            "order_matters": False,
            "accepted_format_notes": ["requires source text correction before deterministic generation"],
            "canonical_answer_schema": {"type": "manual_review"},
        },
    }


def build_classifier_proposal(skill_id: str, examples_map: list[dict[str, Any]]) -> dict[str, Any]:
    proposed_example_map: list[dict[str, Any]] = []
    grouped: dict[str, list[int]] = defaultdict(list)
    manual_review_candidates: list[int] = []
    risk_flags: list[str] = []

    for e in examples_map:
        exid = e.get("example_id")
        text = _norm_text(e.get("problem_preview") or e.get("problem_text") or e.get("question_text"))
        pt = "absolute_value_inequality_linear_expression_basic"

        if _is_malformed_abs_inequality(text):
            pt = "absolute_value_inequality_malformed_source_review"
            if isinstance(exid, int):
                manual_review_candidates.append(exid)
        elif _is_geometric_meaning_choice(text):
            pt = "absolute_value_inequality_geometric_meaning"
        elif _is_choice_text(text) and _is_count_question(text):
            pt = "absolute_value_inequality_integer_solution_count_choice"
        elif _is_linear_abs_inequality(text):
            pt = "absolute_value_inequality_linear_expression_basic"
        elif _is_shifted_abs_inequality(text):
            pt = "absolute_value_inequality_shifted_basic"
        elif _is_zero_center_abs_inequality(text):
            pt = "absolute_value_inequality_zero_center_basic"
        else:
            pt = "absolute_value_inequality_malformed_source_review"
            if isinstance(exid, int):
                manual_review_candidates.append(exid)

        if isinstance(exid, int):
            grouped[pt].append(exid)
        proposed_example_map.append(
            {
                "example_id": exid,
                "proposed_problem_type_id": pt,
                "reason": "heuristic_pattern_match",
                "problem_preview": text[:160],
            }
        )

    if manual_review_candidates:
        risk_flags.append("contains_malformed_or_unclassified_examples")

    proposed_problem_types = sorted(grouped.keys())
    contracts = _proposed_contracts()
    proposed_answer_contracts = {k: contracts[k] for k in proposed_problem_types if k in contracts}

    return {
        "skill_id": skill_id,
        "proposed_problem_types": proposed_problem_types,
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": proposed_answer_contracts,
        "manual_review_candidates": sorted(set(manual_review_candidates)),
        "risk_flags": risk_flags,
    }


def detect_answer_shape(answer_contract: dict[str, Any] | None) -> str:
    c = answer_contract if isinstance(answer_contract, dict) else {}
    explicit_shape = str(c.get("answer_shape", "")).strip()
    if explicit_shape and explicit_shape not in {"", "unknown_answer_shape"}:
        return explicit_shape
    answer_type = str(c.get("answer_type", "")).strip().lower()
    eq = str(c.get("equivalence_type", "")).strip().lower()
    if answer_type in {"ordered_pair", "coordinate_pair"} or eq in {
        "coordinate_pair_equivalence",
        "ordered_pair",
    }:
        return "coordinate_pair"
    if answer_type in {"interval_set"} or eq == "interval_set":
        return "interval_set"
    if answer_type in {"choice", "choice_label"} or eq == "choice_label":
        return "choice_label"
    if answer_type in {"integer", "number", "numeric", "numeric_or_radical", "decimal"} or eq in {
        "numeric_exact",
        "rational_equivalent",
        "numeric_equivalence",
    }:
        return "numeric"
    if answer_type in {"expression", "math_expression", "radical_number"} or eq in {
        "algebraic_equivalent",
        "expression_equivalence",
        "math_expression_equivalence",
        "radical_equivalence",
    }:
        return "expression"
    if answer_type in {"classification", "quadrant_label", "text_label", "category"}:
        return "text_short"
    if "equation" in answer_type:
        return "equation"
    if answer_type in {"solution_set", "set"} or eq == "unordered_solution_set":
        return "set"
    if answer_type in {"text", "text_short", "short_answer"}:
        return "text_short"
    if answer_type in {"single_choice", "multi_choice"}:
        return "choice_label"
    if answer_type in {"manual_review"} or eq in {"manual_review_or_ai_judged"}:
        return "manual_review_or_free_response"
    return "unknown_answer_shape"


def build_phase1_gate_policy(
    candidate_problem_types: list[dict[str, Any]],
    *,
    source_examples_count: int,
    checker_smoke_passed: bool = False,
    dynamic_sampling_passed: bool = False,
    min_examples_runtime_ready: int = 3,
) -> dict[str, Any]:
    candidates = [x for x in candidate_problem_types if isinstance(x, dict)]
    fatal_risk = any(any("fatal" in str(r).lower() for r in (x.get("risk_flags") or [])) for x in candidates)
    base_ready = bool(candidates) and all(
        str(x.get("problem_type_id") or x.get("proposed_problem_type_id") or "").strip() not in {"", "unknown"}
        and bool(str(x.get("answer_shape", "")).strip())
        and str(x.get("answer_shape", "")).strip() != "unknown_answer_shape"
        and isinstance(x.get("answer_contract_proposal"), dict)
        and bool(x.get("answer_contract_proposal"))
        and bool(str(x.get("checker_key_proposal", "")).strip())
        and bool(str(x.get("equivalence_type_proposal", "")).strip())
        for x in candidates
    )
    classifier_allowed = (source_examples_count >= 1) and base_ready and (not fatal_risk)
    low_source = any(int(x.get("matched_example_count", 0)) < min_examples_runtime_ready for x in candidates)
    classifier_status = "classifier_blocked"
    if classifier_allowed and low_source:
        classifier_status = "classifier_auto_pending_promote_with_warning"
    elif classifier_allowed:
        classifier_status = "classifier_auto_pending_promote"

    generator_status = "generator_draft_blocked"
    if classifier_allowed and low_source:
        generator_status = "generator_draft_allowed_with_low_source_warning"
    elif classifier_allowed:
        generator_status = "generator_draft_allowed"

    runtime_foundation = classifier_allowed and all(int(x.get("matched_example_count", 0)) >= min_examples_runtime_ready for x in candidates)
    runtime_allowed = runtime_foundation and checker_smoke_passed and dynamic_sampling_passed and (not fatal_risk)
    runtime_status = "runtime_ready_allowed" if runtime_allowed else "blocked_insufficient_examples"
    runtime_blockers: list[str] = []
    if not runtime_foundation:
        runtime_blockers.append("blocked_insufficient_examples")
    if runtime_foundation and not checker_smoke_passed:
        runtime_blockers.append("blocked_checker_smoke_not_passed")
    if runtime_foundation and not dynamic_sampling_passed:
        runtime_blockers.append("blocked_dynamic_sampling_not_passed")
    if fatal_risk:
        runtime_status = "blocked_fatal_risk"
        runtime_blockers.append("blocked_fatal_risk")
    elif runtime_foundation and (not checker_smoke_passed or not dynamic_sampling_passed):
        runtime_status = "blocked_quality_gates"

    return {
        "classifier_gate": {
            "status": classifier_status,
            "allowed": classifier_allowed,
            "warnings": ["insufficient_examples"] if (classifier_allowed and low_source) else [],
        },
        "generator_draft_gate": {
            "status": generator_status,
            "allowed": classifier_allowed,
            "warnings": ["low_source_examples"] if (classifier_allowed and low_source) else [],
        },
        "runtime_ready_gate": {
            "status": runtime_status,
            "allowed": runtime_allowed,
            "blockers": runtime_blockers,
        },
    }

