from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_CommonLogarithms'
GENERATOR_KEYS = ['src_12385', 'src_12386', 'src_12387', 'src_12388', 'src_12389', 'src_12390', 'src_12391', 'src_12392', 'src_12393', 'src_12394', 'src_12395', 'src_12396', 'src_12397', 'src_12398', 'src_12399', 'src_12400', 'src_12401', 'src_12402']
GENERATOR_SPECS = [{'textbook_example_id': 12385, 'component_id': 'src_12385', 'generator_key': 'src_12385', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12385, 'source_order': 12385, 'sampling_weight': 1.0}, {'textbook_example_id': 12386, 'component_id': 'src_12386', 'generator_key': 'src_12386', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12386, 'source_order': 12386, 'sampling_weight': 1.0}, {'textbook_example_id': 12387, 'component_id': 'src_12387', 'generator_key': 'src_12387', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12387, 'source_order': 12387, 'sampling_weight': 1.0}, {'textbook_example_id': 12388, 'component_id': 'src_12388', 'generator_key': 'src_12388', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'approximate_common_logarithm', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'approximate_common_logarithm', 'checker_key': None, 'equivalence_type': None, 'display_order': 12388, 'source_order': 12388, 'sampling_weight': 1.0}, {'textbook_example_id': 12389, 'component_id': 'src_12389', 'generator_key': 'src_12389', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'count_digits_of_integer_power', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'count_digits_of_integer_power', 'checker_key': None, 'equivalence_type': None, 'display_order': 12389, 'source_order': 12389, 'sampling_weight': 1.0}, {'textbook_example_id': 12390, 'component_id': 'src_12390', 'generator_key': 'src_12390', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12390, 'source_order': 12390, 'sampling_weight': 1.0}, {'textbook_example_id': 12391, 'component_id': 'src_12391', 'generator_key': 'src_12391', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12391, 'source_order': 12391, 'sampling_weight': 1.0}, {'textbook_example_id': 12392, 'component_id': 'src_12392', 'generator_key': 'src_12392', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12392, 'source_order': 12392, 'sampling_weight': 1.0}, {'textbook_example_id': 12393, 'component_id': 'src_12393', 'generator_key': 'src_12393', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'count_digits_of_integer_power', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'count_digits_of_integer_power', 'checker_key': None, 'equivalence_type': None, 'display_order': 12393, 'source_order': 12393, 'sampling_weight': 1.0}, {'textbook_example_id': 12394, 'component_id': 'src_12394', 'generator_key': 'src_12394', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_property_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_property_statements', 'checker_key': None, 'equivalence_type': None, 'display_order': 12394, 'source_order': 12394, 'sampling_weight': 1.0}, {'textbook_example_id': 12395, 'component_id': 'src_12395', 'generator_key': 'src_12395', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12395, 'source_order': 12395, 'sampling_weight': 1.0}, {'textbook_example_id': 12396, 'component_id': 'src_12396', 'generator_key': 'src_12396', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12396, 'source_order': 12396, 'sampling_weight': 1.0}, {'textbook_example_id': 12397, 'component_id': 'src_12397', 'generator_key': 'src_12397', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_property_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_property_statements', 'checker_key': None, 'equivalence_type': None, 'display_order': 12397, 'source_order': 12397, 'sampling_weight': 1.0}, {'textbook_example_id': 12398, 'component_id': 'src_12398', 'generator_key': 'src_12398', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12398, 'source_order': 12398, 'sampling_weight': 1.0}, {'textbook_example_id': 12399, 'component_id': 'src_12399', 'generator_key': 'src_12399', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12399, 'source_order': 12399, 'sampling_weight': 1.0}, {'textbook_example_id': 12400, 'component_id': 'src_12400', 'generator_key': 'src_12400', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_power_of_ten_exponent', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_power_of_ten_exponent', 'checker_key': None, 'equivalence_type': None, 'display_order': 12400, 'source_order': 12400, 'sampling_weight': 1.0}, {'textbook_example_id': 12401, 'component_id': 'src_12401', 'generator_key': 'src_12401', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_power_of_ten_exponent', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_power_of_ten_exponent', 'checker_key': None, 'equivalence_type': None, 'display_order': 12401, 'source_order': 12401, 'sampling_weight': 1.0}, {'textbook_example_id': 12402, 'component_id': 'src_12402', 'generator_key': 'src_12402', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'select_nearest_model_value', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'select_nearest_model_value', 'checker_key': None, 'equivalence_type': None, 'display_order': 12402, 'source_order': 12402, 'sampling_weight': 1.0}]


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
