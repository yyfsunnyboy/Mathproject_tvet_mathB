from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_Event'
GENERATOR_KEYS = ['src_12855', 'src_12856', 'src_12857', 'src_12858', 'src_12859']
GENERATOR_SPECS = [{'textbook_example_id': 12855, 'component_id': 'src_12855', 'generator_key': 'src_12855', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_event_sets', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_event_sets', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12855, 'source_order': 12855, 'sampling_weight': 10.0}, {'textbook_example_id': 12856, 'component_id': 'src_12856', 'generator_key': 'src_12856', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'event_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'event_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12856, 'source_order': 12856, 'sampling_weight': 10.0}, {'textbook_example_id': 12857, 'component_id': 'src_12857', 'generator_key': 'src_12857', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'dice_event_sets', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_event_sets', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12857, 'source_order': 12857, 'sampling_weight': 10.0}, {'textbook_example_id': 12858, 'component_id': 'src_12858', 'generator_key': 'src_12858', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'event_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'event_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12858, 'source_order': 12858, 'sampling_weight': 10.0}, {'textbook_example_id': 12859, 'component_id': 'src_12859', 'generator_key': 'src_12859', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'event_relation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'event_relation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12859, 'source_order': 12859, 'sampling_weight': 10.0}]


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
