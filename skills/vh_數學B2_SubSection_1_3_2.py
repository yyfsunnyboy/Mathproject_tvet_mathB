from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_1_3_2'
GENERATOR_KEYS = ['src_11628', 'src_11629', 'src_11646']
GENERATOR_SPECS = [{'textbook_example_id': 11628, 'component_id': 'src_11628', 'generator_key': 'src_11628', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'compute_terminal_ray_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_terminal_ray_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11628, 'source_order': 11628, 'sampling_weight': 1.0}, {'textbook_example_id': 11629, 'component_id': 'src_11629', 'generator_key': 'src_11629', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compute_terminal_ray_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_terminal_ray_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11629, 'source_order': 11629, 'sampling_weight': 1.0}, {'textbook_example_id': 11646, 'component_id': 'src_11646', 'generator_key': 'src_11646', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compute_terminal_ray_trig_ratios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_terminal_ray_trig_ratios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11646, 'source_order': 11646, 'sampling_weight': 1.0}]


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
