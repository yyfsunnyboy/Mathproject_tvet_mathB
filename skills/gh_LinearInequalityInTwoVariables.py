from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LinearInequalityInTwoVariables'
GENERATOR_KEYS = ['src_12425', 'src_12426', 'src_12427', 'src_12428', 'src_12429', 'src_12430', 'src_12435', 'src_12441', 'src_12442', 'src_12443', 'src_12447']
GENERATOR_SPECS = [{'textbook_example_id': 12425, 'component_id': 'src_12425', 'generator_key': 'src_12425', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'graph_inequality_system', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'graph_inequality_system', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 12425, 'source_order': 12425, 'sampling_weight': 10.0}, {'textbook_example_id': 12426, 'component_id': 'src_12426', 'generator_key': 'src_12426', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'graph_inequality_system', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'graph_inequality_system', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 12426, 'source_order': 12426, 'sampling_weight': 10.0}, {'textbook_example_id': 12427, 'component_id': 'src_12427', 'generator_key': 'src_12427', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_triangle_region_system', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_triangle_region_system', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12427, 'source_order': 12427, 'sampling_weight': 10.0}, {'textbook_example_id': 12428, 'component_id': 'src_12428', 'generator_key': 'src_12428', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'graph_inequality_series', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_inequality_series', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12428, 'source_order': 12428, 'sampling_weight': 10.0}, {'textbook_example_id': 12429, 'component_id': 'src_12429', 'generator_key': 'src_12429', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'quiz', 'line_type': 'graph_inequality_system', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'graph_inequality_system', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 12429, 'source_order': 12429, 'sampling_weight': 10.0}, {'textbook_example_id': 12430, 'component_id': 'src_12430', 'generator_key': 'src_12430', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'read_region_signs_from_figure', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'read_region_signs_from_figure', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12430, 'source_order': 12430, 'sampling_weight': 10.0}, {'textbook_example_id': 12435, 'component_id': 'src_12435', 'generator_key': 'src_12435', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12435, 'source_order': 12435, 'sampling_weight': 10.0}, {'textbook_example_id': 12441, 'component_id': 'src_12441', 'generator_key': 'src_12441', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'select_points_same_side', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'select_points_same_side', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12441, 'source_order': 12441, 'sampling_weight': 10.0}, {'textbook_example_id': 12442, 'component_id': 'src_12442', 'generator_key': 'src_12442', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'graph_inequality_system', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'graph_inequality_system', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 12442, 'source_order': 12442, 'sampling_weight': 10.0}, {'textbook_example_id': 12443, 'component_id': 'src_12443', 'generator_key': 'src_12443', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_region_coefficients_from_figure', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_region_coefficients_from_figure', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12443, 'source_order': 12443, 'sampling_weight': 10.0}, {'textbook_example_id': 12447, 'component_id': 'src_12447', 'generator_key': 'src_12447', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'graph_inequality_with_lattice_count', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_inequality_with_lattice_count', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12447, 'source_order': 12447, 'sampling_weight': 10.0}]


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
