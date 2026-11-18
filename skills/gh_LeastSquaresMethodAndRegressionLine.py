from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_LeastSquaresMethodAndRegressionLine'
GENERATOR_KEYS = ['src_12955', 'src_12956', 'src_12961', 'src_12962', 'src_12964', 'src_12965', 'src_12966', 'src_12969', 'src_12970', 'src_12971']
GENERATOR_SPECS = [{'textbook_example_id': 12955, 'component_id': 'src_12955', 'generator_key': 'src_12955', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_bivariate', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_bivariate', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12955, 'source_order': 12955, 'sampling_weight': 10.0}, {'textbook_example_id': 12956, 'component_id': 'src_12956', 'generator_key': 'src_12956', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_bivariate', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_bivariate', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12956, 'source_order': 12956, 'sampling_weight': 10.0}, {'textbook_example_id': 12961, 'component_id': 'src_12961', 'generator_key': 'src_12961', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'regression_from_summary', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'regression_from_summary', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12961, 'source_order': 12961, 'sampling_weight': 10.0}, {'textbook_example_id': 12962, 'component_id': 'src_12962', 'generator_key': 'src_12962', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'regression_from_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'regression_from_table', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12962, 'source_order': 12962, 'sampling_weight': 10.0}, {'textbook_example_id': 12964, 'component_id': 'src_12964', 'generator_key': 'src_12964', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'regression_rounded_from_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'regression_rounded_from_table', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12964, 'source_order': 12964, 'sampling_weight': 10.0}, {'textbook_example_id': 12965, 'component_id': 'src_12965', 'generator_key': 'src_12965', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'correlation_from_regression_point', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'correlation_from_regression_point', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12965, 'source_order': 12965, 'sampling_weight': 10.0}, {'textbook_example_id': 12966, 'component_id': 'src_12966', 'generator_key': 'src_12966', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'regression_from_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'regression_from_table', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12966, 'source_order': 12966, 'sampling_weight': 10.0}, {'textbook_example_id': 12969, 'component_id': 'src_12969', 'generator_key': 'src_12969', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'regression_from_table', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'regression_from_table', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12969, 'source_order': 12969, 'sampling_weight': 10.0}, {'textbook_example_id': 12970, 'component_id': 'src_12970', 'generator_key': 'src_12970', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'regression_line_unknown_intercept', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'regression_line_unknown_intercept', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12970, 'source_order': 12970, 'sampling_weight': 10.0}, {'textbook_example_id': 12971, 'component_id': 'src_12971', 'generator_key': 'src_12971', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'regression_statement_selection', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'regression_statement_selection', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12971, 'source_order': 12971, 'sampling_weight': 10.0}]


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
