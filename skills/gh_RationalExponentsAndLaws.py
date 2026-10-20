from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RationalExponentsAndLaws'
GENERATOR_KEYS = ['src_12351', 'src_12352', 'src_12353', 'src_12354', 'src_12355', 'src_12356', 'src_12357', 'src_12358', 'src_12359', 'src_12360', 'src_12361', 'src_12362', 'src_12363', 'src_12364', 'src_12365', 'src_12366']
GENERATOR_SPECS = [{'textbook_example_id': 12351, 'component_id': 'src_12351', 'generator_key': 'src_12351', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'express_rational_powers_as_radicals', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_rational_powers_as_radicals', 'checker_key': None, 'equivalence_type': None, 'display_order': 12351, 'source_order': 12351, 'sampling_weight': 1.0}, {'textbook_example_id': 12352, 'component_id': 'src_12352', 'generator_key': 'src_12352', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12352, 'source_order': 12352, 'sampling_weight': 1.0}, {'textbook_example_id': 12353, 'component_id': 'src_12353', 'generator_key': 'src_12353', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12353, 'source_order': 12353, 'sampling_weight': 1.0}, {'textbook_example_id': 12354, 'component_id': 'src_12354', 'generator_key': 'src_12354', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_metabolic_scaling', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_metabolic_scaling', 'checker_key': None, 'equivalence_type': None, 'display_order': 12354, 'source_order': 12354, 'sampling_weight': 1.0}, {'textbook_example_id': 12355, 'component_id': 'src_12355', 'generator_key': 'src_12355', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'express_rational_powers_as_radicals', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_rational_powers_as_radicals', 'checker_key': None, 'equivalence_type': None, 'display_order': 12355, 'source_order': 12355, 'sampling_weight': 1.0}, {'textbook_example_id': 12356, 'component_id': 'src_12356', 'generator_key': 'src_12356', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12356, 'source_order': 12356, 'sampling_weight': 1.0}, {'textbook_example_id': 12357, 'component_id': 'src_12357', 'generator_key': 'src_12357', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12357, 'source_order': 12357, 'sampling_weight': 1.0}, {'textbook_example_id': 12358, 'component_id': 'src_12358', 'generator_key': 'src_12358', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_half_life_model', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_half_life_model', 'checker_key': None, 'equivalence_type': None, 'display_order': 12358, 'source_order': 12358, 'sampling_weight': 1.0}, {'textbook_example_id': 12359, 'component_id': 'src_12359', 'generator_key': 'src_12359', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12359, 'source_order': 12359, 'sampling_weight': 1.0}, {'textbook_example_id': 12360, 'component_id': 'src_12360', 'generator_key': 'src_12360', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12360, 'source_order': 12360, 'sampling_weight': 1.0}, {'textbook_example_id': 12361, 'component_id': 'src_12361', 'generator_key': 'src_12361', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12361, 'source_order': 12361, 'sampling_weight': 1.0}, {'textbook_example_id': 12362, 'component_id': 'src_12362', 'generator_key': 'src_12362', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12362, 'source_order': 12362, 'sampling_weight': 1.0}, {'textbook_example_id': 12363, 'component_id': 'src_12363', 'generator_key': 'src_12363', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12363, 'source_order': 12363, 'sampling_weight': 1.0}, {'textbook_example_id': 12364, 'component_id': 'src_12364', 'generator_key': 'src_12364', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12364, 'source_order': 12364, 'sampling_weight': 1.0}, {'textbook_example_id': 12365, 'component_id': 'src_12365', 'generator_key': 'src_12365', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12365, 'source_order': 12365, 'sampling_weight': 1.0}, {'textbook_example_id': 12366, 'component_id': 'src_12366', 'generator_key': 'src_12366', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_scale_energy_ratio', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scale_energy_ratio', 'checker_key': None, 'equivalence_type': None, 'display_order': 12366, 'source_order': 12366, 'sampling_weight': 1.0}]


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
