from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_FundamentalTrigonometricIdentities'
GENERATOR_KEYS = ['src_11562', 'src_11563', 'src_11564', 'src_11565', 'src_11572', 'src_11573', 'src_11574', 'src_11580', 'src_11585', 'src_11586']
GENERATOR_SPECS = [{'textbook_example_id': 11562, 'component_id': 'src_11562', 'generator_key': 'src_11562', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11562, 'source_order': 11562, 'sampling_weight': 1.0}, {'textbook_example_id': 11563, 'component_id': 'src_11563', 'generator_key': 'src_11563', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'complete_cofunction_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'complete_cofunction_identity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11563, 'source_order': 11563, 'sampling_weight': 1.0}, {'textbook_example_id': 11564, 'component_id': 'src_11564', 'generator_key': 'src_11564', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11564, 'source_order': 11564, 'sampling_weight': 1.0}, {'textbook_example_id': 11565, 'component_id': 'src_11565', 'generator_key': 'src_11565', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11565, 'source_order': 11565, 'sampling_weight': 1.0}, {'textbook_example_id': 11572, 'component_id': 'src_11572', 'generator_key': 'src_11572', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11572, 'source_order': 11572, 'sampling_weight': 1.0}, {'textbook_example_id': 11573, 'component_id': 'src_11573', 'generator_key': 'src_11573', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'complete_cofunction_identity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'complete_cofunction_identity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11573, 'source_order': 11573, 'sampling_weight': 1.0}, {'textbook_example_id': 11574, 'component_id': 'src_11574', 'generator_key': 'src_11574', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11574, 'source_order': 11574, 'sampling_weight': 1.0}, {'textbook_example_id': 11580, 'component_id': 'src_11580', 'generator_key': 'src_11580', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11580, 'source_order': 11580, 'sampling_weight': 1.0}, {'textbook_example_id': 11585, 'component_id': 'src_11585', 'generator_key': 'src_11585', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 11585, 'source_order': 11585, 'sampling_weight': 1.0}, {'textbook_example_id': 11586, 'component_id': 'src_11586', 'generator_key': 'src_11586', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11586, 'source_order': 11586, 'sampling_weight': 1.0}]


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
