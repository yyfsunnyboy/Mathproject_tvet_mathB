from __future__ import annotations

from typing import Any

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "classify_general_circle_graph"
TEXTBOOK_EXAMPLE_ID = 11846
DEFAULT_COMPONENT_ID = "src_11846" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_4_1_2",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "circle.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_2', 'source_example_id': 11846, 'textbook_example_id': 11846, 'source_hash': 'a1517194a14cdae962fe86cbee83c0dd', 'problem_type_id': 'classify_general_circle_graph', 'required_capabilities': ['classify_general_circle_graph'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_2', 'source_example_id': 11846, 'textbook_example_id': 11846, 'source_hash': 'a1517194a14cdae962fe86cbee83c0dd', 'problem_type_id': 'classify_general_circle_graph', 'required_capabilities': ['classify_general_circle_graph'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'classify_general_circle_graph', 'required_capabilities': ['classify_general_circle_graph'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'a1517194a14cdae962fe86cbee83c0dd', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11846, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_4_1_2', 'fixed_domain_key': 'circle.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['classify_general_circle_graph'], 'matched_capabilities': ['classify_general_circle_graph'], 'selected_operation': 'classify_general_circle_graph', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.circle_plane_domain', 'entrypoint': 'build_circle_plane_matrix', 'allowed_operations': ['identify_center_radius_from_general', 'solve_circle_parameter_range', 'circle_through_three_points', 'circle_center_on_axis_area', 'classify_general_circle_graph', 'translate_and_scale_circle', 'compute_circle_area_from_general', 'identify_circle_from_product_form', 'evaluate_center_radius_expression', 'solve_circle_parameter_range_mcq'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_4_1_2'})
    constraints["skill_id"] = "vh_數學B2_SubSection_4_1_2"

    matrix = _v3_invoke_domain_entrypoint(
        build_circle_plane_matrix,
        entrypoint_name="build_circle_plane_matrix",
        domain_operation="classify_general_circle_graph",
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
        domain_operation="classify_general_circle_graph",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
