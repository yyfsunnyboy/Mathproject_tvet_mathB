from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_InterceptForm'
GENERATOR_KEYS = ['src_4547', 'src_4548', 'src_4555', 'src_4558', 'src_4559', 'src_4564', 'src_4604']
GENERATOR_SPECS = [{'textbook_example_id': 4547, 'component_id': 'src_4547', 'generator_key': 'src_4547', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4547', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4547, 'source_order': 4547, 'sampling_weight': 10.0}, {'textbook_example_id': 4548, 'component_id': 'src_4548', 'generator_key': 'src_4548', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4548', 'line_type': 'intercept_form_from_intercept_sum_and_slope', 'answer_type': 'expression', 'problem_type_id': 'intercept_form_from_intercept_sum_and_slope', 'display_order': 4548, 'source_order': 4548, 'sampling_weight': 10.0}, {'textbook_example_id': 4555, 'component_id': 'src_4555', 'generator_key': 'src_4555', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4555', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4555, 'source_order': 4555, 'sampling_weight': 10.0}, {'textbook_example_id': 4558, 'component_id': 'src_4558', 'generator_key': 'src_4558', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4558', 'line_type': 'triangle_area_bisector_line_equation', 'answer_type': 'linear_equation', 'problem_type_id': 'triangle_area_bisector_line_equation', 'display_order': 4558, 'source_order': 4558, 'sampling_weight': 10.0}, {'textbook_example_id': 4559, 'component_id': 'src_4559', 'generator_key': 'src_4559', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4559', 'line_type': 'parabola_secant_parallel_line_choice', 'answer_type': 'single_choice', 'problem_type_id': 'parabola_secant_parallel_line_choice', 'display_order': 4559, 'source_order': 4559, 'sampling_weight': 10.0}, {'textbook_example_id': 4564, 'component_id': 'src_4564', 'generator_key': 'src_4564', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4564', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4564, 'source_order': 4564, 'sampling_weight': 10.0}, {'textbook_example_id': 4604, 'component_id': 'src_4604', 'generator_key': 'src_4604', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4604', 'line_type': 'intercept_form_triangle_area', 'answer_type': 'single_choice', 'problem_type_id': 'intercept_form_triangle_area', 'display_order': 4604, 'source_order': 4604, 'sampling_weight': 10.0}]


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
