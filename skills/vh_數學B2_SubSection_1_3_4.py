from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_4'
GENERATOR_KEYS = ['src_11630', 'src_11631', 'src_11632', 'src_11633', 'src_11647', 'src_11649', 'src_11653']
GENERATOR_SPECS = [{'textbook_example_id': 11630, 'component_id': 'src_11630', 'generator_key': 'src_11630', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11630, 'source_order': 11630, 'sampling_weight': 1.0}, {'textbook_example_id': 11631, 'component_id': 'src_11631', 'generator_key': 'src_11631', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11631, 'source_order': 11631, 'sampling_weight': 1.0}, {'textbook_example_id': 11632, 'component_id': 'src_11632', 'generator_key': 'src_11632', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11632, 'source_order': 11632, 'sampling_weight': 1.0}, {'textbook_example_id': 11633, 'component_id': 'src_11633', 'generator_key': 'src_11633', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11633, 'source_order': 11633, 'sampling_weight': 1.0}, {'textbook_example_id': 11647, 'component_id': 'src_11647', 'generator_key': 'src_11647', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11647, 'source_order': 11647, 'sampling_weight': 1.0}, {'textbook_example_id': 11649, 'component_id': 'src_11649', 'generator_key': 'src_11649', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_signed_trig_constraints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_signed_trig_constraints', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11649, 'source_order': 11649, 'sampling_weight': 1.0}, {'textbook_example_id': 11653, 'component_id': 'src_11653', 'generator_key': 'src_11653', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'classify_trig_derived_point_quadrant', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_trig_derived_point_quadrant', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11653, 'source_order': 11653, 'sampling_weight': 1.0}]


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
