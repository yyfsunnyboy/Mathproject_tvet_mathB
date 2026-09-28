from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_4_1_1'
GENERATOR_KEYS = ['src_12127', 'src_12128', 'src_12136', 'src_12145', 'src_12248']
GENERATOR_SPECS = [{'textbook_example_id': 12127, 'component_id': 'src_12127', 'generator_key': 'src_12127', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12127, 'source_order': 12127, 'sampling_weight': 10.0}, {'textbook_example_id': 12128, 'component_id': 'src_12128', 'generator_key': 'src_12128', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12128, 'source_order': 12128, 'sampling_weight': 10.0}, {'textbook_example_id': 12136, 'component_id': 'src_12136', 'generator_key': 'src_12136', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12136, 'source_order': 12136, 'sampling_weight': 10.0}, {'textbook_example_id': 12145, 'component_id': 'src_12145', 'generator_key': 'src_12145', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'advanced_exercise', 'line_type': 'exp_prime_factor_exponent', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'exp_prime_factor_exponent', 'checker_key': 'expression', 'display_order': 12145, 'source_order': 12145, 'sampling_weight': 10.0}, {'textbook_example_id': 12248, 'component_id': 'src_12248', 'generator_key': 'src_12248', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'exp_law_product_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'exp_law_product_choice', 'checker_key': 'single_choice', 'display_order': 12248, 'source_order': 12248, 'sampling_weight': 10.0}]


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
