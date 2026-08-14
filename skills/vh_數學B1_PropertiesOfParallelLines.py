from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PropertiesOfParallelLines'
GENERATOR_KEYS = ['src_4530', 'src_4535', 'src_4600', 'src_4602']
GENERATOR_SPECS = [{'textbook_example_id': 4530, 'component_id': 'src_4530', 'generator_key': 'src_4530', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'parallel_segments_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'parallel_segments_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4530, 'source_order': 4530, 'sampling_weight': 10.0}, {'textbook_example_id': 4535, 'component_id': 'src_4535', 'generator_key': 'src_4535', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'parallel_segments_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'parallel_segments_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4535, 'source_order': 4535, 'sampling_weight': 10.0}, {'textbook_example_id': 4600, 'component_id': 'src_4600', 'generator_key': 'src_4600', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'parallel_segments_parameter_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'parallel_segments_parameter_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4600, 'source_order': 4600, 'sampling_weight': 10.0}, {'textbook_example_id': 4602, 'component_id': 'src_4602', 'generator_key': 'src_4602', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'parallel_two_point_lines_parameter_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'parallel_two_point_lines_parameter_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4602, 'source_order': 4602, 'sampling_weight': 10.0}]


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
