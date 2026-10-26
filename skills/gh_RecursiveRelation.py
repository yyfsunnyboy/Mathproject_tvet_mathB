from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RecursiveRelation'
GENERATOR_KEYS = ['src_12687', 'src_12688', 'src_12689', 'src_12690', 'src_12692', 'src_12693', 'src_12695', 'src_12697', 'src_12699']
GENERATOR_SPECS = [{'textbook_example_id': 12687, 'component_id': 'src_12687', 'generator_key': 'src_12687', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12687, 'source_order': 12687, 'sampling_weight': 10.0}, {'textbook_example_id': 12688, 'component_id': 'src_12688', 'generator_key': 'src_12688', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12688, 'source_order': 12688, 'sampling_weight': 10.0}, {'textbook_example_id': 12689, 'component_id': 'src_12689', 'generator_key': 'src_12689', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12689, 'source_order': 12689, 'sampling_weight': 10.0}, {'textbook_example_id': 12690, 'component_id': 'src_12690', 'generator_key': 'src_12690', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12690, 'source_order': 12690, 'sampling_weight': 10.0}, {'textbook_example_id': 12692, 'component_id': 'src_12692', 'generator_key': 'src_12692', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12692, 'source_order': 12692, 'sampling_weight': 10.0}, {'textbook_example_id': 12693, 'component_id': 'src_12693', 'generator_key': 'src_12693', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12693, 'source_order': 12693, 'sampling_weight': 10.0}, {'textbook_example_id': 12695, 'component_id': 'src_12695', 'generator_key': 'src_12695', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12695, 'source_order': 12695, 'sampling_weight': 10.0}, {'textbook_example_id': 12697, 'component_id': 'src_12697', 'generator_key': 'src_12697', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12697, 'source_order': 12697, 'sampling_weight': 10.0}, {'textbook_example_id': 12699, 'component_id': 'src_12699', 'generator_key': 'src_12699', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recurrence_from_process', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recurrence_from_process', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12699, 'source_order': 12699, 'sampling_weight': 10.0}]


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
