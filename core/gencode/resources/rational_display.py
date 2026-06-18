"""Shared rational and linear-display helpers for V3 generators."""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any


def normalize_fraction_value(value: Any) -> Fraction:
    """Normalize int/str/Fraction/SymPy Rational-like values to Fraction."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a rational value")
    if isinstance(value, Fraction):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        return Fraction(value).limit_denominator()

    text = str(value or "").strip()
    if not text:
        raise ValueError("empty rational value")
    if text.startswith("$") and text.endswith("$"):
        text = text[1:-1].strip()
    text = text.replace("−", "-")
    match = re.fullmatch(r"(-?)\\frac\{(-?\d+)\}\{(-?\d+)\}", text)
    if match:
        sign = -1 if match.group(1) == "-" else 1
        return Fraction(sign * int(match.group(2)), int(match.group(3)))
    return Fraction(text)


def fraction_to_plain(value: Any) -> str:
    """Return a normalized plain-text fraction, e.g. -3/2 or 4."""
    frac = normalize_fraction_value(value)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def fraction_to_latex(value: Any) -> str:
    """Return standard LaTeX fraction text, e.g. -\\frac{3}{2} or 4."""
    frac = normalize_fraction_value(value)
    if frac.denominator == 1:
        return str(frac.numerator)
    sign = "-" if frac.numerator < 0 else ""
    return f"{sign}\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"


def normalize_linear_expression_display(expr: Any) -> str:
    """Clean simple linear display text such as y = 1x + -3."""
    text = str(expr or "").strip().replace("−", "-")
    if not text:
        return text

    lhs = ""
    rhs = text
    if "=" in text:
        left, right = text.split("=", 1)
        lhs = f"{left.strip()} = "
        rhs = right.strip()

    compact = re.sub(r"\s+", "", rhs)
    compact = compact.replace("+-", "-").replace("-+", "-").replace("--", "+")
    match = re.fullmatch(r"([+-]?(?:\d+(?:/\d+)?)?)x(?:([+-])(\d+(?:/\d+)?))?", compact)
    if match:
        coeff_raw, const_sign, const_raw = match.groups()
        coeff = _parse_linear_coeff(coeff_raw)
        const = Fraction(0, 1)
        if const_raw is not None:
            const = normalize_fraction_value(const_raw)
            if const_sign == "-":
                const = -const
        rhs = _format_linear_rhs(coeff, const)
        return f"{lhs}{rhs}".strip()

    text = re.sub(r"\+\s*-", "- ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def canonicalize_display_answer(value: Any, answer_type: str | None = None) -> str:
    """Return a stable display answer string without changing answer semantics."""
    if isinstance(value, Fraction):
        return fraction_to_latex(value)

    text = str(value or "").strip()
    if not text:
        return text

    normalized_answer_type = str(answer_type or "").strip().lower()
    if normalized_answer_type in {"fraction", "rational", "rational_fraction"}:
        return fraction_to_latex(text)

    text = normalize_linear_expression_display(text)
    text = _replace_plain_fractions_with_latex(text)
    return text


def rational_string_to_latex_in_text(text: Any) -> str:
    """Normalize rational-looking substrings in display text to LaTeX fractions."""
    return _replace_plain_fractions_with_latex(str(text or ""))


def canonicalize_part_display_answer(part: Any) -> str:
    """Return a display-only representation for one multi-part answer value."""
    if isinstance(part, dict):
        expected = part.get("display_answer", part.get("expected_answer", part.get("answer", "")))
        checker = str(part.get("checker") or "").strip()
        equivalence_type = str(part.get("equivalence_type") or part.get("answer_equivalence") or "").strip()
        answer_type = "rational" if checker in {"rational_checker", "numeric_checker"} or equivalence_type in {
            "rational_equivalent",
            "numeric_exact",
        } else None
        return canonicalize_display_answer(expected, answer_type=answer_type)
    return canonicalize_display_answer(part)


def canonicalize_multi_part_display(parts: Any) -> Any:
    """Normalize display values for multi-part answers without changing canonical answers."""
    if isinstance(parts, dict):
        return {
            str(key): canonicalize_part_display_answer(
                {"expected_answer": value, "checker": _infer_part_checker_from_key(str(key))}
            )
            for key, value in parts.items()
        }
    if isinstance(parts, list):
        normalized: list[dict[str, Any]] = []
        for index, raw_part in enumerate(parts):
            if isinstance(raw_part, dict):
                part = dict(raw_part)
                part["display_answer"] = canonicalize_part_display_answer(part)
                normalized.append(part)
            else:
                normalized.append(
                    {
                        "key": str(index),
                        "display_answer": canonicalize_part_display_answer(raw_part),
                    }
                )
        return normalized
    return canonicalize_part_display_answer(parts)


def _parse_linear_coeff(raw: str) -> Fraction:
    if raw in {"", "+"}:
        return Fraction(1, 1)
    if raw == "-":
        return Fraction(-1, 1)
    return normalize_fraction_value(raw)


def _format_linear_rhs(coeff: Fraction, const: Fraction) -> str:
    parts: list[str] = []
    if coeff:
        if coeff == 1:
            parts.append("x")
        elif coeff == -1:
            parts.append("-x")
        else:
            parts.append(f"{fraction_to_plain(coeff)}x")
    if const:
        const_text = fraction_to_plain(abs(const))
        if not parts:
            parts.append(fraction_to_plain(const))
        elif const > 0:
            parts.append(f"+ {const_text}")
        else:
            parts.append(f"- {const_text}")
    if not parts:
        return "0"
    return " ".join(parts)


def _replace_plain_fractions_with_latex(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return fraction_to_latex(match.group(0))

    return re.sub(r"(?<![\\\w])[-+]?\d+/\d+", repl, text)


def _infer_part_checker_from_key(key: str) -> str:
    normalized = str(key or "").strip().lower()
    if normalized in {"area", "value", "numeric", "number", "amount"}:
        return "rational_checker"
    return ""
