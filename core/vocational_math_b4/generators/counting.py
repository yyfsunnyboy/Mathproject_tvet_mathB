"""Deterministic B4 counting generators (Phase 4B-2)."""

from __future__ import annotations

import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.counting_domain_functions import (
    divisor_count_from_prime_factorization,
    factorial_ratio_solve_n,
    repeated_digit_arrangement_count,
)

PROBLEM_TYPE_ID = "repeated_permutation_digits"
GENERATOR_KEY = "b4.counting.repeated_permutation_digits"
DIVISOR_PROBLEM_TYPE_ID = "divisor_count_prime_factorization"
DIVISOR_GENERATOR_KEY = "b4.counting.divisor_count_prime_factorization"
FACTORIAL_SOLVE_PROBLEM_TYPE_ID = "factorial_equation_solve_n"
FACTORIAL_SOLVE_GENERATOR_KEY = "b4.counting.factorial_equation_solve_n"


def _make_numeric_choices(answer: int, rng: random.Random) -> list[int]:
    if answer < 0:
        raise ValueError("answer must be nonnegative for choice generation.")
    candidates = {
        answer,
        max(0, answer - 1),
        max(0, answer + 1),
        max(0, answer - 2),
        max(0, answer + 2),
        answer * 2,
        max(0, answer // 2),
        answer + 3,
    }
    choices = [answer]
    for value in candidates:
        if value not in choices:
            choices.append(value)
        if len(choices) == 4:
            break
    while len(choices) < 4:
        extra = max(0, answer + rng.randint(4, 12))
        if extra not in choices:
            choices.append(extra)
    rng.shuffle(choices)
    return choices


def _sample_parameters(rng: random.Random, difficulty: int) -> tuple[int, int]:
    if difficulty <= 1:
        digit_count = rng.randint(3, 5)
        length = rng.randint(2, 3)
    elif difficulty == 2:
        digit_count = rng.randint(4, 6)
        length = rng.randint(3, 4)
    else:
        digit_count = rng.randint(5, 8)
        length = rng.randint(3, 5)
    return digit_count, length


def generate(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a deterministic repeated-digit-arrangement problem payload."""
    if seen_parameter_tuples is not None and not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")

    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    parameter_tuple: tuple | None = None
    digit_count = length = 0
    for _ in range(50):
        digit_count, length = _sample_parameters(rng, difficulty)
        candidate = (PROBLEM_TYPE_ID, digit_count, length)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = repeated_digit_arrangement_count(
        digit_count=digit_count,
        length=length,
        allow_leading_zero=True,
        last_digit_filter=None,
    )
    question_text = (
        f"有 {digit_count} 個可用數字，每個數字可重複使用，排成 {length} 位數，共有多少種排法？"
    )
    explanation = f"每一位都有 {digit_count} 種選擇，使用 m^n 得 {digit_count}^{length}={answer}。"

    choices = _make_numeric_choices(answer, rng) if multiple_choice else []
    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": PROBLEM_TYPE_ID,
        "generator_key": GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "repeated_permutation_digits",
            "repeated_permutation",
            "multiplication_principle",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_rep_perm_digits_01", "repeated_permutation_digits"],
        "parameters": {
            "digit_count": digit_count,
            "length": length,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])

    seen.add(parameter_tuple)
    return payload


def _ensure_seen_set(seen_parameter_tuples: set[tuple] | None) -> set[tuple]:
    if seen_parameter_tuples is None:
        return set()
    if not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")
    return seen_parameter_tuples


def _validate_and_finalize(payload: dict, multiple_choice: bool) -> None:
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])


def _sample_divisor_parameters(rng: random.Random, difficulty: int) -> tuple[list[int], list[int]]:
    prime_pool = [2, 3, 5, 7, 11]
    if difficulty <= 1:
        prime_count = 2
        exponent_min, exponent_max = 1, 3
    elif difficulty == 2:
        prime_count = rng.randint(2, 3)
        exponent_min, exponent_max = 1, 4
    else:
        prime_count = rng.randint(3, 4)
        exponent_min, exponent_max = 1, 5
    primes = sorted(rng.sample(prime_pool, prime_count))
    exponents = [rng.randint(exponent_min, exponent_max) for _ in range(prime_count)]
    return primes, exponents


def divisor_count_prime_factorization(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic divisor count problems from prime factorization."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    primes: list[int] = []
    exponents: list[int] = []
    for _ in range(50):
        primes, exponents = _sample_divisor_parameters(rng, difficulty)
        candidate = (DIVISOR_PROBLEM_TYPE_ID, tuple(primes), tuple(exponents))
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    factors_str = r" \times ".join(f"{p}^{{{e}}}" for p, e in zip(primes, exponents))
    answer = divisor_count_from_prime_factorization(exponents)
    question_text = f"已知 $N = {factors_str}$，則 $N$ 有多少個正因數？"
    product_expr = "".join(f"({e}+1)" for e in exponents)
    explanation = (
        r"若 $N = p_1^{a_1} \times p_2^{a_2} \times \cdots$，"
        r"正因數個數為 $(a_1+1)(a_2+1)\cdots$，"
        f"本題為 ${product_expr}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": DIVISOR_PROBLEM_TYPE_ID,
        "generator_key": DIVISOR_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "divisor_count_prime_factorization",
            "multiplication_principle",
            "prime_factorization",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_divisor_count_prime_factorization_02",
            "divisor_count_prime_factorization",
        ],
        "parameters": {
            "primes": primes,
            "exponents": exponents,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def factorial_equation_solve_n(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic factorial-ratio equation problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 12):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    if difficulty <= 1:
        low, high = 3, 9
    elif difficulty == 2:
        low, high = 6, 15
    else:
        low, high = 10, 20

    parameter_tuple: tuple | None = None
    k = 0
    for _ in range(50):
        k = rng.randint(low, high)
        candidate = (FACTORIAL_SOLVE_PROBLEM_TYPE_ID, k)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = factorial_ratio_solve_n(0, -1, k)
    question_text = f"若 $\\frac{{n!}}{{(n-1)!}}={k}$，求正整數 $n$。"
    explanation = f"由 $\\frac{{n!}}{{(n-1)!}}=n$，可得 $n={k}$。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": FACTORIAL_SOLVE_PROBLEM_TYPE_ID,
        "generator_key": FACTORIAL_SOLVE_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["factorial_equation_solve_n", "factorial", "solve_n"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_factorial_solve_n_02", "factorial_equation_solve_n"],
        "parameters": {
            "k": k,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload
