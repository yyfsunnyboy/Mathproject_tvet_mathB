from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_HorizontalAndVerticalLineEquations'
GENERATOR_KEYS = ['src_4544']
GENERATOR_SPECS = [{'textbook_example_id': 4544, 'component_id': 'src_4544', 'generator_key': 'src_4544', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4544', 'line_type': 'vertical_line'}]
V3_PACKAGE_ROOT = 'E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_v3_publish_staging\\hv_line_publish\\agent_skills_v3'


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
        v3_package_root=V3_PACKAGE_ROOT,
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
        v3_package_root=V3_PACKAGE_ROOT,
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=V3_PACKAGE_ROOT,
        skill_id=SKILL_ID,
    )
