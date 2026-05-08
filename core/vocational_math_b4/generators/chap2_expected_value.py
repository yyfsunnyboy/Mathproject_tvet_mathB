"""Deterministic B4 Chapter 2 expected-value generators – Phase 6F-R.

Textbook alignment target (B4 Chapter 2-3):
  - 單次硬幣 / 骰子 / 抽取結果對應得失金額或得分
  - 已整理好的金額(得分)分布表，求 E(X)
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

EXPECTATION_DISCRETE_BASIC_PROBLEM_TYPE_ID = "expectation_discrete_basic"
EXPECTATION_DISCRETE_BASIC_GENERATOR_KEY = "b4.chap2.expectation_discrete_basic"

EXPECTATION_FROM_DISTRIBUTION_PROBLEM_TYPE_ID = "expectation_from_distribution"
EXPECTATION_FROM_DISTRIBUTION_GENERATOR_KEY = "b4.chap2.expectation_from_distribution"


def _fraction_str(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    g = math.gcd(abs(numerator), denominator)
    n, d = numerator // g, denominator // g
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _str_from_fraction(fr: Fraction) -> str:
    return _fraction_str(fr.numerator, fr.denominator)


def _textbook_discrete_templates() -> list[dict]:
    """Representative contexts from textbook examples (money/score expectation)."""
    return [
        {
            "context_id": "coin_gain_loss_20_10",
            "question_text": (
                "擲一枚均勻硬幣一次，若出現正面可得 20 元，"
                "若出現反面須付 10 元（以付出記為負值）。"
                "試求玩一次所得到金額的期望值 $E(X)$。"
            ),
            "xs": [20, -10],
            "weights": [(1, 2), (1, 2)],
        },
        {
            "context_id": "dice_1_234_56_payoff",
            "question_text": (
                "擲一顆公正骰子一次：若擲出 1 點可得 12 元，"
                "若擲出 2、3、4 點須付 20 元（記為 -20），"
                "若擲出 5、6 點可得 60 元。"
                "試求擲一次骰子所得金額的期望值 $E(X)$。"
            ),
            "xs": [12, -20, 60],
            "weights": [(1, 6), (3, 6), (2, 6)],
        },
        {
            "context_id": "dice_odd_even_payoff",
            "question_text": (
                "擲一顆公正骰子一次，若為奇數點可得 100 元，"
                "若為偶數點須付 50 元（記為 -50）。"
                "試求玩一次所得到金額的期望值 $E(X)$。"
            ),
            "xs": [100, -50],
            "weights": [(1, 2), (1, 2)],
        },
        {
            "context_id": "coin_two_times_payoff",
            "question_text": (
                "擲一枚均勻硬幣 2 次：若出現 2 個正面可得 400 元，"
                "若出現 1 正 1 反可得 100 元，若出現 2 個反面須付 500 元（記為 -500）。"
                "試求擲 2 次所得金額的期望值 $E(X)$。"
            ),
            "xs": [400, 100, -500],
            "weights": [(1, 4), (2, 4), (1, 4)],
        },
    ]


def _textbook_distribution_templates() -> list[dict]:
    """Pre-built distribution tables with textbook-like wording."""
    return [
        {
            "context_id": "table_coin_game_a",
            "lead": "某硬幣遊戲玩一次，所得金額 $X$ 的分布如下表，試求其期望值 $E(X)$：",
            "xs": [20, -10],
            "weights": [(1, 2), (1, 2)],
        },
        {
            "context_id": "table_dice_game_b",
            "lead": "某骰子遊戲擲一次，所得金額 $X$ 的分布如下表，試求其期望值 $E(X)$：",
            "xs": [12, -20, 60],
            "weights": [(1, 6), (3, 6), (2, 6)],
        },
        {
            "context_id": "table_score_draw_c",
            "lead": "抽卡一次後得到分數 $X$，其機率分布如下表，試求其期望值 $E(X)$：",
            "xs": [0, 10, 20, 30],
            "weights": [(1, 8), (3, 8), (3, 8), (1, 8)],
        },
    ]


def _expected_value_frac(xs: list[int], probs: list[tuple[int, int]]) -> Fraction:
    acc = Fraction(0, 1)
    for x, (pn, pd) in zip(xs, probs, strict=True):
        acc += Fraction(x, 1) * Fraction(pn, pd)
    return acc


def _frac_str_parse(s: str) -> Fraction:
    if "/" in s:
        a, b = s.split("/", 1)
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


def _make_ev_choices(target: Fraction, rng: random.Random) -> list[str]:
    """Always include exactly one correct reduced string and three distractors."""
    correct = _str_from_fraction(target)
    seen: set[str] = {correct}
    wrong: list[str] = []

    def _push(fr: Fraction) -> None:
        s = _str_from_fraction(fr)
        if s not in seen:
            seen.add(s)
            wrong.append(s)

    f0 = target
    deltas = list(range(-8, 9))
    rng.shuffle(deltas)
    for delta in deltas:
        if delta == 0:
            continue
        _push(f0 + Fraction(delta, max(1, f0.denominator)))
        if len(wrong) >= 12:
            break

    for s in ("0", "1", "1/2", "-1/2", "3/2", "-3/2", "5/4", "7/6", "2", "-2"):
        if s not in seen:
            seen.add(s)
            wrong.append(s)

    attempts = 0
    while len(wrong) < 12 and attempts < 80:
        d = rng.randint(1, 14)
        n = rng.randint(-12, 12)
        _push(Fraction(n, d))
        attempts += 1

    rng.shuffle(wrong)
    picks: list[str] = []
    for s in wrong:
        if len(picks) >= 3:
            break
        if _frac_str_parse(s) != target:
            picks.append(s)

    while len(picks) < 3:
        filler = _str_from_fraction(target + Fraction(len(picks) + 1, 7))
        if filler not in seen:
            picks.append(filler)
            seen.add(filler)

    out = [correct] + picks[:3]
    rng.shuffle(out)
    return out


def _explain_sum(xs: list[int], probs: list[tuple[int, int]]) -> tuple[str, str]:
    """Return (formula line with symbols, substituted numeric line)."""
    terms_tex: list[str] = []
    terms_num: list[str] = []
    for x, (pn, pd) in zip(xs, probs, strict=True):
        ps = _fraction_str(pn, pd)
        terms_tex.append(f"({x})\\cdot {ps}")
        terms_num.append(f"({x})\\times {ps}")
    lhs = "+".join(terms_tex)
    rhs = "+".join(terms_num)
    return lhs, rhs


def expectation_discrete_basic(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    question_text = ""
    explanation = ""
    parameter_tuple: tuple | None = None
    ev = Fraction(0, 1)
    xs: list[int] = []
    probs: list[tuple[int, int]] = []
    tpl: dict = {}

    templates = _textbook_discrete_templates()
    for _ in range(200):
        tpl = rng.choice(templates)
        xs = list(tpl["xs"])
        probs = list(tpl["weights"])
        ev = _expected_value_frac(xs, probs)
        key = (tpl["context_id"], tuple(zip(xs, probs, strict=True)))
        if key in seen:
            continue
        probs_line = "；".join(
            [
                f"$P(X={x})={_fraction_str(pn, pd)}$"
                for x, (pn, pd) in zip(xs, probs, strict=True)
            ]
        )
        question_text = f"{tpl['question_text']} 已知：{probs_line}。"

        lhs, rhs_num = _explain_sum(xs, probs)
        evs = _str_from_fraction(ev)
        explanation = (
            "先用期望值公式：\n"
            "$E(X)=\\sum_x x\\cdot P(X=x)="
            + lhs
            + "$。\n"
            "逐項代入計算：$E(X)="
            + rhs_num
            + "="
            + evs
            + "$。\n"
            "所以期望值為 "
            + evs
            + "。"
        )
        parameter_tuple = key
        break

    if parameter_tuple is None:
        raise RuntimeError("expectation_discrete_basic: failed after retries.")

    answer = _str_from_fraction(ev)
    choices = _make_ev_choices(ev, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EXPECTATION_DISCRETE_BASIC_PROBLEM_TYPE_ID,
        "generator_key": EXPECTATION_DISCRETE_BASIC_GENERATOR_KEY,
        "answer_type": "expected_value",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "mathematical_expectation",
            "expectation_discrete_basic",
            "weighted_average",
        ],
        "remediation_candidates": [
            "classical_probability_fraction",
            "union_intersection_probability",
        ],
        "source_style_refs": [
            "tc_b4_ch2_expectation_discrete_01",
            "expectation_discrete_basic",
        ],
        "parameters": {
            "xs": list(xs),
            "weights": probs,
            "ev": str(ev),
            "context_id": tpl["context_id"],
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


def expectation_from_distribution(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    question_text = ""
    explanation = ""
    parameter_tuple: tuple | None = None
    ev = Fraction(0, 1)
    xs: list[int] = []
    probs: list[tuple[int, int]] = []
    tpl: dict = {}

    templates = _textbook_distribution_templates()
    for _ in range(200):
        tpl = rng.choice(templates)
        xs = list(tpl["xs"])
        probs = list(tpl["weights"])
        ev = _expected_value_frac(xs, probs)
        key = (tpl["context_id"], "table", tuple(zip(xs, probs, strict=True)))
        if key in seen:
            continue

        hdr = "| " + " | ".join(["X"] + [str(x) for x in xs]) + " |"
        sep = "| " + " | ".join([":---:"] * (len(xs) + 1)) + " |"
        rowp = "| " + " | ".join(["P(X)"] + [_fraction_str(pn, pd) for pn, pd in probs]) + " |"

        question_text = (
            f"{tpl['lead']}\n\n"
            f"{hdr}\n{sep}\n{rowp}\n\n"
            "請依表計算，試求其期望值。"
        )

        lhs, rhs_num = _explain_sum(xs, probs)
        evs = _str_from_fraction(ev)
        explanation = (
            "先寫公式：\n"
            "$E(X)=\\sum_x x\\cdot P(X=x)="
            + lhs
            + "$。\n"
            "逐項代入：$E(X)="
            + rhs_num
            + "="
            + evs
            + "$。\n"
            "因此期望值為 "
            + evs
            + "。"
        )
        parameter_tuple = key
        break

    if parameter_tuple is None:
        raise RuntimeError("expectation_from_distribution: failed after retries.")

    answer = _str_from_fraction(ev)
    choices = _make_ev_choices(ev, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EXPECTATION_FROM_DISTRIBUTION_PROBLEM_TYPE_ID,
        "generator_key": EXPECTATION_FROM_DISTRIBUTION_GENERATOR_KEY,
        "answer_type": "expected_value",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "mathematical_expectation",
            "expectation_from_distribution",
            "probability_table",
        ],
        "remediation_candidates": [
            "sample_space_count_numeric",
            "classical_probability_fraction",
        ],
        "source_style_refs": [
            "tc_b4_ch2_expectation_table_01",
            "expectation_from_distribution",
        ],
        "parameters": {
            "xs": list(xs),
            "weights": probs,
            "ev": str(ev),
            "presentation": "markdown_table",
            "context_id": tpl["context_id"],
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
