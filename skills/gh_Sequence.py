from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_Sequence'
GENERATOR_KEYS = ['src_12667', 'src_12668', 'src_12669', 'src_12670', 'src_12671', 'src_12672', 'src_12673', 'src_12674', 'src_12675', 'src_12676', 'src_12677', 'src_12678', 'src_12679', 'src_12680', 'src_12681', 'src_12682', 'src_12683', 'src_12684', 'src_12685']
GENERATOR_SPECS = [{'textbook_example_id': 12667, 'component_id': 'src_12667', 'generator_key': 'src_12667', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'sequence_terms_from_formula', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sequence_terms_from_formula', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12667, 'source_order': 12667, 'sampling_weight': 10.0}, {'textbook_example_id': 12668, 'component_id': 'src_12668', 'generator_key': 'src_12668', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'figure_path_pattern', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'figure_path_pattern', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12668, 'source_order': 12668, 'sampling_weight': 10.0}, {'textbook_example_id': 12669, 'component_id': 'src_12669', 'generator_key': 'src_12669', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12669, 'source_order': 12669, 'sampling_weight': 10.0}, {'textbook_example_id': 12670, 'component_id': 'src_12670', 'generator_key': 'src_12670', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12670, 'source_order': 12670, 'sampling_weight': 10.0}, {'textbook_example_id': 12671, 'component_id': 'src_12671', 'generator_key': 'src_12671', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12671, 'source_order': 12671, 'sampling_weight': 10.0}, {'textbook_example_id': 12672, 'component_id': 'src_12672', 'generator_key': 'src_12672', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'sequence_terms_from_formula', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sequence_terms_from_formula', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12672, 'source_order': 12672, 'sampling_weight': 10.0}, {'textbook_example_id': 12673, 'component_id': 'src_12673', 'generator_key': 'src_12673', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'finger_counting_cycle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'finger_counting_cycle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12673, 'source_order': 12673, 'sampling_weight': 10.0}, {'textbook_example_id': 12674, 'component_id': 'src_12674', 'generator_key': 'src_12674', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'geometric_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12674, 'source_order': 12674, 'sampling_weight': 10.0}, {'textbook_example_id': 12675, 'component_id': 'src_12675', 'generator_key': 'src_12675', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_from_relations', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12675, 'source_order': 12675, 'sampling_weight': 10.0}, {'textbook_example_id': 12676, 'component_id': 'src_12676', 'generator_key': 'src_12676', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12676, 'source_order': 12676, 'sampling_weight': 10.0}, {'textbook_example_id': 12677, 'component_id': 'src_12677', 'generator_key': 'src_12677', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12677, 'source_order': 12677, 'sampling_weight': 10.0}, {'textbook_example_id': 12678, 'component_id': 'src_12678', 'generator_key': 'src_12678', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12678, 'source_order': 12678, 'sampling_weight': 10.0}, {'textbook_example_id': 12679, 'component_id': 'src_12679', 'generator_key': 'src_12679', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12679, 'source_order': 12679, 'sampling_weight': 10.0}, {'textbook_example_id': 12680, 'component_id': 'src_12680', 'generator_key': 'src_12680', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12680, 'source_order': 12680, 'sampling_weight': 10.0}, {'textbook_example_id': 12681, 'component_id': 'src_12681', 'generator_key': 'src_12681', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'arithmetic_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12681, 'source_order': 12681, 'sampling_weight': 10.0}, {'textbook_example_id': 12682, 'component_id': 'src_12682', 'generator_key': 'src_12682', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12682, 'source_order': 12682, 'sampling_weight': 10.0}, {'textbook_example_id': 12683, 'component_id': 'src_12683', 'generator_key': 'src_12683', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12683, 'source_order': 12683, 'sampling_weight': 10.0}, {'textbook_example_id': 12684, 'component_id': 'src_12684', 'generator_key': 'src_12684', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12684, 'source_order': 12684, 'sampling_weight': 10.0}, {'textbook_example_id': 12685, 'component_id': 'src_12685', 'generator_key': 'src_12685', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12685, 'source_order': 12685, 'sampling_weight': 10.0}]


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
