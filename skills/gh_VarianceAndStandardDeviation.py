from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_VarianceAndStandardDeviation'
GENERATOR_KEYS = ['src_12924', 'src_12925', 'src_12926', 'src_12927', 'src_12928', 'src_12929', 'src_12930', 'src_12932', 'src_12938', 'src_12940']
GENERATOR_SPECS = [{'textbook_example_id': 12924, 'component_id': 'src_12924', 'generator_key': 'src_12924', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'mean_variance_sd', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'mean_variance_sd', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12924, 'source_order': 12924, 'sampling_weight': 10.0}, {'textbook_example_id': 12925, 'component_id': 'src_12925', 'generator_key': 'src_12925', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'standard_deviation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'standard_deviation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12925, 'source_order': 12925, 'sampling_weight': 10.0}, {'textbook_example_id': 12926, 'component_id': 'src_12926', 'generator_key': 'src_12926', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'grade_distribution_read', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'grade_distribution_read', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12926, 'source_order': 12926, 'sampling_weight': 10.0}, {'textbook_example_id': 12927, 'component_id': 'src_12927', 'generator_key': 'src_12927', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'mean_variance_sd', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'mean_variance_sd', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12927, 'source_order': 12927, 'sampling_weight': 10.0}, {'textbook_example_id': 12928, 'component_id': 'src_12928', 'generator_key': 'src_12928', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'compare_standard_deviation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'compare_standard_deviation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12928, 'source_order': 12928, 'sampling_weight': 10.0}, {'textbook_example_id': 12929, 'component_id': 'src_12929', 'generator_key': 'src_12929', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'standard_deviation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'standard_deviation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12929, 'source_order': 12929, 'sampling_weight': 10.0}, {'textbook_example_id': 12930, 'component_id': 'src_12930', 'generator_key': 'src_12930', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'grade_distribution_read', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'grade_distribution_read', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12930, 'source_order': 12930, 'sampling_weight': 10.0}, {'textbook_example_id': 12932, 'component_id': 'src_12932', 'generator_key': 'src_12932', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_stat', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_stat', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12932, 'source_order': 12932, 'sampling_weight': 10.0}, {'textbook_example_id': 12938, 'component_id': 'src_12938', 'generator_key': 'src_12938', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'standard_deviation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'standard_deviation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12938, 'source_order': 12938, 'sampling_weight': 10.0}, {'textbook_example_id': 12940, 'component_id': 'src_12940', 'generator_key': 'src_12940', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'unknown_given_sd', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'unknown_given_sd', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12940, 'source_order': 12940, 'sampling_weight': 10.0}]


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
