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


def test_practice_title_hides_technical_skill_id_when_chinese_name_exists():
    # Keep classroom title as skill_ch_name; only fall back to mangled skill_id.
    assert "skill_ch_name or skill_id" in INDEX
    assert "not skill_ch_name or skill_ch_name == skill_id" in INDEX


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


def test_stem_ascii_sqrt_inside_math_delimiters_becomes_latex():
    from core.gencode.resources.rational_display import (
        sanitize_student_math_display_text,
        upgrade_ascii_sqrt_inside_math_delimiters,
    )

    stem = r"在△ABC中，已知兩邊長分別為 $sqrt(3)$、6，夾角為 $120^\circ$，試求△ABC的面積。"
    cleaned = sanitize_student_math_display_text(stem, break_multipart_items=False)
    assert "sqrt(" not in cleaned
    assert r"$\sqrt{3}$" in cleaned
    assert r"$120^\circ$" in cleaned
    assert upgrade_ascii_sqrt_inside_math_delimiters(r"已是 $\sqrt{5}$") == r"已是 $\sqrt{5}$"


def test_stem_ascii_multiply_inside_math_delimiters_becomes_latex():
    from core.gencode.resources.rational_display import (
        sanitize_student_math_display_text,
        upgrade_ascii_sqrt_inside_math_delimiters,
    )

    cleaned = sanitize_student_math_display_text(
        r"△ABC中，已知$a=3*sqrt(2)$，$b=3$，試求$\angle B$。",
        break_multipart_items=False,
    )
    assert "*" not in cleaned
    assert "sqrt(" not in cleaned
    assert r"$a=3\sqrt{2}$" in cleaned
    assert r"$\angle B$" in cleaned

    frac = upgrade_ascii_sqrt_inside_math_delimiters(r"面積為 $3*sqrt(3)/2$")
    assert "*" not in frac
    assert r"$\frac{3\sqrt{3}}{2}$" in frac

    unicode_mul = upgrade_ascii_sqrt_inside_math_delimiters(r"$3 * √3/2$")
    assert "*" not in unicode_mul
    assert "√" not in unicode_mul
    assert r"$\frac{3\sqrt{3}}{2}$" in unicode_mul

    # Prose asterisks outside math delimiters must stay untouched.
    prose = upgrade_ascii_sqrt_inside_math_delimiters("請注意 * 號僅供參考，答案為 4")
    assert " * " in prose


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
