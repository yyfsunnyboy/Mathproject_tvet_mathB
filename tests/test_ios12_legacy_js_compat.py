"""Safari 12 (iOS 12.5.x) must still parse the bug-report widget and mistake-notebook scripts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(*parts: str) -> str:
    return ROOT.joinpath(*parts).read_text(encoding="utf-8").replace("\r\n", "\n")


WIDGET = _read("templates", "_bug_report_widget.html")
NOTEBOOK = _read("templates", "mistake_notebook.html")
POLYFILL = _read("static", "js", "legacy_dom_polyfills.js")
INLINE_SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
REGEX_PRECEDERS = set("(,=:[!&|?{};+-*%<>~^") | {""}


def _split_js(source: str) -> tuple[str, list[str]]:
    """Return (code without comments/literals, literal bodies) using a small lexical scanner."""
    code: list[str] = []
    literals: list[str] = []
    i, n = 0, len(source)
    brace_depth: list[int] = []
    last = ""
    while i < n:
        ch, nxt = source[i], source[i + 1] if i + 1 < n else ""
        if ch == "/" and nxt == "/":
            i = source.find("\n", i)
            i = n if i == -1 else i
            continue
        if ch == "/" and nxt == "*":
            i = source.find("*/", i + 2)
            i = n if i == -1 else i + 2
            continue
        if ch in "'\"" or (ch == "/" and last in REGEX_PRECEDERS) or ch == "`" or (ch == "}" and brace_depth and brace_depth[-1] == 0):
            if ch == "}":
                brace_depth.pop()
            quote = "`" if ch in "`}" else ch
            in_class = False
            start = i = i + 1
            while i < n:
                c = source[i]
                if c == "\\":
                    i += 2
                    continue
                if quote == "/" and c in "[]":
                    in_class = c == "["
                elif quote == "`" and c == "$" and source[i + 1 : i + 2] == "{":
                    literals.append(source[start:i])
                    brace_depth.append(0)
                    i += 2
                    break
                elif c == quote and not in_class:
                    literals.append(source[start:i])
                    i += 1
                    break
                i += 1
            code.append(" 0 ")
            last = "0"
            continue
        if brace_depth and ch == "{":
            brace_depth[-1] += 1
        elif brace_depth and ch == "}":
            brace_depth[-1] -= 1
        code.append(ch)
        if not ch.isspace():
            last = ch
        i += 1
    return "".join(code), literals


def _legacy_syntax_problems(source: str) -> list[str]:
    code, literals = _split_js(source)
    problems = []
    if re.search(r"\?\.(?!\d)", code):
        problems.append("optional chaining ?.")
    if "??" in code:
        problems.append("nullish coalescing ??")
    if any(re.search(r"\(\?<[=!]", body) for body in literals):
        problems.append("regex lookbehind")
    return problems


def _inline_scripts(html: str) -> list[str]:
    return [block for block in INLINE_SCRIPT.findall(html) if block.strip()]


def test_scanner_ignores_literals_and_comments_but_flags_code():
    assert _legacy_syntax_problems("const a = b?.c;") == ["optional chaining ?."]
    assert _legacy_syntax_problems("const a = b ?? c;") == ["nullish coalescing ??"]
    assert _legacy_syntax_problems("const r = /(?<=x)y/;") == ["regex lookbehind"]
    assert _legacy_syntax_problems("const a = `${b?.c}`;") == ["optional chaining ?."]
    assert _legacy_syntax_problems("const a = x ?.5 : 1; // b?.c ?? d\nconst s = 'e?.f ??';") == []


def test_bug_report_widget_has_no_safari12_parse_errors():
    scripts = _inline_scripts(WIDGET)
    assert scripts
    for script in scripts:
        assert _legacy_syntax_problems(script) == []


def test_bug_report_widget_only_calls_replace_children_behind_feature_check():
    script = "".join(_inline_scripts(WIDGET))
    helper = script.split("function replacePreview(", 1)[1].split("\n    }\n", 1)[0]
    assert "function imageFrom(" not in helper
    assert "typeof previewContainer.replaceChildren === 'function'" in helper
    assert script.count(".replaceChildren(") == helper.count(".replaceChildren(")


def test_mistake_notebook_scripts_parse_and_load_polyfill_first():
    for script in _inline_scripts(NOTEBOOK):
        assert _legacy_syntax_problems(script) == []
    scripts_block = NOTEBOOK.split("{% block scripts %}", 1)[1]
    polyfill_at = scripts_block.index("js/legacy_dom_polyfills.js")
    assert polyfill_at < scripts_block.index("js/math_display_normalizer.js")
    assert polyfill_at < scripts_block.index(".replaceChildren(")


def test_polyfill_is_es5_and_never_overrides_native():
    assert _legacy_syntax_problems(POLYFILL) == []
    code, _ = _split_js(POLYFILL)
    for modern in ("=>", "let ", "const ", "class "):
        assert modern not in code
    assert 'typeof ctor.prototype.replaceChildren === "function"' in POLYFILL
    assert "Document.prototype" not in POLYFILL
