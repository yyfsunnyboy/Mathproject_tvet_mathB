from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_HorizontalAndVerticalLineEquations'
GENERATOR_KEYS = ['src_4544', 'src_4553', 'src_4562', 'src_4591']
GENERATOR_SPECS = [{'textbook_example_id': 4544, 'component_id': 'src_4544', 'generator_key': 'src_4544', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4544', 'line_type': 'vertical_line', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4544, 'source_order': 4544, 'sampling_weight': 10.0}, {'textbook_example_id': 4553, 'component_id': 'src_4553', 'generator_key': 'src_4553', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4553', 'line_type': 'horizontal_line', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4553, 'source_order': 4553, 'sampling_weight': 10.0}, {'textbook_example_id': 4562, 'component_id': 'src_4562', 'generator_key': 'src_4562', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4562', 'line_type': 'vertical_line', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4562, 'source_order': 4562, 'sampling_weight': 10.0}, {'textbook_example_id': 4591, 'component_id': 'src_4591', 'generator_key': 'src_4591', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4591', 'line_type': 'vertical_line', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4591, 'source_order': 4591, 'sampling_weight': 10.0}]


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
