from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_1_3'
GENERATOR_KEYS = ['src_11735', 'src_11736', 'src_11737', 'src_11738', 'src_11746', 'src_11747', 'src_11816']
GENERATOR_SPECS = [{'textbook_example_id': 11735, 'component_id': 'src_11735', 'generator_key': 'src_11735', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11735, 'source_order': 11735, 'sampling_weight': 10.0}, {'textbook_example_id': 11736, 'component_id': 'src_11736', 'generator_key': 'src_11736', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11736, 'source_order': 11736, 'sampling_weight': 10.0}, {'textbook_example_id': 11737, 'component_id': 'src_11737', 'generator_key': 'src_11737', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11737, 'source_order': 11737, 'sampling_weight': 10.0}, {'textbook_example_id': 11738, 'component_id': 'src_11738', 'generator_key': 'src_11738', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11738, 'source_order': 11738, 'sampling_weight': 10.0}, {'textbook_example_id': 11746, 'component_id': 'src_11746', 'generator_key': 'src_11746', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11746, 'source_order': 11746, 'sampling_weight': 10.0}, {'textbook_example_id': 11747, 'component_id': 'src_11747', 'generator_key': 'src_11747', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11747, 'source_order': 11747, 'sampling_weight': 10.0}, {'textbook_example_id': 11816, 'component_id': 'src_11816', 'generator_key': 'src_11816', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'simplify_vector_path_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_vector_path_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11816, 'source_order': 11816, 'sampling_weight': 10.0}]


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
