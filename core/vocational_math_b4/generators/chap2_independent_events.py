"""Deterministic B4 Chapter 2 independent-events generators – Phase 6E.

Problem types implemented:
  8. independent_joint_probability
  9. independent_at_least_one_probability
"""

from __future__ import annotations

import math
import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

INDEPENDENT_JOINT_PROBLEM_TYPE_ID = "independent_joint_probability"
INDEPENDENT_JOINT_GENERATOR_KEY = "b4.chap2.independent_joint_probability"

INDEPENDENT_AT_LEAST_ONE_PROBLEM_TYPE_ID = "independent_at_least_one_probability"
INDEPENDENT_AT_LEAST_ONE_GENERATOR_KEY = "b4.chap2.independent_at_least_one_probability"


def _fraction_str(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    g = math.gcd(abs(numerator), denominator)
    n, d = numerator // g, denominator // g
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _make_fraction_choices(num: int, den: int, rng: random.Random) -> list[str]:
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

    if len(candidates) < 4:
        for alt_den in [max(2, den - 1), den + 1, den + 2, den + 3]:
            for alt_num in range(1, max(2, alt_den)):
                s = _fraction_str(alt_num, alt_den)
                if s not in candidates:
                    candidates.append(s)
                if len(candidates) >= 4:
                    break
            if len(candidates) >= 4:
                break

    attempts = 0
    while len(candidates) < 4 and attempts < 100:
        alt_den = rng.randint(2, max(3, den + 4))
        alt_num = rng.randint(1, max(1, alt_den - 1))
        s = _fraction_str(alt_num, alt_den)
        if s not in candidates:
            candidates.append(s)
        attempts += 1

    if len(candidates) < 4:
        for s in ("1/2", "1/3", "2/3", "3/4", "1/4"):
            if s not in candidates:
                candidates.append(s)
            if len(candidates) >= 4:
                break

    rng.shuffle(candidates)
    return candidates


def independent_joint_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate direct substitution problems using P(A∩B)=P(A)×P(B)."""
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    pa_pool = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (2, 5), (3, 5)]
    pb_pool = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (2, 5), (4, 5)]

    question_text = explanation = ""
    ans_num = ans_den = 0
    parameter_tuple: tuple | None = None

    for _ in range(100):
        pa_n, pa_d = rng.choice(pa_pool)
        pb_n, pb_d = rng.choice(pb_pool)
        inter_n, inter_d = pa_n * pb_n, pa_d * pb_d
        inter_str = _fraction_str(inter_n, inter_d)
        pa_str = _fraction_str(pa_n, pa_d)
        pb_str = _fraction_str(pb_n, pb_d)

        ask_type = rng.choice(["ask_intersection", "ask_pb", "ask_pa"])
        if ask_type == "ask_intersection":
            answer_str = inter_str
            question_text = (
                f"已知事件 $A$ 與 $B$ 為獨立事件，且 $P(A)={pa_str}$、$P(B)={pb_str}$，"
                "求 $P(A\\cap B)$。"
            )
            explanation = (
                "因為 $A,B$ 為獨立事件，\n"
                "$P(A\\cap B)=P(A)\\times P(B)$。\n"
                f"代入得 $P(A\\cap B)={pa_str}\\times{pb_str}={inter_str}$。"
            )
        elif ask_type == "ask_pb":
            answer_str = pb_str
            question_text = (
                f"已知事件 $A$ 與 $B$ 為獨立事件，$P(A\\cap B)={inter_str}$、$P(A)={pa_str}$，"
                "求 $P(B)$。"
            )
            explanation = (
                "因為 $A,B$ 為獨立事件，$P(A\\cap B)=P(A)\\times P(B)$。\n"
                f"所以 $P(B)=\\dfrac{{P(A\\cap B)}}{{P(A)}}=\\dfrac{{{inter_str}}}{{{pa_str}}}={pb_str}$。"
            )
        else:
            answer_str = pa_str
            question_text = (
                f"已知事件 $A$ 與 $B$ 為獨立事件，$P(A\\cap B)={inter_str}$、$P(B)={pb_str}$，"
                "求 $P(A)$。"
            )
            explanation = (
                "因為 $A,B$ 為獨立事件，$P(A\\cap B)=P(A)\\times P(B)$。\n"
                f"所以 $P(A)=\\dfrac{{P(A\\cap B)}}{{P(B)}}=\\dfrac{{{inter_str}}}{{{pb_str}}}={pa_str}$。"
            )

        if "/" in answer_str:
            ans_num, ans_den = map(int, answer_str.split("/", 1))
        else:
            ans_num, ans_den = int(answer_str), 1

        candidate = (INDEPENDENT_JOINT_PROBLEM_TYPE_ID, ask_type, pa_n, pa_d, pb_n, pb_d)
        if candidate in seen:
            continue
        parameter_tuple = candidate
        break

    if parameter_tuple is None:
        raise ValueError("independent_joint_probability: failed to generate after 100 retries.")

    answer = _fraction_str(ans_num, ans_den)
    choices = _make_fraction_choices(ans_num, ans_den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": INDEPENDENT_JOINT_PROBLEM_TYPE_ID,
        "generator_key": INDEPENDENT_JOINT_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "independent_events",
            "independent_joint_probability",
            "probability_multiplication_rule",
        ],
        "remediation_candidates": [
            "conditional_probability_basic",
            "classical_probability_fraction",
            "union_intersection_probability",
        ],
        "source_style_refs": [
            "tc_b4_ch2_independent_joint_01",
            "independent_joint_probability",
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


def independent_at_least_one_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate at-least-one-success problems using 1-(1-p)^n."""
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    p_pool = [(1, 2), (1, 3), (1, 4), (2, 5), (3, 5)]
    n_pool = [2, 3, 4, 5] if difficulty >= 2 else [2, 3, 4]
    contexts = ["abstract", "target_hit", "inspection_pass"]

    question_text = explanation = ""
    ans_num = ans_den = 0
    parameter_tuple: tuple | None = None

    for _ in range(100):
        p_n, p_d = rng.choice(p_pool)
        n = rng.choice(n_pool)
        ctx = rng.choice(contexts)
        p_str = _fraction_str(p_n, p_d)

        fail_n, fail_d = p_d - p_n, p_d
        fail_all_n = fail_n ** n
        fail_all_d = fail_d ** n
        at_least_one_n = fail_all_d - fail_all_n
        at_least_one_d = fail_all_d
        answer_str = _fraction_str(at_least_one_n, at_least_one_d)

        candidate = (INDEPENDENT_AT_LEAST_ONE_PROBLEM_TYPE_ID, ctx, p_n, p_d, n)
        if candidate in seen:
            continue

        if ctx == "abstract":
            question_text = (
                f"某事件每次成功機率為 $p={p_str}$，且每次試驗互相獨立。"
                f"連續試驗 ${n}$ 次，至少成功一次的機率為何？"
            )
        elif ctx == "target_hit":
            question_text = (
                f"射手每次命中率為 {p_str}，且每次射擊互相獨立。"
                f"連續射擊 ${n}$ 次，至少命中一次的機率為何？"
            )
        else:
            question_text = (
                f"某零件單次檢查通過率為 {p_str}，各次檢查彼此獨立。"
                f"連續檢查 ${n}$ 次，至少一次通過的機率為何？"
            )

        explanation = (
            "由補事件：\n"
            "$P(\\text{至少一次成功})=1-P(\\text{全部失敗})=1-(1-p)^n$。\n"
            f"代入 $p={p_str}, n={n}$："
            f"$P=1-(1-{p_str})^{n}=1-\\left(\\dfrac{{{fail_n}}}{{{fail_d}}}\\right)^{{{n}}}"
            f"=1-\\dfrac{{{fail_all_n}}}{{{fail_all_d}}}={answer_str}$。"
        )

        if "/" in answer_str:
            ans_num, ans_den = map(int, answer_str.split("/", 1))
        else:
            ans_num, ans_den = int(answer_str), 1
        parameter_tuple = candidate
        break

    if parameter_tuple is None:
        raise ValueError("independent_at_least_one_probability: failed to generate after 100 retries.")

    answer = _fraction_str(ans_num, ans_den)
    choices = _make_fraction_choices(ans_num, ans_den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": INDEPENDENT_AT_LEAST_ONE_PROBLEM_TYPE_ID,
        "generator_key": INDEPENDENT_AT_LEAST_ONE_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "independent_events",
            "independent_at_least_one_probability",
            "complement_rule",
        ],
        "remediation_candidates": [
            "independent_joint_probability",
            "complement_probability",
            "classical_probability_fraction",
        ],
        "source_style_refs": [
            "tc_b4_ch2_independent_at_least_one_01",
            "independent_at_least_one_probability",
        ],
        "parameters": {
            "parameter_tuple": parameter_tuple,
            "n": n,
            "p_n": p_n,
            "p_d": p_d,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
