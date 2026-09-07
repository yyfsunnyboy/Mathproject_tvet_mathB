# -*- coding: utf-8 -*-
"""Regression: interval-interpretation must keep symbolic a in |kx-a|."""
from __future__ import annotations

import importlib
import re

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

SKILL = "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
PT = "absolute_value_inequality_interval_interpretation"
QUADRANTS = {"第一象限", "第二象限", "第三象限", "第四象限"}

# |k x - a| < c ... b < x < u ... (b, a)
_STEM_RE = re.compile(
    r"\\left\|\s*(?P<k>\d+)x\s*-\s*a\s*\\right\|\s*<\s*(?P<c>\d+)"
    r".*?b\s*<\s*x\s*<\s*(?P<u>\d+)"
    r".*?\$\(\s*b\s*,\s*a\s*\)\$",
    re.S,
)


def _quadrant(b_value: int, a_value: int) -> str:
    if b_value > 0 and a_value > 0:
        return "第一象限"
    if b_value < 0 and a_value > 0:
        return "第二象限"
    if b_value < 0 and a_value < 0:
        return "第三象限"
    return "第四象限"


def _assert_interval_payload(q: dict, *, seed: int | None = None) -> None:
    qt = str(q.get("question_text") or "")
    assert qt, f"empty question_text seed={seed}"
    m = _STEM_RE.search(qt)
    assert m, f"stem must keep symbolic |kx-a| and (b,a); got={qt!r} seed={seed}"

    k = int(m.group("k"))
    c = int(m.group("c"))
    u = int(m.group("u"))

    givens = (q.get("metadata") or {}).get("givens") or {}
    a_value = int(givens["a_value"])
    b_value = int(givens["b_value"])

    # Solved numeric a must not be substituted into the absolute-value expression.
    assert f"{k}x - {a_value}" not in qt
    assert f"{k}x-{a_value}" not in qt
    assert f"{k}x + {abs(a_value)}" not in qt
    assert f"{k}x+{abs(a_value)}" not in qt

    expected_a = k * u - c
    expected_b = (expected_a - c) // k
    assert a_value == expected_a, f"a_value mismatch seed={seed}"
    assert b_value == expected_b, f"b_value mismatch seed={seed}"
    assert a_value != 0 and b_value != 0, f"axis point seed={seed}"

    choices = q.get("choices") or []
    texts = {str(ch.get("text") if isinstance(ch, dict) else ch) for ch in choices}
    assert texts == QUADRANTS, f"choices must be four quadrants; got={texts} seed={seed}"

    expected_quad = _quadrant(b_value, a_value)
    label = str(q.get("correct_answer") or q.get("answer") or "").strip()
    selected = next(
        ch for ch in choices if isinstance(ch, dict) and ch.get("label") == label
    )
    assert selected["text"] == expected_quad, f"quadrant mismatch seed={seed}"


def test_src_4416_keeps_symbolic_a() -> None:
    mod = importlib.import_module(
        f"agent_skills_v3.{SKILL}.components.src_4416.generate"
    )
    q = mod.generate(level=1, seed=1)
    _assert_interval_payload(q, seed=1)
    assert "| 7x - a |" in q["question_text"].replace("\\left|", "|").replace("\\right|", "|") or (
        "7x - a" in q["question_text"]
    )


def test_adapter_interval_interpretation_symbolic_structure() -> None:
    matrix = build_absolute_value_matrix(
        seed=42,
        line_type=PT,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
    )
    assert "a_value" in matrix["givens"]
    assert "b_value" in matrix["givens"]
    assert "a" not in matrix["givens"] or "a_value" in matrix["givens"]

    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="choice",
        problem_type_id=PT,
        component_id="src_4416",
        textbook_example_id=4416,
        domain_operation=PT,
        seed=42,
    )
    _assert_interval_payload(payload, seed=42)


def test_interval_interpretation_100_sample_regression() -> None:
    mod = importlib.import_module(
        f"agent_skills_v3.{SKILL}.components.src_4416.generate"
    )
    for seed in range(100):
        q = mod.generate(level=1, seed=seed)
        assert q.get("problem_type_id") == PT
        _assert_interval_payload(q, seed=seed)


def test_skill_forced_src_4416_100_samples() -> None:
    skill = importlib.import_module(f"skills.{SKILL}")
    for seed in range(100):
        q = skill.generate(level=1, seed=seed, component_id="src_4416")
        assert q.get("problem_type_id") == PT
        _assert_interval_payload(q, seed=seed)
