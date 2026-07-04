from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "graph_multi_part"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "graph_intercepts_and_linear_equation"
TEXTBOOK_EXAMPLE_ID = 4444
DEFAULT_COMPONENT_ID = "src_4444" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_LinearFunction",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4444, 'textbook_example_id': 4444, 'source_hash': 'd0a11c5da82842663ba5a78475c2b9d4', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'required_capabilities': ['graph_intercepts_and_linear_equation'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'answer_type': 'multi_part', 'source_topology': {'problem_type_id': 'graph_intercepts_and_linear_equation', 'exact_task_operation': 'graph_intercepts_and_linear_equation', 'required_givens': ['linear_function_graph'], 'requested_quantity': ['x_intercept', 'y_intercept', 'linear_function_equation'], 'topology_tags': ['graph_reading', 'two_axis_intercepts', 'equation_from_graph', 'multi_part'], 'answer_schema': 'multi_part_intercepts_and_expression', 'presentation_mode': 'graph_multi_part'}, 'required_givens': ['linear_function_graph'], 'requested_quantity': ['x_intercept', 'y_intercept', 'linear_function_equation'], 'topology_tags': ['graph_reading', 'two_axis_intercepts', 'equation_from_graph', 'multi_part'], 'answer_schema': 'multi_part_intercepts_and_expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4444, 'textbook_example_id': 4444, 'source_hash': 'd0a11c5da82842663ba5a78475c2b9d4', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'required_capabilities': ['graph_intercepts_and_linear_equation'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'answer_type': 'multi_part', 'source_topology': {'problem_type_id': 'graph_intercepts_and_linear_equation', 'exact_task_operation': 'graph_intercepts_and_linear_equation', 'required_givens': ['linear_function_graph'], 'requested_quantity': ['x_intercept', 'y_intercept', 'linear_function_equation'], 'topology_tags': ['graph_reading', 'two_axis_intercepts', 'equation_from_graph', 'multi_part'], 'answer_schema': 'multi_part_intercepts_and_expression', 'presentation_mode': 'graph_multi_part'}, 'required_givens': ['linear_function_graph'], 'requested_quantity': ['x_intercept', 'y_intercept', 'linear_function_equation'], 'topology_tags': ['graph_reading', 'two_axis_intercepts', 'equation_from_graph', 'multi_part'], 'answer_schema': 'multi_part_intercepts_and_expression'}, 'problem_type_id': 'graph_intercepts_and_linear_equation', 'required_capabilities': ['graph_intercepts_and_linear_equation'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'd0a11c5da82842663ba5a78475c2b9d4', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'source_example_id': 4444, 'answer_type': 'multi_part', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_LinearFunction', 'fixed_domain_key': 'coordinate_geometry.line_equation', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['graph_intercepts_and_linear_equation'], 'matched_capabilities': ['graph_intercepts_and_linear_equation'], 'selected_operation': 'graph_intercepts_and_linear_equation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.line_equation_domain', 'entrypoint': 'build_line_equation_matrix', 'allowed_operations': ['two_points', 'point_slope', 'horizontal_line', 'vertical_line', 'oblique_line', 'slope_intercept_equation', 'slope_intercept_find_x_intercept', 'slope_intercept_read_slope_and_intercept', 'intercept_form_equation', 'intercept_form_triangle_area', 'intercept_form_equation_and_triangle_area', 'intercept_form_from_intercept_sum_and_slope', 'parabola_secant_parallel_line_choice', 'triangle_area_bisector_line_equation', 'slope_from_general_or_intercept_form', 'slope_from_general_form', 'slope_of_horizontal_or_vertical_line', 'line_through_point_parallel_to_line', 'line_through_point_perpendicular_to_line', 'parallel_line_slope', 'perpendicular_line_slope', 'parallel_condition_parameter', 'perpendicular_condition_parameter', 'compare_line_slopes', 'line_through_intersection_parallel_to_line', 'line_through_point_perpendicular_to_segment', 'perpendicular_bisector_application', 'coordinate_geometry_word_problem', 'graph_intercepts_and_linear_equation'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_LinearFunction'})
    constraints["skill_id"] = "vh_數學B1_LinearFunction"

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation="graph_intercepts_and_linear_equation",
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
        answer_schema_key="",
        domain_operation="graph_intercepts_and_linear_equation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
