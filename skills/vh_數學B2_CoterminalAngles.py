from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_CoterminalAngles'
GENERATOR_KEYS = ['src_11611', 'src_11613']
GENERATOR_SPECS = [{'textbook_example_id': 11611, 'component_id': 'src_11611', 'generator_key': 'src_11611', 'presentation_mode': 'multiple_inputs', 'response_mode': 'selection', 'interaction_type': 'selection', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'coterminal_angles', 'display_order': 11611, 'source_order': 11611, 'sampling_weight': 10.0}, {'textbook_example_id': 11613, 'component_id': 'src_11613', 'generator_key': 'src_11613', 'presentation_mode': 'multiple_inputs', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'coterminal_angles', 'display_order': 11613, 'source_order': 11613, 'sampling_weight': 10.0}]


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
