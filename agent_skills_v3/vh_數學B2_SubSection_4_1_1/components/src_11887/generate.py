from __future__ import annotations

from typing import Any

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "circle_same_center_scaled_area"
TEXTBOOK_EXAMPLE_ID = 11887
DEFAULT_COMPONENT_ID = "src_11887" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_4_1_1",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "circle.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_1', 'source_example_id': 11887, 'textbook_example_id': 11887, 'source_hash': 'd0bb97052af5da682c2e40e22fc798a9', 'problem_type_id': 'circle_same_center_scaled_area', 'required_capabilities': ['circle_same_center_scaled_area'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_1_1', 'source_example_id': 11887, 'textbook_example_id': 11887, 'source_hash': 'd0bb97052af5da682c2e40e22fc798a9', 'problem_type_id': 'circle_same_center_scaled_area', 'required_capabilities': ['circle_same_center_scaled_area'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'circle_same_center_scaled_area', 'required_capabilities': ['circle_same_center_scaled_area'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'd0bb97052af5da682c2e40e22fc798a9', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11887, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_4_1_1', 'fixed_domain_key': 'circle.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['circle_same_center_scaled_area'], 'matched_capabilities': ['circle_same_center_scaled_area'], 'selected_operation': 'circle_same_center_scaled_area', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.circle_plane_domain', 'entrypoint': 'build_circle_plane_matrix', 'allowed_operations': ['identify_center_radius_from_standard', 'write_circle_from_center_radius', 'write_circle_from_center_point', 'write_circle_equations_from_conditions', 'interpret_circular_locus_equation', 'circle_from_diameter_endpoints', 'circle_equal_radius_at_origin', 'translate_and_scale_circle', 'circle_origin_through_lines_intersection', 'circle_same_center_scaled_area', 'circle_center_tangent_to_line'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_4_1_1'})
    constraints["skill_id"] = "vh_數學B2_SubSection_4_1_1"

    matrix = _v3_invoke_domain_entrypoint(
        build_circle_plane_matrix,
        entrypoint_name="build_circle_plane_matrix",
        domain_operation="circle_same_center_scaled_area",
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
        domain_operation="circle_same_center_scaled_area",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
