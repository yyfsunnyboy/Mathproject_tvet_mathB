from __future__ import annotations

from typing import Any

from core.domain.trigonometry_oblique_triangle_measurement_domain import build_trigonometry_oblique_triangle_measurement_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "solve_side_by_law_of_cosines"
TEXTBOOK_EXAMPLE_ID = 11721
DEFAULT_COMPONENT_ID = "src_11721" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_2_2_4",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "trigonometry.oblique_triangle_measurement",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_4', 'source_example_id': 11721, 'textbook_example_id': 11721, 'source_hash': 'acc8d07bf93c4d354fb0233e22c6005d', 'problem_type_id': 'solve_side_by_law_of_cosines', 'required_capabilities': ['solve_side_by_law_of_cosines'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_2_4', 'source_example_id': 11721, 'textbook_example_id': 11721, 'source_hash': 'acc8d07bf93c4d354fb0233e22c6005d', 'problem_type_id': 'solve_side_by_law_of_cosines', 'required_capabilities': ['solve_side_by_law_of_cosines'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'solve_side_by_law_of_cosines', 'required_capabilities': ['solve_side_by_law_of_cosines'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'acc8d07bf93c4d354fb0233e22c6005d', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11721, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '500公尺'}, {'key': 'B', 'label': 'B', 'text': '600公尺'}, {'key': 'C', 'label': 'C', 'text': '700公尺'}, {'key': 'D', 'label': 'D', 'text': '1000公尺'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_2_2_4', 'fixed_domain_key': 'trigonometry.oblique_triangle_measurement', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_side_by_law_of_cosines'], 'matched_capabilities': ['solve_side_by_law_of_cosines'], 'selected_operation': 'solve_side_by_law_of_cosines', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.trigonometry_oblique_triangle_measurement_domain', 'entrypoint': 'build_trigonometry_oblique_triangle_measurement_matrix', 'allowed_operations': ['solve_side_by_law_of_sines', 'solve_side_by_law_of_cosines'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_2_2_4'})
    constraints["skill_id"] = "vh_數學B2_SubSection_2_2_4"

    matrix = _v3_invoke_domain_entrypoint(
        build_trigonometry_oblique_triangle_measurement_matrix,
        entrypoint_name="build_trigonometry_oblique_triangle_measurement_matrix",
        domain_operation="solve_side_by_law_of_cosines",
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
        domain_operation="solve_side_by_law_of_cosines",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
