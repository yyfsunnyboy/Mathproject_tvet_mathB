from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_4_4'
GENERATOR_KEYS = ['src_11663', 'src_11664', 'src_11665', 'src_11666', 'src_11667', 'src_11668', 'src_11669', 'src_11670', 'src_11671', 'src_11672', 'src_11673', 'src_11674', 'src_11675']
GENERATOR_SPECS = [{'textbook_example_id': 11663, 'component_id': 'src_11663', 'generator_key': 'src_11663', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 9, 'source_order': 9, 'sampling_weight': 1.0}, {'textbook_example_id': 11664, 'component_id': 'src_11664', 'generator_key': 'src_11664', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 10, 'source_order': 10, 'sampling_weight': 1.0}, {'textbook_example_id': 11665, 'component_id': 'src_11665', 'generator_key': 'src_11665', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classify_trig_expression_sign_change', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_trig_expression_sign_change', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 11, 'source_order': 11, 'sampling_weight': 1.0}, {'textbook_example_id': 11666, 'component_id': 'src_11666', 'generator_key': 'src_11666', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compare_trig_values_by_monotonicity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_trig_values_by_monotonicity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 12, 'source_order': 12, 'sampling_weight': 1.0}, {'textbook_example_id': 11667, 'component_id': 'src_11667', 'generator_key': 'src_11667', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exercise', 'line_type': 'classify_trig_equation_feasibility', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_trig_equation_feasibility', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 13, 'source_order': 13, 'sampling_weight': 1.0}, {'textbook_example_id': 11668, 'component_id': 'src_11668', 'generator_key': 'src_11668', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'solve_trig_value_quadratic_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_trig_value_quadratic_constraint', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 14, 'source_order': 14, 'sampling_weight': 1.0}, {'textbook_example_id': 11669, 'component_id': 'src_11669', 'generator_key': 'src_11669', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 15, 'source_order': 15, 'sampling_weight': 1.0}, {'textbook_example_id': 11670, 'component_id': 'src_11670', 'generator_key': 'src_11670', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 16, 'source_order': 16, 'sampling_weight': 1.0}, {'textbook_example_id': 11671, 'component_id': 'src_11671', 'generator_key': 'src_11671', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_tangent_absolute_graph_period', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_tangent_absolute_graph_period', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 17, 'source_order': 17, 'sampling_weight': 1.0}, {'textbook_example_id': 11672, 'component_id': 'src_11672', 'generator_key': 'src_11672', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 18, 'source_order': 18, 'sampling_weight': 1.0}, {'textbook_example_id': 11673, 'component_id': 'src_11673', 'generator_key': 'src_11673', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_trig_decimal', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_trig_decimal', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 19, 'source_order': 19, 'sampling_weight': 1.0}, {'textbook_example_id': 11674, 'component_id': 'src_11674', 'generator_key': 'src_11674', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'count_sine_cosine_intersections', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'count_sine_cosine_intersections', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 20, 'source_order': 20, 'sampling_weight': 1.0}, {'textbook_example_id': 11675, 'component_id': 'src_11675', 'generator_key': 'src_11675', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 21, 'source_order': 21, 'sampling_weight': 1.0}]


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
