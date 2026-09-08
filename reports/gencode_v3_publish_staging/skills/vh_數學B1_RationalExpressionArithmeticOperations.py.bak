from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_RationalExpressionArithmeticOperations'
GENERATOR_KEYS = ['src_4676', 'src_4677', 'src_4686', 'src_4691', 'src_4692', 'src_4702', 'src_4703', 'src_4704']
GENERATOR_SPECS = [{'textbook_example_id': 4676, 'component_id': 'src_4676', 'generator_key': 'src_4676', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4676, 'source_order': 4676, 'sampling_weight': 10.0}, {'textbook_example_id': 4677, 'component_id': 'src_4677', 'generator_key': 'src_4677', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4677, 'source_order': 4677, 'sampling_weight': 10.0}, {'textbook_example_id': 4686, 'component_id': 'src_4686', 'generator_key': 'src_4686', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4686, 'source_order': 4686, 'sampling_weight': 10.0}, {'textbook_example_id': 4691, 'component_id': 'src_4691', 'generator_key': 'src_4691', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4691, 'source_order': 4691, 'sampling_weight': 10.0}, {'textbook_example_id': 4692, 'component_id': 'src_4692', 'generator_key': 'src_4692', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4692, 'source_order': 4692, 'sampling_weight': 10.0}, {'textbook_example_id': 4702, 'component_id': 'src_4702', 'generator_key': 'src_4702', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4702, 'source_order': 4702, 'sampling_weight': 10.0}, {'textbook_example_id': 4703, 'component_id': 'src_4703', 'generator_key': 'src_4703', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4703, 'source_order': 4703, 'sampling_weight': 10.0}, {'textbook_example_id': 4704, 'component_id': 'src_4704', 'generator_key': 'src_4704', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_expression_arithmetic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_expression_arithmetic', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4704, 'source_order': 4704, 'sampling_weight': 10.0}]


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
