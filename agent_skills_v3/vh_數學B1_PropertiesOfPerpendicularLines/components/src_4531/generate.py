from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "perpendicular_segments_parameter"
TEXTBOOK_EXAMPLE_ID = 4531
DEFAULT_COMPONENT_ID = "src_4531" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "parameter_scalar",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.line_equation",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PropertiesOfPerpendicularLines', 'source_example_id': 4531, 'textbook_example_id': 4531, 'source_hash': '49d908a335dc4747a31bf9d44c29fdc7', 'problem_type_id': 'perpendicular_segments_parameter', 'required_capabilities': ['perpendicular_segments_parameter'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'integer', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact'}, 'answer_type': 'integer'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PropertiesOfPerpendicularLines', 'source_example_id': 4531, 'textbook_example_id': 4531, 'source_hash': '49d908a335dc4747a31bf9d44c29fdc7', 'problem_type_id': 'perpendicular_segments_parameter', 'required_capabilities': ['perpendicular_segments_parameter'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'integer', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact'}, 'answer_type': 'integer'}, 'problem_type_id': 'perpendicular_segments_parameter', 'required_capabilities': ['perpendicular_segments_parameter'], 'classification_source': 'phase1_rule_pack', 'source_hash': '49d908a335dc4747a31bf9d44c29fdc7', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'integer', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact'}, 'source_example_id': 4531, 'answer_type': 'integer', 'exact_task_operation': '', 'source_answer_label': '1', 'domain_resolution': {'skill_id': 'vh_數學B1_PropertiesOfPerpendicularLines', 'fixed_domain_key': 'coordinate_geometry.line_equation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['perpendicular_segments_parameter'], 'matched_capabilities': ['perpendicular_segments_parameter'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.coordinate_geometry.line_equation_domain', 'entrypoint': 'build_line_equation_matrix', 'allowed_operations': ['parallel_and_perpendicular_slopes_from_reference', 'triangle_right_angle_verification', 'perpendicular_segments_parameter', 'perpendicular_two_point_lines_parameter', 'perpendicular_slope_quadrant_choice'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_PropertiesOfPerpendicularLines'})
    constraints["skill_id"] = "vh_數學B1_PropertiesOfPerpendicularLines"

    matrix = _v3_invoke_domain_entrypoint(
        build_line_equation_matrix,
        entrypoint_name="build_line_equation_matrix",
        domain_operation="perpendicular_segments_parameter",
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
        answer_schema_key="parameter_scalar",
        domain_operation="perpendicular_segments_parameter",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
