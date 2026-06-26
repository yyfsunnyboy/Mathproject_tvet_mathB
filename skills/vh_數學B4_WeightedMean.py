from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_WeightedMean'
GENERATOR_KEYS = ['src_3842', 'src_3843', 'src_3844']
GENERATOR_SPECS = [{'textbook_example_id': 3842, 'component_id': 'src_3842', 'generator_key': 'src_3842', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_weighted_mean', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_weighted_mean', 'display_order': 3842, 'source_order': 3842, 'sampling_weight': 10.0}, {'textbook_example_id': 3843, 'component_id': 'src_3843', 'generator_key': 'src_3843', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compute_weighted_mean', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_weighted_mean', 'display_order': 3843, 'source_order': 3843, 'sampling_weight': 10.0}, {'textbook_example_id': 3844, 'component_id': 'src_3844', 'generator_key': 'src_3844', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_weighted_mean', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_weighted_mean', 'display_order': 3844, 'source_order': 3844, 'sampling_weight': 10.0}]


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
