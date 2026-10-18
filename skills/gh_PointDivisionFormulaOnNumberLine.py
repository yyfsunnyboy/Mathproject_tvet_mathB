from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PointDivisionFormulaOnNumberLine'
GENERATOR_KEYS = ['src_1027', 'src_1028', 'src_1038', 'src_1039', 'src_1041', 'src_1042']
GENERATOR_SPECS = [{'textbook_example_id': 1027, 'component_id': 'src_1027', 'generator_key': 'src_1027', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_number_line_division_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_number_line_division_points', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1027, 'source_order': 1027, 'sampling_weight': 10.0}, {'textbook_example_id': 1028, 'component_id': 'src_1028', 'generator_key': 'src_1028', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_number_line_division_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_number_line_division_points', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1028, 'source_order': 1028, 'sampling_weight': 10.0}, {'textbook_example_id': 1038, 'component_id': 'src_1038', 'generator_key': 'src_1038', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_line_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_line_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 1038, 'source_order': 1038, 'sampling_weight': 10.0}, {'textbook_example_id': 1039, 'component_id': 'src_1039', 'generator_key': 'src_1039', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_line_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_line_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 1039, 'source_order': 1039, 'sampling_weight': 10.0}, {'textbook_example_id': 1041, 'component_id': 'src_1041', 'generator_key': 'src_1041', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_number_line_division_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_number_line_division_points', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1041, 'source_order': 1041, 'sampling_weight': 10.0}, {'textbook_example_id': 1042, 'component_id': 'src_1042', 'generator_key': 'src_1042', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'select_extreme_weighted_point', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'select_extreme_weighted_point', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 1042, 'source_order': 1042, 'sampling_weight': 10.0}]


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
