from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_TranslationOfALine'
GENERATOR_KEYS = ['src_12411', 'src_12412', 'src_12438']
GENERATOR_SPECS = [{'textbook_example_id': 12411, 'component_id': 'src_12411', 'generator_key': 'src_12411', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'translate_line_equation', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'translate_line_equation', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12411, 'source_order': 12411, 'sampling_weight': 10.0}, {'textbook_example_id': 12412, 'component_id': 'src_12412', 'generator_key': 'src_12412', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'translate_line_equation', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'translate_line_equation', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12412, 'source_order': 12412, 'sampling_weight': 10.0}, {'textbook_example_id': 12438, 'component_id': 'src_12438', 'generator_key': 'src_12438', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_translation_parameter', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_translation_parameter', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12438, 'source_order': 12438, 'sampling_weight': 10.0}]


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
