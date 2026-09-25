from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_3_4'
GENERATOR_KEYS = ['src_11791', 'src_11792', 'src_11800']
GENERATOR_SPECS = [{'textbook_example_id': 11791, 'component_id': 'src_11791', 'generator_key': 'src_11791', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_perpendicular_vector_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_perpendicular_vector_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11791, 'source_order': 11791, 'sampling_weight': 10.0}, {'textbook_example_id': 11792, 'component_id': 'src_11792', 'generator_key': 'src_11792', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_perpendicular_vector_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_perpendicular_vector_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11792, 'source_order': 11792, 'sampling_weight': 10.0}, {'textbook_example_id': 11800, 'component_id': 'src_11800', 'generator_key': 'src_11800', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_perpendicular_vector_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_perpendicular_vector_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11800, 'source_order': 11800, 'sampling_weight': 10.0}]


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
