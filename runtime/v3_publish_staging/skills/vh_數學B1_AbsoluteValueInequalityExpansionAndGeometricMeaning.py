from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning'
GENERATOR_KEYS = ['src_4411', 'src_4415', 'src_4416']
GENERATOR_SPECS = [{'textbook_example_id': 4411, 'component_id': 'src_4411', 'generator_key': 'src_4411', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4411, 'source_order': 4411, 'sampling_weight': 10.0}, {'textbook_example_id': 4415, 'component_id': 'src_4415', 'generator_key': 'src_4415', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4415, 'source_order': 4415, 'sampling_weight': 10.0}, {'textbook_example_id': 4416, 'component_id': 'src_4416', 'generator_key': 'src_4416', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_interval_interpretation', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'absolute_value_inequality_interval_interpretation', 'display_order': 4416, 'source_order': 4416, 'sampling_weight': 10.0}]


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
