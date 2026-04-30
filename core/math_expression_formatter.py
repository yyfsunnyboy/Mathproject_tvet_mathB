# -*- coding: utf-8 -*-
"""Standardize textbook problem text into stable inline LaTeX math expressions."""

from __future__ import annotations

import re
from typing import Any


INLINE_MATH_RE = re.compile(r"\\\((.*?)\\\)")
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]")
DOLLAR_MATH_RE = re.compile(r"\$(.+?)\$")


def _wrap_inline(expr: str) -> str:
    s = str(expr or "").strip()
    if not s:
        return s
    if s.startswith(r"\(") and s.endswith(r"\)"):
        return s
    return rf"\({s}\)"


def standardize_permutation_notation(expr: str) -> str:
    s = str(expr or "")
    # Keep already standardized form
    s = re.sub(r"\{\}\s*\^\s*\{([A-Za-z0-9]+)\}\s*P\s*_\s*\{([A-Za-z0-9]+)\}", r"{}^{\1}P_{\2}", s)
    # P(n,r)
    s = re.sub(r"\bP\s*\(\s*([A-Za-z0-9]+)\s*,\s*([A-Za-z0-9]+)\s*\)", r"{}^{\1}P_{\2}", s)
    # P^n_r / P_r^n
    s = re.sub(r"\bP\s*\^\s*\{?([A-Za-z0-9]+)\}?\s*_\s*\{?([A-Za-z0-9]+)\}?", r"{}^{\1}P_{\2}", s)
    s = re.sub(r"\bP\s*_\s*\{?([A-Za-z0-9]+)\}?\s*\^\s*\{?([A-Za-z0-9]+)\}?", r"{}^{\2}P_{\1}", s)
    return s


def standardize_combination_notation(expr: str) -> str:
    s = str(expr or "")
    s = re.sub(r"\{\}\s*\^\s*\{([A-Za-z0-9]+)\}\s*C\s*_\s*\{([A-Za-z0-9]+)\}", r"{}^{\1}C_{\2}", s)
    s = re.sub(r"\bC\s*\(\s*([A-Za-z0-9]+)\s*,\s*([A-Za-z0-9]+)\s*\)", r"{}^{\1}C_{\2}", s)
    s = re.sub(r"\bC\s*\^\s*\{?([A-Za-z0-9]+)\}?\s*_\s*\{?([A-Za-z0-9]+)\}?", r"{}^{\1}C_{\2}", s)
    s = re.sub(r"\bC\s*_\s*\{?([A-Za-z0-9]+)\}?\s*\^\s*\{?([A-Za-z0-9]+)\}?", r"{}^{\2}C_{\1}", s)
    return s


def _standardize_general_math(expr: str) -> str:
    s = str(expr or "")
    s = standardize_permutation_notation(s)
    s = standardize_combination_notation(s)
    s = s.replace("×", r"\times")
    # keep existing \frac, only convert plain a/b
    s = re.sub(r"(?<!\\)([A-Za-z0-9(){}^_!]+)\s*/\s*([A-Za-z0-9(){}^_!]+)", r"\\frac{\1}{\2}", s)
    s = re.sub(r"(?<=[A-Za-z0-9!])\s*\*\s*(?=[A-Za-z0-9(])", r"\\times", s)
    s = re.sub(r"\s*\\times\s*", r"\\times", s)
    s = re.sub(r"\s*=\s*", "=", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_math_spans(text: str) -> tuple[str, dict[str, str]]:
    token_map: dict[str, str] = {}
    out = str(text or "")

    def _sub(pattern: re.Pattern[str], name: str, src: str) -> str:
        idx = 0

        def repl(m: re.Match[str]) -> str:
            nonlocal idx
            key = f"@@{name}_{idx}@@"
            token_map[key] = m.group(0)
            idx += 1
            return key

        return pattern.sub(repl, src)

    out = _sub(INLINE_MATH_RE, "INLINE", out)
    out = _sub(DISPLAY_MATH_RE, "DISPLAY", out)
    out = _sub(DOLLAR_MATH_RE, "DOLLAR", out)
    return out, token_map


def _restore_math_spans(text: str, token_map: dict[str, str]) -> str:
    out = str(text or "")
    for k, v in token_map.items():
        out = out.replace(k, v)
    return out


def _normalize_existing_math_spans(text: str) -> str:
    def repl_inline(m: re.Match[str]) -> str:
        return _wrap_inline(_standardize_general_math(m.group(1)))

    return INLINE_MATH_RE.sub(repl_inline, text)


def detect_unwrapped_latex_scripts(text: str) -> list[str]:
    protected, _ = _extract_math_spans(text)
    patterns = [
        r"\{\}\^\s*\{?[A-Za-z0-9]+\}?\s*[PC]\s*_\s*\{?[A-Za-z0-9]+\}?",
        r"\b[PC]\s*\^\s*\{?[A-Za-z0-9]+\}?\s*_\s*\{?[A-Za-z0-9]+\}?",
        r"\b[PC]\s*_\s*\{?[A-Za-z0-9]+\}?\s*\^\s*\{?[A-Za-z0-9]+\}?",
        r"\b[a-zA-Z]\s*\^\s*\{?[A-Za-z0-9]+\}?",
        r"\b[a-zA-Z]\s*_\s*\{?[A-Za-z0-9]+\}?",
    ]
    hits: list[str] = []
    for p in patterns:
        for m in re.finditer(p, protected):
            hits.append(m.group(0))
    return hits


def _convert_outside_math(text: str) -> str:
    out = text
    # Convert P/C tokens outside existing math spans
    perm_or_comb = r"(\{\}\^\{[A-Za-z0-9]+\}[PC]_\{[A-Za-z0-9]+\}|[PC]\([A-Za-z0-9]+\s*,\s*[A-Za-z0-9]+\)|[PC]\^\{?[A-Za-z0-9]+\}?\_\{?[A-Za-z0-9]+\}?|[PC]_\{?[A-Za-z0-9]+\}?\^\{?[A-Za-z0-9]+\}?)"
    out = re.sub(perm_or_comb, lambda m: _wrap_inline(_standardize_general_math(m.group(1))), out)
    # fraction a/b
    out = re.sub(
        r"([A-Za-z0-9!]+)\s*/\s*([A-Za-z0-9!]+)",
        lambda m: _wrap_inline(_standardize_general_math(m.group(0))),
        out,
    )
    # merge two inline around equation/multiplication
    out = re.sub(
        r"\\\(([^()]*)\\\)\s*=\s*([0-9]+)\s*[×*]\s*\\\(([^()]*)\\\)",
        lambda m: _wrap_inline(_standardize_general_math(f"{m.group(1)}={m.group(2)}\\times{m.group(3)}")),
        out,
    )
    # wrap standalone n in Chinese sentence contexts
    out = re.sub(r"(?<=[\u4e00-\u9fff\s\(\)])n(?=[\u4e00-\u9fff\s，。,\)])", r"\(n\)", out)
    return out


def standardize_problem_latex(text: str) -> tuple[str, dict[str, Any]]:
    raw = "" if text is None else str(text)
    normalized = _normalize_existing_math_spans(raw)
    protected, token_map = _extract_math_spans(normalized)
    converted = _convert_outside_math(protected)
    out = _restore_math_spans(converted, token_map)
    out = re.sub(r"\s+", " ", out).strip()

    warnings: list[str] = []
    needs_review = False
    if "[WORD_EQUATION_UNPARSED]" in raw or re.search(r"\[FORMULA_IMAGE_\d+\]", raw):
        warnings.append("contains_unparsed_equation_marker")
        needs_review = True
    unwrapped = detect_unwrapped_latex_scripts(out)
    if unwrapped:
        warnings.append("contains_unwrapped_scripts")

    meta = {
        "math_format": "standard_latex",
        "warnings": warnings,
        "needs_review": needs_review,
        "raw_problem_backup": raw,
    }
    return out, meta


def parse_standard_latex_problem(problem_text: str) -> dict[str, Any]:
    t = str(problem_text or "")
    m = re.search(
        r"\{\}\^\{([A-Za-z0-9]+)\}P_\{(\d+)\}\s*=\s*(\d+)\s*\\times\s*\{\}\^\{([A-Za-z0-9]+)\}P_\{(\d+)\}",
        t,
    )
    if not m:
        return {"type": "unknown"}
    return {
        "type": "permutation_equation",
        "left": {"n": m.group(1), "r": int(m.group(2))},
        "multiplier": int(m.group(3)),
        "right": {"n": m.group(4), "r": int(m.group(5))},
    }
