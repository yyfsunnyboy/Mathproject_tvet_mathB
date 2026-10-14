from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RationalNumbers'
GENERATOR_KEYS = ['src_12273', 'src_12274', 'src_12275', 'src_12276', 'src_12278', 'src_12279', 'src_12280', 'src_12281', 'src_12282']
GENERATOR_SPECS = [{'textbook_example_id': 12273, 'component_id': 'src_12273', 'generator_key': 'src_12273', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'fraction_to_decimal_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'fraction_to_decimal_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12273, 'source_order': 12273, 'sampling_weight': 10.0}, {'textbook_example_id': 12274, 'component_id': 'src_12274', 'generator_key': 'src_12274', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'decimal_to_simplest_fraction', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'decimal_to_simplest_fraction', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12274, 'source_order': 12274, 'sampling_weight': 10.0}, {'textbook_example_id': 12275, 'component_id': 'src_12275', 'generator_key': 'src_12275', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'fraction_to_decimal_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'fraction_to_decimal_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12275, 'source_order': 12275, 'sampling_weight': 10.0}, {'textbook_example_id': 12276, 'component_id': 'src_12276', 'generator_key': 'src_12276', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'decimal_to_simplest_fraction', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'decimal_to_simplest_fraction', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12276, 'source_order': 12276, 'sampling_weight': 10.0}, {'textbook_example_id': 12278, 'component_id': 'src_12278', 'generator_key': 'src_12278', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'construct_rational_between_bounds', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'construct_rational_between_bounds', 'checker_key': 'rational_between_bounds_checker', 'equivalence_type': None, 'display_order': 12278, 'source_order': 12278, 'sampling_weight': 10.0}, {'textbook_example_id': 12279, 'component_id': 'src_12279', 'generator_key': 'src_12279', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_rationality_statements', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_rationality_statements', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12279, 'source_order': 12279, 'sampling_weight': 10.0}, {'textbook_example_id': 12280, 'component_id': 'src_12280', 'generator_key': 'src_12280', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_rational_numbers', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_rational_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12280, 'source_order': 12280, 'sampling_weight': 10.0}, {'textbook_example_id': 12281, 'component_id': 'src_12281', 'generator_key': 'src_12281', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'fraction_to_decimal_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'fraction_to_decimal_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12281, 'source_order': 12281, 'sampling_weight': 10.0}, {'textbook_example_id': 12282, 'component_id': 'src_12282', 'generator_key': 'src_12282', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'decimal_to_simplest_fraction', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'decimal_to_simplest_fraction', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12282, 'source_order': 12282, 'sampling_weight': 10.0}]


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
