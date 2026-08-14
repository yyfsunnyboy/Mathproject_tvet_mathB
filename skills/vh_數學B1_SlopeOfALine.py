from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_SlopeOfALine'
GENERATOR_KEYS = ['src_4519', 'src_4520', 'src_4521', 'src_4522', 'src_4523', 'src_4524', 'src_4525', 'src_4529', 'src_4533', 'src_4534', 'src_4590', 'src_4601']
GENERATOR_SPECS = [{'textbook_example_id': 4519, 'component_id': 'src_4519', 'generator_key': 'src_4519', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'slopes_of_named_segments', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'slopes_of_named_segments', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4519, 'source_order': 4519, 'sampling_weight': 10.0}, {'textbook_example_id': 4520, 'component_id': 'src_4520', 'generator_key': 'src_4520', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_and_compare_figure_slopes', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_and_compare_figure_slopes', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4520, 'source_order': 4520, 'sampling_weight': 10.0}, {'textbook_example_id': 4521, 'component_id': 'src_4521', 'generator_key': 'src_4521', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'slope_from_two_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'slope_from_two_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4521, 'source_order': 4521, 'sampling_weight': 10.0}, {'textbook_example_id': 4522, 'component_id': 'src_4522', 'generator_key': 'src_4522', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_parameter_from_known_slope', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parameter_from_known_slope', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4522, 'source_order': 4522, 'sampling_weight': 10.0}, {'textbook_example_id': 4523, 'component_id': 'src_4523', 'generator_key': 'src_4523', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'collinear_three_points_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'collinear_three_points_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4523, 'source_order': 4523, 'sampling_weight': 10.0}, {'textbook_example_id': 4524, 'component_id': 'src_4524', 'generator_key': 'src_4524', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'non_triangle_collinear_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'non_triangle_collinear_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4524, 'source_order': 4524, 'sampling_weight': 10.0}, {'textbook_example_id': 4525, 'component_id': 'src_4525', 'generator_key': 'src_4525', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'parallel_segments_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'parallel_segments_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4525, 'source_order': 4525, 'sampling_weight': 10.0}, {'textbook_example_id': 4529, 'component_id': 'src_4529', 'generator_key': 'src_4529', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'collinear_three_points_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'collinear_three_points_parameter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4529, 'source_order': 4529, 'sampling_weight': 10.0}, {'textbook_example_id': 4533, 'component_id': 'src_4533', 'generator_key': 'src_4533', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'slopes_of_named_segments', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'slopes_of_named_segments', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4533, 'source_order': 4533, 'sampling_weight': 10.0}, {'textbook_example_id': 4534, 'component_id': 'src_4534', 'generator_key': 'src_4534', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'non_triangle_collinear_parameter', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'non_triangle_collinear_parameter', 'checker_key': 'integer_checker', 'equivalence_type': None, 'display_order': 4534, 'source_order': 4534, 'sampling_weight': 10.0}, {'textbook_example_id': 4590, 'component_id': 'src_4590', 'generator_key': 'src_4590', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_parameter_from_known_slope_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_parameter_from_known_slope_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4590, 'source_order': 4590, 'sampling_weight': 10.0}, {'textbook_example_id': 4601, 'component_id': 'src_4601', 'generator_key': 'src_4601', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'collinear_three_points_parameter_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'collinear_three_points_parameter_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4601, 'source_order': 4601, 'sampling_weight': 10.0}]


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
