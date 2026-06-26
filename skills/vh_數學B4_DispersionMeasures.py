from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B4_DispersionMeasures'
GENERATOR_KEYS = ['src_3845', 'src_3846', 'src_3847', 'src_3891', 'src_3892']
GENERATOR_SPECS = [{'textbook_example_id': 3845, 'component_id': 'src_3845', 'generator_key': 'src_3845', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compute_quartiles_and_iqr', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_quartiles_and_iqr', 'display_order': 3845, 'source_order': 3845, 'sampling_weight': 10.0}, {'textbook_example_id': 3846, 'component_id': 'src_3846', 'generator_key': 'src_3846', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'compare_dispersion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_dispersion', 'display_order': 3846, 'source_order': 3846, 'sampling_weight': 10.0}, {'textbook_example_id': 3847, 'component_id': 'src_3847', 'generator_key': 'src_3847', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'compare_dispersion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_dispersion', 'display_order': 3847, 'source_order': 3847, 'sampling_weight': 10.0}, {'textbook_example_id': 3891, 'component_id': 'src_3891', 'generator_key': 'src_3891', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'conceptual_dispersion_judgment', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'conceptual_dispersion_judgment', 'display_order': 3891, 'source_order': 3891, 'sampling_weight': 10.0}, {'textbook_example_id': 3892, 'component_id': 'src_3892', 'generator_key': 'src_3892', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_population_standard_deviation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compute_population_standard_deviation', 'display_order': 3892, 'source_order': 3892, 'sampling_weight': 10.0}]


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
