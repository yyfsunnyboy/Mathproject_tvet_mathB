# -*- coding: utf-8 -*-
"""Payload contracts for B2 §2-1 Law of Cosines shared capabilities."""

from __future__ import annotations

from typing import Any

from core.domain.trigonometry_law_of_cosines_domain import (
    OPS,
    validate_trigonometry_law_of_cosines_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "trigonometry.law_of_cosines"

OPERATION_PAYLOAD_CONTRACTS = {
    operation: {
        "fixed_domain_key": _FIXED,
        "input_schema": {"type": "object", "additionalProperties": True},
        "output_schema": {"type": "domain_matrix", "answer": "canonical_exact"},
        "canonical_answer_contract": "deterministic_exact_trigonometry_oracle",
        "checker": "expression_checker",
    }
    for operation in OPS
}
OPERATION_PAYLOAD_CONTRACTS["solve_detour_extra_distance_by_cosines"].update(
    {"checker": "single_choice_checker"}
)


def adapt_b2_21_law_of_cosines_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation))
    if contract is None:
        raise ValueError(f"unsupported_b2_21_law_of_cosines_operation:{domain_operation}")
    if not validate_trigonometry_law_of_cosines_matrix(matrix):
        raise ValueError(f"invalid_b2_21_law_of_cosines_domain_matrix:{domain_operation}")

    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    answer_type = str(
        kwargs.pop("answer_type", None)
        or facts.get("answer_type")
        or ("single_choice" if matrix.get("choices") else "expression")
    )
    presentation_mode = str(
        kwargs.pop("presentation_mode", None)
        or facts.get("presentation_mode")
        or ("single_choice" if answer_type == "single_choice" else "short_answer")
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=domain_operation,
        domain_operation=domain_operation,
        **kwargs,
    )
    answer_contract = dict(payload.get("answer_contract") or {})
    answer_contract.update(
        {
            "fixed_domain_key": contract["fixed_domain_key"],
            "canonical_answer_contract": contract["canonical_answer_contract"],
        }
    )
    if answer_type == "single_choice":
        answer_contract.update(
            {
                "checker": "single_choice_checker",
                "checker_key": "single_choice_checker",
                "equivalence_type": "choice_label",
                "semantic_choice": True,
                "semantic_answer": matrix.get("semantic_answer") or payload.get("answer"),
            }
        )
        if matrix.get("choices"):
            payload["choices"] = matrix["choices"]
        if matrix.get("correct_label"):
            payload["answer"] = matrix["correct_label"]
            payload["correct_answer"] = matrix["correct_label"]
            answer_contract["expected_answer"] = matrix["correct_label"]
    else:
        for part in answer_contract.get("parts") or []:
            part.update(
                {
                    "checker": "expression_checker",
                    "checker_key": "expression_checker",
                    "equivalence_type": "algebraic_equivalent",
                }
            )
        answer_contract.update(
            {
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
            }
        )
    payload["answer_contract"] = answer_contract
    return payload
