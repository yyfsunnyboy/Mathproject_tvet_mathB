from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_TrigonometricFunctionsOfAcuteAngles'
GENERATOR_KEYS = ['src_11557', 'src_11558', 'src_11567', 'src_11568', 'src_11576', 'src_11577', 'src_11579', 'src_11581', 'src_11582', 'src_11583']
GENERATOR_SPECS = [{'textbook_example_id': 11557, 'component_id': 'src_11557', 'generator_key': 'src_11557', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'compute_right_triangle_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_right_triangle_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11557, 'source_order': 11557, 'sampling_weight': 1.0}, {'textbook_example_id': 11558, 'component_id': 'src_11558', 'generator_key': 'src_11558', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11558, 'source_order': 11558, 'sampling_weight': 1.0}, {'textbook_example_id': 11567, 'component_id': 'src_11567', 'generator_key': 'src_11567', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compute_right_triangle_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_right_triangle_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11567, 'source_order': 11567, 'sampling_weight': 1.0}, {'textbook_example_id': 11568, 'component_id': 'src_11568', 'generator_key': 'src_11568', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11568, 'source_order': 11568, 'sampling_weight': 1.0}, {'textbook_example_id': 11576, 'component_id': 'src_11576', 'generator_key': 'src_11576', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compute_right_triangle_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_right_triangle_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11576, 'source_order': 11576, 'sampling_weight': 1.0}, {'textbook_example_id': 11577, 'component_id': 'src_11577', 'generator_key': 'src_11577', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11577, 'source_order': 11577, 'sampling_weight': 1.0}, {'textbook_example_id': 11579, 'component_id': 'src_11579', 'generator_key': 'src_11579', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11579, 'source_order': 11579, 'sampling_weight': 1.0}, {'textbook_example_id': 11581, 'component_id': 'src_11581', 'generator_key': 'src_11581', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11581, 'source_order': 11581, 'sampling_weight': 1.0}, {'textbook_example_id': 11582, 'component_id': 'src_11582', 'generator_key': 'src_11582', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_acute_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_acute_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11582, 'source_order': 11582, 'sampling_weight': 1.0}, {'textbook_example_id': 11583, 'component_id': 'src_11583', 'generator_key': 'src_11583', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compute_chord_and_arc_length', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_chord_and_arc_length', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11583, 'source_order': 11583, 'sampling_weight': 1.0}]


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
