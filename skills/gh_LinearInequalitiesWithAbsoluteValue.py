from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LinearInequalitiesWithAbsoluteValue'
GENERATOR_KEYS = ['src_1033', 'src_1034', 'src_1035', 'src_1036', 'src_1037', 'src_1040', 'src_1044', 'src_1045', 'src_1046', 'src_1048', 'src_1049', 'src_12331', 'src_12332', 'src_12333']
GENERATOR_SPECS = [{'textbook_example_id': 1033, 'component_id': 'src_1033', 'generator_key': 'src_1033', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1033, 'source_order': 1033, 'sampling_weight': 10.0}, {'textbook_example_id': 1034, 'component_id': 'src_1034', 'generator_key': 'src_1034', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1034, 'source_order': 1034, 'sampling_weight': 10.0}, {'textbook_example_id': 1035, 'component_id': 'src_1035', 'generator_key': 'src_1035', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1035, 'source_order': 1035, 'sampling_weight': 10.0}, {'textbook_example_id': 1036, 'component_id': 'src_1036', 'generator_key': 'src_1036', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'inequality_solution', 'answer_value_type': 'inequality_solution', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 1036, 'source_order': 1036, 'sampling_weight': 10.0}, {'textbook_example_id': 1037, 'component_id': 'src_1037', 'generator_key': 'src_1037', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1037, 'source_order': 1037, 'sampling_weight': 10.0}, {'textbook_example_id': 1040, 'component_id': 'src_1040', 'generator_key': 'src_1040', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_absolute_value_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_absolute_value_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 1040, 'source_order': 1040, 'sampling_weight': 10.0}, {'textbook_example_id': 1044, 'component_id': 'src_1044', 'generator_key': 'src_1044', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1044, 'source_order': 1044, 'sampling_weight': 10.0}, {'textbook_example_id': 1045, 'component_id': 'src_1045', 'generator_key': 'src_1045', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1045, 'source_order': 1045, 'sampling_weight': 10.0}, {'textbook_example_id': 1046, 'component_id': 'src_1046', 'generator_key': 'src_1046', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1046, 'source_order': 1046, 'sampling_weight': 10.0}, {'textbook_example_id': 1048, 'component_id': 'src_1048', 'generator_key': 'src_1048', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1048, 'source_order': 1048, 'sampling_weight': 10.0}, {'textbook_example_id': 1049, 'component_id': 'src_1049', 'generator_key': 'src_1049', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1049, 'source_order': 1049, 'sampling_weight': 10.0}, {'textbook_example_id': 12331, 'component_id': 'src_12331', 'generator_key': 'src_12331', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12331, 'source_order': 12331, 'sampling_weight': 10.0}, {'textbook_example_id': 12332, 'component_id': 'src_12332', 'generator_key': 'src_12332', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'inequality_solution', 'answer_value_type': 'inequality_solution', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12332, 'source_order': 12332, 'sampling_weight': 10.0}, {'textbook_example_id': 12333, 'component_id': 'src_12333', 'generator_key': 'src_12333', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_tolerance_range_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_tolerance_range_application', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12333, 'source_order': 12333, 'sampling_weight': 10.0}]


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
