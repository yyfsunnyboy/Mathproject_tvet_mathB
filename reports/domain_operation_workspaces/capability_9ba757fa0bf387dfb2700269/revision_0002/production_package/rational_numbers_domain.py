"""Exact, seed-deterministic operations for the number_system.rational_numbers domain.

Each operation is one shared implementation.  Source items supply their inputs
through ``constraints``; seeded generation produces inputs of the same shape.
Rendering and answer topology belong to the adapter module.
"""

from __future__ import annotations

import copy
import random
import re
from fractions import Fraction
from math import gcd, isqrt
from typing import Any, Callable

DOMAIN_KEY = "number_system.rational_numbers"

_DECIMAL = re.compile(r"^([+-]?)(\d+)(?:\.(\d*))?$")
_REPEATING = re.compile(r"^([+-]?)(\d+)\.(\d*)\((\d+)\)$")
_TERMINATING_DENOMINATORS = (2, 4, 5, 8, 10, 16, 20, 25, 40, 50)
_REPEATING_DENOMINATORS = (3, 6, 7, 9, 11, 12, 13, 15, 22, 27, 33, 37)
_NON_SQUARES = (2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15)
_SQUARES = (1, 4, 9, 16, 25, 36, 49, 64, 81, 100)


# --- exact arithmetic -------------------------------------------------------

def parse_exact_rational(value: Any) -> Fraction:
    """Parse an int, Fraction, ``a/b``, finite decimal or ``1.4(5)`` repeating decimal."""
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
    repeating = _REPEATING.fullmatch(text)
    if repeating:
        sign, whole, nonrepeating, cycle = repeating.groups()
        scale = 10 ** len(nonrepeating)
        exact = Fraction(int(whole)) + Fraction(int(nonrepeating or "0"), scale)
        exact += Fraction(int(cycle), scale * (10 ** len(cycle) - 1))
        return -exact if sign == "-" else exact
    finite = _DECIMAL.fullmatch(text)
    if not finite:
        raise ValueError(f"unsupported exact rational notation: {value!r}")
    sign, whole, tail = finite.groups()
    exact = Fraction(int(whole))
    if tail:
        exact += Fraction(int(tail), 10 ** len(tail))
    return -exact if sign == "-" else exact


def canonical_fraction(value: Any) -> str:
    exact = parse_exact_rational(value)
    return str(exact.numerator) if exact.denominator == 1 else f"{exact.numerator}/{exact.denominator}"


def decimal_notation(value: Any) -> str:
    """Return a finite or parenthesized repeating decimal string, rejecting fraction notation."""
    text = str(value).strip().replace(" ", "")
    if not (_DECIMAL.fullmatch(text) or _REPEATING.fullmatch(text)):
        raise ValueError(f"not a decimal notation: {value!r}")
    return text


def has_terminating_expansion(value: Any) -> bool:
    denominator = parse_exact_rational(value).denominator
    for prime in (2, 5):
        while denominator % prime == 0:
            denominator //= prime
    return denominator == 1


def fraction_to_decimal_expansion(value: Any) -> dict[str, Any]:
    """Long division with a remainder map: shortest pre-period, shortest period."""
    exact = parse_exact_rational(value)
    sign = "-" if exact < 0 else ""
    magnitude = abs(exact)
    whole, remainder = divmod(magnitude.numerator, magnitude.denominator)
    digits: list[str] = []
    seen: dict[int, int] = {}
    while remainder and remainder not in seen:
        seen[remainder] = len(digits)
        digit, remainder = divmod(remainder * 10, magnitude.denominator)
        digits.append(str(digit))
    if remainder:
        start = seen[remainder]
        nonrepeating, cycle = "".join(digits[:start]), "".join(digits[start:])
        decimal, kind = f"{sign}{whole}.{nonrepeating}({cycle})", "repeating"
    else:
        nonrepeating, cycle = "".join(digits), ""
        decimal = f"{sign}{whole}.{nonrepeating}" if digits else f"{sign}{whole}"
        kind = "terminating"
    return {
        "fraction": canonical_fraction(exact),
        "decimal": decimal,
        "kind": kind,
        "nonrepeating": nonrepeating,
        "cycle": cycle,
    }


def decimal_to_simplest_fraction(value: Any) -> dict[str, Any]:
    exact = parse_exact_rational(decimal_notation(value))
    return {
        "decimal": decimal_notation(value),
        "fraction": canonical_fraction(exact),
        "numerator": exact.numerator,
        "denominator": exact.denominator,
    }


def is_strictly_between(candidate: Any, lower: Any, upper: Any) -> bool:
    return parse_exact_rational(lower) < parse_exact_rational(candidate) < parse_exact_rational(upper)


def construct_rational_between_bounds(lower: Any, upper: Any) -> dict[str, Any]:
    low, high = parse_exact_rational(lower), parse_exact_rational(upper)
    if not low < high:
        raise ValueError("lower bound must be strictly less than upper bound")
    bounds = {"lower": canonical_fraction(low), "upper": canonical_fraction(high)}
    return {
        **bounds,
        "example": canonical_fraction((low + high) / 2),
        "predicate": {"relation": "strict_between", **bounds},
    }


def plot_rational_points_on_number_line(points: list[Any], labels: list[str] | None = None) -> dict[str, Any]:
    exact = [parse_exact_rational(point) for point in points]
    if not exact:
        raise ValueError("number line needs at least one point")
    names = list(labels) if labels else [chr(ord("A") + index) for index in range(len(exact))]
    if len(names) != len(exact) or len(set(names)) != len(names) or not all(str(n).strip() for n in names):
        raise ValueError("number line labels must be unique and match the points")
    return {
        "coordinate_system": "number_line",
        "points": [{"label": str(name), "value": canonical_fraction(value)} for name, value in zip(names, exact)],
        "ordered_points": [canonical_fraction(value) for value in sorted(exact)],
    }


def _descriptor_value(descriptor: dict[str, Any]) -> Fraction | None:
    kind = descriptor["kind"]
    if kind == "rational":
        return parse_exact_rational(descriptor["value"])
    if kind in {"finite_decimal", "repeating_decimal"}:
        return parse_exact_rational(decimal_notation(descriptor["value"]))
    if kind == "sqrt":
        radicand = int(descriptor["radicand"])
        if radicand < 0:
            raise ValueError("sqrt radicand must be non-negative")
        root = isqrt(radicand)
        return Fraction(root) if root * root == radicand else None
    if kind == "sum":
        # Terms are rationals and non-negative square roots: a sum of square roots of
        # non-negative integers is rational only when every root is rational.
        values = [_descriptor_value(term) for term in descriptor["terms"]]
        if not values:
            raise ValueError("sum descriptor needs terms")
        return sum(values, Fraction(0)) if all(value is not None for value in values) else None
    raise ValueError(f"unsupported rationality descriptor kind: {kind}")


def is_rational_descriptor(descriptor: dict[str, Any]) -> bool:
    return _descriptor_value(descriptor) is not None


def identify_rational_numbers(candidates: list[dict[str, Any]]) -> list[int]:
    """One-based positions of every rational candidate."""
    return [index for index, candidate in enumerate(candidates, start=1) if is_rational_descriptor(candidate)]


def evaluate_rationality_statements(statements: list[dict[str, Any]]) -> list[bool]:
    outcomes: list[bool] = []
    for statement in statements:
        predicate = statement["predicate"]
        if predicate == "is_rational":
            actual = is_rational_descriptor(statement["value"])
        elif predicate == "is_irrational":
            actual = not is_rational_descriptor(statement["value"])
        elif predicate == "equals":
            left, right = _descriptor_value(statement["left"]), _descriptor_value(statement["right"])
            if left is None or right is None:
                raise ValueError("equals statements compare rational descriptors only")
            actual = left == right
        elif predicate == "no_rational_between":
            actual = not parse_exact_rational(statement["lower"]) < parse_exact_rational(statement["upper"])
        elif predicate == "all_irrational":
            actual = all(not is_rational_descriptor(value) for value in statement["values"])
        elif predicate == "sqrt_difference_identity":
            # sqrt((sqrt(a) - sqrt(b))^2) = |sqrt(a) - sqrt(b)|, which equals sqrt(a) - sqrt(b) iff a >= b.
            actual = int(statement["left_radicand"]) >= int(statement["right_radicand"])
        else:
            raise ValueError(f"unsupported statement predicate: {predicate}")
        outcomes.append(bool(actual))
    return outcomes


# --- seeded inputs ----------------------------------------------------------

def _coprime_numerator(rng: random.Random, denominator: int, limit: int) -> int:
    while True:
        numerator = rng.randint(1, limit)
        if gcd(numerator, denominator) == 1:
            return numerator


def _seed_fractions(rng: random.Random) -> list[str]:
    denominators = [rng.choice(_TERMINATING_DENOMINATORS), rng.choice(_REPEATING_DENOMINATORS)]
    rng.shuffle(denominators)
    return [canonical_fraction(Fraction(_coprime_numerator(rng, q, 2 * q - 1), q)) for q in denominators]


def _seed_bounds(rng: random.Random) -> tuple[str, str]:
    denominator = rng.randint(2, 9)
    lower = Fraction(rng.randint(-3 * denominator, 3 * denominator), denominator)
    upper = lower + Fraction(1, rng.choice((denominator, denominator + 1, 2 * denominator)))
    return canonical_fraction(lower), canonical_fraction(upper)


def _seed_descriptor(rng: random.Random, rational: bool) -> dict[str, Any]:
    if not rational:
        if rng.random() < 0.5:
            return {"kind": "sqrt", "radicand": rng.choice(_NON_SQUARES)}
        return {
            "kind": "sum",
            "terms": [{"kind": "rational", "value": str(rng.randint(1, 5))}, {"kind": "sqrt", "radicand": rng.choice(_NON_SQUARES)}],
        }
    kind = rng.choice(("rational", "finite_decimal", "repeating_decimal", "sqrt"))
    if kind == "rational":
        q = rng.randint(2, 9)
        return {"kind": "rational", "value": canonical_fraction(Fraction(rng.choice((1, -1)) * _coprime_numerator(rng, q, 3 * q), q))}
    if kind == "finite_decimal":
        numerator = _coprime_numerator(rng, 10, 999)
        return {"kind": "finite_decimal", "value": fraction_to_decimal_expansion(Fraction(numerator, rng.choice((10, 100, 1000))))["decimal"]}
    if kind == "repeating_decimal":
        q = rng.choice(_REPEATING_DENOMINATORS)
        return {"kind": "repeating_decimal", "value": fraction_to_decimal_expansion(Fraction(_coprime_numerator(rng, q, q - 1), q))["decimal"]}
    return {"kind": "sqrt", "radicand": rng.choice(_SQUARES)}


def _seed_statements(rng: random.Random) -> list[dict[str, Any]]:
    def is_rational() -> dict[str, Any]:
        return {"predicate": "is_rational", "value": _seed_descriptor(rng, rng.random() < 0.5)}

    def is_irrational() -> dict[str, Any]:
        return {"predicate": "is_irrational", "value": _seed_descriptor(rng, rng.random() < 0.5)}

    def equals() -> dict[str, Any]:
        digit = rng.randint(1, 8)
        terms = [
            {"kind": "repeating_decimal", "value": f"0.({digit})"},
            {"kind": "repeating_decimal", "value": f"0.({9 - digit})"},
        ]
        right = {"kind": "rational", "value": "1"} if rng.random() < 0.5 else {"kind": "finite_decimal", "value": "0.9"}
        return {"predicate": "equals", "left": {"kind": "sum", "terms": terms}, "right": right}

    def no_rational_between() -> dict[str, Any]:
        lower, upper = _seed_bounds(rng)
        return {"predicate": "no_rational_between", "lower": lower, "upper": upper}

    def all_irrational() -> dict[str, Any]:
        first = {"kind": "sqrt", "radicand": rng.choice(_NON_SQUARES)}
        second = _seed_descriptor(rng, rng.random() < 0.5)
        return {"predicate": "all_irrational", "values": [first, second]}

    def sqrt_difference_identity() -> dict[str, Any]:
        left, right = rng.sample(_NON_SQUARES, 2)
        return {"predicate": "sqrt_difference_identity", "left_radicand": left, "right_radicand": right}

    makers = [is_rational, is_irrational, equals, no_rational_between, all_irrational, sqrt_difference_identity]
    return [makers[index]() for index in rng.sample(range(len(makers)), 4)]


def _seed_candidates(rng: random.Random) -> list[dict[str, Any]]:
    flags = [rng.random() < 0.5 for _ in range(5)]
    if all(flags) or not any(flags):
        position = rng.randrange(len(flags))
        flags[position] = not flags[position]
    return [_seed_descriptor(rng, flag) for flag in flags]


def _seed_points(rng: random.Random) -> list[str]:
    denominator = rng.choice((2, 3, 4, 5, 6))
    count = rng.choice((2, 3))
    values: list[Fraction] = []
    while len(values) < count:
        value = Fraction(rng.choice([n for n in range(-2 * denominator, 2 * denominator + 1) if n]), denominator)
        if value not in values:
            values.append(value)
    return [canonical_fraction(value) for value in values]


# --- givens / operation table ----------------------------------------------

def _supplied_list(constraints: dict[str, Any], key: str, seeded: Callable[[], list[Any]]) -> list[Any]:
    values = constraints.get(key)
    values = seeded() if values is None else copy.deepcopy(values)
    if not isinstance(values, list) or not values:
        raise ValueError(f"constraint {key} must be a non-empty list")
    return values


def _fraction_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    fractions = _supplied_list(constraints, "fractions", lambda: _seed_fractions(rng))
    return {"fractions": [canonical_fraction(value) for value in fractions]}


def _decimal_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    def seeded() -> list[str]:
        return [fraction_to_decimal_expansion(value)["decimal"] for value in _seed_fractions(rng)]

    return {"decimals": [decimal_notation(value) for value in _supplied_list(constraints, "decimals", seeded)]}


def _points_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    points = [canonical_fraction(value) for value in _supplied_list(constraints, "points", lambda: _seed_points(rng))]
    labels = constraints.get("labels")
    labels = [str(label) for label in labels] if labels else [chr(ord("A") + index) for index in range(len(points))]
    return {"points": points, "labels": labels}


def _bounds_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("lower") is not None and constraints.get("upper") is not None:
        lower, upper = constraints["lower"], constraints["upper"]
    else:
        lower, upper = _seed_bounds(rng)
    return {"lower": canonical_fraction(lower), "upper": canonical_fraction(upper)}


def _statement_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    return {"statements": _supplied_list(constraints, "statements", lambda: _seed_statements(rng))}


def _candidate_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    return {"candidates": _supplied_list(constraints, "candidates", lambda: _seed_candidates(rng))}


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "fraction_to_decimal_expansion": (
        _fraction_givens,
        lambda g: {"parts": [fraction_to_decimal_expansion(value) for value in g["fractions"]]},
    ),
    "decimal_to_simplest_fraction": (
        _decimal_givens,
        lambda g: {"parts": [decimal_to_simplest_fraction(value) for value in g["decimals"]]},
    ),
    "plot_rational_points_on_number_line": (
        _points_givens,
        lambda g: plot_rational_points_on_number_line(g["points"], g["labels"]),
    ),
    "construct_rational_between_bounds": (
        _bounds_givens,
        lambda g: construct_rational_between_bounds(g["lower"], g["upper"]),
    ),
    "evaluate_rationality_statements": (
        _statement_givens,
        lambda g: {"truth_values": evaluate_rationality_statements(g["statements"])},
    ),
    "identify_rational_numbers": (
        _candidate_givens,
        lambda g: {"indices": identify_rational_numbers(g["candidates"])},
    ),
}
OPERATIONS = tuple(_OPERATIONS)


def build_rational_numbers_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_rational_numbers_operation:{operation}")
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


@_validator("fraction_to_decimal_expansion")
def validate_fraction_to_decimal_expansion_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    fractions, parts = givens["fractions"], answer["parts"]
    if not fractions or len(parts) != len(fractions):
        return False
    for fraction, part in zip(fractions, parts):
        exact = parse_exact_rational(fraction)
        decimal, nonrepeating, cycle = part["decimal"], part["nonrepeating"], part["cycle"]
        if part["fraction"] != fraction or canonical_fraction(exact) != fraction:
            return False
        if part["kind"] != ("terminating" if has_terminating_expansion(exact) else "repeating"):
            return False
        fractional = decimal.partition(".")[2]
        if part["kind"] == "repeating":
            if not cycle or fractional != f"{nonrepeating}({cycle})" or set(cycle) <= {"0"} or set(cycle) == {"9"}:
                return False
            if any(cycle == cycle[:d] * (len(cycle) // d) for d in range(1, len(cycle)) if len(cycle) % d == 0):
                return False
            if nonrepeating and nonrepeating[-1] == cycle[-1]:
                return False
        elif cycle or fractional != nonrepeating or nonrepeating.endswith("0"):
            return False
        if parse_exact_rational(decimal) != exact:
            return False
    return True


@_validator("decimal_to_simplest_fraction")
def validate_decimal_to_simplest_fraction_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    decimals, parts = givens["decimals"], answer["parts"]
    if not decimals or len(parts) != len(decimals):
        return False
    for decimal, part in zip(decimals, parts):
        numerator, denominator = part["numerator"], part["denominator"]
        if part["decimal"] != decimal or decimal_notation(decimal) != decimal:
            return False
        if type(numerator) is not int or type(denominator) is not int or denominator <= 0:
            return False
        if gcd(abs(numerator), denominator) != 1 or part["fraction"] != canonical_fraction(Fraction(numerator, denominator)):
            return False
        if Fraction(numerator, denominator) != parse_exact_rational(decimal):
            return False
    return True


@_validator("plot_rational_points_on_number_line")
def validate_plot_rational_points_on_number_line_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    points, labels = givens["points"], givens["labels"]
    plotted = answer["points"]
    if answer["coordinate_system"] != "number_line" or not points or len(plotted) != len(points):
        return False
    if [p["label"] for p in plotted] != labels or len(set(labels)) != len(labels):
        return False
    if [p["value"] for p in plotted] != [canonical_fraction(point) for point in points]:
        return False
    return answer["ordered_points"] == [canonical_fraction(v) for v in sorted(parse_exact_rational(p) for p in points)]


@_validator("construct_rational_between_bounds")
def validate_construct_rational_between_bounds_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    lower, upper, example = answer["lower"], answer["upper"], answer["example"]
    if (lower, upper) != (givens["lower"], givens["upper"]) or canonical_fraction(example) != example:
        return False
    if answer["predicate"] != {"relation": "strict_between", "lower": lower, "upper": upper}:
        return False
    return is_strictly_between(example, lower, upper)


@_validator("evaluate_rationality_statements")
def validate_evaluate_rationality_statements_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    statements, truth_values = givens["statements"], answer["truth_values"]
    if not statements or len(truth_values) != len(statements) or not all(type(v) is bool for v in truth_values):
        return False
    return truth_values == evaluate_rationality_statements(statements)


@_validator("identify_rational_numbers")
def validate_identify_rational_numbers_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    candidates, indices = givens["candidates"], answer["indices"]
    if not indices or not all(type(i) is int and 1 <= i <= len(candidates) for i in indices):
        return False
    if indices != sorted(set(indices)):
        return False
    return indices == identify_rational_numbers(candidates)
