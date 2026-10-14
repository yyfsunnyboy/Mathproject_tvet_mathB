from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_5'
GENERATOR_KEYS = ['src_11634', 'src_11635', 'src_11648']
GENERATOR_SPECS = [{'textbook_example_id': 11634, 'component_id': 'src_11634', 'generator_key': 'src_11634', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11634, 'source_order': 11634, 'sampling_weight': 1.0}, {'textbook_example_id': 11635, 'component_id': 'src_11635', 'generator_key': 'src_11635', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11635, 'source_order': 11635, 'sampling_weight': 1.0}, {'textbook_example_id': 11648, 'component_id': 'src_11648', 'generator_key': 'src_11648', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_arbitrary_angle_trig_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_arbitrary_angle_trig_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11648, 'source_order': 11648, 'sampling_weight': 1.0}]


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
