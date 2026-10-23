from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_ArithmeticOperationsOfPolynomials'
GENERATOR_KEYS = ['src_12520', 'src_12521', 'src_12522', 'src_12523', 'src_12524', 'src_12526', 'src_12527', 'src_12528', 'src_12529', 'src_12530', 'src_12531', 'src_12532', 'src_12533', 'src_12534', 'src_12535', 'src_12537']
GENERATOR_SPECS = [{'textbook_example_id': 12520, 'component_id': 'src_12520', 'generator_key': 'src_12520', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12520, 'source_order': 12520, 'sampling_weight': 10.0}, {'textbook_example_id': 12521, 'component_id': 'src_12521', 'generator_key': 'src_12521', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12521, 'source_order': 12521, 'sampling_weight': 10.0}, {'textbook_example_id': 12522, 'component_id': 'src_12522', 'generator_key': 'src_12522', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12522, 'source_order': 12522, 'sampling_weight': 10.0}, {'textbook_example_id': 12523, 'component_id': 'src_12523', 'generator_key': 'src_12523', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12523, 'source_order': 12523, 'sampling_weight': 10.0}, {'textbook_example_id': 12524, 'component_id': 'src_12524', 'generator_key': 'src_12524', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12524, 'source_order': 12524, 'sampling_weight': 10.0}, {'textbook_example_id': 12526, 'component_id': 'src_12526', 'generator_key': 'src_12526', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12526, 'source_order': 12526, 'sampling_weight': 10.0}, {'textbook_example_id': 12527, 'component_id': 'src_12527', 'generator_key': 'src_12527', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12527, 'source_order': 12527, 'sampling_weight': 10.0}, {'textbook_example_id': 12528, 'component_id': 'src_12528', 'generator_key': 'src_12528', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12528, 'source_order': 12528, 'sampling_weight': 10.0}, {'textbook_example_id': 12529, 'component_id': 'src_12529', 'generator_key': 'src_12529', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12529, 'source_order': 12529, 'sampling_weight': 10.0}, {'textbook_example_id': 12530, 'component_id': 'src_12530', 'generator_key': 'src_12530', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12530, 'source_order': 12530, 'sampling_weight': 10.0}, {'textbook_example_id': 12531, 'component_id': 'src_12531', 'generator_key': 'src_12531', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12531, 'source_order': 12531, 'sampling_weight': 10.0}, {'textbook_example_id': 12532, 'component_id': 'src_12532', 'generator_key': 'src_12532', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12532, 'source_order': 12532, 'sampling_weight': 10.0}, {'textbook_example_id': 12533, 'component_id': 'src_12533', 'generator_key': 'src_12533', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12533, 'source_order': 12533, 'sampling_weight': 10.0}, {'textbook_example_id': 12534, 'component_id': 'src_12534', 'generator_key': 'src_12534', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12534, 'source_order': 12534, 'sampling_weight': 10.0}, {'textbook_example_id': 12535, 'component_id': 'src_12535', 'generator_key': 'src_12535', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_divisor_from_quotient_remainder', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_divisor_from_quotient_remainder', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12535, 'source_order': 12535, 'sampling_weight': 10.0}, {'textbook_example_id': 12537, 'component_id': 'src_12537', 'generator_key': 'src_12537', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12537, 'source_order': 12537, 'sampling_weight': 10.0}]


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
