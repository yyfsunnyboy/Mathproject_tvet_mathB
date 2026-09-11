from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_4_3'
GENERATOR_KEYS = ['src_11655', 'src_11656', 'src_11657', 'src_11658', 'src_11659', 'src_11660', 'src_11661', 'src_11662']
GENERATOR_SPECS = [{'textbook_example_id': 11655, 'component_id': 'src_11655', 'generator_key': 'src_11655', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'compare_trig_values_by_monotonicity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_trig_values_by_monotonicity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 1, 'source_order': 1, 'sampling_weight': 1.0}, {'textbook_example_id': 11656, 'component_id': 'src_11656', 'generator_key': 'src_11656', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compare_trig_values_by_monotonicity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_trig_values_by_monotonicity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 2, 'source_order': 2, 'sampling_weight': 1.0}, {'textbook_example_id': 11657, 'component_id': 'src_11657', 'generator_key': 'src_11657', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_trig_value_quadratic_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_trig_value_quadratic_constraint', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 3, 'source_order': 3, 'sampling_weight': 1.0}, {'textbook_example_id': 11658, 'component_id': 'src_11658', 'generator_key': 'src_11658', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'solve_trig_value_quadratic_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_trig_value_quadratic_constraint', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 4, 'source_order': 4, 'sampling_weight': 1.0}, {'textbook_example_id': 11659, 'component_id': 'src_11659', 'generator_key': 'src_11659', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 5, 'source_order': 5, 'sampling_weight': 1.0}, {'textbook_example_id': 11660, 'component_id': 'src_11660', 'generator_key': 'src_11660', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 6, 'source_order': 6, 'sampling_weight': 1.0}, {'textbook_example_id': 11661, 'component_id': 'src_11661', 'generator_key': 'src_11661', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 7, 'source_order': 7, 'sampling_weight': 1.0}, {'textbook_example_id': 11662, 'component_id': 'src_11662', 'generator_key': 'src_11662', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 8, 'source_order': 8, 'sampling_weight': 1.0}]


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
