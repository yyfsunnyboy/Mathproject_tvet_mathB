"""Exact, seed-deterministic operations for the algebra.radical_operations domain.

Radical arithmetic (squarefree normalization, products, like-term collection) is
delegated to the promoted ``algebra.multiplication_formulas`` radical simplifier;
this domain adds conjugate rationalization, square-root denesting, exact ordering
and the AM-GM / formula applications built on it.  Source items supply their
inputs through ``constraints``; seeded generation produces inputs of the same shape.
Rendering and answer topology belong to the adapter module.

Structured inputs
-----------------
radical sum   ``[[coefficient, radicand], ...]`` meaning Σ c·√r (r = "1" is rational)
factor        a radical sum, or ``{"terms": radical sum, "power": k}``
term          ``{"coefficient": c?, "numerator": [factor, ...]?, "denominator": [factor, ...]?}``
expression    ``[term, ...]`` (a sum of terms)
nested root   ``{"rational": p, "radical": [k, q]}`` meaning √(p + k·√q)
"""

from __future__ import annotations

import random
from fractions import Fraction
from functools import cmp_to_key
from math import isqrt
from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_domain import (
    canonical_rational,
    parse_exact_rational,
    radical_plain,
    serialize_radical_value,
    simplify_radical_expression,
)

DOMAIN_KEY = "algebra.radical_operations"

_MAX_PARTS = 4
_MAX_TERMS = 6
_MAX_POWER = 4
_LABELS = "abcdefgh"

Value = dict[int, Fraction]


# --- exact radical values (Σ c·√m, m squarefree) ------------------------------

def _value(serialized: Any) -> Value:
    out: Value = {}
    for coefficient, radicand in serialized:
        c = parse_exact_rational(coefficient)
        if c:
            out[int(radicand)] = out.get(int(radicand), Fraction(0)) + c
    return {m: c for m, c in out.items() if c}


def _sum_of(value: Value) -> list[list[Any]]:
    return [[canonical_rational(c), m] for m, c in sorted(value.items())]


def _evaluate(products: list[dict[str, Any]]) -> Value:
    return _value(simplify_radical_expression(products)["value"])


def _mul(u: Value, v: Value) -> Value:
    if not u or not v:
        return {}
    return _evaluate([{"factors": [_sum_of(u), _sum_of(v)]}])


def _add(*values: Value) -> Value:
    out: Value = {}
    for value in values:
        for m, c in value.items():
            out[m] = out.get(m, Fraction(0)) + c
    return {m: c for m, c in out.items() if c}


def _scale(value: Value, factor: Fraction) -> Value:
    return {m: c * factor for m, c in value.items() if c * factor}


def _rational(q: Any) -> Value:
    q = Fraction(q)
    return {1: q} if q else {}


def serialize_value(value: Value) -> list[list[Any]]:
    return serialize_radical_value(value)


def value_plain(value: Value) -> str:
    return radical_plain(value)


def rational_square_root(q: Fraction) -> Fraction | None:
    if q < 0:
        return None
    n, d = isqrt(q.numerator), isqrt(q.denominator)
    return Fraction(n, d) if n * n == q.numerator and d * d == q.denominator else None


def sign_of(value: Value, _depth: int = 0) -> int:
    """Exact sign of Σ c·√m: split into two halves and compare squares when they disagree."""
    terms = sorted((m, c) for m, c in value.items() if c)
    if not terms:
        return 0
    if len(terms) == 1:
        return 1 if terms[0][1] > 0 else -1
    if _depth > 24:
        raise ValueError("radical_sign_undetermined")
    half = len(terms) // 2
    p, q = dict(terms[:half]), dict(terms[half:])
    sp, sq = sign_of(p, _depth + 1), sign_of(q, _depth + 1)
    if sq == 0 or sp == sq:
        return sp
    if sp == 0:
        return sq
    return sp * sign_of(_add(_mul(p, p), _scale(_mul(q, q), Fraction(-1))), _depth + 1)


def compare_values(u: Value, w: Value) -> int:
    return sign_of(_add(u, _scale(w, Fraction(-1))))


def floor_of(value: Value) -> int:
    guess = int(sum(float(c) * m ** 0.5 for m, c in value.items()) // 1)
    for n in (guess, guess - 1, guess + 1, guess - 2, guess + 2):
        if compare_values(value, _rational(n)) >= 0 and compare_values(value, _rational(n + 1)) < 0:
            return n
    raise ValueError("floor_undetermined")


def rationalizing_factor(denominator: Value) -> tuple[Value, Fraction]:
    """Return (f, N) with denominator·f = N rational and positive."""
    if not denominator:
        raise ValueError("denominator_is_zero")
    terms = sorted(denominator.items())
    if len(terms) == 1:
        m, c = terms[0]
        factor, norm = ({1: Fraction(1)}, c) if m == 1 else ({m: Fraction(1)}, c * m)
    elif len(terms) == 2:
        (m1, c1), (m2, c2) = terms
        factor, norm = {m1: c1, m2: -c2}, c1 * c1 * m1 - c2 * c2 * m2
    else:
        raise ValueError("denominator_not_rationalizable_by_one_conjugate")
    if norm < 0:
        factor, norm = _scale(factor, Fraction(-1)), -norm
    return factor, norm


# --- input normalization -------------------------------------------------------

def _radical_sum(terms: Any) -> list[list[str]]:
    if not isinstance(terms, list) or not 1 <= len(terms) <= _MAX_TERMS:
        raise ValueError("radical sum must be a non-empty list of [coefficient, radicand]")
    out = []
    for term in terms:
        if not isinstance(term, (list, tuple)) or len(term) != 2:
            raise ValueError("radical term must be [coefficient, radicand]")
        if parse_exact_rational(term[1]) <= 0:
            raise ValueError("radicand must be positive")
        out.append([canonical_rational(term[0]), canonical_rational(term[1])])
    return out


def _factor(factor: Any) -> dict[str, Any]:
    if isinstance(factor, dict):
        power = factor.get("power", 1)
        if type(power) is not int or not 1 <= power <= _MAX_POWER:
            raise ValueError("factor power out of range")
        return {"terms": _radical_sum(factor.get("terms")), "power": power}
    return {"terms": _radical_sum(factor), "power": 1}


def _term(term: Any) -> dict[str, Any]:
    if not isinstance(term, dict):
        raise ValueError("term must be a mapping")
    numerator = term.get("numerator") or [[["1", "1"]]]
    denominator = term.get("denominator") or []
    if not isinstance(numerator, list) or not isinstance(denominator, list):
        raise ValueError("numerator / denominator must be factor lists")
    return {
        "coefficient": canonical_rational(term.get("coefficient", 1)),
        "numerator": [_factor(f) for f in numerator],
        "denominator": [_factor(f) for f in denominator],
    }


def _expression(expression: Any) -> list[dict[str, Any]]:
    if not isinstance(expression, list) or not 1 <= len(expression) <= _MAX_TERMS:
        raise ValueError("expression must be a non-empty list of terms")
    return [_term(t) for t in expression]


def _expanded_factors(factors: list[dict[str, Any]]) -> list[list[list[str]]]:
    return [f["terms"] for f in factors for _ in range(f["power"])]


def _nested_root(root: Any) -> dict[str, Any]:
    if not isinstance(root, dict) or not isinstance(root.get("radical"), (list, tuple)) or len(root["radical"]) != 2:
        raise ValueError("nested root must be {rational, radical: [k, q]}")
    k, q = root["radical"]
    q = parse_exact_rational(q)
    if q.denominator != 1 or q <= 1:
        raise ValueError("inner radicand must be an integer > 1")
    return {"rational": canonical_rational(root["rational"]), "radical": [canonical_rational(k), int(q)]}


def _positive(value: Any, name: str) -> Fraction:
    exact = parse_exact_rational(value)
    if exact <= 0:
        raise ValueError(f"{name} must be positive")
    return exact


# --- operations ----------------------------------------------------------------

def evaluate_radical_fraction_term(term: dict[str, Any]) -> dict[str, Any]:
    numerator = _evaluate([{"coefficient": term["coefficient"],
                            "factors": _expanded_factors(term["numerator"])}])
    if not term["denominator"]:
        return {"numerator": serialize_value(numerator), "denominator": [["1", 1]], "conjugate": None,
                "norm": "1", "value": serialize_value(numerator), "value_plain": value_plain(numerator)}
    denominator = _evaluate([{"factors": _expanded_factors(term["denominator"])}])
    conjugate, norm = rationalizing_factor(denominator)
    value = _scale(_mul(numerator, conjugate), 1 / norm)
    return {
        "numerator": serialize_value(numerator),
        "denominator": serialize_value(denominator),
        "conjugate": serialize_value(conjugate),
        "norm": canonical_rational(norm),
        "value": serialize_value(value),
        "value_plain": value_plain(value),
    }


def simplify_radical_fraction_expression(expression: list[dict[str, Any]]) -> dict[str, Any]:
    terms = [evaluate_radical_fraction_term(t) for t in expression]
    total = _add(*[_value(t["value"]) for t in terms])
    return {"terms": terms, "value": serialize_value(total), "value_plain": value_plain(total)}


def simplify_radical_fraction_expressions(expressions: Any) -> dict[str, Any]:
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} expressions are required")
    return {"parts": [simplify_radical_fraction_expression(_expression(e)) for e in expressions]}


def denest_square_root(root: dict[str, Any]) -> dict[str, Any]:
    """√(p + k√q) = √x ± √y with x + y = p, xy = k²q/4, x > y > 0."""
    p, k, q = parse_exact_rational(root["rational"]), parse_exact_rational(root["radical"][0]), root["radical"][1]
    if p <= 0 or k == 0:
        raise ValueError("needs p > 0 and a non-zero radical coefficient")
    n = k * k * q / 4
    discriminant = p * p - 4 * n
    root_of_discriminant = rational_square_root(discriminant) if discriminant > 0 else None
    if root_of_discriminant is None:
        raise ValueError("not_denestable_over_rationals")
    x, y = (p + root_of_discriminant) / 2, (p - root_of_discriminant) / 2
    if y <= 0:
        raise ValueError("not_a_real_nested_square_root")
    sign = 1 if k > 0 else -1
    value = _evaluate([{"factors": [[[1, canonical_rational(x)], [sign, canonical_rational(y)]]]}])
    inner = _evaluate([{"factors": [[[canonical_rational(p), 1], [canonical_rational(k), q]]]}])
    if _mul(value, value) != inner or sign_of(value) <= 0:
        raise ValueError("denesting_check_failed")
    return {
        "n": canonical_rational(n),
        "x": canonical_rational(x),
        "y": canonical_rational(y),
        "sign": sign,
        "value": serialize_value(value),
        "value_plain": value_plain(value),
    }


def denest_square_roots(roots: Any) -> dict[str, Any]:
    if not isinstance(roots, list) or not 1 <= len(roots) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} nested roots are required")
    return {"parts": [denest_square_root(_nested_root(r)) for r in roots]}


def evaluate_integer_fraction_part_expression(root: Any, sign: Any) -> dict[str, Any]:
    """With a = ⌊v⌋, b = v − a for v = √(p + k√q), return a + sign·(1/b)."""
    if sign not in (1, -1):
        raise ValueError("sign must be 1 or -1")
    denested = denest_square_root(_nested_root(root))
    value = _value(denested["value"])
    if len(value) != 2 or 1 not in value:
        raise ValueError("value must be a rational plus one radical")
    a = floor_of(value)
    b = _add(value, _rational(-a))
    conjugate, norm = rationalizing_factor(b)
    reciprocal = _scale(conjugate, 1 / norm)
    result = _add(_rational(a), _scale(reciprocal, Fraction(sign)))
    return {
        "denested": denested,
        "integer_part": a,
        "fractional_part": serialize_value(b),
        "reciprocal": serialize_value(reciprocal),
        "value": serialize_value(result),
        "value_plain": value_plain(result),
    }


def order_radical_numbers(numbers: Any) -> dict[str, Any]:
    if not isinstance(numbers, list) or not 2 <= len(numbers) <= len(_LABELS):
        raise ValueError("between 2 and 8 labelled numbers are required")
    rows = []
    for number in numbers:
        label = str(number.get("label") if isinstance(number, dict) else "")
        if len(label) != 1 or label not in _LABELS:
            raise ValueError("labels must be single letters a-h")
        evaluated = evaluate_radical_fraction_term(_term(number["term"]))
        rows.append((label, evaluated, _value(evaluated["value"])))
    if len({r[0] for r in rows}) != len(rows):
        raise ValueError("labels must be distinct")
    for i, (_, _, u) in enumerate(rows):
        for _, _, w in rows[i + 1:]:
            if compare_values(u, w) == 0:
                raise ValueError("numbers must be pairwise distinct")
    descending = sorted(rows, key=cmp_to_key(lambda r1, r2: compare_values(r2[2], r1[2])))
    return {
        "values": [{"label": label, **evaluated, "square": serialize_value(_mul(v, v))} for label, evaluated, v in rows],
        "descending": [r[0] for r in descending],
        "order_plain": ">".join(r[0] for r in descending),
    }


def _lorentz_factor(speed_ratio: Fraction) -> Fraction:
    if not 0 < speed_ratio < 1:
        raise ValueError("speed ratio must satisfy 0 < x < 1")
    root = rational_square_root(1 - speed_ratio * speed_ratio)
    if root is None:
        raise ValueError("1 - x^2 must be a rational square")
    return 1 / root


def evaluate_time_dilation_relation(relation: dict[str, Any]) -> dict[str, Any]:
    """Earth time T = t / √(1 − x²) for travel time t at x times light speed."""
    find = relation.get("find")
    if find == "earth_years":
        t, x = _positive(relation["traveler_years"], "traveler_years"), parse_exact_rational(relation["speed_ratio"])
        gamma = _lorentz_factor(x)
        return {"find": find, "gamma": canonical_rational(gamma), "kind": "rational", "value": canonical_rational(t * gamma)}
    if find == "travel_years_from_age_match":
        older, younger = parse_exact_rational(relation["traveler_age"]), parse_exact_rational(relation["child_age"])
        x = parse_exact_rational(relation["speed_ratio"])
        gamma = _lorentz_factor(x)
        if older <= younger or younger < 0:
            raise ValueError("traveler must be older than the child")
        t = (older - younger) / (gamma - 1)
        return {"find": find, "gamma": canonical_rational(gamma), "kind": "rational", "value": canonical_rational(t),
                "earth_years": canonical_rational(gamma * t), "final_age": canonical_rational(older + t)}
    if find == "speed_ratio":
        t, earth = _positive(relation["traveler_years"], "traveler_years"), _positive(relation["earth_years"], "earth_years")
        if t >= earth:
            raise ValueError("earth time must exceed travel time")
        square = 1 - (t / earth) ** 2
        value = _evaluate([{"factors": [[[1, canonical_rational(square)]]]}])
        return {"find": find, "kind": "radical", "speed_ratio_squared": canonical_rational(square),
                "value": serialize_value(value), "value_plain": value_plain(value)}
    raise ValueError(f"unsupported time dilation target: {find!r}")


def evaluate_time_dilation_relations(relations: Any) -> dict[str, Any]:
    if not isinstance(relations, list) or not 1 <= len(relations) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} relations are required")
    return {"relations": [evaluate_time_dilation_relation(dict(r)) for r in relations]}


def optimize_by_am_gm(problem: Any) -> dict[str, Any]:
    """Two positive variables x, y; the optimum is where AM-GM holds with equality."""
    if not isinstance(problem, dict):
        raise ValueError("problem must be a mapping")
    kind = problem.get("kind")
    if kind == "max_product_linear_sum":
        p, q, total = (_positive(problem[k], k) for k in ("p", "q", "total"))
        x, y = total / (2 * p), total / (2 * q)
        optimum = x * y
    elif kind == "min_linear_sum_fixed_product":
        p, q, product = (_positive(problem[k], k) for k in ("p", "q", "product"))
        x, y = rational_square_root(q * product / p), rational_square_root(p * product / q)
        if x is None or y is None:
            raise ValueError("equality point must be rational")
        optimum = p * x + q * y
    elif kind == "min_box_surface":
        height, volume = _positive(problem["height"], "height"), _positive(problem["volume"], "volume")
        base_area = volume / height
        side = rational_square_root(base_area)
        if side is None:
            raise ValueError("base side must be rational")
        x = y = side
        optimum = 2 * base_area + 4 * height * side
    else:
        raise ValueError(f"unsupported AM-GM problem kind: {kind!r}")
    return {"kind": kind, "x": canonical_rational(x), "y": canonical_rational(y), "optimum": canonical_rational(optimum)}


def nearest_integer_from_radical_relation(known: Any, rhs: Any, sign: Any) -> dict[str, Any]:
    """√a + sign·√known = √rhs, so √a = √rhs − sign·√known and a = (√a)²."""
    m, n = _positive(known, "known"), _positive(rhs, "rhs")
    if sign not in (1, -1):
        raise ValueError("sign must be 1 or -1")
    root = _evaluate([{"factors": [[[1, canonical_rational(n)], [-sign, canonical_rational(m)]]]}])
    if sign_of(root) <= 0:
        raise ValueError("relation has no real solution")
    a = _mul(root, root)
    if set(a) <= {1}:
        raise ValueError("a must be irrational")
    nearest = floor_of(_add(a, _rational(Fraction(1, 2))))
    return {"sqrt_a": serialize_value(root), "a": serialize_value(a), "a_plain": value_plain(a), "nearest_integer": nearest}


# --- seeded inputs -------------------------------------------------------------

_SQUAREFREE = (2, 3, 5, 6, 7, 10, 11, 13)


def _nonzero(rng: random.Random, low: int, high: int) -> int:
    return rng.choice([v for v in range(low, high + 1) if v])


def _fraction_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    expressions = constraints.get("expressions")
    if expressions is None:
        k = rng.choice((2, 5, 6, 7, 10, 11))
        expressions = [[{"numerator": [[[1, 1]]], "denominator": [[[1, k + 1], [-1, k]]]}]]
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} expressions are required")
    return {"expressions": [_expression(e) for e in expressions]}


def _seeded_root(rng: random.Random) -> dict[str, Any]:
    x = rng.choice(_SQUAREFREE)
    return {"rational": x + 1, "radical": [2 * rng.choice((1, -1)), x]}


def _denest_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    roots = constraints.get("roots")
    if roots is None:
        roots = [_seeded_root(rng)]
    if not isinstance(roots, list) or not 1 <= len(roots) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} nested roots are required")
    givens = {"roots": [_nested_root(r) for r in roots]}
    if constraints.get("context") is not None:
        givens["context"] = str(constraints["context"])
    return givens


def _parts_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    root = constraints.get("root") or _seeded_root(rng)
    sign = constraints.get("sign", rng.choice((1, -1)))
    return {"root": _nested_root(root), "sign": sign}


def _order_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    numbers = constraints.get("numbers")
    if numbers is None:
        total = rng.choice((13, 17, 19))
        splits = rng.sample([p for p in range(2, total // 2 + 1) if isqrt(p) ** 2 != p and isqrt(total - p) ** 2 != total - p], 3)
        numbers = [{"label": label, "term": {"numerator": [[[1, p], [1, total - p]]]}} for label, p in zip("abc", splits)]
    return {"numbers": [{"label": str(n["label"]), "term": _term(n["term"])} for n in numbers]}


_TRIPLES = ((3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25))


def _time_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    relations = constraints.get("relations")
    if relations is None:
        a, b, c = rng.choice(_TRIPLES)
        relations = [{"find": "earth_years", "traveler_years": b * rng.randint(1, 4), "speed_ratio": f"{a}/{c}"}]
    if not isinstance(relations, list) or not 1 <= len(relations) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} relations are required")
    out = []
    for relation in relations:
        if not isinstance(relation, dict):
            raise ValueError("relation must be a mapping")
        out.append({k: (v if k == "find" else canonical_rational(v)) for k, v in relation.items()})
    return {"relations": out}


def _am_gm_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    problem = constraints.get("problem")
    if problem is None:
        problem = {"kind": "max_product_linear_sum", "p": 2, "q": 2, "total": 4 * rng.randint(2, 12), "context": "rope_rectangle"}
    if not isinstance(problem, dict):
        raise ValueError("problem must be a mapping")
    return {"problem": {k: (v if k in ("kind", "context") else canonical_rational(v)) for k, v in problem.items()}}


def _nearest_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("known") is not None:
        known, rhs, sign = constraints["known"], constraints["rhs"], constraints.get("sign", -1)
    else:
        known, rhs = rng.sample(_SQUAREFREE, 2)
        sign = -1
    return {"known": canonical_rational(known), "rhs": canonical_rational(rhs), "sign": sign}


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "simplify_radical_fraction_expressions": (
        _fraction_givens, lambda g: simplify_radical_fraction_expressions(g["expressions"]),
    ),
    "denest_square_roots": (_denest_givens, lambda g: denest_square_roots(g["roots"])),
    "evaluate_integer_fraction_part_expression": (
        _parts_givens, lambda g: evaluate_integer_fraction_part_expression(g["root"], g["sign"]),
    ),
    "order_radical_numbers": (_order_givens, lambda g: order_radical_numbers(g["numbers"])),
    "evaluate_time_dilation_relations": (_time_givens, lambda g: evaluate_time_dilation_relations(g["relations"])),
    "optimize_by_am_gm": (_am_gm_givens, lambda g: optimize_by_am_gm(g["problem"])),
    "nearest_integer_from_radical_relation": (
        _nearest_givens, lambda g: nearest_integer_from_radical_relation(g["known"], g["rhs"], g["sign"]),
    ),
}
OPERATIONS = tuple(_OPERATIONS)


def build_radical_operations_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_radical_operations_operation:{operation}")
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
                if _OPERATIONS[operation][1](matrix["givens"]) != matrix["answer"]:
                    return False
                return bool(check(matrix["givens"], matrix["answer"]))
            except Exception:
                return False

        validate.__name__ = f"validate_{operation}_matrix"
        return validate

    return wrap


@_validator("simplify_radical_fraction_expressions")
def validate_simplify_radical_fraction_expressions_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for part in answer["parts"]:
        for term in part["terms"]:
            if term["conjugate"] is not None:
                product = _mul(_value(term["denominator"]), _value(term["conjugate"]))
                if set(product) != {1} or product[1] != parse_exact_rational(term["norm"]):
                    return False
        total = _add(*[_value(t["value"]) for t in part["terms"]])
        if serialize_value(total) != part["value"]:
            return False
    return len(answer["parts"]) == len(givens["expressions"])


@_validator("denest_square_roots")
def validate_denest_square_roots_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for root, part in zip(givens["roots"], answer["parts"]):
        inner = _evaluate([{"factors": [[[root["rational"], 1], [root["radical"][0], root["radical"][1]]]]}])
        value = _value(part["value"])
        if _mul(value, value) != inner or sign_of(value) <= 0:
            return False
    return len(answer["parts"]) == len(givens["roots"])


@_validator("evaluate_integer_fraction_part_expression")
def validate_evaluate_integer_fraction_part_expression_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    b = _value(answer["fractional_part"])
    if not (sign_of(b) > 0 and compare_values(b, _rational(1)) < 0):
        return False
    return _mul(b, _value(answer["reciprocal"])) == {1: Fraction(1)}


@_validator("order_radical_numbers")
def validate_order_radical_numbers_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    values = {row["label"]: _value(row["value"]) for row in answer["values"]}
    order = answer["descending"]
    return sorted(order) == sorted(values) and all(
        compare_values(values[hi], values[lo]) > 0 for hi, lo in zip(order, order[1:])
    )


@_validator("evaluate_time_dilation_relations")
def validate_evaluate_time_dilation_relations_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for relation, result in zip(givens["relations"], answer["relations"]):
        if result["find"] == "earth_years":
            t, x = parse_exact_rational(relation["traveler_years"]), parse_exact_rational(relation["speed_ratio"])
            if (t / parse_exact_rational(result["value"])) ** 2 != 1 - x * x:
                return False
        elif result["find"] == "travel_years_from_age_match":
            t = parse_exact_rational(result["value"])
            if parse_exact_rational(relation["traveler_age"]) + t != (
                parse_exact_rational(relation["child_age"]) + parse_exact_rational(result["earth_years"])
            ):
                return False
        elif result["find"] == "speed_ratio":
            x = _value(result["value"])
            t, earth = parse_exact_rational(relation["traveler_years"]), parse_exact_rational(relation["earth_years"])
            if _mul(x, x) != _rational(1 - (t / earth) ** 2) or sign_of(x) <= 0:
                return False
    return len(answer["relations"]) == len(givens["relations"])


@_validator("optimize_by_am_gm")
def validate_optimize_by_am_gm_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    problem = givens["problem"]
    x, y, optimum = (parse_exact_rational(answer[k]) for k in ("x", "y", "optimum"))
    if x <= 0 or y <= 0:
        return False
    if answer["kind"] == "max_product_linear_sum":
        p, q, total = (parse_exact_rational(problem[k]) for k in ("p", "q", "total"))
        return p * x + q * y == total and p * x == q * y and optimum == x * y
    if answer["kind"] == "min_linear_sum_fixed_product":
        p, q, product = (parse_exact_rational(problem[k]) for k in ("p", "q", "product"))
        return x * y == product and p * x == q * y and optimum == p * x + q * y
    height, volume = parse_exact_rational(problem["height"]), parse_exact_rational(problem["volume"])
    return x == y and x * y * height == volume and optimum == 2 * x * y + 2 * height * (x + y)


@_validator("nearest_integer_from_radical_relation")
def validate_nearest_integer_from_radical_relation_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, n = _value(answer["a"]), answer["nearest_integer"]
    return compare_values(a, _rational(Fraction(2 * n - 1, 2))) > 0 and compare_values(a, _rational(Fraction(2 * n + 1, 2))) < 0
