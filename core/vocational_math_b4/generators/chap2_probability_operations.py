"""Deterministic B4 Chapter 2 probability-operations generators – Phase 6K.

Skill:
  vh_數學B4_ProbabilityOperations  (2-2 機率的運算)

Problem types implemented:
  1. event_operation_probability   (事件運算機率：差集/補集/德摩根，採 set algebra 角度)
  2. probability_algebra_mixed     (代數混合：補事件、聯集/交集代數推導)

Both intentionally distinct from union_intersection_probability
(which already covers ask_union / ask_intersection direct substitution).

Excluded:
  - Three-event inclusion-exclusion
  - Venn diagram visual
  - Long word problems
  - Listing/handwriting problem types
"""

from __future__ import annotations

import math
import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID = "event_operation_probability"
EVENT_OPERATION_PROBABILITY_GENERATOR_KEY = "b4.chap2.event_operation_probability"

PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID = "probability_algebra_mixed"
PROBABILITY_ALGEBRA_MIXED_GENERATOR_KEY = "b4.chap2.probability_algebra_mixed"


def _fraction_str(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    g = math.gcd(abs(numerator), denominator)
    n, d = numerator // g, denominator // g
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _make_fraction_choices(num: int, den: int, rng: random.Random) -> list[str]:
    """Generate 4 unique fraction-string choices including the correct answer."""
    correct = _fraction_str(num, den)
    candidates: list[str] = [correct]
    for delta in [1, -1, 2, -2, 3, -3]:
        dn = num + delta
        if 0 <= dn <= den and dn != num:
            s = _fraction_str(dn, den)
            if s not in candidates:
                candidates.append(s)
            if len(candidates) >= 4:
                break

    attempts = 0
    while len(candidates) < 4 and attempts < 80:
        alt_den = rng.randint(2, max(3, den + 4))
        alt_num = rng.randint(1, max(1, alt_den - 1))
        s = _fraction_str(alt_num, alt_den)
        if s not in candidates:
            candidates.append(s)
        attempts += 1

    if len(candidates) < 4:
        for s in ("1/2", "1/3", "2/3", "3/4", "1/4", "5/6"):
            if s not in candidates:
                candidates.append(s)
            if len(candidates) >= 4:
                break

    rng.shuffle(candidates)
    return candidates


def _sample_event_pair_params(
    rng: random.Random, difficulty: int
) -> tuple[int, int, int, int]:
    """Sample valid (D, a, b, c) such that 0<c<=min(a,b), a+b-c<=D, a,b<D.

    Used as the canonical (D, P(A)=a/D, P(B)=b/D, P(A∩B)=c/D) tuple.
    Returns (0,0,0,0) on failure.
    """
    if difficulty <= 1:
        denoms = [4, 5, 6, 8, 10]
    elif difficulty == 2:
        denoms = [6, 8, 10, 12, 15]
    else:
        denoms = [10, 12, 15, 20]

    for _ in range(200):
        D = rng.choice(denoms)
        a = rng.randint(1, D - 1)
        b = rng.randint(1, D - 1)
        if a + b > D:
            continue
        c_max = min(a, b)
        if c_max < 1:
            continue
        c = rng.randint(1, c_max)
        if a + b - c <= 0 or a + b - c > D:
            continue
        if a == b == c:
            continue
        return D, a, b, c
    return 0, 0, 0, 0


def event_operation_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate event-set algebra probability problems.

    Variants (Phase 6K):
      - ask_only_a:        find P(A∩B') = P(A) - P(A∩B)
      - ask_only_b:        find P(A'∩B) = P(B) - P(A∩B)
      - ask_neither:       find P(A'∩B') = 1 - P(A∪B)
                                       = 1 - (P(A)+P(B)-P(A∩B))
      - ask_either_only:   find P(A∩B') + P(A'∩B)
                                       = P(A) + P(B) - 2 P(A∩B)
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    sub_types = ["ask_only_a", "ask_only_b", "ask_neither", "ask_either_only"]
    if seed is not None:
        sub_type = sub_types[abs(int(seed)) % len(sub_types)]
    else:
        sub_type = rng.choice(sub_types)

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    num = den = 0

    rotate = list(range(len(sub_types)))
    start = sub_types.index(sub_type)
    rotated = rotate[start:] + rotate[:start]

    for _ in range(120):
        for offset in rotated:
            sub_type_try = sub_types[offset]
            D, a, b, c = _sample_event_pair_params(rng, difficulty)
            if D == 0:
                continue
            pa_str = _fraction_str(a, D)
            pb_str = _fraction_str(b, D)
            pab_str = _fraction_str(c, D)

            if sub_type_try == "ask_only_a":
                ans_n = a - c
                ans_d = D
                if ans_n <= 0:
                    continue
                ans_str = _fraction_str(ans_n, ans_d)
                candidate = (
                    EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
                    "ask_only_a",
                    D,
                    a,
                    b,
                    c,
                )
                if candidate in seen:
                    continue
                question_text = (
                    f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cap B)={pab_str}$，"
                    "求 $P(A\\cap B')$（即只屬於 $A$ 而不屬於 $B$ 的機率）。"
                )
                explanation = (
                    "由 $A=(A\\cap B)\\cup(A\\cap B')$ 且兩者互斥：\n"
                    "$P(A\\cap B')=P(A)-P(A\\cap B)$。\n"
                    f"代入得 $P(A\\cap B')={pa_str}-{pab_str}"
                    f"=\\dfrac{{{a}}}{{{D}}}-\\dfrac{{{c}}}{{{D}}}"
                    f"=\\dfrac{{{ans_n}}}{{{D}}}={ans_str}$。"
                )
                num, den = ans_n, ans_d
                parameter_tuple = candidate
                break

            if sub_type_try == "ask_only_b":
                ans_n = b - c
                ans_d = D
                if ans_n <= 0:
                    continue
                ans_str = _fraction_str(ans_n, ans_d)
                candidate = (
                    EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
                    "ask_only_b",
                    D,
                    a,
                    b,
                    c,
                )
                if candidate in seen:
                    continue
                question_text = (
                    f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cap B)={pab_str}$，"
                    "求 $P(A'\\cap B)$（即只屬於 $B$ 而不屬於 $A$ 的機率）。"
                )
                explanation = (
                    "由 $B=(A\\cap B)\\cup(A'\\cap B)$ 且兩者互斥：\n"
                    "$P(A'\\cap B)=P(B)-P(A\\cap B)$。\n"
                    f"代入得 $P(A'\\cap B)={pb_str}-{pab_str}"
                    f"=\\dfrac{{{b}}}{{{D}}}-\\dfrac{{{c}}}{{{D}}}"
                    f"=\\dfrac{{{ans_n}}}{{{D}}}={ans_str}$。"
                )
                num, den = ans_n, ans_d
                parameter_tuple = candidate
                break

            if sub_type_try == "ask_neither":
                paub = a + b - c
                ans_n = D - paub
                ans_d = D
                if ans_n <= 0 or paub <= 0:
                    continue
                paub_str = _fraction_str(paub, D)
                ans_str = _fraction_str(ans_n, ans_d)
                candidate = (
                    EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
                    "ask_neither",
                    D,
                    a,
                    b,
                    c,
                )
                if candidate in seen:
                    continue
                question_text = (
                    f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cap B)={pab_str}$，"
                    "求 $P(A'\\cap B')$（即兩個事件皆不發生的機率）。"
                )
                explanation = (
                    "由 De Morgan 定律：$A'\\cap B'=(A\\cup B)'$，故\n"
                    "$P(A'\\cap B')=1-P(A\\cup B)=1-[P(A)+P(B)-P(A\\cap B)]$。\n"
                    f"先求 $P(A\\cup B)={pa_str}+{pb_str}-{pab_str}={paub_str}$，"
                    f"再得 $P(A'\\cap B')=1-{paub_str}={ans_str}$。"
                )
                num, den = ans_n, ans_d
                parameter_tuple = candidate
                break

            # ask_either_only
            ans_n = a + b - 2 * c
            ans_d = D
            if ans_n <= 0:
                continue
            ans_str = _fraction_str(ans_n, ans_d)
            candidate = (
                EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
                "ask_either_only",
                D,
                a,
                b,
                c,
            )
            if candidate in seen:
                continue
            question_text = (
                f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cap B)={pab_str}$，"
                "求恰好只發生 $A$ 或只發生 $B$ 的機率，即 $P(A\\cap B')+P(A'\\cap B)$。"
            )
            explanation = (
                "$P(A\\cap B')+P(A'\\cap B)$\n"
                "$=[P(A)-P(A\\cap B)]+[P(B)-P(A\\cap B)]$\n"
                "$=P(A)+P(B)-2P(A\\cap B)$。\n"
                f"代入得 ${pa_str}+{pb_str}-2\\times {pab_str}"
                f"=\\dfrac{{{a + b - 2 * c}}}{{{D}}}={ans_str}$。"
            )
            num, den = ans_n, ans_d
            parameter_tuple = candidate
            break

        if parameter_tuple is not None:
            break

    if parameter_tuple is None:
        raise ValueError(
            "event_operation_probability: failed to generate after retries."
        )

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EVENT_OPERATION_PROBABILITY_PROBLEM_TYPE_ID,
        "generator_key": EVENT_OPERATION_PROBABILITY_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "probability_operations",
            "event_operation_probability",
            "set_algebra",
            "de_morgan",
        ],
        "remediation_candidates": [
            "complement_probability",
            "union_intersection_probability",
            "classical_probability_fraction",
        ],
        "source_style_refs": [
            "tc_b4_ch2_event_operation_probability_01",
            "event_operation_probability",
        ],
        "parameters": {
            "parameter_tuple": parameter_tuple,
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


def probability_algebra_mixed(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate algebra-mixed probability problems involving complements.

    Variants (Phase 6K):
      - ask_pa_from_complement:        given P(A')=x, find P(A)=1-x
      - ask_paub_with_pa_complement:   given P(A')=x, P(B)=y, P(A∩B)=z,
                                       find P(A∪B) (must derive P(A) first)
      - ask_paub_complement:           given P(A∪B)=u, find P((A∪B)')=1-u
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    sub_types = [
        "ask_pa_from_complement",
        "ask_paub_with_pa_complement",
        "ask_paub_complement",
    ]
    if seed is not None:
        sub_type = sub_types[abs(int(seed)) % len(sub_types)]
    else:
        sub_type = rng.choice(sub_types)

    rotate = list(range(len(sub_types)))
    start = sub_types.index(sub_type)
    rotated = rotate[start:] + rotate[:start]

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    num = den = 0

    for _ in range(120):
        for offset in rotated:
            sub_type_try = sub_types[offset]

            if sub_type_try == "ask_pa_from_complement":
                if difficulty <= 1:
                    denoms = [4, 5, 6, 8, 10]
                elif difficulty == 2:
                    denoms = [5, 6, 8, 10, 12]
                else:
                    denoms = [8, 10, 12, 15]
                D = rng.choice(denoms)
                comp_a = rng.randint(1, D - 1)
                a = D - comp_a
                if a <= 0 or a == D:
                    continue
                candidate = (
                    PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID,
                    "ask_pa_from_complement",
                    D,
                    a,
                )
                if candidate in seen:
                    continue
                pa_prime_str = _fraction_str(comp_a, D)
                pa_str = _fraction_str(a, D)
                question_text = (
                    f"已知 $P(A')={pa_prime_str}$，其中 $A'$ 為 $A$ 的補事件。"
                    "求 $P(A)$。"
                )
                explanation = (
                    "由補事件公式：$P(A)=1-P(A')$。\n"
                    f"代入得 $P(A)=1-{pa_prime_str}"
                    f"=\\dfrac{{{D}}}{{{D}}}-\\dfrac{{{comp_a}}}{{{D}}}"
                    f"=\\dfrac{{{a}}}{{{D}}}={pa_str}$。"
                )
                num, den = a, D
                parameter_tuple = candidate
                break

            if sub_type_try == "ask_paub_with_pa_complement":
                D, a, b, c = _sample_event_pair_params(rng, difficulty)
                if D == 0:
                    continue
                paub = a + b - c
                if paub <= 0 or paub > D or paub == a + b:
                    continue
                comp_a = D - a
                if comp_a <= 0:
                    continue
                candidate = (
                    PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID,
                    "ask_paub_with_pa_complement",
                    D,
                    a,
                    b,
                    c,
                )
                if candidate in seen:
                    continue
                pa_prime_str = _fraction_str(comp_a, D)
                pa_str = _fraction_str(a, D)
                pb_str = _fraction_str(b, D)
                pab_str = _fraction_str(c, D)
                paub_str = _fraction_str(paub, D)
                question_text = (
                    f"已知 $P(A')={pa_prime_str}$、$P(B)={pb_str}$、"
                    f"$P(A\\cap B)={pab_str}$，求 $P(A\\cup B)$。"
                )
                explanation = (
                    f"先由補事件求 $P(A)=1-P(A')=1-{pa_prime_str}={pa_str}$。\n"
                    "再由加法定理：\n"
                    "$P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$。\n"
                    f"代入得 $P(A\\cup B)={pa_str}+{pb_str}-{pab_str}"
                    f"=\\dfrac{{{paub}}}{{{D}}}={paub_str}$。"
                )
                num, den = paub, D
                parameter_tuple = candidate
                break

            # ask_paub_complement
            if difficulty <= 1:
                denoms = [4, 5, 6, 8, 10]
            elif difficulty == 2:
                denoms = [5, 6, 8, 10, 12]
            else:
                denoms = [8, 10, 12, 15]
            D = rng.choice(denoms)
            paub = rng.randint(2, D - 1)
            comp = D - paub
            if comp <= 0 or paub == comp:
                continue
            candidate = (
                PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID,
                "ask_paub_complement",
                D,
                paub,
            )
            if candidate in seen:
                continue
            paub_str = _fraction_str(paub, D)
            comp_str = _fraction_str(comp, D)
            question_text = (
                f"已知 $P(A\\cup B)={paub_str}$，求 $P((A\\cup B)')$"
                "（$A\\cup B$ 不發生的機率）。"
            )
            explanation = (
                "由補事件公式：\n"
                "$P((A\\cup B)')=1-P(A\\cup B)$。\n"
                f"代入得 $P((A\\cup B)')=1-{paub_str}"
                f"=\\dfrac{{{D}}}{{{D}}}-\\dfrac{{{paub}}}{{{D}}}"
                f"=\\dfrac{{{comp}}}{{{D}}}={comp_str}$。"
            )
            num, den = comp, D
            parameter_tuple = candidate
            break

        if parameter_tuple is not None:
            break

    if parameter_tuple is None:
        raise ValueError(
            "probability_algebra_mixed: failed to generate after retries."
        )

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": PROBABILITY_ALGEBRA_MIXED_PROBLEM_TYPE_ID,
        "generator_key": PROBABILITY_ALGEBRA_MIXED_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "probability_operations",
            "probability_algebra_mixed",
            "complement_probability",
            "addition_theorem",
        ],
        "remediation_candidates": [
            "complement_probability",
            "union_intersection_probability",
            "classical_probability_fraction",
        ],
        "source_style_refs": [
            "tc_b4_ch2_probability_algebra_mixed_01",
            "probability_algebra_mixed",
        ],
        "parameters": {
            "parameter_tuple": parameter_tuple,
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
