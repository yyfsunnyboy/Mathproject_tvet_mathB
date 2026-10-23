from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_EquationOfALine'
GENERATOR_KEYS = ['src_12405', 'src_12406', 'src_12407', 'src_12408', 'src_12409', 'src_12410', 'src_12432', 'src_12437', 'src_12445']
GENERATOR_SPECS = [{'textbook_example_id': 12405, 'component_id': 'src_12405', 'generator_key': 'src_12405', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12405, 'source_order': 12405, 'sampling_weight': 10.0}, {'textbook_example_id': 12406, 'component_id': 'src_12406', 'generator_key': 'src_12406', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12406, 'source_order': 12406, 'sampling_weight': 10.0}, {'textbook_example_id': 12407, 'component_id': 'src_12407', 'generator_key': 'src_12407', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'slope_of_line_from_equation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'slope_of_line_from_equation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12407, 'source_order': 12407, 'sampling_weight': 10.0}, {'textbook_example_id': 12408, 'component_id': 'src_12408', 'generator_key': 'src_12408', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12408, 'source_order': 12408, 'sampling_weight': 10.0}, {'textbook_example_id': 12409, 'component_id': 'src_12409', 'generator_key': 'src_12409', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12409, 'source_order': 12409, 'sampling_weight': 10.0}, {'textbook_example_id': 12410, 'component_id': 'src_12410', 'generator_key': 'src_12410', 'presentation_mode': 'table_fill', 'response_mode': 'table_fill', 'interaction_type': 'table_fill', 'source_kind': 'quiz', 'line_type': 'fill_line_property_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'fill_line_property_table', 'checker_key': 'table_fill_checker', 'equivalence_type': None, 'display_order': 12410, 'source_order': 12410, 'sampling_weight': 10.0}, {'textbook_example_id': 12432, 'component_id': 'src_12432', 'generator_key': 'src_12432', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12432, 'source_order': 12432, 'sampling_weight': 10.0}, {'textbook_example_id': 12437, 'component_id': 'src_12437', 'generator_key': 'src_12437', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_line_equations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_line_equations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12437, 'source_order': 12437, 'sampling_weight': 10.0}, {'textbook_example_id': 12445, 'component_id': 'src_12445', 'generator_key': 'src_12445', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_axis_triangle_area_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_axis_triangle_area_line', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12445, 'source_order': 12445, 'sampling_weight': 10.0}]


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
