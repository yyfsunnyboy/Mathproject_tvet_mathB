from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_OpinionPollInterpretation'
GENERATOR_KEYS = ['src_3860', 'src_3861']
GENERATOR_SPECS = [
    {
        'textbook_example_id': 3860, 'component_id': 'src_3860', 'generator_key': 'src_3860',
        'presentation_mode': 'single_choice', 'response_mode': 'single_choice',
        'interaction_type': 'single_choice', 'source_kind': 'example',
        'line_type': 'poll_interval_from_support_and_margin', 'answer_type': 'single_choice',
        'answer_value_type': 'choice_label', 'problem_type_id': 'poll_interval_from_support_and_margin',
        'display_order': 3860, 'source_order': 3860, 'sampling_weight': 10.0,
    },
    {
        'textbook_example_id': 3861, 'component_id': 'src_3861', 'generator_key': 'src_3861',
        'presentation_mode': 'single_choice', 'response_mode': 'single_choice',
        'interaction_type': 'single_choice', 'source_kind': 'quiz',
        'line_type': 'poll_support_from_interval', 'answer_type': 'single_choice',
        'answer_value_type': 'choice_label', 'problem_type_id': 'poll_support_from_interval',
        'display_order': 3861, 'source_order': 3861, 'sampling_weight': 10.0,
    },
]


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
