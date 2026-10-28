from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LinearPermutation'
GENERATOR_KEYS = ['src_12774', 'src_12775', 'src_12776', 'src_12777', 'src_12778', 'src_12779', 'src_12780', 'src_12781', 'src_12782', 'src_12783', 'src_12784', 'src_12785', 'src_12786', 'src_12787', 'src_12788', 'src_12789', 'src_12790', 'src_12791', 'src_12792']
GENERATOR_SPECS = [{'textbook_example_id': 12774, 'component_id': 'src_12774', 'generator_key': 'src_12774', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12774, 'source_order': 12774, 'sampling_weight': 10.0}, {'textbook_example_id': 12775, 'component_id': 'src_12775', 'generator_key': 'src_12775', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12775, 'source_order': 12775, 'sampling_weight': 10.0}, {'textbook_example_id': 12776, 'component_id': 'src_12776', 'generator_key': 'src_12776', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'distinct_digit_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distinct_digit_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12776, 'source_order': 12776, 'sampling_weight': 10.0}, {'textbook_example_id': 12777, 'component_id': 'src_12777', 'generator_key': 'src_12777', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'adjacent_separated', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'adjacent_separated', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12777, 'source_order': 12777, 'sampling_weight': 10.0}, {'textbook_example_id': 12778, 'component_id': 'src_12778', 'generator_key': 'src_12778', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12778, 'source_order': 12778, 'sampling_weight': 10.0}, {'textbook_example_id': 12779, 'component_id': 'src_12779', 'generator_key': 'src_12779', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12779, 'source_order': 12779, 'sampling_weight': 10.0}, {'textbook_example_id': 12780, 'component_id': 'src_12780', 'generator_key': 'src_12780', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12780, 'source_order': 12780, 'sampling_weight': 10.0}, {'textbook_example_id': 12781, 'component_id': 'src_12781', 'generator_key': 'src_12781', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12781, 'source_order': 12781, 'sampling_weight': 10.0}, {'textbook_example_id': 12782, 'component_id': 'src_12782', 'generator_key': 'src_12782', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'two_group_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'two_group_line', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12782, 'source_order': 12782, 'sampling_weight': 10.0}, {'textbook_example_id': 12783, 'component_id': 'src_12783', 'generator_key': 'src_12783', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12783, 'source_order': 12783, 'sampling_weight': 10.0}, {'textbook_example_id': 12784, 'component_id': 'src_12784', 'generator_key': 'src_12784', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12784, 'source_order': 12784, 'sampling_weight': 10.0}, {'textbook_example_id': 12785, 'component_id': 'src_12785', 'generator_key': 'src_12785', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12785, 'source_order': 12785, 'sampling_weight': 10.0}, {'textbook_example_id': 12786, 'component_id': 'src_12786', 'generator_key': 'src_12786', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12786, 'source_order': 12786, 'sampling_weight': 10.0}, {'textbook_example_id': 12787, 'component_id': 'src_12787', 'generator_key': 'src_12787', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'distinct_digit_numbers', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distinct_digit_numbers', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12787, 'source_order': 12787, 'sampling_weight': 10.0}, {'textbook_example_id': 12788, 'component_id': 'src_12788', 'generator_key': 'src_12788', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12788, 'source_order': 12788, 'sampling_weight': 10.0}, {'textbook_example_id': 12789, 'component_id': 'src_12789', 'generator_key': 'src_12789', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'ends_from_group', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'ends_from_group', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12789, 'source_order': 12789, 'sampling_weight': 10.0}, {'textbook_example_id': 12790, 'component_id': 'src_12790', 'generator_key': 'src_12790', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'ends_and_block', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'ends_and_block', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12790, 'source_order': 12790, 'sampling_weight': 10.0}, {'textbook_example_id': 12791, 'component_id': 'src_12791', 'generator_key': 'src_12791', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'fixed_order_insertion', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'fixed_order_insertion', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12791, 'source_order': 12791, 'sampling_weight': 10.0}, {'textbook_example_id': 12792, 'component_id': 'src_12792', 'generator_key': 'src_12792', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'relative_order_three', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'relative_order_three', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12792, 'source_order': 12792, 'sampling_weight': 10.0}]


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
