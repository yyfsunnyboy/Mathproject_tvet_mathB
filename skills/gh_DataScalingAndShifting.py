from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_DataScalingAndShifting'
GENERATOR_KEYS = ['src_12933', 'src_12939', 'src_12941', 'src_12942', 'src_12943', 'src_12944', 'src_12945']
GENERATOR_SPECS = [{'textbook_example_id': 12933, 'component_id': 'src_12933', 'generator_key': 'src_12933', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_stat', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_stat', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12933, 'source_order': 12933, 'sampling_weight': 10.0}, {'textbook_example_id': 12939, 'component_id': 'src_12939', 'generator_key': 'src_12939', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'linear_find_scale_sd', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'linear_find_scale_sd', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12939, 'source_order': 12939, 'sampling_weight': 10.0}, {'textbook_example_id': 12941, 'component_id': 'src_12941', 'generator_key': 'src_12941', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'statement_selection', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'statement_selection', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12941, 'source_order': 12941, 'sampling_weight': 10.0}, {'textbook_example_id': 12942, 'component_id': 'src_12942', 'generator_key': 'src_12942', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'linear_mean_sd', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_mean_sd', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12942, 'source_order': 12942, 'sampling_weight': 10.0}, {'textbook_example_id': 12943, 'component_id': 'src_12943', 'generator_key': 'src_12943', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'standardize_scores', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'standardize_scores', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12943, 'source_order': 12943, 'sampling_weight': 10.0}, {'textbook_example_id': 12944, 'component_id': 'src_12944', 'generator_key': 'src_12944', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'monthly_mean_sd', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'monthly_mean_sd', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12944, 'source_order': 12944, 'sampling_weight': 10.0}, {'textbook_example_id': 12945, 'component_id': 'src_12945', 'generator_key': 'src_12945', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'linear_mean_sd', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_mean_sd', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12945, 'source_order': 12945, 'sampling_weight': 10.0}]


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
