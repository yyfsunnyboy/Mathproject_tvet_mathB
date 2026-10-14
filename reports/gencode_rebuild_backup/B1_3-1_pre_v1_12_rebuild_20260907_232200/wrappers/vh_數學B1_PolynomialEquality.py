from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PolynomialEquality'
GENERATOR_KEYS = ['src_4611', 'src_4621', 'src_4632', 'src_4717']
GENERATOR_SPECS = [{'textbook_example_id': 4611, 'component_id': 'src_4611', 'generator_key': 'src_4611', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_equality_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_equality_identity', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4611, 'source_order': 4611, 'sampling_weight': 10.0}, {'textbook_example_id': 4621, 'component_id': 'src_4621', 'generator_key': 'src_4621', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_equality_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_equality_identity', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4621, 'source_order': 4621, 'sampling_weight': 10.0}, {'textbook_example_id': 4632, 'component_id': 'src_4632', 'generator_key': 'src_4632', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_equality_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_equality_identity', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4632, 'source_order': 4632, 'sampling_weight': 10.0}, {'textbook_example_id': 4717, 'component_id': 'src_4717', 'generator_key': 'src_4717', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_equality_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_equality_identity', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4717, 'source_order': 4717, 'sampling_weight': 10.0}]


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
