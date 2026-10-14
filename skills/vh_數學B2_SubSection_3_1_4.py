from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_3_1_4'
GENERATOR_KEYS = ['src_11739', 'src_11740', 'src_11741', 'src_11742', 'src_11743', 'src_11744', 'src_11748', 'src_11749', 'src_11750', 'src_11751', 'src_11752', 'src_11753', 'src_11817', 'src_11818']
GENERATOR_SPECS = [{'textbook_example_id': 11739, 'component_id': 'src_11739', 'generator_key': 'src_11739', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_scalar_multiple_relation_fill', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_scalar_multiple_relation_fill', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11739, 'source_order': 11739, 'sampling_weight': 10.0}, {'textbook_example_id': 11740, 'component_id': 'src_11740', 'generator_key': 'src_11740', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_scalar_multiple_relation_fill', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_scalar_multiple_relation_fill', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11740, 'source_order': 11740, 'sampling_weight': 10.0}, {'textbook_example_id': 11741, 'component_id': 'src_11741', 'generator_key': 'src_11741', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11741, 'source_order': 11741, 'sampling_weight': 10.0}, {'textbook_example_id': 11742, 'component_id': 'src_11742', 'generator_key': 'src_11742', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11742, 'source_order': 11742, 'sampling_weight': 10.0}, {'textbook_example_id': 11743, 'component_id': 'src_11743', 'generator_key': 'src_11743', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'identify_resultant_path_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'identify_resultant_path_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11743, 'source_order': 11743, 'sampling_weight': 10.0}, {'textbook_example_id': 11744, 'component_id': 'src_11744', 'generator_key': 'src_11744', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11744, 'source_order': 11744, 'sampling_weight': 10.0}, {'textbook_example_id': 11748, 'component_id': 'src_11748', 'generator_key': 'src_11748', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11748, 'source_order': 11748, 'sampling_weight': 10.0}, {'textbook_example_id': 11749, 'component_id': 'src_11749', 'generator_key': 'src_11749', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'construct_linear_combination_choice', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'construct_linear_combination_choice', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11749, 'source_order': 11749, 'sampling_weight': 10.0}, {'textbook_example_id': 11750, 'component_id': 'src_11750', 'generator_key': 'src_11750', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_scalar_multiple_relation_fill', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_scalar_multiple_relation_fill', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11750, 'source_order': 11750, 'sampling_weight': 10.0}, {'textbook_example_id': 11751, 'component_id': 'src_11751', 'generator_key': 'src_11751', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11751, 'source_order': 11751, 'sampling_weight': 10.0}, {'textbook_example_id': 11752, 'component_id': 'src_11752', 'generator_key': 'src_11752', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11752, 'source_order': 11752, 'sampling_weight': 10.0}, {'textbook_example_id': 11753, 'component_id': 'src_11753', 'generator_key': 'src_11753', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'express_section_point_vector', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_section_point_vector', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11753, 'source_order': 11753, 'sampling_weight': 10.0}, {'textbook_example_id': 11817, 'component_id': 'src_11817', 'generator_key': 'src_11817', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'solve_section_coefficient_pair', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_section_coefficient_pair', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11817, 'source_order': 11817, 'sampling_weight': 10.0}, {'textbook_example_id': 11818, 'component_id': 'src_11818', 'generator_key': 'src_11818', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'express_linear_combination_from_givens', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'express_linear_combination_from_givens', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11818, 'source_order': 11818, 'sampling_weight': 10.0}]


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
