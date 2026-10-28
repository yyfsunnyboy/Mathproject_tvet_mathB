from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PermutationWithIdenticalItems'
GENERATOR_KEYS = ['src_12793', 'src_12794', 'src_12795', 'src_12796', 'src_12797', 'src_12798', 'src_12799', 'src_12800', 'src_12802', 'src_12803']
GENERATOR_SPECS = [{'textbook_example_id': 12793, 'component_id': 'src_12793', 'generator_key': 'src_12793', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identical_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'identical_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12793, 'source_order': 12793, 'sampling_weight': 10.0}, {'textbook_example_id': 12794, 'component_id': 'src_12794', 'generator_key': 'src_12794', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'grid_paths', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'grid_paths', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12794, 'source_order': 12794, 'sampling_weight': 10.0}, {'textbook_example_id': 12795, 'component_id': 'src_12795', 'generator_key': 'src_12795', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'multiset_digit_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'multiset_digit_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12795, 'source_order': 12795, 'sampling_weight': 10.0}, {'textbook_example_id': 12796, 'component_id': 'src_12796', 'generator_key': 'src_12796', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identical_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'identical_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12796, 'source_order': 12796, 'sampling_weight': 10.0}, {'textbook_example_id': 12797, 'component_id': 'src_12797', 'generator_key': 'src_12797', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'grid_paths', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'grid_paths', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12797, 'source_order': 12797, 'sampling_weight': 10.0}, {'textbook_example_id': 12798, 'component_id': 'src_12798', 'generator_key': 'src_12798', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'multiset_digit_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'multiset_digit_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12798, 'source_order': 12798, 'sampling_weight': 10.0}, {'textbook_example_id': 12799, 'component_id': 'src_12799', 'generator_key': 'src_12799', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12799, 'source_order': 12799, 'sampling_weight': 10.0}, {'textbook_example_id': 12800, 'component_id': 'src_12800', 'generator_key': 'src_12800', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'colored_distinct_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'colored_distinct_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12800, 'source_order': 12800, 'sampling_weight': 10.0}, {'textbook_example_id': 12802, 'component_id': 'src_12802', 'generator_key': 'src_12802', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'line_walk', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'line_walk', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12802, 'source_order': 12802, 'sampling_weight': 10.0}, {'textbook_example_id': 12803, 'component_id': 'src_12803', 'generator_key': 'src_12803', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'column_shooting_order', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'column_shooting_order', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12803, 'source_order': 12803, 'sampling_weight': 10.0}]


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
