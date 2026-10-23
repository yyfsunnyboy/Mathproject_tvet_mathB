from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_TangentLinesOfACircle'
GENERATOR_KEYS = ['src_12500', 'src_12501', 'src_12502', 'src_12503', 'src_12504', 'src_12505', 'src_12506', 'src_12507', 'src_12508', 'src_12509', 'src_12510', 'src_12511', 'src_12512', 'src_12514', 'src_12516']
GENERATOR_SPECS = [{'textbook_example_id': 12500, 'component_id': 'src_12500', 'generator_key': 'src_12500', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12500, 'source_order': 12500, 'sampling_weight': 10.0}, {'textbook_example_id': 12501, 'component_id': 'src_12501', 'generator_key': 'src_12501', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12501, 'source_order': 12501, 'sampling_weight': 10.0}, {'textbook_example_id': 12502, 'component_id': 'src_12502', 'generator_key': 'src_12502', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12502, 'source_order': 12502, 'sampling_weight': 10.0}, {'textbook_example_id': 12503, 'component_id': 'src_12503', 'generator_key': 'src_12503', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12503, 'source_order': 12503, 'sampling_weight': 10.0}, {'textbook_example_id': 12504, 'component_id': 'src_12504', 'generator_key': 'src_12504', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_circle_from_tangent_point', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_from_tangent_point', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12504, 'source_order': 12504, 'sampling_weight': 10.0}, {'textbook_example_id': 12505, 'component_id': 'src_12505', 'generator_key': 'src_12505', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12505, 'source_order': 12505, 'sampling_weight': 10.0}, {'textbook_example_id': 12506, 'component_id': 'src_12506', 'generator_key': 'src_12506', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12506, 'source_order': 12506, 'sampling_weight': 10.0}, {'textbook_example_id': 12507, 'component_id': 'src_12507', 'generator_key': 'src_12507', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12507, 'source_order': 12507, 'sampling_weight': 10.0}, {'textbook_example_id': 12508, 'component_id': 'src_12508', 'generator_key': 'src_12508', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12508, 'source_order': 12508, 'sampling_weight': 10.0}, {'textbook_example_id': 12509, 'component_id': 'src_12509', 'generator_key': 'src_12509', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12509, 'source_order': 12509, 'sampling_weight': 10.0}, {'textbook_example_id': 12510, 'component_id': 'src_12510', 'generator_key': 'src_12510', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12510, 'source_order': 12510, 'sampling_weight': 10.0}, {'textbook_example_id': 12511, 'component_id': 'src_12511', 'generator_key': 'src_12511', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12511, 'source_order': 12511, 'sampling_weight': 10.0}, {'textbook_example_id': 12512, 'component_id': 'src_12512', 'generator_key': 'src_12512', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12512, 'source_order': 12512, 'sampling_weight': 10.0}, {'textbook_example_id': 12514, 'component_id': 'src_12514', 'generator_key': 'src_12514', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12514, 'source_order': 12514, 'sampling_weight': 10.0}, {'textbook_example_id': 12516, 'component_id': 'src_12516', 'generator_key': 'src_12516', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12516, 'source_order': 12516, 'sampling_weight': 10.0}]


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
