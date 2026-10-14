from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_ArcLengthAndAreaOfSector'
GENERATOR_KEYS = ['src_11608', 'src_11609', 'src_11610', 'src_11619', 'src_11620', 'src_11624', 'src_11625']
GENERATOR_SPECS = [{'textbook_example_id': 11608, 'component_id': 'src_11608', 'generator_key': 'src_11608', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11608, 'source_order': 11608, 'sampling_weight': 1.0}, {'textbook_example_id': 11609, 'component_id': 'src_11609', 'generator_key': 'src_11609', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11609, 'source_order': 11609, 'sampling_weight': 1.0}, {'textbook_example_id': 11610, 'component_id': 'src_11610', 'generator_key': 'src_11610', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11610, 'source_order': 11610, 'sampling_weight': 1.0}, {'textbook_example_id': 11619, 'component_id': 'src_11619', 'generator_key': 'src_11619', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11619, 'source_order': 11619, 'sampling_weight': 1.0}, {'textbook_example_id': 11620, 'component_id': 'src_11620', 'generator_key': 'src_11620', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11620, 'source_order': 11620, 'sampling_weight': 1.0}, {'textbook_example_id': 11624, 'component_id': 'src_11624', 'generator_key': 'src_11624', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11624, 'source_order': 11624, 'sampling_weight': 1.0}, {'textbook_example_id': 11625, 'component_id': 'src_11625', 'generator_key': 'src_11625', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sector_arc_and_area', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sector_arc_and_area', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 11625, 'source_order': 11625, 'sampling_weight': 1.0}]


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
