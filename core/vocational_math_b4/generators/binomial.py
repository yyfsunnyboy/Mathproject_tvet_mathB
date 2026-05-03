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

PROBLEM_TYPE_ID = "binomial_expansion_basic"
GENERATOR_KEY = "b4.binomial.binomial_expansion_basic"


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

