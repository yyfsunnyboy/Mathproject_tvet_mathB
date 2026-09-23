from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_2_1_1'
GENERATOR_KEYS = ['src_11676', 'src_11677', 'src_11678', 'src_11679', 'src_11680', 'src_11681', 'src_11707', 'src_11708', 'src_11709', 'src_11710', 'src_11716', 'src_11717', 'src_11718']
GENERATOR_SPECS = [{'textbook_example_id': 11676, 'component_id': 'src_11676', 'generator_key': 'src_11676', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_area_sas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_area_sas', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11676, 'source_order': 11676, 'sampling_weight': 10.0}, {'textbook_example_id': 11677, 'component_id': 'src_11677', 'generator_key': 'src_11677', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_triangle_area_sas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_area_sas', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11677, 'source_order': 11677, 'sampling_weight': 10.0}, {'textbook_example_id': 11678, 'component_id': 'src_11678', 'generator_key': 'src_11678', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_and_circumradius_by_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_and_circumradius_by_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11678, 'source_order': 11678, 'sampling_weight': 10.0}, {'textbook_example_id': 11679, 'component_id': 'src_11679', 'generator_key': 'src_11679', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_side_and_circumradius_by_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_and_circumradius_by_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11679, 'source_order': 11679, 'sampling_weight': 10.0}, {'textbook_example_id': 11680, 'component_id': 'src_11680', 'generator_key': 'src_11680', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11680, 'source_order': 11680, 'sampling_weight': 10.0}, {'textbook_example_id': 11681, 'component_id': 'src_11681', 'generator_key': 'src_11681', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_angle_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11681, 'source_order': 11681, 'sampling_weight': 10.0}, {'textbook_example_id': 11707, 'component_id': 'src_11707', 'generator_key': 'src_11707', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_area_sas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_area_sas', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11707, 'source_order': 11707, 'sampling_weight': 10.0}, {'textbook_example_id': 11708, 'component_id': 'src_11708', 'generator_key': 'src_11708', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_and_circumradius_by_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_and_circumradius_by_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11708, 'source_order': 11708, 'sampling_weight': 10.0}, {'textbook_example_id': 11709, 'component_id': 'src_11709', 'generator_key': 'src_11709', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11709, 'source_order': 11709, 'sampling_weight': 10.0}, {'textbook_example_id': 11710, 'component_id': 'src_11710', 'generator_key': 'src_11710', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11710, 'source_order': 11710, 'sampling_weight': 10.0}, {'textbook_example_id': 11716, 'component_id': 'src_11716', 'generator_key': 'src_11716', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_sin_from_side_and_circumradius', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_sin_from_side_and_circumradius', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11716, 'source_order': 11716, 'sampling_weight': 10.0}, {'textbook_example_id': 11717, 'component_id': 'src_11717', 'generator_key': 'src_11717', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_side_ratio_by_law_of_sines', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_side_ratio_by_law_of_sines', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11717, 'source_order': 11717, 'sampling_weight': 10.0}, {'textbook_example_id': 11718, 'component_id': 'src_11718', 'generator_key': 'src_11718', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_side_by_law_of_sines', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_side_by_law_of_sines', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11718, 'source_order': 11718, 'sampling_weight': 10.0}]


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
