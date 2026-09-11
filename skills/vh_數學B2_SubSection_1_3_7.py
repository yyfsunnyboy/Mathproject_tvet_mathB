from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_7'
GENERATOR_KEYS = ['src_11640', 'src_11641', 'src_11642', 'src_11643', 'src_11644', 'src_11651', 'src_11652']
GENERATOR_SPECS = [{'textbook_example_id': 11640, 'component_id': 'src_11640', 'generator_key': 'src_11640', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11640, 'source_order': 11640, 'sampling_weight': 1.0}, {'textbook_example_id': 11641, 'component_id': 'src_11641', 'generator_key': 'src_11641', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11641, 'source_order': 11641, 'sampling_weight': 1.0}, {'textbook_example_id': 11642, 'component_id': 'src_11642', 'generator_key': 'src_11642', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11642, 'source_order': 11642, 'sampling_weight': 1.0}, {'textbook_example_id': 11643, 'component_id': 'src_11643', 'generator_key': 'src_11643', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'simplify_fundamental_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_fundamental_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11643, 'source_order': 11643, 'sampling_weight': 1.0}, {'textbook_example_id': 11644, 'component_id': 'src_11644', 'generator_key': 'src_11644', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exercise', 'line_type': 'classify_trig_derived_point_quadrant', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_trig_derived_point_quadrant', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 11644, 'source_order': 11644, 'sampling_weight': 1.0}, {'textbook_example_id': 11651, 'component_id': 'src_11651', 'generator_key': 'src_11651', 'presentation_mode': 'table_fill', 'response_mode': 'table_fill', 'interaction_type': 'table_fill', 'source_kind': 'exercise', 'line_type': 'complete_reference_angle_conversion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'complete_reference_angle_conversion', 'checker_key': 'table_fill_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11651, 'source_order': 11651, 'sampling_weight': 1.0}, {'textbook_example_id': 11652, 'component_id': 'src_11652', 'generator_key': 'src_11652', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11652, 'source_order': 11652, 'sampling_weight': 1.0}]


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
