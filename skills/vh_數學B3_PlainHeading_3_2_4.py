from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_PlainHeading_3_2_4'
GENERATOR_KEYS = ['src_12072', 'src_12073', 'src_12079', 'src_12080', 'src_12084', 'src_12085', 'src_12108', 'src_12109']
GENERATOR_SPECS = [{'textbook_example_id': 12072, 'component_id': 'src_12072', 'generator_key': 'src_12072', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12072, 'source_order': 12072, 'sampling_weight': 10.0}, {'textbook_example_id': 12073, 'component_id': 'src_12073', 'generator_key': 'src_12073', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12073, 'source_order': 12073, 'sampling_weight': 10.0}, {'textbook_example_id': 12079, 'component_id': 'src_12079', 'generator_key': 'src_12079', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12079, 'source_order': 12079, 'sampling_weight': 10.0}, {'textbook_example_id': 12080, 'component_id': 'src_12080', 'generator_key': 'src_12080', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12080, 'source_order': 12080, 'sampling_weight': 10.0}, {'textbook_example_id': 12084, 'component_id': 'src_12084', 'generator_key': 'src_12084', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12084, 'source_order': 12084, 'sampling_weight': 10.0}, {'textbook_example_id': 12085, 'component_id': 'src_12085', 'generator_key': 'src_12085', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12085, 'source_order': 12085, 'sampling_weight': 10.0}, {'textbook_example_id': 12108, 'component_id': 'src_12108', 'generator_key': 'src_12108', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'same_side_test', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'same_side_test', 'checker_key': 'single_choice', 'display_order': 12108, 'source_order': 12108, 'sampling_weight': 10.0}, {'textbook_example_id': 12109, 'component_id': 'src_12109', 'generator_key': 'src_12109', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'same_side_parameter', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'same_side_parameter', 'checker_key': 'single_choice', 'display_order': 12109, 'source_order': 12109, 'sampling_weight': 10.0}]


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
