from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_CentralTendencyMeasures'
GENERATOR_KEYS = ['src_3835', 'src_3836', 'src_3837', 'src_3838', 'src_3839', 'src_3840', 'src_3841', 'src_3887', 'src_3888', 'src_3889', 'src_3890']
GENERATOR_SPECS = [{'textbook_example_id': 3835, 'component_id': 'src_3835', 'generator_key': 'src_3835', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3835, 'source_order': 3835, 'sampling_weight': 10.0}, {'textbook_example_id': 3836, 'component_id': 'src_3836', 'generator_key': 'src_3836', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_median_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_median_from_raw_values', 'display_order': 3836, 'source_order': 3836, 'sampling_weight': 10.0}, {'textbook_example_id': 3837, 'component_id': 'src_3837', 'generator_key': 'src_3837', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_mode_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_mode_from_raw_values', 'display_order': 3837, 'source_order': 3837, 'sampling_weight': 10.0}, {'textbook_example_id': 3838, 'component_id': 'src_3838', 'generator_key': 'src_3838', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3838, 'source_order': 3838, 'sampling_weight': 10.0}, {'textbook_example_id': 3839, 'component_id': 'src_3839', 'generator_key': 'src_3839', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3839, 'source_order': 3839, 'sampling_weight': 10.0}, {'textbook_example_id': 3840, 'component_id': 'src_3840', 'generator_key': 'src_3840', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3840, 'source_order': 3840, 'sampling_weight': 10.0}, {'textbook_example_id': 3841, 'component_id': 'src_3841', 'generator_key': 'src_3841', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_weighted_mean', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_weighted_mean', 'display_order': 3841, 'source_order': 3841, 'sampling_weight': 10.0}, {'textbook_example_id': 3887, 'component_id': 'src_3887', 'generator_key': 'src_3887', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3887, 'source_order': 3887, 'sampling_weight': 10.0}, {'textbook_example_id': 3888, 'component_id': 'src_3888', 'generator_key': 'src_3888', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3888, 'source_order': 3888, 'sampling_weight': 10.0}, {'textbook_example_id': 3889, 'component_id': 'src_3889', 'generator_key': 'src_3889', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3889, 'source_order': 3889, 'sampling_weight': 10.0}, {'textbook_example_id': 3890, 'component_id': 'src_3890', 'generator_key': 'src_3890', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_weighted_mean', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_weighted_mean', 'display_order': 3890, 'source_order': 3890, 'sampling_weight': 10.0}]


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
