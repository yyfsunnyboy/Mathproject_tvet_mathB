from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_6'
GENERATOR_KEYS = ['src_11636', 'src_11637', 'src_11638', 'src_11639', 'src_11650', 'src_11654']
GENERATOR_SPECS = [{'textbook_example_id': 11636, 'component_id': 'src_11636', 'generator_key': 'src_11636', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11636, 'source_order': 11636, 'sampling_weight': 1.0}, {'textbook_example_id': 11637, 'component_id': 'src_11637', 'generator_key': 'src_11637', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11637, 'source_order': 11637, 'sampling_weight': 1.0}, {'textbook_example_id': 11638, 'component_id': 'src_11638', 'generator_key': 'src_11638', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11638, 'source_order': 11638, 'sampling_weight': 1.0}, {'textbook_example_id': 11639, 'component_id': 'src_11639', 'generator_key': 'src_11639', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11639, 'source_order': 11639, 'sampling_weight': 1.0}, {'textbook_example_id': 11650, 'component_id': 'src_11650', 'generator_key': 'src_11650', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11650, 'source_order': 11650, 'sampling_weight': 1.0}, {'textbook_example_id': 11654, 'component_id': 'src_11654', 'generator_key': 'src_11654', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'solve_arbitrary_angle_vertical_projection', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_arbitrary_angle_vertical_projection', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11654, 'source_order': 11654, 'sampling_weight': 1.0}]


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
