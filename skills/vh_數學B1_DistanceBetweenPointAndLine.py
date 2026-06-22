from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_DistanceBetweenPointAndLine'
GENERATOR_KEYS = ['src_4568', 'src_4569', 'src_4575', 'src_4576', 'src_4586', 'src_4587', 'src_4607']
GENERATOR_SPECS = [{'textbook_example_id': 4568, 'component_id': 'src_4568', 'generator_key': 'src_4568', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compare_point_to_line_distances', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'compare_point_to_line_distances', 'display_order': 4568, 'source_order': 4568, 'sampling_weight': 1.0}, {'textbook_example_id': 4569, 'component_id': 'src_4569', 'generator_key': 'src_4569', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_from_point_to_line_parameter', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'distance_from_point_to_line_parameter', 'display_order': 4569, 'source_order': 4569, 'sampling_weight': 1.0}, {'textbook_example_id': 4575, 'component_id': 'src_4575', 'generator_key': 'src_4575', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_from_point_to_line', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_from_point_to_line', 'display_order': 4575, 'source_order': 4575, 'sampling_weight': 1.0}, {'textbook_example_id': 4576, 'component_id': 'src_4576', 'generator_key': 'src_4576', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_from_point_to_line_parameter', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'distance_from_point_to_line_parameter', 'display_order': 4576, 'source_order': 4576, 'sampling_weight': 1.0}, {'textbook_example_id': 4586, 'component_id': 'src_4586', 'generator_key': 'src_4586', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compare_point_to_line_distances', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'compare_point_to_line_distances', 'display_order': 4586, 'source_order': 4586, 'sampling_weight': 1.0}, {'textbook_example_id': 4587, 'component_id': 'src_4587', 'generator_key': 'src_4587', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'distance_from_point_to_line_parameter', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'distance_from_point_to_line_parameter', 'display_order': 4587, 'source_order': 4587, 'sampling_weight': 1.0}, {'textbook_example_id': 4607, 'component_id': 'src_4607', 'generator_key': 'src_4607', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'distance_from_point_to_line_parameter_single_choice_scalar', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'distance_from_point_to_line_parameter_single_choice_scalar', 'display_order': 4607, 'source_order': 4607, 'sampling_weight': 1.0}]


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
