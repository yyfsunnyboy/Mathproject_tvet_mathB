from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_AbsoluteValueInequality'
GENERATOR_KEYS = ['src_4400', 'src_4402', 'src_4403', 'src_4404', 'src_4405', 'src_4406', 'src_4407', 'src_4409', 'src_4413', 'src_4499']
GENERATOR_SPECS = [{'textbook_example_id': 4400, 'component_id': 'src_4400', 'generator_key': 'src_4400', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_zero_center_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_zero_center_basic', 'display_order': 4400, 'source_order': 4400, 'sampling_weight': 10.0}, {'textbook_example_id': 4402, 'component_id': 'src_4402', 'generator_key': 'src_4402', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_shifted_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_shifted_basic', 'display_order': 4402, 'source_order': 4402, 'sampling_weight': 10.0}, {'textbook_example_id': 4403, 'component_id': 'src_4403', 'generator_key': 'src_4403', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_shifted_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_shifted_basic', 'display_order': 4403, 'source_order': 4403, 'sampling_weight': 10.0}, {'textbook_example_id': 4404, 'component_id': 'src_4404', 'generator_key': 'src_4404', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4404, 'source_order': 4404, 'sampling_weight': 10.0}, {'textbook_example_id': 4405, 'component_id': 'src_4405', 'generator_key': 'src_4405', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4405, 'source_order': 4405, 'sampling_weight': 10.0}, {'textbook_example_id': 4406, 'component_id': 'src_4406', 'generator_key': 'src_4406', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4406, 'source_order': 4406, 'sampling_weight': 10.0}, {'textbook_example_id': 4407, 'component_id': 'src_4407', 'generator_key': 'src_4407', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_linear_expression_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'display_order': 4407, 'source_order': 4407, 'sampling_weight': 10.0}, {'textbook_example_id': 4409, 'component_id': 'src_4409', 'generator_key': 'src_4409', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'absolute_value_inequality_zero_center_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_zero_center_basic', 'display_order': 4409, 'source_order': 4409, 'sampling_weight': 10.0}, {'textbook_example_id': 4413, 'component_id': 'src_4413', 'generator_key': 'src_4413', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'absolute_value_inequality_zero_center_basic', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'absolute_value_inequality_zero_center_basic', 'display_order': 4413, 'source_order': 4413, 'sampling_weight': 10.0}, {'textbook_example_id': 4499, 'component_id': 'src_4499', 'generator_key': 'src_4499', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'absolute_value_inequality_integer_solution_count_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'absolute_value_inequality_integer_solution_count_choice', 'display_order': 4499, 'source_order': 4499, 'sampling_weight': 10.0}]


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
