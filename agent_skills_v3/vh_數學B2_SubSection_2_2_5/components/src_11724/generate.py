from __future__ import annotations

from typing import Any

from core.domain.trigonometry_solid_measurement_domain import build_trigonometry_solid_measurement_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "solve_height_from_isosceles_bearing_walk_elevation"
TEXTBOOK_EXAMPLE_ID = 11724
DEFAULT_COMPONENT_ID = "src_11724" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_2_2_5",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "trigonometry.solid_measurement",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_5', 'source_example_id': 11724, 'textbook_example_id': 11724, 'source_hash': 'd6d9ddfe4e3bd13ca3aaea96a23f3a7a', 'problem_type_id': 'solve_height_from_isosceles_bearing_walk_elevation', 'required_capabilities': ['solve_height_from_isosceles_bearing_walk_elevation'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_5', 'source_example_id': 11724, 'textbook_example_id': 11724, 'source_hash': 'd6d9ddfe4e3bd13ca3aaea96a23f3a7a', 'problem_type_id': 'solve_height_from_isosceles_bearing_walk_elevation', 'required_capabilities': ['solve_height_from_isosceles_bearing_walk_elevation'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'solve_height_from_isosceles_bearing_walk_elevation', 'required_capabilities': ['solve_height_from_isosceles_bearing_walk_elevation'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'd6d9ddfe4e3bd13ca3aaea96a23f3a7a', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11724, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '100'}, {'key': 'B', 'label': 'B', 'text': '\\(100\\sqrt[] { 2 }\\)'}, {'key': 'C', 'label': 'C', 'text': '\\(100\\sqrt[] { 3 }\\)'}, {'key': 'D', 'label': 'D', 'text': '200'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_2_2_5', 'fixed_domain_key': 'trigonometry.solid_measurement', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_height_from_isosceles_bearing_walk_elevation'], 'matched_capabilities': ['solve_height_from_isosceles_bearing_walk_elevation'], 'selected_operation': 'solve_height_from_isosceles_bearing_walk_elevation', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.trigonometry_solid_measurement_domain', 'entrypoint': 'build_trigonometry_solid_measurement_matrix', 'allowed_operations': ['solve_tower_two_elevation_path_and_river_width', 'solve_height_from_two_elevation_tan_ratios', 'solve_height_from_isosceles_bearing_walk_elevation'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_2_2_5'})
    constraints["skill_id"] = "vh_數學B2_SubSection_2_2_5"

    matrix = _v3_invoke_domain_entrypoint(
        build_trigonometry_solid_measurement_matrix,
        entrypoint_name="build_trigonometry_solid_measurement_matrix",
        domain_operation="solve_height_from_isosceles_bearing_walk_elevation",
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
        domain_operation="solve_height_from_isosceles_bearing_walk_elevation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
