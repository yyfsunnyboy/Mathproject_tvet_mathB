"""Exact, seed-deterministic operations for the number_system.real_numbers domain.

Each operation is one shared implementation.  Source items supply their inputs
through ``constraints``; seeded generation produces inputs of the same shape.
Rendering and answer topology belong to the adapter module.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction
from math import isqrt
from typing import Any, Callable

DOMAIN_KEY = "number_system.real_numbers"

_DECIMAL = re.compile(r"^([+-]?)(\d+)(?:\.(\d+))?$")
_NON_SQUARES = (2, 3, 5, 6, 7, 10, 11)
_APPROXIMATION_MODES = ("truncate",)


# --- exact arithmetic -------------------------------------------------------

def parse_exact_rational(value: Any) -> Fraction:
    """Parse an int, Fraction, ``a/b`` or finite decimal string exactly."""
    if isinstance(value, bool):
        raise TypeError("boolean is not a rational input")
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
    finite = _DECIMAL.fullmatch(text)
    if not finite:
        raise ValueError(f"unsupported exact rational notation: {value!r}")
    sign, whole, tail = finite.groups()
    exact = Fraction(int(whole)) + (Fraction(int(tail), 10 ** len(tail)) if tail else 0)
    return -exact if sign == "-" else exact


def canonical_rational(value: Any) -> str:
    exact = parse_exact_rational(value)
    return str(exact.numerator) if exact.denominator == 1 else f"{exact.numerator}/{exact.denominator}"


def is_perfect_square(n: int) -> bool:
    return n >= 0 and isqrt(n) ** 2 == n


def _require_non_square_radicand(radicand: Any) -> int:
    if type(radicand) is not int or radicand <= 1 or is_perfect_square(radicand):
        raise ValueError(f"radicand must be a positive non-square integer: {radicand!r}")
    return radicand


def fixed_decimal(scaled: int, places: int) -> str:
    """Render ``scaled / 10**places`` with exactly ``places`` decimal digits."""
    sign = "-" if scaled < 0 else ""
    digits = str(abs(scaled)).rjust(places + 1, "0")
    if places == 0:
        return f"{sign}{digits}"
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


# --- operations ---------------------------------------------------------------

def _radical_number(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError("radical number must be {'rational': r, 'radical': s}")
    return {
        "rational": canonical_rational(value.get("rational", 0)),
        "radical": canonical_rational(value.get("radical", 0)),
    }


def solve_rational_unknowns_from_radical_identity(
    radicand: int,
    coefficients: dict[str, Any],
    rhs: dict[str, Any],
) -> dict[str, Any]:
    """Solve Σ (p_i + q_i·√n)·x_i = r + s·√n for rational unknowns x_i.

    Because √n is irrational and every x_i is rational, the identity holds exactly
    when the rational parts and the √n parts agree separately:
    Σ p_i·x_i = r and Σ q_i·x_i = s.  Two equations determine two unknowns.
    """
    n = _require_non_square_radicand(radicand)
    if not isinstance(coefficients, dict) or len(coefficients) != 2:
        raise ValueError("exactly two rational unknowns are required")
    names = list(coefficients)
    coeffs = {name: _radical_number(coefficients[name]) for name in names}
    target = _radical_number(rhs)
    (p1, q1), (p2, q2) = (
        (parse_exact_rational(coeffs[name]["rational"]), parse_exact_rational(coeffs[name]["radical"])) for name in names
    )
    r, s = parse_exact_rational(target["rational"]), parse_exact_rational(target["radical"])
    determinant = p1 * q2 - p2 * q1
    if determinant == 0:
        raise ValueError("rational and radical part equations are dependent")
    first = (r * q2 - p2 * s) / determinant
    second = (p1 * s - r * q1) / determinant
    values = {names[0]: canonical_rational(first), names[1]: canonical_rational(second)}
    return {
        "radicand": n,
        "unknowns": names,
        "values": values,
        "rational_part_equation": {"coefficients": {name: coeffs[name]["rational"] for name in names}, "constant": target["rational"]},
        "radical_part_equation": {"coefficients": {name: coeffs[name]["radical"] for name in names}, "constant": target["radical"]},
    }


def approximate_square_root_by_decimal_search(radicand: int, places: int, mode: str = "truncate") -> dict[str, Any]:
    """十分逼近法: narrow √n one decimal place at a time using exact integer squares.

    At place d the bracket is [k/10^d, (k+1)/10^d] with k = isqrt(n·100^d), so
    (k/10^d)² ≤ n < ((k+1)/10^d)².  Truncation to ``places`` digits is the lower end.
    """
    n = _require_non_square_radicand(radicand)
    if type(places) is not int or not 0 <= places <= 4:
        raise ValueError("places must be an integer between 0 and 4")
    if mode not in _APPROXIMATION_MODES:
        raise ValueError(f"unsupported approximation mode: {mode!r}")
    steps = []
    for place in range(places + 1):
        lower = isqrt(n * 100 ** place)
        steps.append({
            "place": place,
            "lower": fixed_decimal(lower, place),
            "upper": fixed_decimal(lower + 1, place),
            "lower_square": fixed_decimal(lower * lower, 2 * place),
            "upper_square": fixed_decimal((lower + 1) ** 2, 2 * place),
        })
    return {
        "radicand": n,
        "places": places,
        "mode": mode,
        "approximation": steps[-1]["lower"],
        "steps": steps,
    }


# --- givens -----------------------------------------------------------------

def _identity_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("coefficients") is not None and constraints.get("rhs") is not None:
        return {
            "radicand": _require_non_square_radicand(constraints.get("radicand", 2)),
            "coefficients": {str(k): _radical_number(v) for k, v in constraints["coefficients"].items()},
            "rhs": _radical_number(constraints["rhs"]),
        }
    while True:
        radicand = rng.choice(_NON_SQUARES[:3])
        p1, q1, p2, q2 = (rng.choice([v for v in range(-6, 7) if v]) for _ in range(4))
        if p1 * q2 - p2 * q1 == 0:
            continue
        a, b = rng.randint(-5, 5), rng.randint(-5, 5)
        return {
            "radicand": radicand,
            "coefficients": {"a": _radical_number({"rational": p1, "radical": q1}), "b": _radical_number({"rational": p2, "radical": q2})},
            "rhs": _radical_number({"rational": p1 * a + p2 * b, "radical": q1 * a + q2 * b}),
        }


def _approximation_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("radicand") is not None:
        radicand = constraints["radicand"]
    else:
        radicand = rng.choice(_NON_SQUARES)
    return {
        "radicand": _require_non_square_radicand(radicand),
        "places": int(constraints.get("places", 2)),
        "mode": str(constraints.get("mode", "truncate")),
    }


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "solve_rational_unknowns_from_radical_identity": (
        _identity_givens,
        lambda g: solve_rational_unknowns_from_radical_identity(g["radicand"], g["coefficients"], g["rhs"]),
    ),
    "approximate_square_root_by_decimal_search": (
        _approximation_givens,
        lambda g: approximate_square_root_by_decimal_search(g["radicand"], g["places"], g["mode"]),
    ),
}
OPERATIONS = tuple(_OPERATIONS)


def build_real_numbers_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_real_numbers_operation:{operation}")
    seed_value = 0 if seed is None else int(seed)
    rng = random.Random(f"{DOMAIN_KEY}:{operation}:{seed_value}")
    make_givens, solve = _OPERATIONS[operation]
    givens = make_givens(constraints if isinstance(constraints, dict) else {}, rng)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": solve(givens),
        "validation_facts": {"domain_operation": operation, "seed": seed_value},
    }


# --- validators (contract integrity; never raise) ---------------------------

def _validator(operation: str) -> Callable[[Callable[[dict[str, Any], dict[str, Any]], bool]], Callable[[Any], bool]]:
    def wrap(check: Callable[[dict[str, Any], dict[str, Any]], bool]) -> Callable[[Any], bool]:
        def validate(matrix: Any) -> bool:
            try:
                facts = matrix.get("validation_facts") or {}
                if (
                    matrix.get("domain") != DOMAIN_KEY
                    or matrix.get("domain_operation") != operation
                    or facts.get("domain_operation") != operation
                ):
                    return False
                return bool(check(matrix["givens"], matrix["answer"]))
            except Exception:
                return False

        validate.__name__ = check.__name__
        validate.__doc__ = check.__doc__
        return validate

    return wrap


@_validator("solve_rational_unknowns_from_radical_identity")
def validate_solve_rational_unknowns_from_radical_identity_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n = _require_non_square_radicand(givens["radicand"])
    names = answer["unknowns"]
    if names != list(givens["coefficients"]) or answer["radicand"] != n or set(answer["values"]) != set(names):
        return False
    values = {name: parse_exact_rational(answer["values"][name]) for name in names}
    if any(canonical_rational(values[name]) != answer["values"][name] for name in names):
        return False
    rational_side = sum(parse_exact_rational(givens["coefficients"][x]["rational"]) * values[x] for x in names)
    radical_side = sum(parse_exact_rational(givens["coefficients"][x]["radical"]) * values[x] for x in names)
    return (
        rational_side == parse_exact_rational(givens["rhs"]["rational"])
        and radical_side == parse_exact_rational(givens["rhs"]["radical"])
    )


@_validator("approximate_square_root_by_decimal_search")
def validate_approximate_square_root_by_decimal_search_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, places = _require_non_square_radicand(givens["radicand"]), givens["places"]
    steps = answer["steps"]
    if (answer["radicand"], answer["places"], answer["mode"]) != (n, places, givens["mode"]) or len(steps) != places + 1:
        return False
    for place, step in enumerate(steps):
        lower, upper = parse_exact_rational(step["lower"]), parse_exact_rational(step["upper"])
        if step["place"] != place or upper - lower != Fraction(1, 10 ** place):
            return False
        if not lower * lower <= n < upper * upper:
            return False
        if parse_exact_rational(step["lower_square"]) != lower * lower or parse_exact_rational(step["upper_square"]) != upper * upper:
            return False
    approximation = answer["approximation"]
    return approximation == steps[-1]["lower"] and len(approximation.partition(".")[2]) == places
