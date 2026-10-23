from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_ParallelAndPerpendicularLines'
GENERATOR_KEYS = ['src_12413', 'src_12414', 'src_12415', 'src_12416', 'src_12417', 'src_12418', 'src_12431', 'src_12433', 'src_12439', 'src_12440', 'src_12444', 'src_12446']
GENERATOR_SPECS = [{'textbook_example_id': 12413, 'component_id': 'src_12413', 'generator_key': 'src_12413', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12413, 'source_order': 12413, 'sampling_weight': 10.0}, {'textbook_example_id': 12414, 'component_id': 'src_12414', 'generator_key': 'src_12414', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_constructions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12414, 'source_order': 12414, 'sampling_weight': 10.0}, {'textbook_example_id': 12415, 'component_id': 'src_12415', 'generator_key': 'src_12415', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_line_constructions', 'answer_type': 'coordinate_pair', 'answer_value_type': 'coordinate_pair', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': None, 'display_order': 12415, 'source_order': 12415, 'sampling_weight': 10.0}, {'textbook_example_id': 12416, 'component_id': 'src_12416', 'generator_key': 'src_12416', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_line_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12416, 'source_order': 12416, 'sampling_weight': 10.0}, {'textbook_example_id': 12417, 'component_id': 'src_12417', 'generator_key': 'src_12417', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_line_constructions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12417, 'source_order': 12417, 'sampling_weight': 10.0}, {'textbook_example_id': 12418, 'component_id': 'src_12418', 'generator_key': 'src_12418', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_line_constructions', 'answer_type': 'coordinate_pair', 'answer_value_type': 'coordinate_pair', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': None, 'display_order': 12418, 'source_order': 12418, 'sampling_weight': 10.0}, {'textbook_example_id': 12431, 'component_id': 'src_12431', 'generator_key': 'src_12431', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12431, 'source_order': 12431, 'sampling_weight': 10.0}, {'textbook_example_id': 12433, 'component_id': 'src_12433', 'generator_key': 'src_12433', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12433, 'source_order': 12433, 'sampling_weight': 10.0}, {'textbook_example_id': 12439, 'component_id': 'src_12439', 'generator_key': 'src_12439', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_line_parameters', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_line_parameters', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12439, 'source_order': 12439, 'sampling_weight': 10.0}, {'textbook_example_id': 12440, 'component_id': 'src_12440', 'generator_key': 'src_12440', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_constructions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12440, 'source_order': 12440, 'sampling_weight': 10.0}, {'textbook_example_id': 12444, 'component_id': 'src_12444', 'generator_key': 'src_12444', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_rectangle_perpendicular_diagonals', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'solve_rectangle_perpendicular_diagonals', 'checker_key': 'expression_equivalence_checker', 'equivalence_type': None, 'display_order': 12444, 'source_order': 12444, 'sampling_weight': 10.0}, {'textbook_example_id': 12446, 'component_id': 'src_12446', 'generator_key': 'src_12446', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_constructions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_constructions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12446, 'source_order': 12446, 'sampling_weight': 10.0}]


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
