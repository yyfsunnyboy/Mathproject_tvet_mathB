"""Exact, deterministic candidate implementation for rational-number operations.

This file is intentionally isolated in a review workspace.  It is not imported by
production runtime code.
"""

from fractions import Fraction
from math import isqrt
import re


_DECIMAL = re.compile(r"^([+-]?)(\d+)(?:\.(\d*))?$")
_REPEATING = re.compile(r"^([+-]?)(\d+)\.(\d*)\((\d+)\)$")


def parse_exact_rational(value):
    """Parse an integer, finite decimal, fraction, or `1.4(5)` repeating decimal."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str):
        raise TypeError("exact rational input must be int, Fraction, or string")
    text = value.strip().replace(" ", "")
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    repeating = _REPEATING.fullmatch(text)
    if repeating:
        sign, whole, nonrepeat, cycle = repeating.groups()
        scale = 10 ** len(nonrepeat)
        value_fraction = Fraction(int(whole)) + Fraction(int(nonrepeat or "0"), scale)
        value_fraction += Fraction(int(cycle), scale * (10 ** len(cycle) - 1))
        return -value_fraction if sign == "-" else value_fraction
    finite = _DECIMAL.fullmatch(text)
    if not finite:
        raise ValueError("unsupported exact rational notation")
    sign, whole, tail = finite.groups()
    value_fraction = Fraction(int(whole))
    if tail:
        value_fraction += Fraction(int(tail), 10 ** len(tail))
    return -value_fraction if sign == "-" else value_fraction


def canonical_fraction(value):
    value = parse_exact_rational(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def fraction_to_decimal_expansion(numerator, denominator=None):
    """Return a canonical terminating or parenthesized repeating decimal expansion."""
    value = Fraction(numerator, denominator) if denominator is not None else parse_exact_rational(numerator)
    sign = "-" if value < 0 else ""
    value = abs(value)
    whole, remainder = divmod(value.numerator, value.denominator)
    digits, seen = [], {}
    while remainder and remainder not in seen:
        seen[remainder] = len(digits)
        remainder *= 10
        digit, remainder = divmod(remainder, value.denominator)
        digits.append(str(digit))
    if not digits:
        return {"decimal": f"{sign}{whole}", "kind": "terminating", "cycle": ""}
    if not remainder:
        return {"decimal": f"{sign}{whole}." + "".join(digits), "kind": "terminating", "cycle": ""}
    cycle_start = seen[remainder]
    nonrepeat = "".join(digits[:cycle_start])
    cycle = "".join(digits[cycle_start:])
    return {"decimal": f"{sign}{whole}.{nonrepeat}({cycle})", "kind": "repeating", "cycle": cycle}


def decimal_to_simplest_fraction(value):
    return canonical_fraction(parse_exact_rational(value))


def construct_rational_between_bounds(lower, upper):
    lower, upper = parse_exact_rational(lower), parse_exact_rational(upper)
    if not lower < upper:
        raise ValueError("lower must be strictly less than upper")
    return canonical_fraction((lower + upper) / 2)


def is_strictly_between(candidate, lower, upper):
    candidate = parse_exact_rational(candidate)
    return parse_exact_rational(lower) < candidate < parse_exact_rational(upper)


def _descriptor_value(descriptor):
    kind = descriptor["kind"]
    if kind in {"rational", "finite_decimal", "repeating_decimal"}:
        return parse_exact_rational(descriptor["value"])
    if kind == "sqrt":
        radicand = int(descriptor["radicand"])
        root = isqrt(radicand)
        return Fraction(root) if root * root == radicand else None
    if kind == "sum":
        values = [_descriptor_value(term) for term in descriptor["terms"]]
        return sum(values, Fraction()) if all(value is not None for value in values) else None
    raise ValueError(f"unsupported rationality descriptor kind: {kind}")


def classify_rational_expression(descriptor):
    """Classify a restricted structural expression without evaluating source text heuristically."""
    return _descriptor_value(descriptor) is not None


def identify_rational_numbers(candidates):
    """Return one-based positions of all rational candidates; response topology is adapter-owned."""
    return tuple(index for index, candidate in enumerate(candidates, start=1) if classify_rational_expression(candidate))


def evaluate_rationality_statements(statements):
    """Evaluate a small exact statement DSL used by rational-number instructional items."""
    outcomes = []
    for statement in statements:
        predicate = statement["predicate"]
        if predicate == "is_rational":
            actual = classify_rational_expression(statement["value"])
        elif predicate == "is_irrational":
            actual = not classify_rational_expression(statement["value"])
        elif predicate == "equals":
            actual = _descriptor_value(statement["left"]) == _descriptor_value(statement["right"])
        elif predicate == "no_rational_between":
            actual = not parse_exact_rational(statement["lower"]) < parse_exact_rational(statement["upper"])
        elif predicate == "all_irrational":
            actual = all(not classify_rational_expression(value) for value in statement["values"])
        elif predicate == "sqrt_difference_identity":
            # sqrt((sqrt(a)-sqrt(b))^2) equals sqrt(a)-sqrt(b) iff a >= b.
            actual = int(statement["left_radicand"]) >= int(statement["right_radicand"])
        else:
            raise ValueError(f"unsupported statement predicate: {predicate}")
        outcomes.append(bool(actual))
    return tuple(outcomes)


def plot_rational_points_on_number_line(points):
    """Provide exact semantic coordinates; rendering remains the presentation layer's job."""
    exact_points = [parse_exact_rational(point) for point in points]
    return {
        "coordinate_system": "number_line",
        "points": [canonical_fraction(point) for point in exact_points],
        "ordered_points": [canonical_fraction(point) for point in sorted(exact_points)],
    }
