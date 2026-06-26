from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_VarianceAndStandardDeviation'
GENERATOR_KEYS = ['src_3848', 'src_3849', 'src_3850', 'src_3851', 'src_3899']
GENERATOR_SPECS = [{'textbook_example_id': 3848, 'component_id': 'src_3848', 'generator_key': 'src_3848', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3848, 'source_order': 3848, 'sampling_weight': 10.0}, {'textbook_example_id': 3849, 'component_id': 'src_3849', 'generator_key': 'src_3849', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3849, 'source_order': 3849, 'sampling_weight': 10.0}, {'textbook_example_id': 3850, 'component_id': 'src_3850', 'generator_key': 'src_3850', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3850, 'source_order': 3850, 'sampling_weight': 10.0}, {'textbook_example_id': 3851, 'component_id': 'src_3851', 'generator_key': 'src_3851', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_sample_standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_sample_standard_deviation', 'display_order': 3851, 'source_order': 3851, 'sampling_weight': 10.0}, {'textbook_example_id': 3899, 'component_id': 'src_3899', 'generator_key': 'src_3899', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3899, 'source_order': 3899, 'sampling_weight': 10.0}]


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
