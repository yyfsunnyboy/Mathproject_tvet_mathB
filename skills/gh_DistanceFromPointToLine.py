from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_DistanceFromPointToLine'
GENERATOR_KEYS = ['src_12419', 'src_12420', 'src_12421', 'src_12422', 'src_12423', 'src_12424', 'src_12434', 'src_12448']
GENERATOR_SPECS = [{'textbook_example_id': 12419, 'component_id': 'src_12419', 'generator_key': 'src_12419', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_line_distances', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'compute_line_distances', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12419, 'source_order': 12419, 'sampling_weight': 10.0}, {'textbook_example_id': 12420, 'component_id': 'src_12420', 'generator_key': 'src_12420', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_line_distances', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'compute_line_distances', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12420, 'source_order': 12420, 'sampling_weight': 10.0}, {'textbook_example_id': 12421, 'component_id': 'src_12421', 'generator_key': 'src_12421', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_window_decorative_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_window_decorative_lines', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12421, 'source_order': 12421, 'sampling_weight': 10.0}, {'textbook_example_id': 12422, 'component_id': 'src_12422', 'generator_key': 'src_12422', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_line_parameters', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_line_parameters', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12422, 'source_order': 12422, 'sampling_weight': 10.0}, {'textbook_example_id': 12423, 'component_id': 'src_12423', 'generator_key': 'src_12423', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_line_distances', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'compute_line_distances', 'checker_key': 'expression_equivalence_checker', 'equivalence_type': None, 'display_order': 12423, 'source_order': 12423, 'sampling_weight': 10.0}, {'textbook_example_id': 12424, 'component_id': 'src_12424', 'generator_key': 'src_12424', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_window_decorative_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_window_decorative_lines', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12424, 'source_order': 12424, 'sampling_weight': 10.0}, {'textbook_example_id': 12434, 'component_id': 'src_12434', 'generator_key': 'src_12434', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12434, 'source_order': 12434, 'sampling_weight': 10.0}, {'textbook_example_id': 12448, 'component_id': 'src_12448', 'generator_key': 'src_12448', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_parallel_line_family', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parallel_line_family', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12448, 'source_order': 12448, 'sampling_weight': 10.0}]


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
