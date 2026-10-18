from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LinearEquationsWithAbsoluteValue'
GENERATOR_KEYS = ['src_1030', 'src_1031', 'src_1032', 'src_1043', 'src_1047', 'src_12327']
GENERATOR_SPECS = [{'textbook_example_id': 1030, 'component_id': 'src_1030', 'generator_key': 'src_1030', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1030, 'source_order': 1030, 'sampling_weight': 10.0}, {'textbook_example_id': 1031, 'component_id': 'src_1031', 'generator_key': 'src_1031', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1031, 'source_order': 1031, 'sampling_weight': 10.0}, {'textbook_example_id': 1032, 'component_id': 'src_1032', 'generator_key': 'src_1032', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 1032, 'source_order': 1032, 'sampling_weight': 10.0}, {'textbook_example_id': 1043, 'component_id': 'src_1043', 'generator_key': 'src_1043', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1043, 'source_order': 1043, 'sampling_weight': 10.0}, {'textbook_example_id': 1047, 'component_id': 'src_1047', 'generator_key': 'src_1047', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 1047, 'source_order': 1047, 'sampling_weight': 10.0}, {'textbook_example_id': 12327, 'component_id': 'src_12327', 'generator_key': 'src_12327', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_equations', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12327, 'source_order': 12327, 'sampling_weight': 10.0}]


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
