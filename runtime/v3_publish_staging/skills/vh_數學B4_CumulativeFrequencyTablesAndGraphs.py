from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_CumulativeFrequencyTablesAndGraphs'
GENERATOR_KEYS = ['src_3830', 'src_3831', 'src_3832', 'src_3833', 'src_3834']
GENERATOR_SPECS = [{'textbook_example_id': 3830, 'component_id': 'src_3830', 'generator_key': 'src_3830', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'cumulative_frequency_graph_reading', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'cumulative_frequency_graph_reading', 'display_order': 3830, 'source_order': 3830, 'sampling_weight': 10.0}, {'textbook_example_id': 3831, 'component_id': 'src_3831', 'generator_key': 'src_3831', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'cumulative_frequency_table_construction', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'cumulative_frequency_table_construction', 'display_order': 3831, 'source_order': 3831, 'sampling_weight': 10.0}, {'textbook_example_id': 3832, 'component_id': 'src_3832', 'generator_key': 'src_3832', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'cumulative_frequency_graph_reading', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'cumulative_frequency_graph_reading', 'display_order': 3832, 'source_order': 3832, 'sampling_weight': 10.0}, {'textbook_example_id': 3833, 'component_id': 'src_3833', 'generator_key': 'src_3833', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'cumulative_frequency_graph_reading', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'cumulative_frequency_graph_reading', 'display_order': 3833, 'source_order': 3833, 'sampling_weight': 10.0}, {'textbook_example_id': 3834, 'component_id': 'src_3834', 'generator_key': 'src_3834', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'class_frequency_from_cumulative_difference', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'class_frequency_from_cumulative_difference', 'display_order': 3834, 'source_order': 3834, 'sampling_weight': 10.0}]


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
