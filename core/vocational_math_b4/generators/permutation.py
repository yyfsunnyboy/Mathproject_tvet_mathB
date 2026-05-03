"""Deterministic B4 permutation generators (Phase 4B-2)."""

from __future__ import annotations

import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.counting_domain_functions import permutation

PROBLEM_TYPE_ID = "permutation_role_assignment"
GENERATOR_KEY = "b4.permutation.permutation_role_assignment"


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
        n = rng.randint(5, 8)
        r = rng.randint(2, 3)
    elif difficulty == 2:
        n = rng.randint(8, 12)
        r = rng.randint(2, 4)
    else:
        n = rng.randint(10, 15)
        r = rng.randint(3, 5)
    if r > n:
        r = n
    return n, r


def generate(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a deterministic permutation-role-assignment problem payload."""
    if seen_parameter_tuples is not None and not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")

    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    parameter_tuple: tuple | None = None
    n = r = 0
    for _ in range(50):
        n, r = _sample_parameters(rng, difficulty)
        candidate = (PROBLEM_TYPE_ID, n, r)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = permutation(n, r)
    question_text = f"從 {n} 位同學中選出 {r} 位分別擔任不同職務，共有多少種安排方式？"
    explanation = f"職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P({n},{r})={answer}。"

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
        "diagnosis_tags": ["permutation_role_assignment", "permutation", "order_matters"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_role_assignment_03", "permutation_role_assignment"],
        "parameters": {
            "n": n,
            "r": r,
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
