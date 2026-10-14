from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_2_6'
GENERATOR_KEYS = ['src_11772', 'src_11773', 'src_11774', 'src_11782', 'src_11810']
GENERATOR_SPECS = [{'textbook_example_id': 11772, 'component_id': 'src_11772', 'generator_key': 'src_11772', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_scaled_direction_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_scaled_direction_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11772, 'source_order': 11772, 'sampling_weight': 10.0}, {'textbook_example_id': 11773, 'component_id': 'src_11773', 'generator_key': 'src_11773', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_scaled_direction_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_scaled_direction_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11773, 'source_order': 11773, 'sampling_weight': 10.0}, {'textbook_example_id': 11774, 'component_id': 'src_11774', 'generator_key': 'src_11774', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'identify_unit_vector_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'identify_unit_vector_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11774, 'source_order': 11774, 'sampling_weight': 10.0}, {'textbook_example_id': 11782, 'component_id': 'src_11782', 'generator_key': 'src_11782', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_scaled_direction_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_scaled_direction_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11782, 'source_order': 11782, 'sampling_weight': 10.0}, {'textbook_example_id': 11810, 'component_id': 'src_11810', 'generator_key': 'src_11810', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_scaled_direction_vector', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_scaled_direction_vector', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11810, 'source_order': 11810, 'sampling_weight': 10.0}]


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
