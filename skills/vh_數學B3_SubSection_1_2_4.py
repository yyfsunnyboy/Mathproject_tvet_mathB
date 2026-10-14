from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_2_4'
GENERATOR_KEYS = ['src_11936', 'src_11937', 'src_11938', 'src_11939', 'src_11940', 'src_11947', 'src_11948', 'src_11958', 'src_11959', 'src_11960', 'src_11969']
GENERATOR_SPECS = [{'textbook_example_id': 11936, 'component_id': 'src_11936', 'generator_key': 'src_11936', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11936, 'source_order': 11936, 'sampling_weight': 10.0}, {'textbook_example_id': 11937, 'component_id': 'src_11937', 'generator_key': 'src_11937', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11937, 'source_order': 11937, 'sampling_weight': 10.0}, {'textbook_example_id': 11938, 'component_id': 'src_11938', 'generator_key': 'src_11938', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11938, 'source_order': 11938, 'sampling_weight': 10.0}, {'textbook_example_id': 11939, 'component_id': 'src_11939', 'generator_key': 'src_11939', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11939, 'source_order': 11939, 'sampling_weight': 10.0}, {'textbook_example_id': 11940, 'component_id': 'src_11940', 'generator_key': 'src_11940', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_first_threshold_crossing', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_first_threshold_crossing', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11940, 'source_order': 11940, 'sampling_weight': 10.0}, {'textbook_example_id': 11947, 'component_id': 'src_11947', 'generator_key': 'src_11947', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11947, 'source_order': 11947, 'sampling_weight': 10.0}, {'textbook_example_id': 11948, 'component_id': 'src_11948', 'generator_key': 'src_11948', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11948, 'source_order': 11948, 'sampling_weight': 10.0}, {'textbook_example_id': 11958, 'component_id': 'src_11958', 'generator_key': 'src_11958', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_series_sum_given', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11958, 'source_order': 11958, 'sampling_weight': 10.0}, {'textbook_example_id': 11959, 'component_id': 'src_11959', 'generator_key': 'src_11959', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_series_sum_given', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11959, 'source_order': 11959, 'sampling_weight': 10.0}, {'textbook_example_id': 11960, 'component_id': 'src_11960', 'generator_key': 'src_11960', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_series_sum_given', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11960, 'source_order': 11960, 'sampling_weight': 10.0}, {'textbook_example_id': 11969, 'component_id': 'src_11969', 'generator_key': 'src_11969', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'geometric_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11969, 'source_order': 11969, 'sampling_weight': 10.0}]


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
