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

# Coordinate geometry context keywords — when present without explicit comb/perm language,
# C/P followed by (...) must be treated as point labels, not combination/permutation symbols.
_COORDINATE_CONTEXT_RE = re.compile(
    r"點|座標|坐標|象限|x\s*軸|y\s*軸|平面|直線|距離|中點|分點|重心|線段|坐標系|座標系"
)
# Explicit combination / permutation context keywords
_COMB_PERM_CONTEXT_RE = re.compile(
    r"排列|組合|任取|取出|全排列|相異|重複排列|共有|種"
)
# C/P immediately followed by a parenthesised argument (coordinate-point or function form)
_CP_PAREN_FORM_RE = re.compile(r"\b[CP]\s*\([^()]*\)", re.IGNORECASE)


def normalize_operator_artifacts(text: str) -> str:
    """Normalize common PDF/OCR operator artifacts without guessing ambiguous cases."""
    if text is None:
        return text

    normalized = str(text)
    normalized = re.sub(r"\s*[#＃﹟]\s*", " × ", normalized)
    normalized = re.sub(r"\s*×\s*", " × ", normalized)
    normalized = re.sub(r"\s{2,}", " ", normalized)
    normalized = re.sub(r"\s+([。；，、,.!?])", r"\1", normalized)
    return normalized.strip()


def normalize_combination_permutation_notation(text: str) -> str:
    """Normalize Taiwanese C_r^n / P_r^n notation into stable C(n,r) / P(n,r).

    In coordinate-geometry context (座標/點/象限 …) without explicit combination/
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

    # sub/sup patterns require _ or ^ — they cannot accidentally match A(x,y) forms.
    normalized = _COMB_PERM_PATTERN_SUB_SUP.sub(sub_sub_sup, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB.sub(sub_sup_sub, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB_VAR.sub(
        lambda m: f"{m.group(1).upper()}({m.group(2)},{m.group(3)})", normalized
    )

    # Spaced/compact patterns (e.g. "C 3 1" → "C(1,3)") are designed to normalise
    # OCR-split combination notation.  In coordinate-only context (座標/點/象限 …
    # without any 排列/組合/任取/種 … language) these patterns must be skipped
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
    (點/座標/坐標/象限/直線 …) *without* explicit combination/permutation language
    (排列/組合/任取/種 …).  In that case they must not be flagged as suspicious
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
        (r"[#＃﹟]\s*[#＃﹟]", "suspicious_pdf_artifact"),
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

    if re.search(r"\b[gh]\b", raw) and re.search(r"[#＃﹟]|[_^]\s*[ih]\b|\b[CP]\s+\d", raw, flags=re.IGNORECASE):
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
