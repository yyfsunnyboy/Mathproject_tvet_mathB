# -*- coding: utf-8 -*-
"""Utilities for normalizing textbook math formula text extracted from PDF/OCR."""

from __future__ import annotations

import re
from typing import Any


_COMB_PERM_PATTERN_SUB_SUP = re.compile(r"\b([CP])\s*_\s*\{?(\d+)\}?\s*\^\s*\{?(\d+)\}?", re.IGNORECASE)
_COMB_PERM_PATTERN_SUP_SUB = re.compile(r"\b([CP])\s*\^\s*\{?(\d+)\}?\s*_\s*\{?(\d+)\}?", re.IGNORECASE)
_COMB_PERM_PATTERN_SUP_SUB_VAR = re.compile(r"\b([CP])\s*\^\s*\{?([a-zA-Z])\}?\s*_\s*\{?(\d+)\}?", re.IGNORECASE)
_COMB_PERM_PATTERN_SPACED = re.compile(r"\b([CP])\s+(\d+)\s+(\d+)\b", re.IGNORECASE)
_COMB_PERM_PATTERN_COMPACT = re.compile(r"\b([CP])(\d+)\s+(\d+)\b", re.IGNORECASE)
_NORMALIZED_COMB_PERM = re.compile(r"\b([CP])\((\d+),\s*(\d+)\)", re.IGNORECASE)

# Coordinate geometry context keywords ??when present without explicit comb/perm language,
# C/P followed by (...) must be treated as point labels, not combination/permutation symbols.
_COORDINATE_CONTEXT_RE = re.compile(
    r"坐標|平面|點|線段|直線|重心|中點|象限|x\s*軸|y\s*軸|座標",
    re.IGNORECASE,
)
# Explicit combination / permutation context keywords
_COMB_PERM_CONTEXT_RE = re.compile(
    r"排列|組合|選法|從.*選|取.*個|C\(|P\(",
    re.IGNORECASE,
)
# C/P immediately followed by a parenthesised argument (coordinate-point or function form)
_CP_PAREN_FORM_RE = re.compile(r"\b[CP]\s*\([^()]*\)", re.IGNORECASE)
_DISPLAY_MATH_BLOCK_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
_DISPLAY_DISALLOWED_RE = re.compile(
    r"\\begin|cases|aligned|array|matrix|split|gather|\\sum|\\int",
    re.IGNORECASE,
)


def normalize_operator_artifacts(text: str) -> str:
    """Normalize common PDF/OCR operator artifacts without guessing ambiguous cases."""
    if text is None:
        return text

    normalized = str(text)
    normalized = re.sub(r"\s*#\s*", " ? ", normalized)
    normalized = re.sub(r"\?\s*\?", " ? ", normalized)
    normalized = re.sub(r"\s{2,}", " ", normalized)
    normalized = re.sub(r"\s+([?.!?])", r"\1", normalized)
    return normalized.strip()


def normalize_combination_permutation_notation(text: str) -> str:
    """Normalize Taiwanese C_r^n / P_r^n notation into stable C(n,r) / P(n,r).

    In coordinate-geometry context (摨扳?/暺?鞊⊿? ?? without explicit combination/
    permutation language, C/P followed by parentheses are treated as point labels
    and left untouched.
    """
    if text is None:
        return text

    normalized = str(text)

    def sub_sub_sup(match: re.Match[str]) -> str:
        symbol = match.group(1).upper()
        r = match.group(2)
        n = match.group(3)
        return f"{symbol}({n},{r})"

    def sub_sup_sub(match: re.Match[str]) -> str:
        symbol = match.group(1).upper()
        n = match.group(2)
        r = match.group(3)
        return f"{symbol}({n},{r})"

    def sub_spaced(match: re.Match[str]) -> str:
        symbol = match.group(1).upper()
        r = match.group(2)
        n = match.group(3)
        return f"{symbol}({n},{r})"

    # sub/sup patterns require _ or ^ ??they cannot accidentally match A(x,y) forms.
    normalized = _COMB_PERM_PATTERN_SUB_SUP.sub(sub_sub_sup, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB.sub(sub_sup_sub, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB_VAR.sub(
        lambda m: f"{m.group(1).upper()}({m.group(2)},{m.group(3)})", normalized
    )

    # Spaced/compact patterns (e.g. "C 3 1" ??"C(1,3)") are designed to normalise
    # OCR-split combination notation.  In coordinate-only context (摨扳?/暺?鞊⊿? ??
    # without any ??/蝯?/隞餃?/蝔???language) these patterns must be skipped
    # entirely: space-separated digits following a C or P label are coordinates,
    # not combination/permutation indices.
    is_coord_ctx = bool(_COORDINATE_CONTEXT_RE.search(normalized))
    has_comb_perm_ctx = bool(_COMB_PERM_CONTEXT_RE.search(normalized))

    if not (is_coord_ctx and not has_comb_perm_ctx):
        normalized = _COMB_PERM_PATTERN_SPACED.sub(sub_spaced, normalized)
        normalized = _COMB_PERM_PATTERN_COMPACT.sub(sub_spaced, normalized)

    return normalized


def normalize_math_text(text: str) -> str:
    """Apply conservative math text normalization for imported textbook content."""
    if text is None:
        return text
    normalized = normalize_operator_artifacts(str(text))
    normalized = normalize_combination_permutation_notation(normalized)
    normalized = re.sub(r"\s{2,}", " ", normalized)
    return normalized.strip()


def _extract_comb_perm_terms(
    text: str, *, include_normalized: bool = True
) -> list[tuple[str, int, int]]:
    """Extract (symbol, n, r) triples from recognised combination/permutation notation.

    Parameters
    ----------
    include_normalized:
        When *False*, skip ``_NORMALIZED_COMB_PERM`` matches (i.e. C(n,r) / P(n,r)
        with digit arguments).  Set to *False* in coordinate-only context so that
        coordinate point labels like ``C(3,1)`` are not counted as combination terms.
    """
    terms: list[tuple[str, int, int]] = []

    for match in _COMB_PERM_PATTERN_SUB_SUP.finditer(text):
        terms.append((match.group(1).upper(), int(match.group(3)), int(match.group(2))))
    for match in _COMB_PERM_PATTERN_SUP_SUB.finditer(text):
        terms.append((match.group(1).upper(), int(match.group(2)), int(match.group(3))))
    if include_normalized:
        for match in _NORMALIZED_COMB_PERM.finditer(text):
            terms.append((match.group(1).upper(), int(match.group(2)), int(match.group(3))))

    return terms


def _has_inconsistent_combination_sum(terms: list[tuple[str, int, int]]) -> bool:
    combos = [(n, r) for symbol, n, r in terms if symbol == "C"]
    if len(combos) < 3:
        return False

    ns = [n for n, _ in combos]
    rs = [r for _, r in combos]
    sequential_r = all((rs[i + 1] - rs[i]) == 1 for i in range(len(rs) - 1))
    repeated_or_drifting_n = len(set(ns)) > 1
    return sequential_r and repeated_or_drifting_n


def detect_suspicious_formula(text: str) -> dict[str, Any]:
    """Detect formula patterns likely caused by PDF/OCR extraction errors.

    Coordinate geometry context guard
    ----------------------------------
    Per AGENTS.md section rules, C/P followed by (...) are coordinate point labels
    (e.g. C(3,1), P(a,b)) when the surrounding text contains coordinate keywords
    (暺?摨扳?/??/鞊⊿?/?渡? ?? *without* explicit combination/permutation language
    (??/蝯?/隞餃?/蝔???.  In that case they must not be flagged as suspicious
    combination notation, and must not be counted as combination terms for the
    consistency check.
    """
    raw = "" if text is None else str(text)
    normalized_preview = normalize_math_text(raw)
    reasons: list[str] = []
    suggestions: list[str] = []

    is_coord_ctx = bool(_COORDINATE_CONTEXT_RE.search(raw))
    has_comb_perm_ctx = bool(_COMB_PERM_CONTEXT_RE.search(raw))
    # "coordinate-only": coordinate geometry language present, no explicit comb/perm language.
    # In this mode C/P(...) forms are point labels, not combination/permutation symbols.
    coord_only = is_coord_ctx and not has_comb_perm_ctx

    # When in coordinate-only mode, exclude C(n,r)/P(n,r) normalised forms from term
    # extraction so that coordinate point labels don't trigger the consistency check.
    raw_terms = _extract_comb_perm_terms(raw, include_normalized=not coord_only)
    normalized_terms = _extract_comb_perm_terms(
        normalized_preview, include_normalized=not coord_only
    )
    all_terms = raw_terms or normalized_terms

    if _has_inconsistent_combination_sum(all_terms):
        reasons.append("combination_upper_index_inconsistent")
        suggestions.append("Check whether all C_r^n terms in the sum should share the same upper index n.")

    artifact_patterns = [
        (r"#\s*#", "suspicious_pdf_artifact"),
        (r"\?\s*\?", "suspicious_pdf_artifact"),
        (r"[_^]\s*[ih]\b", "suspicious_pdf_artifact"),
        (r"\b[CP]\s*(?:\n|\r\n?)\s*\d", "suspicious_combination_notation"),
        (r"\b[CP]\s+\d(?:\s|$)", "suspicious_combination_notation"),
    ]
    for pattern, reason in artifact_patterns:
        if re.search(pattern, raw, flags=re.IGNORECASE) and reason not in reasons:
            reasons.append(reason)

    if re.search(r"\b\d+\s+\d+\s*!", raw):
        reasons.append("suspicious_factorial")
        suggestions.append("Check if a broken factorial such as '5 1 !' should be '5!'.")

    if re.search(r"\b[gh]\b", raw) and re.search(
        r"#|\?|[_^]\s*[ih]\b|\b[CP]\s+\d", raw, flags=re.IGNORECASE
    ):
        if "suspicious_pdf_artifact" not in reasons:
            reasons.append("suspicious_pdf_artifact")

    # When C/P(...) should not be treated as combination/permutation (no comb/perm context),
    # strip those parenthetical forms before testing for a comb/perm signal so that point
    # labels like P(a,b) or C(3,1) do not trigger suspicious_combination_notation.
    if not has_comb_perm_ctx:
        raw_for_signal = _CP_PAREN_FORM_RE.sub("", raw)
    else:
        raw_for_signal = raw
    has_comb_perm_signal = bool(
        re.search(r"\b[CP]\b|\b[CP]\s*[_^]|\b[CP]\d", raw_for_signal, flags=re.IGNORECASE)
    )
    if has_comb_perm_signal and not all_terms and not re.search(
        r"\b[CP]\(\d+,\s*\d+\)", normalized_preview, flags=re.IGNORECASE
    ):
        if "suspicious_combination_notation" not in reasons:
            reasons.append("suspicious_combination_notation")
            suggestions.append("Check C/P notation; OCR may have split upper/lower indices.")

    if "suspicious_pdf_artifact" in reasons:
        suggestions.append("Review PDF/OCR artifacts such as #, _ i, ^ h, or broken standalone symbols.")

    return {
        "is_suspicious": bool(reasons),
        "reasons": reasons,
        "suggestions": suggestions,
        "normalized_preview": normalized_preview,
    }


def _is_short_inline_like_formula(content: str) -> bool:
    c = str(content or "").strip()
    if not c or len(c) > 80:
        return False
    if _DISPLAY_DISALLOWED_RE.search(c):
        return False
    if "\n" in c or "\r" in c:
        return False
    patterns = [
        r"^[A-Za-z]\s*\\left\([^\\\n]{1,60}\\right\)$",
        r"^[A-Za-z]\s*\([^()\n]{1,60}\)$",
        r"^[fgFG]\s*\([^()\n]{1,60}\)$",
        r"\\triangle\s*[A-Za-z]{2,6}",
        r"\\overline\s*\{?[A-Za-z]{1,6}\}?",
        r"\\left\|.*\\right\|",
        r"[<>]|\\le|\\ge|=",
    ]
    if any(re.search(p, c) for p in patterns):
        return True
    return bool(re.fullmatch(r"[A-Za-z0-9\s\\\{\}\^\_\+\-\*/=<>,\.\|\(\)]+", c))


def _has_same_line_text_context(text: str, start: int, end: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    left = text[line_start:start]
    right = text[end:line_end]
    return bool(left.strip()) and bool(right.strip())


def _cleanup_inline_latex_spacing(text: str) -> str:
    out = str(text or "")

    def _compact_left_right(m: re.Match[str]) -> str:
        inner = m.group(1)
        inner = re.sub(r"\s*,\s*", ",", inner.strip())
        return rf"\left({inner}\right)"

    out = re.sub(r"\\left\(\s*([^()\n]*?)\s*\\right\)", _compact_left_right, out)
    out = re.sub(r"\\\)\s*,\s*\\\(", r"\\)、\\(", out)
    out = out.replace("三點、若", "三點，若")

    out = re.sub(
        r"\\\(([A-Z])\s*\(\s*([^()\\\n]{1,40})\s*\)\\\)",
        lambda m: r"\(" + str(m.group(1)) + r"\left(" + str(re.sub(r'\s*,\s*', ',', m.group(2).strip())) + r"\right)\)",
        out,
    )
    out = re.sub(
        r"\\\(([^\\\n]*?)\\\)",
        lambda m: r"\(" + str(re.sub(r'(?<!\\)\s*(<=|>=|<|>|=)\s*', r'\1', m.group(1).strip())) + r"\)",
        out,
    )
    out = re.sub(r"\\\(a、b\\\)", r"\\(a\\)、\\(b\\)", out)

    out = re.sub(
        r"([\u4e00-\u9fff])\\\(",
        lambda m: f"{m.group(1)} \\(",
        out,
    )
    out = re.sub(
        r"\\\)([\u4e00-\u9fff])",
        lambda m: f"\\) {m.group(1)}",
        out,
    )

    out = re.sub(r"([\u4e00-\u9fff])([0-9]+)([\u4e00-\u9fff])", r"\1 \(\2\) \3", out)
    out = re.sub(r"試求：\((\d+)\)", r"試求：\n(\1)", out)
    out = re.sub(r"？\((\d+)\)", r"？\n(\1)", out)
    out = re.sub(r"\((\d+)\)點", r"(\1) 點", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()

def normalize_converted_docx_latex_text(text: str) -> dict[str, Any]:
    raw = "" if text is None else str(text)
    changes: list[dict[str, Any]] = []

    def _replace(match: re.Match[str]) -> str:
        before = match.group(0)
        content = match.group(1)
        start, end = match.span()

        if not _has_same_line_text_context(raw, start, end):
            return before
        if not _is_short_inline_like_formula(content):
            return before

        after = rf"\({content.strip()}\)"
        if after != before:
            changes.append(
                {
                    "before": before,
                    "after": after,
                    "reason": "display_math_inline_context_short_formula",
                    "confidence": 0.95,
                }
            )
        return after

    converted = _DISPLAY_MATH_BLOCK_RE.sub(_replace, raw)
    cleaned = _cleanup_inline_latex_spacing(converted)
    if cleaned != converted:
        changes.append(
            {
                "before": converted,
                "after": cleaned,
                "reason": "inline_spacing_and_cjk_punctuation_cleanup",
                "confidence": 0.95,
            }
        )

    needs_review = any(float(c.get("confidence", 0.0)) < 0.9 for c in changes)
    return {"text": cleaned, "changes": changes, "needs_review": needs_review}

