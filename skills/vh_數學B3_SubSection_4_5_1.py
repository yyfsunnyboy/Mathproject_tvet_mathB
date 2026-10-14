from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_4_5_1'
GENERATOR_KEYS = ['src_12221', 'src_12222', 'src_12223', 'src_12224', 'src_12238', 'src_12265']
GENERATOR_SPECS = [{'textbook_example_id': 12221, 'component_id': 'src_12221', 'generator_key': 'src_12221', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12221, 'source_order': 12221, 'sampling_weight': 10.0}, {'textbook_example_id': 12222, 'component_id': 'src_12222', 'generator_key': 'src_12222', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12222, 'source_order': 12222, 'sampling_weight': 10.0}, {'textbook_example_id': 12223, 'component_id': 'src_12223', 'generator_key': 'src_12223', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12223, 'source_order': 12223, 'sampling_weight': 10.0}, {'textbook_example_id': 12224, 'component_id': 'src_12224', 'generator_key': 'src_12224', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12224, 'source_order': 12224, 'sampling_weight': 10.0}, {'textbook_example_id': 12238, 'component_id': 'src_12238', 'generator_key': 'src_12238', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12238, 'source_order': 12238, 'sampling_weight': 10.0}, {'textbook_example_id': 12265, 'component_id': 'src_12265', 'generator_key': 'src_12265', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'common_log_given_approx_eval', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'common_log_given_approx_eval', 'checker_key': 'expression', 'display_order': 12265, 'source_order': 12265, 'sampling_weight': 10.0}]


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
