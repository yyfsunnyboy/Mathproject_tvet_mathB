"""Shared math-input normalization for deterministic answer checkers.

Converts keyboard / LaTeX / handwriting-OCR notation into one plain-text
form so every checker family parses the same mathematical content the same
way.  Nothing here decides correctness; it only removes notation noise.
"""
from __future__ import annotations

import re
import unicodedata
from fractions import Fraction

_SUPERSCRIPTS = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁻": "-", "⁺": "+", "⁽": "(", "⁾": ")", "ⁿ": "n",
}
_SUBSCRIPTS = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
}
_SUPERSCRIPT_RUN = re.compile("[" + "".join(_SUPERSCRIPTS) + "]+")
_SUBSCRIPT_RUN = re.compile("[" + "".join(_SUBSCRIPTS) + "]+")

_UNICODE_MAP = {
    "\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2010": "-", "\u2011": "-",
    "\u2044": "/", "\u2215": "/",
    "≦": "≤", "⩽": "≤", "≧": "≥", "⩾": "≥",
    "×": "*", "·": "*", "⋅": "*", "∙": "*", "÷": "/",
    "【": "[", "】": "]", "〔": "(", "〕": ")",
}

_FRAC_CMD = re.compile(r"\\[dtc]?frac(?![A-Za-z])")
_SQRT_CMD = re.compile(r"\\sqrt(?![A-Za-z])")
_TEXT_CMD = re.compile(
    r"\\(?:text|textrm|textnormal|mathrm|mathit|mathbf|textbf|mbox|operatorname)(?![A-Za-z])"
)
_REALS_CMD = re.compile(r"\\(?:mathbb|mathbf|Bbb)\s*\{\s*R\s*\}|\\(?:mathbb|Bbb)\s*R(?![A-Za-z])")
_SIZING_CMD = re.compile(r"\\(?:left|right|bigl|bigr|Bigl|Bigr|biggl|biggr|big|Big|bigg|Bigg)(?![A-Za-z])")
_DEGREE_CMD = re.compile(r"\{\}\s*\^\s*\\circ|\^\s*\{\s*\\circ\s*\}|\^\s*\\circ|\\circ(?![A-Za-z])|\\degree(?![A-Za-z])")
_SPACING_CMD = re.compile(r"\\(?:quad|qquad)(?![A-Za-z])|\\[,;:! ]")

# Longer names first; the negative lookahead keeps \in from eating \infty.
_SYMBOL_COMMANDS = (
    ("infty", "∞"), ("infin", "∞"),
    ("leqslant", "≤"), ("leq", "≤"), ("le", "≤"),
    ("geqslant", "≥"), ("geq", "≥"), ("ge", "≥"),
    ("lt", "<"), ("gt", ">"), ("neq", "≠"), ("ne", "≠"),
    ("cup", "∪"), ("cap", "∩"), ("in", "∈"),
    ("pm", "±"), ("mp", "∓"),
    ("cdot", "*"), ("times", "*"), ("div", "/"),
    ("emptyset", "∅"), ("varnothing", "∅"),
    ("mid", "|"), ("vert", "|"), ("lvert", "|"), ("rvert", "|"),
    ("lbrace", "{"), ("rbrace", "}"), ("colon", ":"),
)
_SYMBOL_RE = re.compile(
    r"\\(" + "|".join(name for name, _ in _SYMBOL_COMMANDS) + r")(?![A-Za-z])"
)
_SYMBOL_LOOKUP = dict(_SYMBOL_COMMANDS)


def _skip_spaces(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def _read_group(s: str, i: int, *, allow_bare: bool) -> tuple[str | None, int]:
    """Read a `{...}` group (brace-balanced) or, if allowed, one bare token."""
    i = _skip_spaces(s, i)
    if i >= len(s):
        return None, i
    if s[i] == "{":
        depth = 0
        for j in range(i, len(s)):
            if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
                depth += 1
            elif s[j] == "}" and (j == 0 or s[j - 1] != "\\"):
                depth -= 1
                if depth == 0:
                    return s[i + 1 : j], j + 1
        return None, i
    if not allow_bare:
        return None, i
    if s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        if m:
            return m.group(0), i + m.end()
        return None, i
    if s[i] in "}":
        return None, i
    return s[i], i + 1


def _convert_groups(s: str) -> str:
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        m = _FRAC_CMD.match(s, i)
        if m:
            num, j = _read_group(s, m.end(), allow_bare=True)
            den, k = _read_group(s, j, allow_bare=True) if num is not None else (None, j)
            if num is not None and den is not None:
                out.append(f"(({_convert_groups(num)})/({_convert_groups(den)}))")
                i = k
                continue
        m = _SQRT_CMD.match(s, i)
        if m:
            j = _skip_spaces(s, m.end())
            index = None
            if j < n and s[j] == "[":
                close = s.find("]", j)
                if close > j:
                    index = s[j + 1 : close].strip()
                    j = close + 1
            if index is None and j < n and s[j] == "(":
                out.append("sqrt")
                i = j
                continue
            digits = re.match(r"\d+(?:\.\d+)?", s[j:]) if index is None else None
            if digits:
                out.append(f"sqrt({digits.group(0)})")
                i = j + digits.end()
                continue
            radicand, k = _read_group(s, j, allow_bare=True)
            if radicand is not None:
                inner = _convert_groups(radicand)
                if index:
                    out.append(f"(({inner})^(1/({_convert_groups(index)})))")
                else:
                    out.append(f"sqrt({inner})")
                i = k
                continue
        m = _TEXT_CMD.match(s, i)
        if m:
            body, k = _read_group(s, m.end(), allow_bare=False)
            if body is not None:
                out.append(_convert_groups(body))
                i = k
                continue
        if s[i] in "^_" and i + 1 < n:
            j = _skip_spaces(s, i + 1)
            if j < n and s[j] == "{":
                body, k = _read_group(s, j, allow_bare=False)
                if body is not None:
                    inner = _convert_groups(body)
                    out.append(f"^({inner})" if s[i] == "^" else f"_{inner}")
                    i = k
                    continue
        out.append(s[i])
        i += 1
    return "".join(out)


def latex_to_plain(text: object) -> str:
    """Normalize LaTeX / unicode math notation to plain keyboard notation.

    `\\frac{a}{b}` -> `((a)/(b))`, `\\infty` -> `∞`, `\\le` -> `≤`,
    `x²` -> `x^(2)`, `\\text{或}` -> `或`, `\\left( ... \\right)` -> `( ... )`.
    Unknown commands are left untouched for the caller to handle.
    """
    s = str(text if text is not None else "").strip()
    if not s:
        return ""
    s = _SUPERSCRIPT_RUN.sub(lambda m: "^(" + "".join(_SUPERSCRIPTS[c] for c in m.group(0)) + ")", s)
    s = _SUBSCRIPT_RUN.sub(lambda m: "_" + "".join(_SUBSCRIPTS[c] for c in m.group(0)), s)
    s = unicodedata.normalize("NFKC", s)
    for src, dst in _UNICODE_MAP.items():
        s = s.replace(src, dst)
    s = s.replace("$", "")
    s = _SIZING_CMD.sub("", s)
    s = s.replace(r"\{", "{").replace(r"\}", "}")
    s = s.replace(r"\(", "").replace(r"\)", "").replace(r"\[", "").replace(r"\]", "")
    s = _REALS_CMD.sub("ℝ", s)
    s = _DEGREE_CMD.sub("°", s)
    s = _convert_groups(s)
    s = _SPACING_CMD.sub(" ", s)
    s = _SYMBOL_RE.sub(lambda m: _SYMBOL_LOOKUP[m.group(1)], s)
    return re.sub(r"\s+", " ", s).strip()


class _ExactNumberParser:
    """value := sign* primary ('/' sign* primary)* ; primary := number | '(' value ')'."""

    _NUMBER = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)")

    def __init__(self, text: str) -> None:
        self.s = text
        self.i = 0

    def parse(self) -> Fraction | None:
        value = self._value()
        if value is None or self.i != len(self.s):
            return None
        return value

    def _signed(self) -> Fraction | None:
        sign = 1
        while self.i < len(self.s) and self.s[self.i] in "+-":
            if self.s[self.i] == "-":
                sign = -sign
            self.i += 1
        primary = self._primary()
        return None if primary is None else sign * primary

    def _value(self) -> Fraction | None:
        acc = self._signed()
        while acc is not None and self.i < len(self.s) and self.s[self.i] == "/":
            self.i += 1
            den = self._signed()
            if den is None or den == 0:
                return None
            acc = acc / den
        return acc

    def _primary(self) -> Fraction | None:
        if self.i >= len(self.s):
            return None
        if self.s[self.i] == "(":
            self.i += 1
            inner = self._value()
            if inner is None or self.i >= len(self.s) or self.s[self.i] != ")":
                return None
            self.i += 1
            return inner
        m = self._NUMBER.match(self.s, self.i)
        if not m:
            return None
        self.i = m.end()
        return Fraction(m.group(0))


def parse_exact_number(text: object) -> Fraction | None:
    """Parse a single exact rational written as int / decimal / fraction / LaTeX fraction.

    Accepts `22/7`, `\\frac{22}{7}`, `-\\frac{5}{3}`, `\\frac{-5}{3}`, `2/-3`, `3.5`,
    `((−5)/(3))`.  Returns None for anything else (including expressions with
    `+`, `*`, variables or radicals), so callers keep their own strict paths.
    """
    if isinstance(text, bool):
        return None
    if isinstance(text, int):
        return Fraction(text, 1)
    if isinstance(text, Fraction):
        return text
    s = latex_to_plain(text)
    s = re.sub(r"\s+", "", s)
    if not s:
        return None
    try:
        return _ExactNumberParser(s).parse()
    except (ValueError, ZeroDivisionError):
        return None
