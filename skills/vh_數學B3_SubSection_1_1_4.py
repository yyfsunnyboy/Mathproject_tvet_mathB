from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_1_4'
GENERATOR_KEYS = ['src_11906', 'src_11907', 'src_11917', 'src_11962']
GENERATOR_SPECS = [{'textbook_example_id': 11906, 'component_id': 'src_11906', 'generator_key': 'src_11906', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_recurrence_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_recurrence_general', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11906, 'source_order': 11906, 'sampling_weight': 10.0}, {'textbook_example_id': 11907, 'component_id': 'src_11907', 'generator_key': 'src_11907', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_recurrence_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_recurrence_general', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11907, 'source_order': 11907, 'sampling_weight': 10.0}, {'textbook_example_id': 11917, 'component_id': 'src_11917', 'generator_key': 'src_11917', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_recurrence_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_recurrence_general', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11917, 'source_order': 11917, 'sampling_weight': 10.0}, {'textbook_example_id': 11962, 'component_id': 'src_11962', 'generator_key': 'src_11962', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'arithmetic_recurrence_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_recurrence_general', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11962, 'source_order': 11962, 'sampling_weight': 10.0}]


def _resolve_v3_package_root() -> str:
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
