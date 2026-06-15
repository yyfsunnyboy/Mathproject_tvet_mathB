from __future__ import annotations

import re
from fractions import Fraction
from math import gcd
from typing import Any

_BAD_PATTERN = re.compile(r"\^|\*\*|sqrt|sin|cos|tan|log|ln|\|", re.I)
_RATIONAL_RE = re.compile(r"^[+-]?(?:\d+/\d+|\d+)$")
_VAR_TOKEN_RE = re.compile(r"[a-zA-Z]+")


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    replacements = {
        "（": "(",
        "）": ")",
        "，": ",",
        "、": ",",
        "：": ":",
        "－": "-",
        "−": "-",
        "＋": "+",
        "﹣": "-",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = text.replace(" ", "")
    return text


def _parse_rational(token: str) -> Fraction | None:
    token = str(token or "").strip()
    if not token:
        return None
    if not _RATIONAL_RE.fullmatch(token):
        return None
    try:
        return Fraction(token)
    except (ValueError, ZeroDivisionError):
        return None


def _has_invalid_variables(expr: str) -> bool:
    for match in _VAR_TOKEN_RE.finditer(expr):
        if match.group(0).lower() not in {"x", "y"}:
            return True
    return False


def _split_top_level_terms(expr: str) -> list[str]:
    expr = expr.strip()
    if not expr:
        return []
    terms: list[str] = []
    current = ""
    for ch in expr:
        if ch in "+-" and current:
            terms.append(current)
            current = ch
        elif ch in "+-" and not current:
            current = ch
        else:
            current += ch
    if current:
        terms.append(current)
    return terms


def _parse_term(term: str) -> tuple[Fraction, Fraction, Fraction] | None:
    term = term.strip()
    if not term:
        return None
    sign = Fraction(1, 1)
    if term[0] == "+":
        term = term[1:]
    elif term[0] == "-":
        sign = Fraction(-1, 1)
        term = term[1:]
    if not term:
        return None

    var = ""
    if term[-1].lower() in {"x", "y"}:
        var = term[-1].lower()
        num_part = term[:-1]
    else:
        num_part = term

    if var:
        if num_part in {"", "+"}:
            coeff = Fraction(1, 1)
        elif num_part == "-":
            coeff = Fraction(-1, 1)
        else:
            parsed = _parse_rational(num_part)
            if parsed is None:
                return None
            coeff = parsed
        coeff *= sign
        if var == "x":
            return coeff, Fraction(0, 1), Fraction(0, 1)
        return Fraction(0, 1), coeff, Fraction(0, 1)

    parsed = _parse_rational(num_part)
    if parsed is None:
        return None
    return Fraction(0, 1), Fraction(0, 1), parsed * sign


def _add_triples(
    left: tuple[Fraction, Fraction, Fraction],
    right: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1], left[2] + right[2]


def _scale_triple(
    triple: tuple[Fraction, Fraction, Fraction],
    factor: Fraction,
) -> tuple[Fraction, Fraction, Fraction]:
    return triple[0] * factor, triple[1] * factor, triple[2] * factor


def _parse_linear_polynomial(expr: str) -> tuple[Fraction, Fraction, Fraction] | None:
    expanded = _expand_parentheses(expr)
    if expanded is None or _has_invalid_variables(expanded):
        return None
    total = (Fraction(0, 1), Fraction(0, 1), Fraction(0, 1))
    for term in _split_top_level_terms(expanded):
        parsed = _parse_term(term)
        if parsed is None:
            return None
        total = _add_triples(total, parsed)
    return total


def _extract_multiplier(prefix: str) -> tuple[Fraction, str]:
    if not prefix:
        return Fraction(1, 1), prefix
    match = re.search(r"([+-]?(?:\d+/\d+|\d+))$", prefix)
    if match:
        coeff = _parse_rational(match.group(1))
        if coeff is None:
            return None, prefix  # type: ignore[return-value]
        return coeff, prefix[: match.start()]
    if prefix.endswith("-"):
        return Fraction(-1, 1), prefix[:-1]
    if prefix.endswith("+"):
        return Fraction(1, 1), prefix[:-1]
    return Fraction(1, 1), prefix


def _expand_parentheses(expr: str) -> str | None:
    text = expr
    guard = 0
    while "(" in text:
        guard += 1
        if guard > 32:
            return None
        start = text.rfind("(")
        end = text.find(")", start)
        if end < 0:
            return None
        inner = text[start + 1 : end]
        prefix = text[:start]
        suffix = text[end + 1 :]
        mult, prefix_rest = _extract_multiplier(prefix)
        if mult is None:
            return None
        inner_poly = _parse_linear_polynomial(inner)
        if inner_poly is None:
            return None
        expanded_inner = _format_polynomial(_scale_triple(inner_poly, mult))
        if prefix_rest and expanded_inner and expanded_inner[0] not in "+-":
            expanded_inner = f"+{expanded_inner}"
        text = f"{prefix_rest}{expanded_inner}{suffix}"
    return text


def _format_polynomial(triple: tuple[Fraction, Fraction, Fraction]) -> str:
    ax, by, c = triple
    terms: list[str] = []
    for coeff, var in ((ax, "x"), (by, "y")):
        if coeff == 0:
            continue
        if var == "x":
            if coeff == 1:
                terms.append("x")
            elif coeff == -1:
                terms.append("-x")
            else:
                terms.append(f"{coeff}x")
        else:
            if coeff == 1:
                terms.append("y")
            elif coeff == -1:
                terms.append("-y")
            else:
                terms.append(f"{coeff}y")
    if c != 0:
        terms.append(str(c))
    if not terms:
        return "0"
    joined = terms[0]
    for term in terms[1:]:
        if term.startswith("-"):
            joined += term
        else:
            joined += f"+{term}"
    return joined


def _to_general_form_triple(equation: str) -> tuple[Fraction, Fraction, Fraction] | None:
    text = _normalize_text(equation)
    if not text or _BAD_PATTERN.search(text):
        return None
    if "=" not in text:
        return None
    if "x" not in text.lower() and "y" not in text.lower():
        return None
    left, right = text.split("=", 1)
    left_poly = _parse_linear_polynomial(left)
    right_poly = _parse_linear_polynomial(right)
    if left_poly is None or right_poly is None:
        return None
    ax = left_poly[0] - right_poly[0]
    by = left_poly[1] - right_poly[1]
    c = left_poly[2] - right_poly[2]
    if ax == 0 and by == 0:
        return None
    return ax, by, c


def _to_integer_triple(triple: tuple[Fraction, Fraction, Fraction]) -> tuple[int, int, int] | None:
    ax, by, c = triple
    denoms = [ax.denominator, by.denominator, c.denominator]
    lcm = 1
    for d in denoms:
        lcm = lcm * d // gcd(lcm, d)
    a_int = int(ax * lcm)
    b_int = int(by * lcm)
    c_int = int(c * lcm)
    g = gcd(gcd(abs(a_int), abs(b_int)), abs(c_int))
    if g == 0:
        return None
    a_int //= g
    b_int //= g
    c_int //= g
    return a_int, b_int, c_int


def _triples_proportional(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> bool:
    a1, b1, c1 = left
    a2, b2, c2 = right
    cross = [
        a1 * b2 - a2 * b1,
        a1 * c2 - a2 * c1,
        b1 * c2 - b2 * c1,
    ]
    return all(v == 0 for v in cross)


def canonicalize_linear_equation(value: Any) -> tuple[int, int, int] | None:
    triple = _to_general_form_triple(str(value or ""))
    if triple is None:
        return None
    return _to_integer_triple(triple)


def check_linear_equation_equivalent_answer(user_answer: Any, correct_answer: Any) -> bool:
    user_triple = canonicalize_linear_equation(user_answer)
    correct_triple = canonicalize_linear_equation(correct_answer)
    if user_triple is None or correct_triple is None:
        return False
    return _triples_proportional(user_triple, correct_triple)
