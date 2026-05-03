"""Pure binomial functions for vocational math B4."""

from __future__ import annotations

import math


def _validate_nonnegative_int(value: object, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer.")


def pascal_identity(n: int, r: int) -> int:
    """Return C(n, r) + C(n, r+1), equivalent to C(n+1, r+1)."""
    _validate_nonnegative_int(n, "n")
    _validate_nonnegative_int(r, "r")
    if n < 1 or r < 1 or r > n:
        raise ValueError("Require n >= 1 and 1 <= r <= n.")
    if r == n:
        return math.comb(n, r)
    return math.comb(n, r) + math.comb(n, r + 1)


def binomial_coefficient_sum(n: int) -> int:
    """Return sum of coefficients in (x + 1)^n."""
    _validate_nonnegative_int(n, "n")
    return 2**n


def binomial_expansion_coefficients(a: int, b: int, n: int) -> list[int]:
    """Return coefficients of (a*x + b)^n from x^n down to x^0."""
    if not isinstance(a, int) or isinstance(a, bool):
        raise ValueError("a must be an integer.")
    if not isinstance(b, int) or isinstance(b, bool):
        raise ValueError("b must be an integer.")
    _validate_nonnegative_int(n, "n")
    return [math.comb(n, k) * (a ** (n - k)) * (b**k) for k in range(n + 1)]


def binomial_term_coefficient(a: int, b: int, n: int, target_power: int) -> int:
    """Return coefficient of x^target_power in (a*x + b)^n."""
    if not isinstance(a, int) or isinstance(a, bool):
        raise ValueError("a must be an integer.")
    if not isinstance(b, int) or isinstance(b, bool):
        raise ValueError("b must be an integer.")
    _validate_nonnegative_int(n, "n")
    _validate_nonnegative_int(target_power, "target_power")
    if target_power > n:
        raise ValueError("target_power must be <= n.")
    k = n - target_power
    return math.comb(n, k) * (a**target_power) * (b**k)


def pascal_triangle_row(n: int) -> list[int]:
    """Return row n of Pascal's triangle from C(n,0) to C(n,n)."""
    _validate_nonnegative_int(n, "n")
    return [math.comb(n, r) for r in range(n + 1)]

