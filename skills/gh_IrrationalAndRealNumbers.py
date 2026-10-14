from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_IrrationalAndRealNumbers'
GENERATOR_KEYS = ['src_12283', 'src_12284', 'src_12285']
GENERATOR_SPECS = [{'textbook_example_id': 12283, 'component_id': 'src_12283', 'generator_key': 'src_12283', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_rational_unknowns_from_radical_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_rational_unknowns_from_radical_identity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12283, 'source_order': 12283, 'sampling_weight': 10.0}, {'textbook_example_id': 12284, 'component_id': 'src_12284', 'generator_key': 'src_12284', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_rational_unknowns_from_radical_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_rational_unknowns_from_radical_identity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12284, 'source_order': 12284, 'sampling_weight': 10.0}, {'textbook_example_id': 12285, 'component_id': 'src_12285', 'generator_key': 'src_12285', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'approximate_square_root_by_decimal_search', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'approximate_square_root_by_decimal_search', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12285, 'source_order': 12285, 'sampling_weight': 10.0}]


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
