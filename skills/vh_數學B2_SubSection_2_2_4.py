from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_2_2_4'
GENERATOR_KEYS = ['src_11691', 'src_11692', 'src_11693', 'src_11694', 'src_11702', 'src_11703', 'src_11721', 'src_11722']
GENERATOR_SPECS = [{'textbook_example_id': 11691, 'component_id': 'src_11691', 'generator_key': 'src_11691', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11691, 'source_order': 11691, 'sampling_weight': 10.0}, {'textbook_example_id': 11692, 'component_id': 'src_11692', 'generator_key': 'src_11692', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_side_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11692, 'source_order': 11692, 'sampling_weight': 10.0}, {'textbook_example_id': 11693, 'component_id': 'src_11693', 'generator_key': 'src_11693', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11693, 'source_order': 11693, 'sampling_weight': 10.0}, {'textbook_example_id': 11694, 'component_id': 'src_11694', 'generator_key': 'src_11694', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11694, 'source_order': 11694, 'sampling_weight': 10.0}, {'textbook_example_id': 11702, 'component_id': 'src_11702', 'generator_key': 'src_11702', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11702, 'source_order': 11702, 'sampling_weight': 10.0}, {'textbook_example_id': 11703, 'component_id': 'src_11703', 'generator_key': 'src_11703', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11703, 'source_order': 11703, 'sampling_weight': 10.0}, {'textbook_example_id': 11721, 'component_id': 'src_11721', 'generator_key': 'src_11721', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_side_by_law_of_cosines', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_side_by_law_of_cosines', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11721, 'source_order': 11721, 'sampling_weight': 10.0}, {'textbook_example_id': 11722, 'component_id': 'src_11722', 'generator_key': 'src_11722', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_side_by_law_of_sines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_side_by_law_of_sines', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11722, 'source_order': 11722, 'sampling_weight': 10.0}]


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
