from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_2_2'
GENERATOR_KEYS = ['src_11762', 'src_11763', 'src_11764', 'src_11765', 'src_11766', 'src_11767', 'src_11776', 'src_11777', 'src_11778', 'src_11779', 'src_11780', 'src_11807', 'src_11808', 'src_11819']
GENERATOR_SPECS = [{'textbook_example_id': 11762, 'component_id': 'src_11762', 'generator_key': 'src_11762', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11762, 'source_order': 11762, 'sampling_weight': 10.0}, {'textbook_example_id': 11763, 'component_id': 'src_11763', 'generator_key': 'src_11763', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11763, 'source_order': 11763, 'sampling_weight': 10.0}, {'textbook_example_id': 11764, 'component_id': 'src_11764', 'generator_key': 'src_11764', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11764, 'source_order': 11764, 'sampling_weight': 10.0}, {'textbook_example_id': 11765, 'component_id': 'src_11765', 'generator_key': 'src_11765', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11765, 'source_order': 11765, 'sampling_weight': 10.0}, {'textbook_example_id': 11766, 'component_id': 'src_11766', 'generator_key': 'src_11766', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11766, 'source_order': 11766, 'sampling_weight': 10.0}, {'textbook_example_id': 11767, 'component_id': 'src_11767', 'generator_key': 'src_11767', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11767, 'source_order': 11767, 'sampling_weight': 10.0}, {'textbook_example_id': 11776, 'component_id': 'src_11776', 'generator_key': 'src_11776', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_parallelogram_fourth_vertex', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parallelogram_fourth_vertex', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11776, 'source_order': 11776, 'sampling_weight': 10.0}, {'textbook_example_id': 11777, 'component_id': 'src_11777', 'generator_key': 'src_11777', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11777, 'source_order': 11777, 'sampling_weight': 10.0}, {'textbook_example_id': 11778, 'component_id': 'src_11778', 'generator_key': 'src_11778', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11778, 'source_order': 11778, 'sampling_weight': 10.0}, {'textbook_example_id': 11779, 'component_id': 'src_11779', 'generator_key': 'src_11779', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11779, 'source_order': 11779, 'sampling_weight': 10.0}, {'textbook_example_id': 11780, 'component_id': 'src_11780', 'generator_key': 'src_11780', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11780, 'source_order': 11780, 'sampling_weight': 10.0}, {'textbook_example_id': 11807, 'component_id': 'src_11807', 'generator_key': 'src_11807', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11807, 'source_order': 11807, 'sampling_weight': 10.0}, {'textbook_example_id': 11808, 'component_id': 'src_11808', 'generator_key': 'src_11808', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_vector_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11808, 'source_order': 11808, 'sampling_weight': 10.0}, {'textbook_example_id': 11819, 'component_id': 'src_11819', 'generator_key': 'src_11819', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11819, 'source_order': 11819, 'sampling_weight': 10.0}]


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
