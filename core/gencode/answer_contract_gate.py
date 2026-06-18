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
    "ordered_tuple_exact",
    "unordered_tuple_equivalent",
    "manual_review_or_ai_judged",
    "linear_equation_equivalent",
    "multi_part_answer",
}

_NON_RAW_STRING_EQ_TYPES = {
    "numeric_exact",
    "rational_equivalent",
    "choice_label",
    "unordered_solution_set",
    "interval_set",
    "algebraic_equivalent",
    "ordered_tuple_exact",
    "unordered_tuple_equivalent",
    "manual_review_or_ai_judged",
    "linear_equation_equivalent",
    "multi_part_answer",
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
    "coordinate_pair_equivalence": "ordered_tuple_exact",
    "ordered_pair": "ordered_tuple_exact",
}

_DEFAULT_CONTRACT_BY_ANSWER_TYPE = {
    "short_answer": ("exact_string", "text_short_checker"),
    "text": ("exact_string", "text_short_checker"),
    "text_short": ("exact_string", "text_short_checker"),
    "numeric": ("numeric_exact", "numeric_checker"),
    "integer": ("numeric_exact", "integer_checker"),
    "expression": ("algebraic_equivalent", "expression_checker"),
    "equation": ("linear_equation_equivalent", "linear_equation_equivalent_checker"),
    "linear_equation": ("linear_equation_equivalent", "linear_equation_equivalent_checker"),
    "fraction": ("rational_equivalent", "rational_checker"),
    "rational": ("rational_equivalent", "rational_checker"),
    "set": ("unordered_solution_set", "set_checker"),
    "solution_set": ("unordered_solution_set", "set_checker"),
    "interval": ("interval_set", "interval_checker"),
    "ordered_pair": ("ordered_tuple_exact", "tuple_checker"),
    "coordinate_pair": ("ordered_tuple_exact", "tuple_checker"),
    "ordered_tuple": ("ordered_tuple_exact", "tuple_checker"),
    "unordered_tuple": ("unordered_tuple_equivalent", "tuple_checker"),
    "multi_part": ("multi_part_answer", "multi_part_answer_checker"),
}


def coerce_single_choice_contract(answer_contract: dict[str, Any]) -> dict[str, Any]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    answer_type = str(ac.get("answer_type", "")).strip()
    presentation = str(ac.get("presentation_mode", "")).strip()
    if answer_type not in {"single_choice", "choice", "choice_label"} and presentation != "single_choice":
        return ac
    ac.update(
        {
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "answer_equivalence": "choice_label",
            "equivalence_type": "choice_label",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "presentation_mode": "single_choice",
            "choices_required": True,
            "frontend_render_choices": True,
        }
    )
    return ac


def _is_coordinate_pair_short_answer(candidate: dict[str, Any], ac: dict[str, Any]) -> bool:
    answer_type = str(ac.get("answer_type", "")).strip()
    presentation = str(ac.get("presentation_mode", "")).strip()
    if answer_type in {"single_choice", "choice", "choice_label"} or presentation == "single_choice":
        return False
    semantic_values = {
        str(ac.get("answer_shape", "")).strip(),
        str(ac.get("semantic_answer_shape", "")).strip(),
        str(ac.get("answer_semantics", "")).strip(),
        str(ac.get("semantics", "")).strip(),
    }
    math_objects = set(candidate.get("math_objects") or [])
    draft = candidate.get("problem_type_spec_draft")
    if isinstance(draft, dict):
        stem = draft.get("stem_contract") if isinstance(draft.get("stem_contract"), dict) else {}
        math_objects.update(stem.get("allowed_math_objects") or [])
        math_objects.update(stem.get("required_math_objects") or [])
    return "coordinate_pair" in semantic_values or "coordinate_pair" in math_objects


def _contract_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    c = candidate.get("answer_contract_proposal")
    if isinstance(c, dict) and c:
        return dict(c)
    return {}


def _problem_type_id(candidate: dict[str, Any]) -> str:
    return str(candidate.get("problem_type_id") or candidate.get("proposed_problem_type_id") or "").strip()


def normalize_contract(candidate: dict[str, Any]) -> dict[str, Any]:
    ac = _contract_from_candidate(candidate)
    coerce_single_choice_contract(ac)
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
    if _is_coordinate_pair_short_answer(candidate, ac):
        answer_type = "coordinate_pair"
        equivalence_type = "ordered_tuple_exact"
        checker_key = "tuple_checker"
    else:
        default_equivalence, default_checker = _DEFAULT_CONTRACT_BY_ANSWER_TYPE.get(answer_type, ("", ""))
        if not equivalence_type:
            equivalence_type = default_equivalence
        if not checker_key:
            checker_key = default_checker
    return {
        "answer_type": answer_type,
        "answer_shape": str(ac.get("answer_shape", "")).strip(),
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

    owned_flags = {
        "missing_answer_contract_problem_type",
        "missing_checker_key_problem_type",
        "invalid_equivalence_type_problem_type",
    }
    promote_blockers = [x for x in (row.get("promote_blockers", []) or []) if x not in owned_flags]
    risk_flags = [x for x in (row.get("risk_flags", []) or []) if x not in owned_flags]
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
