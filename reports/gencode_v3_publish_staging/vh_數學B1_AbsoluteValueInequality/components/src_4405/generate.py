from __future__ import annotations

from typing import Any

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "absolute_value_inequality_linear_expression_basic"
TEXTBOOK_EXAMPLE_ID = 4405
DEFAULT_COMPONENT_ID = "src_4405" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_absolute_value_matrix(
        seed=seed,
        line_type="absolute_value_inequality_linear_expression_basic",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValueInequality', 'source_example_id': 4405, 'textbook_example_id': 4405, 'source_hash': '36123d847ef3018da83567676aaaf511', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'required_capabilities': ['absolute_value_inequality_linear_expression_basic'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValueInequality', 'source_example_id': 4405, 'textbook_example_id': 4405, 'source_hash': '36123d847ef3018da83567676aaaf511', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'required_capabilities': ['absolute_value_inequality_linear_expression_basic'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'required_capabilities': ['absolute_value_inequality_linear_expression_basic'], 'classification_source': 'python_skill_classifier', 'source_hash': '36123d847ef3018da83567676aaaf511', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4405, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_AbsoluteValueInequality', 'fixed_domain_key': 'algebra.absolute_value', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['absolute_value_inequality_linear_expression_basic'], 'matched_capabilities': ['absolute_value_inequality_linear_expression_basic'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.absolute_value_domain', 'entrypoint': 'build_absolute_value_matrix', 'allowed_operations': ['absolute_value_inequality_zero_center_basic', 'absolute_value_inequality_linear_expression_basic', 'absolute_value_inequality_shifted_basic', 'absolute_value_inequality_integer_solution_count_choice'], 'curriculum_profile': 'vocational_high_b'}},
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
        domain_operation="absolute_value_inequality_linear_expression_basic",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
