from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PointAndCircleRelationship'
GENERATOR_KEYS = ['src_12464', 'src_12465', 'src_12466', 'src_12467', 'src_12468', 'src_12469', 'src_12473', 'src_12477', 'src_12478']
GENERATOR_SPECS = [{'textbook_example_id': 12464, 'component_id': 'src_12464', 'generator_key': 'src_12464', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'classify_points_against_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_points_against_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12464, 'source_order': 12464, 'sampling_weight': 10.0}, {'textbook_example_id': 12465, 'component_id': 'src_12465', 'generator_key': 'src_12465', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_point_distances', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_point_distances', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12465, 'source_order': 12465, 'sampling_weight': 10.0}, {'textbook_example_id': 12466, 'component_id': 'src_12466', 'generator_key': 'src_12466', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_mohr_circles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_mohr_circles', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12466, 'source_order': 12466, 'sampling_weight': 10.0}, {'textbook_example_id': 12467, 'component_id': 'src_12467', 'generator_key': 'src_12467', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_point_position_parameter_range', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_point_position_parameter_range', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12467, 'source_order': 12467, 'sampling_weight': 10.0}, {'textbook_example_id': 12468, 'component_id': 'src_12468', 'generator_key': 'src_12468', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_circle_point_distances', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_point_distances', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12468, 'source_order': 12468, 'sampling_weight': 10.0}, {'textbook_example_id': 12469, 'component_id': 'src_12469', 'generator_key': 'src_12469', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12469, 'source_order': 12469, 'sampling_weight': 10.0}, {'textbook_example_id': 12473, 'component_id': 'src_12473', 'generator_key': 'src_12473', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12473, 'source_order': 12473, 'sampling_weight': 10.0}, {'textbook_example_id': 12477, 'component_id': 'src_12477', 'generator_key': 'src_12477', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_point_distances', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_point_distances', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12477, 'source_order': 12477, 'sampling_weight': 10.0}, {'textbook_example_id': 12478, 'component_id': 'src_12478', 'generator_key': 'src_12478', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'solve_storm_entry_time', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'solve_storm_entry_time', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12478, 'source_order': 12478, 'sampling_weight': 10.0}]


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
