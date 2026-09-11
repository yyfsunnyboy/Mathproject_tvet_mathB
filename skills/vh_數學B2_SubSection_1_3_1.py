from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_1'
GENERATOR_KEYS = ['src_11626', 'src_11627', 'src_11645']
GENERATOR_SPECS = [{'textbook_example_id': 11626, 'component_id': 'src_11626', 'generator_key': 'src_11626', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'classify_standard_position_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_standard_position_angle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11626, 'source_order': 11626, 'sampling_weight': 1.0}, {'textbook_example_id': 11627, 'component_id': 'src_11627', 'generator_key': 'src_11627', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'classify_standard_position_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_standard_position_angle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11627, 'source_order': 11627, 'sampling_weight': 1.0}, {'textbook_example_id': 11645, 'component_id': 'src_11645', 'generator_key': 'src_11645', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'classify_standard_position_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_standard_position_angle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11645, 'source_order': 11645, 'sampling_weight': 1.0}]


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
