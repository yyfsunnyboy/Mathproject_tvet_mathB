# -*- coding: utf-8 -*-
"""Practice-runtime integration tests for published parallel/perpendicular V3 skills."""

from __future__ import annotations

from core.legacy_generator_adapter import invoke_skill_generate
from core.routes.practice import get_skill, _finalize_practice_question_api_fields

PARALLEL_SKILL = "vh_數學B1_PropertiesOfParallelLines"
PERP_SKILL = "vh_數學B1_PropertiesOfPerpendicularLines"


def _generate(skill_id: str, component_id: str, seed: int = 7) -> dict:
    mod = get_skill(skill_id)
    assert mod is not None
    payload = invoke_skill_generate(
        mod,
        level=1,
        seed=seed,
        component_id=component_id,
        skill_id=skill_id,
    )
    return _finalize_practice_question_api_fields(payload, skill_id=skill_id)


def _handwriting_enabled(payload: dict) -> bool:
    ui = (payload.get("answer_contract") or {}).get("ui_contract") or payload.get("ui_contract") or {}
    return bool(ui.get("handwriting_enabled"))


def test_parallel_skill_runtime_components():
    for component_id in ("src_4530", "src_4600"):
        payload = _generate(PARALLEL_SKILL, component_id)
        assert payload.get("question_text")
        assert payload.get("correct_answer") is not None
        assert _handwriting_enabled(payload)


def test_perpendicular_skill_runtime_components():
    for component_id in ("src_4526", "src_4527", "src_4538"):
        payload = _generate(PERP_SKILL, component_id)
        assert payload.get("question_text")
        assert payload.get("correct_answer") is not None
        assert _handwriting_enabled(payload)
