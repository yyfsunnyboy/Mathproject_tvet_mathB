from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "classify_angle_quality_from_dot_mcq"
TEXTBOOK_EXAMPLE_ID = 11815
DEFAULT_COMPONENT_ID = "src_11815" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_3_3_1",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "vector.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_3_1', 'source_example_id': 11815, 'textbook_example_id': 11815, 'source_hash': '450c0529d1ac346e9b2f19d9efdb807b', 'problem_type_id': 'classify_angle_quality_from_dot_mcq', 'required_capabilities': ['classify_angle_quality_from_dot_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_3_1', 'source_example_id': 11815, 'textbook_example_id': 11815, 'source_hash': '450c0529d1ac346e9b2f19d9efdb807b', 'problem_type_id': 'classify_angle_quality_from_dot_mcq', 'required_capabilities': ['classify_angle_quality_from_dot_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'classify_angle_quality_from_dot_mcq', 'required_capabilities': ['classify_angle_quality_from_dot_mcq'], 'classification_source': 'phase1_rule_pack', 'source_hash': '450c0529d1ac346e9b2f19d9efdb807b', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11815, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '\\(\\theta\\)為銳角'}, {'key': 'B', 'label': 'B', 'text': '\\(\\theta\\)為直角'}, {'key': 'C', 'label': 'C', 'text': '\\(\\theta\\)為鈍角'}, {'key': 'D', 'label': 'D', 'text': '\\(\\theta\\)為平角'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_3_3_1', 'fixed_domain_key': 'vector.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['classify_angle_quality_from_dot_mcq'], 'matched_capabilities': ['classify_angle_quality_from_dot_mcq'], 'selected_operation': 'classify_angle_quality_from_dot_mcq', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.vector_plane_domain', 'entrypoint': 'build_vector_plane_matrix', 'allowed_operations': ['classify_angle_quality_from_dot_mcq', 'compute_cosine_of_angle_from_dot', 'solve_navigation_heading_correction'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_3_3_1'})
    constraints["skill_id"] = "vh_數學B2_SubSection_3_3_1"

    matrix = _v3_invoke_domain_entrypoint(
        build_vector_plane_matrix,
        entrypoint_name="build_vector_plane_matrix",
        domain_operation="classify_angle_quality_from_dot_mcq",
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
        domain_operation="classify_angle_quality_from_dot_mcq",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
