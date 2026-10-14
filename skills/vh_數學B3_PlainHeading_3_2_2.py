from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_PlainHeading_3_2_2'
GENERATOR_KEYS = ['src_12065', 'src_12124']
GENERATOR_SPECS = [{'textbook_example_id': 12065, 'component_id': 'src_12065', 'generator_key': 'src_12065', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exam_practice', 'line_type': 'integer_feasible_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'integer_feasible_choice', 'checker_key': 'single_choice', 'display_order': 12065, 'source_order': 12065, 'sampling_weight': 10.0}, {'textbook_example_id': 12124, 'component_id': 'src_12124', 'generator_key': 'src_12124', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'integer_feasible_count', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'integer_feasible_count', 'checker_key': 'expression', 'display_order': 12124, 'source_order': 12124, 'sampling_weight': 10.0}]


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
