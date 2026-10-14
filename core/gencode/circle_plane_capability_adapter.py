# -*- coding: utf-8 -*-
"""Payload contracts for B2 Chapter 4 plane-circle shared capabilities."""

from __future__ import annotations

from typing import Any

from core.domain.circle_plane_domain import OPS, validate_circle_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

_FIXED = "circle.plane"

_MULTI_PART_OPS = frozenset(
    {
        "compute_tangent_segment_lengths",
        "tangents_perpendicular_to_line",
        "tangents_parallel_to_line",
        "solve_line_circle_relation_ranges_multipart",
        "classify_lines_vs_circle_multipart",
        "classify_point_vs_circles_multipart",
        "identify_center_radius_from_standard",
        "write_circle_equations_from_conditions",
        "interpret_circular_locus_equation",
        "identify_center_radius_from_general",
        "classify_general_circle_graph",
    }
)
_CHOICE_OPS = frozenset(
    {
        "tangent_at_point_on_circle_mcq",
        "solve_circle_parameter_range_mcq",
        "compute_tangent_segment_length_mcq",
        "count_line_vs_two_circles_intersections",
        "compute_tangents_from_point_quad_area",
        "compute_triangle_center_chord_area",
        "solve_diameter_chord_parameter_mcq",
        "classify_line_circle_relation_mcq",
        "identify_point_on_circle_mcq",
        "circle_origin_through_lines_intersection",
        "circle_same_center_scaled_area",
        "circle_center_tangent_to_line",
        "circle_center_on_axis_area",
        "identify_circle_from_product_form",
        "evaluate_center_radius_expression",
    }
)
_EQUATION_OPS = frozenset(
    {
        "count_line_circle_intersections",
        "compute_storm_path_length_in_circle",
        "solve_line_circle_parameter_range",
        "solve_point_circle_parameter_range",
        "solve_line_circle_tangent_parameter",
        "solve_axis_tangent_parameter",
        "compute_chord_length",
        "classify_line_circle_relation",
        "tangent_at_point_on_circle",
        "write_circle_from_center_radius",
        "write_circle_from_center_point",
        "circle_from_diameter_endpoints",
        "circle_equal_radius_at_origin",
        "translate_and_scale_circle",
        "circle_through_three_points",
        "compute_circle_area_from_general",
        "solve_circle_parameter_range",
    }
)

OPERATION_PAYLOAD_CONTRACTS = {
    operation: {
        "fixed_domain_key": _FIXED,
        "input_schema": {"type": "object", "additionalProperties": True},
        "output_schema": {"type": "domain_matrix", "answer": "canonical_exact"},
        "canonical_answer_contract": "deterministic_exact_circle_oracle",
        "checker": "expression_checker",
    }
    for operation in OPS
}

for _op in _MULTI_PART_OPS:
    OPERATION_PAYLOAD_CONTRACTS[_op].update({"checker": "multi_part_answer_checker"})
for _op in _CHOICE_OPS:
    OPERATION_PAYLOAD_CONTRACTS[_op].update({"checker": "single_choice_checker"})
for _op in _EQUATION_OPS:
    OPERATION_PAYLOAD_CONTRACTS[_op].update(
        {"checker": "expression_checker", "equivalence_type": "equation_equivalent"}
    )


def adapt_circle_plane_matrix(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    **kwargs: Any,
) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation))
    if contract is None:
        raise ValueError(f"unsupported_circle_plane_operation:{domain_operation}")
    if not validate_circle_plane_matrix(matrix):
        raise ValueError(f"invalid_circle_plane_domain_matrix:{domain_operation}")

    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    answer_type = str(
        kwargs.pop("answer_type", None)
        or facts.get("answer_type")
        or (
            "single_choice"
            if matrix.get("choices")
            else "multi_part"
            if isinstance((matrix.get("answer") or {}), dict)
            and isinstance(((matrix.get("answer") or {}).get("parts")), dict)
            and len(((matrix.get("answer") or {}).get("parts") or {})) > 1
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
            if not isinstance(part, dict):
                continue
            label = str(part.get("key") or part.get("label") or "")
            part.update(
                {
                    "checker": "expression_checker",
                    "checker_key": "expression_checker",
                    "equivalence_type": (
                        "equation_equivalent"
                        if ("方程式" in label or "標準" in label or "一般" in label or label.startswith("("))
                        else "algebraic_equivalent"
                    ),
                }
            )
        answer_contract.update(
            {
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
            }
        )
    else:
        equiv = "equation_equivalent" if str(domain_operation) in _EQUATION_OPS else "algebraic_equivalent"
        if str(domain_operation) in {"solve_circle_parameter_range", "compute_circle_area_from_general"}:
            equiv = "algebraic_equivalent"
        answer_contract.update(
            {
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": equiv,
            }
        )
    payload["answer_contract"] = answer_contract
    return payload
