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
    factorial,
    factorial_ratio_solve_n,
    multiplication_principle_count,
    permutation,
    repeated_choice_count,
    repeated_digit_arrangement_count,
)

PROBLEM_TYPE_ID = "repeated_permutation_digits"
GENERATOR_KEY = "b4.counting.repeated_permutation_digits"
DIVISOR_PROBLEM_TYPE_ID = "divisor_count_prime_factorization"
DIVISOR_GENERATOR_KEY = "b4.counting.divisor_count_prime_factorization"
FACTORIAL_SOLVE_PROBLEM_TYPE_ID = "factorial_equation_solve_n"
FACTORIAL_SOLVE_GENERATOR_KEY = "b4.counting.factorial_equation_solve_n"
FACTORIAL_EVAL_PROBLEM_TYPE_ID = "factorial_evaluation"
FACTORIAL_EVAL_GENERATOR_KEY = "b4.counting.factorial_evaluation"
MULT_PRINCIPLE_INDEPENDENT_PROBLEM_TYPE_ID = "mult_principle_independent_choices"
MULT_PRINCIPLE_INDEPENDENT_GENERATOR_KEY = "b4.counting.mult_principle_independent_choices"
MULT_DIGITS_NO_REPEAT_PROBLEM_TYPE_ID = "mult_digits_no_repeat"
MULT_DIGITS_NO_REPEAT_GENERATOR_KEY = "b4.counting.mult_digits_no_repeat"
REPEATED_PERM_ASSIGN_PROBLEM_TYPE_ID = "repeated_permutation_assignment"
REPEATED_PERM_ASSIGN_GENERATOR_KEY = "b4.counting.repeated_permutation_assignment"


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


def _sample_factorial_evaluation_params(rng: random.Random, difficulty: int) -> tuple[int, int, str]:
    variant = rng.choice(["direct", "ratio"])
    if difficulty <= 1:
        if variant == "direct":
            n = rng.randint(3, 6)
            k = 0
        else:
            n = rng.randint(5, 8)
            k = rng.randint(1, 3)
    elif difficulty == 2:
        if variant == "direct":
            n = rng.randint(5, 8)
            k = 0
        else:
            n = rng.randint(7, 10)
            k = rng.randint(2, 4)
    else:
        if variant == "direct":
            n = rng.randint(7, 10)
            k = 0
        else:
            n = rng.randint(9, 12)
            k = rng.randint(3, 5)
    if variant == "direct":
        k = 0
    else:
        if k > n:
            k = n
    return n, k, variant


def factorial_evaluation(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic factorial value or factorial-ratio problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 17):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = k = 0
    variant = ""

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (3, 0, "direct"),
            (5, 2, "ratio"),
            (6, 0, "direct"),
            (7, 1, "ratio"),
            (4, 0, "direct"),
        ][seed - 1]
        n, k, variant = preset
        cand = (FACTORIAL_EVAL_PROBLEM_TYPE_ID, n, k, variant)
        if cand not in seen:
            parameter_tuple = cand

    if parameter_tuple is None:
        for _ in range(50):
            n, k, variant = _sample_factorial_evaluation_params(rng, difficulty)
            candidate = (FACTORIAL_EVAL_PROBLEM_TYPE_ID, n, k, variant)
            if candidate not in seen:
                parameter_tuple = candidate
                break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if variant == "direct":
        answer = factorial(n)
        question_text = f"計算 ${n}!$ 的值。"
        product_part = r" \times ".join(str(i) for i in range(n, 0, -1))
        explanation = f"${n}!={product_part}={answer}$。"
    else:
        answer = factorial(n) // factorial(n - k)
        question_text = f"計算 $\\frac{{{n}!}}{{{(n - k)}!}}$ 的值。"
        if k == 0:
            factors_str = "1"
        else:
            factors_str = r" \times ".join(str(i) for i in range(n, n - k, -1))
        explanation = f"$\\frac{{{n}!}}{{{(n - k)}!}}={factors_str}={answer}$。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": FACTORIAL_EVAL_PROBLEM_TYPE_ID,
        "generator_key": FACTORIAL_EVAL_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["factorial_evaluation", "factorial", "factorial_notation"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_factorial_evaluation_01", "factorial_evaluation"],
        "parameters": {
            "n": n,
            "k": k,
            "variant": variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_mult_principle_independent_params(
    rng: random.Random, difficulty: int
) -> tuple[list[str], list[int]]:
    if difficulty <= 1:
        stage_count = rng.choice([2, 3])
        low, high = 2, 8
    elif difficulty == 2:
        stage_count = rng.choice([3, 4])
        low, high = 2, 10
    else:
        stage_count = rng.choice([4, 5])
        low, high = 3, 12
    name_pools = [
        ["搭公車", "轉捷運", "步行路段"],
        ["早餐", "午餐", "點心", "晚餐"],
        ["選上衣", "選褲子", "選鞋子", "選帽子", "選外套"],
        ["填志願一", "填志願二", "填志願三", "填志願四", "填志願五"],
    ]
    eligible = [p for p in name_pools if len(p) >= stage_count]
    pool = rng.choice(eligible if eligible else name_pools)
    stage_count = min(stage_count, len(pool))
    stage_names = rng.sample(pool, stage_count)
    counts = [rng.randint(low, high) for _ in range(stage_count)]
    return stage_names, counts


def mult_principle_independent_choices(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic multiplication-principle (independent stages) problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 19):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    stage_names: list[str] = []
    counts: list[int] = []

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (["搭公車", "轉捷運"], [3, 4]),
            (["早餐", "午餐", "點心"], [2, 3, 2]),
            (["選上衣", "選褲子"], [5, 6]),
            (["填志願一", "填志願二", "填志願三"], [4, 3, 2]),
            (["搭公車", "轉捷運", "步行路段"], [2, 2, 3]),
        ][seed - 1]
        stage_names, counts = list(preset[0]), list(preset[1])
        cand = (MULT_PRINCIPLE_INDEPENDENT_PROBLEM_TYPE_ID, tuple(stage_names), tuple(counts))
        if cand not in seen:
            parameter_tuple = cand

    if parameter_tuple is None:
        for _ in range(50):
            stage_names, counts = _sample_mult_principle_independent_params(rng, difficulty)
            candidate = (
                MULT_PRINCIPLE_INDEPENDENT_PROBLEM_TYPE_ID,
                tuple(stage_names),
                tuple(counts),
            )
            if candidate not in seen:
                parameter_tuple = candidate
                break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = multiplication_principle_count(counts)
    stage_parts = [f"{name}有 {c} 種選法" for name, c in zip(stage_names, counts)]
    question_text = (
        f"完成一件事分為 {len(stage_names)} 個獨立階段："
        f"{'、'.join(stage_parts)}，共有多少種方法？"
    )
    prod_latex = r" \times ".join(str(c) for c in counts)
    explanation = (
        "使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。"
        f"例如：${prod_latex}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": MULT_PRINCIPLE_INDEPENDENT_PROBLEM_TYPE_ID,
        "generator_key": MULT_PRINCIPLE_INDEPENDENT_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "mult_principle_independent_choices",
            "multiplication_principle",
            "independent_stages",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_mult_principle_independent_choices_01",
            "mult_principle_independent_choices",
        ],
        "parameters": {
            "stage_names": stage_names,
            "counts": counts,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_mult_digits_no_repeat_params(
    rng: random.Random, difficulty: int
) -> tuple[int, int, bool]:
    if difficulty <= 1:
        digit_pool_size = rng.randint(5, 7)
        positions = rng.randint(2, 3)
        allow_zero = rng.choice([True, False])
    elif difficulty == 2:
        digit_pool_size = rng.randint(6, 9)
        positions = rng.randint(3, 4)
        allow_zero = rng.choice([True, False])
    else:
        digit_pool_size = rng.randint(7, 10)
        positions = rng.randint(3, 5)
        allow_zero = rng.choice([True, False])
    if positions > digit_pool_size:
        positions = digit_pool_size
    return digit_pool_size, positions, allow_zero


def mult_digits_no_repeat(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic no-repeat digit arrangement counting problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 23):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    digit_pool_size = positions = 0
    allow_zero = False

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (5, 3, False),
            (6, 2, True),
            (7, 3, True),
            (5, 2, False),
            (6, 3, False),
        ][seed - 1]
        digit_pool_size, positions, allow_zero = preset
        cand = (MULT_DIGITS_NO_REPEAT_PROBLEM_TYPE_ID, digit_pool_size, positions, allow_zero)
        if cand not in seen:
            parameter_tuple = cand

    if parameter_tuple is None:
        for _ in range(50):
            digit_pool_size, positions, allow_zero = _sample_mult_digits_no_repeat_params(rng, difficulty)
            candidate = (MULT_DIGITS_NO_REPEAT_PROBLEM_TYPE_ID, digit_pool_size, positions, allow_zero)
            if candidate not in seen:
                parameter_tuple = candidate
                break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if not allow_zero:
        answer = permutation(digit_pool_size, positions)
        digits_desc = "、".join(str(i) for i in range(1, digit_pool_size + 1))
        question_text = (
            f"使用 {digits_desc} 共 {digit_pool_size} 個數字，組成不重複的 {positions} 位數，共有多少個？"
        )
        explanation = (
            f"數字不可重複，使用 $P^{{n}}_{{r}}$ 得 $P^{{{digit_pool_size}}}_{{{positions}}}={answer}$。"
        )
    else:
        answer = (digit_pool_size - 1) * permutation(digit_pool_size - 1, positions - 1)
        digits_desc = "、".join(str(i) for i in range(0, digit_pool_size))
        question_text = (
            f"使用 {digits_desc} 共 {digit_pool_size} 個數字，組成不重複的 {positions} 位數，"
            "且首位不可為 $0$，共有多少個？"
        )
        if positions == 1:
            explanation = (
                f"首位不可為 $0$，共有 ${digit_pool_size - 1}$ 種方法，即答案為 ${answer}$。"
            )
        else:
            explanation = (
                "第一位不能為 $0$，有 "
                f"${digit_pool_size - 1}$ 種選法；其餘 ${positions - 1}$ 位有 "
                f"$P^{{{digit_pool_size - 1}}}_{{{positions - 1}}}$ 種，所以 "
                f"${digit_pool_size - 1}\\times P^{{{digit_pool_size - 1}}}_{{{positions - 1}}}={answer}$。"
            )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": MULT_DIGITS_NO_REPEAT_PROBLEM_TYPE_ID,
        "generator_key": MULT_DIGITS_NO_REPEAT_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["mult_digits_no_repeat", "multiplication_principle", "digits_no_repeat"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_mult_digits_no_repeat_01", "mult_digits_no_repeat"],
        "parameters": {
            "digit_pool_size": digit_pool_size,
            "positions": positions,
            "allow_zero": allow_zero,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_repeated_permutation_assignment_params(
    rng: random.Random, difficulty: int
) -> tuple[int, int, str]:
    if difficulty <= 1:
        choices_per_position = rng.randint(2, 5)
        positions = rng.randint(2, 4)
    elif difficulty == 2:
        choices_per_position = rng.randint(3, 8)
        positions = rng.randint(3, 5)
    else:
        choices_per_position = rng.randint(4, 10)
        positions = rng.randint(4, 6)
    context = rng.choice(["tasks_to_people", "letters_to_mailboxes", "items_to_boxes"])
    return choices_per_position, positions, context


def repeated_permutation_assignment(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic repeated-choice assignment (m^n) problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 29):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    choices_per_position = positions = 0
    context = ""

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (4, 3, "tasks_to_people"),
            (3, 4, "letters_to_mailboxes"),
            (5, 2, "items_to_boxes"),
            (4, 4, "tasks_to_people"),
            (3, 3, "letters_to_mailboxes"),
        ][seed - 1]
        choices_per_position, positions, context = preset
        cand = (REPEATED_PERM_ASSIGN_PROBLEM_TYPE_ID, choices_per_position, positions, context)
        if cand not in seen:
            parameter_tuple = cand

    if parameter_tuple is None:
        for _ in range(50):
            choices_per_position, positions, context = _sample_repeated_permutation_assignment_params(
                rng, difficulty
            )
            candidate = (REPEATED_PERM_ASSIGN_PROBLEM_TYPE_ID, choices_per_position, positions, context)
            if candidate not in seen:
                parameter_tuple = candidate
                break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = repeated_choice_count(choices_per_position, positions)
    m, n = choices_per_position, positions
    if context == "tasks_to_people":
        question_text = (
            f"將 {n} 個不同工作分別指派給 {m} 位人員，每個工作可指派給任一人，"
            "且同一人可負責多個工作，共有多少種指派方式？"
        )
    elif context == "letters_to_mailboxes":
        question_text = (
            f"將 {n} 封不同信件分別投入 {m} 個信箱，每封信可投入任一信箱，"
            "且同一信箱可收到多封信，共有多少種投法？"
        )
    else:
        question_text = (
            f"將 {n} 件不同物品分別放入 {m} 個盒子，每件物品可放入任一盒子，"
            "且同一盒子可放多件物品，共有多少種放法？"
        )

    explanation = (
        "每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。"
        f"例如：${m}^{{{n}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": REPEATED_PERM_ASSIGN_PROBLEM_TYPE_ID,
        "generator_key": REPEATED_PERM_ASSIGN_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["repeated_permutation_assignment", "repeated_choice", "assignment"],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_repeated_permutation_assignment_01",
            "repeated_permutation_assignment",
        ],
        "parameters": {
            "choices_per_position": choices_per_position,
            "positions": positions,
            "context": context,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload
