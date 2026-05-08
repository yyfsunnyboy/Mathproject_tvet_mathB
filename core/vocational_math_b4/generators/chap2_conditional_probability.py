"""Deterministic B4 Chapter 2 conditional probability generators – Phase 6D.

Problem types implemented:
  Phase 6D:
    6. conditional_probability_basic         (vh_數學B4_ConditionalProbability)
    7. without_replacement_conditional_probability (vh_數學B4_ConditionalProbability)

Scope constraints (Phase 6D):
  - Direct formula substitution only: P(B|A) = P(A∩B) / P(A)
  - No 3-event, no independence formal proof, no Bayes theorem
  - No image / figure; no long word-problem with complex mapping
  - Handwriting listing types remain excluded

Answer format:
  - Both types → fraction string "a/b" (reduced to lowest terms)
  - answer_type = "rational_fraction"
"""

from __future__ import annotations

import math
import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

# ─── constants ───────────────────────────────────────────────────────────────

CONDITIONAL_BASIC_PROBLEM_TYPE_ID  = "conditional_probability_basic"
CONDITIONAL_BASIC_GENERATOR_KEY    = "b4.chap2.conditional_probability_basic"

WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID = "without_replacement_conditional_probability"
WITHOUT_REPLACEMENT_GENERATOR_KEY   = "b4.chap2.without_replacement_conditional_probability"

# ─── shared helpers (local copies — no cross-file import needed) ─────────────

def _fraction_str(numerator: int, denominator: int) -> str:
    """Return reduced fraction as 'a/b', or '0' / '1' for degenerate cases."""
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
    # Guard against small denominators (e.g. den=2) where only a few unique
    # values exist for a fixed denominator, which can otherwise cause an
    # infinite loop in distractor generation.
    if len(candidates) < 4:
        for alt_den in [max(2, den - 1), den + 1, den + 2, den + 3]:
            upper = max(1, alt_den - 1)
            for alt_num in range(1, upper + 1):
                s = _fraction_str(alt_num, alt_den)
                if s not in candidates:
                    candidates.append(s)
                if len(candidates) >= 4:
                    break
            if len(candidates) >= 4:
                break

    # Final bounded fallback to guarantee termination.
    attempts = 0
    while len(candidates) < 4 and attempts < 100:
        alt_den = rng.randint(2, max(3, den + 4))
        alt_num = rng.randint(1, max(1, alt_den - 1))
        s = _fraction_str(alt_num, alt_den)
        if s not in candidates:
            candidates.append(s)
        attempts += 1

    if len(candidates) < 4:
        # Deterministic emergency fillers (still unique fractions in (0,1]).
        for s in ("1/2", "1/3", "2/3", "3/4", "1/4"):
            if s not in candidates:
                candidates.append(s)
            if len(candidates) >= 4:
                break
    rng.shuffle(candidates)
    return candidates


# ─── conditional_probability_basic ───────────────────────────────────────────

# (label, D_choices, note)
_COND_BASIC_DENOMS_BY_DIFF: dict[int, list[int]] = {
    1: [4, 5, 6, 8, 10],
    2: [6, 8, 10, 12, 15],
    3: [10, 12, 15, 20],
}

# Context flavours: (label, A_event, B_event, A_inter_B_desc)
_COND_BASIC_CONTEXTS = [
    # 0: abstract notation
    "abstract",
    # 1: survey / questionnaire
    "survey",
    # 2: quality inspection
    "quality",
]


def _cond_basic_abstract(pa_str: str, pab_str: str) -> tuple[str, str, str]:
    """Abstract notation flavour."""
    q = (
        f"已知 $P(A)={pa_str}$，$P(A \\cap B)={pab_str}$，"
        "求條件機率 $P(B|A)$。"
    )
    exp_template = (
        "由條件機率公式：\n"
        "$P(B|A)=\\dfrac{{P(A \\cap B)}}{{P(A)}}"
        "=\\dfrac{{{pab}}}{{{{P(A)}}}}"
    )
    return q, None, None  # handled inline in caller


def _cond_basic_survey(
    pa_n: int, pab_n: int, D: int,
    pa_str: str, pab_str: str, ans_str: str,
) -> tuple[str, str]:
    """Survey flavour: students who study math / pass exam."""
    q = (
        f"某班有 ${D}$ 人，其中 ${pa_n}$ 人喜歡數學（事件 $A$），"
        f"${pab_n}$ 人同時喜歡數學且喜歡物理（事件 $A \\cap B$）。"
        "若隨機選出一位喜歡數學的同學，他也喜歡物理的機率為？"
    )
    exp = (
        f"$P(A)=\\dfrac{{{pa_n}}}{{{D}}}={pa_str}$，"
        f"$P(A \\cap B)=\\dfrac{{{pab_n}}}{{{D}}}={pab_str}$。\n"
        "由條件機率公式：\n"
        f"$P(B|A)=\\dfrac{{P(A \\cap B)}}{{P(A)}}"
        f"=\\dfrac{{{pab_str}}}{{{pa_str}}}={ans_str}$。"
    )
    return q, exp


def _cond_basic_quality(
    pa_n: int, pab_n: int, D: int,
    pa_str: str, pab_str: str, ans_str: str,
) -> tuple[str, str]:
    """Quality inspection flavour: defective products."""
    q = (
        f"某批產品共 ${D}$ 件，其中 ${pa_n}$ 件為外觀瑕疵品（事件 $A$），"
        f"${pab_n}$ 件同時具有外觀瑕疵且功能異常（事件 $A \\cap B$）。"
        "從瑕疵品中隨機取 $1$ 件，功能也異常的機率為？"
    )
    exp = (
        f"$P(A)=\\dfrac{{{pa_n}}}{{{D}}}={pa_str}$，"
        f"$P(A \\cap B)=\\dfrac{{{pab_n}}}{{{D}}}={pab_str}$。\n"
        "由條件機率公式：\n"
        f"$P(B|A)=\\dfrac{{P(A \\cap B)}}{{P(A)}}"
        f"=\\dfrac{{{pab_str}}}{{{pa_str}}}={ans_str}$。"
    )
    return q, exp


def conditional_probability_basic(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a P(B|A) = P(A∩B)/P(A) direct substitution problem.

    Given P(A) and P(A∩B), find P(B|A).

    Constraints (Phase 6D):
      - 0 < P(A∩B) < P(A) <= 1
      - P(A) shares denominator D with P(A∩B) for clean arithmetic
      - Three context flavours: abstract / survey / quality
      - No conditional probability chain; no Bayes theorem
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    denoms = _COND_BASIC_DENOMS_BY_DIFF.get(difficulty, _COND_BASIC_DENOMS_BY_DIFF[1])

    # Rotate context by seed
    contexts = _COND_BASIC_CONTEXTS[:]
    if seed is not None:
        start = abs(int(seed)) % len(contexts)
        ctx_order = contexts[start:] + contexts[:start]
    else:
        ctx_order = contexts
        rng.shuffle(ctx_order)

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    ans_num = ans_den = 0

    for _ in range(100):
        D = rng.choice(denoms)
        # pa_n: numerator of P(A), must be in [1, D]
        pa_n = rng.randint(1, D)
        # pab_n: numerator of P(A∩B), must be strictly less than pa_n and >= 1
        if pa_n < 2:
            continue
        pab_n = rng.randint(1, pa_n - 1)

        # Answer = P(B|A) = (pab_n/D) / (pa_n/D) = pab_n/pa_n
        # Use pab_n / pa_n as the answer fraction
        ans_n, ans_d = pab_n, pa_n

        ctx = ctx_order[rng.randint(0, len(ctx_order) - 1)]
        candidate = (CONDITIONAL_BASIC_PROBLEM_TYPE_ID, ctx, D, pa_n, pab_n)
        if candidate in seen:
            continue

        pa_str  = _fraction_str(pa_n,  D)
        pab_str = _fraction_str(pab_n, D)
        ans_str = _fraction_str(ans_n, ans_d)

        if ctx == "abstract":
            question_text = (
                f"已知 $P(A)={pa_str}$，$P(A \\cap B)={pab_str}$，"
                "求條件機率 $P(B|A)$。"
            )
            explanation = (
                "由條件機率公式：\n"
                f"$P(B|A)=\\dfrac{{P(A \\cap B)}}{{P(A)}}"
                f"=\\dfrac{{{pab_str}}}{{{pa_str}}}"
                f"=\\dfrac{{{pab_n}}}{{{pa_n}}}={ans_str}$。"
            )
        elif ctx == "survey":
            question_text, explanation = _cond_basic_survey(
                pa_n, pab_n, D, pa_str, pab_str, ans_str
            )
        else:  # quality
            question_text, explanation = _cond_basic_quality(
                pa_n, pab_n, D, pa_str, pab_str, ans_str
            )

        ans_num, ans_den = ans_n, ans_d
        parameter_tuple = candidate
        break

    if parameter_tuple is None:
        raise ValueError("conditional_probability_basic: failed to generate after 100 retries.")

    answer  = _fraction_str(ans_num, ans_den)
    choices = _make_fraction_choices(ans_num, ans_den, rng) if multiple_choice else []

    payload = {
        "question_text":  question_text,
        "choices":        choices,
        "answer":         answer,
        "explanation":    explanation,
        "skill_id":       skill_id,
        "subskill_id":    subskill_id,
        "problem_type_id": CONDITIONAL_BASIC_PROBLEM_TYPE_ID,
        "generator_key":  CONDITIONAL_BASIC_GENERATOR_KEY,
        "answer_type":    "rational_fraction",
        "difficulty":     difficulty,
        "diagnosis_tags": [
            "conditional_probability",
            "conditional_probability_formula",
            "probability_fraction",
        ],
        "remediation_candidates": [
            "classical_probability_fraction",
            "union_intersection_probability",
            "complement_probability",
        ],
        "source_style_refs": [
            "tc_b4_ch2_conditional_01",
            "conditional_probability_basic",
        ],
        "parameters": {
            "context":   ctx,
            "D":         D,
            "pa_n":      pa_n,
            "pab_n":     pab_n,
            "ans_n":     ans_num,
            "ans_d":     ans_den,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


# ─── without_replacement_conditional_probability ─────────────────────────────

# Scenario templates for without-replacement problems.
# Each entry: (label, question_fn, explanation_fn) where fns accept (bag_params)
_WOR_SCENARIOS = [
    "red_white_ball",
    "red_blue_ball",
    "numbered_cards",
]


def _wor_ball_scenario(
    color_a: str, color_b: str,
    n_a: int, n_b: int,
    event_first: str, color_cond: str, color_ask: str,
    n_cond: int, n_remaining: int,
) -> tuple[str, str, int, int]:
    """Generic two-color ball without-replacement scenario helper."""
    n_total = n_a + n_b
    # P(second=color_ask | first=event_first)
    # After drawing color_cond as first: remaining = n_total-1
    # count of color_ask left depends on whether color_ask == color_cond
    if color_cond == color_ask:
        n_ask_remain = n_cond - 1
    else:
        n_ask_remain = n_a if color_ask == color_a else n_b
    n_remain = n_total - 1
    return n_ask_remain, n_remain


def without_replacement_conditional_probability(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a without-replacement conditional probability problem.

    Two-step scenarios only (Phase 6D):
      - red_white_ball:  bag with red and white balls; draw 2 sequentially without replacement
      - red_blue_ball:   bag with red and blue balls; draw 2 sequentially without replacement
      - numbered_cards:  numbered cards 1..N; draw 2 cards without replacement,
                         given first is even/odd find P(second is target)

    Answer = P(second event | first event) via direct counting.
    No Bayes, no three-step chains, no multi-event complex trees.
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    scenarios = _WOR_SCENARIOS[:]
    if seed is not None:
        start = abs(int(seed)) % len(scenarios)
        scenario_order = scenarios[start:] + scenarios[:start]
    else:
        scenario_order = scenarios
        rng.shuffle(scenario_order)

    if difficulty <= 1:
        ball_totals = [5, 6, 7, 8]
    elif difficulty == 2:
        ball_totals = [6, 7, 8, 9, 10]
    else:
        ball_totals = [8, 9, 10, 12]

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    ans_num = ans_den = 0

    for _ in range(100):
        scenario = scenario_order[rng.randint(0, len(scenario_order) - 1)]

        # ── red_white_ball or red_blue_ball ──────────────────────────────────
        if scenario in ("red_white_ball", "red_blue_ball"):
            color_b = "白球" if scenario == "red_white_ball" else "藍球"
            color_a = "紅球"
            n_total = rng.choice(ball_totals)
            # n_red in [2, n_total-2] so both colours have ≥2 each
            if n_total < 4:
                continue
            n_red = rng.randint(2, n_total - 2)
            n_other = n_total - n_red

            # Randomly decide: given first is red or first is color_b
            first_color, first_n = rng.choice([
                (color_a, n_red),
                (color_b, n_other),
            ])
            # Ask: second is same color or other color
            ask_color, ask_n = rng.choice([
                (color_a, n_red),
                (color_b, n_other),
            ])

            # After drawing first_color, remaining:
            if ask_color == first_color:
                ans_num = first_n - 1
            else:
                ans_num = ask_n
            ans_den = n_total - 1

            if ans_num <= 0:
                continue

            candidate = (WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID, scenario, n_total, n_red, first_color, ask_color)
            if candidate in seen:
                continue

            ans_str  = _fraction_str(ans_num, ans_den)
            pa_count = first_n  # count of first_color in bag

            question_text = (
                f"袋中裝有 ${n_red}$ 顆{color_a}與 ${n_other}$ 顆{color_b}，共 ${n_total}$ 顆。"
                f"不放回連取兩顆，已知第一顆為{first_color}，"
                f"第二顆也是{ask_color}的機率為？"
            )
            explanation = (
                f"第一顆取出{first_color}後，袋中剩 ${n_total - 1}$ 顆，"
                f"其中{ask_color}有 ${ans_num}$ 顆。\n"
                f"故所求條件機率 $P(\\text{{第二顆為{ask_color}}}|\\text{{第一顆為{first_color}}})$"
                f"$=\\dfrac{{{ans_num}}}{{{ans_den}}}={ans_str}$。"
            )
            parameter_tuple = candidate

        # ── numbered_cards ────────────────────────────────────────────────────
        else:
            # Cards 1..N; draw 2 without replacement
            if difficulty <= 1:
                N_choices = [6, 8, 10]
            else:
                N_choices = [8, 10, 12]
            N = rng.choice(N_choices)

            evens = list(range(2, N + 1, 2))
            odds  = list(range(1, N + 1, 2))

            # Condition: first card is even or odd
            cond_type, cond_cards = rng.choice([
                ("偶數", evens),
                ("奇數", odds),
            ])
            n_cond = len(cond_cards)
            if n_cond < 1:
                continue

            # Ask: second card is even or odd (allow same or different)
            ask_type, ask_cards = rng.choice([
                ("偶數", evens),
                ("奇數", odds),
            ])

            # After drawing a card of cond_type, remaining = N-1 cards
            # count of ask_type left:
            if ask_type == cond_type:
                ans_num = n_cond - 1
            else:
                n_ask = len(ask_cards)
                ans_num = n_ask
            ans_den = N - 1

            if ans_num <= 0:
                continue

            candidate = (WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID, "numbered_cards", N, cond_type, ask_type)
            if candidate in seen:
                continue

            ans_str = _fraction_str(ans_num, ans_den)

            question_text = (
                f"將 $1$ 到 ${N}$ 的 ${N}$ 張號碼牌不放回地依序各抽一張。"
                f"已知第一張為{cond_type}號碼牌，"
                f"第二張也是{ask_type}號碼牌的機率為？"
            )
            explanation = (
                f"$1$ 至 ${N}$ 共 ${N}$ 張，{cond_type}號碼牌有 ${n_cond}$ 張。\n"
                f"取走一張{cond_type}牌後，剩 ${N - 1}$ 張，"
                f"其中{ask_type}號碼牌有 ${ans_num}$ 張。\n"
                f"故所求條件機率 $=\\dfrac{{{ans_num}}}{{{ans_den}}}={ans_str}$。"
            )
            parameter_tuple = candidate

        break

    if parameter_tuple is None:
        raise ValueError(
            "without_replacement_conditional_probability: failed to generate after 100 retries."
        )

    answer  = _fraction_str(ans_num, ans_den)
    choices = _make_fraction_choices(ans_num, ans_den, rng) if multiple_choice else []

    payload = {
        "question_text":  question_text,
        "choices":        choices,
        "answer":         answer,
        "explanation":    explanation,
        "skill_id":       skill_id,
        "subskill_id":    subskill_id,
        "problem_type_id": WITHOUT_REPLACEMENT_PROBLEM_TYPE_ID,
        "generator_key":  WITHOUT_REPLACEMENT_GENERATOR_KEY,
        "answer_type":    "rational_fraction",
        "difficulty":     difficulty,
        "diagnosis_tags": [
            "conditional_probability",
            "without_replacement",
            "sequential_draw",
        ],
        "remediation_candidates": [
            "classical_probability_fraction",
            "conditional_probability_basic",
            "sample_space_count_numeric",
        ],
        "source_style_refs": [
            "tc_b4_ch2_conditional_wor_01",
            "without_replacement_conditional_probability",
        ],
        "parameters": {
            "scenario":        scenario,
            "ans_num":         ans_num,
            "ans_den":         ans_den,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])

    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
