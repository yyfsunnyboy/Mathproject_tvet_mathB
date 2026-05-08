"""Deterministic B4 Chapter 2 probability generators – Phase 6C-1 & 6C-2.

Problem types implemented:
  Phase 6C-1:
    1. classical_probability_fraction  (vh_數學B4_ProbabilityDefinition)
    2. complement_probability           (vh_數學B4_ProbabilityProperties)
    3. sample_space_count_numeric       (vh_數學B4_SampleSpaceAndEvents)
  Phase 6C-2:
    4. union_intersection_probability   (vh_數學B4_ProbabilityProperties)
    5. dice_coin_probability_count      (vh_數學B4_ProbabilityDefinition)

Deliberately excluded (not_ready / handwriting):
  - sample_space_listing
  - event_set_listing
  - subset_listing

Answer format:
  - rational types → fraction string "a/b" (reduced to lowest terms)
  - sample_space_count → integer
"""

from __future__ import annotations

import math
import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

# ─── constants ──────────────────────────────────────────────────────────────

CLASSICAL_PROBLEM_TYPE_ID = "classical_probability_fraction"
CLASSICAL_GENERATOR_KEY = "b4.chap2.classical_probability_fraction"

COMPLEMENT_PROBLEM_TYPE_ID = "complement_probability"
COMPLEMENT_GENERATOR_KEY = "b4.chap2.complement_probability"

SAMPLE_SPACE_COUNT_PROBLEM_TYPE_ID = "sample_space_count_numeric"
SAMPLE_SPACE_COUNT_GENERATOR_KEY = "b4.chap2.sample_space_count_numeric"


# ─── shared helpers ─────────────────────────────────────────────────────────

def _fraction_str(numerator: int, denominator: int) -> str:
    """Return reduced fraction as 'a/b', or '0' / '1' for degenerate cases."""
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    g = math.gcd(abs(numerator), denominator)
    n, d = numerator // g, denominator // g
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _make_fraction_choices(
    num: int, den: int, rng: random.Random
) -> list[str]:
    """Generate 4 unique fraction-string choices including the correct answer."""
    correct = _fraction_str(num, den)
    candidates: list[str] = [correct]

    # Generate distractor numerators
    distractor_nums = set()
    for delta in [1, -1, 2, -2, 3]:
        dn = num + delta
        if 0 <= dn <= den and dn != num:
            distractor_nums.add(dn)
    for dn in sorted(distractor_nums):
        if len(candidates) >= 4:
            break
        s = _fraction_str(dn, den)
        if s not in candidates:
            candidates.append(s)

    # Fallback distractors with different denominators
    while len(candidates) < 4:
        alt_num = rng.randint(0, den)
        s = _fraction_str(alt_num, den)
        if s not in candidates:
            candidates.append(s)

    rng.shuffle(candidates)
    return candidates


def _make_integer_choices(answer: int, rng: random.Random) -> list[int]:
    """Generate 4 unique integer choices including the correct answer."""
    pool = {answer}
    for delta in [answer * 2, answer // 2, answer - 1, answer + 1, answer * 4, answer * 6]:
        if delta > 0 and delta != answer:
            pool.add(delta)
    choices = [answer] + [x for x in pool if x != answer]
    choices = choices[:4]
    while len(choices) < 4:
        extra = answer + rng.randint(2, answer + 5)
        if extra not in choices:
            choices.append(extra)
    rng.shuffle(choices)
    return choices


# ─── classical_probability_fraction ─────────────────────────────────────────

_CLASSICAL_SCENARIOS = [
    # (scenario_key, template_fn(n_total, n_event, rng) -> (question_text, explanation))
    "colored_balls",
    "integer_range",
    "card_draw",
]


def _classical_colored_balls(n_total: int, n_event: int, rng: random.Random) -> tuple[str, str]:
    colors = ["紅球", "藍球", "綠球", "黃球", "白球"]
    event_color = rng.choice(colors[:3])
    other_total = n_total - n_event
    question = (
        f"袋中裝有 ${n_event}$ 顆{event_color}及 ${other_total}$ 顆其他顏色球，"
        f"共 ${n_total}$ 顆。隨機取 $1$ 顆，取到{event_color}的機率為？"
    )
    prob = _fraction_str(n_event, n_total)
    explanation = (
        f"樣本空間共有 $n(S)={n_total}$ 種等可能結果，"
        f"取到{event_color}有 $n(A)={n_event}$ 種，"
        f"故 $P(A)=\\dfrac{{n(A)}}{{n(S)}}=\\dfrac{{{n_event}}}{{{n_total}}}={prob}$。"
    )
    return question, explanation


def _classical_integer_range(n_total: int, n_event: int, rng: random.Random) -> tuple[str, str]:
    # Pick n_event numbers from 1..n_total satisfying some condition
    conditions = ["奇數", "偶數", "3的倍數"]
    # Just use divisibility by k where k divides n_event count
    # Simplify: just state "從1到n_total選1個整數，有n_event個符合條件"
    condition = rng.choice(["奇數", "偶數"])
    if condition == "奇數":
        actual_event = (n_total + 1) // 2
    else:
        actual_event = n_total // 2
    # Remap n_event to actual_event to keep math consistent
    n_event_use = actual_event
    prob = _fraction_str(n_event_use, n_total)
    question = (
        f"從 $1$ 到 ${n_total}$ 中隨機選取一個整數，選到{condition}的機率為？"
    )
    explanation = (
        f"$1$ 到 ${n_total}$ 共 ${n_total}$ 個整數，"
        f"其中{condition}有 ${n_event_use}$ 個，"
        f"故 $P=\\dfrac{{{n_event_use}}}{{{n_total}}}={prob}$。"
    )
    return question, explanation, n_event_use  # type: ignore[return-value]


def _classical_card_draw(n_total: int, n_event: int, rng: random.Random) -> tuple[str, str]:
    question = (
        f"共有 ${n_total}$ 張號碼牌（編號 $1$ 至 ${n_total}$），隨機抽 $1$ 張，"
        f"抽到號碼為 ${n_event}$ 的倍數之機率為？"
    )
    # count multiples of n_event in 1..n_total
    count = n_total // n_event
    prob = _fraction_str(count, n_total)
    explanation = (
        f"$1$ 到 ${n_total}$ 中 ${n_event}$ 的倍數共有 $\\lfloor {n_total}/{n_event}\\rfloor={count}$ 個，"
        f"故 $P=\\dfrac{{{count}}}{{{n_total}}}={prob}$。"
    )
    return question, explanation, count  # type: ignore[return-value]


def classical_probability_fraction(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a classical probability problem; answer is a reduced fraction string."""
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    # Parameter sampling
    if difficulty <= 1:
        total_pool = list(range(4, 11))
    elif difficulty == 2:
        total_pool = list(range(8, 21))
    else:
        total_pool = list(range(15, 31))

    scenario = rng.choice(_CLASSICAL_SCENARIOS)
    parameter_tuple: tuple | None = None
    n_total = n_event = 0
    question_text = explanation = ""
    num = den = 0

    for _ in range(50):
        if scenario == "colored_balls":
            n_total = rng.choice(total_pool)
            n_event = rng.randint(1, n_total - 1)
            candidate = (CLASSICAL_PROBLEM_TYPE_ID, "colored_balls", n_total, n_event)
            if candidate in seen:
                continue
            question_text, explanation = _classical_colored_balls(n_total, n_event, rng)
            num, den = n_event, n_total
            parameter_tuple = candidate
            break

        elif scenario == "integer_range":
            n_total = rng.choice([t for t in total_pool if t >= 4])
            candidate = (CLASSICAL_PROBLEM_TYPE_ID, "integer_range", n_total)
            if candidate in seen:
                scenario = "colored_balls"
                continue
            result = _classical_integer_range(n_total, 0, rng)
            question_text, explanation, n_event = result[0], result[1], result[2]
            num, den = n_event, n_total
            parameter_tuple = candidate
            break

        elif scenario == "card_draw":
            n_total = rng.choice([t for t in total_pool if t >= 6])
            # pick a divisor k such that k < n_total and k >= 2
            divisors = [k for k in range(2, n_total) if n_total % k == 0 or k <= 5]
            if not divisors:
                scenario = "colored_balls"
                continue
            k = rng.choice(divisors[:6])
            candidate = (CLASSICAL_PROBLEM_TYPE_ID, "card_draw", n_total, k)
            if candidate in seen:
                continue
            result = _classical_card_draw(n_total, k, rng)
            question_text, explanation, count = result[0], result[1], result[2]
            num, den = count, n_total
            parameter_tuple = candidate
            break

    if parameter_tuple is None:
        raise ValueError("classical_probability_fraction: failed to find a new parameter tuple after 50 retries.")

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": CLASSICAL_PROBLEM_TYPE_ID,
        "generator_key": CLASSICAL_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "classical_probability_fraction",
            "classical_probability",
            "sample_space",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_b4_ch2_classical_probability_01",
            "classical_probability_fraction",
        ],
        "parameters": {
            "scenario": scenario,
            "n_total": den,
            "n_event": num,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


# ─── complement_probability ──────────────────────────────────────────────────

_COMPLEMENT_SCENARIOS = ["direct_given_pa", "colored_balls_complement"]


def complement_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a complement-probability problem: P(A') = 1 - P(A).

    Scope: direct complement only. Does NOT handle multi-step independent events
    or union/intersection (those are future problem_types).
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    if difficulty <= 1:
        total_pool = list(range(4, 11))
    elif difficulty == 2:
        total_pool = list(range(8, 21))
    else:
        total_pool = list(range(15, 31))

    scenario = rng.choice(_COMPLEMENT_SCENARIOS)
    parameter_tuple: tuple | None = None
    n_total = n_event = 0
    question_text = explanation = ""
    num = den = 0  # numerator/denominator of P(A')

    for _ in range(50):
        if scenario == "direct_given_pa":
            # Give P(A) = a/b, ask for P(A')
            b = rng.choice(total_pool)
            a = rng.randint(1, b - 1)
            candidate = (COMPLEMENT_PROBLEM_TYPE_ID, "direct_given_pa", a, b)
            if candidate in seen:
                scenario = rng.choice(_COMPLEMENT_SCENARIOS)
                continue
            pa_str = _fraction_str(a, b)
            comp_num = b - a
            pa_prime_str = _fraction_str(comp_num, b)
            question_text = (
                f"已知事件 $A$ 的機率 $P(A)={pa_str}$，"
                f"求 $P(A')$（$A$ 的補事件）。"
            )
            explanation = (
                f"由補事件公式：$P(A')=1-P(A)=1-{pa_str}="
                f"\\dfrac{{{b}}}{{{b}}}-\\dfrac{{{a}}}{{{b}}}="
                f"\\dfrac{{{comp_num}}}{{{b}}}={pa_prime_str}$。"
            )
            num, den = comp_num, b
            parameter_tuple = candidate
            break

        else:  # colored_balls_complement
            n_total = rng.choice(total_pool)
            n_event = rng.randint(1, n_total - 1)
            candidate = (COMPLEMENT_PROBLEM_TYPE_ID, "colored_balls_complement", n_total, n_event)
            if candidate in seen:
                scenario = rng.choice(_COMPLEMENT_SCENARIOS)
                continue
            pa_str = _fraction_str(n_event, n_total)
            comp_num = n_total - n_event
            pa_prime_str = _fraction_str(comp_num, n_total)
            colors = ["紅球", "藍球", "綠球"]
            event_color = rng.choice(colors)
            other = n_total - n_event
            question_text = (
                f"袋中有 ${n_event}$ 顆{event_color}及 ${other}$ 顆其他顏色球，共 ${n_total}$ 顆。"
                f"隨機取 $1$ 顆，取到**非**{event_color}的機率為？"
            )
            explanation = (
                f"取到{event_color}的機率 $P(A)=\\dfrac{{{n_event}}}{{{n_total}}}={pa_str}$，"
                f"故取到非{event_color}（補事件）：\n"
                f"$P(A')=1-P(A)=1-{pa_str}=\\dfrac{{{comp_num}}}{{{n_total}}}={pa_prime_str}$。"
            )
            num, den = comp_num, n_total
            parameter_tuple = candidate
            break

    if parameter_tuple is None:
        raise ValueError("complement_probability: failed to find a new parameter tuple after 50 retries.")

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": COMPLEMENT_PROBLEM_TYPE_ID,
        "generator_key": COMPLEMENT_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "complement_probability",
            "complement_event",
            "probability_properties",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_b4_ch2_complement_probability_01",
            "complement_probability",
        ],
        "parameters": {
            "scenario": scenario,
            "n_event_numerator": num,
            "n_total_denominator": den,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


# ─── sample_space_count_numeric ───────────────────────────────────────────────

_SAMPLE_SPACE_COUNT_SCENARIOS = [
    "coin_tosses",
    "dice_rolls",
    "sequential_choices",
]


def sample_space_count_numeric(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a sample-space *counting* problem; answer is a non-negative integer.

    Scope: asks for n(S) only (pure count). Does NOT ask students to LIST the
    sample space — that is sample_space_listing (handwriting / not_ready).
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    if difficulty <= 1:
        n_pool = [2, 3]
        sides_pool = [2, 6]
    elif difficulty == 2:
        n_pool = [2, 3, 4]
        sides_pool = [2, 4, 6]
    else:
        n_pool = [3, 4, 5]
        sides_pool = [4, 6, 8]

    if seed is not None:
        start_idx = abs(int(seed)) % len(_SAMPLE_SPACE_COUNT_SCENARIOS)
    else:
        start_idx = rng.randrange(len(_SAMPLE_SPACE_COUNT_SCENARIOS))
    scenario_cycle = (
        _SAMPLE_SPACE_COUNT_SCENARIOS[start_idx:]
        + _SAMPLE_SPACE_COUNT_SCENARIOS[:start_idx]
    )
    scenario = scenario_cycle[0]
    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    answer = 0

    for _ in range(50):
        scenario_found = False
        for scenario in scenario_cycle:
            if scenario == "coin_tosses":
                n = rng.choice(n_pool)
                candidate = (SAMPLE_SPACE_COUNT_PROBLEM_TYPE_ID, "coin_tosses", n)
                if candidate in seen:
                    continue
                answer = 2 ** n
                question_text = (
                    f"公正的硬幣（正面/反面）投擲 ${n}$ 次，樣本空間共有幾個元素？"
                )
                explanation = (
                    f"每次投擲有 $2$ 種結果（正面或反面），連續投擲 ${n}$ 次，"
                    f"依乘法原理：$n(S)=2^{{{n}}}={answer}$。"
                )
                parameter_tuple = candidate
                scenario_found = True
                break

            if scenario == "dice_rolls":
                sides = rng.choice(sides_pool)
                n = rng.choice(n_pool)
                candidate = (SAMPLE_SPACE_COUNT_PROBLEM_TYPE_ID, "dice_rolls", sides, n)
                if candidate in seen:
                    continue
                answer = sides ** n
                if sides == 6 and n == 2:
                    question_text = "同時擲兩顆公正骰子（點數 1 到 6），樣本空間共有幾個元素？"
                    explanation = (
                        "第一顆骰子有 $6$ 種點數結果，第二顆骰子也有 $6$ 種點數結果，"
                        "依乘法原理：$n(S)=6\\times6=36$。"
                    )
                else:
                    die_name = "骰子" if sides == 6 else f"{sides}面骰"
                    question_text = (
                        f"投擲一顆公正的 {die_name} ${n}$ 次，"
                        f"樣本空間共有幾個元素？"
                    )
                    explanation = (
                        f"每次有 ${sides}$ 種點數結果，連續投擲 ${n}$ 次，"
                        f"依乘法原理：$n(S)={sides}^{{{n}}}={answer}$。"
                    )
                parameter_tuple = candidate
                scenario_found = True
                break

            # sequential_choices
            m = rng.randint(2, 5)
            k = rng.randint(2, 4)
            candidate = (SAMPLE_SPACE_COUNT_PROBLEM_TYPE_ID, "sequential_choices", m, k)
            if candidate in seen:
                continue
            answer = m ** k
            question_text = (
                f"某流程分成 ${k}$ 個階段，第一階段到第 ${k}$ 階段各有 ${m}$ 種選擇，"
                "問共有幾種結果？"
            )
            explanation = (
                f"每一階段都有 ${m}$ 種選擇，共 ${k}$ 個階段，"
                f"依乘法原理：$n(S)=m\\times m\\times\\cdots\\times m={m}^{{{k}}}={answer}$。"
            )
            parameter_tuple = candidate
            scenario_found = True
            break

        if scenario_found:
            break

    if parameter_tuple is None:
        raise ValueError("sample_space_count_numeric: failed to find a new parameter tuple after 50 retries.")

    choices = _make_integer_choices(answer, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": SAMPLE_SPACE_COUNT_PROBLEM_TYPE_ID,
        "generator_key": SAMPLE_SPACE_COUNT_GENERATOR_KEY,
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "sample_space_count_numeric",
            "sample_space",
            "multiplication_principle",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_b4_ch2_sample_space_count_01",
            "sample_space_count_numeric",
        ],
        "parameters": {
            "scenario": scenario,
            "answer": answer,
            "parameter_tuple": parameter_tuple,
        },
        "context_type": scenario,
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice and choices:
        from core.vocational_math_b4.domain.b4_validators import (
            validate_answer_in_choices,
            validate_choices_unique,
        )
        validate_choices_unique(choices)
        validate_answer_in_choices(answer, choices)

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


# ─── Phase 6C-2 ─────────────────────────────────────────────────────────────
# union_intersection_probability  (vh_數學B4_ProbabilityProperties)
# dice_coin_probability_count     (vh_數學B4_ProbabilityDefinition)

UNION_INTERSECTION_PROBLEM_TYPE_ID = "union_intersection_probability"
UNION_INTERSECTION_GENERATOR_KEY = "b4.chap2.union_intersection_probability"

DICE_COIN_PROBLEM_TYPE_ID = "dice_coin_probability_count"
DICE_COIN_GENERATOR_KEY = "b4.chap2.dice_coin_probability_count"


# ─── union_intersection_probability ──────────────────────────────────────────

def _sample_valid_union_params(rng: random.Random, difficulty: int) -> tuple[int, int, int, int, int, int]:
    """Sample valid (pa_n,pa_d, pb_n,pb_d, pab_n,pab_d) such that all constraints hold.

    Returns (pa_num, pa_den, pb_num, pb_den, pab_num, pab_den, paub_num, paub_den)
    — but we use a single denominator for simplicity.
    All fractions share denominator D; P(A)=a/D, P(B)=b/D, P(A∩B)=c/D.
    P(A∪B)=(a+b-c)/D; constraints: 0<c<=a, 0<c<=b, a+b-c<=D.
    """
    if difficulty <= 1:
        denoms = [4, 5, 6, 8, 10]
    elif difficulty == 2:
        denoms = [6, 8, 10, 12, 15]
    else:
        denoms = [10, 12, 15, 20]

    for _ in range(200):
        D = rng.choice(denoms)
        # pick a,b in [1,D-1] such that a+b <= D (union can't exceed 1)
        a = rng.randint(1, D - 1)
        b = rng.randint(1, D - 1)
        if a + b > D:
            continue
        # c (intersection) must be ≤ min(a,b) and ≥ 1
        c_max = min(a, b)
        if c_max < 1:
            continue
        c = rng.randint(1, c_max)
        # P(A∪B) = (a+b-c)/D
        paub = a + b - c
        if paub <= 0 or paub > D:
            continue
        # avoid trivial cases where answer equals P(A) or P(B)
        if paub == a or paub == b:
            continue
        return D, a, b, c, paub
    return 0, 0, 0, 0, 0  # fallback sentinel


def union_intersection_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a P(A∪B)=P(A)+P(B)-P(A∩B) problem.

    Two sub-types:
      - ask_union:         given P(A),P(B),P(A∩B), find P(A∪B)
      - ask_intersection:  given P(A∪B),P(A),P(B),  find P(A∩B)

    Scope (Phase 6C-2):
      - Direct substitution only; no conditional prob; no 3-event inclusion-exclusion.
      - No figure/image; no long set-mapping word problems.
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    # Ask type: alternated by seed parity
    sub_types = ["ask_union", "ask_intersection"]
    if seed is not None:
        sub_type = sub_types[abs(int(seed)) % 2]
    else:
        sub_type = rng.choice(sub_types)

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    num = den = 0

    for _ in range(80):
        result = _sample_valid_union_params(rng, difficulty)
        if result[0] == 0:
            continue
        D, a, b, c, paub = result

        pa_str = _fraction_str(a, D)
        pb_str = _fraction_str(b, D)
        pab_str = _fraction_str(c, D)
        paub_str = _fraction_str(paub, D)

        if sub_type == "ask_union":
            candidate = (UNION_INTERSECTION_PROBLEM_TYPE_ID, "ask_union", D, a, b, c)
            if candidate in seen:
                sub_type = "ask_intersection"
                continue
            question_text = (
                f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cap B)={pab_str}$，"
                "求 $P(A\\cup B)$。"
            )
            explanation = (
                "由加法定理：\n"
                f"$P(A\\cup B)=P(A)+P(B)-P(A\\cap B)"
                f"={pa_str}+{pb_str}-{pab_str}"
                f"=\\dfrac{{{a}}}{{{D}}}+\\dfrac{{{b}}}{{{D}}}-\\dfrac{{{c}}}{{{D}}}"
                f"=\\dfrac{{{paub}}}{{{D}}}={paub_str}$。"
            )
            num, den = paub, D
            parameter_tuple = candidate

        else:  # ask_intersection
            candidate = (UNION_INTERSECTION_PROBLEM_TYPE_ID, "ask_intersection", D, a, b, paub)
            if candidate in seen:
                sub_type = "ask_union"
                continue
            question_text = (
                f"已知 $P(A)={pa_str}$、$P(B)={pb_str}$、$P(A\\cup B)={paub_str}$，"
                "求 $P(A\\cap B)$。"
            )
            explanation = (
                "由加法定理 $P(A\\cup B)=P(A)+P(B)-P(A\\cap B)$，整理得：\n"
                f"$P(A\\cap B)=P(A)+P(B)-P(A\\cup B)"
                f"={pa_str}+{pb_str}-{paub_str}"
                f"=\\dfrac{{{a}}}{{{D}}}+\\dfrac{{{b}}}{{{D}}}-\\dfrac{{{paub}}}{{{D}}}"
                f"=\\dfrac{{{c}}}{{{D}}}={pab_str}$。"
            )
            num, den = c, D
            parameter_tuple = candidate

        break

    if parameter_tuple is None:
        raise ValueError("union_intersection_probability: failed to generate after 80 retries.")

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": UNION_INTERSECTION_PROBLEM_TYPE_ID,
        "generator_key": UNION_INTERSECTION_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "union_intersection_probability",
            "addition_theorem",
            "probability_properties",
        ],
        "remediation_candidates": ["complement_probability", "classical_probability_fraction"],
        "source_style_refs": [
            "tc_b4_ch2_union_intersection_01",
            "union_intersection_probability",
        ],
        "parameters": {
            "sub_type": sub_type,
            "D": den,
            "pa_num": a,
            "pb_num": b,
            "pab_num": c,
            "paub_num": paub,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


# ─── dice_coin_probability_count ─────────────────────────────────────────────

def _comb(n: int, k: int) -> int:
    return math.comb(n, k)


# single_die_property: condition builders
def _single_die_event(rng: random.Random) -> tuple[str, int, int]:
    """Return (condition_text, n_event, n_sample=6)."""
    N = 6
    choices_list = [
        ("偶數（$2,4,6$）", 3),
        ("奇數（$1,3,5$）", 3),
        ("大於 $4$（即 $5$ 或 $6$）", 2),
        ("小於 $3$（即 $1$ 或 $2$）", 2),
        ("$3$ 的倍數（$3$ 或 $6$）", 2),
        ("不大於 $2$（即 $1$ 或 $2$）", 2),
        ("$4$ 以上（$4,5,6$）", 3),
        ("$1$ 點", 1),
        ("$6$ 點", 1),
    ]
    cond_text, n_event = rng.choice(choices_list)
    return cond_text, n_event, N


def dice_coin_probability_count(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a dice/coin classical probability problem.

    Three contexts (Phase 6C-2):
      - single_die_property:  one fair die, condition on face value
      - two_dice_sum:         two fair dice, target sum
      - coin_exact_heads:     n coins (n=2..4), exact k heads

    No image, no listing, no conditional prob, no multi-step independent events.
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    contexts = ["single_die_property", "two_dice_sum", "coin_exact_heads"]
    # Rotate context by seed for variety
    if seed is not None:
        start = abs(int(seed)) % len(contexts)
        context_order = contexts[start:] + contexts[:start]
    else:
        context_order = list(contexts)
        rng.shuffle(context_order)

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    num = den = 0
    context_used = ""

    for _ in range(80):
        for ctx in context_order:

            if ctx == "single_die_property":
                cond_text, n_event, N = _single_die_event(rng)
                candidate = (DICE_COIN_PROBLEM_TYPE_ID, "single_die", cond_text)
                if candidate in seen:
                    continue
                num, den = n_event, N
                prob_str = _fraction_str(num, den)
                question_text = (
                    f"擲一顆公正骰子（$1$ 到 $6$ 點）一次，"
                    f"點數為{cond_text}的機率為？"
                )
                explanation = (
                    f"樣本空間 $n(S)=6$；"
                    f"點數為{cond_text}的結果有 $n(A)={n_event}$ 種，\n"
                    f"故 $P(A)=\\dfrac{{n(A)}}{{n(S)}}="
                    f"\\dfrac{{{n_event}}}{{6}}={prob_str}$。"
                )
                parameter_tuple = candidate
                context_used = "single_die_property"
                break

            if ctx == "two_dice_sum":
                # count pairs (d1,d2) with d1+d2 = target
                if difficulty <= 1:
                    targets = [7, 6, 8]
                elif difficulty == 2:
                    targets = [7, 5, 9, 6, 8]
                else:
                    targets = list(range(2, 13))
                target = rng.choice(targets)
                candidate = (DICE_COIN_PROBLEM_TYPE_ID, "two_dice_sum", target)
                if candidate in seen:
                    continue
                count = sum(
                    1 for d1 in range(1, 7) for d2 in range(1, 7)
                    if d1 + d2 == target
                )
                if count == 0:
                    continue
                num, den = count, 36
                prob_str = _fraction_str(num, den)
                question_text = (
                    f"同時擲兩顆公正骰子（各 $1$ 到 $6$ 點），"
                    f"點數和恰好為 ${target}$ 的機率為？"
                )
                explanation = (
                    f"樣本空間共 $n(S)=6\\times6=36$ 種等可能結果；\n"
                    f"點數和為 ${target}$ 的有序對共 $n(A)={count}$ 種，\n"
                    f"故 $P(A)=\\dfrac{{n(A)}}{{n(S)}}="
                    f"\\dfrac{{{count}}}{{36}}={prob_str}$。"
                )
                parameter_tuple = candidate
                context_used = "two_dice_sum"
                break

            # coin_exact_heads
            n = rng.choice([2, 3, 4])
            k = rng.randint(0, n)
            candidate = (DICE_COIN_PROBLEM_TYPE_ID, "coin_exact_heads", n, k)
            if candidate in seen:
                continue
            count = _comb(n, k)
            total = 2 ** n
            num, den = count, total
            prob_str = _fraction_str(num, den)
            heads_str = f"${k}$ 次正面"
            question_text = (
                f"將一枚公正硬幣拋擲 ${n}$ 次，恰好出現 ${k}$ 次正面的機率為？"
            )
            explanation = (
                f"樣本空間共 $n(S)=2^{{{n}}}={total}$ 種等可能結果；\n"
                f"恰好 ${k}$ 次正面的結果數：$n(A)=C_{{{n}}}^{{{k}}}={count}$，\n"
                f"故 $P(A)=\\dfrac{{n(A)}}{{n(S)}}="
                f"\\dfrac{{{count}}}{{{total}}}={prob_str}$。"
            )
            parameter_tuple = candidate
            context_used = "coin_exact_heads"
            break

        if parameter_tuple is not None:
            break

    if parameter_tuple is None:
        raise ValueError("dice_coin_probability_count: failed to generate after 80 retries.")

    answer = _fraction_str(num, den)
    choices = _make_fraction_choices(num, den, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": DICE_COIN_PROBLEM_TYPE_ID,
        "generator_key": DICE_COIN_GENERATOR_KEY,
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "dice_coin_probability_count",
            "classical_probability",
            "sample_space",
        ],
        "remediation_candidates": ["classical_probability_fraction", "sample_space_count_numeric"],
        "source_style_refs": [
            "tc_b4_ch2_dice_coin_01",
            "dice_coin_probability_count",
        ],
        "parameters": {
            "context": context_used,
            "n_event": num,
            "n_sample": den,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
