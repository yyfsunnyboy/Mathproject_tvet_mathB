from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_3_1'
GENERATOR_KEYS = ['src_11799', 'src_11824']
GENERATOR_SPECS = [{'textbook_example_id': 11799, 'component_id': 'src_11799', 'generator_key': 'src_11799', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_cosine_of_angle_from_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_cosine_of_angle_from_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11799, 'source_order': 11799, 'sampling_weight': 10.0}, {'textbook_example_id': 11824, 'component_id': 'src_11824', 'generator_key': 'src_11824', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_cosine_of_angle_from_dot', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_cosine_of_angle_from_dot', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11824, 'source_order': 11824, 'sampling_weight': 10.0}]


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
