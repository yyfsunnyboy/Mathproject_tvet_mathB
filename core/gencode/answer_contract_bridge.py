from __future__ import annotations

from typing import Any

from core.gencode.checker_registry import select_checker_from_answer_contract
from core.gencode.classifier_proposal import detect_answer_shape

_EQUIVALENCE_TO_LEGACY = {
    "exact_text": "exact_string",
    "normalized_text_equivalence": "string_equivalence",
    "numeric_equal": "numeric_exact",
    "numeric_equivalence": "numeric_equivalence",
    "numeric_tolerance": "numeric_equivalence",
    "numeric_tolerance_equivalence": "numeric_equivalence",
    "fraction_equal": "rational_equivalent",
    "algebraic_equivalent": "algebraic_equivalent",
    "math_expression_equivalence": "expression_equivalence",
    "radical_equivalence": "expression_equivalence",
    "expression_equivalence": "expression_equivalence",
    "set_equal": "unordered_solution_set",
    "unordered_solution_set": "unordered_solution_set",
    "choice_label": "choice_label",
    "normalized_label": "string_equivalence",
    "interval_equivalence": "interval_set",
    "inequality_solution_equivalence": "interval_set",
    "coordinate_pair_equivalence": "coordinate_pair_equivalence",
}


def legacy_fields_from_answer_contract(answer_contract: dict[str, Any]) -> dict[str, Any]:
    """Derive legacy checker/equivalence/answer_shape from answer_contract."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    answer_type = str(ac.get("answer_type", "")).strip()
    answer_shape = str(ac.get("answer_shape", "")).strip()
    equivalence = str(ac.get("answer_equivalence", "")).strip()
    checker_key, eq_canonical = select_checker_from_answer_contract(ac)
    eq_legacy = _EQUIVALENCE_TO_LEGACY.get(equivalence or eq_canonical, equivalence or eq_canonical)
    proposal = {
        "answer_type": answer_type,
        "equivalence_type": eq_legacy,
        "checker_key": checker_key,
        "answer_shape": answer_shape,
    }
    if not answer_shape:
        proposal["answer_shape"] = detect_answer_shape(proposal)
    return {
        "answer_type": answer_type,
        "checker_key": checker_key,
        "equivalence_type": eq_legacy,
        "answer_shape": proposal.get("answer_shape") or detect_answer_shape(proposal),
        "answer_equivalence": equivalence,
        "selected_checker": checker_key,
    }
