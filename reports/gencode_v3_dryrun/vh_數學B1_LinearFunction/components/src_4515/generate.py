from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "linear_equation_from_two_points_choice"
TEXTBOOK_EXAMPLE_ID = 4515
DEFAULT_COMPONENT_ID = "src_4515" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_LinearFunction",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4515, 'textbook_example_id': 4515, 'source_hash': 'bd2c947f28849b82a585629b7bc0bb94', 'problem_type_id': 'linear_equation_from_two_points_choice', 'required_capabilities': ['linear_equation_from_two_points_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'source_topology': {'problem_type_id': 'linear_equation_from_two_points_choice', 'exact_task_operation': 'linear_equation_from_two_points_choice', 'required_givens': ['two_points_on_linear_function'], 'requested_quantity': ['linear_function_equation'], 'topology_tags': ['two_points', 'slope_then_intercept', 'single_choice'], 'answer_schema': 'choice_label_with_expression', 'presentation_mode': 'single_choice'}, 'required_givens': ['two_points_on_linear_function'], 'requested_quantity': ['linear_function_equation'], 'topology_tags': ['two_points', 'slope_then_intercept', 'single_choice'], 'answer_schema': 'choice_label_with_expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4515, 'textbook_example_id': 4515, 'source_hash': 'bd2c947f28849b82a585629b7bc0bb94', 'problem_type_id': 'linear_equation_from_two_points_choice', 'required_capabilities': ['linear_equation_from_two_points_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'source_topology': {'problem_type_id': 'linear_equation_from_two_points_choice', 'exact_task_operation': 'linear_equation_from_two_points_choice', 'required_givens': ['two_points_on_linear_function'], 'requested_quantity': ['linear_function_equation'], 'topology_tags': ['two_points', 'slope_then_intercept', 'single_choice'], 'answer_schema': 'choice_label_with_expression', 'presentation_mode': 'single_choice'}, 'required_givens': ['two_points_on_linear_function'], 'requested_quantity': ['linear_function_equation'], 'topology_tags': ['two_points', 'slope_then_intercept', 'single_choice'], 'answer_schema': 'choice_label_with_expression'}, 'problem_type_id': 'linear_equation_from_two_points_choice', 'required_capabilities': ['linear_equation_from_two_points_choice'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'bd2c947f28849b82a585629b7bc0bb94', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4515, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '−x + 2'}, {'key': 'B', 'label': 'B', 'text': 'x − 2'}, {'key': 'C', 'label': 'C', 'text': 'x + 2'}, {'key': 'D', 'label': 'D', 'text': '−x − 2'}], 'domain_resolution': {'skill_id': 'vh_數學B1_LinearFunction', 'fixed_domain_key': 'coordinate_geometry.line_equation', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['linear_equation_from_two_points_choice'], 'matched_capabilities': ['linear_equation_from_two_points_choice'], 'selected_operation': 'linear_equation_from_two_points_choice', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.line_equation_domain', 'entrypoint': 'build_line_equation_matrix', 'allowed_operations': ['two_points', 'point_slope', 'horizontal_line', 'vertical_line', 'oblique_line', 'slope_intercept_equation', 'slope_intercept_find_x_intercept', 'slope_intercept_read_slope_and_intercept', 'intercept_form_equation', 'intercept_form_triangle_area', 'intercept_form_equation_and_triangle_area', 'intercept_form_from_intercept_sum_and_slope', 'parabola_secant_parallel_line_choice', 'triangle_area_bisector_line_equation', 'slope_from_general_or_intercept_form', 'slope_from_general_form', 'slope_of_horizontal_or_vertical_line', 'line_through_point_parallel_to_line', 'line_through_point_perpendicular_to_line', 'parallel_line_slope', 'perpendicular_line_slope', 'parallel_condition_parameter', 'perpendicular_condition_parameter', 'compare_line_slopes', 'line_through_intersection_parallel_to_line', 'line_through_point_perpendicular_to_segment', 'perpendicular_bisector_application', 'coordinate_geometry_word_problem', 'graph_intercepts_and_linear_equation', 'draw_constant_function_graph', 'draw_linear_function_graph', 'graph_based_linear_application_inverse', 'linear_equation_from_two_points_choice'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_LinearFunction'})
    constraints["skill_id"] = "vh_數學B1_LinearFunction"

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation="linear_equation_from_two_points_choice",
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
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
        answer_schema_key="choice_label",
        domain_operation="linear_equation_from_two_points_choice",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
