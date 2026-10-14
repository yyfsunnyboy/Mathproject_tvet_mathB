from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_4_1_2'
GENERATOR_KEYS = ['src_12129', 'src_12130', 'src_12137', 'src_12138', 'src_12139']
GENERATOR_SPECS = [{'textbook_example_id': 12129, 'component_id': 'src_12129', 'generator_key': 'src_12129', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12129, 'source_order': 12129, 'sampling_weight': 10.0}, {'textbook_example_id': 12130, 'component_id': 'src_12130', 'generator_key': 'src_12130', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12130, 'source_order': 12130, 'sampling_weight': 10.0}, {'textbook_example_id': 12137, 'component_id': 'src_12137', 'generator_key': 'src_12137', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_fill_integer_exponent', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_fill_integer_exponent', 'checker_key': 'multi_part', 'display_order': 12137, 'source_order': 12137, 'sampling_weight': 10.0}, {'textbook_example_id': 12138, 'component_id': 'src_12138', 'generator_key': 'src_12138', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_zero_negative_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_zero_negative_eval', 'checker_key': 'multi_part', 'display_order': 12138, 'source_order': 12138, 'sampling_weight': 10.0}, {'textbook_example_id': 12139, 'component_id': 'src_12139', 'generator_key': 'src_12139', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12139, 'source_order': 12139, 'sampling_weight': 10.0}]


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
