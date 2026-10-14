# -*- coding: utf-8 -*-
"""Short multipart stems flow inline: (1)/(2) markers never force a line break."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from core.gencode.resources.rational_display import sanitize_student_math_display_text

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "templates" / "index.html"

_HELPERS = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf8');
const start = html.indexOf('        const MULTIPART_MARKER =');
const end = html.indexOf('        function setQuestionDisplayText', start);
const api = new Function(html.slice(start, end) + '\nreturn {joinMultipartMarkerLines, findMultipartItemsStart};')();
const out = JSON.parse(process.argv[2]).map((text) => {
  const joined = api.joinMultipartMarkerLines(text);
  const at = api.findMultipartItemsStart(joined);
  return {joined, items: at < 0 ? null : joined.slice(at)};
});
process.stdout.write(JSON.stringify(out));
"""


def _node() -> str:
    node = shutil.which("node")
    if not node:
        candidates = sorted((Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe"))
        node = str(candidates[0]) if candidates else None
    if not node:
        pytest.skip("Node.js runtime is required for stem layout helpers")
    return node


def _layout(values: list[str]) -> list[dict]:
    completed = subprocess.run(
        [_node(), "-e", _HELPERS, str(INDEX), json.dumps(values, ensure_ascii=False)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_marker_line_breaks_become_inline_gaps() -> None:
    out = _layout([
        "設$f(x)=5x^{2} + 3x - 4$，利用餘式定理求：(1) 除以$x-1$的餘式 \n(2) 除以$x-3$的餘式",
        "解下列不等式：\n(1) \\(5 x + 6 < - 3 x - 26\\)\n(2) \\(\\frac{3 x}{2} > - x\\)",
        "因式分解下列多項式：(1)$x^{3} + 1$(2)$8x^{3} - 1$",
    ])
    assert out[0]["joined"] == "設$f(x)=5x^{2} + 3x - 4$，利用餘式定理求：(1) 除以$x-1$的餘式\u3000(2) 除以$x-3$的餘式"
    assert out[0]["items"] == "(1) 除以$x-1$的餘式\u3000(2) 除以$x-3$的餘式"
    assert out[1]["joined"] == "解下列不等式：(1) \\(5 x + 6 < - 3 x - 26\\)\u3000(2) \\(\\frac{3 x}{2} > - x\\)"
    assert out[2]["joined"] == "因式分解下列多項式：(1)$x^{3} + 1$\u3000(2)$8x^{3} - 1$"
    assert all("\n" not in row["joined"] for row in out)


def test_function_calls_math_and_paragraphs_are_not_treated_as_items() -> None:
    values = ["已知 f(1)=3，求 f(2)。", "第一段說明。\n第二段說明。", "滿足$f(-2)=f(1)=0$，且$f(4)=18$"]
    out = _layout(values + ["且$f\n(4)=18$，試求$f(x)$。"])
    assert [row["joined"] for row in out[:3]] == values
    assert all(row["items"] is None for row in out)
    assert out[3]["joined"] == "且$f (4)=18$，試求$f(x)$。"


def test_stem_renderer_and_css_use_inline_flow() -> None:
    html = INDEX.read_text(encoding="utf-8")
    css = re.sub(r"\s+", " ", html)
    stem_rule = re.search(r"\.multipart-stem \{([^}]*)\}", css).group(1)
    assert "flex-direction: column" not in stem_rule and "display: block" in stem_rule
    assert re.search(r"\.multipart-stem-prompt, \.multipart-stem-item \{ display: inline;", css)
    assert re.search(r"\.multipart-stem-items, \.question-multipart-items \{ display: inline-block; max-width: 100%;", css)
    body = html[html.index("function renderStructuredStem("):html.index("function showMissingQuestionTextError(")]
    assert "createElement('div');\n                    row" not in body
    assert "<br" not in body and "'\\n'" not in body
    setter = html[html.index("function setQuestionDisplayText("):html.index("function renderStructuredStem(")]
    assert "question_text" not in setter and ".length <" not in setter


def test_compact_stem_is_measured_bounded_and_desktop_only() -> None:
    html = INDEX.read_text(encoding="utf-8")
    body = html[html.index("function measureStemLayout("):html.index("function scheduleQuestionAnswerRowFit(")]
    assert "getBoundingClientRect" in body and "createRange" in body
    assert "question_text" not in body and "textContent.length" not in body
    assert "getComputedStyle(area).display !== 'grid'" in body
    assert "STEM_COMPACT_MAX_GAPS" in body and "STEM_COMPACT_MAX_DEFICIT" in body
    assert "if (!after.oneLine) reset();" in body
    consts = dict(re.findall(r"const (STEM_COMPACT_\w+) = ([\d.]+);", html))
    assert float(consts["STEM_COMPACT_MIN_SCALE"]) >= 0.92
    assert float(consts["STEM_COMPACT_MAX_DEFICIT"]) <= 0.12
    assert int(consts["STEM_COMPACT_MAX_GAPS"]) <= 2
    schedule = html[html.index("function scheduleQuestionAnswerRowFit("):]
    assert schedule.index("fitCompactStem();") < schedule.index("fitQuestionAnswerRow();")

    css = re.sub(r"\s+", " ", (ROOT / "static" / "css" / "practice_answer_layout.css").read_text(encoding="utf-8"))
    compact = re.search(r"@media \(min-width: 900px\) \{ \.practice-question-block > "
                        r"#question-container\.question-stem-compact \{(.*?)\} \}", css)
    assert compact, "compact stem must stay inside the desktop media query"
    assert "var(--stem-compact-scale, 1)" in compact.group(1)


def test_stem_sanitizer_keeps_generator_text_without_inserted_breaks() -> None:
    stem = "設$f(x)=2x^2$，滿足$f(3)=18$，試求：(1) $x+4$ (2) $x-1$"
    assert sanitize_student_math_display_text(stem, break_multipart_items=False) == stem
    # Non-stem display text keeps its existing formatting contract.
    assert sanitize_student_math_display_text("(1) 3 (2) 5") == "(1) 3 \n(2) 5"
