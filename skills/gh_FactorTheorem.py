from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_FactorTheorem'
GENERATOR_KEYS = ['src_12519', 'src_12550', 'src_12551', 'src_12552', 'src_12553', 'src_12554', 'src_12555', 'src_12556', 'src_12557', 'src_12558', 'src_12559']
GENERATOR_SPECS = [{'textbook_example_id': 12519, 'component_id': 'src_12519', 'generator_key': 'src_12519', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12519, 'source_order': 12519, 'sampling_weight': 10.0}, {'textbook_example_id': 12550, 'component_id': 'src_12550', 'generator_key': 'src_12550', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'select_linear_factors', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'select_linear_factors', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12550, 'source_order': 12550, 'sampling_weight': 10.0}, {'textbook_example_id': 12551, 'component_id': 'src_12551', 'generator_key': 'src_12551', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'interpolate_polynomials', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interpolate_polynomials', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12551, 'source_order': 12551, 'sampling_weight': 10.0}, {'textbook_example_id': 12552, 'component_id': 'src_12552', 'generator_key': 'src_12552', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_erased_cubic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_erased_cubic', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12552, 'source_order': 12552, 'sampling_weight': 10.0}, {'textbook_example_id': 12553, 'component_id': 'src_12553', 'generator_key': 'src_12553', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12553, 'source_order': 12553, 'sampling_weight': 10.0}, {'textbook_example_id': 12554, 'component_id': 'src_12554', 'generator_key': 'src_12554', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'interpolate_polynomials', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interpolate_polynomials', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12554, 'source_order': 12554, 'sampling_weight': 10.0}, {'textbook_example_id': 12555, 'component_id': 'src_12555', 'generator_key': 'src_12555', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_masked_synthetic_coefficient', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_masked_synthetic_coefficient', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12555, 'source_order': 12555, 'sampling_weight': 10.0}, {'textbook_example_id': 12556, 'component_id': 'src_12556', 'generator_key': 'src_12556', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12556, 'source_order': 12556, 'sampling_weight': 10.0}, {'textbook_example_id': 12557, 'component_id': 'src_12557', 'generator_key': 'src_12557', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12557, 'source_order': 12557, 'sampling_weight': 10.0}, {'textbook_example_id': 12558, 'component_id': 'src_12558', 'generator_key': 'src_12558', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12558, 'source_order': 12558, 'sampling_weight': 10.0}, {'textbook_example_id': 12559, 'component_id': 'src_12559', 'generator_key': 'src_12559', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'interpolate_polynomials', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interpolate_polynomials', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12559, 'source_order': 12559, 'sampling_weight': 10.0}]


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
