from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_IntegerExponentsAndLaws'
GENERATOR_KEYS = ['src_12343', 'src_12344', 'src_12345', 'src_12346', 'src_12347', 'src_12348', 'src_12349', 'src_12350']
GENERATOR_SPECS = [{'textbook_example_id': 12343, 'component_id': 'src_12343', 'generator_key': 'src_12343', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12343, 'source_order': 12343, 'sampling_weight': 1.0}, {'textbook_example_id': 12344, 'component_id': 'src_12344', 'generator_key': 'src_12344', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12344, 'source_order': 12344, 'sampling_weight': 1.0}, {'textbook_example_id': 12345, 'component_id': 'src_12345', 'generator_key': 'src_12345', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12345, 'source_order': 12345, 'sampling_weight': 1.0}, {'textbook_example_id': 12346, 'component_id': 'src_12346', 'generator_key': 'src_12346', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_power_law_model', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_power_law_model', 'checker_key': None, 'equivalence_type': None, 'display_order': 12346, 'source_order': 12346, 'sampling_weight': 1.0}, {'textbook_example_id': 12347, 'component_id': 'src_12347', 'generator_key': 'src_12347', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12347, 'source_order': 12347, 'sampling_weight': 1.0}, {'textbook_example_id': 12348, 'component_id': 'src_12348', 'generator_key': 'src_12348', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_exponent_blank_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_exponent_blank_equations', 'checker_key': None, 'equivalence_type': None, 'display_order': 12348, 'source_order': 12348, 'sampling_weight': 1.0}, {'textbook_example_id': 12349, 'component_id': 'src_12349', 'generator_key': 'src_12349', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12349, 'source_order': 12349, 'sampling_weight': 1.0}, {'textbook_example_id': 12350, 'component_id': 'src_12350', 'generator_key': 'src_12350', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_power_law_model', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_power_law_model', 'checker_key': None, 'equivalence_type': None, 'display_order': 12350, 'source_order': 12350, 'sampling_weight': 1.0}]


def _resolve_v3_package_root() -> str:
    """Resolve V3 house root from this facade location: skills/ -> <root>/agent_skills_v3."""
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID,
        GENERATOR_KEYS,
        GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level,
        seed=seed,
        difficulty=difficulty,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return dispatch_check(
        user_answer,
        correct_answer,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )
