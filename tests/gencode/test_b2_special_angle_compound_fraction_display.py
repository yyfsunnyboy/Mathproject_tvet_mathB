# -*- coding: utf-8 -*-
from __future__ import annotations

from skills.vh_數學B2_TrigonometricValuesOfSpecialAngles import check, generate


def test_11578_stem_uses_stacked_displaystyle_fraction() -> None:
    payload = generate(level=1, seed=0, component_id="src_11578")
    stem = str(payload.get("question_text") or "")
    assert r"\displaystyle\frac" in stem
    assert r"\sin^{2}\left(\frac{\pi}{4}\right)" in stem
    assert "(1−sin²(π/4))/(1+sin²(π/4))" not in stem
    assert "(1-sin²(π/4))/(1+sin²(π/4))" not in stem
    assert r"\sin^{2}45^{\circ}" in stem or "sin²45" in stem


def test_11578_answers_and_checker_unchanged() -> None:
    payload = generate(level=1, seed=0, component_id="src_11578")
    answer = payload.get("correct_answer") or payload.get("answer")
    assert answer == {"part_1": "1/3", "part_2": "5"}
    assert check(answer, answer, question_payload=payload) is True
    assert (
        check({"part_1": "1/2", "part_2": "5"}, answer, question_payload=payload) is False
    )
