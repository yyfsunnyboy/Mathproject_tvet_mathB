from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_1_2'
GENERATOR_KEYS = ['src_11832', 'src_11833', 'src_11834', 'src_11835', 'src_11836', 'src_11837', 'src_11838', 'src_11839', 'src_11840', 'src_11845', 'src_11846', 'src_11847', 'src_11848', 'src_11849', 'src_11876', 'src_11888', 'src_11889', 'src_11892', 'src_11893']
GENERATOR_SPECS = [{'textbook_example_id': 11832, 'component_id': 'src_11832', 'generator_key': 'src_11832', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11832, 'source_order': 11832, 'sampling_weight': 10.0}, {'textbook_example_id': 11833, 'component_id': 'src_11833', 'generator_key': 'src_11833', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11833, 'source_order': 11833, 'sampling_weight': 10.0}, {'textbook_example_id': 11834, 'component_id': 'src_11834', 'generator_key': 'src_11834', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11834, 'source_order': 11834, 'sampling_weight': 10.0}, {'textbook_example_id': 11835, 'component_id': 'src_11835', 'generator_key': 'src_11835', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11835, 'source_order': 11835, 'sampling_weight': 10.0}, {'textbook_example_id': 11836, 'component_id': 'src_11836', 'generator_key': 'src_11836', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11836, 'source_order': 11836, 'sampling_weight': 10.0}, {'textbook_example_id': 11837, 'component_id': 'src_11837', 'generator_key': 'src_11837', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11837, 'source_order': 11837, 'sampling_weight': 10.0}, {'textbook_example_id': 11838, 'component_id': 'src_11838', 'generator_key': 'src_11838', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11838, 'source_order': 11838, 'sampling_weight': 10.0}, {'textbook_example_id': 11839, 'component_id': 'src_11839', 'generator_key': 'src_11839', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11839, 'source_order': 11839, 'sampling_weight': 10.0}, {'textbook_example_id': 11840, 'component_id': 'src_11840', 'generator_key': 'src_11840', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'circle_center_on_axis_area', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'circle_center_on_axis_area', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11840, 'source_order': 11840, 'sampling_weight': 10.0}, {'textbook_example_id': 11845, 'component_id': 'src_11845', 'generator_key': 'src_11845', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11845, 'source_order': 11845, 'sampling_weight': 10.0}, {'textbook_example_id': 11846, 'component_id': 'src_11846', 'generator_key': 'src_11846', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_general_circle_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_general_circle_graph', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11846, 'source_order': 11846, 'sampling_weight': 10.0}, {'textbook_example_id': 11847, 'component_id': 'src_11847', 'generator_key': 'src_11847', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11847, 'source_order': 11847, 'sampling_weight': 10.0}, {'textbook_example_id': 11848, 'component_id': 'src_11848', 'generator_key': 'src_11848', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11848, 'source_order': 11848, 'sampling_weight': 10.0}, {'textbook_example_id': 11849, 'component_id': 'src_11849', 'generator_key': 'src_11849', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11849, 'source_order': 11849, 'sampling_weight': 10.0}, {'textbook_example_id': 11876, 'component_id': 'src_11876', 'generator_key': 'src_11876', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'evaluate_center_radius_expression', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'evaluate_center_radius_expression', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11876, 'source_order': 11876, 'sampling_weight': 10.0}, {'textbook_example_id': 11888, 'component_id': 'src_11888', 'generator_key': 'src_11888', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_circle_area_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_circle_area_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11888, 'source_order': 11888, 'sampling_weight': 10.0}, {'textbook_example_id': 11889, 'component_id': 'src_11889', 'generator_key': 'src_11889', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'identify_circle_from_product_form', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'identify_circle_from_product_form', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11889, 'source_order': 11889, 'sampling_weight': 10.0}, {'textbook_example_id': 11892, 'component_id': 'src_11892', 'generator_key': 'src_11892', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11892, 'source_order': 11892, 'sampling_weight': 10.0}, {'textbook_example_id': 11893, 'component_id': 'src_11893', 'generator_key': 'src_11893', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_circle_parameter_range_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_circle_parameter_range_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11893, 'source_order': 11893, 'sampling_weight': 10.0}]


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
