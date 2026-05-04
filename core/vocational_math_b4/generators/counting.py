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


def _sample_addition_parameters(rng: random.Random, difficulty: int) -> tuple[list[str], list[int]]:
    name_pool = ["球類社團", "音樂社團", "美術社團", "科學社團", "語文社團", "志工社團", "舞蹈社團"]
    if difficulty <= 1:
        category_count = rng.choice([2, 3])
        low, high = 2, 8
    elif difficulty == 2:
        category_count = rng.choice([3, 4])
        low, high = 3, 12
    else:
        category_count = rng.choice([4, 5])
        low, high = 5, 20
    category_names = rng.sample(name_pool, category_count)
    counts = [rng.randint(low, high) for _ in range(category_count)]
    return category_names, counts


def add_principle_mutually_exclusive_choice(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    from core.vocational_math_b4.domain.counting_domain_functions import addition_principle_count

    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)
    problem_type_id = "add_principle_mutually_exclusive_choice"
    generator_key = "b4.counting.add_principle_mutually_exclusive_choice"

    parameter_tuple: tuple | None = None
    category_names: list[str] = []
    counts: list[int] = []
    for _ in range(50):
        category_names, counts = _sample_addition_parameters(rng, difficulty)
        candidate = (problem_type_id, tuple(category_names), tuple(counts))
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = addition_principle_count(counts)
    parts = [f"{c} 種{name}" for name, c in zip(category_names, counts)]
    question_text = f"某校社團活動可選擇{'、'.join(parts)}，若只選擇其中一種社團，共有多少種選法？"
    explanation = f"使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：${'+'.join(str(x) for x in counts)}={answer}$。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": problem_type_id,
        "generator_key": generator_key,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "add_principle_mutually_exclusive_choice",
            "addition_principle",
            "mutually_exclusive",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_add_principle_mutually_exclusive_choice_01",
            "add_principle_mutually_exclusive_choice",
        ],
        "parameters": {
            "category_names": category_names,
            "counts": counts,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_repeated_choice_parameters(rng: random.Random, difficulty: int) -> tuple[int, int]:
    if difficulty <= 1:
        choices_per_position = rng.randint(2, 5)
        positions = rng.randint(2, 4)
    elif difficulty == 2:
        choices_per_position = rng.randint(3, 8)
        positions = rng.randint(3, 5)
    else:
        choices_per_position = rng.randint(4, 10)
        positions = rng.randint(4, 6)
    return choices_per_position, positions


def repeated_choice_basic(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    from core.vocational_math_b4.domain.counting_domain_functions import repeated_choice_count

    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)
    problem_type_id = "repeated_choice_basic"
    generator_key = "b4.counting.repeated_choice_basic"

    parameter_tuple: tuple | None = None
    choices_per_position = positions = 0
    if seed is not None:
        if difficulty <= 1:
            choices_vals = [2, 3, 4, 5]
            position_vals = [2, 3, 4]
        elif difficulty == 2:
            choices_vals = [3, 4, 5, 6, 7, 8]
            position_vals = [3, 4, 5]
        else:
            choices_vals = [4, 5, 6, 7, 8, 9, 10]
            position_vals = [4, 5, 6]
        idx = max(0, seed - 1)
        choices_per_position = choices_vals[idx % len(choices_vals)]
        positions = position_vals[(idx // len(choices_vals)) % len(position_vals)]
        seeded_candidate = (problem_type_id, choices_per_position, positions)
        if seeded_candidate not in seen:
            parameter_tuple = seeded_candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        choices_per_position, positions = _sample_repeated_choice_parameters(rng, difficulty)
        candidate = (problem_type_id, choices_per_position, positions)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = repeated_choice_count(choices_per_position, positions)
    question_text = (
        f"有 {positions} 位同學，每人可從 {choices_per_position} 種飲料中任選一種，且可重複選擇，共有多少種選法？"
    )
    explanation = (
        f"每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{{n}}$。例如："
        f"${choices_per_position}^{{{positions}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": problem_type_id,
        "generator_key": generator_key,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "repeated_choice_basic",
            "repeated_choice",
            "multiplication_principle",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_repeated_choice_basic_01", "repeated_choice_basic"],
        "parameters": {
            "choices_per_position": choices_per_position,
            "positions": positions,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload
