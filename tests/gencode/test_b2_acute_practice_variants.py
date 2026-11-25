# -*- coding: utf-8 -*-
from __future__ import annotations

import re

from skills.vh_數學B2_TrigonometricFunctionsOfAcuteAngles import generate


def _nums(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\d+", text))


def test_cable_projection_varies_by_seed_and_keeps_structure() -> None:
    payloads = [generate(level=1, seed=seed, component_id="src_11584") for seed in range(30)]
    stems = {str(p.get("question_text") or "") for p in payloads}
    params = {_nums(str(p.get("question_text") or "")) for p in payloads}
    assert len(stems) >= 8
    assert len(params) >= 8
    # seed 0 keeps textbook instance
    t0 = str(generate(level=1, seed=0, component_id="src_11584").get("question_text") or "")
    assert "900" in t0 and "45" in t0 and "500" in t0
    for payload in payloads:
        qt = str(payload.get("question_text") or "")
        assert "纜車站" in qt and "仰角" in qt
        visual = payload.get("visual_spec") or {}
        assert visual.get("kind") == "coordinate_plane"
        assert visual.get("required") is True
        labels = " ".join(
            str(item.get("label") or "")
            for item in list(visual.get("points") or []) + list(visual.get("lines") or [])
        )
        nums = _nums(qt)
        # Stem numbers must appear on the diagram (figure/text sync gate).
        for token in nums[:3]:
            assert token in labels
        parts = (payload.get("answer_contract") or {}).get("parts") or []
        assert {str(p.get("key")) for p in parts} >= {"elevation", "horizontal_projection"}


def test_four_acute_types_have_seed_variation_or_documented_pool() -> None:
    # Representative component per runtime problem_type.
    cases = {
        "compute_right_triangle_trig_ratios": "src_11557",
        "solve_acute_trig_constraints": "src_11558",
        "simplify_fundamental_trig_expression": "src_11581",
        "solve_right_triangle_projection": "src_11584",
    }
    for pt, cid in cases.items():
        stems = {
            str(generate(level=1, seed=seed, component_id=cid).get("question_text") or "")
            for seed in range(30)
        }
        assert len(stems) >= 3, (pt, cid, len(stems))
