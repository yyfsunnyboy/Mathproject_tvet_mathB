from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_BinomialTheorem'
GENERATOR_KEYS = ['src_12835', 'src_12836', 'src_12837', 'src_12839', 'src_12840', 'src_12841', 'src_12842', 'src_12843', 'src_12844', 'src_12846', 'src_12847', 'src_12848']
GENERATOR_SPECS = [{'textbook_example_id': 12835, 'component_id': 'src_12835', 'generator_key': 'src_12835', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'binomial_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'binomial_expansion', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12835, 'source_order': 12835, 'sampling_weight': 10.0}, {'textbook_example_id': 12836, 'component_id': 'src_12836', 'generator_key': 'src_12836', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'binomial_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'binomial_expansion', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12836, 'source_order': 12836, 'sampling_weight': 10.0}, {'textbook_example_id': 12837, 'component_id': 'src_12837', 'generator_key': 'src_12837', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'general_term_coefficient', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'general_term_coefficient', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12837, 'source_order': 12837, 'sampling_weight': 10.0}, {'textbook_example_id': 12839, 'component_id': 'src_12839', 'generator_key': 'src_12839', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'at_least_k_selection', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'at_least_k_selection', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12839, 'source_order': 12839, 'sampling_weight': 10.0}, {'textbook_example_id': 12840, 'component_id': 'src_12840', 'generator_key': 'src_12840', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'combination_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'combination_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12840, 'source_order': 12840, 'sampling_weight': 10.0}, {'textbook_example_id': 12841, 'component_id': 'src_12841', 'generator_key': 'src_12841', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'binomial_sum_bound', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'binomial_sum_bound', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12841, 'source_order': 12841, 'sampling_weight': 10.0}, {'textbook_example_id': 12842, 'component_id': 'src_12842', 'generator_key': 'src_12842', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'binomial_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'binomial_expansion', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12842, 'source_order': 12842, 'sampling_weight': 10.0}, {'textbook_example_id': 12843, 'component_id': 'src_12843', 'generator_key': 'src_12843', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'radical_binomial_power', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'radical_binomial_power', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12843, 'source_order': 12843, 'sampling_weight': 10.0}, {'textbook_example_id': 12844, 'component_id': 'src_12844', 'generator_key': 'src_12844', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'general_term_coefficient', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'general_term_coefficient', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12844, 'source_order': 12844, 'sampling_weight': 10.0}, {'textbook_example_id': 12846, 'component_id': 'src_12846', 'generator_key': 'src_12846', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'at_least_k_selection', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'at_least_k_selection', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12846, 'source_order': 12846, 'sampling_weight': 10.0}, {'textbook_example_id': 12847, 'component_id': 'src_12847', 'generator_key': 'src_12847', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'general_term_coefficient', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'general_term_coefficient', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12847, 'source_order': 12847, 'sampling_weight': 10.0}, {'textbook_example_id': 12848, 'component_id': 'src_12848', 'generator_key': 'src_12848', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coefficient_solve_parameter', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'coefficient_solve_parameter', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12848, 'source_order': 12848, 'sampling_weight': 10.0}]


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
