from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_2_4'
GENERATOR_KEYS = ['src_11863', 'src_11864', 'src_11865', 'src_11873', 'src_11894']
GENERATOR_SPECS = [{'textbook_example_id': 11863, 'component_id': 'src_11863', 'generator_key': 'src_11863', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_tangent_segment_lengths', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_tangent_segment_lengths', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11863, 'source_order': 11863, 'sampling_weight': 10.0}, {'textbook_example_id': 11864, 'component_id': 'src_11864', 'generator_key': 'src_11864', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_tangent_segment_lengths', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_tangent_segment_lengths', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11864, 'source_order': 11864, 'sampling_weight': 10.0}, {'textbook_example_id': 11865, 'component_id': 'src_11865', 'generator_key': 'src_11865', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'count_line_vs_two_circles_intersections', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'count_line_vs_two_circles_intersections', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11865, 'source_order': 11865, 'sampling_weight': 10.0}, {'textbook_example_id': 11873, 'component_id': 'src_11873', 'generator_key': 'src_11873', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_tangent_segment_lengths', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_tangent_segment_lengths', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11873, 'source_order': 11873, 'sampling_weight': 10.0}, {'textbook_example_id': 11894, 'component_id': 'src_11894', 'generator_key': 'src_11894', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_tangent_segment_length_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_tangent_segment_length_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11894, 'source_order': 11894, 'sampling_weight': 10.0}]


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
