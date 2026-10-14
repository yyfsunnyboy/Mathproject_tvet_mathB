from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PolynomialArithmeticOperations'
GENERATOR_KEYS = ['src_4612', 'src_4613', 'src_4614', 'src_4615', 'src_4616', 'src_4617', 'src_4622', 'src_4623', 'src_4624', 'src_4625', 'src_4626', 'src_4627', 'src_4633', 'src_4634', 'src_4635', 'src_4636', 'src_4637', 'src_4706']
GENERATOR_SPECS = [{'textbook_example_id': 4612, 'component_id': 'src_4612', 'generator_key': 'src_4612', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4612, 'source_order': 4612, 'sampling_weight': 10.0}, {'textbook_example_id': 4613, 'component_id': 'src_4613', 'generator_key': 'src_4613', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4613, 'source_order': 4613, 'sampling_weight': 10.0}, {'textbook_example_id': 4614, 'component_id': 'src_4614', 'generator_key': 'src_4614', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4614, 'source_order': 4614, 'sampling_weight': 10.0}, {'textbook_example_id': 4615, 'component_id': 'src_4615', 'generator_key': 'src_4615', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4615, 'source_order': 4615, 'sampling_weight': 10.0}, {'textbook_example_id': 4616, 'component_id': 'src_4616', 'generator_key': 'src_4616', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4616, 'source_order': 4616, 'sampling_weight': 10.0}, {'textbook_example_id': 4617, 'component_id': 'src_4617', 'generator_key': 'src_4617', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_shifted_basis_eval', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_shifted_basis_eval', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4617, 'source_order': 4617, 'sampling_weight': 10.0}, {'textbook_example_id': 4622, 'component_id': 'src_4622', 'generator_key': 'src_4622', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4622, 'source_order': 4622, 'sampling_weight': 10.0}, {'textbook_example_id': 4623, 'component_id': 'src_4623', 'generator_key': 'src_4623', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_multiply', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_multiply', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4623, 'source_order': 4623, 'sampling_weight': 10.0}, {'textbook_example_id': 4624, 'component_id': 'src_4624', 'generator_key': 'src_4624', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4624, 'source_order': 4624, 'sampling_weight': 10.0}, {'textbook_example_id': 4625, 'component_id': 'src_4625', 'generator_key': 'src_4625', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4625, 'source_order': 4625, 'sampling_weight': 10.0}, {'textbook_example_id': 4626, 'component_id': 'src_4626', 'generator_key': 'src_4626', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4626, 'source_order': 4626, 'sampling_weight': 10.0}, {'textbook_example_id': 4627, 'component_id': 'src_4627', 'generator_key': 'src_4627', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_remainder_param_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_remainder_param_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4627, 'source_order': 4627, 'sampling_weight': 10.0}, {'textbook_example_id': 4633, 'component_id': 'src_4633', 'generator_key': 'src_4633', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4633, 'source_order': 4633, 'sampling_weight': 10.0}, {'textbook_example_id': 4634, 'component_id': 'src_4634', 'generator_key': 'src_4634', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_multiply', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_multiply', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4634, 'source_order': 4634, 'sampling_weight': 10.0}, {'textbook_example_id': 4635, 'component_id': 'src_4635', 'generator_key': 'src_4635', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4635, 'source_order': 4635, 'sampling_weight': 10.0}, {'textbook_example_id': 4636, 'component_id': 'src_4636', 'generator_key': 'src_4636', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4636, 'source_order': 4636, 'sampling_weight': 10.0}, {'textbook_example_id': 4637, 'component_id': 'src_4637', 'generator_key': 'src_4637', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4637, 'source_order': 4637, 'sampling_weight': 10.0}, {'textbook_example_id': 4706, 'component_id': 'src_4706', 'generator_key': 'src_4706', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4706, 'source_order': 4706, 'sampling_weight': 10.0}]


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
