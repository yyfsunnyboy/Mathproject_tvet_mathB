from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PropertiesOfPerpendicularLines'
GENERATOR_KEYS = ['src_4526', 'src_4527', 'src_4531', 'src_4532', 'src_4536', 'src_4537', 'src_4538', 'src_4539']
GENERATOR_SPECS = [{'textbook_example_id': 4526, 'component_id': 'src_4526', 'generator_key': 'src_4526', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'parallel_and_perpendicular_slopes_from_reference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'parallel_and_perpendicular_slopes_from_reference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4526, 'source_order': 4526, 'sampling_weight': 10.0}, {'textbook_example_id': 4527, 'component_id': 'src_4527', 'generator_key': 'src_4527', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'triangle_right_angle_verification', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'triangle_right_angle_verification', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4527, 'source_order': 4527, 'sampling_weight': 10.0}, {'textbook_example_id': 4531, 'component_id': 'src_4531', 'generator_key': 'src_4531', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'perpendicular_segments_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'perpendicular_segments_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4531, 'source_order': 4531, 'sampling_weight': 10.0}, {'textbook_example_id': 4532, 'component_id': 'src_4532', 'generator_key': 'src_4532', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'parallel_and_perpendicular_slopes_from_reference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'parallel_and_perpendicular_slopes_from_reference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4532, 'source_order': 4532, 'sampling_weight': 10.0}, {'textbook_example_id': 4536, 'component_id': 'src_4536', 'generator_key': 'src_4536', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'perpendicular_segments_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'perpendicular_segments_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4536, 'source_order': 4536, 'sampling_weight': 10.0}, {'textbook_example_id': 4537, 'component_id': 'src_4537', 'generator_key': 'src_4537', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'perpendicular_two_point_lines_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'perpendicular_two_point_lines_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4537, 'source_order': 4537, 'sampling_weight': 10.0}, {'textbook_example_id': 4538, 'component_id': 'src_4538', 'generator_key': 'src_4538', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'perpendicular_slope_quadrant_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'perpendicular_slope_quadrant_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4538, 'source_order': 4538, 'sampling_weight': 10.0}, {'textbook_example_id': 4539, 'component_id': 'src_4539', 'generator_key': 'src_4539', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'parallel_and_perpendicular_slopes_from_reference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'parallel_and_perpendicular_slopes_from_reference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4539, 'source_order': 4539, 'sampling_weight': 10.0}]


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
