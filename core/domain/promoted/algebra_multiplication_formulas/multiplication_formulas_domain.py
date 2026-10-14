"""Exact, seed-deterministic operations for the algebra.multiplication_formulas domain.

Each operation is one shared implementation.  Source items supply their inputs
through ``constraints``; seeded generation produces inputs of the same shape.
Rendering and answer topology belong to the adapter module.

Structured inputs
-----------------
polynomial   ``[[coefficient, {variable: exponent}], ...]``
expression   ``[{"coefficient": c?, "factors": [[polynomial, power], ...]}, ...]``
             (a sum of products of powered polynomials)
radical sum  ``[[coefficient, radicand], ...]`` meaning Σ c·√r (r = "1" is rational)
radical expr ``[{"coefficient": c?, "factors": [radical sum, ...]}, ...]``
"""

from __future__ import annotations

import random
import re
from fractions import Fraction
from math import gcd, isqrt
from typing import Any, Callable

DOMAIN_KEY = "algebra.multiplication_formulas"

_DECIMAL = re.compile(r"^([+-]?)(\d+)(?:\.(\d+))?$")
_VARIABLE = re.compile(r"^[a-z]$")
_MAX_POWER = 6
_MAX_PARTS = 4

Monomial = tuple[tuple[str, int], ...]
Polynomial = dict[Monomial, Fraction]


# --- exact rationals --------------------------------------------------------

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


def integer_cube_root(n: int) -> int | None:
    sign = -1 if n < 0 else 1
    root = round(abs(n) ** (1 / 3))
    for candidate in (root - 1, root, root + 1):
        if candidate >= 0 and candidate ** 3 == abs(n):
            return sign * candidate
    return None


def squarefree_decomposition(n: int) -> tuple[int, int]:
    """Return (s, f) with n = s²·f and f squarefree."""
    if type(n) is not int or n <= 0:
        raise ValueError(f"radicand must be a positive integer: {n!r}")
    outside, inside, factor = 1, n, 2
    while factor * factor <= inside:
        while inside % (factor * factor) == 0:
            inside //= factor * factor
            outside *= factor
        factor += 1
    return outside, inside


# --- polynomials ------------------------------------------------------------

def _monomial(powers: Any) -> Monomial:
    if not isinstance(powers, dict):
        raise TypeError("monomial powers must be a {variable: exponent} mapping")
    items = []
    for variable, exponent in powers.items():
        if not _VARIABLE.fullmatch(str(variable)) or type(exponent) is not int or exponent < 0:
            raise ValueError(f"invalid monomial factor: {variable!r}^{exponent!r}")
        if exponent:
            items.append((str(variable), exponent))
    return tuple(sorted(items))


def parse_polynomial(terms: Any) -> Polynomial:
    if not isinstance(terms, list) or not terms:
        raise ValueError("polynomial must be a non-empty list of [coefficient, powers] terms")
    poly: Polynomial = {}
    for term in terms:
        if not isinstance(term, (list, tuple)) or len(term) != 2:
            raise ValueError("polynomial term must be [coefficient, powers]")
        key = _monomial(term[1])
        poly[key] = poly.get(key, Fraction(0)) + parse_exact_rational(term[0])
    return {k: v for k, v in poly.items() if v}


def poly_add(p: Polynomial, q: Polynomial) -> Polynomial:
    out = dict(p)
    for key, coefficient in q.items():
        out[key] = out.get(key, Fraction(0)) + coefficient
    return {k: v for k, v in out.items() if v}


def poly_mul(p: Polynomial, q: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for k1, c1 in p.items():
        for k2, c2 in q.items():
            merged = dict(k1)
            for variable, exponent in k2:
                merged[variable] = merged.get(variable, 0) + exponent
            key = tuple(sorted(merged.items()))
            out[key] = out.get(key, Fraction(0)) + c1 * c2
    return {k: v for k, v in out.items() if v}


def poly_pow(p: Polynomial, power: int) -> Polynomial:
    if type(power) is not int or not 1 <= power <= _MAX_POWER:
        raise ValueError(f"power must be an integer between 1 and {_MAX_POWER}")
    out: Polynomial = {(): Fraction(1)}
    for _ in range(power):
        out = poly_mul(out, p)
    return out


def poly_variables(*polys: Polynomial) -> list[str]:
    return sorted({variable for poly in polys for key in poly for variable, _ in key})


def ordered_terms(poly: Polynomial, variables: list[str] | None = None) -> list[tuple[Fraction, Monomial]]:
    """Descending lexicographic order in alphabetical variables (textbook order)."""
    names = variables or poly_variables(poly)

    def rank(key: Monomial) -> tuple[int, ...]:
        exponents = dict(key)
        return tuple(-exponents.get(name, 0) for name in names)

    return [(poly[key], key) for key in sorted(poly, key=rank)]


def serialize_polynomial(poly: Polynomial) -> list[list[Any]]:
    return [[canonical_rational(c), dict(key)] for c, key in ordered_terms(poly)]


def _monomial_plain(key: Monomial) -> str:
    return "".join(v if e == 1 else f"{v}^{e}" for v, e in key)


def polynomial_plain(poly: Polynomial) -> str:
    """Keyboard form, e.g. ``a^3+6a^2b-3ab/2+1``."""
    if not poly:
        return "0"
    text = ""
    for coefficient, key in ordered_terms(poly):
        magnitude, mono = abs(coefficient), _monomial_plain(key)
        if not mono:
            body = canonical_rational(magnitude)
        else:
            numerator = "" if magnitude.numerator == 1 else str(magnitude.numerator)
            body = f"{numerator}{mono}" + (f"/{magnitude.denominator}" if magnitude.denominator != 1 else "")
        text += ("-" if coefficient < 0 else ("+" if text else "")) + body
    return text


# --- multiplication-formula operations --------------------------------------

def _expression(expression: Any) -> list[dict[str, Any]]:
    if not isinstance(expression, list) or not expression:
        raise ValueError("expression must be a non-empty list of products")
    products = []
    for product in expression:
        if not isinstance(product, dict) or not isinstance(product.get("factors"), list) or not product["factors"]:
            raise ValueError("product must define a non-empty factors list")
        factors = []
        for factor in product["factors"]:
            if not isinstance(factor, (list, tuple)) or len(factor) != 2:
                raise ValueError("factor must be [polynomial, power]")
            poly = parse_polynomial(factor[0])
            if not poly:
                raise ValueError("factor polynomial must be non-zero")
            factors.append({"polynomial": poly, "power": factor[1]})
        products.append({"coefficient": parse_exact_rational(product.get("coefficient", 1)), "factors": factors})
    return products


def expand_expression(expression: Any) -> tuple[Polynomial, list[dict[str, Any]]]:
    """Expand Σ c·Π (polynomial)^power exactly; returns total and per-product expansions."""
    total: Polynomial = {}
    pieces = []
    for product in _expression(expression):
        value: Polynomial = {(): product["coefficient"]}
        for factor in product["factors"]:
            value = poly_mul(value, poly_pow(factor["polynomial"], factor["power"]))
        pieces.append(value)
        total = poly_add(total, value)
    return total, pieces


def serialize_expression(expression: Any) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": canonical_rational(product["coefficient"]),
            "factors": [[serialize_polynomial(f["polynomial"]), f["power"]] for f in product["factors"]],
        }
        for product in _expression(expression)
    ]


def expand_polynomial_expressions(expressions: Any) -> dict[str, Any]:
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} expressions are required")
    parts = []
    for expression in expressions:
        total, pieces = expand_expression(expression)
        if not total:
            raise ValueError("expansion must not vanish")
        parts.append({
            "expanded": serialize_polynomial(total),
            "expanded_plain": polynomial_plain(total),
            "product_expansions": [serialize_polynomial(piece) for piece in pieces],
        })
    return {"parts": parts}


def _cube_root_term(coefficient: Fraction, key: Monomial) -> tuple[Fraction, Monomial] | None:
    numerator, denominator = integer_cube_root(coefficient.numerator), integer_cube_root(coefficient.denominator)
    if numerator is None or denominator is None or any(e % 3 for _, e in key):
        return None
    return Fraction(numerator, denominator), tuple((v, e // 3) for v, e in key)


def factor_by_cube_formula(polynomial: Any) -> dict[str, Any]:
    """Factor A³ ± B³ = (A ± B)(A² ∓ AB + B²) or A³ ± 3A²B + 3AB² ± B³ = (A ± B)³.

    A and B are the cube roots of the first and last terms in textbook order; the
    identity is verified by exact re-expansion, otherwise the input is refused.
    """
    poly = parse_polynomial(polynomial)
    terms = ordered_terms(poly)
    if len(terms) not in (2, 4):
        raise ValueError("cube formulas apply to two-term or four-term polynomials")
    first, last = _cube_root_term(*terms[0]), _cube_root_term(*terms[-1])
    if first is None or last is None:
        raise ValueError("first and last terms must be perfect cubes")
    a_term, b_term = {first[1]: first[0]}, {last[1]: last[0]}
    binomial = poly_add(a_term, b_term)
    if len(terms) == 2:
        quadratic = poly_add(poly_add(poly_mul(a_term, a_term), poly_mul({(): Fraction(-1)}, poly_mul(a_term, b_term))),
                             poly_mul(b_term, b_term))
        factors = [[serialize_polynomial(binomial), 1], [serialize_polynomial(quadratic), 1]]
        formula = "sum_of_cubes" if last[0] > 0 else "difference_of_cubes"
        check = poly_mul(binomial, quadratic)
    else:
        factors = [[serialize_polynomial(binomial), 3]]
        formula = "cube_of_sum" if last[0] > 0 else "cube_of_difference"
        check = poly_pow(binomial, 3)
    if check != poly:
        raise ValueError("polynomial does not match a cube formula")
    return {
        "polynomial": serialize_polynomial(poly),
        "formula": formula,
        "a_term": serialize_polynomial(a_term),
        "b_term": serialize_polynomial(b_term),
        "factors": factors,
    }


def factor_by_cube_formulas(polynomials: Any) -> dict[str, Any]:
    if not isinstance(polynomials, list) or not 1 <= len(polynomials) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} polynomials are required")
    return {"parts": [factor_by_cube_formula(p) for p in polynomials]}


# x is a root of x² − s·x + N = 0; elements of Q[x]/(x² − s·x + N) are pairs (a, b) = a + b·x.

def _quadratic_base(base: Any) -> dict[str, Any]:
    if not isinstance(base, dict):
        raise TypeError("base must describe a relation or a radical value")
    kind = base.get("kind")
    if kind == "relation":
        sign = base.get("sign")
        if sign not in (1, -1):
            raise ValueError("relation sign must be 1 or -1")
        value = parse_exact_rational(base["value"])
        return {"kind": kind, "sign": sign, "value": canonical_rational(value), "trace": value, "norm": Fraction(sign)}
    if kind == "radical":
        p, q = parse_exact_rational(base["rational"]), parse_exact_rational(base["radical"])
        m = base.get("radicand")
        if type(m) is not int or squarefree_decomposition(m) != (1, m) or m <= 1 or q == 0:
            raise ValueError("radical value needs a squarefree radicand > 1 and non-zero radical part")
        norm = p * p - q * q * m
        if norm == 0:
            raise ValueError("radical value must be non-zero")
        return {"kind": kind, "rational": canonical_rational(p), "radical": canonical_rational(q), "radicand": m,
                "trace": 2 * p, "norm": norm}
    raise ValueError(f"unsupported base kind: {kind!r}")


def _ring_mul(u: tuple[Fraction, Fraction], v: tuple[Fraction, Fraction], s: Fraction, n: Fraction) -> tuple[Fraction, Fraction]:
    (a1, b1), (a2, b2) = u, v
    return a1 * a2 - n * b1 * b2, a1 * b2 + a2 * b1 + s * b1 * b2


def _ring_pow(u: tuple[Fraction, Fraction], k: int, s: Fraction, n: Fraction) -> tuple[Fraction, Fraction]:
    out = (Fraction(1), Fraction(0))
    for _ in range(k):
        out = _ring_mul(out, u, s, n)
    return out


def evaluate_reciprocal_power_expressions(base: Any, targets: Any) -> dict[str, Any]:
    """Evaluate xⁿ + τ·x⁻ⁿ exactly, given x ± 1/x = s or x = p + q√m."""
    info = _quadratic_base(base)
    s, n = info["trace"], info["norm"]
    if not isinstance(targets, list) or not 1 <= len(targets) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} targets are required")
    x, inverse = (Fraction(0), Fraction(1)), (s / n, Fraction(-1) / n)
    values = []
    for target in targets:
        power, sign = target.get("power"), target.get("sign")
        if type(power) is not int or not 1 <= power <= _MAX_POWER or sign not in (1, -1):
            raise ValueError(f"invalid target: {target!r}")
        up, down = _ring_pow(x, power, s, n), _ring_pow(inverse, power, s, n)
        a, b = up[0] + sign * down[0], up[1] + sign * down[1]
        if b == 0:
            value = {"rational": canonical_rational(a), "radical": "0"}
        elif info["kind"] == "radical":
            p, q = parse_exact_rational(info["rational"]), parse_exact_rational(info["radical"])
            value = {"rational": canonical_rational(a + b * p), "radical": canonical_rational(b * q)}
        else:
            raise ValueError("target is not determined as a rational value by the relation")
        values.append({"power": power, "sign": sign, "value": value})
    public = {k: v for k, v in info.items() if k not in ("trace", "norm")}
    return {"base": public, "norm": canonical_rational(n), "values": values}


def _simplified_radical_terms(terms: Any) -> list[tuple[Fraction, int]]:
    """c·√(p/q) = (c·s/q)·√f with p·q = s²·f, term by term in the written order."""
    if not isinstance(terms, list) or not terms:
        raise ValueError("radical sum must be a non-empty list of [coefficient, radicand]")
    out = []
    for term in terms:
        if not isinstance(term, (list, tuple)) or len(term) != 2:
            raise ValueError("radical term must be [coefficient, radicand]")
        coefficient, radicand = parse_exact_rational(term[0]), parse_exact_rational(term[1])
        if radicand <= 0:
            raise ValueError("radicand must be positive")
        outside, inside = squarefree_decomposition(radicand.numerator * radicand.denominator)
        out.append((coefficient * Fraction(outside, radicand.denominator), inside))
    return out


def _radical_sum(terms: Any) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for coefficient, key in _simplified_radical_terms(terms):
        out[key] = out.get(key, Fraction(0)) + coefficient
    return {k: v for k, v in out.items() if v}


def _radical_mul(u: dict[int, Fraction], v: dict[int, Fraction]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for m1, c1 in u.items():
        for m2, c2 in v.items():
            g = gcd(m1, m2)
            key = (m1 // g) * (m2 // g)
            out[key] = out.get(key, Fraction(0)) + c1 * c2 * g
    return {k: v for k, v in out.items() if v}


def serialize_radical_value(value: dict[int, Fraction]) -> list[list[Any]]:
    return [[canonical_rational(value[m]), m] for m in sorted(value)]


def radical_plain(value: dict[int, Fraction]) -> str:
    if not value:
        return "0"
    text = ""
    for m in sorted(value):
        c = value[m]
        magnitude = abs(c)
        if m == 1:
            body = canonical_rational(magnitude)
        else:
            numerator = "" if magnitude.numerator == 1 else str(magnitude.numerator)
            body = f"{numerator}sqrt({m})" + (f"/{magnitude.denominator}" if magnitude.denominator != 1 else "")
        text += ("-" if c < 0 else ("+" if text else "")) + body
    return text


def simplify_radical_expression(expression: Any) -> dict[str, Any]:
    if not isinstance(expression, list) or not expression:
        raise ValueError("radical expression must be a non-empty list of products")
    total: dict[int, Fraction] = {}
    simplified_terms = []
    for product in expression:
        if not isinstance(product, dict) or not isinstance(product.get("factors"), list) or not product["factors"]:
            raise ValueError("radical product must define a non-empty factors list")
        value = {1: parse_exact_rational(product.get("coefficient", 1))}
        factor_values = []
        for factor in product["factors"]:
            factor_values.append([[canonical_rational(c), m] for c, m in _simplified_radical_terms(factor)])
            value = _radical_mul(value, _radical_sum(factor))
        simplified_terms.append(factor_values)
        for key, coefficient in value.items():
            total[key] = total.get(key, Fraction(0)) + coefficient
    total = {k: v for k, v in total.items() if v}
    return {"simplified_factors": simplified_terms, "value": serialize_radical_value(total), "value_plain": radical_plain(total)}


def simplify_radical_expressions(expressions: Any) -> dict[str, Any]:
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= _MAX_PARTS:
        raise ValueError(f"between 1 and {_MAX_PARTS} radical expressions are required")
    return {"parts": [simplify_radical_expression(e) for e in expressions]}


def solve_rational_unknowns_from_squared_radical_identity(coefficient: Any, radicand: Any, rhs_radical: Any) -> dict[str, Any]:
    """(a + q√m)² = b + r√m with rational a, b: a² + q²m = b and 2aq = r."""
    q, r = parse_exact_rational(coefficient), parse_exact_rational(rhs_radical)
    if type(radicand) is not int or radicand <= 1 or squarefree_decomposition(radicand) != (1, radicand) or q == 0:
        raise ValueError("needs a squarefree radicand > 1 and a non-zero radical coefficient")
    a = r / (2 * q)
    b = a * a + q * q * radicand
    return {
        "unknowns": ["a", "b"],
        "values": {"a": canonical_rational(a), "b": canonical_rational(b)},
        "radical_part_equation": {"coefficient_of_a": canonical_rational(2 * q), "constant": canonical_rational(r)},
        "rational_part_constant": canonical_rational(q * q * radicand),
    }


def evaluate_product_under_power_relation(variable: Any, power: Any, value: Any, expression: Any) -> dict[str, Any]:
    """Expand the expression, then replace variable^power by value; the result must be constant."""
    if not _VARIABLE.fullmatch(str(variable)) or type(power) is not int or not 2 <= power <= _MAX_POWER:
        raise ValueError("relation must be variable^power = value with power between 2 and 6")
    c = parse_exact_rational(value)
    expanded, _ = expand_expression(expression)
    if poly_variables(expanded) not in ([], [variable]):
        raise ValueError("expression may only use the related variable")
    reduced: Polynomial = {}
    for key, coefficient in expanded.items():
        exponent = dict(key).get(variable, 0)
        quotient, remainder = divmod(exponent, power)
        mono = ((variable, remainder),) if remainder else ()
        reduced[mono] = reduced.get(mono, Fraction(0)) + coefficient * c ** quotient
    reduced = {k: v for k, v in reduced.items() if v}
    if any(reduced_key for reduced_key in reduced):
        raise ValueError("expression is not determined by the power relation")
    return {
        "relation": {"variable": str(variable), "power": power, "value": canonical_rational(c)},
        "expanded": serialize_polynomial(expanded),
        "expanded_plain": polynomial_plain(expanded),
        "value": canonical_rational(reduced.get((), Fraction(0))),
    }


# --- seeded inputs ------------------------------------------------------------

def _nonzero(rng: random.Random, low: int, high: int) -> int:
    return rng.choice([v for v in range(low, high + 1) if v])


def _binomial(p: int, q: int, x: str = "a", y: str | None = "b") -> list[list[Any]]:
    return [[p, {x: 1}], [q, {y: 1} if y else {}]]


def _seeded_expression(rng: random.Random) -> list[dict[str, Any]]:
    p, q = rng.randint(1, 3), _nonzero(rng, -3, 3)
    pattern = rng.choice(("square", "cube", "cube_product"))
    if pattern == "square":
        return [{"factors": [[_binomial(p, q), 2]]}]
    if pattern == "cube":
        return [{"factors": [[_binomial(p, q), 3]]}]
    return [{"factors": [[_binomial(p, q), 1], [[[p * p, {"a": 2}], [-p * q, {"a": 1, "b": 1}], [q * q, {"b": 2}]], 1]]}]


def _seeded_cube_polynomial(rng: random.Random) -> list[list[Any]]:
    u, k = rng.randint(1, 3), _nonzero(rng, -4, 4)
    if rng.random() < 0.5:
        return [[u ** 3, {"x": 3}], [k ** 3, {}]]
    return [[u ** 3, {"x": 3}], [3 * u * u * k, {"x": 2}], [3 * u * k * k, {"x": 1}], [k ** 3, {}]]


def _expand_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    expressions = constraints.get("expressions")
    if expressions is None:
        expressions = [_seeded_expression(rng) for _ in range(rng.randint(1, 3))]
    return {"expressions": [serialize_expression(e) for e in expressions]}


def _factor_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    polynomials = constraints.get("polynomials")
    if polynomials is None:
        polynomials = [_seeded_cube_polynomial(rng) for _ in range(rng.randint(1, 3))]
    return {"polynomials": [serialize_polynomial(parse_polynomial(p)) for p in polynomials]}


def _reciprocal_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    base, targets = constraints.get("base"), constraints.get("targets")
    if base is None:
        sign = rng.choice((1, -1))
        base = {"kind": "relation", "sign": sign, "value": rng.randint(3, 8) if sign == 1 else _nonzero(rng, -6, 6)}
        targets = [{"power": 2, "sign": 1}, {"power": 3, "sign": sign}]
    info = _quadratic_base(base)
    public = {k: v for k, v in info.items() if k not in ("trace", "norm")}
    return {"base": public, "targets": [{"power": t["power"], "sign": t["sign"]} for t in targets]}


def _radical_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    expressions = constraints.get("expressions")
    if expressions is None:
        m = rng.choice((2, 3, 5))
        s, t = rng.sample(range(2, 6), 2)
        expressions = [[{"factors": [[[1, s * s * m]]]}, {"factors": [[[1, t * t * m]]]}]]
    normalized = []
    for expression in expressions:
        normalized.append([
            {
                "coefficient": canonical_rational(product.get("coefficient", 1)),
                "factors": [[[canonical_rational(c), canonical_rational(r)] for c, r in factor] for factor in product["factors"]],
            }
            for product in expression
        ])
    return {"expressions": normalized}


def _squared_identity_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("coefficient") is not None:
        q, m, r = constraints["coefficient"], constraints.get("radicand"), constraints["rhs_radical"]
    else:
        q, m = rng.randint(1, 4), rng.choice((2, 3, 5, 6, 7))
        r = 2 * q * _nonzero(rng, -5, 5)
    return {"coefficient": canonical_rational(q), "radicand": m, "rhs_radical": canonical_rational(r)}


def _power_relation_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    if constraints.get("expression") is not None:
        variable, power, value = constraints.get("variable", "a"), constraints.get("power", 3), constraints["value"]
        expression = constraints["expression"]
    else:
        variable, power, value, m = "a", 3, _nonzero(rng, -5, 5), rng.randint(1, 2)
        expression = [{"factors": [
            [[[1, {"a": 1}], [-m, {}]], 1], [[[1, {"a": 1}], [m, {}]], 1],
            [[[1, {"a": 2}], [-m, {"a": 1}], [m * m, {}]], 1], [[[1, {"a": 2}], [m, {"a": 1}], [m * m, {}]], 1],
        ]}]
    return {"variable": str(variable), "power": power, "value": canonical_rational(value),
            "expression": serialize_expression(expression)}


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "expand_polynomial_expressions": (_expand_givens, lambda g: expand_polynomial_expressions(g["expressions"])),
    "factor_by_cube_formulas": (_factor_givens, lambda g: factor_by_cube_formulas(g["polynomials"])),
    "evaluate_reciprocal_power_expressions": (
        _reciprocal_givens, lambda g: evaluate_reciprocal_power_expressions(g["base"], g["targets"]),
    ),
    "simplify_radical_expressions": (_radical_givens, lambda g: simplify_radical_expressions(g["expressions"])),
    "solve_rational_unknowns_from_squared_radical_identity": (
        _squared_identity_givens,
        lambda g: solve_rational_unknowns_from_squared_radical_identity(g["coefficient"], g["radicand"], g["rhs_radical"]),
    ),
    "evaluate_product_under_power_relation": (
        _power_relation_givens,
        lambda g: evaluate_product_under_power_relation(g["variable"], g["power"], g["value"], g["expression"]),
    ),
}
OPERATIONS = tuple(_OPERATIONS)


def build_multiplication_formulas_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_multiplication_formulas_operation:{operation}")
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


@_validator("expand_polynomial_expressions")
def validate_expand_polynomial_expressions_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    parts = answer["parts"]
    if len(parts) != len(givens["expressions"]):
        return False
    for expression, part in zip(givens["expressions"], parts):
        total, _ = expand_expression(expression)
        if parse_polynomial(part["expanded"]) != total or part["expanded_plain"] != polynomial_plain(total):
            return False
    return True


@_validator("factor_by_cube_formulas")
def validate_factor_by_cube_formulas_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    parts = answer["parts"]
    if len(parts) != len(givens["polynomials"]):
        return False
    for polynomial, part in zip(givens["polynomials"], parts):
        product: Polynomial = {(): Fraction(1)}
        for factor, power in part["factors"]:
            product = poly_mul(product, poly_pow(parse_polynomial(factor), power))
        powers = [power for _, power in part["factors"]]
        expected_powers = [3] if part["formula"].startswith("cube_of") else [1, 1]
        if product != parse_polynomial(polynomial) or powers != expected_powers:
            return False
    return True


@_validator("evaluate_reciprocal_power_expressions")
def validate_evaluate_reciprocal_power_expressions_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return answer == evaluate_reciprocal_power_expressions(givens["base"], givens["targets"]) and len(
        answer["values"]
    ) == len(givens["targets"])


@_validator("simplify_radical_expressions")
def validate_simplify_radical_expressions_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    parts = answer["parts"]
    if len(parts) != len(givens["expressions"]):
        return False
    for part in parts:
        radicands = [m for _, m in part["value"]]
        if radicands != sorted(set(radicands)) or any(squarefree_decomposition(m) != (1, m) for m in radicands):
            return False
    return answer == simplify_radical_expressions(givens["expressions"])


@_validator("solve_rational_unknowns_from_squared_radical_identity")
def validate_solve_rational_unknowns_from_squared_radical_identity_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, b = parse_exact_rational(answer["values"]["a"]), parse_exact_rational(answer["values"]["b"])
    q, r, m = parse_exact_rational(givens["coefficient"]), parse_exact_rational(givens["rhs_radical"]), givens["radicand"]
    return a * a + q * q * m == b and 2 * a * q == r


@_validator("evaluate_product_under_power_relation")
def validate_evaluate_product_under_power_relation_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return answer == evaluate_product_under_power_relation(
        givens["variable"], givens["power"], givens["value"], givens["expression"]
    )
