from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_StandardFormOfACircle'
GENERATOR_KEYS = ['src_12449', 'src_12450', 'src_12451', 'src_12452', 'src_12470', 'src_12474', 'src_12476', 'src_12479', 'src_12480']
GENERATOR_SPECS = [{'textbook_example_id': 12449, 'component_id': 'src_12449', 'generator_key': 'src_12449', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12449, 'source_order': 12449, 'sampling_weight': 10.0}, {'textbook_example_id': 12450, 'component_id': 'src_12450', 'generator_key': 'src_12450', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_equations', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'write_circle_equations', 'checker_key': 'equation_checker', 'equivalence_type': None, 'display_order': 12450, 'source_order': 12450, 'sampling_weight': 10.0}, {'textbook_example_id': 12451, 'component_id': 'src_12451', 'generator_key': 'src_12451', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12451, 'source_order': 12451, 'sampling_weight': 10.0}, {'textbook_example_id': 12452, 'component_id': 'src_12452', 'generator_key': 'src_12452', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12452, 'source_order': 12452, 'sampling_weight': 10.0}, {'textbook_example_id': 12470, 'component_id': 'src_12470', 'generator_key': 'src_12470', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12470, 'source_order': 12470, 'sampling_weight': 10.0}, {'textbook_example_id': 12474, 'component_id': 'src_12474', 'generator_key': 'src_12474', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12474, 'source_order': 12474, 'sampling_weight': 10.0}, {'textbook_example_id': 12476, 'component_id': 'src_12476', 'generator_key': 'src_12476', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12476, 'source_order': 12476, 'sampling_weight': 10.0}, {'textbook_example_id': 12479, 'component_id': 'src_12479', 'generator_key': 'src_12479', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'write_circle_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12479, 'source_order': 12479, 'sampling_weight': 10.0}, {'textbook_example_id': 12480, 'component_id': 'src_12480', 'generator_key': 'src_12480', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circular_arch_height', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_circular_arch_height', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12480, 'source_order': 12480, 'sampling_weight': 10.0}]


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
