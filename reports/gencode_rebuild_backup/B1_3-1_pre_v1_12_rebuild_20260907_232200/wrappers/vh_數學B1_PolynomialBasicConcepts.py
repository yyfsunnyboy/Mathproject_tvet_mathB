from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PolynomialBasicConcepts'
GENERATOR_KEYS = ['src_4609', 'src_4610', 'src_4618', 'src_4619', 'src_4620', 'src_4629', 'src_4630', 'src_4631', 'src_4716']
GENERATOR_SPECS = [{'textbook_example_id': 4609, 'component_id': 'src_4609', 'generator_key': 'src_4609', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_descending_power_properties', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_descending_power_properties', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4609, 'source_order': 4609, 'sampling_weight': 10.0}, {'textbook_example_id': 4610, 'component_id': 'src_4610', 'generator_key': 'src_4610', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_param_degree_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_param_degree_constraint', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4610, 'source_order': 4610, 'sampling_weight': 10.0}, {'textbook_example_id': 4618, 'component_id': 'src_4618', 'generator_key': 'src_4618', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_descending_power_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_descending_power_table', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4618, 'source_order': 4618, 'sampling_weight': 10.0}, {'textbook_example_id': 4619, 'component_id': 'src_4619', 'generator_key': 'src_4619', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_param_degree_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_param_degree_constraint', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4619, 'source_order': 4619, 'sampling_weight': 10.0}, {'textbook_example_id': 4620, 'component_id': 'src_4620', 'generator_key': 'src_4620', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'zero_polynomial_find_coeffs', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'zero_polynomial_find_coeffs', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4620, 'source_order': 4620, 'sampling_weight': 10.0}, {'textbook_example_id': 4629, 'component_id': 'src_4629', 'generator_key': 'src_4629', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_descending_power_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_descending_power_table', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4629, 'source_order': 4629, 'sampling_weight': 10.0}, {'textbook_example_id': 4630, 'component_id': 'src_4630', 'generator_key': 'src_4630', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_param_degree_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_param_degree_constraint', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4630, 'source_order': 4630, 'sampling_weight': 10.0}, {'textbook_example_id': 4631, 'component_id': 'src_4631', 'generator_key': 'src_4631', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'zero_polynomial_find_coeffs', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'zero_polynomial_find_coeffs', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4631, 'source_order': 4631, 'sampling_weight': 10.0}, {'textbook_example_id': 4716, 'component_id': 'src_4716', 'generator_key': 'src_4716', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_degree_product_sum', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_degree_product_sum', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4716, 'source_order': 4716, 'sampling_weight': 10.0}]


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
