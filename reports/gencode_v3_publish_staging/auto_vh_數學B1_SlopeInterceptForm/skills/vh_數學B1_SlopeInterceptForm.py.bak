from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_SlopeInterceptForm'
GENERATOR_KEYS = ['src_4545', 'src_4554', 'src_4563', 'src_4603', 'src_4605']
GENERATOR_SPECS = [{'textbook_example_id': 4545, 'component_id': 'src_4545', 'generator_key': 'src_4545', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4545', 'line_type': 'slope_intercept_equation', 'answer_type': 'expression', 'problem_type_id': 'slope_intercept_equation', 'display_order': 4545, 'source_order': 4545, 'sampling_weight': 10.0}, {'textbook_example_id': 4554, 'component_id': 'src_4554', 'generator_key': 'src_4554', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4554', 'line_type': 'slope_intercept_equation', 'answer_type': 'expression', 'problem_type_id': 'slope_intercept_equation', 'display_order': 4554, 'source_order': 4554, 'sampling_weight': 10.0}, {'textbook_example_id': 4563, 'component_id': 'src_4563', 'generator_key': 'src_4563', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4563', 'line_type': 'slope_intercept_equation', 'answer_type': 'expression', 'problem_type_id': 'slope_intercept_equation', 'display_order': 4563, 'source_order': 4563, 'sampling_weight': 10.0}, {'textbook_example_id': 4603, 'component_id': 'src_4603', 'generator_key': 'src_4603', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4603', 'line_type': 'slope_intercept_read_slope_and_intercept', 'answer_type': 'text_short', 'problem_type_id': 'slope_intercept_read_slope_and_intercept', 'display_order': 4603, 'source_order': 4603, 'sampling_weight': 10.0}, {'textbook_example_id': 4605, 'component_id': 'src_4605', 'generator_key': 'src_4605', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4605', 'line_type': 'slope_intercept_find_x_intercept', 'answer_type': 'single_choice', 'problem_type_id': 'slope_intercept_find_x_intercept', 'display_order': 4605, 'source_order': 4605, 'sampling_weight': 10.0}]


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
