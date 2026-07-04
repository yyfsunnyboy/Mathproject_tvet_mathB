from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_LinearFunction'
GENERATOR_KEYS = ['src_4424', 'src_4425', 'src_4426', 'src_4433', 'src_4434', 'src_4441', 'src_4442', 'src_4444', 'src_4445', 'src_4446', 'src_4448', 'src_4449', 'src_4500', 'src_4515', 'src_4516']
GENERATOR_SPECS = [{'textbook_example_id': 4424, 'component_id': 'src_4424', 'generator_key': 'src_4424', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4424, 'source_order': 4424, 'sampling_weight': 10.0}, {'textbook_example_id': 4425, 'component_id': 'src_4425', 'generator_key': 'src_4425', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_based_tiered_linear_application_multi_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4425, 'source_order': 4425, 'sampling_weight': 10.0}, {'textbook_example_id': 4426, 'component_id': 'src_4426', 'generator_key': 'src_4426', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'collinear_trisection_coordinate', 'answer_type': 'coordinate_pair', 'answer_value_type': 'coordinate_pair', 'problem_type_id': 'collinear_trisection_coordinate', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': None, 'display_order': 4426, 'source_order': 4426, 'sampling_weight': 10.0}, {'textbook_example_id': 4433, 'component_id': 'src_4433', 'generator_key': 'src_4433', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'draw_constant_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_constant_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4433, 'source_order': 4433, 'sampling_weight': 10.0}, {'textbook_example_id': 4434, 'component_id': 'src_4434', 'generator_key': 'src_4434', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'draw_linear_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_linear_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4434, 'source_order': 4434, 'sampling_weight': 10.0}, {'textbook_example_id': 4441, 'component_id': 'src_4441', 'generator_key': 'src_4441', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'quiz', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4441, 'source_order': 4441, 'sampling_weight': 10.0}, {'textbook_example_id': 4442, 'component_id': 'src_4442', 'generator_key': 'src_4442', 'presentation_mode': 'graph_short_answer', 'response_mode': 'graph_short_answer', 'interaction_type': 'graph_short_answer', 'source_kind': 'quiz', 'line_type': 'graph_based_linear_application_inverse', 'answer_type': 'numeric', 'answer_value_type': 'numeric', 'problem_type_id': 'graph_based_linear_application_inverse', 'checker_key': 'numeric_checker', 'equivalence_type': None, 'display_order': 4442, 'source_order': 4442, 'sampling_weight': 10.0}, {'textbook_example_id': 4444, 'component_id': 'src_4444', 'generator_key': 'src_4444', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4444, 'source_order': 4444, 'sampling_weight': 10.0}, {'textbook_example_id': 4445, 'component_id': 'src_4445', 'generator_key': 'src_4445', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_based_tiered_linear_application_multi_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4445, 'source_order': 4445, 'sampling_weight': 10.0}, {'textbook_example_id': 4446, 'component_id': 'src_4446', 'generator_key': 'src_4446', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'robust_budget_feasibility_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'robust_budget_feasibility_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4446, 'source_order': 4446, 'sampling_weight': 10.0}, {'textbook_example_id': 4448, 'component_id': 'src_4448', 'generator_key': 'src_4448', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'quiz', 'line_type': 'draw_constant_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_constant_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4448, 'source_order': 4448, 'sampling_weight': 10.0}, {'textbook_example_id': 4449, 'component_id': 'src_4449', 'generator_key': 'src_4449', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'quiz', 'line_type': 'draw_linear_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_linear_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4449, 'source_order': 4449, 'sampling_weight': 10.0}, {'textbook_example_id': 4500, 'component_id': 'src_4500', 'generator_key': 'src_4500', 'presentation_mode': 'graph_single_choice', 'response_mode': 'graph_single_choice', 'interaction_type': 'graph_single_choice', 'source_kind': 'test', 'line_type': 'graph_based_linear_model_equation', 'answer_type': 'single_choice', 'answer_value_type': 'choice', 'problem_type_id': 'graph_based_linear_model_equation', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4500, 'source_order': 4500, 'sampling_weight': 10.0}, {'textbook_example_id': 4515, 'component_id': 'src_4515', 'generator_key': 'src_4515', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'linear_equation_from_two_points_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'linear_equation_from_two_points_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4515, 'source_order': 4515, 'sampling_weight': 10.0}, {'textbook_example_id': 4516, 'component_id': 'src_4516', 'generator_key': 'src_4516', 'presentation_mode': 'graph_single_choice', 'response_mode': 'graph_single_choice', 'interaction_type': 'graph_single_choice', 'source_kind': 'test', 'line_type': 'linear_graph_feasibility_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'linear_graph_feasibility_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4516, 'source_order': 4516, 'sampling_weight': 10.0}]


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
