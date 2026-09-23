from __future__ import annotations

from typing import Any

from core.domain.trigonometry_law_of_sines_domain import build_trigonometry_law_of_sines_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "compute_sin_from_side_and_circumradius"
TEXTBOOK_EXAMPLE_ID = 11716
DEFAULT_COMPONENT_ID = "src_11716" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B2_SubSection_2_1_1",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard",
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "trigonometry.law_of_sines",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_1_1', 'source_example_id': 11716, 'textbook_example_id': 11716, 'source_hash': '08140b02a5767f410f8217c20d5ccd0a', 'problem_type_id': 'compute_sin_from_side_and_circumradius', 'required_capabilities': ['compute_sin_from_side_and_circumradius'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B2_SubSection_2_1_1', 'source_example_id': 11716, 'textbook_example_id': 11716, 'source_hash': '08140b02a5767f410f8217c20d5ccd0a', 'problem_type_id': 'compute_sin_from_side_and_circumradius', 'required_capabilities': ['compute_sin_from_side_and_circumradius'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'compute_sin_from_side_and_circumradius', 'required_capabilities': ['compute_sin_from_side_and_circumradius'], 'classification_source': 'phase1_rule_pack', 'source_hash': '08140b02a5767f410f8217c20d5ccd0a', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 11716, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B2_SubSection_2_1_1', 'fixed_domain_key': 'trigonometry.law_of_sines', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compute_sin_from_side_and_circumradius'], 'matched_capabilities': ['compute_sin_from_side_and_circumradius'], 'selected_operation': 'compute_sin_from_side_and_circumradius', 'registry_revision': '2026-09-10-v1.10', 'domain_module': 'core.domain.trigonometry_law_of_sines_domain', 'entrypoint': 'build_trigonometry_law_of_sines_matrix', 'allowed_operations': ['compute_triangle_area_sas', 'solve_side_and_circumradius_by_sines', 'solve_angle_by_law_of_sines', 'compute_sin_from_side_and_circumradius', 'solve_side_ratio_by_law_of_sines', 'solve_side_by_law_of_sines'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B2_SubSection_2_1_1'})
    constraints["skill_id"] = "vh_數學B2_SubSection_2_1_1"

    matrix = _v3_invoke_domain_entrypoint(
        build_trigonometry_law_of_sines_matrix,
        entrypoint_name="build_trigonometry_law_of_sines_matrix",
        domain_operation="compute_sin_from_side_and_circumradius",
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
        answer_schema_key="",
        domain_operation="compute_sin_from_side_and_circumradius",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
