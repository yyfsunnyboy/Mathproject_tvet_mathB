"""Regression coverage for trusted textbook LaTeX on shared skill cards."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "instance" / "kumon_math.db"


def _real_vocational_descriptions() -> dict[str, str]:
    if not DATABASE.exists():
        pytest.skip("the checked-in vocational catalog database is unavailable")
    connection = sqlite3.connect(f"file:{DATABASE.as_posix()}?mode=ro", uri=True)
    try:
        return dict(
            connection.execute(
                "SELECT skill_id, description FROM skills_info "
                "WHERE skill_id LIKE 'vh_%' AND is_active = 1"
            )
        )
    finally:
        connection.close()


def test_real_trigonometry_descriptions_keep_single_escape_latex_and_delimiters():
    descriptions = _real_vocational_descriptions()
    expected = {
        "vh_數學B2_RatioAndRatioValue": (r"\sin", r"\frac", r"\text{對邊}"),
        "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": (r"\theta", r"\cos", r"\tan"),
        "vh_數學B2_TrigonometricValuesOfSpecialAngles": (r"\sqrt{2}", r"^\circ", r"\frac{1}{2}"),
        "vh_數學B2_FundamentalTrigonometricIdentities": (r"\sin^2", r"\theta", r"\frac"),
    }
    for skill_id, commands in expected.items():
        description = descriptions[skill_id]
        assert all(command in description for command in commands)
        assert description.count("$") % 2 == 0
        assert r"\cic" not in description
        assert r"\\" not in description


def test_real_catalog_has_card_descriptions_for_each_vocational_volume():
    descriptions = _real_vocational_descriptions()
    for volume in ("數學B1", "數學B2", "數學B3", "數學B4"):
        assert any(
            skill_id.startswith(f"vh_{volume}_") and description
            for skill_id, description in descriptions.items()
        )


def test_shared_renderer_configures_mathjax_v3_and_safe_dynamic_card_typesetting():
    renderer = (ROOT / "templates/partials/skill_card_math_renderer.html").read_text(encoding="utf-8")
    assert "inlineMath: [['$', '$'], ['\\\\(', '\\\\)']]" in renderer
    assert "displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]" in renderer
    assert "typesetPromise(targets)" in renderer
    assert "typesetClear(targets)" in renderer
    assert "MutationObserver" in renderer
    assert ".skill-card-description" in renderer
    assert "innerHTML" not in renderer


def test_shared_skill_card_keeps_jinja_autoescape_and_all_card_pages_use_renderer():
    card = (ROOT / "templates/partials/skill_card.html").read_text(encoding="utf-8")
    assert 'class="skill-card-description"' in card
    assert "{{ skill_card.description }}" in card
    assert "description|safe" not in card

    for template in (
        "templates/dashboard.html",
        "templates/vocational_student_home.html",
        "templates/vocational_mock_exam_scope.html",
    ):
        assert "include 'partials/skill_card_math_renderer.html'" in (ROOT / template).read_text(
            encoding="utf-8"
        )
