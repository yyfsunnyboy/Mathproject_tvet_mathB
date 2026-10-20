from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PositiveIntegerExponentsAndLaws'
GENERATOR_KEYS = ['src_12339', 'src_12340', 'src_12341', 'src_12342']
GENERATOR_SPECS = [{'textbook_example_id': 12339, 'component_id': 'src_12339', 'generator_key': 'src_12339', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_exponent_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_exponent_expressions', 'checker_key': None, 'equivalence_type': None, 'display_order': 12339, 'source_order': 12339, 'sampling_weight': 1.0}, {'textbook_example_id': 12340, 'component_id': 'src_12340', 'generator_key': 'src_12340', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_repeated_folding', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_repeated_folding', 'checker_key': None, 'equivalence_type': None, 'display_order': 12340, 'source_order': 12340, 'sampling_weight': 1.0}, {'textbook_example_id': 12341, 'component_id': 'src_12341', 'generator_key': 'src_12341', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_exponent_blank_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_exponent_blank_equations', 'checker_key': None, 'equivalence_type': None, 'display_order': 12341, 'source_order': 12341, 'sampling_weight': 1.0}, {'textbook_example_id': 12342, 'component_id': 'src_12342', 'generator_key': 'src_12342', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'select_nearest_model_value', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'select_nearest_model_value', 'checker_key': None, 'equivalence_type': None, 'display_order': 12342, 'source_order': 12342, 'sampling_weight': 1.0}]


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
