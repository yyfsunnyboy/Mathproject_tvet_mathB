from __future__ import annotations

from typing import Any

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "construct_linear_combination_choice"
TEXTBOOK_EXAMPLE_ID = 11749
DEFAULT_COMPONENT_ID = "src_11749" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_3_1_4",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "vector.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_1_4', 'source_example_id': 11749, 'textbook_example_id': 11749, 'source_hash': 'b92ffef334ea8747e1ace250d6fa679d', 'problem_type_id': 'construct_linear_combination_choice', 'required_capabilities': ['construct_linear_combination_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_3_1_4', 'source_example_id': 11749, 'textbook_example_id': 11749, 'source_hash': 'b92ffef334ea8747e1ace250d6fa679d', 'problem_type_id': 'construct_linear_combination_choice', 'required_capabilities': ['construct_linear_combination_choice'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'construct_linear_combination_choice', 'required_capabilities': ['construct_linear_combination_choice'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'b92ffef334ea8747e1ace250d6fa679d', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11749, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_3_1_4', 'fixed_domain_key': 'vector.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['construct_linear_combination_choice'], 'matched_capabilities': ['construct_linear_combination_choice'], 'selected_operation': 'construct_linear_combination_choice', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.vector_plane_domain', 'entrypoint': 'build_vector_plane_matrix', 'allowed_operations': ['construct_linear_combination_choice', 'express_linear_combination_from_givens', 'express_section_point_vector', 'identify_resultant_path_mcq', 'solve_scalar_multiple_relation_fill', 'solve_section_coefficient_pair'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_3_1_4'})
    constraints["skill_id"] = "vh_數學B2_SubSection_3_1_4"

    matrix = _v3_invoke_domain_entrypoint(
        build_vector_plane_matrix,
        entrypoint_name="build_vector_plane_matrix",
        domain_operation="construct_linear_combination_choice",
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
        answer_schema_key="choice_label",
        domain_operation="construct_linear_combination_choice",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
