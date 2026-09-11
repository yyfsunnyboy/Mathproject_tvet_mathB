from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = ROOT / "static" / "js" / "math_display_normalizer.js"


def _normalize(values: list[str]) -> list[str]:
    script = (
        "const n=require(process.argv[1]);"
        "const values=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(values.map(v=>n.normalizeMathText(v))));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(NORMALIZER), json.dumps(values, ensure_ascii=False)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_slash_pi_negative_parenthesized_and_trig_fractions_become_latex():
    assert _normalize(["3/5", "19π/4", "-5π/6", "(3/4)π", "-(3/5)", "sin(19π/4)"]) == [
        r"\(\frac{3}{5}\)", r"\(\frac{19\pi}{4}\)", r"\(-\frac{5\pi}{6}\)",
        r"\(\frac{3}{4}\pi\)", r"\(-\frac{3}{5}\)",
        r"\(\sin\left(\frac{19\pi}{4}\right)\)",
    ]


def test_existing_latex_is_preserved():
    existing = r"\(\frac{3\pi}{4}\)"
    assert _normalize([existing]) == [existing]


def test_ascii_sympy_pi_fractions_use_stacked_latex_without_touching_paths():
    assert _normalize(["2*pi/3", "-pi/2", "sin(3*pi/4)"]) == [
        r"\(\frac{2\pi}{3}\)", r"\(-\frac{\pi}{2}\)",
        r"\(\sin\left(\frac{3\pi}{4}\right)\)",
    ]


def test_plain_dates_urls_and_paths_are_not_converted():
    values = ["日期 2026/9/11", "https://example.test/a/3/5", r"C:\tmp\3/5", "純文字說明"]
    assert _normalize(values) == values


def test_practice_question_subquestion_and_table_paths_use_shared_normalizer():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement(element" in source
    assert "MathDisplayNormalizer.normalizeMathText(text" in source
    assert "renderMathContent(subquestionsContainer)" in source


def test_adaptive_question_choice_and_hint_typesetting_uses_shared_normalizer():
    source = (ROOT / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement(element" in source
    assert "await typesetMath(choiceList)" in source
    assert "await typesetMath(hintBox)" in source


def test_correct_answer_display_delegates_to_shared_normalizer_and_mathjax():
    source = (ROOT / "static" / "js" / "correct_answer_feedback.js").read_text(encoding="utf-8")
    assert "MathDisplayNormalizer.normalizeMathText" in source
    assert "MathJax.typesetPromise" in source


def test_textbook_example_preview_uses_same_shared_renderer():
    source = (ROOT / "templates" / "admin_v3_example_preview.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement" in source
    assert "await triggerMathJax([contentBlock])" in source
