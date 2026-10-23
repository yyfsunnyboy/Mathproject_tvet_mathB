from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LineSlope'
GENERATOR_KEYS = ['src_12403', 'src_12404', 'src_12436']
GENERATOR_SPECS = [{'textbook_example_id': 12403, 'component_id': 'src_12403', 'generator_key': 'src_12403', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'rank_line_slopes', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rank_line_slopes', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12403, 'source_order': 12403, 'sampling_weight': 10.0}, {'textbook_example_id': 12404, 'component_id': 'src_12404', 'generator_key': 'src_12404', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_slope_sign_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_slope_sign_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12404, 'source_order': 12404, 'sampling_weight': 10.0}, {'textbook_example_id': 12436, 'component_id': 'src_12436', 'generator_key': 'src_12436', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rank_line_slopes', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rank_line_slopes', 'checker_key': 'ordered_inequality_checker', 'equivalence_type': None, 'display_order': 12436, 'source_order': 12436, 'sampling_weight': 10.0}]


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
