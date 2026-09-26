from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_1_2'
GENERATOR_KEYS = ['src_11899', 'src_11900', 'src_11902', 'src_11903', 'src_11914', 'src_11915', 'src_11916', 'src_11923', 'src_11951', 'src_11961', 'src_11963', 'src_11966']
GENERATOR_SPECS = [{'textbook_example_id': 11899, 'component_id': 'src_11899', 'generator_key': 'src_11899', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_nth_from_a1_d', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_nth_from_a1_d', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11899, 'source_order': 11899, 'sampling_weight': 10.0}, {'textbook_example_id': 11900, 'component_id': 'src_11900', 'generator_key': 'src_11900', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_nth_from_a1_d', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_nth_from_a1_d', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11900, 'source_order': 11900, 'sampling_weight': 10.0}, {'textbook_example_id': 11902, 'component_id': 'src_11902', 'generator_key': 'src_11902', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_insert_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_insert_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11902, 'source_order': 11902, 'sampling_weight': 10.0}, {'textbook_example_id': 11903, 'component_id': 'src_11903', 'generator_key': 'src_11903', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_insert_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_insert_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11903, 'source_order': 11903, 'sampling_weight': 10.0}, {'textbook_example_id': 11914, 'component_id': 'src_11914', 'generator_key': 'src_11914', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_nth_from_a1_d', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_nth_from_a1_d', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11914, 'source_order': 11914, 'sampling_weight': 10.0}, {'textbook_example_id': 11915, 'component_id': 'src_11915', 'generator_key': 'src_11915', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_from_two_terms', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_from_two_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11915, 'source_order': 11915, 'sampling_weight': 10.0}, {'textbook_example_id': 11916, 'component_id': 'src_11916', 'generator_key': 'src_11916', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_insert_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_insert_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11916, 'source_order': 11916, 'sampling_weight': 10.0}, {'textbook_example_id': 11923, 'component_id': 'src_11923', 'generator_key': 'src_11923', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_from_two_terms', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_from_two_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11923, 'source_order': 11923, 'sampling_weight': 10.0}, {'textbook_example_id': 11951, 'component_id': 'src_11951', 'generator_key': 'src_11951', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_d_from_a1_an', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_d_from_a1_an', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11951, 'source_order': 11951, 'sampling_weight': 10.0}, {'textbook_example_id': 11961, 'component_id': 'src_11961', 'generator_key': 'src_11961', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_nth_from_a1_d', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_nth_from_a1_d', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11961, 'source_order': 11961, 'sampling_weight': 10.0}, {'textbook_example_id': 11963, 'component_id': 'src_11963', 'generator_key': 'src_11963', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_first_threshold_crossing', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_first_threshold_crossing', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11963, 'source_order': 11963, 'sampling_weight': 10.0}, {'textbook_example_id': 11966, 'component_id': 'src_11966', 'generator_key': 'src_11966', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_insert_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_insert_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11966, 'source_order': 11966, 'sampling_weight': 10.0}]


def _resolve_v3_package_root() -> str:
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
