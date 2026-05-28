from __future__ import annotations

from typing import Any

from core.gencode.classifier_proposal import detect_answer_shape

_EQUIVALENCE_TO_LEGACY = {
    "exact_text": "exact_string",
    "numeric_equal": "numeric_exact",
    "fraction_equal": "rational_equivalent",
    "algebraic_equivalent": "algebraic_equivalent",
    "set_equal": "unordered_solution_set",
    "choice_label": "choice_label",
}

_CHECKER_FROM_ANSWER_TYPE = {
    "single_choice": ("choice_label_checker", "choice_label"),
    "multi_choice": ("choice_label_checker", "choice_label"),
    "short_answer": ("text_checker", "exact_string"),
    "numeric": ("integer_checker", "numeric_exact"),
    "fraction": ("fraction_checker", "rational_equivalent"),
    "expression": ("expression_equivalence_checker", "expression_equivalence"),
    "set": ("solution_set_checker", "unordered_solution_set"),
    "table": ("text_checker", "exact_string"),
}


def legacy_fields_from_answer_contract(answer_contract: dict[str, Any]) -> dict[str, Any]:
    """Derive legacy checker/equivalence/answer_shape from answer_contract only."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    answer_type = str(ac.get("answer_type", "")).strip()
    equivalence = str(ac.get("answer_equivalence", "")).strip()
    checker_key, eq_default = _CHECKER_FROM_ANSWER_TYPE.get(answer_type, ("text_checker", "exact_string"))
    eq_legacy = _EQUIVALENCE_TO_LEGACY.get(equivalence, eq_default)
    proposal = {
        "answer_type": answer_type,
        "equivalence_type": eq_legacy,
        "checker_key": checker_key,
    }
    return {
        "answer_type": answer_type,
        "checker_key": checker_key,
        "equivalence_type": eq_legacy,
        "answer_shape": detect_answer_shape(proposal),
    }
