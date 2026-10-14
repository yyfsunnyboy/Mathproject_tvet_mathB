from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_2_1'
GENERATOR_KEYS = ['src_11851', 'src_11852', 'src_11866', 'src_11875', 'src_11884']
GENERATOR_SPECS = [{'textbook_example_id': 11851, 'component_id': 'src_11851', 'generator_key': 'src_11851', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_point_vs_circles_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_point_vs_circles_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11851, 'source_order': 11851, 'sampling_weight': 10.0}, {'textbook_example_id': 11852, 'component_id': 'src_11852', 'generator_key': 'src_11852', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'classify_point_vs_circles_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_point_vs_circles_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11852, 'source_order': 11852, 'sampling_weight': 10.0}, {'textbook_example_id': 11866, 'component_id': 'src_11866', 'generator_key': 'src_11866', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_point_vs_circles_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_point_vs_circles_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11866, 'source_order': 11866, 'sampling_weight': 10.0}, {'textbook_example_id': 11875, 'component_id': 'src_11875', 'generator_key': 'src_11875', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_point_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_point_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11875, 'source_order': 11875, 'sampling_weight': 10.0}, {'textbook_example_id': 11884, 'component_id': 'src_11884', 'generator_key': 'src_11884', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'identify_point_on_circle_mcq', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'identify_point_on_circle_mcq', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11884, 'source_order': 11884, 'sampling_weight': 10.0}]


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
