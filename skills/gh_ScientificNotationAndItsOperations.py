from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_ScientificNotationAndItsOperations'
GENERATOR_KEYS = ['src_12377', 'src_12378', 'src_12379', 'src_12380', 'src_12381', 'src_12382', 'src_12383', 'src_12384']
GENERATOR_SPECS = [{'textbook_example_id': 12377, 'component_id': 'src_12377', 'generator_key': 'src_12377', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12377, 'source_order': 12377, 'sampling_weight': 1.0}, {'textbook_example_id': 12378, 'component_id': 'src_12378', 'generator_key': 'src_12378', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12378, 'source_order': 12378, 'sampling_weight': 1.0}, {'textbook_example_id': 12379, 'component_id': 'src_12379', 'generator_key': 'src_12379', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12379, 'source_order': 12379, 'sampling_weight': 1.0}, {'textbook_example_id': 12380, 'component_id': 'src_12380', 'generator_key': 'src_12380', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12380, 'source_order': 12380, 'sampling_weight': 1.0}, {'textbook_example_id': 12381, 'component_id': 'src_12381', 'generator_key': 'src_12381', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12381, 'source_order': 12381, 'sampling_weight': 1.0}, {'textbook_example_id': 12382, 'component_id': 'src_12382', 'generator_key': 'src_12382', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12382, 'source_order': 12382, 'sampling_weight': 1.0}, {'textbook_example_id': 12383, 'component_id': 'src_12383', 'generator_key': 'src_12383', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_scientific_notation_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_scientific_notation_expression', 'checker_key': None, 'equivalence_type': None, 'display_order': 12383, 'source_order': 12383, 'sampling_weight': 1.0}, {'textbook_example_id': 12384, 'component_id': 'src_12384', 'generator_key': 'src_12384', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_number_property_statements', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_number_property_statements', 'checker_key': None, 'equivalence_type': None, 'display_order': 12384, 'source_order': 12384, 'sampling_weight': 1.0}]


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
