"""Validation helpers for vocational math B4 payloads and values."""

from __future__ import annotations

import re


_REQUIRED_PAYLOAD_KEYS = {
    "question_text",
    "choices",
    "answer",
    "explanation",
    "skill_id",
    "subskill_id",
    "problem_type_id",
    "generator_key",
    "difficulty",
    "diagnosis_tags",
    "remediation_candidates",
    "source_style_refs",
}

_PLACEHOLDER_TOKENS = [
    "[BLANK]",
    "[FORMULA_MISSING]",
    "[FORMULA_IMAGE",
    "[WORD_EQUATION_UNPARSED]",
    "□",
    "＿＿",
]


def validate_positive_integer(value: object, name: str = "value") -> bool:
    """Validate value is an integer > 0."""
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"validate_positive_integer: {name} must be a positive integer.")
    return True


def validate_nonnegative_integer(value: object, name: str = "value") -> bool:
    """Validate value is an integer >= 0."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"validate_nonnegative_integer: {name} must be a nonnegative integer.")
    return True


def validate_n_ge_r(n: int, r: int) -> bool:
    """Validate n and r are nonnegative integers with n >= r."""
    validate_nonnegative_integer(n, "n")
    validate_nonnegative_integer(r, "r")
    if n < r:
        raise ValueError("validate_n_ge_r: n must be >= r.")
    return True


def validate_choices_unique(choices: list) -> bool:
    """Validate choices is a list with unique entries."""
    if not isinstance(choices, list) or not choices:
        raise ValueError("validate_choices_unique: choices must be a non-empty list.")
    if len(set(choices)) != len(choices):
        raise ValueError("validate_choices_unique: choices must be unique.")
    return True


def validate_answer_in_choices(answer: object, choices: list) -> bool:
    """Validate answer appears in choices."""
    if not isinstance(choices, list) or not choices:
        raise ValueError("validate_answer_in_choices: choices must be a non-empty list.")
    if answer not in choices:
        raise ValueError("validate_answer_in_choices: answer must be included in choices.")
    return True


def validate_no_unfilled_placeholder(text: str) -> bool:
    """Validate text contains no unfilled placeholder markers."""
    if not isinstance(text, str):
        raise ValueError("validate_no_unfilled_placeholder: text must be a string.")
    for token in _PLACEHOLDER_TOKENS:
        if token in text:
            raise ValueError(f"validate_no_unfilled_placeholder: found placeholder token {token}.")
    return True


def validate_integer_answer(answer: object) -> bool:
    """Validate answer is int-like (int or integer string)."""
    if isinstance(answer, bool):
        raise ValueError("validate_integer_answer: bool is not an integer answer.")
    if isinstance(answer, int):
        return True
    if isinstance(answer, str) and re.fullmatch(r"[+-]?\d+", answer.strip()):
        return True
    raise ValueError("validate_integer_answer: answer must be an integer or integer-form string.")


def validate_expression_answer(answer: object) -> bool:
    """Validate answer is a non-empty expression-like string."""
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("validate_expression_answer: answer must be a non-empty string.")
    if not re.search(r"[0-9a-zA-ZxX+\-*/^() ]", answer):
        raise ValueError("validate_expression_answer: answer does not look like a math expression.")
    return True


def validate_polynomial_answer(answer: object) -> bool:
    """Validate answer is a polynomial-like expression string."""
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("validate_polynomial_answer: answer must be a non-empty string.")
    normalized = answer.replace(" ", "")
    if "x" not in normalized and "X" not in normalized:
        raise ValueError("validate_polynomial_answer: polynomial answer must include variable x.")
    if not re.fullmatch(r"[0-9xX+\-*/^()]+", normalized):
        raise ValueError("validate_polynomial_answer: contains invalid polynomial characters.")
    return True


def validate_parameter_tuple_not_seen(parameter_tuple: tuple, seen: set) -> bool:
    """Validate parameter tuple has not appeared in seen set."""
    if not isinstance(parameter_tuple, tuple):
        raise ValueError("validate_parameter_tuple_not_seen: parameter_tuple must be a tuple.")
    if not isinstance(seen, set):
        raise ValueError("validate_parameter_tuple_not_seen: seen must be a set.")
    if parameter_tuple in seen:
        raise ValueError("validate_parameter_tuple_not_seen: parameter tuple already seen.")
    return True


def validate_problem_payload_contract(payload: dict) -> bool:
    """Validate payload includes all required contract keys."""
    if not isinstance(payload, dict):
        raise ValueError("validate_problem_payload_contract: payload must be a dict.")
    missing = sorted(_REQUIRED_PAYLOAD_KEYS - set(payload.keys()))
    if missing:
        raise ValueError(f"validate_problem_payload_contract: missing keys: {', '.join(missing)}")
    return True


# ─── Phase 6C-1: Student-answer checkers for Chap2 probability ───────────────
#
# Naming convention: check_* functions judge student answers at runtime.
# They are separate from validate_* functions which guard generator payloads.
#
# Design follows Phase 6B contract:
#   - canonical answer stored as reduced fraction string "a/b" or integer
#   - flexible mode: accepts equivalent decimals and percentages
#   - strict mode: canonical format only (set strict_fraction=True)
#   - probability_range guard: 0 <= P <= 1 (enabled by default for prob types)


from fractions import Fraction as _Fraction


def _normalize_fullwidth(s: str) -> str:
    """Convert full-width digits/letters to half-width ASCII."""
    return "".join(
        chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c
        for c in s
    )


def _strip_latex_fraction(s: str) -> str | None:
    """Extract 'a/b' from LaTeX \\frac{a}{b}, \\dfrac{a}{b}, or $\\frac{a}{b}$."""
    s = s.strip().lstrip("$").rstrip("$").strip()
    m = re.fullmatch(r"\\d?frac\{(-?\d+)\}\{(-?\d+)\}", s.replace(" ", ""))
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None


def _parse_rational(raw: str) -> "_Fraction | None":
    """Parse a raw student answer string into a Fraction.

    Accepts: plain fraction 'a/b', LaTeX \\frac{a}{b}, integer, decimal, percentage.
    Returns None on parse failure or division by zero.
    """
    s = raw.strip()
    s = _normalize_fullwidth(s)

    # LaTeX fraction
    latex_result = _strip_latex_fraction(s)
    if latex_result is not None:
        s = latex_result

    # Percentage: remove trailing %
    is_pct = s.endswith("%")
    if is_pct:
        s = s[:-1].strip()

    try:
        if "/" in s:
            parts = s.split("/", 1)
            num = int(parts[0].strip())
            den = int(parts[1].strip())
            if den == 0:
                return None
            f = _Fraction(num, den)
        else:
            f = _Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None

    if is_pct:
        f = f / 100

    return f


def check_probability_range(value: object) -> bool:
    """Return True if value is a number in [0, 1]; raises ValueError otherwise.

    Boundary values 0 and 1 are legal (impossible / certain events).
    Used as a shared pre-check for all probability-type answers.
    """
    try:
        fv = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError("check_probability_range: value is not numeric.")
    if fv < 0 or fv > 1:
        raise ValueError(
            f"check_probability_range: probability must be between 0 and 1, got {fv}."
        )
    return True


def check_rational_answer(
    user_answer: object,
    expected_numerator: int,
    expected_denominator: int,
    *,
    allow_decimal: bool = True,
    allow_percentage: bool = True,
    strict_fraction: bool = False,
    validate_probability_range: bool = True,
) -> bool:
    """Check a student's rational/fraction answer against an expected reduced fraction.

    Parameters
    ----------
    user_answer:
        Raw student input (str, int, or float).
    expected_numerator, expected_denominator:
        The correct answer expressed as a reduced fraction.
    allow_decimal:
        Flexible mode — accept equivalent decimal (0.5 == 1/2).
    allow_percentage:
        Flexible mode — accept equivalent percentage (50% == 1/2).
    strict_fraction:
        If True, only accept plain 'a/b' or integer; reject decimal and
        percentage even if allow_decimal/allow_percentage are True.
    validate_probability_range:
        If True, verify the expected answer is in [0, 1].

    Returns True if correct, False if wrong; raises ValueError on bad config.
    """
    if expected_denominator <= 0:
        raise ValueError("check_rational_answer: expected_denominator must be positive.")

    expected_frac = _Fraction(expected_numerator, expected_denominator)

    if validate_probability_range:
        check_probability_range(expected_frac)

    if user_answer is None:
        return False

    raw = str(user_answer).strip()
    if not raw:
        return False

    if strict_fraction:
        f = _parse_rational(raw)
        if f is None:
            return False
        plain = _normalize_fullwidth(raw.strip())
        latex_ex = _strip_latex_fraction(plain)
        check_str = latex_ex if latex_ex else plain
        if "%" in check_str or ("." in check_str and "/" not in check_str):
            return False
        return f == expected_frac

    parsed = _parse_rational(raw)
    if parsed is None:
        return False

    normalized_raw = _normalize_fullwidth(raw.strip())
    if not allow_percentage and normalized_raw.endswith("%"):
        return False
    if not allow_decimal:
        if "." in normalized_raw and "/" not in normalized_raw and "%" not in normalized_raw:
            return False

    return parsed == expected_frac


def check_expected_value_answer(user_answer: object, correct_answer_str: str) -> bool:
    """Grade E(X) style answers: accept equivalent fractions and decimals; reject percentages.

    correct_answer_str must be a reduced fraction string (e.g. '3/2') or an integer string.
    """
    ca = str(correct_answer_str or "").strip()
    if not ca:
        return False
    if "/" in ca:
        num_str, den_str = ca.split("/", 1)
        exp_num, exp_den = int(num_str), int(den_str)
    else:
        exp_num, exp_den = int(ca), 1
    return check_rational_answer(
        user_answer,
        exp_num,
        exp_den,
        allow_decimal=True,
        allow_percentage=False,
        validate_probability_range=False,
    )


def check_integer_answer(
    user_answer: object,
    expected: int,
    *,
    allow_negative: bool = False,
) -> bool:
    """Check a student's integer answer (e.g. sample space count, set size).

    Accepts integer or integer-form string; supports full-width digits.
    Rejects decimals (36.0), fractions (1/2), percentages (50%), and
    negative values unless allow_negative=True.

    Returns True if correct, False if wrong or invalid format.
    """
    if user_answer is None:
        return False

    raw = str(user_answer).strip()
    if not raw:
        return False

    raw = _normalize_fullwidth(raw)

    if not re.fullmatch(r"-?\d+", raw):
        return False

    try:
        user_int = int(raw)
    except ValueError:
        return False

    if not allow_negative and user_int < 0:
        return False

    return user_int == expected
