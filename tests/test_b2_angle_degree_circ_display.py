"""Degree stems must use ^\\circ so MathJax renders a true degree mark."""

from __future__ import annotations

import importlib
import re

from core.domain.trigonometry_angle_domain import build_trigonometry_angle_matrix
from core.legacy_generator_adapter import normalize_runtime_value

_BAD_BARE_CIRC = re.compile(r"\$[^$]*[^.^]\\circ\$")
_GOOD_SUP_CIRC = re.compile(r"\^\s*\\circ")


def test_deg_to_rad_list_uses_superscript_circ() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=30,
        domain_operation="convert_angle_measure",
        constraints={"variant": "deg_to_rad_list"},
    )
    question = str((matrix.get("givens") or {}).get("question_text") or "")
    assert "化為弧度" in question
    assert "-570" in question
    assert r"^\circ" in question
    assert _GOOD_SUP_CIRC.search(question), question
    assert _BAD_BARE_CIRC.search(question) is None, question


def test_two_way_convert_keeps_superscript_circ() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=30,
        domain_operation="convert_angle_measure",
        constraints={"variant": "two_way"},
    )
    question = str((matrix.get("givens") or {}).get("question_text") or "")
    assert r"^\circ" in question
    assert "化為弧度" in question


def test_runtime_src_11617_deg_list_display_and_answers_stable() -> None:
    mod = importlib.import_module(
        "agent_skills_v3.vh_數學B2_AngleMeasurementAndConversion.components.src_11617.generate"
    )
    payload = normalize_runtime_value(mod.generate(level=1, seed=30))
    question = str(payload.get("question") or payload.get("question_text") or "")
    assert r"^\circ" in question
    assert _BAD_BARE_CIRC.search(question) is None
    ac = payload.get("answer_contract") or {}
    parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
    assert parts, "multipart parts required"
    # Checker contract unchanged: expression parts with expected answers present
    for part in parts:
        assert part.get("expected_answer") not in (None, "")
        assert "circ" not in str(part.get("expected_answer"))
