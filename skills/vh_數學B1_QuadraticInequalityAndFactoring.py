from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_QuadraticInequalityAndFactoring'
GENERATOR_KEYS = ['src_4473', 'src_4480', 'src_4490']
GENERATOR_SPECS = [{'textbook_example_id': 4473, 'component_id': 'src_4473', 'generator_key': 'src_4473', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_quadratic_by_cross_multiplication', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'integer_factor_quadratic_by_cross_multiplication', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 4473, 'source_order': 4473, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4480, 'component_id': 'src_4480', 'generator_key': 'src_4480', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_quadratic_by_cross_multiplication', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'integer_factor_quadratic_by_cross_multiplication', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 4480, 'source_order': 4480, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4490, 'component_id': 'src_4490', 'generator_key': 'src_4490', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_quadratic_by_cross_multiplication', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'integer_factor_quadratic_by_cross_multiplication', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 4490, 'source_order': 4490, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]


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
