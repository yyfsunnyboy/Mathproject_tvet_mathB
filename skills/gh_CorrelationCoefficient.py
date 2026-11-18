from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_CorrelationCoefficient'
GENERATOR_KEYS = ['src_12949', 'src_12950', 'src_12951', 'src_12952', 'src_12953', 'src_12957', 'src_12958', 'src_12959', 'src_12967', 'src_12968', 'src_12972']
GENERATOR_SPECS = [{'textbook_example_id': 12949, 'component_id': 'src_12949', 'generator_key': 'src_12949', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_bivariate', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_bivariate', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12949, 'source_order': 12949, 'sampling_weight': 10.0}, {'textbook_example_id': 12950, 'component_id': 'src_12950', 'generator_key': 'src_12950', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'correlation_from_table', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_table', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12950, 'source_order': 12950, 'sampling_weight': 10.0}, {'textbook_example_id': 12951, 'component_id': 'src_12951', 'generator_key': 'src_12951', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'correlation_from_table', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_table', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12951, 'source_order': 12951, 'sampling_weight': 10.0}, {'textbook_example_id': 12952, 'component_id': 'src_12952', 'generator_key': 'src_12952', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'correlation_from_table', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_table', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12952, 'source_order': 12952, 'sampling_weight': 10.0}, {'textbook_example_id': 12953, 'component_id': 'src_12953', 'generator_key': 'src_12953', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'correlation_from_table', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_table', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12953, 'source_order': 12953, 'sampling_weight': 10.0}, {'textbook_example_id': 12957, 'component_id': 'src_12957', 'generator_key': 'src_12957', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_bivariate', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_bivariate', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12957, 'source_order': 12957, 'sampling_weight': 10.0}, {'textbook_example_id': 12958, 'component_id': 'src_12958', 'generator_key': 'src_12958', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_bivariate', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_bivariate', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12958, 'source_order': 12958, 'sampling_weight': 10.0}, {'textbook_example_id': 12959, 'component_id': 'src_12959', 'generator_key': 'src_12959', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'correlation_remove_point', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'correlation_remove_point', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12959, 'source_order': 12959, 'sampling_weight': 10.0}, {'textbook_example_id': 12967, 'component_id': 'src_12967', 'generator_key': 'src_12967', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'correlation_change_add_point', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'correlation_change_add_point', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12967, 'source_order': 12967, 'sampling_weight': 10.0}, {'textbook_example_id': 12968, 'component_id': 'src_12968', 'generator_key': 'src_12968', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'correlation_from_table', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_table', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12968, 'source_order': 12968, 'sampling_weight': 10.0}, {'textbook_example_id': 12972, 'component_id': 'src_12972', 'generator_key': 'src_12972', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'correlation_rescale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'correlation_rescale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12972, 'source_order': 12972, 'sampling_weight': 10.0}]


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
