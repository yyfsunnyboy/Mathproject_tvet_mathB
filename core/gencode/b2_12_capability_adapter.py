"""Formal payload contracts and readiness audit data for Math B2 section 1-2."""

from __future__ import annotations

from typing import Any

from core.domain.geometry_similarity_domain import validate_similarity_matrix
from core.domain.trigonometry_acute_domain import validate_acute_trigonometry_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload


OPERATION_PAYLOAD_CONTRACTS: dict[str, dict[str, Any]] = {
    "solve_similar_triangle_proportion": {
        "fixed_domain_key": "geometry.similarity",
        "presentation_mode": "short_answer",
        "answer_type": "expression",
        "input_contract": ("proportion_terms", "unknown_index"),
        "canonical_answer_contract": "exact_positive_rational",
        "checker": "expression_checker",
    },
    "compute_right_triangle_trig_ratios": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("opposite", "adjacent", "hypotenuse"),
        "canonical_answer_contract": "exact_ratio_parts_sin_cos_tan",
        "checker": "multi_part_answer_checker",
    },
    "evaluate_exact_special_angle_expression": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "short_answer",
        "answer_type": "expression",
        "input_contract": ("terms",),
        "canonical_answer_contract": "exact_reduced_symbolic_expression",
        "checker": "expression_checker",
    },
    "complete_cofunction_identity": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("function", "angle", "unit"),
        "canonical_answer_contract": "cofunction_enum_and_exact_complement_degrees",
        "checker": "multi_part_answer_checker",
    },
    "solve_acute_trig_constraints": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("known", "relations", "targets"),
        "canonical_answer_contract": "positive_acute_exact_symbolic_targets",
        "checker": "multi_part_answer_checker",
    },
    "solve_right_triangle_projection": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("hypotenuse", "angle", "unit", "base_elevation", "requested"),
        "canonical_answer_contract": "exact_positive_length_parts_with_units",
        "checker": "multi_part_answer_checker",
    },
    "evaluate_trig_decimal": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("requests",),
        "canonical_answer_contract": "decimal_round_half_up_with_explicit_tolerance",
        "checker": "multi_part_answer_checker",
    },
    "simplify_fundamental_trig_expression": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("expressions", "required_form"),
        "canonical_answer_contract": "symbolic_trig_equivalence_with_ast_required_form",
        "checker": "multi_part_answer_checker",
    },
    "collinear_three_points_parameter": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "short_answer",
        "answer_type": "expression",
        "input_contract": ("point_a", "point_b", "point_c", "parameter_name"),
        "canonical_answer_contract": "coordinate_geometry_collinearity_parameter",
        "checker": "expression_checker",
    },
    "sector_arc_and_area": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("radius", "theta_degrees"),
        "canonical_answer_contract": "delegated_sector_exact_pi_parts",
        "checker": "multi_part_answer_checker",
    },
    "compute_chord_and_arc_length": {
        "fixed_domain_key": "trigonometry.acute",
        "presentation_mode": "multiple_inputs",
        "answer_type": "multi_part",
        "input_contract": ("radius", "central_angle", "unit"),
        "canonical_answer_contract": "exact_chord_and_delegated_arc_parts",
        "checker": "multi_part_answer_checker",
    },
}


B2_12_EXAMPLE_OPERATION_MAP: dict[int, str] = {
    11556: "solve_similar_triangle_proportion", 11566: "solve_similar_triangle_proportion",
    11557: "compute_right_triangle_trig_ratios", 11567: "compute_right_triangle_trig_ratios", 11576: "compute_right_triangle_trig_ratios",
    11558: "solve_acute_trig_constraints", 11565: "solve_acute_trig_constraints", 11568: "solve_acute_trig_constraints", 11574: "solve_acute_trig_constraints",
    11577: "solve_acute_trig_constraints", 11579: "solve_acute_trig_constraints", 11582: "solve_acute_trig_constraints", 11585: "solve_acute_trig_constraints",
    11559: "evaluate_exact_special_angle_expression", 11569: "evaluate_exact_special_angle_expression", 11578: "evaluate_exact_special_angle_expression",
    11560: "solve_right_triangle_projection", 11570: "solve_right_triangle_projection", 11584: "solve_right_triangle_projection",
    11561: "evaluate_trig_decimal", 11571: "evaluate_trig_decimal",
    11562: "simplify_fundamental_trig_expression", 11564: "simplify_fundamental_trig_expression", 11572: "simplify_fundamental_trig_expression",
    11580: "simplify_fundamental_trig_expression", 11581: "simplify_fundamental_trig_expression", 11586: "simplify_fundamental_trig_expression",
    11563: "complete_cofunction_identity", 11573: "complete_cofunction_identity",
    11575: "collinear_three_points_parameter", 11583: "compute_chord_and_arc_length",
}


def audit_b2_12_example_mapping() -> dict[str, Any]:
    expected = set(range(11556, 11587))
    mapped = set(B2_12_EXAMPLE_OPERATION_MAP)
    return {
        "expected_examples": len(expected),
        "mapped_examples": len(mapped),
        "missing_examples": sorted(expected - mapped),
        "unexpected_examples": sorted(mapped - expected),
        "example_mapping_complete": mapped == expected,
    }


def _validate_matrix(operation: str, matrix: dict[str, Any]) -> bool:
    if operation == "solve_similar_triangle_proportion":
        return validate_similarity_matrix(matrix)
    return validate_acute_trigonometry_matrix(matrix)


def _semantic_choice_is_unique(matrix: dict[str, Any]) -> bool:
    import sympy as sp

    answer = matrix.get("answer") if isinstance(matrix.get("answer"), dict) else {}
    semantic = answer.get("value", answer.get("canonical_form"))
    choices = matrix.get("source_choices") or matrix.get("givens", {}).get("source_choices") or []
    matches = 0
    for choice in choices:
        value = choice.get("value", choice.get("text")) if isinstance(choice, dict) else choice
        try:
            matches += int(sp.simplify(sp.sympify(value) - sp.sympify(semantic)) == 0)
        except (sp.SympifyError, TypeError, ValueError):
            matches += int(str(value).strip() == str(semantic).strip())
    return matches == 1


def adapt_b2_12_batch1_matrix(matrix: dict[str, Any], *, domain_operation: str, **kwargs: Any) -> dict[str, Any]:
    contract = OPERATION_PAYLOAD_CONTRACTS.get(str(domain_operation or "").strip())
    if contract is None:
        raise ValueError(f"unsupported_b2_12_batch1_operation:{domain_operation}")
    if not _validate_matrix(str(domain_operation), matrix):
        raise ValueError(f"invalid_b2_12_batch1_domain_matrix:{domain_operation}")
    requested_mode = str(kwargs.pop("presentation_mode", contract["presentation_mode"]))
    requested_type = str(kwargs.pop("answer_type", contract["answer_type"]))
    if requested_mode == "single_choice" and not _semantic_choice_is_unique(matrix):
        raise ValueError("single_choice_requires_unique_semantic_answer")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=requested_mode,
        answer_type=requested_type,
        problem_type_id=domain_operation,
        domain_operation=domain_operation,
        **kwargs,
    )
    answer_contract = dict(payload.get("answer_contract") or {})
    answer_contract["canonical_answer_contract"] = contract["canonical_answer_contract"]
    answer_contract["fixed_domain_key"] = contract["fixed_domain_key"]
    if domain_operation == "complete_cofunction_identity":
        for part in answer_contract.get("parts") or []:
            if part.get("key") == "cofunction":
                part.update({"checker": "expression_checker", "checker_key": "expression_checker", "equivalence_type": "algebraic_equivalent"})
    if domain_operation == "evaluate_trig_decimal":
        requests = list((matrix.get("givens") or {}).get("requests") or [])
        for index, part in enumerate(answer_contract.get("parts") or []):
            precision = int(requests[index].get("precision", 8)) if index < len(requests) else 8
            part.update({
                "checker": "decimal_tolerance_checker",
                "checker_key": "decimal_tolerance_checker",
                "equivalence_type": "decimal_tolerance",
                "precision": precision,
                "rounding_policy": "ROUND_HALF_UP",
                "tolerance": str(5 * 10 ** (-(precision + 1))),
            })
    if domain_operation == "solve_acute_trig_constraints":
        for part in answer_contract.get("parts") or []:
            expected = str(part.get("expected_answer") or "")
            if expected.startswith("{") and expected.endswith("}"):
                part.update({
                    "checker": "solution_set_checker",
                    "checker_key": "solution_set_checker",
                    "equivalence_type": "unordered_solution_set",
                    "answer_type": "solution_set",
                })
    if domain_operation == "simplify_fundamental_trig_expression":
        required_form = str((matrix.get("givens") or {}).get("required_form") or "simplified_trig")
        for part in answer_contract.get("parts") or []:
            part.update({
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
                "required_form": required_form,
            })
    if domain_operation == "compute_chord_and_arc_length":
        for part in answer_contract.get("parts") or []:
            part.update({"unit": str((matrix.get("givens") or {}).get("length_unit") or "unit")})
            if part.get("key") == "arc_length":
                part["required_form"] = "pi_expression"
    if domain_operation == "solve_right_triangle_projection":
        answer_contract["unit"] = str((matrix.get("givens") or {}).get("length_unit") or "unit")
    if requested_mode == "single_choice":
        answer_contract["semantic_canonical_answer"] = (matrix.get("answer") or {}).get("value")
        answer_contract["semantic_choice_unique"] = True
    payload["answer_contract"] = answer_contract
    return payload
