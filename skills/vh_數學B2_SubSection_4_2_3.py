from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_2_3'
GENERATOR_KEYS = ['src_11859', 'src_11860', 'src_11861', 'src_11862', 'src_11871', 'src_11872', 'src_11885', 'src_11895']
GENERATOR_SPECS = [{'textbook_example_id': 11859, 'component_id': 'src_11859', 'generator_key': 'src_11859', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'tangent_at_point_on_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangent_at_point_on_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11859, 'source_order': 11859, 'sampling_weight': 10.0}, {'textbook_example_id': 11860, 'component_id': 'src_11860', 'generator_key': 'src_11860', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'tangent_at_point_on_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangent_at_point_on_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11860, 'source_order': 11860, 'sampling_weight': 10.0}, {'textbook_example_id': 11861, 'component_id': 'src_11861', 'generator_key': 'src_11861', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'tangents_parallel_to_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangents_parallel_to_line', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11861, 'source_order': 11861, 'sampling_weight': 10.0}, {'textbook_example_id': 11862, 'component_id': 'src_11862', 'generator_key': 'src_11862', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'tangents_perpendicular_to_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangents_perpendicular_to_line', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11862, 'source_order': 11862, 'sampling_weight': 10.0}, {'textbook_example_id': 11871, 'component_id': 'src_11871', 'generator_key': 'src_11871', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'tangent_at_point_on_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangent_at_point_on_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11871, 'source_order': 11871, 'sampling_weight': 10.0}, {'textbook_example_id': 11872, 'component_id': 'src_11872', 'generator_key': 'src_11872', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'tangents_parallel_to_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'tangents_parallel_to_line', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11872, 'source_order': 11872, 'sampling_weight': 10.0}, {'textbook_example_id': 11885, 'component_id': 'src_11885', 'generator_key': 'src_11885', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'tangent_at_point_on_circle_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'tangent_at_point_on_circle_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11885, 'source_order': 11885, 'sampling_weight': 10.0}, {'textbook_example_id': 11895, 'component_id': 'src_11895', 'generator_key': 'src_11895', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_tangents_from_point_quad_area', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_tangents_from_point_quad_area', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11895, 'source_order': 11895, 'sampling_weight': 10.0}]


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
