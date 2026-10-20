from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RealExponentsAndLaws'
GENERATOR_KEYS = ['src_12367', 'src_12368', 'src_12369', 'src_12370', 'src_12371', 'src_12372', 'src_12373', 'src_12374', 'src_12375', 'src_12376']
GENERATOR_SPECS = [{'textbook_example_id': 12367, 'component_id': 'src_12367', 'generator_key': 'src_12367', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12367, 'source_order': 12367, 'sampling_weight': 1.0}, {'textbook_example_id': 12368, 'component_id': 'src_12368', 'generator_key': 'src_12368', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12368, 'source_order': 12368, 'sampling_weight': 1.0}, {'textbook_example_id': 12369, 'component_id': 'src_12369', 'generator_key': 'src_12369', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_cooling_coefficient', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_cooling_coefficient', 'checker_key': None, 'equivalence_type': None, 'display_order': 12369, 'source_order': 12369, 'sampling_weight': 1.0}, {'textbook_example_id': 12370, 'component_id': 'src_12370', 'generator_key': 'src_12370', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12370, 'source_order': 12370, 'sampling_weight': 1.0}, {'textbook_example_id': 12371, 'component_id': 'src_12371', 'generator_key': 'src_12371', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12371, 'source_order': 12371, 'sampling_weight': 1.0}, {'textbook_example_id': 12372, 'component_id': 'src_12372', 'generator_key': 'src_12372', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_cooling_initial_temperature', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_cooling_initial_temperature', 'checker_key': None, 'equivalence_type': None, 'display_order': 12372, 'source_order': 12372, 'sampling_weight': 1.0}, {'textbook_example_id': 12373, 'component_id': 'src_12373', 'generator_key': 'src_12373', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_linear_unknowns_from_exponential_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_linear_unknowns_from_exponential_table', 'checker_key': None, 'equivalence_type': None, 'display_order': 12373, 'source_order': 12373, 'sampling_weight': 1.0}, {'textbook_example_id': 12374, 'component_id': 'src_12374', 'generator_key': 'src_12374', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'select_nearest_model_value', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'select_nearest_model_value', 'checker_key': None, 'equivalence_type': None, 'display_order': 12374, 'source_order': 12374, 'sampling_weight': 1.0}, {'textbook_example_id': 12375, 'component_id': 'src_12375', 'generator_key': 'src_12375', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12375, 'source_order': 12375, 'sampling_weight': 1.0}, {'textbook_example_id': 12376, 'component_id': 'src_12376', 'generator_key': 'src_12376', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12376, 'source_order': 12376, 'sampling_weight': 1.0}]


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
