from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_3_2'
GENERATOR_KEYS = ['src_11785', 'src_11786', 'src_11796', 'src_11797', 'src_11802']
GENERATOR_SPECS = [{'textbook_example_id': 11785, 'component_id': 'src_11785', 'generator_key': 'src_11785', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_regular_polygon_edge_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_regular_polygon_edge_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11785, 'source_order': 11785, 'sampling_weight': 10.0}, {'textbook_example_id': 11786, 'component_id': 'src_11786', 'generator_key': 'src_11786', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_regular_polygon_edge_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_regular_polygon_edge_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11786, 'source_order': 11786, 'sampling_weight': 10.0}, {'textbook_example_id': 11796, 'component_id': 'src_11796', 'generator_key': 'src_11796', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_regular_polygon_edge_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_regular_polygon_edge_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11796, 'source_order': 11796, 'sampling_weight': 10.0}, {'textbook_example_id': 11797, 'component_id': 'src_11797', 'generator_key': 'src_11797', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_dot_product_from_magnitudes_angle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_product_from_magnitudes_angle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11797, 'source_order': 11797, 'sampling_weight': 10.0}, {'textbook_example_id': 11802, 'component_id': 'src_11802', 'generator_key': 'src_11802', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_dot_identity_multipart', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_identity_multipart', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11802, 'source_order': 11802, 'sampling_weight': 10.0}]


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
