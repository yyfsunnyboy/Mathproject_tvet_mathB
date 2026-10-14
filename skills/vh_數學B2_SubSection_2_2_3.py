from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_2_2_3'
GENERATOR_KEYS = ['src_11687', 'src_11688', 'src_11689', 'src_11690', 'src_11698', 'src_11699', 'src_11700', 'src_11701', 'src_11704', 'src_11720', 'src_11723', 'src_11728', 'src_11729', 'src_11730']
GENERATOR_SPECS = [{'textbook_example_id': 11687, 'component_id': 'src_11687', 'generator_key': 'src_11687', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_height_from_sight_line_elevation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_height_from_sight_line_elevation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11687, 'source_order': 11687, 'sampling_weight': 10.0}, {'textbook_example_id': 11688, 'component_id': 'src_11688', 'generator_key': 'src_11688', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_adjacent_from_hypotenuse_ground_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_adjacent_from_hypotenuse_ground_angle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11688, 'source_order': 11688, 'sampling_weight': 10.0}, {'textbook_example_id': 11689, 'component_id': 'src_11689', 'generator_key': 'src_11689', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_two_elevation_horizontal_shift', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_two_elevation_horizontal_shift', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11689, 'source_order': 11689, 'sampling_weight': 10.0}, {'textbook_example_id': 11690, 'component_id': 'src_11690', 'generator_key': 'src_11690', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_two_elevation_unknown_height', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_two_elevation_unknown_height', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11690, 'source_order': 11690, 'sampling_weight': 10.0}, {'textbook_example_id': 11698, 'component_id': 'src_11698', 'generator_key': 'src_11698', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_height_decimal_from_sight_line_elevation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_height_decimal_from_sight_line_elevation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11698, 'source_order': 11698, 'sampling_weight': 10.0}, {'textbook_example_id': 11699, 'component_id': 'src_11699', 'generator_key': 'src_11699', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_opposite_from_adjacent_elevation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_opposite_from_adjacent_elevation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11699, 'source_order': 11699, 'sampling_weight': 10.0}, {'textbook_example_id': 11700, 'component_id': 'src_11700', 'generator_key': 'src_11700', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_adjacent_from_hypotenuse_ground_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_adjacent_from_hypotenuse_ground_angle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11700, 'source_order': 11700, 'sampling_weight': 10.0}, {'textbook_example_id': 11701, 'component_id': 'src_11701', 'generator_key': 'src_11701', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_two_elevation_unknown_height', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_two_elevation_unknown_height', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11701, 'source_order': 11701, 'sampling_weight': 10.0}, {'textbook_example_id': 11704, 'component_id': 'src_11704', 'generator_key': 'src_11704', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_broken_tree_original_height', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_broken_tree_original_height', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11704, 'source_order': 11704, 'sampling_weight': 10.0}, {'textbook_example_id': 11720, 'component_id': 'src_11720', 'generator_key': 'src_11720', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_building_height_with_flagpole_elevations', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_building_height_with_flagpole_elevations', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11720, 'source_order': 11720, 'sampling_weight': 10.0}, {'textbook_example_id': 11723, 'component_id': 'src_11723', 'generator_key': 'src_11723', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_horizontal_from_height_depression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_horizontal_from_height_depression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11723, 'source_order': 11723, 'sampling_weight': 10.0}, {'textbook_example_id': 11728, 'component_id': 'src_11728', 'generator_key': 'src_11728', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_opposite_from_adjacent_elevation', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_opposite_from_adjacent_elevation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11728, 'source_order': 11728, 'sampling_weight': 10.0}, {'textbook_example_id': 11729, 'component_id': 'src_11729', 'generator_key': 'src_11729', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_horizontal_from_height_elevation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_horizontal_from_height_elevation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11729, 'source_order': 11729, 'sampling_weight': 10.0}, {'textbook_example_id': 11730, 'component_id': 'src_11730', 'generator_key': 'src_11730', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_two_elevation_horizontal_shift', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_two_elevation_horizontal_shift', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11730, 'source_order': 11730, 'sampling_weight': 10.0}]


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
