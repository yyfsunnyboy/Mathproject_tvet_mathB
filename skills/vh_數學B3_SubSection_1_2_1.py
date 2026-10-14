from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_2_1'
GENERATOR_KEYS = ['src_11924', 'src_11925', 'src_11926', 'src_11927', 'src_11928', 'src_11929', 'src_11930', 'src_11931', 'src_11941', 'src_11942', 'src_11943', 'src_11944', 'src_11949', 'src_11950', 'src_11953', 'src_11954', 'src_11955', 'src_11956', 'src_11957']
GENERATOR_SPECS = [{'textbook_example_id': 11924, 'component_id': 'src_11924', 'generator_key': 'src_11924', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11924, 'source_order': 11924, 'sampling_weight': 10.0}, {'textbook_example_id': 11925, 'component_id': 'src_11925', 'generator_key': 'src_11925', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11925, 'source_order': 11925, 'sampling_weight': 10.0}, {'textbook_example_id': 11926, 'component_id': 'src_11926', 'generator_key': 'src_11926', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11926, 'source_order': 11926, 'sampling_weight': 10.0}, {'textbook_example_id': 11927, 'component_id': 'src_11927', 'generator_key': 'src_11927', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_r_from_a1_an', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_r_from_a1_an', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11927, 'source_order': 11927, 'sampling_weight': 10.0}, {'textbook_example_id': 11928, 'component_id': 'src_11928', 'generator_key': 'src_11928', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_from_two_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11928, 'source_order': 11928, 'sampling_weight': 10.0}, {'textbook_example_id': 11929, 'component_id': 'src_11929', 'generator_key': 'src_11929', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_from_two_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11929, 'source_order': 11929, 'sampling_weight': 10.0}, {'textbook_example_id': 11930, 'component_id': 'src_11930', 'generator_key': 'src_11930', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_ratio_from_shifted_pair_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_ratio_from_shifted_pair_sums', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11930, 'source_order': 11930, 'sampling_weight': 10.0}, {'textbook_example_id': 11931, 'component_id': 'src_11931', 'generator_key': 'src_11931', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_ratio_from_product_quotient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_ratio_from_product_quotient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11931, 'source_order': 11931, 'sampling_weight': 10.0}, {'textbook_example_id': 11941, 'component_id': 'src_11941', 'generator_key': 'src_11941', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11941, 'source_order': 11941, 'sampling_weight': 10.0}, {'textbook_example_id': 11942, 'component_id': 'src_11942', 'generator_key': 'src_11942', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_from_two_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11942, 'source_order': 11942, 'sampling_weight': 10.0}, {'textbook_example_id': 11943, 'component_id': 'src_11943', 'generator_key': 'src_11943', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_insert_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_insert_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11943, 'source_order': 11943, 'sampling_weight': 10.0}, {'textbook_example_id': 11944, 'component_id': 'src_11944', 'generator_key': 'src_11944', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_ratio_from_shifted_pair_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_ratio_from_shifted_pair_sums', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11944, 'source_order': 11944, 'sampling_weight': 10.0}, {'textbook_example_id': 11949, 'component_id': 'src_11949', 'generator_key': 'src_11949', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exercise', 'line_type': 'geometric_from_two_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11949, 'source_order': 11949, 'sampling_weight': 10.0}, {'textbook_example_id': 11950, 'component_id': 'src_11950', 'generator_key': 'src_11950', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_growth_table_cells', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'geometric_growth_table_cells', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11950, 'source_order': 11950, 'sampling_weight': 10.0}, {'textbook_example_id': 11953, 'component_id': 'src_11953', 'generator_key': 'src_11953', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11953, 'source_order': 11953, 'sampling_weight': 10.0}, {'textbook_example_id': 11954, 'component_id': 'src_11954', 'generator_key': 'src_11954', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_from_two_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11954, 'source_order': 11954, 'sampling_weight': 10.0}, {'textbook_example_id': 11955, 'component_id': 'src_11955', 'generator_key': 'src_11955', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_from_two_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_from_two_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11955, 'source_order': 11955, 'sampling_weight': 10.0}, {'textbook_example_id': 11956, 'component_id': 'src_11956', 'generator_key': 'src_11956', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_nth_from_a1_r', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_nth_from_a1_r', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11956, 'source_order': 11956, 'sampling_weight': 10.0}, {'textbook_example_id': 11957, 'component_id': 'src_11957', 'generator_key': 'src_11957', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'geometric_ratio_from_shifted_pair_sums', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'geometric_ratio_from_shifted_pair_sums', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11957, 'source_order': 11957, 'sampling_weight': 10.0}]


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
