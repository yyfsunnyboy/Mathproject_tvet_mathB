from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_AbsoluteValue'
GENERATOR_KEYS = ['src_4398', 'src_4399', 'src_4408', 'src_4412']
GENERATOR_SPECS = [{'textbook_example_id': 4398, 'component_id': 'src_4398', 'generator_key': 'src_4398', 'presentation_mode': 'multiple_inputs', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_basic_absolute_value_equation', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_basic_absolute_value_equation', 'display_order': 4398, 'source_order': 4398, 'sampling_weight': 10.0}, {'textbook_example_id': 4399, 'component_id': 'src_4399', 'generator_key': 'src_4399', 'presentation_mode': 'integer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'number_line_distance_between_two_points', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'number_line_distance_between_two_points', 'display_order': 4399, 'source_order': 4399, 'sampling_weight': 10.0}, {'textbook_example_id': 4408, 'component_id': 'src_4408', 'generator_key': 'src_4408', 'presentation_mode': 'multiple_inputs', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_basic_absolute_value_equation', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_basic_absolute_value_equation', 'display_order': 4408, 'source_order': 4408, 'sampling_weight': 10.0}, {'textbook_example_id': 4412, 'component_id': 'src_4412', 'generator_key': 'src_4412', 'presentation_mode': 'multiple_inputs', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'solve_basic_absolute_value_equation', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_basic_absolute_value_equation', 'display_order': 4412, 'source_order': 4412, 'sampling_weight': 10.0}]


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
