from __future__ import annotations

from typing import Any

EQUIVALENCE_TYPE_WHITELIST = {
    "exact_string",
    "numeric_exact",
    "rational_equivalent",
    "choice_label",
    "unordered_solution_set",
    "interval_set",
    "algebraic_equivalent",
    "manual_review_or_ai_judged",
}

_NON_RAW_STRING_EQ_TYPES = {
    "numeric_exact",
    "rational_equivalent",
    "choice_label",
    "unordered_solution_set",
    "interval_set",
    "algebraic_equivalent",
    "manual_review_or_ai_judged",
}

_EQUIVALENCE_CANONICAL_MAP = {
    "exact_text": "exact_string",
    "string_equivalence": "exact_string",
    "numeric_equal": "numeric_exact",
    "numeric_equivalence": "numeric_exact",
    "fraction_equal": "rational_equivalent",
    "set_equal": "unordered_solution_set",
    "interval_equivalence": "interval_set",
    "inequality_solution_equivalence": "interval_set",
    "expression_equivalence": "algebraic_equivalent",
}


def _contract_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    c = candidate.get("answer_contract_proposal")
    if isinstance(c, dict) and c:
        return dict(c)
    return {}


def _problem_type_id(candidate: dict[str, Any]) -> str:
    return str(candidate.get("problem_type_id") or candidate.get("proposed_problem_type_id") or "").strip()


def normalize_contract(candidate: dict[str, Any]) -> dict[str, Any]:
    ac = _contract_from_candidate(candidate)
    checker_key = str(
        ac.get("checker_key")
        or ac.get("checker")
        or candidate.get("checker_key_proposal")
        or ""
    ).strip()
    raw_equivalence_type = str(
        ac.get("equivalence_type")
        or ac.get("answer_equivalence")
        or candidate.get("equivalence_type_proposal")
        or ""
    ).strip()
    equivalence_type = _EQUIVALENCE_CANONICAL_MAP.get(raw_equivalence_type, raw_equivalence_type)
    # Guard rail: problem_type_id should never appear in equivalence_type.
    pt = _problem_type_id(candidate)
    if pt and equivalence_type == pt:
        equivalence_type = ""
    answer_type = str(ac.get("answer_type", "")).strip()
    if answer_type == "numeric" and not equivalence_type:
        equivalence_type = "numeric_exact"
    return {
        "answer_type": answer_type,
        "equivalence_type": equivalence_type,
        "checker_key": checker_key,
        "order_matters": bool(ac.get("order_matters", True)),
        "accepted_format_notes": list(ac.get("accepted_format_notes") or []),
        "canonical_answer_schema": ac.get("canonical_answer_schema", answer_type),
    }


def summarize_answer_contracts(candidate_problem_types: list[dict[str, Any]]) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    missing_contract: list[str] = []
    missing_checker: list[str] = []
    equivalence_test_required: list[str] = []
    convertible_to_choice: list[str] = []
    manual_review_or_ai_judged: list[str] = []

    for cand in candidate_problem_types:
        if not isinstance(cand, dict):
            continue
        pt = _problem_type_id(cand)
        if not pt:
            continue
        ac = normalize_contract(cand)
        observed[pt] = ac
        if not ac.get("answer_type") or not ac.get("equivalence_type"):
            missing_contract.append(pt)
        if not ac.get("checker_key"):
            missing_checker.append(pt)
        eq = str(ac.get("equivalence_type", "")).strip()
        at = str(ac.get("answer_type", "")).strip()
        if eq in _NON_RAW_STRING_EQ_TYPES:
            equivalence_test_required.append(pt)
        if at in {"short_answer", "expression"} and eq not in {"manual_review_or_ai_judged"}:
            convertible_to_choice.append(pt)
        if eq == "manual_review_or_ai_judged" or str(ac.get("checker_key", "")).strip() == "manual_review_checker":
            manual_review_or_ai_judged.append(pt)

    return {
        "equivalence_type_whitelist": sorted(EQUIVALENCE_TYPE_WHITELIST),
        "observed_problem_type_answer_contracts": observed,
        "missing_answer_contract_problem_types": sorted(set(missing_contract)),
        "missing_checker_key_problem_types": sorted(set(missing_checker)),
        "equivalence_test_required_problem_types": sorted(set(equivalence_test_required)),
        "convertible_to_choice_problem_types": sorted(set(convertible_to_choice)),
        "manual_review_or_ai_judged_problem_types": sorted(set(manual_review_or_ai_judged)),
    }


def apply_runtime_gate_to_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    row = dict(candidate)
    ac = normalize_contract(row)
    eq = str(ac.get("equivalence_type", "")).strip()
    ck = str(ac.get("checker_key", "")).strip()
    missing_contract = not bool(ac.get("answer_type")) or not bool(eq)
    missing_checker = not bool(ck)
    invalid_eq = bool(eq) and eq not in EQUIVALENCE_TYPE_WHITELIST

    promote_blockers = list(row.get("promote_blockers", []) or [])
    risk_flags = list(row.get("risk_flags", []) or [])
    runtime_status = "runtime_ready_candidate"
    next_action = "phase2_foundation_preflight"
    if missing_contract or missing_checker:
        runtime_status = "FOUNDATION_REPAIR_REQUIRED"
        next_action = "repair_answer_contract_foundation"
    if invalid_eq:
        runtime_status = "candidate_only"
        next_action = "repair_invalid_equivalence_type"

    if missing_contract:
        promote_blockers.append("missing_answer_contract_problem_type")
        risk_flags.append("missing_answer_contract_problem_type")
    if missing_checker:
        promote_blockers.append("missing_checker_key_problem_type")
        risk_flags.append("missing_checker_key_problem_type")
    if invalid_eq:
        promote_blockers.append("invalid_equivalence_type_problem_type")
        risk_flags.append("invalid_equivalence_type_problem_type")

    row["answer_contract_proposal"] = {**(row.get("answer_contract_proposal") or {}), **ac}
    row["checker_key_proposal"] = ck
    row["equivalence_type_proposal"] = eq
    row["runtime_status"] = runtime_status
    row["next_action"] = next_action
    row["promote_blockers"] = sorted(set(promote_blockers))
    row["risk_flags"] = sorted(set(risk_flags))
    if runtime_status != "runtime_ready_candidate":
        row["promote_recommendation"] = "conservative_hold_for_that_candidate"
    return row
