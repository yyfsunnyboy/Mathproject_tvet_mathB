from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_2_1'
GENERATOR_KEYS = ['src_11754', 'src_11755', 'src_11756', 'src_11757', 'src_11758', 'src_11759', 'src_11760', 'src_11761', 'src_11775', 'src_11783', 'src_11822']
GENERATOR_SPECS = [{'textbook_example_id': 11754, 'component_id': 'src_11754', 'generator_key': 'src_11754', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_components_and_magnitude', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_components_and_magnitude', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11754, 'source_order': 11754, 'sampling_weight': 10.0}, {'textbook_example_id': 11755, 'component_id': 'src_11755', 'generator_key': 'src_11755', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_vector_components_and_magnitude', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_components_and_magnitude', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11755, 'source_order': 11755, 'sampling_weight': 10.0}, {'textbook_example_id': 11756, 'component_id': 'src_11756', 'generator_key': 'src_11756', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_equal_vector_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_equal_vector_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11756, 'source_order': 11756, 'sampling_weight': 10.0}, {'textbook_example_id': 11757, 'component_id': 'src_11757', 'generator_key': 'src_11757', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_equal_vector_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_equal_vector_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11757, 'source_order': 11757, 'sampling_weight': 10.0}, {'textbook_example_id': 11758, 'component_id': 'src_11758', 'generator_key': 'src_11758', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_directed_segment_and_magnitude', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_directed_segment_and_magnitude', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11758, 'source_order': 11758, 'sampling_weight': 10.0}, {'textbook_example_id': 11759, 'component_id': 'src_11759', 'generator_key': 'src_11759', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_directed_segment_and_magnitude', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_directed_segment_and_magnitude', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11759, 'source_order': 11759, 'sampling_weight': 10.0}, {'textbook_example_id': 11760, 'component_id': 'src_11760', 'generator_key': 'src_11760', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_parallelogram_fourth_vertex', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parallelogram_fourth_vertex', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11760, 'source_order': 11760, 'sampling_weight': 10.0}, {'textbook_example_id': 11761, 'component_id': 'src_11761', 'generator_key': 'src_11761', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_parallelogram_fourth_vertex', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parallelogram_fourth_vertex', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11761, 'source_order': 11761, 'sampling_weight': 10.0}, {'textbook_example_id': 11775, 'component_id': 'src_11775', 'generator_key': 'src_11775', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_directed_segment_mixed_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_directed_segment_mixed_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11775, 'source_order': 11775, 'sampling_weight': 10.0}, {'textbook_example_id': 11783, 'component_id': 'src_11783', 'generator_key': 'src_11783', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_directed_segment_and_magnitude', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_directed_segment_and_magnitude', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11783, 'source_order': 11783, 'sampling_weight': 10.0}, {'textbook_example_id': 11822, 'component_id': 'src_11822', 'generator_key': 'src_11822', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_triangle_perimeter_from_two_vectors', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_triangle_perimeter_from_two_vectors', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11822, 'source_order': 11822, 'sampling_weight': 10.0}]


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
