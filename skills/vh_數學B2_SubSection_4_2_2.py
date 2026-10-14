from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_2_2'
GENERATOR_KEYS = ['src_11853', 'src_11854', 'src_11855', 'src_11856', 'src_11857', 'src_11858', 'src_11867', 'src_11868', 'src_11869', 'src_11870', 'src_11874', 'src_11878', 'src_11879', 'src_11880', 'src_11881', 'src_11882', 'src_11883']
GENERATOR_SPECS = [{'textbook_example_id': 11853, 'component_id': 'src_11853', 'generator_key': 'src_11853', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_line_circle_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_line_circle_relation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11853, 'source_order': 11853, 'sampling_weight': 10.0}, {'textbook_example_id': 11854, 'component_id': 'src_11854', 'generator_key': 'src_11854', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'classify_lines_vs_circle_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_lines_vs_circle_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11854, 'source_order': 11854, 'sampling_weight': 10.0}, {'textbook_example_id': 11855, 'component_id': 'src_11855', 'generator_key': 'src_11855', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_line_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11855, 'source_order': 11855, 'sampling_weight': 10.0}, {'textbook_example_id': 11856, 'component_id': 'src_11856', 'generator_key': 'src_11856', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_line_circle_tangent_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_circle_tangent_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11856, 'source_order': 11856, 'sampling_weight': 10.0}, {'textbook_example_id': 11857, 'component_id': 'src_11857', 'generator_key': 'src_11857', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_chord_length', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_chord_length', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11857, 'source_order': 11857, 'sampling_weight': 10.0}, {'textbook_example_id': 11858, 'component_id': 'src_11858', 'generator_key': 'src_11858', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_chord_length', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_chord_length', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11858, 'source_order': 11858, 'sampling_weight': 10.0}, {'textbook_example_id': 11867, 'component_id': 'src_11867', 'generator_key': 'src_11867', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_lines_vs_circle_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_lines_vs_circle_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11867, 'source_order': 11867, 'sampling_weight': 10.0}, {'textbook_example_id': 11868, 'component_id': 'src_11868', 'generator_key': 'src_11868', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_line_circle_relation_ranges_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_circle_relation_ranges_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11868, 'source_order': 11868, 'sampling_weight': 10.0}, {'textbook_example_id': 11869, 'component_id': 'src_11869', 'generator_key': 'src_11869', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'count_line_circle_intersections', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'count_line_circle_intersections', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11869, 'source_order': 11869, 'sampling_weight': 10.0}, {'textbook_example_id': 11870, 'component_id': 'src_11870', 'generator_key': 'src_11870', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_chord_length', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_chord_length', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11870, 'source_order': 11870, 'sampling_weight': 10.0}, {'textbook_example_id': 11874, 'component_id': 'src_11874', 'generator_key': 'src_11874', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_storm_path_length_in_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_storm_path_length_in_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11874, 'source_order': 11874, 'sampling_weight': 10.0}, {'textbook_example_id': 11878, 'component_id': 'src_11878', 'generator_key': 'src_11878', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'classify_line_circle_relation_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'classify_line_circle_relation_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11878, 'source_order': 11878, 'sampling_weight': 10.0}, {'textbook_example_id': 11879, 'component_id': 'src_11879', 'generator_key': 'src_11879', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_diameter_chord_parameter_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_diameter_chord_parameter_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11879, 'source_order': 11879, 'sampling_weight': 10.0}, {'textbook_example_id': 11880, 'component_id': 'src_11880', 'generator_key': 'src_11880', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_line_circle_tangent_parameter', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_line_circle_tangent_parameter', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11880, 'source_order': 11880, 'sampling_weight': 10.0}, {'textbook_example_id': 11881, 'component_id': 'src_11881', 'generator_key': 'src_11881', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_triangle_center_chord_area', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_triangle_center_chord_area', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11881, 'source_order': 11881, 'sampling_weight': 10.0}, {'textbook_example_id': 11882, 'component_id': 'src_11882', 'generator_key': 'src_11882', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'classify_line_circle_relation_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'classify_line_circle_relation_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11882, 'source_order': 11882, 'sampling_weight': 10.0}, {'textbook_example_id': 11883, 'component_id': 'src_11883', 'generator_key': 'src_11883', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_axis_tangent_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_axis_tangent_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11883, 'source_order': 11883, 'sampling_weight': 10.0}]


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
