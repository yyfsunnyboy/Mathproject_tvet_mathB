"""Shared rational and linear-display helpers for V3 generators."""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any


# Long classroom-float noise from sympy Float sstr / IEEE formatting.
_FLOAT_NOISE_RE = re.compile(r"(?<![\d.\\])(-?\d+\.\d{6,})(?!\d)")
# Coefficient 1/-1 before a vector symbol. Do NOT treat subscript digits
# (e.g. k_1\vec{b}, k_{1}\vec{b}) as trivial coefficients.
_TRIVIAL_POS_VEC_COEFF_RE = re.compile(
    r"(?<![\d.A-Za-z_])1(\\(?:vec|overrightarrow)\{)"
)
_TRIVIAL_NEG_VEC_COEFF_RE = re.compile(
    r"(?<![\d.A-Za-z_])-1(\\(?:vec|overrightarrow)\{)"
)


def normalize_fraction_value(value: Any) -> Fraction:
    """Normalize int/str/Fraction/SymPy Rational-like values to Fraction."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a rational value")
    if isinstance(value, Fraction):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        if abs(value) < 1e-15:
            return Fraction(0, 1)
        return Fraction(value).limit_denominator(10_000)

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
    # Sympy Float noise tokens
    if re.fullmatch(r"-?\d+\.\d{6,}", text):
        return Fraction(float(text)).limit_denominator(10_000)
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


def compact_float_noise_token(token: str) -> str:
    """Map noisy float tokens to compact exact/plain classroom forms (display only)."""
    raw = str(token or "").strip()
    if not raw:
        return raw
    try:
        value = float(raw)
    except ValueError:
        return raw
    if abs(value) < 1e-12:
        return "0"
    frac = Fraction(value).limit_denominator(10_000)
    if abs(float(frac) - value) > 1e-9:
        text = f"{value:.12g}"
        if text in {"-0", "-0.0"}:
            return "0"
        return text
    return fraction_to_plain(frac)


def sanitize_float_noise_in_text(text: Any) -> str:
    """Replace long float tails in student-facing text. Does not touch short decimals."""
    source = str(text or "")
    if not source:
        return source
    return _FLOAT_NOISE_RE.sub(lambda m: compact_float_noise_token(m.group(0)), source)


def sanitize_trivial_vector_coefficients(text: Any) -> str:
    """Display-only: 1\\vec{a} → \\vec{a}, -1\\vec{a} → -\\vec{a}."""
    source = str(text or "")
    if not source:
        return source
    source = _TRIVIAL_POS_VEC_COEFF_RE.sub(r"\1", source)
    source = _TRIVIAL_NEG_VEC_COEFF_RE.sub(r"-\1", source)
    return source


def ensure_multipart_item_line_breaks(text: Any) -> str:
    """Insert newlines before ``(2)``/``(3)``… when a stem lists multipart items inline.

    Legacy fallback only. Prefer structured ``stem_structure`` when available.
    Does not treat bare coefficients as item markers.
    """
    source = str(text or "")
    if not source:
        return source
    # If already has an item-boundary newline before (2)/(3), leave as-is.
    if re.search(r"\n[\(（]\s*[2-9]\d*\s*[\)）]", source):
        return source
    if not re.search(r"[\(（]\s*1\s*[\)）]", source):
        return source
    # Break before subsequent numbered items: (2) (3) … / （2）（3）…
    return re.sub(r"(?<!\n)([\(（]\s*[2-9]\d*\s*[\)）])", r"\n\1", source)


_ASCII_SQRT_FALLBACK_RE = re.compile(r"(?<![\\\w])sqrt\(([^()]+)\)")
_UNICODE_SQRT_RE = re.compile(r"√\s*(?:\(([^()]+)\)|\{([^{}]+)\}|(\d+))")
_TEX_SQRT_TO_ASCII_RE = re.compile(r"\\sqrt\s*\{([^{}]+)\}")
_SIMPLE_ASSIGNMENT_RE = re.compile(
    r"^([A-Za-z](?:_[A-Za-z0-9]+)?)\s*=\s*(.+)$"
)
# Ascii multiply between math atoms already partly upgraded to TeX.
_ASCII_MUL_IN_TEX_RE = re.compile(
    r"([0-9.\)\}]|\\(?:pi|circ))"
    r"\s*\*\s*"
    r"(\\sqrt|\\frac|\\left\(|\(|[0-9.\\])"
)


def _normalize_radicals_for_arithmetic_parse(expr: str) -> str:
    """Map unicode / TeX radicals to ``sqrt(...)`` so the numeric parser can run."""
    text = str(expr or "").replace("−", "-")
    text = _UNICODE_SQRT_RE.sub(
        lambda m: f"sqrt({m.group(1) or m.group(2) or m.group(3)})",
        text,
    )
    text = _TEX_SQRT_TO_ASCII_RE.sub(r"sqrt(\1)", text)
    text = text.replace(r"\left(", "(").replace(r"\right)", ")")
    return text


def _try_arithmetic_latex_fragment(expr: str) -> str | None:
    """Return LaTeX for a bounded numeric fragment, or None when unsafe to convert."""
    raw = _normalize_radicals_for_arithmetic_parse(expr).strip()
    if not raw:
        return None
    # Only convert when an ascii multiply or radical is present; leave plain TeX alone.
    if not re.search(r"(?:\*|sqrt\()", raw):
        return None
    if not re.fullmatch(r"[0-9.sqrt()+*/\-\s]+", raw):
        return None
    try:
        from core.gencode.choice_math_display import _arithmetic_latex

        return _arithmetic_latex(raw)
    except Exception:
        return None


def _suppress_residual_ascii_multiply_in_tex(expr: str) -> str:
    """Remove leftover ascii ``*`` between already-TeX atoms (display only)."""

    def _repl(match: re.Match[str]) -> str:
        left, right = match.group(1), match.group(2)
        if right.startswith((r"\sqrt", r"\frac", r"\left(", "(", r"\pi")):
            return f"{left}{right}"
        if re.match(r"[0-9.]", right):
            return f"{left} \\times {right}"
        return f"{left}{right}"

    return _ASCII_MUL_IN_TEX_RE.sub(_repl, expr)


def upgrade_ascii_sqrt_inside_math_delimiters(text: Any) -> str:
    """Convert checker-friendly ascii math inside ``$...$`` / ``\\(...\\)`` to LaTeX.

    Handles ``sqrt(...)``, unicode ``√``, and ascii ``*`` multiplication such as
    ``3*sqrt(3)/2`` → ``\\frac{3\\sqrt{3}}{2}``. Assignment forms like
    ``a=3*sqrt(2)`` only convert the RHS. Canonical checker answers are not
    routed through this helper, and prose outside math delimiters is untouched.
    """
    source = str(text or "")
    if not re.search(r"(?:\*|sqrt\(|√)", source):
        return source

    def _upgrade_inner(inner: str) -> str:
        original = str(inner or "")
        raw = original.strip().replace("−", "-")
        if not re.search(r"(?:\*|sqrt\(|√|\\sqrt)", raw):
            return original

        assignment = _SIMPLE_ASSIGNMENT_RE.fullmatch(raw)
        if assignment:
            lhs, rhs = assignment.group(1), assignment.group(2)
            converted = _try_arithmetic_latex_fragment(rhs)
            if converted is not None:
                return f"{lhs}={converted}"
            rhs_fallback = _ASCII_SQRT_FALLBACK_RE.sub(
                r"\\sqrt{\1}",
                _normalize_radicals_for_arithmetic_parse(rhs),
            )
            rhs_fallback = _suppress_residual_ascii_multiply_in_tex(rhs_fallback)
            return f"{lhs}={rhs_fallback}"

        converted = _try_arithmetic_latex_fragment(raw)
        if converted is not None:
            return converted

        fallback = _ASCII_SQRT_FALLBACK_RE.sub(
            r"\\sqrt{\1}",
            _normalize_radicals_for_arithmetic_parse(raw),
        )
        return _suppress_residual_ascii_multiply_in_tex(fallback)

    def _dollar(match: re.Match[str]) -> str:
        return f"${_upgrade_inner(match.group(1))}$"

    def _paren(match: re.Match[str]) -> str:
        return rf"\({_upgrade_inner(match.group(1))}\)"

    upgraded = re.sub(r"(?<!\$)\$(?!\$)([^$]+)\$", _dollar, source)
    upgraded = re.sub(r"\\\((.+?)\\\)", _paren, upgraded)
    return upgraded


def sanitize_student_math_display_text(text: Any, *, break_multipart_items: bool = True) -> str:
    """Shared student-facing cleanup for numeric float noise and trivial vec coeffs.

    Problem stems pass ``break_multipart_items=False``: their layout is left to the
    browser, and the marker regex cannot tell ``(2)`` items from ``f(2)`` inside math.
    """
    cleaned = sanitize_trivial_vector_coefficients(sanitize_float_noise_in_text(text))
    cleaned = upgrade_ascii_sqrt_inside_math_delimiters(cleaned)
    return ensure_multipart_item_line_breaks(cleaned) if break_multipart_items else cleaned


def latex_coeff_times_symbol(coeff: Any, symbol_latex: str) -> str:
    """Format coeff*symbol for LaTeX stems (1 → bare symbol, -1 → -symbol)."""
    frac = normalize_fraction_value(coeff)
    sym = str(symbol_latex or "").strip()
    if not sym:
        return fraction_to_latex(frac)
    if frac == 0:
        return "0"
    if frac == 1:
        return sym
    if frac == -1:
        return f"-{sym}"
    return f"{fraction_to_latex(frac)}{sym}"


def latex_difference_of_scaled_symbols(c1: Any, sym1: str, c2: Any, sym2: str) -> str:
    """Render c1*sym1 - c2*sym2 with trivial coefficients removed."""
    left = latex_coeff_times_symbol(c1, sym1)
    right_frac = normalize_fraction_value(c2)
    if right_frac == 0:
        return left
    if right_frac > 0:
        return f"{left}-{latex_coeff_times_symbol(right_frac, sym2)}"
    return f"{left}+{latex_coeff_times_symbol(-right_frac, sym2)}"


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
    if isinstance(value, float):
        frac = Fraction(value).limit_denominator(10_000)
        if abs(float(frac) - value) <= 1e-9:
            return fraction_to_latex(frac)
        return compact_float_noise_token(str(value))

    text = str(value or "").strip()
    if not text:
        return text

    normalized_answer_type = str(answer_type or "").strip().lower()
    if normalized_answer_type in {"fraction", "rational", "rational_fraction"}:
        return fraction_to_latex(text)

    text = sanitize_student_math_display_text(text)
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
