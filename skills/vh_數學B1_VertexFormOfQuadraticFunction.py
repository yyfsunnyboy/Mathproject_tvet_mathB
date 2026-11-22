from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_VertexFormOfQuadraticFunction'
GENERATOR_KEYS = ['src_4451', 'src_4452', 'src_4453', 'src_4456', 'src_4504']
GENERATOR_SPECS = [{'textbook_example_id': 4451, 'component_id': 'src_4451', 'generator_key': 'src_4451', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_graph_translation_fill_blank', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'text_quadratic_graph_translation_fill_blank_short_answer', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4451, 'source_order': 4451, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4452, 'component_id': 'src_4452', 'generator_key': 'src_4452', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_form_translation_to_new_function', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'text_quadratic_vertex_form_translation_to_new_function_short_answer', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4452, 'source_order': 4452, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4453, 'component_id': 'src_4453', 'generator_key': 'src_4453', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'quadratic_vertex_form_properties', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'single_choice_quadratic_vertex_form_properties_single_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4453, 'source_order': 4453, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4456, 'component_id': 'src_4456', 'generator_key': 'src_4456', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'numeric_quadratic_vertex_or_parameter_computation_short_answer', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4456, 'source_order': 4456, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4504, 'component_id': 'src_4504', 'generator_key': 'src_4504', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'numeric_quadratic_vertex_or_parameter_computation_single_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4504, 'source_order': 4504, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]


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
