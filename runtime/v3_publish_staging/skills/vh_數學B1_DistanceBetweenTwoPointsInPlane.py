from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_DistanceBetweenTwoPointsInPlane'
GENERATOR_KEYS = ['src_4419', 'src_4432', 'src_4436', 'src_4437']
GENERATOR_SPECS = [{'textbook_example_id': 4419, 'component_id': 'src_4419', 'generator_key': 'src_4419', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_unknown_coordinate_from_two_point_distance', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_unknown_coordinate_from_two_point_distance', 'display_order': 4419, 'source_order': 4419, 'sampling_weight': 10.0}, {'textbook_example_id': 4432, 'component_id': 'src_4432', 'generator_key': 'src_4432', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_unknown_coordinate_from_two_point_distance', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_unknown_coordinate_from_two_point_distance', 'display_order': 4432, 'source_order': 4432, 'sampling_weight': 10.0}, {'textbook_example_id': 4436, 'component_id': 'src_4436', 'generator_key': 'src_4436', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compute_distance_between_two_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_distance_between_two_points', 'display_order': 4436, 'source_order': 4436, 'sampling_weight': 10.0}, {'textbook_example_id': 4437, 'component_id': 'src_4437', 'generator_key': 'src_4437', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'solve_unknown_coordinate_from_two_point_distance', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_unknown_coordinate_from_two_point_distance', 'display_order': 4437, 'source_order': 4437, 'sampling_weight': 10.0}]


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
