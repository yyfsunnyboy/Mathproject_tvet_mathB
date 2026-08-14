from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "solve_parameter_from_known_slope_choice"
TEXTBOOK_EXAMPLE_ID = 4590
DEFAULT_COMPONENT_ID = "src_4590" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_SlopeOfALine",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_SlopeOfALine', 'source_example_id': 4590, 'textbook_example_id': 4590, 'source_hash': '5e4dea9ba47176e0b2c555dbd11781e7', 'problem_type_id': 'solve_parameter_from_known_slope_choice', 'required_capabilities': ['solve_parameter_from_known_slope_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_SlopeOfALine', 'source_example_id': 4590, 'textbook_example_id': 4590, 'source_hash': '5e4dea9ba47176e0b2c555dbd11781e7', 'problem_type_id': 'solve_parameter_from_known_slope_choice', 'required_capabilities': ['solve_parameter_from_known_slope_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'solve_parameter_from_known_slope_choice', 'required_capabilities': ['solve_parameter_from_known_slope_choice'], 'classification_source': 'phase1_rule_pack', 'source_hash': '5e4dea9ba47176e0b2c555dbd11781e7', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4590, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '−2'}, {'key': 'B', 'label': 'B', 'text': '1'}, {'key': 'C', 'label': 'C', 'text': '2'}, {'key': 'D', 'label': 'D', 'text': '4'}], 'domain_resolution': {'skill_id': 'vh_數學B1_SlopeOfALine', 'fixed_domain_key': 'coordinate_geometry.line_equation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_parameter_from_known_slope_choice'], 'matched_capabilities': ['solve_parameter_from_known_slope_choice'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.line_equation_domain', 'entrypoint': 'build_line_equation_matrix', 'allowed_operations': ['slope_from_two_points', 'solve_parameter_from_known_slope', 'solve_parameter_from_known_slope_choice', 'collinear_three_points_parameter', 'non_triangle_collinear_parameter', 'parallel_segments_parameter', 'perpendicular_segments_parameter', 'collinear_three_points_parameter_choice', 'slopes_of_named_segments', 'classify_and_compare_figure_slopes'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_SlopeOfALine'})
    constraints["skill_id"] = "vh_數學B1_SlopeOfALine"

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation="solve_parameter_from_known_slope_choice",
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
        domain_operation="solve_parameter_from_known_slope_choice",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
