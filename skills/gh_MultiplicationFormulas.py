from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_MultiplicationFormulas'
GENERATOR_KEYS = ['src_12286', 'src_12287', 'src_12288', 'src_12289', 'src_12290', 'src_12291', 'src_12292', 'src_12293', 'src_12294', 'src_12295', 'src_12296', 'src_12297', 'src_12298', 'src_12299', 'src_12300', 'src_12301']
GENERATOR_SPECS = [{'textbook_example_id': 12286, 'component_id': 'src_12286', 'generator_key': 'src_12286', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12286, 'source_order': 12286, 'sampling_weight': 10.0}, {'textbook_example_id': 12287, 'component_id': 'src_12287', 'generator_key': 'src_12287', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12287, 'source_order': 12287, 'sampling_weight': 10.0}, {'textbook_example_id': 12288, 'component_id': 'src_12288', 'generator_key': 'src_12288', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12288, 'source_order': 12288, 'sampling_weight': 10.0}, {'textbook_example_id': 12289, 'component_id': 'src_12289', 'generator_key': 'src_12289', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'factor_by_cube_formulas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_by_cube_formulas', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12289, 'source_order': 12289, 'sampling_weight': 10.0}, {'textbook_example_id': 12290, 'component_id': 'src_12290', 'generator_key': 'src_12290', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_reciprocal_power_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12290, 'source_order': 12290, 'sampling_weight': 10.0}, {'textbook_example_id': 12291, 'component_id': 'src_12291', 'generator_key': 'src_12291', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_radical_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_radical_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12291, 'source_order': 12291, 'sampling_weight': 10.0}, {'textbook_example_id': 12292, 'component_id': 'src_12292', 'generator_key': 'src_12292', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12292, 'source_order': 12292, 'sampling_weight': 10.0}, {'textbook_example_id': 12293, 'component_id': 'src_12293', 'generator_key': 'src_12293', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12293, 'source_order': 12293, 'sampling_weight': 10.0}, {'textbook_example_id': 12294, 'component_id': 'src_12294', 'generator_key': 'src_12294', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12294, 'source_order': 12294, 'sampling_weight': 10.0}, {'textbook_example_id': 12295, 'component_id': 'src_12295', 'generator_key': 'src_12295', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'factor_by_cube_formulas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_by_cube_formulas', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12295, 'source_order': 12295, 'sampling_weight': 10.0}, {'textbook_example_id': 12296, 'component_id': 'src_12296', 'generator_key': 'src_12296', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_reciprocal_power_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12296, 'source_order': 12296, 'sampling_weight': 10.0}, {'textbook_example_id': 12297, 'component_id': 'src_12297', 'generator_key': 'src_12297', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_rational_unknowns_from_squared_radical_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_rational_unknowns_from_squared_radical_identity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12297, 'source_order': 12297, 'sampling_weight': 10.0}, {'textbook_example_id': 12298, 'component_id': 'src_12298', 'generator_key': 'src_12298', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'expand_polynomial_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'expand_polynomial_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12298, 'source_order': 12298, 'sampling_weight': 10.0}, {'textbook_example_id': 12299, 'component_id': 'src_12299', 'generator_key': 'src_12299', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'factor_by_cube_formulas', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_by_cube_formulas', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12299, 'source_order': 12299, 'sampling_weight': 10.0}, {'textbook_example_id': 12300, 'component_id': 'src_12300', 'generator_key': 'src_12300', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_reciprocal_power_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_reciprocal_power_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12300, 'source_order': 12300, 'sampling_weight': 10.0}, {'textbook_example_id': 12301, 'component_id': 'src_12301', 'generator_key': 'src_12301', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_product_under_power_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_product_under_power_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12301, 'source_order': 12301, 'sampling_weight': 10.0}]


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
