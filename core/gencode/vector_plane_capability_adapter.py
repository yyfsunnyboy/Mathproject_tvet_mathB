# -*- coding: utf-8 -*-
"""Payload contracts for B2 Chapter 3 plane-vector shared capabilities."""

from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import OPS, validate_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "vector.plane"

_MULTI_PART_OPS = frozenset(
    {
        "compute_vector_components_and_magnitude",
        "solve_equal_vector_coordinates",
        "compute_directed_segment_and_magnitude",
        "compute_triangle_chain_and_perimeter",
    }
)
_CHOICE_OPS = frozenset({"compute_triangle_perimeter_from_two_vectors"})

OPERATION_PAYLOAD_CONTRACTS = {
    operation: {
        "fixed_domain_key": _FIXED,
        "input_schema": {"type": "object", "additionalProperties": True},
        "output_schema": {"type": "domain_matrix", "answer": "canonical_exact"},
        "canonical_answer_contract": "deterministic_exact_vector_oracle",
        "checker": "expression_checker",
    }
    for operation in OPS
}

for _op in _MULTI_PART_OPS:
    OPERATION_PAYLOAD_CONTRACTS[_op].update({"checker": "multi_part_answer_checker"})
for _op in _CHOICE_OPS:
    OPERATION_PAYLOAD_CONTRACTS[_op].update({"checker": "single_choice_checker"})


def adapt_vector_plane_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation))
    if contract is None:
        raise ValueError(f"unsupported_vector_plane_operation:{domain_operation}")
    if not validate_vector_plane_matrix(matrix):
        raise ValueError(f"invalid_vector_plane_domain_matrix:{domain_operation}")

    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    answer_type = str(
        kwargs.pop("answer_type", None)
        or facts.get("answer_type")
        or (
            "single_choice"
            if matrix.get("choices")
            else "multi_part"
            if isinstance((matrix.get("answer") or {}).get("parts"), dict)
            and len((matrix.get("answer") or {}).get("parts") or {}) > 1
            else "expression"
        )
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
    elif answer_type == "multi_part":
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
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
            }
        )
    else:
        answer_contract.update(
            {
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
            }
        )
    payload["answer_contract"] = answer_contract
    return payload
