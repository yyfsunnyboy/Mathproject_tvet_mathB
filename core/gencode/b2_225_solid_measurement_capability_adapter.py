# -*- coding: utf-8 -*-
"""Payload adapter for B2 §2-2-5 solid measurement."""

from __future__ import annotations

from typing import Any

from core.domain.trigonometry_solid_measurement_domain import (
    OPS,
    TOWER_RIVER_OP,
    validate_trigonometry_solid_measurement_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "trigonometry.solid_measurement"

OPERATION_PAYLOAD_CONTRACTS = {
    operation: {
        "fixed_domain_key": _FIXED,
        "canonical_answer_contract": "deterministic_exact_trigonometry_oracle",
        "checker": "expression_checker",
    }
    for operation in OPS
}
OPERATION_PAYLOAD_CONTRACTS[TOWER_RIVER_OP].update({"checker": "multi_part_answer_checker"})
OPERATION_PAYLOAD_CONTRACTS["solve_height_from_two_elevation_tan_ratios"].update(
    {"checker": "single_choice_checker"}
)
OPERATION_PAYLOAD_CONTRACTS["solve_height_from_isosceles_bearing_walk_elevation"].update(
    {"checker": "single_choice_checker"}
)


def adapt_b2_225_solid_measurement_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation))
    if contract is None:
        raise ValueError(f"unsupported_b2_225_solid_operation:{domain_operation}")
    if not validate_trigonometry_solid_measurement_matrix(matrix):
        raise ValueError(f"invalid_b2_225_solid_domain_matrix:{domain_operation}")

    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    answer_type = str(
        kwargs.pop("answer_type", None)
        or facts.get("answer_type")
        or ("single_choice" if matrix.get("choices") else "multi_part" if domain_operation == TOWER_RIVER_OP else "expression")
    )
    presentation_mode = str(
        kwargs.pop("presentation_mode", None)
        or facts.get("presentation_mode")
        or (
            "single_choice"
            if answer_type == "single_choice"
            else "multiple_inputs"
            if answer_type == "multi_part"
            else "short_answer"
        )
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
        payload["choice_contract_valid"] = True
    elif answer_type == "multi_part":
        parts = (matrix.get("answer") or {}).get("parts") or {}
        payload["answer"] = parts
        payload["correct_answer"] = parts
        answer_contract.update(
            {
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
                "equivalence_type": "multi_part_answer",
                "parts": [
                    {
                        "key": str(k),
                        "checker": "expression_checker",
                        "checker_key": "expression_checker",
                        "equivalence_type": "algebraic_equivalent",
                        "expected_answer": v,
                    }
                    for k, v in parts.items()
                ],
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
    payload["fixed_domain_key"] = _FIXED
    return payload
