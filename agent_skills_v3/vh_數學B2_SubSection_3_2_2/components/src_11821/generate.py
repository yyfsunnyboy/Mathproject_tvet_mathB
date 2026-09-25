from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "compute_chain_closure_vector_mcq"
TEXTBOOK_EXAMPLE_ID = 11821
DEFAULT_COMPONENT_ID = "src_11821" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_3_2_2",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "vector.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_2_2', 'source_example_id': 11821, 'textbook_example_id': 11821, 'source_hash': '9de1a9e8f864b0f627c0d6cd9df90798', 'problem_type_id': 'compute_chain_closure_vector_mcq', 'required_capabilities': ['compute_chain_closure_vector_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_2_2', 'source_example_id': 11821, 'textbook_example_id': 11821, 'source_hash': '9de1a9e8f864b0f627c0d6cd9df90798', 'problem_type_id': 'compute_chain_closure_vector_mcq', 'required_capabilities': ['compute_chain_closure_vector_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'compute_chain_closure_vector_mcq', 'required_capabilities': ['compute_chain_closure_vector_mcq'], 'classification_source': 'phase1_rule_pack', 'source_hash': '9de1a9e8f864b0f627c0d6cd9df90798', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11821, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_3_2_2', 'fixed_domain_key': 'vector.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compute_chain_closure_vector_mcq'], 'matched_capabilities': ['compute_chain_closure_vector_mcq'], 'selected_operation': 'compute_chain_closure_vector_mcq', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.vector_plane_domain', 'entrypoint': 'build_vector_plane_matrix', 'allowed_operations': ['compute_chain_closure_vector_mcq', 'compute_point_vectors_linear_combination', 'compute_triangle_chain_and_perimeter', 'compute_vector_linear_combination', 'compute_vector_sum_difference', 'solve_parallelogram_fourth_vertex'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_3_2_2'})
    constraints["skill_id"] = "vh_數學B2_SubSection_3_2_2"

    matrix = _v3_invoke_domain_entrypoint(
        build_vector_plane_matrix,
        entrypoint_name="build_vector_plane_matrix",
        domain_operation="compute_chain_closure_vector_mcq",
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
        domain_operation="compute_chain_closure_vector_mcq",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
