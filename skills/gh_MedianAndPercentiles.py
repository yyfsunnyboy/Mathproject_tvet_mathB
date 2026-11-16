from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_MedianAndPercentiles'
GENERATOR_KEYS = ['src_12918', 'src_12919', 'src_12920', 'src_12921', 'src_12922', 'src_12923', 'src_12934', 'src_12935', 'src_12946']
GENERATOR_SPECS = [{'textbook_example_id': 12918, 'component_id': 'src_12918', 'generator_key': 'src_12918', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'median_lists', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'median_lists', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12918, 'source_order': 12918, 'sampling_weight': 10.0}, {'textbook_example_id': 12919, 'component_id': 'src_12919', 'generator_key': 'src_12919', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'percentile_frequency', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'percentile_frequency', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12919, 'source_order': 12919, 'sampling_weight': 10.0}, {'textbook_example_id': 12920, 'component_id': 'src_12920', 'generator_key': 'src_12920', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'quartile_frequency', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quartile_frequency', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12920, 'source_order': 12920, 'sampling_weight': 10.0}, {'textbook_example_id': 12921, 'component_id': 'src_12921', 'generator_key': 'src_12921', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'median_consecutive', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'median_consecutive', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12921, 'source_order': 12921, 'sampling_weight': 10.0}, {'textbook_example_id': 12922, 'component_id': 'src_12922', 'generator_key': 'src_12922', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'percentile_frequency', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'percentile_frequency', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12922, 'source_order': 12922, 'sampling_weight': 10.0}, {'textbook_example_id': 12923, 'component_id': 'src_12923', 'generator_key': 'src_12923', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'statement_selection', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'statement_selection', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12923, 'source_order': 12923, 'sampling_weight': 10.0}, {'textbook_example_id': 12934, 'component_id': 'src_12934', 'generator_key': 'src_12934', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_stat', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_stat', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12934, 'source_order': 12934, 'sampling_weight': 10.0}, {'textbook_example_id': 12935, 'component_id': 'src_12935', 'generator_key': 'src_12935', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'list_summary_stats', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'list_summary_stats', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12935, 'source_order': 12935, 'sampling_weight': 10.0}, {'textbook_example_id': 12946, 'component_id': 'src_12946', 'generator_key': 'src_12946', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'statement_selection', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'statement_selection', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12946, 'source_order': 12946, 'sampling_weight': 10.0}]


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
