from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LogicAndSets'
GENERATOR_KEYS = ['src_12744', 'src_12745', 'src_12747', 'src_12748', 'src_12763', 'src_12764', 'src_12766', 'src_12767']
GENERATOR_SPECS = [{'textbook_example_id': 12744, 'component_id': 'src_12744', 'generator_key': 'src_12744', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'interval_set_operations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interval_set_operations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12744, 'source_order': 12744, 'sampling_weight': 10.0}, {'textbook_example_id': 12745, 'component_id': 'src_12745', 'generator_key': 'src_12745', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'proposition_truth', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'proposition_truth', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12745, 'source_order': 12745, 'sampling_weight': 10.0}, {'textbook_example_id': 12747, 'component_id': 'src_12747', 'generator_key': 'src_12747', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'condition_relation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'condition_relation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12747, 'source_order': 12747, 'sampling_weight': 10.0}, {'textbook_example_id': 12748, 'component_id': 'src_12748', 'generator_key': 'src_12748', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'finite_set_operations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'finite_set_operations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12748, 'source_order': 12748, 'sampling_weight': 10.0}, {'textbook_example_id': 12763, 'component_id': 'src_12763', 'generator_key': 'src_12763', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'proposition_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'proposition_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12763, 'source_order': 12763, 'sampling_weight': 10.0}, {'textbook_example_id': 12764, 'component_id': 'src_12764', 'generator_key': 'src_12764', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'implication_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'implication_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12764, 'source_order': 12764, 'sampling_weight': 10.0}, {'textbook_example_id': 12766, 'component_id': 'src_12766', 'generator_key': 'src_12766', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'finite_set_operations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'finite_set_operations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12766, 'source_order': 12766, 'sampling_weight': 10.0}, {'textbook_example_id': 12767, 'component_id': 'src_12767', 'generator_key': 'src_12767', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'equation_root_sets', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'equation_root_sets', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12767, 'source_order': 12767, 'sampling_weight': 10.0}]


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
