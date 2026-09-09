from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_TrigonometricValuesOfSpecialAngles'
GENERATOR_KEYS = ['src_11559', 'src_11560', 'src_11569', 'src_11570', 'src_11578', 'src_11584']
GENERATOR_SPECS = [{'textbook_example_id': 11559, 'component_id': 'src_11559', 'generator_key': 'src_11559', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'evaluate_exact_special_angle_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_special_angle_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11559, 'source_order': 11559, 'sampling_weight': 1.0}, {'textbook_example_id': 11560, 'component_id': 'src_11560', 'generator_key': 'src_11560', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'solve_right_triangle_projection', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_right_triangle_projection', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11560, 'source_order': 11560, 'sampling_weight': 1.0}, {'textbook_example_id': 11569, 'component_id': 'src_11569', 'generator_key': 'src_11569', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_special_angle_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_special_angle_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11569, 'source_order': 11569, 'sampling_weight': 1.0}, {'textbook_example_id': 11570, 'component_id': 'src_11570', 'generator_key': 'src_11570', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_right_triangle_projection', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_right_triangle_projection', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11570, 'source_order': 11570, 'sampling_weight': 1.0}, {'textbook_example_id': 11578, 'component_id': 'src_11578', 'generator_key': 'src_11578', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_exact_special_angle_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_exact_special_angle_expression', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11578, 'source_order': 11578, 'sampling_weight': 1.0}, {'textbook_example_id': 11584, 'component_id': 'src_11584', 'generator_key': 'src_11584', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'solve_right_triangle_projection', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_right_triangle_projection', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11584, 'source_order': 11584, 'sampling_weight': 1.0}]


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
