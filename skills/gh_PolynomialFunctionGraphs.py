from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_PolynomialFunctionGraphs'
GENERATOR_KEYS = ['src_12629', 'src_12630']
GENERATOR_SPECS = [{'textbook_example_id': 12629, 'component_id': 'src_12629', 'generator_key': 'src_12629', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_graph_solutions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_graph_solutions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12629, 'source_order': 12629, 'sampling_weight': 10.0}, {'textbook_example_id': 12630, 'component_id': 'src_12630', 'generator_key': 'src_12630', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_graph_solutions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_graph_solutions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12630, 'source_order': 12630, 'sampling_weight': 10.0}]


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
