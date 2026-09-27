from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_2_2_3'
GENERATOR_KEYS = ['src_12003', 'src_12004', 'src_12005', 'src_12006', 'src_12016', 'src_12020', 'src_12028', 'src_12029', 'src_12030']
GENERATOR_SPECS = [{'textbook_example_id': 12003, 'component_id': 'src_12003', 'generator_key': 'src_12003', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12003, 'source_order': 12003, 'sampling_weight': 10.0}, {'textbook_example_id': 12004, 'component_id': 'src_12004', 'generator_key': 'src_12004', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12004, 'source_order': 12004, 'sampling_weight': 10.0}, {'textbook_example_id': 12005, 'component_id': 'src_12005', 'generator_key': 'src_12005', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_parameter_equal_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_equal_roots', 'checker_key': 'expression_checker', 'display_order': 12005, 'source_order': 12005, 'sampling_weight': 10.0}, {'textbook_example_id': 12006, 'component_id': 'src_12006', 'generator_key': 'src_12006', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12006, 'source_order': 12006, 'sampling_weight': 10.0}, {'textbook_example_id': 12016, 'component_id': 'src_12016', 'generator_key': 'src_12016', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12016, 'source_order': 12016, 'sampling_weight': 10.0}, {'textbook_example_id': 12020, 'component_id': 'src_12020', 'generator_key': 'src_12020', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12020, 'source_order': 12020, 'sampling_weight': 10.0}, {'textbook_example_id': 12028, 'component_id': 'src_12028', 'generator_key': 'src_12028', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_parameter_equal_roots', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_parameter_equal_roots', 'checker_key': 'single_choice_checker', 'display_order': 12028, 'source_order': 12028, 'sampling_weight': 10.0}, {'textbook_example_id': 12029, 'component_id': 'src_12029', 'generator_key': 'src_12029', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12029, 'source_order': 12029, 'sampling_weight': 10.0}, {'textbook_example_id': 12030, 'component_id': 'src_12030', 'generator_key': 'src_12030', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_parameter_two_distinct', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_parameter_two_distinct', 'checker_key': 'single_choice_checker', 'display_order': 12030, 'source_order': 12030, 'sampling_weight': 10.0}]


def _resolve_v3_package_root() -> str:
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs: Any) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID, GENERATOR_KEYS, GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level, seed=seed, difficulty=difficulty, **kwargs,
    )


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> Any:
    return dispatch_check(user_answer, correct_answer, question_payload=question_payload, v3_package_root=_resolve_v3_package_root(), skill_id=SKILL_ID)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(step, question_payload=question_payload, v3_package_root=_resolve_v3_package_root(), skill_id=SKILL_ID)
