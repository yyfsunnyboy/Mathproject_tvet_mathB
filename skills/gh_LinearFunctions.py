from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LinearFunctions'
GENERATOR_KEYS = ['src_12560', 'src_12561', 'src_12562', 'src_12563', 'src_12564', 'src_12565', 'src_12566', 'src_12598']
GENERATOR_SPECS = [{'textbook_example_id': 12560, 'component_id': 'src_12560', 'generator_key': 'src_12560', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_linear_functions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_linear_functions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12560, 'source_order': 12560, 'sampling_weight': 10.0}, {'textbook_example_id': 12561, 'component_id': 'src_12561', 'generator_key': 'src_12561', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_linear_functions', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_linear_functions', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12561, 'source_order': 12561, 'sampling_weight': 10.0}, {'textbook_example_id': 12562, 'component_id': 'src_12562', 'generator_key': 'src_12562', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_function_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12562, 'source_order': 12562, 'sampling_weight': 10.0}, {'textbook_example_id': 12563, 'component_id': 'src_12563', 'generator_key': 'src_12563', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_linear_functions', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'solve_linear_functions', 'checker_key': 'expression_equivalence_checker', 'equivalence_type': None, 'display_order': 12563, 'source_order': 12563, 'sampling_weight': 10.0}, {'textbook_example_id': 12564, 'component_id': 'src_12564', 'generator_key': 'src_12564', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_linear_functions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_linear_functions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12564, 'source_order': 12564, 'sampling_weight': 10.0}, {'textbook_example_id': 12565, 'component_id': 'src_12565', 'generator_key': 'src_12565', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_linear_functions', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_linear_functions', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12565, 'source_order': 12565, 'sampling_weight': 10.0}, {'textbook_example_id': 12566, 'component_id': 'src_12566', 'generator_key': 'src_12566', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12566, 'source_order': 12566, 'sampling_weight': 10.0}, {'textbook_example_id': 12598, 'component_id': 'src_12598', 'generator_key': 'src_12598', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12598, 'source_order': 12598, 'sampling_weight': 10.0}]


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
