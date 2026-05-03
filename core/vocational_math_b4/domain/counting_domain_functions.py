"""Pure counting and combinatorics functions for vocational math B4."""

from __future__ import annotations

import itertools
import math
from functools import reduce
from operator import mul


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_nonnegative_int(value: object, name: str) -> None:
    if not _is_nonnegative_int(value):
        raise ValueError(f"{name} must be a nonnegative integer.")


def _validate_nonempty_nonnegative_int_list(values: list[int], name: str) -> None:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{name} must be a non-empty list.")
    for idx, value in enumerate(values):
        _validate_nonnegative_int(value, f"{name}[{idx}]")


def addition_principle_count(counts: list[int]) -> int:
    """Return the sum of mutually exclusive counts."""
    _validate_nonempty_nonnegative_int_list(counts, "counts")
    return sum(counts)


def multiplication_principle_count(counts: list[int]) -> int:
    """Return the product of independent choice counts."""
    _validate_nonempty_nonnegative_int_list(counts, "counts")
    return reduce(mul, counts, 1)


def factorial(n: int) -> int:
    """Return n! for a nonnegative integer n."""
    _validate_nonnegative_int(n, "n")
    return math.factorial(n)


def factorial_ratio_solve_n(
    numerator_offset: int,
    denominator_offset: int,
    target: int,
    search_min: int = 1,
    search_max: int = 20,
) -> int:
    """Solve unique n in range for (n+a)!/(n+b)! == target."""
    for name, value in (("numerator_offset", numerator_offset), ("denominator_offset", denominator_offset)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{name} must be an integer.")
    _validate_nonnegative_int(target, "target")
    if target == 0:
        raise ValueError("target must be positive.")
    if not isinstance(search_min, int) or isinstance(search_min, bool):
        raise ValueError("search_min must be an integer.")
    if not isinstance(search_max, int) or isinstance(search_max, bool):
        raise ValueError("search_max must be an integer.")
    if search_min > search_max:
        raise ValueError("search_min must be <= search_max.")

    matches: list[int] = []
    for n in range(search_min, search_max + 1):
        top = n + numerator_offset
        bottom = n + denominator_offset
        if top < 0 or bottom < 0:
            continue
        top_fact = math.factorial(top)
        bottom_fact = math.factorial(bottom)
        if top_fact % bottom_fact != 0:
            continue
        if top_fact // bottom_fact == target:
            matches.append(n)

    if len(matches) != 1:
        raise ValueError(f"Expected exactly one solution for n, found {len(matches)}.")
    return matches[0]


def permutation(n: int, r: int) -> int:
    """Return P(n, r)."""
    _validate_nonnegative_int(n, "n")
    _validate_nonnegative_int(r, "r")
    if n < r:
        raise ValueError("n must be >= r.")
    if hasattr(math, "perm"):
        return math.perm(n, r)
    return math.factorial(n) // math.factorial(n - r)


def combination(n: int, r: int) -> int:
    """Return C(n, r)."""
    _validate_nonnegative_int(n, "n")
    _validate_nonnegative_int(r, "r")
    if n < r:
        raise ValueError("n must be >= r.")
    return math.comb(n, r)


def repeated_choice_count(choices_per_position: int, positions: int) -> int:
    """Return choices_per_position ** positions."""
    _validate_nonnegative_int(choices_per_position, "choices_per_position")
    _validate_nonnegative_int(positions, "positions")
    return choices_per_position**positions


def repeated_digit_arrangement_count(
    digit_count: int,
    length: int,
    allow_leading_zero: bool = True,
    last_digit_filter: str | None = None,
) -> int:
    """Count repeated digit arrangements by count-only assumptions."""
    _validate_nonnegative_int(digit_count, "digit_count")
    _validate_nonnegative_int(length, "length")
    if last_digit_filter not in (None, "even", "odd"):
        raise ValueError("last_digit_filter must be one of None, 'even', 'odd'.")
    if not allow_leading_zero:
        raise ValueError("allow_leading_zero=False is unsupported here; use digit_arrangement_count.")
    if length == 0:
        return 1
    if last_digit_filter is None:
        return digit_count**length

    even_count = (digit_count + 1) // 2
    odd_count = digit_count // 2
    last_count = even_count if last_digit_filter == "even" else odd_count
    return (digit_count ** (length - 1)) * last_count


def repeated_assignment_count(
    item_count: int,
    recipient_count: int,
    allow_empty: bool = True,
) -> int:
    """Count assignments of items to recipients with optional empties."""
    _validate_nonnegative_int(item_count, "item_count")
    _validate_nonnegative_int(recipient_count, "recipient_count")
    if not allow_empty:
        raise ValueError("allow_empty=False is not implemented in this phase.")
    return recipient_count**item_count


def divisor_count_from_prime_factorization(exponents: list[int]) -> int:
    """Return divisor count from prime-power exponents."""
    _validate_nonempty_nonnegative_int_list(exponents, "exponents")
    return reduce(mul, (e + 1 for e in exponents), 1)


def digit_arrangement_count(
    digits: list[int],
    length: int,
    allow_repetition: bool = False,
    allow_leading_zero: bool = False,
    last_digit_filter: str | None = None,
) -> int:
    """Count digit arrangements under repetition/leading/parity constraints."""
    if not isinstance(digits, list) or not digits:
        raise ValueError("digits must be a non-empty list.")
    if len(set(digits)) != len(digits):
        raise ValueError("digits must contain unique elements.")
    for idx, d in enumerate(digits):
        if not isinstance(d, int) or isinstance(d, bool):
            raise ValueError(f"digits[{idx}] must be an integer.")
    _validate_nonnegative_int(length, "length")
    if last_digit_filter not in (None, "even", "odd"):
        raise ValueError("last_digit_filter must be one of None, 'even', 'odd'.")
    if length == 0:
        return 1
    if not allow_repetition and length > len(digits):
        raise ValueError("length cannot exceed number of digits when allow_repetition is False.")

    pool = itertools.product(digits, repeat=length) if allow_repetition else itertools.permutations(digits, length)
    count = 0
    for seq in pool:
        if not allow_leading_zero and seq[0] == 0:
            continue
        if last_digit_filter == "even" and seq[-1] % 2 != 0:
            continue
        if last_digit_filter == "odd" and seq[-1] % 2 == 0:
            continue
        count += 1
    return count


def adjacent_arrangement_count(
    total_items: int,
    block_size: int,
    distinct: bool = True,
) -> int:
    """Count arrangements where a designated block stays adjacent."""
    _validate_nonnegative_int(total_items, "total_items")
    _validate_nonnegative_int(block_size, "block_size")
    if not distinct:
        raise ValueError("distinct must be True in this phase.")
    if block_size < 2 or total_items < block_size:
        raise ValueError("Require total_items >= block_size >= 2.")
    return math.factorial(total_items - block_size + 1) * math.factorial(block_size)


def non_adjacent_arrangement_count(
    total_items: int,
    separated_items: int,
    distinct: bool = True,
) -> int:
    """Count arrangements where designated items are pairwise non-adjacent."""
    _validate_nonnegative_int(total_items, "total_items")
    _validate_nonnegative_int(separated_items, "separated_items")
    if not distinct:
        raise ValueError("distinct must be True in this phase.")
    if separated_items < 2 or total_items < separated_items:
        raise ValueError("Require total_items >= separated_items >= 2.")

    valid_position_sets = 0
    for positions in itertools.combinations(range(total_items), separated_items):
        if all(positions[i + 1] - positions[i] > 1 for i in range(len(positions) - 1)):
            valid_position_sets += 1

    return valid_position_sets * math.factorial(separated_items) * math.factorial(total_items - separated_items)


def polygon_diagonal_count(n: int) -> int:
    """Return number of diagonals in an n-gon."""
    _validate_nonnegative_int(n, "n")
    if n < 4:
        raise ValueError("n must be >= 4.")
    return math.comb(n, 2) - n


def polygon_triangle_count(n: int) -> int:
    """Return number of triangles from vertices of an n-gon."""
    _validate_nonnegative_int(n, "n")
    if n < 3:
        raise ValueError("n must be >= 3.")
    return math.comb(n, 3)


def combination_equation_solve_n(
    r: int,
    target: int,
    search_min: int = 0,
    search_max: int = 50,
) -> int:
    """Solve unique n in range for C(n, r) == target."""
    _validate_nonnegative_int(r, "r")
    _validate_nonnegative_int(target, "target")
    if target == 0:
        raise ValueError("target must be positive.")
    if not isinstance(search_min, int) or isinstance(search_min, bool):
        raise ValueError("search_min must be an integer.")
    if not isinstance(search_max, int) or isinstance(search_max, bool):
        raise ValueError("search_max must be an integer.")
    if search_min > search_max:
        raise ValueError("search_min must be <= search_max.")

    matches = [n for n in range(search_min, search_max + 1) if n >= r and math.comb(n, r) == target]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one solution for n, found {len(matches)}.")
    return matches[0]


def enumeration_count(branches: list[int]) -> int:
    """Return product of branch counts in a tree-like enumeration."""
    _validate_nonempty_nonnegative_int_list(branches, "branches")
    return reduce(mul, branches, 1)
