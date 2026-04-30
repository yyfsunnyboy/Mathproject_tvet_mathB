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
    """Normalize Taiwanese C_r^n / P_r^n notation into stable C(n,r) / P(n,r)."""
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

    normalized = _COMB_PERM_PATTERN_SUB_SUP.sub(sub_sub_sup, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB.sub(sub_sup_sub, normalized)
    normalized = _COMB_PERM_PATTERN_SUP_SUB_VAR.sub(lambda m: f"{m.group(1).upper()}({m.group(2)},{m.group(3)})", normalized)
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


def _extract_comb_perm_terms(text: str) -> list[tuple[str, int, int]]:
    terms: list[tuple[str, int, int]] = []

    for match in _COMB_PERM_PATTERN_SUB_SUP.finditer(text):
        terms.append((match.group(1).upper(), int(match.group(3)), int(match.group(2))))
    for match in _COMB_PERM_PATTERN_SUP_SUB.finditer(text):
        terms.append((match.group(1).upper(), int(match.group(2)), int(match.group(3))))
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
    """Detect formula patterns likely caused by PDF/OCR extraction errors."""
    raw = "" if text is None else str(text)
    normalized_preview = normalize_math_text(raw)
    reasons: list[str] = []
    suggestions: list[str] = []

    raw_terms = _extract_comb_perm_terms(raw)
    normalized_terms = _extract_comb_perm_terms(normalized_preview)
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

    has_comb_perm_signal = bool(re.search(r"\b[CP]\b|\b[CP]\s*[_^]|\b[CP]\d", raw, flags=re.IGNORECASE))
    if has_comb_perm_signal and not all_terms and not re.search(r"\b[CP]\(\d+,\s*\d+\)", normalized_preview, flags=re.IGNORECASE):
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
