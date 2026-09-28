from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_3_3_4'
GENERATOR_KEYS = ['src_12092', 'src_12093', 'src_12094', 'src_12095', 'src_12096', 'src_12105', 'src_12106', 'src_12115', 'src_12125']
GENERATOR_SPECS = [{'textbook_example_id': 12092, 'component_id': 'src_12092', 'generator_key': 'src_12092', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12092, 'source_order': 12092, 'sampling_weight': 10.0}, {'textbook_example_id': 12093, 'component_id': 'src_12093', 'generator_key': 'src_12093', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12093, 'source_order': 12093, 'sampling_weight': 10.0}, {'textbook_example_id': 12094, 'component_id': 'src_12094', 'generator_key': 'src_12094', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12094, 'source_order': 12094, 'sampling_weight': 10.0}, {'textbook_example_id': 12095, 'component_id': 'src_12095', 'generator_key': 'src_12095', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12095, 'source_order': 12095, 'sampling_weight': 10.0}, {'textbook_example_id': 12096, 'component_id': 'src_12096', 'generator_key': 'src_12096', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exam_practice', 'line_type': 'lp_application', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'lp_application', 'checker_key': 'single_choice', 'display_order': 12096, 'source_order': 12096, 'sampling_weight': 10.0}, {'textbook_example_id': 12105, 'component_id': 'src_12105', 'generator_key': 'src_12105', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12105, 'source_order': 12105, 'sampling_weight': 10.0}, {'textbook_example_id': 12106, 'component_id': 'src_12106', 'generator_key': 'src_12106', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12106, 'source_order': 12106, 'sampling_weight': 10.0}, {'textbook_example_id': 12115, 'component_id': 'src_12115', 'generator_key': 'src_12115', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'constraint_system_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'constraint_system_choice', 'checker_key': 'single_choice', 'display_order': 12115, 'source_order': 12115, 'sampling_weight': 10.0}, {'textbook_example_id': 12125, 'component_id': 'src_12125', 'generator_key': 'src_12125', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'constraint_system_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'constraint_system_choice', 'checker_key': 'single_choice', 'display_order': 12125, 'source_order': 12125, 'sampling_weight': 10.0}]


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
