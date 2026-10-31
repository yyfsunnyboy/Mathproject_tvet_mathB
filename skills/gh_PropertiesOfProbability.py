from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PropertiesOfProbability'
GENERATOR_KEYS = ['src_12885', 'src_12886', 'src_12887', 'src_12888', 'src_12889', 'src_12890']
GENERATOR_SPECS = [{'textbook_example_id': 12885, 'component_id': 'src_12885', 'generator_key': 'src_12885', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'probability_algebra', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'probability_algebra', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12885, 'source_order': 12885, 'sampling_weight': 10.0}, {'textbook_example_id': 12886, 'component_id': 'src_12886', 'generator_key': 'src_12886', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12886, 'source_order': 12886, 'sampling_weight': 10.0}, {'textbook_example_id': 12887, 'component_id': 'src_12887', 'generator_key': 'src_12887', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'dice_count_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12887, 'source_order': 12887, 'sampling_weight': 10.0}, {'textbook_example_id': 12888, 'component_id': 'src_12888', 'generator_key': 'src_12888', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'probability_algebra', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'probability_algebra', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12888, 'source_order': 12888, 'sampling_weight': 10.0}, {'textbook_example_id': 12889, 'component_id': 'src_12889', 'generator_key': 'src_12889', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'urn_draw_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12889, 'source_order': 12889, 'sampling_weight': 10.0}, {'textbook_example_id': 12890, 'component_id': 'src_12890', 'generator_key': 'src_12890', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'replacement_count_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'replacement_count_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12890, 'source_order': 12890, 'sampling_weight': 10.0}]


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
