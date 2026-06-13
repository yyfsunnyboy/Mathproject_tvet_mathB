from __future__ import annotations

from typing import Any

# Runtime-available checkers (generic registry; not skill-specific).
CHECKER_CAPABILITIES: dict[str, dict[str, Any]] = {
    "choice_label_checker": {
        "runtime_available": True,
        "answer_types": ["single_choice", "multi_choice", "choice_label", "choice"],
        "equivalence_types": ["choice_label", "choice_label_exact"],
        "module": "core.checkers.choice_label_checker",
    },
    "integer_checker": {
        "runtime_available": True,
        "answer_types": ["integer", "numeric", "decimal", "number"],
        "equivalence_types": ["numeric_equivalence", "numeric_equal", "numeric_exact", "numeric_tolerance"],
        "module": "pipeline",
    },
    "numeric_checker": {
        "runtime_available": True,
        "answer_types": ["numeric", "decimal", "integer", "number"],
        "equivalence_types": ["numeric_equivalence", "numeric_equal", "numeric_exact", "numeric_tolerance", "numeric_tolerance_equivalence"],
        "module": "pipeline",
    },
    "rational_checker": {
        "runtime_available": True,
        "answer_types": ["fraction", "rational"],
        "equivalence_types": ["fraction_equal", "rational_equivalent"],
        "module": "pipeline",
    },
    "decimal_tolerance_checker": {
        "runtime_available": True,
        "answer_types": ["numeric", "decimal", "integer", "number", "rational"],
        "equivalence_types": ["decimal_tolerance"],
        "module": "pipeline",
    },
    "percentage_checker": {
        "runtime_available": True,
        "answer_types": ["numeric", "decimal", "integer", "number", "rational"],
        "equivalence_types": ["percentage_equivalent"],
        "module": "pipeline",
    },
    "expression_equivalence_checker": {
        "runtime_available": True,
        "answer_types": [
            "numeric_or_radical",
            "radical_number",
            "math_expression",
            "expression",
        ],
        "equivalence_types": [
            "radical_equivalence",
            "math_expression_equivalence",
            "algebraic_equivalent",
            "expression_equivalence",
        ],
        "module": "pipeline",
    },
    "expression_checker": {
        "runtime_available": True,
        "answer_types": [
            "numeric_or_radical",
            "radical_number",
            "math_expression",
            "expression",
        ],
        "equivalence_types": [
            "radical_equivalence",
            "math_expression_equivalence",
            "algebraic_equivalent",
            "expression_equivalence",
        ],
        "module": "pipeline",
    },
    "equation_checker": {
        "runtime_available": True,
        "answer_types": ["expression", "equation"],
        "equivalence_types": ["equation_equivalent"],
        "module": "pipeline",
    },
    "solution_set_checker": {
        "runtime_available": True,
        "answer_types": ["set", "solution_set", "integer_set", "number_set"],
        "equivalence_types": ["unordered_solution_set", "set_equal"],
        "module": "core.checkers.solution_set_checker",
    },
    "set_checker": {
        "runtime_available": True,
        "answer_types": ["set", "solution_set", "integer_set", "number_set"],
        "equivalence_types": ["unordered_solution_set", "set_equal"],
        "module": "core.checkers.solution_set_checker",
    },
    "interval_checker": {
        "runtime_available": True,
        "answer_types": ["interval", "union_of_intervals", "interval_set"],
        "equivalence_types": ["interval_equivalence", "interval_set", "inequality_solution_equivalence"],
        "module": "core.checkers.interval_checker",
    },
    "quadrant_checker": {
        "runtime_available": True,
        "answer_types": ["classification", "quadrant_label", "text_label", "category"],
        "equivalence_types": ["normalized_label", "normalized_text_equivalence"],
        "module": "core.checkers.quadrant_checker",
    },
    "coordinate_pair_checker": {
        "runtime_available": True,
        "answer_types": ["ordered_pair", "coordinate_pair", "ordered_tuple", "unordered_tuple"],
        "equivalence_types": ["coordinate_pair_equivalence", "ordered_pair", "ordered_tuple_exact", "unordered_tuple_equivalent"],
        "module": "core.checkers.coordinate_pair_checker",
    },
    "tuple_checker": {
        "runtime_available": True,
        "answer_types": ["ordered_pair", "coordinate_pair", "ordered_tuple", "unordered_tuple"],
        "equivalence_types": ["coordinate_pair_equivalence", "ordered_pair", "ordered_tuple_exact", "unordered_tuple_equivalent"],
        "module": "core.checkers.coordinate_pair_checker",
    },
    "fraction_checker": {
        "runtime_available": True,
        "answer_types": ["fraction"],
        "equivalence_types": ["fraction_equal", "rational_equivalent"],
        "module": "pipeline",
    },
    "text_checker": {
        "runtime_available": True,
        "answer_types": ["short_answer", "text", "table", "text_short"],
        "equivalence_types": ["exact_text", "normalized_text_equivalence", "string_equivalence", "exact_string", "case_insensitive_string"],
        "module": "pipeline",
        "discouraged_for": ["numeric", "numeric_or_radical", "set", "interval"],
    },
    "text_short_checker": {
        "runtime_available": True,
        "answer_types": ["short_answer", "text", "table", "text_short", "expression", "numeric", "numeric_or_radical", "set", "solution_set", "interval", "rational", "integer", "single_choice", "choice"],
        "equivalence_types": ["exact_text", "normalized_text_equivalence", "string_equivalence", "exact_string", "case_insensitive_string", "choice_label"],
        "module": "pipeline",
        "discouraged_for": ["numeric", "numeric_or_radical", "set", "interval"],
    },
    "matrix_checker": {
        "runtime_available": True,
        "answer_types": ["matrix"],
        "equivalence_types": ["matrix_exact"],
        "module": "pipeline",
    },
    "manual_review_checker": {
        "runtime_available": True,
        "answer_types": ["manual_review"],
        "equivalence_types": ["manual_review_or_ai_judged"],
        "module": "pipeline",
    },
    "ai_judged_checker": {
        "runtime_available": True,
        "answer_types": ["manual_review"],
        "equivalence_types": ["manual_review_or_ai_judged"],
        "module": "pipeline",
    },
    "radical_equivalence_checker": {
        "runtime_available": False,
        "answer_types": ["numeric_or_radical", "radical_number"],
        "equivalence_types": ["radical_equivalence"],
        "module": None,
    },
}


def select_checker_from_answer_contract(answer_contract: dict[str, Any]) -> tuple[str, str]:
    """Return (checker_key, equivalence_type legacy) from explicit contract fields."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    equivalence = str(ac.get("answer_equivalence") or ac.get("equivalence_type") or "").strip()
    if checker:
        return checker, equivalence
    answer_type = str(ac.get("answer_type", "")).strip()
    for key, cap in CHECKER_CAPABILITIES.items():
        if not cap.get("runtime_available"):
            continue
        if answer_type in cap.get("answer_types", []):
            eqs = cap.get("equivalence_types", [])
            return key, equivalence or (eqs[0] if eqs else "")
    return "text_checker", equivalence or "exact_text"


def validate_answer_contract_capability(answer_contract: dict[str, Any]) -> dict[str, Any]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    answer_type = str(ac.get("answer_type", "")).strip()
    equivalence = str(ac.get("answer_equivalence") or ac.get("equivalence_type") or "").strip()
    blockers: list[str] = []
    warnings: list[str] = []

    if not checker:
        blockers.append("checker_contract_missing")
        return {
            "checker_capability_status": "blocked",
            "checker_contract_blockers": blockers,
            "checker_contract_warnings": warnings,
            "selected_checker": "",
        }

    cap = CHECKER_CAPABILITIES.get(checker)
    if not cap:
        blockers.append("checker_contract_missing")
    elif not cap.get("runtime_available"):
        blockers.append("checker_contract_missing")
    else:
        allowed_types = set(cap.get("answer_types", []))
        allowed_eq = set(cap.get("equivalence_types", []))
        if answer_type and answer_type not in allowed_types:
            blockers.append("answer_contract_not_supported")
        if equivalence and allowed_eq and equivalence not in allowed_eq:
            warnings.append("equivalence_type_mismatch")
        discouraged = set(cap.get("discouraged_for", []))
        if answer_type in discouraged:
            warnings.append(f"checker_{checker}_discouraged_for_{answer_type}")

    if checker == "text_checker" and equivalence in {"exact_text", "exact_string"}:
        if answer_type in {
            "numeric",
            "numeric_or_radical",
            "set",
            "solution_set",
            "interval",
            "expression",
        }:
            blockers.append("answer_contract_not_supported")

    status = "blocked" if blockers else ("warn" if warnings else "ok")
    return {
        "checker_capability_status": status,
        "checker_contract_blockers": sorted(set(blockers)),
        "checker_contract_warnings": sorted(set(warnings)),
        "selected_checker": checker,
    }
