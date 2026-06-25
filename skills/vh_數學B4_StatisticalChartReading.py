from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_StatisticalChartReading'
GENERATOR_KEYS = ['src_3884', 'src_3885', 'src_3886']
GENERATOR_SPECS = [
    {
        'textbook_example_id': 3884, 'component_id': 'src_3884', 'generator_key': 'src_3884',
        'presentation_mode': 'single_choice', 'response_mode': 'single_choice',
        'interaction_type': 'single_choice', 'source_kind': 'test',
        'line_type': 'cumulative_above_fail_count', 'answer_type': 'single_choice',
        'answer_value_type': 'choice_label', 'semantic_answer_type': 'integer',
        'problem_type_id': 'cumulative_above_fail_count',
        'domain_key': 'statistics.table_chart', 'domain_operation': 'cumulative_above_fail_count',
        'display_order': 3884, 'source_order': 3884, 'sampling_weight': 10.0,
    },
    {
        'textbook_example_id': 3885, 'component_id': 'src_3885', 'generator_key': 'src_3885',
        'presentation_mode': 'single_choice', 'response_mode': 'single_choice',
        'interaction_type': 'single_choice', 'source_kind': 'test',
        'line_type': 'cumulative_above_interval_count', 'answer_type': 'single_choice',
        'answer_value_type': 'choice_label', 'semantic_answer_type': 'integer',
        'problem_type_id': 'cumulative_above_interval_count',
        'domain_key': 'statistics.table_chart', 'domain_operation': 'cumulative_above_interval_count',
        'display_order': 3885, 'source_order': 3885, 'sampling_weight': 10.0,
    },
    {
        'textbook_example_id': 3886, 'component_id': 'src_3886', 'generator_key': 'src_3886',
        'presentation_mode': 'single_choice', 'response_mode': 'single_choice',
        'interaction_type': 'single_choice', 'source_kind': 'test',
        'line_type': 'cumulative_below_interval_count', 'answer_type': 'single_choice',
        'answer_value_type': 'choice_label', 'semantic_answer_type': 'integer',
        'problem_type_id': 'cumulative_below_interval_count',
        'domain_key': 'statistics.table_chart', 'domain_operation': 'cumulative_below_interval_count',
        'display_order': 3886, 'source_order': 3886, 'sampling_weight': 10.0,
    },
]


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
