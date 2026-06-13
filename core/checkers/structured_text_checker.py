# -*- coding: utf-8 -*-
"""
core/checkers/structured_text_checker.py
=========================================
Deterministic checker for structured short-text answers.

Supports answers like:
  "向右 2, 向上 4"       (translation description)
  "x = -3"               (axis of symmetry)
  "(1, -2)"              (coordinate pair)
  "頂點=(1,-2), 對稱軸=x=1"  (multi-field vertex + axis)
  "向上"                 (opening direction)

All comparison is deterministic (no LLM).  Normalization rules:
  • 中文逗號/頓號  →  ","
  • 全形數字       →  半形
  • 全形括號       →  半形
  • 全形等號       →  半形
  • 多餘空白合併/移除
  • 座標 "(a, b)"  →  "(a,b)" (去空白)
  • "x = h"  →  "x=h"
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any


# ── Normalization ─────────────────────────────────────────────────────────────

_FULLWIDTH_DIGIT_MAP = str.maketrans(
    "０１２３４５６７８９",
    "0123456789",
)
_FULLWIDTH_PUNCT_MAP = str.maketrans(
    "（）【】，、＝＋－＊／",
    "()[],,=+-*/",
)


def normalize_separators(text: str) -> str:
    """Replace Chinese punctuation separators with ASCII comma."""
    result = str(text or "")
    result = result.replace("，", ",")
    result = result.replace("、", ",")
    result = re.sub(r",\s*", ", ", result)  # normalise spacing after comma
    return result


def normalize_fullwidth(text: str) -> str:
    """Convert fullwidth digits, brackets, and common operators to halfwidth."""
    result = str(text or "")
    result = result.translate(_FULLWIDTH_DIGIT_MAP)
    result = result.translate(_FULLWIDTH_PUNCT_MAP)
    # Also handle NFC / NFKC normalisation for remaining fullwidth chars
    result = unicodedata.normalize("NFKC", result)
    return result


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces; strip leading/trailing whitespace."""
    result = str(text or "").strip()
    result = re.sub(r"\s+", " ", result)
    return result


def normalize_equation(text: str) -> str:
    """Remove spaces around '=' and '-' for equation-style answers."""
    result = str(text or "")
    result = re.sub(r"\s*=\s*", "=", result)
    # Normalise "(a, b)" → "(a,b)"
    result = re.sub(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", r"(\1,\2)", result)
    return result


def normalize_structured_text(text: str) -> str:
    """Apply all normalization layers to a structured-text answer.

    Call order:
      fullwidth → separators → whitespace → equation
    """
    result = normalize_fullwidth(str(text or ""))
    result = normalize_separators(result)
    result = normalize_whitespace(result)
    result = normalize_equation(result)
    return result


# ── Field extraction ──────────────────────────────────────────────────────────

def split_answer_fields(text: str, separator: str = ",") -> list[str]:
    """Split normalised answer text by separator, stripping each field."""
    normalised = normalize_structured_text(text)
    # Use the normalised separator (always "," after normalization)
    parts = normalised.split(",")
    return [p.strip() for p in parts if p.strip()]


# ── Comparison ────────────────────────────────────────────────────────────────

def compare_structured_text(
    expected: str,
    actual: str,
    *,
    answer_fields: list[str] | None = None,
    answer_separator: str = ",",
) -> dict[str, Any]:
    """Deterministic structured-text comparison.

    Returns:
      {
        "is_correct": bool,
        "expected_normalised": str,
        "actual_normalised": str,
        "field_results": list[dict] | None,
        "reason": str,
      }
    """
    exp_norm = normalize_structured_text(str(expected or ""))
    act_norm = normalize_structured_text(str(actual or ""))

    if exp_norm == act_norm:
        return {
            "is_correct": True,
            "expected_normalised": exp_norm,
            "actual_normalised": act_norm,
            "field_results": None,
            "reason": "exact_match_after_normalisation",
        }

    # Field-wise comparison when answer_fields are defined
    if answer_fields and len(answer_fields) >= 2:
        exp_parts = split_answer_fields(expected, answer_separator)
        act_parts = split_answer_fields(actual, answer_separator)
        if len(exp_parts) != len(act_parts):
            return {
                "is_correct": False,
                "expected_normalised": exp_norm,
                "actual_normalised": act_norm,
                "field_results": None,
                "reason": f"field_count_mismatch:expected_{len(exp_parts)}_got_{len(act_parts)}",
            }
        field_results = [
            {
                "field": answer_fields[i] if i < len(answer_fields) else f"field_{i}",
                "expected": exp_parts[i],
                "actual": act_parts[i],
                "match": exp_parts[i] == act_parts[i],
            }
            for i in range(len(exp_parts))
        ]
        all_match = all(r["match"] for r in field_results)
        return {
            "is_correct": all_match,
            "expected_normalised": exp_norm,
            "actual_normalised": act_norm,
            "field_results": field_results,
            "reason": "field_wise_match" if all_match else "field_mismatch",
        }

    return {
        "is_correct": False,
        "expected_normalised": exp_norm,
        "actual_normalised": act_norm,
        "field_results": None,
        "reason": "normalised_mismatch",
    }


def check_structured_text_answer(
    user_answer: Any,
    correct_answer: Any,
    *,
    answer_fields: list[str] | None = None,
    answer_separator: str = ",",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Entry point compatible with Gencode checker protocol.

    Returns a dict with at least:
      {"is_correct": bool, "checker": "structured_text_checker", ...}
    """
    # Try to read answer_fields from payload if not provided
    if answer_fields is None and isinstance(payload, dict):
        answer_fields = payload.get("answer_fields") or \
                        (payload.get("answer_contract") or {}).get("answer_fields")
    if answer_fields is None and isinstance(payload, dict):
        answer_fields = (payload.get("metadata") or {}).get("answer_fields")

    result = compare_structured_text(
        str(correct_answer or ""),
        str(user_answer or ""),
        answer_fields=answer_fields or [],
        answer_separator=answer_separator,
    )
    return {
        "is_correct": result["is_correct"],
        "checker": "structured_text_checker",
        "expected_normalised": result["expected_normalised"],
        "actual_normalised": result["actual_normalised"],
        "field_results": result.get("field_results"),
        "reason": result.get("reason"),
    }
