from __future__ import annotations

from typing import Any

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "classify_line_circle_relation_mcq"
TEXTBOOK_EXAMPLE_ID = 11882
DEFAULT_COMPONENT_ID = "src_11882" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_4_2_2",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "choice_label",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "circle.plane",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_2_2', 'source_example_id': 11882, 'textbook_example_id': 11882, 'source_hash': '42f40df9c4d91b3b4041980c966bcb4d', 'problem_type_id': 'classify_line_circle_relation_mcq', 'required_capabilities': ['classify_line_circle_relation_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_4_2_2', 'source_example_id': 11882, 'textbook_example_id': 11882, 'source_hash': '42f40df9c4d91b3b4041980c966bcb4d', 'problem_type_id': 'classify_line_circle_relation_mcq', 'required_capabilities': ['classify_line_circle_relation_mcq'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'classify_line_circle_relation_mcq', 'required_capabilities': ['classify_line_circle_relation_mcq'], 'classification_source': 'phase1_rule_pack', 'source_hash': '42f40df9c4d91b3b4041980c966bcb4d', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 11882, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '兩者相離'}, {'key': 'B', 'label': 'B', 'text': '交於一點'}, {'key': 'C', 'label': 'C', 'text': '交於二點'}, {'key': 'D', 'label': 'D', 'text': '直線過圓心'}], 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_4_2_2', 'fixed_domain_key': 'circle.plane', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['classify_line_circle_relation_mcq'], 'matched_capabilities': ['classify_line_circle_relation_mcq'], 'selected_operation': 'classify_line_circle_relation_mcq', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.circle_plane_domain', 'entrypoint': 'build_circle_plane_matrix', 'allowed_operations': ['classify_line_circle_relation', 'classify_lines_vs_circle_multipart', 'solve_line_circle_parameter_range', 'solve_line_circle_tangent_parameter', 'compute_chord_length', 'solve_line_circle_relation_ranges_multipart', 'count_line_circle_intersections', 'compute_storm_path_length_in_circle', 'classify_line_circle_relation_mcq', 'solve_diameter_chord_parameter_mcq', 'compute_triangle_center_chord_area', 'solve_axis_tangent_parameter'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_4_2_2'})
    constraints["skill_id"] = "vh_數學B2_SubSection_4_2_2"

    matrix = _v3_invoke_domain_entrypoint(
        build_circle_plane_matrix,
        entrypoint_name="build_circle_plane_matrix",
        domain_operation="classify_line_circle_relation_mcq",
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
        domain_operation="classify_line_circle_relation_mcq",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
