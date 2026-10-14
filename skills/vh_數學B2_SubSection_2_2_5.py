from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_2_2_5'
GENERATOR_KEYS = ['src_11695', 'src_11697', 'src_11724']
GENERATOR_SPECS = [{'textbook_example_id': 11695, 'component_id': 'src_11695', 'generator_key': 'src_11695', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_tower_two_elevation_path_and_river_width', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_tower_two_elevation_path_and_river_width', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11695, 'source_order': 11695, 'sampling_weight': 10.0}, {'textbook_example_id': 11697, 'component_id': 'src_11697', 'generator_key': 'src_11697', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'solve_height_from_two_elevation_tan_ratios', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_height_from_two_elevation_tan_ratios', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11697, 'source_order': 11697, 'sampling_weight': 10.0}, {'textbook_example_id': 11724, 'component_id': 'src_11724', 'generator_key': 'src_11724', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_height_from_isosceles_bearing_walk_elevation', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_height_from_isosceles_bearing_walk_elevation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11724, 'source_order': 11724, 'sampling_weight': 10.0}]


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
