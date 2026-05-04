"""Deterministic B4 binomial generators (Phase 4E-3)."""

from __future__ import annotations

import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.binomial_domain_functions import binomial_expansion_coefficients
from core.vocational_math_b4.domain.counting_domain_functions import combination

PROBLEM_TYPE_ID = "binomial_expansion_basic"
GENERATOR_KEY = "b4.binomial.binomial_expansion_basic"
COEFFICIENT_SUM_PROBLEM_TYPE_ID = "binomial_coefficient_sum"
COEFFICIENT_SUM_GENERATOR_KEY = "b4.binomial.binomial_coefficient_sum"
SPECIFIC_TERM_PROBLEM_TYPE_ID = "binomial_specific_term_coefficient"
SPECIFIC_TERM_GENERATOR_KEY = "b4.binomial.binomial_specific_term_coefficient"
EQUATION_SOLVE_N_PROBLEM_TYPE_ID = "binomial_equation_solve_n"
EQUATION_SOLVE_N_GENERATOR_KEY = "b4.binomial.binomial_equation_solve_n"


def _make_numeric_choices(answer: int, rng: random.Random) -> list[int]:
    offsets = [1, -1, 2, -2, 3, -3, 5, -5]
    choices = [answer]
    for offset in offsets:
        candidate = answer + offset
        if candidate >= 0 and candidate not in choices:
            choices.append(candidate)
        if len(choices) == 4:
            break
    while len(choices) < 4:
        candidate = max(0, abs(answer) + rng.randint(4, 20))
        if candidate not in choices:
            choices.append(candidate)
    rng.shuffle(choices)
    return choices


def _validate_and_finalize(payload: dict, multiple_choice: bool) -> None:
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])


def _format_binomial(a: int, b: int) -> str:
    x_part = "x" if a == 1 else f"{a}x"
    sign = "+" if b > 0 else "-"
    return f"({x_part}{sign}{abs(b)})"


def _sample_coefficient_sum_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int]:
    if difficulty <= 1:
        return 1, rng.randint(1, 4), rng.randint(2, 5)
    if difficulty == 2:
        return rng.randint(1, 3), rng.randint(1, 5), rng.randint(3, 6)

    while True:
        a = rng.randint(1, 4)
        b = rng.choice([v for v in range(-5, 6) if v != 0])
        if a + b != 0:
            return a, b, rng.randint(4, 7)


def _sample_specific_term_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int, int]:
    if difficulty <= 1:
        a = 1
        b = rng.randint(1, 4)
        n = rng.randint(2, 5)
    elif difficulty == 2:
        a = rng.randint(1, 3)
        b = rng.randint(1, 5)
        n = rng.randint(3, 6)
    else:
        a = rng.randint(1, 4)
        b = rng.choice([v for v in range(-5, 6) if v != 0])
        n = rng.randint(4, 7)
    return a, b, n, rng.randint(0, n)


def _sample_equation_solve_n_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int, str]:
    if difficulty <= 1:
        variant = rng.choice(["r1", "r2"])
        if variant == "r1":
            n = rng.randint(3, 12)
            r = 1
        else:
            n = rng.randint(4, 10)
            r = 2
    elif difficulty == 2:
        variant = rng.choice(["r1", "r2"])
        if variant == "r1":
            n = rng.randint(8, 20)
            r = 1
        else:
            n = rng.randint(6, 15)
            r = 2
    else:
        variant = "r2"
        n = rng.randint(10, 25)
        r = 2
    m = combination(n, r)
    return n, r, m, variant


def _ensure_seen_set(seen_parameter_tuples: set[tuple] | None) -> set[tuple]:
    if seen_parameter_tuples is None:
        return set()
    if not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")
    return seen_parameter_tuples


def _sample_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int]:
    if difficulty <= 1:
        a = 1
        b = rng.randint(1, 4)
        n = rng.randint(2, 4)
    elif difficulty == 2:
        a = rng.randint(1, 3)
        b = rng.randint(1, 5)
        n = rng.randint(3, 5)
    else:
        a = rng.randint(1, 4)
        b = rng.choice([v for v in range(-5, 6) if v != 0])
        n = rng.randint(4, 6)
    return a, b, n


def generate(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic binomial expansion coefficient problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 12):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = 0
    for _ in range(50):
        a, b, n = _sample_parameters(rng, difficulty)
        candidate = (PROBLEM_TYPE_ID, a, b, n)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = binomial_expansion_coefficients(a, b, n)
    if a == 1:
        poly_text = f"(x{b:+d})".replace("+", "+").replace("-","-")
    else:
        poly_text = f"({a}x{b:+d})".replace("+", "+").replace("-","-")
    question_text = f"展開 ${poly_text}^{{{n}}}$，請寫出由高次到低次的係數。"
    explanation = (
        f"由二項式定理，${poly_text}^{{{n}}}$ 的第 $k$ 項係數為 "
        r"$\binom{n}{k}a^{n-k}b^{k}$，"
        r"係數依序對應 $x^n$ 到 $x^0$。"
    )

    payload = {
        "question_text": question_text,
        "choices": [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": PROBLEM_TYPE_ID,
        "generator_key": GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["binomial_expansion_basic", "binomial_theorem", "coefficient"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_binomial_expand_basic_01", "binomial_expansion_basic"],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "parameter_tuple": parameter_tuple,
        },
        "supports_multiple_choice": False,
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if payload["choices"]:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])

    seen.add(parameter_tuple)
    return payload


def binomial_expansion_basic(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Alias for runtime consistency with generator naming."""
    return generate(
        skill_id=skill_id,
        subskill_id=subskill_id,
        difficulty=difficulty,
        seed=seed,
        seen_parameter_tuples=seen_parameter_tuples,
        multiple_choice=multiple_choice,
    )


def binomial_coefficient_sum(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate coefficient-sum problems for binomial expansions."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = 0

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        a, b, n = [(1, 1, 2), (1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 2, 5)][seed - 1]
        candidate = (COEFFICIENT_SUM_PROBLEM_TYPE_ID, a, b, n)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        a, b, n = _sample_coefficient_sum_parameters(rng, difficulty)
        candidate = (COEFFICIENT_SUM_PROBLEM_TYPE_ID, a, b, n)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = sum(binomial_expansion_coefficients(a, b, n))
    poly = _format_binomial(a, b)
    substitution = f"({a}+{b})" if b > 0 else f"({a}-{abs(b)})"
    question_text = f"展開 ${poly}^{{{n}}}$ 後，所有係數和為多少？"
    explanation = (
        f"係數和可令 $x=1$，所以 ${poly}^{{{n}}}$ 的係數和為 "
        f"${substitution}^{{{n}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": COEFFICIENT_SUM_PROBLEM_TYPE_ID,
        "generator_key": COEFFICIENT_SUM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "binomial_coefficient_sum",
            "binomial_theorem",
            "coefficient_sum",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_binomial_coefficient_sum_01", "binomial_coefficient_sum"],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def binomial_specific_term_coefficient(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate specific-term coefficient problems for binomial expansions."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = k = 0

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        a, b, n, k = [(1, 1, 2, 1), (1, 2, 3, 2), (1, 3, 4, 0), (1, 4, 5, 3), (1, 2, 5, 5)][seed - 1]
        candidate = (SPECIFIC_TERM_PROBLEM_TYPE_ID, a, b, n, k)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        a, b, n, k = _sample_specific_term_parameters(rng, difficulty)
        candidate = (SPECIFIC_TERM_PROBLEM_TYPE_ID, a, b, n, k)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    coefficients = binomial_expansion_coefficients(a, b, n)
    answer = coefficients[n - k]
    poly = _format_binomial(a, b)
    if k == 0:
        target_text = "常數項"
    else:
        target_text = f"$x^{{{k}}}$ 項"
    question_text = f"展開 ${poly}^{{{n}}}$ 後，{target_text}係數為多少？"
    explanation = (
        f"展開係數依 $x^{{{n}}}$ 到 $x^{{0}}$ 排列，"
        f"{target_text}係數為 ${answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": SPECIFIC_TERM_PROBLEM_TYPE_ID,
        "generator_key": SPECIFIC_TERM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "binomial_specific_term_coefficient",
            "binomial_theorem",
            "specific_coefficient",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_specific_term_coefficient_01",
            "binomial_specific_term_coefficient",
        ],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "k": k,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def binomial_equation_solve_n(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate simple binomial-coefficient equations asking for n."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = r = m = 0
    variant = ""

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        n, r, variant = [(3, 1, "r1"), (4, 2, "r2"), (8, 1, "r1"), (7, 2, "r2"), (12, 1, "r1")][seed - 1]
        m = combination(n, r)
        candidate = (EQUATION_SOLVE_N_PROBLEM_TYPE_ID, n, r, m, variant)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        n, r, m, variant = _sample_equation_solve_n_parameters(rng, difficulty)
        candidate = (EQUATION_SOLVE_N_PROBLEM_TYPE_ID, n, r, m, variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = n
    question_text = f"若 $C^{{n}}_{{{r}}}={m}$，求正整數 $n$。"
    if variant == "r1":
        explanation = f"因為 $C^{{n}}_{{1}}=n$，所以 $n={answer}$。"
    else:
        explanation = (
            f"因為 $C^{{n}}_{{2}}=\\frac{{n(n-1)}}{{2}}$，"
            f"檢查可得 $C^{{{n}}}_{{2}}={m}$，所以 $n={answer}$。"
        )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EQUATION_SOLVE_N_PROBLEM_TYPE_ID,
        "generator_key": EQUATION_SOLVE_N_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["binomial_equation_solve_n", "combination", "solve_n"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_binomial_equation_solve_n_01", "binomial_equation_solve_n"],
        "parameters": {
            "n": n,
            "r": r,
            "m": m,
            "variant": variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload

