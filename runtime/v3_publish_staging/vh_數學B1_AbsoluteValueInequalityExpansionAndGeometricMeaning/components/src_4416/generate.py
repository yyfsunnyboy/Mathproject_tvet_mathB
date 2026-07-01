from __future__ import annotations

from typing import Any

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "absolute_value_inequality_interval_interpretation"
TEXTBOOK_EXAMPLE_ID = 4416
DEFAULT_COMPONENT_ID = "src_4416" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_absolute_value_matrix(
        seed=seed,
        line_type="absolute_value_inequality_interval_interpretation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning', 'source_example_id': 4416, 'textbook_example_id': 4416, 'source_hash': 'cd46af1fa69d92232798fcc22592cbc5', 'problem_type_id': 'absolute_value_inequality_interval_interpretation', 'required_capabilities': ['absolute_value_inequality_interval_interpretation'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning', 'source_example_id': 4416, 'textbook_example_id': 4416, 'source_hash': 'cd46af1fa69d92232798fcc22592cbc5', 'problem_type_id': 'absolute_value_inequality_interval_interpretation', 'required_capabilities': ['absolute_value_inequality_interval_interpretation'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'absolute_value_inequality_interval_interpretation', 'required_capabilities': ['absolute_value_inequality_interval_interpretation'], 'classification_source': 'python_skill_classifier', 'source_hash': 'cd46af1fa69d92232798fcc22592cbc5', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 4416, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '第一象限'}, {'key': 'B', 'label': 'B', 'text': '第二象限'}, {'key': 'C', 'label': 'C', 'text': '第三象限'}, {'key': 'D', 'label': 'D', 'text': '第四象限 〔111統測B〕'}], 'domain_resolution': {'skill_id': 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning', 'fixed_domain_key': 'algebra.absolute_value', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['absolute_value_inequality_interval_interpretation'], 'matched_capabilities': ['absolute_value_inequality_interval_interpretation'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.absolute_value_domain', 'entrypoint': 'build_absolute_value_matrix', 'allowed_operations': ['absolute_value_inequality_zero_center_basic', 'absolute_value_inequality_linear_expression_basic', 'absolute_value_inequality_shifted_basic', 'absolute_value_inequality_interval_interpretation'], 'curriculum_profile': 'vocational_high_b'}},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation="absolute_value_inequality_interval_interpretation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
