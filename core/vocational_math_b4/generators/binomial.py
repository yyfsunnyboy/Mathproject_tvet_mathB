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
MIDDLE_TERM_PROBLEM_TYPE_ID = "binomial_middle_term_coefficient"
MIDDLE_TERM_GENERATOR_KEY = "b4.binomial.binomial_middle_term_coefficient"
ODD_EVEN_SUM_PROBLEM_TYPE_ID = "binomial_odd_even_coefficient_sum"
ODD_EVEN_SUM_GENERATOR_KEY = "b4.binomial.binomial_odd_even_coefficient_sum"
HOCKEY_STICK_SUM_PROBLEM_TYPE_ID = "combination_hockey_stick_sum"
HOCKEY_STICK_SUM_GENERATOR_KEY = "b4.binomial.combination_hockey_stick_sum"
SPECIFIC_NEGATIVE_TERM_PROBLEM_TYPE_ID = "binomial_specific_coefficient_with_negative_term"
SPECIFIC_NEGATIVE_TERM_GENERATOR_KEY = "b4.binomial.binomial_specific_coefficient_with_negative_term"
TWO_VAR_SPECIFIC_PROBLEM_TYPE_ID = "binomial_two_variable_specific_coefficient"
TWO_VAR_SPECIFIC_GENERATOR_KEY = "b4.binomial.binomial_two_variable_specific_coefficient"
LAURENT_SPECIFIC_PROBLEM_TYPE_ID = "binomial_laurent_specific_power_coefficient"
LAURENT_SPECIFIC_GENERATOR_KEY = "b4.binomial.binomial_laurent_specific_power_coefficient"

_MAX_BINOMIAL_SPECIFIC_ANSWER = 500_000


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


def _explain_specific_term_coefficient(a: int, b: int, n: int, k: int, answer: int, poly: str) -> str:
    r_sel = n - k
    lead = "常數項即 $x^{0}$ 項。" if k == 0 else ""
    return (
        lead
        + f"將 ${poly}^{{{n}}}$ 視為 $(ax+b)^n$（此處 $a={a}$，$b={b}$）。"
        f"一般項的第 $r+1$ 項為 $\\binom{{n}}{{r}}(ax)^{{n-r}}b^{{r}}$。"
        f"欲求 $x^{{{k}}}$ 需 $n-r={k}$，故 $r={r_sel}$。"
        f"係數為 $\\binom{{{n}}}{{{r_sel}}}({a})^{{{k}}}({b})^{{{r_sel}}}={answer}$。"
    )


def _explain_negative_specific_term(a: int, b: int, n: int, k: int, answer: int, poly: str, target_text: str) -> str:
    r_sel = n - k
    return (
        f"將 ${poly}^{{{n}}}$ 視為 $(ax+b)^n$，其中 $b={b}<0$，符號須保留。"
        f"{target_text} 對應一般項取 $r={r_sel}$（第 ${r_sel + 1}$ 項），"
        f"係數為 $\\binom{{{n}}}{{{r_sel}}}({a})^{{{k}}}({b})^{{{r_sel}}}={answer}$。"
    )


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
        a = rng.choice([1, 2])
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


def _sample_middle_term_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int]:
    if difficulty <= 1:
        a = rng.choice([1, 2])
        b_pool = list(range(-4, 0)) + list(range(1, 5))
        return a, rng.choice(b_pool), rng.choice([2, 4, 6])
    if difficulty == 2:
        return rng.randint(1, 3), rng.randint(1, 5), rng.choice([4, 6, 8])
    return rng.randint(1, 4), rng.choice([v for v in range(-5, 6) if v != 0]), rng.choice([6, 8, 10])


def _sample_odd_even_sum_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int, str]:
    if difficulty <= 1:
        return 1, rng.randint(1, 4), rng.randint(2, 5), rng.choice(["odd", "even"])
    if difficulty == 2:
        return rng.randint(1, 3), rng.randint(1, 5), rng.randint(3, 6), rng.choice(["odd", "even"])
    return (
        rng.randint(1, 4),
        rng.choice([v for v in range(-5, 6) if v != 0]),
        rng.randint(4, 7),
        rng.choice(["odd", "even"]),
    )


def _sample_specific_negative_term_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, int, int]:
    if difficulty <= 1:
        a = rng.choice([1, 2])
        b, n = rng.randint(-4, -1), rng.randint(2, 5)
    elif difficulty == 2:
        a, b, n = rng.randint(1, 3), rng.randint(-5, -1), rng.randint(3, 6)
    else:
        a, b, n = rng.randint(1, 4), rng.randint(-8, -1), rng.randint(4, 7)
    return a, b, n, rng.randint(0, n)


def _sample_hockey_stick_parameters(rng: random.Random, difficulty: int) -> tuple[int, int]:
    if difficulty <= 1:
        r = rng.randint(0, 2)
        n = rng.randint(r + 2, r + 5)
    elif difficulty == 2:
        r = rng.randint(1, 4)
        n = rng.randint(r + 3, r + 7)
    else:
        r = rng.randint(2, 5)
        n = rng.randint(r + 4, r + 8)
    return r, n


def format_combination_latex(n: int, r: int, *, wrap_in_dollars: bool = False) -> str:
    """Format combination in textbook LaTeX style: C^{n}_{r} (optionally wrapped)."""
    core = rf"C^{{{n}}}_{{{r}}}"
    return f"${core}$" if wrap_in_dollars else core


def _summation_terms_latex(terms: list[str]) -> str:
    if len(terms) <= 6:
        return "+".join(terms)
    return "+".join([terms[0], terms[1], terms[2], r"\cdots", terms[-1]])


def _build_hockey_stick_standard_terms_latex(r: int, n: int) -> str:
    terms = [format_combination_latex(k, r) for k in range(r, n + 1)]
    return _summation_terms_latex(terms)


def _build_hockey_stick_shifted_terms_latex(r: int, n: int) -> str:
    """Shifted / staggered presentation via symmetry: C^{m}_{m-r} (= C^{m}_{r})."""
    terms = [format_combination_latex(m, m - r) for m in range(r, n + 1)]
    return _summation_terms_latex(terms)


def _build_hockey_stick_identity_latex(r: int, n: int) -> str:
    left = (
        rf"{format_combination_latex(r, r)}+{format_combination_latex(r+1, r)}+\cdots+{format_combination_latex(n, r)}"
    )
    right = format_combination_latex(n + 1, r + 1)
    return rf"{left}={right}"


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
    n = 0

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        n = [3, 4, 5, 6, 7][seed - 1]
        candidate = (COEFFICIENT_SUM_PROBLEM_TYPE_ID, n)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        if difficulty <= 1:
            n = rng.randint(4, 7)
        elif difficulty == 2:
            n = rng.randint(6, 10)
        else:
            n = rng.randint(9, 14)
        candidate = (COEFFICIENT_SUM_PROBLEM_TYPE_ID, n)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = 2 ** n
    
    terms_latex = "+".join([rf"C^{{{n}}}_{{{k}}}" for k in range(n + 1)])
    if terms_latex.count("+") > 4:
        terms_latex = rf"C^{{{n}}}_{{0}}+C^{{{n}}}_{{1}}+C^{{{n}}}_{{2}}+\cdots+C^{{{n}}}_{{{n}}}"
    identity_latex = rf"C^{{{n}}}_{{0}}+C^{{{n}}}_{{1}}+C^{{{n}}}_{{2}}+\cdots+C^{{{n}}}_{{{n}}}=2^{{{n}}}"

    question_text = f"求下列組合數和的值：\n${terms_latex}$"
    explanation = (
        f"根據二項式係數和性質：\n"
        f"${identity_latex}$。\n"
        f"因此值為 ${answer}$。"
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
            "combination_identity",
            "coefficient_sum",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_binomial_coefficient_sum_01", "binomial_coefficient_sum"],
        "parameters": {
            "n": n,
            "parity": "all",
            "terms_latex": terms_latex,
            "identity_latex": identity_latex,
            "answer": answer,
            "template_context": "pure_combination_sum",
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
        a, b, n, k = [
            (2, 1, 3, 2),
            (1, 2, 3, 2),
            (1, 3, 4, 0),
            (3, 1, 4, 2),
            (2, 3, 5, 4),
        ][seed - 1]
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
        target_text = "常數項（指定次方為 $x^{0}$）"
    else:
        target_text = f"$x^{{{k}}}$ 項（指定次方係數）"
    question_text = f"展開 ${poly}^{{{n}}}$ 後，求 {target_text}的係數。"
    explanation = _explain_specific_term_coefficient(a, b, n, k, answer, poly)

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
    if variant == "r1" or r == 1:
        explanation = (
            f"因為 $C^{{n}}_{{1}}=n$，且題目給 $C^{{n}}_{{1}}={m}$，"
            f"所以 $n={answer}$。"
        )
    else:
        explanation = (
            f"因為 $C^{{n}}_{{2}}=\\frac{{n(n-1)}}{{2}}$，"
            f"題目給 $C^{{n}}_{{2}}={m}$。"
            f"檢查 $C^{{{answer}}}_{{2}}={m}$，所以 $n={answer}$。"
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


def combination_hockey_stick_sum(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic hockey-stick identity sum problems (int answer)."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    r = n = 0
    variants = ("standard_hockey_stick", "shifted_textbook")
    if seed is not None:
        variant = variants[seed % 2]
    else:
        variant = rng.choice(variants)
    template_context = "direct_sum"

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1 and variant == "standard_hockey_stick":
        presets = [(0, 4), (1, 5), (2, 6), (1, 6), (2, 7)]
        r, n = presets[seed - 1]
        candidate = (HOCKEY_STICK_SUM_PROBLEM_TYPE_ID, variant, r, n)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(80):
        if parameter_tuple is not None:
            break
        r, n = _sample_hockey_stick_parameters(rng, difficulty)
        if variant == "shifted_textbook" and r < 2:
            # Keep shifted variant aligned with common textbook examples (avoid trivial r=0/1 cases).
            continue
        answer_try = combination(n + 1, r + 1)
        if answer_try > 500_000:
            continue
        candidate = (HOCKEY_STICK_SUM_PROBLEM_TYPE_ID, variant, r, n)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 80 retries.")

    term_count = n - r + 1
    if variant == "standard_hockey_stick":
        terms_latex = _build_hockey_stick_standard_terms_latex(r, n)
        normalized_terms_latex = terms_latex
    else:
        terms_latex = _build_hockey_stick_shifted_terms_latex(r, n)
        normalized_terms_latex = _build_hockey_stick_standard_terms_latex(r, n)

    identity_latex = _build_hockey_stick_identity_latex(r, n)
    answer = combination(n + 1, r + 1)
    question_text = "利用組合數恆等式，求下列和：" + rf"${terms_latex}$。"
    if variant == "standard_hockey_stick":
        explanation = (
            "根據 hockey-stick identity："
            + rf"${identity_latex}$。"
            + rf"因此答案為 ${format_combination_latex(n+1, r+1)}={answer}$。"
        )
    else:
        explanation = (
            rf"利用 $C^{{m}}_{{m-r}}=C^{{m}}_{{r}}$，可將各項改寫為同一下標 $r$ 的和："
            + rf"${normalized_terms_latex}$。"
            + "再由 hockey-stick identity 得："
            + rf"${identity_latex}$。"
            + rf"因此答案為 ${format_combination_latex(n+1, r+1)}={answer}$。"
        )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": HOCKEY_STICK_SUM_PROBLEM_TYPE_ID,
        "generator_key": HOCKEY_STICK_SUM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_hockey_stick_sum",
            "combination_identity",
            "binomial_coefficient",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_combination_hockey_stick_sum_01",
            "combination_hockey_stick_sum",
        ],
        "parameters": {
            "variant": variant,
            "r": r,
            "n": n,
            "term_count": term_count,
            "terms_latex": terms_latex,
            "normalized_terms_latex": normalized_terms_latex,
            "identity_latex": identity_latex,
            "answer": answer,
            "template_context": template_context,
            "formula_components": {
                "left_start_k": r,
                "left_end_k": n,
                "right_n": n + 1,
                "right_r": r + 1,
            },
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def binomial_middle_term_coefficient(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = 0

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        a, b, n = [(2, 1, 4), (1, -2, 4), (3, 2, 6), (2, -1, 6), (1, 3, 8)][seed - 1]
        candidate = (MIDDLE_TERM_PROBLEM_TYPE_ID, a, b, n)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        a, b, n = _sample_middle_term_parameters(rng, difficulty)
        candidate = (MIDDLE_TERM_PROBLEM_TYPE_ID, a, b, n)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    coefficients = binomial_expansion_coefficients(a, b, n)
    middle_power = n // 2
    answer = coefficients[n - middle_power]
    poly = _format_binomial(a, b)
    term_number = n - middle_power + 1
    question_text = (
        f"展開 ${poly}^{{{n}}}$ 後，求中間項係數（$n$ 為偶數時唯一的中間項，對應 $x^{{{middle_power}}}$）。"
    )
    explanation = (
        f"$n={n}$ 為偶數，展開式恰有一個中間項：對應 $x^{{{middle_power}}}$，"
        f"若將 $(ax)^{{n}}$ 視為第 $1$ 項並依降幂往下數，該項為第 ${term_number}$ 項。"
        f"係數為 ${answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": MIDDLE_TERM_PROBLEM_TYPE_ID,
        "generator_key": MIDDLE_TERM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["binomial_middle_term_coefficient", "binomial_theorem", "middle_term"],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_middle_term_coefficient_01",
            "binomial_middle_term_coefficient",
        ],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "middle_power": middle_power,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def binomial_odd_even_coefficient_sum(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = 0
    target_parity = "odd"

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        n, target_parity = [
            (3, "odd"),
            (4, "even"),
            (5, "odd"),
            (6, "even"),
            (7, "odd"),
        ][seed - 1]
        candidate = (ODD_EVEN_SUM_PROBLEM_TYPE_ID, n, target_parity)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        if difficulty <= 1:
            n = rng.randint(4, 7)
        elif difficulty == 2:
            n = rng.randint(6, 10)
        else:
            n = rng.randint(9, 14)
        target_parity = rng.choice(["odd", "even"])
        candidate = (ODD_EVEN_SUM_PROBLEM_TYPE_ID, n, target_parity)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = 2 ** (n - 1)
    
    if target_parity == "even":
        terms_latex = "+".join([rf"C^{{{n}}}_{{{k}}}" for k in range(0, n + 1, 2)])
        if terms_latex.count("+") > 3:
            terms_latex = rf"C^{{{n}}}_{{0}}+C^{{{n}}}_{{2}}+C^{{{n}}}_{{4}}+\cdots"
        identity_latex = rf"C^{{{n}}}_{{0}}+C^{{{n}}}_{{2}}+C^{{{n}}}_{{4}}+\cdots=2^{{{n}-1}}"
        template_context = "even_combination_sum"
    else:
        terms_latex = "+".join([rf"C^{{{n}}}_{{{k}}}" for k in range(1, n + 1, 2)])
        if terms_latex.count("+") > 3:
            terms_latex = rf"C^{{{n}}}_{{1}}+C^{{{n}}}_{{3}}+C^{{{n}}}_{{5}}+\cdots"
        identity_latex = rf"C^{{{n}}}_{{1}}+C^{{{n}}}_{{3}}+C^{{{n}}}_{{5}}+\cdots=2^{{{n}-1}}"
        template_context = "odd_combination_sum"

    question_text = f"求下列組合數和的值：\n${terms_latex}$"
    explanation = (
        f"根據組合數奇偶項和性質：\n"
        f"${identity_latex}$。\n"
        f"因此值為 $2^{{{n}-1}} = {answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": ODD_EVEN_SUM_PROBLEM_TYPE_ID,
        "generator_key": ODD_EVEN_SUM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["binomial_odd_even_coefficient_sum", "combination_identity", "odd_even_terms"],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_odd_even_coefficient_sum_01",
            "binomial_odd_even_coefficient_sum",
        ],
        "parameters": {
            "n": n,
            "parity": target_parity,
            "terms_latex": terms_latex,
            "identity_latex": identity_latex,
            "answer": answer,
            "template_context": template_context,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def binomial_specific_coefficient_with_negative_term(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = k = 0

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        a, b, n, k = [
            (2, -1, 4, 2),
            (1, -2, 3, 2),
            (1, -3, 4, 0),
            (3, -2, 5, 3),
            (2, -2, 5, 5),
        ][seed - 1]
        candidate = (SPECIFIC_NEGATIVE_TERM_PROBLEM_TYPE_ID, a, b, n, k)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        a, b, n, k = _sample_specific_negative_term_parameters(rng, difficulty)
        candidate = (SPECIFIC_NEGATIVE_TERM_PROBLEM_TYPE_ID, a, b, n, k)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    coefficients = binomial_expansion_coefficients(a, b, n)
    answer = coefficients[n - k]
    poly = _format_binomial(a, b)
    target_text = "常數項（$x^{0}$）" if k == 0 else f"$x^{{{k}}}$ 項"
    question_text = f"展開 ${poly}^{{{n}}}$ 後，求 {target_text}係數（式中含負常數項）。"
    explanation = _explain_negative_specific_term(a, b, n, k, answer, poly, target_text)

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": SPECIFIC_NEGATIVE_TERM_PROBLEM_TYPE_ID,
        "generator_key": SPECIFIC_NEGATIVE_TERM_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "binomial_specific_coefficient_with_negative_term",
            "binomial_theorem",
            "negative_term",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_specific_coefficient_with_negative_term_01",
            "binomial_specific_coefficient_with_negative_term",
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


def _format_two_variable_binomial_latex(a: int, b: int, *, y_plus: bool) -> str:
    x_part = "x" if a == 1 else f"{a}x"
    if y_plus:
        if b == 1:
            y_part = "+y"
        else:
            y_part = f"+{b}y"
    else:
        if b == 1:
            y_part = "-y"
        else:
            y_part = f"-{b}y"
    return f"({x_part}{y_part})"


def _two_variable_term_coefficient(a: int, b: int, n: int, q: int, *, y_plus: bool) -> int:
    p = n - q
    signed_b = b if y_plus else -b
    return combination(n, q) * (a**p) * (signed_b**q)


def _sample_two_variable_parameters(
    rng: random.Random, difficulty: int
) -> tuple[int, int, int, int, bool]:
    if difficulty <= 1:
        n = rng.randint(3, 5)
        a = rng.randint(1, 3)
        b = rng.randint(1, 3)
        y_plus = rng.choice([True, True, False])
    elif difficulty == 2:
        n = rng.randint(3, 7)
        a = rng.randint(1, 4)
        b = rng.randint(1, 5)
        y_plus = rng.choice([True, False])
    else:
        n = rng.randint(4, 7)
        a = rng.randint(2, 5)
        b = rng.randint(1, 5)
        y_plus = rng.choice([True, False])
    q = rng.randint(0, n)
    return a, b, n, q, y_plus


def _explain_two_variable_coefficient(
    a: int,
    b: int,
    n: int,
    p: int,
    q: int,
    *,
    y_plus: bool,
    answer: int,
    poly: str,
) -> str:
    signed_latex = f"{b}" if y_plus else f"(-{b})"
    return (
        f"將 ${poly}^{{{n}}}$ 視為 $(ax\\pm by)^n$ 的形式（此處 $a={a}$，$y$ 的係數可寫成 $\\pm {b}$）。"
        f"指定 $x^{{{p}}}y^{{{q}}}$（$p+q=n$）對應一般項 $\\binom{{{n}}}{{{q}}}(ax)^{{{p}}}(\\pm by)^{{{q}}}$，"
        f"係數為 $\\binom{{{n}}}{{{q}}}\\cdot {a}^{{{p}}}\\cdot ({signed_latex})^{{{q}}}={answer}$。"
    )


def binomial_two_variable_specific_coefficient(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Coefficient of x^p y^q in (ax ± by)^n with p+q=n (int answer)."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = q = 0
    y_plus = True

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        presets = [
            (2, 3, 4, 2, True),
            (2, 3, 4, 2, False),
            (1, 2, 5, 2, False),
            (3, 1, 5, 1, True),
            (2, 1, 3, 1, True),
        ]
        a, b, n, q, y_plus = presets[seed - 1]
        candidate = (TWO_VAR_SPECIFIC_PROBLEM_TYPE_ID, a, b, n, q, y_plus)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(80):
        if parameter_tuple is not None:
            break
        a, b, n, q, y_plus = _sample_two_variable_parameters(rng, difficulty)
        ans_try = _two_variable_term_coefficient(a, b, n, q, y_plus=y_plus)
        if abs(ans_try) > _MAX_BINOMIAL_SPECIFIC_ANSWER:
            continue
        candidate = (TWO_VAR_SPECIFIC_PROBLEM_TYPE_ID, a, b, n, q, y_plus)
        if candidate not in seen:
            parameter_tuple = candidate
            break

    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 80 retries.")

    p = n - q
    answer = _two_variable_term_coefficient(a, b, n, q, y_plus=y_plus)
    poly = _format_two_variable_binomial_latex(a, b, y_plus=y_plus)
    question_text = (
        f"在 ${poly}^{{{n}}}$ 的展開式中，求 $x^{{{p}}}y^{{{q}}}$ 項的係數（只需係數，不必寫出完整展開式）。"
    )
    explanation = _explain_two_variable_coefficient(
        a, b, n, p, q, y_plus=y_plus, answer=answer, poly=poly
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": TWO_VAR_SPECIFIC_PROBLEM_TYPE_ID,
        "generator_key": TWO_VAR_SPECIFIC_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "binomial_two_variable_specific_coefficient",
            "binomial_theorem",
            "specific_coefficient",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_two_variable_specific_coefficient_01",
            "binomial_two_variable_specific_coefficient",
        ],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "p": p,
            "q": q,
            "y_plus": y_plus,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _format_laurent_binomial_latex(a: int, b: int, *, term_plus: bool) -> str:
    x_part = "x" if a == 1 else f"{a}x"
    frac = f"\\frac{{{b}}}{{x}}"
    if term_plus:
        inner = f"{x_part}+{frac}"
    else:
        inner = f"{x_part}-{frac}"
    return f"\\left({inner}\\right)"


def _laurent_power_term_coefficient(a: int, b: int, n: int, r: int, *, term_plus: bool) -> int:
    signed_b = b if term_plus else -b
    return combination(n, r) * (a ** (n - r)) * (signed_b**r)


def _sample_laurent_parameters(
    rng: random.Random, difficulty: int
) -> tuple[int, int, int, int, bool]:
    if difficulty <= 1:
        n = rng.randint(4, 6)
        a = rng.randint(1, 2)
        b = rng.randint(1, 3)
        term_plus = rng.choice([True, True, False])
    elif difficulty == 2:
        n = rng.randint(4, 7)
        a = rng.randint(1, 3)
        b = rng.randint(1, 4)
        term_plus = rng.choice([True, False])
    else:
        n = rng.randint(5, 8)
        a = rng.randint(1, 4)
        b = rng.randint(1, 4)
        term_plus = rng.choice([True, False])
    r = rng.randint(0, n)
    return a, b, n, r, term_plus


def _explain_laurent_coefficient(
    a: int,
    b: int,
    n: int,
    r: int,
    k: int,
    *,
    term_plus: bool,
    answer: int,
    poly: str,
) -> str:
    signed_note = f"{b}" if term_plus else f"(-{b})"
    return (
        f"將 ${poly}^{{{n}}}$ 的一般項寫成 $\\binom{{{n}}}{{{r}}}(ax)^{{{n-r}}}\\left(\\frac{{\\pm b}}{{x}}\\right)^{{{r}}}$。"
        f"$x$ 的次方為 $(n-r)-r=n-2r$，令 $n-2r={k}$ 得 $r={r}$。"
        f"係數為 $\\binom{{{n}}}{{{r}}}\\cdot {a}^{{{n-r}}}\\cdot ({signed_note})^{{{r}}}={answer}$。"
    )


def binomial_laurent_specific_power_coefficient(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Coefficient of x^k in (ax ± b/x)^n with k=n-2r (int answer)."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = n = r = 0
    term_plus = True

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        presets = [
            (1, 3, 6, 1, True),
            (1, 2, 6, 2, True),
            (2, 1, 4, 2, True),
            (1, 1, 5, 2, False),
            (2, 2, 5, 1, True),
        ]
        a, b, n, r, term_plus = presets[seed - 1]
        candidate = (LAURENT_SPECIFIC_PROBLEM_TYPE_ID, a, b, n, r, term_plus)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(80):
        if parameter_tuple is not None:
            break
        a, b, n, r, term_plus = _sample_laurent_parameters(rng, difficulty)
        ans_try = _laurent_power_term_coefficient(a, b, n, r, term_plus=term_plus)
        if abs(ans_try) > _MAX_BINOMIAL_SPECIFIC_ANSWER:
            continue
        candidate = (LAURENT_SPECIFIC_PROBLEM_TYPE_ID, a, b, n, r, term_plus)
        if candidate not in seen:
            parameter_tuple = candidate
            break

    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 80 retries.")

    k = n - 2 * r
    answer = _laurent_power_term_coefficient(a, b, n, r, term_plus=term_plus)
    poly = _format_laurent_binomial_latex(a, b, term_plus=term_plus)
    question_text = (
        f"在 ${poly}^{{{n}}}$ 的展開式中，求 $x^{{{k}}}$ 項的係數（只需係數，不必寫出完整展開式）。"
    )
    explanation = _explain_laurent_coefficient(
        a, b, n, r, k, term_plus=term_plus, answer=answer, poly=poly
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": LAURENT_SPECIFIC_PROBLEM_TYPE_ID,
        "generator_key": LAURENT_SPECIFIC_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "binomial_laurent_specific_power_coefficient",
            "binomial_theorem",
            "specific_coefficient",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_binomial_laurent_specific_power_coefficient_01",
            "binomial_laurent_specific_power_coefficient",
        ],
        "parameters": {
            "a": a,
            "b": b,
            "n": n,
            "r": r,
            "k": k,
            "term_plus": term_plus,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload

