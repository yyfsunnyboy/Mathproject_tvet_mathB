from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_GeneralFormOfACircle'
GENERATOR_KEYS = ['src_12453', 'src_12454', 'src_12455', 'src_12456', 'src_12457', 'src_12458', 'src_12459', 'src_12460', 'src_12461', 'src_12462', 'src_12463', 'src_12471', 'src_12472', 'src_12475']
GENERATOR_SPECS = [{'textbook_example_id': 12453, 'component_id': 'src_12453', 'generator_key': 'src_12453', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12453, 'source_order': 12453, 'sampling_weight': 10.0}, {'textbook_example_id': 12454, 'component_id': 'src_12454', 'generator_key': 'src_12454', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12454, 'source_order': 12454, 'sampling_weight': 10.0}, {'textbook_example_id': 12455, 'component_id': 'src_12455', 'generator_key': 'src_12455', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12455, 'source_order': 12455, 'sampling_weight': 10.0}, {'textbook_example_id': 12456, 'component_id': 'src_12456', 'generator_key': 'src_12456', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_distance_ratio_locus', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'solve_distance_ratio_locus', 'checker_key': 'equation_checker', 'equivalence_type': None, 'display_order': 12456, 'source_order': 12456, 'sampling_weight': 10.0}, {'textbook_example_id': 12457, 'component_id': 'src_12457', 'generator_key': 'src_12457', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_distance_ratio_locus', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_distance_ratio_locus', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12457, 'source_order': 12457, 'sampling_weight': 10.0}, {'textbook_example_id': 12458, 'component_id': 'src_12458', 'generator_key': 'src_12458', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'analyze_general_circle', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12458, 'source_order': 12458, 'sampling_weight': 10.0}, {'textbook_example_id': 12459, 'component_id': 'src_12459', 'generator_key': 'src_12459', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12459, 'source_order': 12459, 'sampling_weight': 10.0}, {'textbook_example_id': 12460, 'component_id': 'src_12460', 'generator_key': 'src_12460', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12460, 'source_order': 12460, 'sampling_weight': 10.0}, {'textbook_example_id': 12461, 'component_id': 'src_12461', 'generator_key': 'src_12461', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_distance_ratio_locus', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'solve_distance_ratio_locus', 'checker_key': 'equation_checker', 'equivalence_type': None, 'display_order': 12461, 'source_order': 12461, 'sampling_weight': 10.0}, {'textbook_example_id': 12462, 'component_id': 'src_12462', 'generator_key': 'src_12462', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12462, 'source_order': 12462, 'sampling_weight': 10.0}, {'textbook_example_id': 12463, 'component_id': 'src_12463', 'generator_key': 'src_12463', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12463, 'source_order': 12463, 'sampling_weight': 10.0}, {'textbook_example_id': 12471, 'component_id': 'src_12471', 'generator_key': 'src_12471', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12471, 'source_order': 12471, 'sampling_weight': 10.0}, {'textbook_example_id': 12472, 'component_id': 'src_12472', 'generator_key': 'src_12472', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12472, 'source_order': 12472, 'sampling_weight': 10.0}, {'textbook_example_id': 12475, 'component_id': 'src_12475', 'generator_key': 'src_12475', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'analyze_general_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_general_circle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12475, 'source_order': 12475, 'sampling_weight': 10.0}]


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
