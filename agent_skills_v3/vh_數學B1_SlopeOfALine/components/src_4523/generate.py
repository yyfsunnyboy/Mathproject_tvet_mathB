from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "collinear_three_points_parameter"
TEXTBOOK_EXAMPLE_ID = 4523
DEFAULT_COMPONENT_ID = "src_4523" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_SlopeOfALine",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "parameter_scalar",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_SlopeOfALine', 'source_example_id': 4523, 'textbook_example_id': 4523, 'source_hash': '5e60a0cdd75663369f80ea10528313c1', 'problem_type_id': 'collinear_three_points_parameter', 'required_capabilities': ['collinear_three_points_parameter'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_SlopeOfALine', 'source_example_id': 4523, 'textbook_example_id': 4523, 'source_hash': '5e60a0cdd75663369f80ea10528313c1', 'problem_type_id': 'collinear_three_points_parameter', 'required_capabilities': ['collinear_three_points_parameter'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'collinear_three_points_parameter', 'required_capabilities': ['collinear_three_points_parameter'], 'classification_source': 'phase1_rule_pack', 'source_hash': '5e60a0cdd75663369f80ea10528313c1', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4523, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_SlopeOfALine', 'fixed_domain_key': 'coordinate_geometry.line_equation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['collinear_three_points_parameter'], 'matched_capabilities': ['collinear_three_points_parameter'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.line_equation_domain', 'entrypoint': 'build_line_equation_matrix', 'allowed_operations': ['slope_from_two_points', 'solve_parameter_from_known_slope', 'solve_parameter_from_known_slope_choice', 'collinear_three_points_parameter', 'non_triangle_collinear_parameter', 'parallel_segments_parameter', 'perpendicular_segments_parameter', 'collinear_three_points_parameter_choice', 'slopes_of_named_segments', 'classify_and_compare_figure_slopes'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_SlopeOfALine'})
    constraints["skill_id"] = "vh_數學B1_SlopeOfALine"

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation="collinear_three_points_parameter",
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    matrix = normalize_domain_payload_to_v3_matrix(matrix, norm_context)

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="parameter_scalar",
        domain_operation="collinear_three_points_parameter",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
