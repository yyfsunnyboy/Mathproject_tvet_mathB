# -*- coding: utf-8 -*-
"""Payload contracts for B2 Chapter 3 plane-vector shared capabilities."""

from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import OPS, validate_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

from core.checkers.vector_answer_normalization import (
    DIRECTED_SEGMENT_ANSWER_OPS,
    VECTOR_EXPRESSION_ANSWER_OPS,
    answer_shape_for_domain_operation,
)

_FIXED = "vector.plane"

_MULTI_PART_OPS = frozenset(
    {
        "compute_directed_segment_and_magnitude",
        "compute_directed_segment_mixed_multipart",
        "compute_dot_identity_multipart",
        "compute_regular_polygon_edge_dot",
        "compute_triangle_chain_and_perimeter",
        "compute_vector_components_and_magnitude",
        "express_named_vectors_in_given_basis",
        "plot_navigation_points_coordinates",
        "solve_angle_from_magnitude_identity",
        "solve_equal_vector_coordinates",
        "solve_scalar_multiple_relation_fill",
        "solve_section_coefficient_pair",
    }
)
_CHOICE_OPS = frozenset(
    {
        "classify_angle_quality_from_dot_mcq",
        "classify_dot_sign_from_diagram_mcq",
        "compute_chain_closure_vector_mcq",
        "compute_midpoint_dot_product",
        "compute_triangle_perimeter_from_two_vectors",
        "construct_linear_combination_choice",
        "identify_equal_vector_mcq",
        "identify_resultant_path_mcq",
        "identify_unit_vector_mcq",
        "solve_collinear_ratio_mcq",
        "solve_dot_product_parameter_mcq",
        "solve_parallel_then_magnitude_mcq",
        "solve_unknown_vector_linear_equation",
    }
)

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
    if str(domain_operation) in DIRECTED_SEGMENT_ANSWER_OPS:
        answer_contract["answer_shape"] = "directed_segment"
    elif str(domain_operation) in VECTOR_EXPRESSION_ANSWER_OPS:
        answer_contract.setdefault("answer_shape", "vector_expression")
    else:
        shaped = answer_shape_for_domain_operation(domain_operation)
        if shaped:
            answer_contract.setdefault("answer_shape", shaped)
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
            if not isinstance(part, dict):
                continue
            part.update(
                {
                    "checker": "expression_checker",
                    "checker_key": "expression_checker",
                    "equivalence_type": "algebraic_equivalent",
                }
            )
            part_key = str(part.get("key") or "").strip().lower()
            expected = str(part.get("expected_answer") or "")
            if str(domain_operation) in DIRECTED_SEGMENT_ANSWER_OPS or part_key == "simplified":
                part["answer_shape"] = "directed_segment"
            elif part_key in {"vector", "unit", "ab", "ac", "bc"} or str(domain_operation) in VECTOR_EXPRESSION_ANSWER_OPS:
                # Coordinate-pair answers stay numeric; symbolic / named vectors get keyboard vec rules.
                if not (expected.startswith("(") and expected.endswith(")")):
                    part.setdefault("answer_shape", answer_contract.get("answer_shape") or "vector_expression")
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
