from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_QuadraticFunctionGraph'
GENERATOR_KEYS = ['src_4450', 'src_4460', 'src_4466', 'src_4503']
GENERATOR_SPECS = [{'textbook_example_id': 4450, 'component_id': 'src_4450', 'generator_key': 'src_4450', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_graph_translation_fill_blank', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'integer_quadratic_graph_translation_fill_blank', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4450, 'source_order': 4450, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4460, 'component_id': 'src_4460', 'generator_key': 'src_4460', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_graph_translation_fill_blank', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'integer_quadratic_graph_translation_fill_blank', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4460, 'source_order': 4460, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4466, 'component_id': 'src_4466', 'generator_key': 'src_4466', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_graph_translation_fill_blank', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'integer_quadratic_graph_translation_fill_blank', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4466, 'source_order': 4466, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4503, 'component_id': 'src_4503', 'generator_key': 'src_4503', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'quadratic_graph_properties_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'integer_quadratic_graph_properties_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4503, 'source_order': 4503, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]


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
