from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_LinearTransformationOfData'
GENERATOR_KEYS = ['src_3852', 'src_3853', 'src_3854', 'src_3855', 'src_3894', 'src_3895', 'src_3896']
GENERATOR_SPECS = [{'textbook_example_id': 3852, 'component_id': 'src_3852', 'generator_key': 'src_3852', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3852, 'source_order': 3852, 'sampling_weight': 10.0}, {'textbook_example_id': 3853, 'component_id': 'src_3853', 'generator_key': 'src_3853', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3853, 'source_order': 3853, 'sampling_weight': 10.0}, {'textbook_example_id': 3854, 'component_id': 'src_3854', 'generator_key': 'src_3854', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3854, 'source_order': 3854, 'sampling_weight': 10.0}, {'textbook_example_id': 3855, 'component_id': 'src_3855', 'generator_key': 'src_3855', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3855, 'source_order': 3855, 'sampling_weight': 10.0}, {'textbook_example_id': 3894, 'component_id': 'src_3894', 'generator_key': 'src_3894', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_arithmetic_mean_from_raw_values', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_arithmetic_mean_from_raw_values', 'display_order': 3894, 'source_order': 3894, 'sampling_weight': 10.0}, {'textbook_example_id': 3895, 'component_id': 'src_3895', 'generator_key': 'src_3895', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3895, 'source_order': 3895, 'sampling_weight': 10.0}, {'textbook_example_id': 3896, 'component_id': 'src_3896', 'generator_key': 'src_3896', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3896, 'source_order': 3896, 'sampling_weight': 10.0}]


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
