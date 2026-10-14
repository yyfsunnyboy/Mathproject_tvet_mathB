from __future__ import annotations

from typing import Any

from core.domain.trigonometry_right_triangle_measurement_domain import build_trigonometry_right_triangle_measurement_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "solve_broken_tree_original_height"
TEXTBOOK_EXAMPLE_ID = 11704
DEFAULT_COMPONENT_ID = "src_11704" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_2_2_3",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "numeric_scalar",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "trigonometry.right_triangle_measurement",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_3', 'source_example_id': 11704, 'textbook_example_id': 11704, 'source_hash': '4272d473cfe7b97dfe247d9fb11ab107', 'problem_type_id': 'solve_broken_tree_original_height', 'required_capabilities': ['solve_broken_tree_original_height'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_3', 'source_example_id': 11704, 'textbook_example_id': 11704, 'source_hash': '4272d473cfe7b97dfe247d9fb11ab107', 'problem_type_id': 'solve_broken_tree_original_height', 'required_capabilities': ['solve_broken_tree_original_height'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'solve_broken_tree_original_height', 'required_capabilities': ['solve_broken_tree_original_height'], 'classification_source': 'phase1_rule_pack', 'source_hash': '4272d473cfe7b97dfe247d9fb11ab107', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11704, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_2_2_3', 'fixed_domain_key': 'trigonometry.right_triangle_measurement', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_broken_tree_original_height'], 'matched_capabilities': ['solve_broken_tree_original_height'], 'selected_operation': 'solve_broken_tree_original_height', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.trigonometry_right_triangle_measurement_domain', 'entrypoint': 'build_trigonometry_right_triangle_measurement_matrix', 'allowed_operations': ['solve_height_from_sight_line_elevation', 'solve_adjacent_from_hypotenuse_ground_angle', 'solve_opposite_from_adjacent_elevation', 'solve_horizontal_from_height_elevation', 'solve_horizontal_from_height_depression', 'solve_two_elevation_horizontal_shift', 'solve_two_elevation_unknown_height', 'solve_building_height_with_flagpole_elevations', 'solve_broken_tree_original_height', 'solve_height_decimal_from_sight_line_elevation'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_2_2_3'})
    constraints["skill_id"] = "vh_數學B2_SubSection_2_2_3"

    matrix = _v3_invoke_domain_entrypoint(
        build_trigonometry_right_triangle_measurement_matrix,
        entrypoint_name="build_trigonometry_right_triangle_measurement_matrix",
        domain_operation="solve_broken_tree_original_height",
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
        answer_schema_key="numeric_scalar",
        domain_operation="solve_broken_tree_original_height",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
