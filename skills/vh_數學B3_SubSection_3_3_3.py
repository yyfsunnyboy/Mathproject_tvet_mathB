from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = 'vh_數學B3_SubSection_3_3_3'
GENERATOR_KEYS = ['src_12090', 'src_12091', 'src_12103', 'src_12114', 'src_12116', 'src_12126']
GENERATOR_SPECS = [{'textbook_example_id': 12090, 'component_id': 'src_12090', 'generator_key': 'src_12090', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12090, 'source_order': 12090, 'sampling_weight': 10.0}, {'textbook_example_id': 12091, 'component_id': 'src_12091', 'generator_key': 'src_12091', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12091, 'source_order': 12091, 'sampling_weight': 10.0}, {'textbook_example_id': 12103, 'component_id': 'src_12103', 'generator_key': 'src_12103', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12103, 'source_order': 12103, 'sampling_weight': 10.0}, {'textbook_example_id': 12114, 'component_id': 'src_12114', 'generator_key': 'src_12114', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12114, 'source_order': 12114, 'sampling_weight': 10.0}, {'textbook_example_id': 12116, 'component_id': 'src_12116', 'generator_key': 'src_12116', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12116, 'source_order': 12116, 'sampling_weight': 10.0}, {'textbook_example_id': 12126, 'component_id': 'src_12126', 'generator_key': 'src_12126', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'lp_extrema', 'checker_key': 'single_choice', 'display_order': 12126, 'source_order': 12126, 'sampling_weight': 10.0}]


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
