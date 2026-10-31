from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_SampleSpace'
GENERATOR_KEYS = ['src_12849', 'src_12850', 'src_12851', 'src_12852', 'src_12853', 'src_12854']
GENERATOR_SPECS = [{'textbook_example_id': 12849, 'component_id': 'src_12849', 'generator_key': 'src_12849', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'coin_outcome_space', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coin_outcome_space', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12849, 'source_order': 12849, 'sampling_weight': 10.0}, {'textbook_example_id': 12850, 'component_id': 'src_12850', 'generator_key': 'src_12850', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'draw_outcome_space', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'draw_outcome_space', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12850, 'source_order': 12850, 'sampling_weight': 10.0}, {'textbook_example_id': 12851, 'component_id': 'src_12851', 'generator_key': 'src_12851', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'coin_outcome_space', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coin_outcome_space', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12851, 'source_order': 12851, 'sampling_weight': 10.0}, {'textbook_example_id': 12852, 'component_id': 'src_12852', 'generator_key': 'src_12852', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'draw_outcome_space', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'draw_outcome_space', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12852, 'source_order': 12852, 'sampling_weight': 10.0}, {'textbook_example_id': 12853, 'component_id': 'src_12853', 'generator_key': 'src_12853', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'coded_event_sets', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coded_event_sets', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12853, 'source_order': 12853, 'sampling_weight': 10.0}, {'textbook_example_id': 12854, 'component_id': 'src_12854', 'generator_key': 'src_12854', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'coded_event_sets', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coded_event_sets', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12854, 'source_order': 12854, 'sampling_weight': 10.0}]


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
