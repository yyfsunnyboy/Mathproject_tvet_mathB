# -*- coding: utf-8 -*-
"""Shared student-practice inline math typography contract regressions."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static" / "css" / "practice_math_typography.css").read_text(encoding="utf-8")
INDEX = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
CONTRACT = (ROOT / "docs" / "VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md").read_text(encoding="utf-8")


def test_practice_page_links_shared_typography_css():
    assert "practice_math_typography.css" in INDEX
    assert "tex-svg.js" in INDEX
    # Practice page must not load KaTeX alongside MathJax for stems.
    assert "katex.min" not in INDEX.lower()
    assert "cdn.jsdelivr.net/npm/katex" not in INDEX.lower()


def test_practice_surfaces_use_canonical_wrapper_class():
    for element_id in ("question-text", "question-choices", "subquestions-container", "result-display"):
        anchor = INDEX.find(f'id="{element_id}"')
        assert anchor >= 0, element_id
        window = INDEX[anchor : anchor + 140]
        assert "practice-math-surface" in window, window


def test_css_contract_forbids_middle_baseline_override():
    # Strip block comments so documentation prose does not trip the rule.
    css_code = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    assert "vertical-align: middle" not in css_code
    assert "font-size: 100%" in CSS
    assert "line-height: 1.75" in CSS


def test_no_practice_mjx_middle_important_in_index():
    for match in re.finditer(
        r"mjx-container[^{]*\{[^}]*vertical-align\s*:\s*middle\s*!important",
        INDEX,
        flags=re.I | re.S,
    ):
        snippet = INDEX[max(0, match.start() - 100) : match.end() + 40]
        assert "suggestion-btn" in snippet, snippet


def test_runtime_contract_documents_inline_math_typography():
    assert "9.3 Student-facing inline math typography" in CONTRACT
    assert "practice-math-surface" in CONTRACT
    assert "vertical-align: middle !important" in CONTRACT


def test_numeric_display_cleanup_still_works():
    from core.gencode.resources.rational_display import (
        latex_coeff_times_symbol,
        sanitize_student_math_display_text,
    )

    assert sanitize_student_math_display_text("4.000000000000000") == "4"
    assert latex_coeff_times_symbol(1, r"\vec{a}") == r"\vec{a}"
    assert (ROOT / "static" / "js" / "math_display_normalizer.js").is_file()
    assert (ROOT / "static" / "js" / "choice_math.js").is_file()


def test_audit_script_reports_clean_chapter():
    from scripts.audit_b2_ch3_math_typography import main
    import io
    import sys

    buf = io.StringIO()
    old = sys.stdout
    try:
        sys.stdout = buf
        main()
    finally:
        sys.stdout = old
    out = buf.getvalue()
    assert '"pass": true' in out or '"pass":true' in out
