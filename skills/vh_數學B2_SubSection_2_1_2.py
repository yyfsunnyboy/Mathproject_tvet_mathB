from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_2_1_2'
GENERATOR_KEYS = ['src_11682', 'src_11683', 'src_11684', 'src_11685', 'src_11686', 'src_11711', 'src_11712', 'src_11713', 'src_11714', 'src_11715', 'src_11719', 'src_11727']
GENERATOR_SPECS = [{'textbook_example_id': 11682, 'component_id': 'src_11682', 'generator_key': 'src_11682', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11682, 'source_order': 11682, 'sampling_weight': 10.0}, {'textbook_example_id': 11683, 'component_id': 'src_11683', 'generator_key': 'src_11683', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11683, 'source_order': 11683, 'sampling_weight': 10.0}, {'textbook_example_id': 11684, 'component_id': 'src_11684', 'generator_key': 'src_11684', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11684, 'source_order': 11684, 'sampling_weight': 10.0}, {'textbook_example_id': 11685, 'component_id': 'src_11685', 'generator_key': 'src_11685', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_angle_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11685, 'source_order': 11685, 'sampling_weight': 10.0}, {'textbook_example_id': 11686, 'component_id': 'src_11686', 'generator_key': 'src_11686', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'solve_detour_extra_distance_by_cosines', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_detour_extra_distance_by_cosines', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11686, 'source_order': 11686, 'sampling_weight': 10.0}, {'textbook_example_id': 11711, 'component_id': 'src_11711', 'generator_key': 'src_11711', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11711, 'source_order': 11711, 'sampling_weight': 10.0}, {'textbook_example_id': 11712, 'component_id': 'src_11712', 'generator_key': 'src_11712', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_angle_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_angle_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11712, 'source_order': 11712, 'sampling_weight': 10.0}, {'textbook_example_id': 11713, 'component_id': 'src_11713', 'generator_key': 'src_11713', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_cosine_identity_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_cosine_identity_angle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11713, 'source_order': 11713, 'sampling_weight': 10.0}, {'textbook_example_id': 11714, 'component_id': 'src_11714', 'generator_key': 'src_11714', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11714, 'source_order': 11714, 'sampling_weight': 10.0}, {'textbook_example_id': 11715, 'component_id': 'src_11715', 'generator_key': 'src_11715', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_circumradius_from_three_sides', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_circumradius_from_three_sides', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11715, 'source_order': 11715, 'sampling_weight': 10.0}, {'textbook_example_id': 11719, 'component_id': 'src_11719', 'generator_key': 'src_11719', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11719, 'source_order': 11719, 'sampling_weight': 10.0}, {'textbook_example_id': 11727, 'component_id': 'src_11727', 'generator_key': 'src_11727', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11727, 'source_order': 11727, 'sampling_weight': 10.0}]


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
