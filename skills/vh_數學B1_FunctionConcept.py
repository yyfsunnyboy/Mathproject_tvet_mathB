from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_FunctionConcept'
GENERATOR_KEYS = ['src_4430', 'src_4431']
GENERATOR_SPECS = [{'textbook_example_id': 4430, 'component_id': 'src_4430', 'generator_key': 'src_4430', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'free_fall_function_value_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'free_fall_function_value_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4430, 'source_order': 4430, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4431, 'component_id': 'src_4431', 'generator_key': 'src_4431', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'piecewise_utility_bill_savings_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'piecewise_utility_bill_savings_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4431, 'source_order': 4431, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]


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
