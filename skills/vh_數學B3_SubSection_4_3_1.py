from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_4_3_1'
GENERATOR_KEYS = ['src_12171', 'src_12172', 'src_12188', 'src_12250']
GENERATOR_SPECS = [{'textbook_example_id': 12171, 'component_id': 'src_12171', 'generator_key': 'src_12171', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'log_definition_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_definition_eval', 'checker_key': 'multi_part', 'display_order': 12171, 'source_order': 12171, 'sampling_weight': 10.0}, {'textbook_example_id': 12172, 'component_id': 'src_12172', 'generator_key': 'src_12172', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'log_definition_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_definition_eval', 'checker_key': 'multi_part', 'display_order': 12172, 'source_order': 12172, 'sampling_weight': 10.0}, {'textbook_example_id': 12188, 'component_id': 'src_12188', 'generator_key': 'src_12188', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'log_domain_validity_choice', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_domain_validity_choice', 'checker_key': 'multi_part', 'display_order': 12188, 'source_order': 12188, 'sampling_weight': 10.0}, {'textbook_example_id': 12250, 'component_id': 'src_12250', 'generator_key': 'src_12250', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'log_domain_validity_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'log_domain_validity_choice', 'checker_key': 'single_choice', 'display_order': 12250, 'source_order': 12250, 'sampling_weight': 10.0}]


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
