from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B3_SubSection_1_2_2'
GENERATOR_KEYS = ['src_11932', 'src_11933', 'src_11945', 'src_11970']
GENERATOR_SPECS = [{'textbook_example_id': 11932, 'component_id': 'src_11932', 'generator_key': 'src_11932', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_mean_value', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'geometric_mean_value', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11932, 'source_order': 11932, 'sampling_weight': 10.0}, {'textbook_example_id': 11933, 'component_id': 'src_11933', 'generator_key': 'src_11933', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_mean_value', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'geometric_mean_value', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11933, 'source_order': 11933, 'sampling_weight': 10.0}, {'textbook_example_id': 11945, 'component_id': 'src_11945', 'generator_key': 'src_11945', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'geometric_mean_solve_x', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_mean_solve_x', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11945, 'source_order': 11945, 'sampling_weight': 10.0}, {'textbook_example_id': 11970, 'component_id': 'src_11970', 'generator_key': 'src_11970', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'ap_gp_mixed_mean_middle', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'ap_gp_mixed_mean_middle', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11970, 'source_order': 11970, 'sampling_weight': 10.0}]


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
