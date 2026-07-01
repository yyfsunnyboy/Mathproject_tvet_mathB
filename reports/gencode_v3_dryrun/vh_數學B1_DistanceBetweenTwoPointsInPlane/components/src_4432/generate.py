from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.distance_between_two_points_domain import build_distance_between_two_points_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "solve_unknown_coordinate_from_two_point_distance"
TEXTBOOK_EXAMPLE_ID = 4432
DEFAULT_COMPONENT_ID = "src_4432" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_distance_between_two_points_matrix(
        seed=seed,
        line_type="solve_unknown_coordinate_from_two_point_distance",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_DistanceBetweenTwoPointsInPlane', 'source_example_id': 4432, 'textbook_example_id': 4432, 'source_hash': '652a474ffd6b276a308962a1adb2874e', 'problem_type_id': 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2', 'required_capabilities': ['short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_DistanceBetweenTwoPointsInPlane', 'source_example_id': 4432, 'textbook_example_id': 4432, 'source_hash': '652a474ffd6b276a308962a1adb2874e', 'problem_type_id': 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2', 'required_capabilities': ['short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2', 'required_capabilities': ['short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2'], 'classification_source': 'phase1_rule_pack', 'source_hash': '652a474ffd6b276a308962a1adb2874e', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4432, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_DistanceBetweenTwoPointsInPlane', 'fixed_domain_key': 'coordinate_geometry.distance_between_two_points', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.distance_between_two_points_domain', 'entrypoint': 'build_distance_between_two_points_matrix', 'allowed_operations': ['compute_distance_between_two_points', 'solve_unknown_coordinate_from_two_point_distance'], 'curriculum_profile': 'vocational_high_b'}},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="parameter_solution_set",
        domain_operation="solve_unknown_coordinate_from_two_point_distance",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
