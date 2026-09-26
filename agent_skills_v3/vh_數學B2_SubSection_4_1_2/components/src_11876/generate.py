from __future__ import annotations

from typing import Any

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "evaluate_center_radius_expression"
TEXTBOOK_EXAMPLE_ID = 11876
DEFAULT_COMPONENT_ID = "src_11876" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_4_1_2",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "circle.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_2', 'source_example_id': 11876, 'textbook_example_id': 11876, 'source_hash': 'ee23ce6f4c88f84a7d0bfd732b3159b5', 'problem_type_id': 'evaluate_center_radius_expression', 'required_capabilities': ['evaluate_center_radius_expression'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_2', 'source_example_id': 11876, 'textbook_example_id': 11876, 'source_hash': 'ee23ce6f4c88f84a7d0bfd732b3159b5', 'problem_type_id': 'evaluate_center_radius_expression', 'required_capabilities': ['evaluate_center_radius_expression'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'evaluate_center_radius_expression', 'required_capabilities': ['evaluate_center_radius_expression'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'ee23ce6f4c88f84a7d0bfd732b3159b5', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11876, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '2'}, {'key': 'B', 'label': 'B', 'text': '4'}, {'key': 'C', 'label': 'C', 'text': '6'}, {'key': 'D', 'label': 'D', 'text': '8'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_4_1_2', 'fixed_domain_key': 'circle.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_center_radius_expression'], 'matched_capabilities': ['evaluate_center_radius_expression'], 'selected_operation': 'evaluate_center_radius_expression', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.circle_plane_domain', 'entrypoint': 'build_circle_plane_matrix', 'allowed_operations': ['identify_center_radius_from_general', 'solve_circle_parameter_range', 'circle_through_three_points', 'circle_center_on_axis_area', 'classify_general_circle_graph', 'translate_and_scale_circle', 'compute_circle_area_from_general', 'identify_circle_from_product_form', 'evaluate_center_radius_expression', 'solve_circle_parameter_range_mcq'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_4_1_2'})
    constraints["skill_id"] = "vh_數學B2_SubSection_4_1_2"

    matrix = _v3_invoke_domain_entrypoint(
        build_circle_plane_matrix,
        entrypoint_name="build_circle_plane_matrix",
        domain_operation="evaluate_center_radius_expression",
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
        domain_operation="evaluate_center_radius_expression",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
