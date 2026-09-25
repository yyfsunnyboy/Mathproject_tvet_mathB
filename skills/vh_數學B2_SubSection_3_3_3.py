from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_3_3'
GENERATOR_KEYS = ['src_11787', 'src_11788', 'src_11789', 'src_11790', 'src_11798', 'src_11811']
GENERATOR_SPECS = [{'textbook_example_id': 11787, 'component_id': 'src_11787', 'generator_key': 'src_11787', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_dot_product_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_product_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11787, 'source_order': 11787, 'sampling_weight': 10.0}, {'textbook_example_id': 11788, 'component_id': 'src_11788', 'generator_key': 'src_11788', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_dot_product_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_product_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11788, 'source_order': 11788, 'sampling_weight': 10.0}, {'textbook_example_id': 11789, 'component_id': 'src_11789', 'generator_key': 'src_11789', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_cosine_of_angle_from_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_cosine_of_angle_from_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11789, 'source_order': 11789, 'sampling_weight': 10.0}, {'textbook_example_id': 11790, 'component_id': 'src_11790', 'generator_key': 'src_11790', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_cosine_of_angle_from_dot', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_cosine_of_angle_from_dot', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11790, 'source_order': 11790, 'sampling_weight': 10.0}, {'textbook_example_id': 11798, 'component_id': 'src_11798', 'generator_key': 'src_11798', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_dot_product_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_product_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11798, 'source_order': 11798, 'sampling_weight': 10.0}, {'textbook_example_id': 11811, 'component_id': 'src_11811', 'generator_key': 'src_11811', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_dot_product_coordinates', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_dot_product_coordinates', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11811, 'source_order': 11811, 'sampling_weight': 10.0}]


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
