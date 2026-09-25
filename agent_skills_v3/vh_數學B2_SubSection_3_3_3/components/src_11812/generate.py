from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "compute_midpoint_dot_product"
TEXTBOOK_EXAMPLE_ID = 11812
DEFAULT_COMPONENT_ID = "src_11812" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_3_3_3",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "vector.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_3_3', 'source_example_id': 11812, 'textbook_example_id': 11812, 'source_hash': 'ce5b720a95617b70b517e4412687ea9f', 'problem_type_id': 'compute_midpoint_dot_product', 'required_capabilities': ['compute_midpoint_dot_product'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_3_3', 'source_example_id': 11812, 'textbook_example_id': 11812, 'source_hash': 'ce5b720a95617b70b517e4412687ea9f', 'problem_type_id': 'compute_midpoint_dot_product', 'required_capabilities': ['compute_midpoint_dot_product'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'compute_midpoint_dot_product', 'required_capabilities': ['compute_midpoint_dot_product'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'ce5b720a95617b70b517e4412687ea9f', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11812, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '2'}, {'key': 'B', 'label': 'B', 'text': '4'}, {'key': 'C', 'label': 'C', 'text': '6'}, {'key': 'D', 'label': 'D', 'text': '8'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_3_3_3', 'fixed_domain_key': 'vector.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compute_midpoint_dot_product'], 'matched_capabilities': ['compute_midpoint_dot_product'], 'selected_operation': 'compute_midpoint_dot_product', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.vector_plane_domain', 'entrypoint': 'build_vector_plane_matrix', 'allowed_operations': ['compute_cosine_of_angle_from_dot', 'compute_dot_product_coordinates', 'compute_midpoint_dot_product', 'plot_navigation_points_coordinates', 'solve_dot_product_parameter_mcq'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_3_3_3'})
    constraints["skill_id"] = "vh_數學B2_SubSection_3_3_3"

    matrix = _v3_invoke_domain_entrypoint(
        build_vector_plane_matrix,
        entrypoint_name="build_vector_plane_matrix",
        domain_operation="compute_midpoint_dot_product",
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
        domain_operation="compute_midpoint_dot_product",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
