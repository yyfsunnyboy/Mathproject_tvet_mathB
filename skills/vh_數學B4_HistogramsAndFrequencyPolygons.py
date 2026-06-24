from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_HistogramsAndFrequencyPolygons'
GENERATOR_KEYS = ['src_3826', 'src_3827', 'src_3828', 'src_3829']
GENERATOR_SPECS = [{'textbook_example_id': 3826, 'component_id': 'src_3826', 'generator_key': 'src_3826', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'frequency_distribution_chart_construction', 'answer_type': 'string', 'answer_value_type': 'string', 'problem_type_id': 'frequency_distribution_chart_construction', 'display_order': 3826, 'source_order': 3826, 'sampling_weight': 10.0}, {'textbook_example_id': 3827, 'component_id': 'src_3827', 'generator_key': 'src_3827', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'frequency_distribution_chart_construction', 'answer_type': 'string', 'answer_value_type': 'string', 'problem_type_id': 'frequency_distribution_chart_construction', 'display_order': 3827, 'source_order': 3827, 'sampling_weight': 10.0}, {'textbook_example_id': 3828, 'component_id': 'src_3828', 'generator_key': 'src_3828', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'frequency_distribution_chart_construction', 'answer_type': 'string', 'answer_value_type': 'string', 'problem_type_id': 'frequency_distribution_chart_construction', 'display_order': 3828, 'source_order': 3828, 'sampling_weight': 10.0}, {'textbook_example_id': 3829, 'component_id': 'src_3829', 'generator_key': 'src_3829', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'histogram_distribution_update', 'answer_type': 'string', 'answer_value_type': 'string', 'problem_type_id': 'histogram_distribution_update', 'display_order': 3829, 'source_order': 3829, 'sampling_weight': 1.0}]


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
