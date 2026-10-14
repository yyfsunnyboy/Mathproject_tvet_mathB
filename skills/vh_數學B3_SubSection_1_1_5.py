from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_1_5'
GENERATOR_KEYS = ['src_11908', 'src_11909', 'src_11910', 'src_11911', 'src_11912', 'src_11918', 'src_11919', 'src_11920', 'src_11921', 'src_11952', 'src_11964', 'src_11965', 'src_11967', 'src_11968']
GENERATOR_SPECS = [{'textbook_example_id': 11908, 'component_id': 'src_11908', 'generator_key': 'src_11908', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11908, 'source_order': 11908, 'sampling_weight': 10.0}, {'textbook_example_id': 11909, 'component_id': 'src_11909', 'generator_key': 'src_11909', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11909, 'source_order': 11909, 'sampling_weight': 10.0}, {'textbook_example_id': 11910, 'component_id': 'src_11910', 'generator_key': 'src_11910', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11910, 'source_order': 11910, 'sampling_weight': 10.0}, {'textbook_example_id': 11911, 'component_id': 'src_11911', 'generator_key': 'src_11911', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11911, 'source_order': 11911, 'sampling_weight': 10.0}, {'textbook_example_id': 11912, 'component_id': 'src_11912', 'generator_key': 'src_11912', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_odd_count_mid_total', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_odd_count_mid_total', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11912, 'source_order': 11912, 'sampling_weight': 10.0}, {'textbook_example_id': 11918, 'component_id': 'src_11918', 'generator_key': 'src_11918', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11918, 'source_order': 11918, 'sampling_weight': 10.0}, {'textbook_example_id': 11919, 'component_id': 'src_11919', 'generator_key': 'src_11919', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11919, 'source_order': 11919, 'sampling_weight': 10.0}, {'textbook_example_id': 11920, 'component_id': 'src_11920', 'generator_key': 'src_11920', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_series_from_two_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_from_two_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11920, 'source_order': 11920, 'sampling_weight': 10.0}, {'textbook_example_id': 11921, 'component_id': 'src_11921', 'generator_key': 'src_11921', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_index_and_total_sum', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_index_and_total_sum', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11921, 'source_order': 11921, 'sampling_weight': 10.0}, {'textbook_example_id': 11952, 'component_id': 'src_11952', 'generator_key': 'src_11952', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11952, 'source_order': 11952, 'sampling_weight': 10.0}, {'textbook_example_id': 11964, 'component_id': 'src_11964', 'generator_key': 'src_11964', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_series_from_two_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_series_from_two_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11964, 'source_order': 11964, 'sampling_weight': 10.0}, {'textbook_example_id': 11965, 'component_id': 'src_11965', 'generator_key': 'src_11965', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11965, 'source_order': 11965, 'sampling_weight': 10.0}, {'textbook_example_id': 11967, 'component_id': 'src_11967', 'generator_key': 'src_11967', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11967, 'source_order': 11967, 'sampling_weight': 10.0}, {'textbook_example_id': 11968, 'component_id': 'src_11968', 'generator_key': 'src_11968', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_sum_multiples_range', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_sum_multiples_range', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11968, 'source_order': 11968, 'sampling_weight': 10.0}]


def _resolve_v3_package_root() -> str:
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
