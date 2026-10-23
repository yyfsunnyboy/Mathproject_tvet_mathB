from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RemainderTheorem'
GENERATOR_KEYS = ['src_12518', 'src_12538', 'src_12539', 'src_12540', 'src_12541', 'src_12542', 'src_12543', 'src_12544', 'src_12545', 'src_12546', 'src_12547', 'src_12548', 'src_12549']
GENERATOR_SPECS = [{'textbook_example_id': 12518, 'component_id': 'src_12518', 'generator_key': 'src_12518', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12518, 'source_order': 12518, 'sampling_weight': 10.0}, {'textbook_example_id': 12538, 'component_id': 'src_12538', 'generator_key': 'src_12538', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12538, 'source_order': 12538, 'sampling_weight': 10.0}, {'textbook_example_id': 12539, 'component_id': 'src_12539', 'generator_key': 'src_12539', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12539, 'source_order': 12539, 'sampling_weight': 10.0}, {'textbook_example_id': 12540, 'component_id': 'src_12540', 'generator_key': 'src_12540', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12540, 'source_order': 12540, 'sampling_weight': 10.0}, {'textbook_example_id': 12541, 'component_id': 'src_12541', 'generator_key': 'src_12541', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12541, 'source_order': 12541, 'sampling_weight': 10.0}, {'textbook_example_id': 12542, 'component_id': 'src_12542', 'generator_key': 'src_12542', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12542, 'source_order': 12542, 'sampling_weight': 10.0}, {'textbook_example_id': 12543, 'component_id': 'src_12543', 'generator_key': 'src_12543', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12543, 'source_order': 12543, 'sampling_weight': 10.0}, {'textbook_example_id': 12544, 'component_id': 'src_12544', 'generator_key': 'src_12544', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12544, 'source_order': 12544, 'sampling_weight': 10.0}, {'textbook_example_id': 12545, 'component_id': 'src_12545', 'generator_key': 'src_12545', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12545, 'source_order': 12545, 'sampling_weight': 10.0}, {'textbook_example_id': 12546, 'component_id': 'src_12546', 'generator_key': 'src_12546', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12546, 'source_order': 12546, 'sampling_weight': 10.0}, {'textbook_example_id': 12547, 'component_id': 'src_12547', 'generator_key': 'src_12547', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12547, 'source_order': 12547, 'sampling_weight': 10.0}, {'textbook_example_id': 12548, 'component_id': 'src_12548', 'generator_key': 'src_12548', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_from_remainder_congruences', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_from_remainder_congruences', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12548, 'source_order': 12548, 'sampling_weight': 10.0}, {'textbook_example_id': 12549, 'component_id': 'src_12549', 'generator_key': 'src_12549', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_remainder_with_linear_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_with_linear_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12549, 'source_order': 12549, 'sampling_weight': 10.0}]


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
