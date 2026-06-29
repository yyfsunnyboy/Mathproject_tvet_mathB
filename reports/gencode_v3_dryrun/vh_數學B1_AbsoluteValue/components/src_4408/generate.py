from __future__ import annotations

from typing import Any

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "solve_basic_absolute_value_equation"
TEXTBOOK_EXAMPLE_ID = 4408
DEFAULT_COMPONENT_ID = "src_4408" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_absolute_value_matrix(
        seed=seed,
        line_type="solve_basic_absolute_value_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValue', 'source_example_id': 4408, 'textbook_example_id': 4408, 'source_hash': '532befe434d6575440dd23ab2b44e515', 'problem_type_id': 'solve_basic_absolute_value_equation', 'required_capabilities': ['solve_basic_absolute_value_equation'], 'classification_source': 'deterministic_structural', 'presentation_mode': 'multiple_inputs', 'answer_contract': {'answer_type': 'solution_set', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set'}, 'answer_type': 'solution_set'}, 'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValue', 'source_example_id': 4408, 'textbook_example_id': 4408, 'source_hash': '532befe434d6575440dd23ab2b44e515', 'problem_type_id': 'solve_basic_absolute_value_equation', 'required_capabilities': ['solve_basic_absolute_value_equation'], 'classification_source': 'deterministic_structural', 'presentation_mode': 'multiple_inputs', 'answer_contract': {'answer_type': 'solution_set', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set'}, 'answer_type': 'solution_set'}, 'classification_status': 'resolved', 'skill_id': 'vh_數學B1_AbsoluteValue', 'source_example_id': 4408, 'textbook_example_id': 4408, 'source_hash': '532befe434d6575440dd23ab2b44e515', 'problem_type_id': 'solve_basic_absolute_value_equation', 'required_capabilities': ['solve_basic_absolute_value_equation'], 'classification_source': 'deterministic_structural', 'presentation_mode': 'multiple_inputs', 'answer_contract': {'answer_type': 'solution_set', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set'}, 'answer_type': 'solution_set', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_AbsoluteValue', 'fixed_domain_key': 'algebra.absolute_value', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_basic_absolute_value_equation'], 'matched_capabilities': ['solve_basic_absolute_value_equation'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.absolute_value_domain', 'entrypoint': 'build_absolute_value_matrix', 'allowed_operations': ['solve_basic_absolute_value_equation', 'solve_basic_absolute_value_equation_no_solution', 'number_line_distance_between_two_points'], 'curriculum_profile': 'vocational_high_b'}},
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
        domain_operation="solve_basic_absolute_value_equation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
