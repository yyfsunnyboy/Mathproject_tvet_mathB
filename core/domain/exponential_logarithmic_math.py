# -*- coding: utf-8 -*-
"""Exact exponent and logarithm primitives for B3 Chapter 4.

Pure math. No randomness, no Flask, no DB. Rational powers and rational
logarithms are exact (Fraction). Common-log approximations use only the
four-decimal values a question explicitly gives.
"""

from __future__ import annotations

from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction
from typing import Iterable, Mapping

Monomial = dict[str, Fraction]

GIVEN_LOG10: dict[int, Decimal] = {
    2: Decimal("0.3010"),
    3: Decimal("0.4771"),
    5: Decimal("0.6990"),
    7: Decimal("0.8451"),
}


def as_fraction(value: object) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        return Fraction(value)
    return Fraction(str(value))


def integer_root(n: int, k: int) -> int | None:
    """Exact integer k-th root of n, or None."""
    if k <= 0:
        raise ValueError("root_index")
    if n < 0:
        if k % 2 == 0:
            return None
        inner = integer_root(-n, k)
        return None if inner is None else -inner
    if n in (0, 1):
        return n
    guess = int(round(n ** (1.0 / k)))
    for candidate in (guess - 1, guess, guess + 1):
        if candidate >= 0 and candidate**k == n:
            return candidate
    return None


def rational_power(base: object, exponent: object) -> Fraction:
    """base ** exponent when the result is rational; otherwise ValueError."""
    b = as_fraction(base)
    e = as_fraction(exponent)
    if b == 0:
        if e <= 0:
            raise ValueError("zero_power_undefined")
        return Fraction(0)
    if b < 0 and e.denominator % 2 == 0:
        raise ValueError("even_root_of_negative")
    num = integer_root(b.numerator, e.denominator)
    den = integer_root(b.denominator, e.denominator)
    if num is None or den is None:
        raise ValueError("irrational_power")
    return Fraction(num, den) ** e.numerator


def factor_int(n: int) -> dict[int, int]:
    if n <= 0:
        raise ValueError("factor_positive_only")
    out: dict[int, int] = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def prime_vector(value: object, exponent: object = 1) -> dict[int, Fraction]:
    """value ** exponent as {prime: rational exponent}; value must be > 0."""
    v = as_fraction(value)
    if v <= 0:
        raise ValueError("log_argument_not_positive")
    e = as_fraction(exponent)
    out: dict[int, Fraction] = {}
    for p, k in factor_int(v.numerator).items():
        out[p] = out.get(p, Fraction(0)) + e * k
    for p, k in factor_int(v.denominator).items():
        out[p] = out.get(p, Fraction(0)) - e * k
    return {p: k for p, k in out.items() if k != 0}


def log_exact(base: object, arg: object, *, base_exp: object = 1, arg_exp: object = 1) -> Fraction:
    """log_{base^base_exp}(arg^arg_exp) when rational; otherwise ValueError.

    Enforces the logarithm domain: base > 0, base != 1, argument > 0.
    """
    vb = prime_vector(base, base_exp)
    if not vb:
        raise ValueError("log_base_is_one")
    va = prime_vector(arg, arg_exp)
    if not va:
        return Fraction(0)
    pivot = next(iter(vb))
    ratio = va.get(pivot, Fraction(0)) / vb[pivot]
    for p in set(vb) | set(va):
        if va.get(p, Fraction(0)) != ratio * vb.get(p, Fraction(0)):
            raise ValueError("log_not_rational")
    return ratio


def log_domain_ok(base: object, arg: object) -> bool:
    b = as_fraction(base)
    a = as_fraction(arg)
    return b > 0 and b != 1 and a > 0


# ---------------------------------------------------------------- monomials

def mono(**exps: object) -> Monomial:
    return {k: as_fraction(v) for k, v in exps.items() if as_fraction(v) != 0}


def mono_mul(*items: Mapping[str, Fraction]) -> Monomial:
    out: dict[str, Fraction] = {}
    for item in items:
        for var, e in item.items():
            out[var] = out.get(var, Fraction(0)) + as_fraction(e)
    return {k: v for k, v in sorted(out.items()) if v != 0}


def mono_pow(item: Mapping[str, Fraction], exponent: object) -> Monomial:
    e = as_fraction(exponent)
    return {k: as_fraction(v) * e for k, v in sorted(item.items()) if as_fraction(v) * e != 0}


def mono_plain(item: Mapping[str, Fraction]) -> str:
    """Parser-safe canonical answer, e.g. ``a^10*b^(-1/2)``."""
    parts = []
    for var, e in sorted(item.items()):
        e = as_fraction(e)
        if e == 0:
            continue
        if e == 1:
            parts.append(var)
        elif e.denominator == 1 and e > 0:
            parts.append(f"{var}^{e.numerator}")
        else:
            parts.append(f"{var}^({fraction_plain(e)})")
    return "*".join(parts) if parts else "1"


# ------------------------------------------------------------ formatting

def fraction_plain(value: object) -> str:
    v = as_fraction(value)
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def decimal_plain(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text


def fraction_as_terminating_decimal(value: object) -> str | None:
    v = as_fraction(value)
    den = v.denominator
    for p in (2, 5):
        while den % p == 0:
            den //= p
    if den != 1:
        return None
    with localcontext() as ctx:
        ctx.prec = 40
        return decimal_plain(Decimal(v.numerator) / Decimal(v.denominator))


# ------------------------------------------------------- common logarithm

def true_log10(value: object) -> Decimal:
    v = as_fraction(value)
    if v <= 0:
        raise ValueError("log_argument_not_positive")
    with localcontext() as ctx:
        ctx.prec = 50
        return (Decimal(v.numerator).ln() - Decimal(v.denominator).ln()) / Decimal(10).ln()


def approx_log10(value: object, given: Mapping[int, Decimal] | None = None) -> Decimal:
    """log10 built only from the given prime approximations (default 2,3,5,7)."""
    table = dict(GIVEN_LOG10 if given is None else given)
    total = Decimal(0)
    for p, k in prime_vector(value).items():
        if p not in table:
            raise ValueError(f"no_given_log_for_prime:{p}")
        total += table[p] * Decimal(k.numerator) / Decimal(k.denominator)
    return total


def round_half_up(value: Decimal, places: int) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def floor_decimal(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_FLOOR))


def table_log(value: object) -> Decimal:
    """Four-decimal common-log table value (mantissa for 1 <= value < 10)."""
    return round_half_up(true_log10(value), 4)


def characteristic_mantissa(log_value: Decimal) -> tuple[int, Decimal]:
    n = floor_decimal(log_value)
    return n, log_value - n


def digit_count(log_value: Decimal) -> int:
    if log_value < 0:
        raise ValueError("digit_count_needs_number_at_least_one")
    return floor_decimal(log_value) + 1


def first_nonzero_decimal_place(log_value: Decimal) -> int:
    if log_value >= 0:
        raise ValueError("first_nonzero_needs_number_below_one")
    return -floor_decimal(log_value)


def robust_floor(approx: Decimal, exact: Decimal, *, margin: Decimal = Decimal("0.01")) -> bool:
    """True when both values share a floor and neither sits near an integer."""
    if floor_decimal(approx) != floor_decimal(exact):
        return False
    for value in (approx, exact):
        frac = value - floor_decimal(value)
        if frac < margin or frac > 1 - margin:
            return False
    return True


def sum_fractions(values: Iterable[object]) -> Fraction:
    total = Fraction(0)
    for v in values:
        total += as_fraction(v)
    return total
