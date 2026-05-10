"""Deterministic B4 Chapter 2 expectation-extension generators – Phase 6K + 6K-D.

Skills:
  vh_數學B4_ApplicationsOfExpectation  (2-3 數學期望值 — 應用)
  vh_數學B4_MathematicalExpectation    (2-3 數學期望值 — 自評綜合)

Problem types implemented:
  1. expectation_word_problem_profit_fairness
       Phase 6K-D variety repair:
         a. lottery_payoff               (彩券獎額分布)
         b. game_fee_net_payoff          (玩一次須付入場費，依結果得獎金，求期望淨利)
         c. fair_game_entrance_fee       (已知獎金分布，求公平入場費 = E(獎金))
         d. ball_draw_payoff             (抽球遊戲：紅/白/黑球各對應金額)

  2. expectation_assessment_numeric
       Phase 6K-D textbook alignment:
         a. coin_single_payoff           (擲一枚硬幣一次：正面得 X、反面付 Y)
         b. dice_single_payoff           (擲一顆骰子一次：奇/偶或三段式得失)
         c. coin_two_times_payoff        (擲硬幣 2 次：2 正/1 正 1 反/2 反 各對應金額)
         d. distribution_table_money     (已整理好的得失分布表 X / P(X))

Strict guardrails (Phase 6K + 6K-D):
  - 不做保險精算 / 投資報酬複雜題
  - 不做大學機率論 / 抽象隨機變數分布
  - 不做超長文字題
  - 不做 image-related 題
  - 不做求未知數使期望值=0 的反推題
  - 不做手寫 / free-response
  - 不大量使用「抽卡 / 圓盤」（保留為極少量備援，不主導）
  - 不出現「隨機權重」「隨機分割」「W ∈」抽象語句

Answer format:
  - expected_value (rational fraction or integer string)
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID = (
    "expectation_word_problem_profit_fairness"
)
EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_GENERATOR_KEY = (
    "b4.chap2.expectation_word_problem_profit_fairness"
)

EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID = "expectation_assessment_numeric"
EXPECTATION_ASSESSMENT_NUMERIC_GENERATOR_KEY = "b4.chap2.expectation_assessment_numeric"


# ─── shared helpers ──────────────────────────────────────────────────────────

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


def _frac_str_parse(s: str) -> Fraction:
    if "/" in s:
        a, b = s.split("/", 1)
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


def _expected_value_frac(xs: list[int], probs: list[tuple[int, int]]) -> Fraction:
    acc = Fraction(0, 1)
    for x, (pn, pd) in zip(xs, probs, strict=True):
        acc += Fraction(x, 1) * Fraction(pn, pd)
    return acc


def _make_ev_choices(target: Fraction, rng: random.Random) -> list[str]:
    correct = _str_from_fraction(target)
    seen: set[str] = {correct}
    wrong: list[str] = []

    def _push(fr: Fraction) -> None:
        s = _str_from_fraction(fr)
        if s not in seen:
            seen.add(s)
            wrong.append(s)

    deltas = list(range(-8, 9))
    rng.shuffle(deltas)
    for delta in deltas:
        if delta == 0:
            continue
        _push(target + Fraction(delta, max(1, target.denominator)))
        if len(wrong) >= 12:
            break

    for s in ("0", "1", "1/2", "-1/2", "3/2", "-3/2", "5/4", "7/6", "2", "-2", "5"):
        if s not in seen:
            seen.add(s)
            wrong.append(s)

    attempts = 0
    while len(wrong) < 12 and attempts < 80:
        d = rng.randint(1, 14)
        n = rng.randint(-30, 30)
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
    terms_tex: list[str] = []
    terms_num: list[str] = []
    for x, (pn, pd) in zip(xs, probs, strict=True):
        ps = _fraction_str(pn, pd)
        terms_tex.append(f"({x})\\cdot {ps}")
        terms_num.append(f"({x})\\times {ps}")
    return "+".join(terms_tex), "+".join(terms_num)


def _ev_explanation_block(xs: list[int], probs: list[tuple[int, int]], ev: Fraction) -> str:
    """Standard textbook explanation: 公式 → 逐項代入 → 化簡。"""
    lhs, rhs_num = _explain_sum(xs, probs)
    evs = _str_from_fraction(ev)
    return (
        "依期望值公式：\n"
        "$E(X)=\\sum_x x\\cdot P(X=x)="
        + lhs
        + "$。\n"
        "逐項代入計算：$E(X)="
        + rhs_num
        + "="
        + evs
        + "$。"
    )


# ════════════════════════════════════════════════════════════════════════════
# A. expectation_word_problem_profit_fairness  (ApplicationsOfExpectation)
# ════════════════════════════════════════════════════════════════════════════

# A.1  Lottery payoff: 彩券售出 N 張，獎額分布。
_LOTTERY_TEMPLATES = [
    {
        "context_id": "lottery_school_a",
        "n_total": 200,
        "tiers": [(1000, 1), (500, 4), (100, 20)],
    },
    {
        "context_id": "lottery_charity_b",
        "n_total": 500,
        "tiers": [(2000, 1), (1000, 4), (200, 20)],
    },
    {
        "context_id": "lottery_city_c",
        "n_total": 1000,
        "tiers": [(2000, 5), (1000, 10), (500, 20)],
    },
    {
        "context_id": "lottery_simple_d",
        "n_total": 100,
        "tiers": [(500, 1), (200, 5), (50, 10)],
    },
]


# A.2  Game fee net payoff: 玩一次須付入場費，依結果獲得獎金，求期望淨利。
_GAME_FEE_TEMPLATES = [
    {
        "context_id": "ring_toss_game",
        "lead": (
            "某攤位舉辦套圈圈遊戲，玩一次須先付入場費 $30$ 元。"
            "玩完後依命中環數可得獎金："
        ),
        "fee": 30,
        # 命中等級, 獎金, 機率(分子, 分母)
        "rewards": [
            ("命中第一環獲得 $200$ 元", 200, (1, 10)),
            ("命中第二環獲得 $50$ 元", 50, (3, 10)),
            ("未命中得 $0$ 元", 0, (6, 10)),
        ],
        "ask_phrase": "試求玩一次此遊戲的期望淨收益 $E(X)$（單位：元，扣除入場費後）。",
    },
    {
        "context_id": "dart_game_a",
        "lead": (
            "某園遊會擲飛鏢遊戲，每玩一次須付 $20$ 元，"
            "依命中區域可得獎金："
        ),
        "fee": 20,
        "rewards": [
            ("命中紅心獲得 $100$ 元", 100, (1, 10)),
            ("命中外環獲得 $30$ 元", 30, (3, 10)),
            ("未命中得 $0$ 元", 0, (6, 10)),
        ],
        "ask_phrase": "試求玩一次此遊戲的期望淨收益 $E(X)$（單位：元）。",
    },
    {
        "context_id": "wheel_payoff_with_fee",
        "lead": (
            "某遊戲攤位以擲一顆公正骰子決定獎金，玩一次須先付 $40$ 元。"
            "依擲出點數獲得獎金："
        ),
        "fee": 40,
        "rewards": [
            ("擲出 $6$ 點獲得 $180$ 元", 180, (1, 6)),
            ("擲出 $4$ 或 $5$ 點獲得 $60$ 元", 60, (2, 6)),
            ("擲出 $1$、$2$、$3$ 點得 $0$ 元", 0, (3, 6)),
        ],
        "ask_phrase": "試求玩一次此遊戲的期望淨收益 $E(X)$（單位：元）。",
    },
]


# A.3  Fair game entrance fee: 求公平入場費（= E(獎金)）
_FAIR_FEE_TEMPLATES = [
    {
        "context_id": "fair_fee_basic_a",
        "lead": (
            "某攤位舉辦遊戲，依擲一顆公正骰子的點數決定獎金："
            "$1$ 點得 $30$ 元，$2$ 或 $3$ 點得 $60$ 元，"
            "$4$、$5$、$6$ 點得 $90$ 元。"
        ),
        "xs": [30, 60, 90],
        "weights": [(1, 6), (2, 6), (3, 6)],
        "ask_phrase": (
            "若主辦單位希望此遊戲對玩家而言為公平遊戲（即期望淨利為 $0$），"
            "請問每玩一次的入場費應收多少元？"
        ),
        "answer_label": "公平入場費",
    },
    {
        "context_id": "fair_fee_card_a",
        "lead": (
            "某簡單抽籤遊戲，籤筒中有 $10$ 支籤，"
            "其中 $1$ 支可得 $200$ 元，$3$ 支可得 $80$ 元，其餘 $6$ 支得 $0$ 元。"
        ),
        "xs": [200, 80, 0],
        "weights": [(1, 10), (3, 10), (6, 10)],
        "ask_phrase": (
            "若希望此抽籤遊戲為公平遊戲，請問每抽一支籤應收的公平入場費為多少元？"
        ),
        "answer_label": "公平入場費",
    },
    {
        "context_id": "fair_fee_coin_pair",
        "lead": (
            "擲一枚均勻硬幣 $2$ 次，依結果獲得獎金："
            "$2$ 個正面得 $80$ 元，$1$ 正 $1$ 反得 $20$ 元，$2$ 個反面得 $0$ 元。"
        ),
        "xs": [80, 20, 0],
        "weights": [(1, 4), (2, 4), (1, 4)],
        "ask_phrase": (
            "若每玩一次須收取公平入場費（即玩家期望淨利為 $0$），"
            "請問此公平入場費為多少元？"
        ),
        "answer_label": "公平入場費",
    },
]


# A.4  Ball draw payoff: 抽球遊戲，依顏色得獎金。
_BALL_DRAW_TEMPLATES = [
    {
        "context_id": "ball_draw_rwb_a",
        "lead": (
            "袋中有大小相同的紅球 $5$ 個、白球 $3$ 個、黑球 $2$ 個。"
            "若抽中紅球可得 $10$ 元、抽中白球可得 $20$ 元、抽中黑球可得 $100$ 元。"
        ),
        "xs": [10, 20, 100],
        "weights": [(5, 10), (3, 10), (2, 10)],
        "ask_phrase": "從袋中任取一球，試求所得獎金的期望值 $E(X)$（單位：元）。",
    },
    {
        "context_id": "ball_draw_rwb_b",
        "lead": (
            "袋中有大小相同的紅球 $4$ 個、藍球 $4$ 個、綠球 $2$ 個。"
            "若抽中紅球可得 $50$ 元、抽中藍球可得 $25$ 元、抽中綠球可得 $200$ 元。"
        ),
        "xs": [50, 25, 200],
        "weights": [(4, 10), (4, 10), (2, 10)],
        "ask_phrase": "從袋中任取一球，試求所得獎金的期望值 $E(X)$（單位：元）。",
    },
    {
        "context_id": "ball_draw_multiples",
        "lead": (
            "袋中有編號 $1$ 至 $10$ 的相同大小球各一顆。"
            "規定抽中為 $5$ 倍數的球可得 $20$ 元，"
            "抽中為其他編號的球可得 $5$ 元。"
        ),
        "xs": [20, 5],
        "weights": [(2, 10), (8, 10)],
        "ask_phrase": "從袋中任取一球，試求所得獎金的期望值 $E(X)$（單位：元）。",
    },
]


_APP_EXP_SCENARIOS = ("lottery", "game_fee", "fair_fee", "ball_draw")


def _build_lottery_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    for _ in range(40):
        tpl = rng.choice(_LOTTERY_TEMPLATES)
        n_total = int(tpl["n_total"])
        tiers = list(tpl["tiers"])
        prize_total = sum(m for _amt, m in tiers)
        if prize_total >= n_total:
            continue
        zero_count = n_total - prize_total
        xs = [amt for amt, _m in tiers] + [0]
        probs = [(m, n_total) for _amt, m in tiers] + [(zero_count, n_total)]
        ev = _expected_value_frac(xs, probs)

        key = ("lottery", tpl["context_id"], n_total, tuple(tiers))
        if key in seen:
            continue

        tier_phrase_parts = [f"${amt}$ 元 ${m}$ 張" for amt, m in tiers]
        tier_phrase = "、".join(tier_phrase_parts)

        question_text = (
            f"某攤位售出 ${n_total}$ 張彩券，獎額分布為："
            f"{tier_phrase}，其餘為銘謝惠顧（得 $0$ 元）。"
            "若隨機抽取一張，試求一張彩券的期望所得金額 $E(X)$（單位：元）。"
        )
        evs = _str_from_fraction(ev)
        explanation = (
            _ev_explanation_block(xs, probs, ev)
            + f"\n故一張彩券的期望所得金額為 {evs} 元。"
        )

        return _finalize_app_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id="lottery",
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            extra_params={"n_total": n_total, "tiers": [list(t) for t in tiers]},
            parameter_tuple=key,
        )
    return None


def _build_game_fee_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    for _ in range(40):
        tpl = rng.choice(_GAME_FEE_TEMPLATES)
        rewards = list(tpl["rewards"])
        fee = int(tpl["fee"])
        # 淨收益 X = 獎金 - 入場費
        xs = [int(r[1]) - fee for r in rewards]
        probs = [tuple(r[2]) for r in rewards]
        prob_sum = sum(Fraction(pn, pd) for pn, pd in probs)
        if prob_sum != 1:
            continue
        ev = _expected_value_frac(xs, probs)
        key = ("game_fee", tpl["context_id"], fee, tuple((r[1], r[2]) for r in rewards))
        if key in seen:
            continue

        reward_lines = "、".join(r[0] for r in rewards)
        question_text = f"{tpl['lead']}{reward_lines}。{tpl['ask_phrase']}"

        evs = _str_from_fraction(ev)
        # 詳解寫成「先求獎金期望值 → 再扣入場費」的兩段，貼近課本敘事。
        gross_xs = [int(r[1]) for r in rewards]
        gross_ev = _expected_value_frac(gross_xs, probs)
        gross_evs = _str_from_fraction(gross_ev)
        gross_lhs, gross_rhs = _explain_sum(gross_xs, probs)
        explanation = (
            "先求一次遊戲的期望獎金 $E(\\text{獎金})$：\n"
            f"$E(\\text{{獎金}})={gross_lhs}={gross_rhs}={gross_evs}$ 元。\n"
            f"扣除入場費 ${fee}$ 元後，期望淨收益為：\n"
            f"$E(X)=E(\\text{{獎金}})-{fee}={gross_evs}-{fee}={evs}$ 元。"
        )

        return _finalize_app_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id="game_fee",
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            extra_params={"fee": fee, "rewards": [list(r) for r in rewards]},
            parameter_tuple=key,
        )
    return None


def _build_fair_fee_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    for _ in range(40):
        tpl = rng.choice(_FAIR_FEE_TEMPLATES)
        xs = list(tpl["xs"])
        probs = [tuple(p) for p in tpl["weights"]]
        prob_sum = sum(Fraction(pn, pd) for pn, pd in probs)
        if prob_sum != 1:
            continue
        ev = _expected_value_frac(xs, probs)
        key = ("fair_fee", tpl["context_id"], tuple(xs), tuple(probs))
        if key in seen:
            continue

        question_text = f"{tpl['lead']}{tpl['ask_phrase']}"

        evs = _str_from_fraction(ev)
        explanation = (
            _ev_explanation_block(xs, probs, ev)
            + f"\n公平入場費 = 期望獎金 = {evs} 元。"
        )

        return _finalize_app_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id="fair_fee",
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            extra_params={"answer_role": "fair_entrance_fee"},
            parameter_tuple=key,
        )
    return None


def _build_ball_draw_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    for _ in range(40):
        tpl = rng.choice(_BALL_DRAW_TEMPLATES)
        xs = list(tpl["xs"])
        probs = [tuple(p) for p in tpl["weights"]]
        prob_sum = sum(Fraction(pn, pd) for pn, pd in probs)
        if prob_sum != 1:
            continue
        ev = _expected_value_frac(xs, probs)
        key = ("ball_draw", tpl["context_id"], tuple(xs), tuple(probs))
        if key in seen:
            continue

        question_text = f"{tpl['lead']}{tpl['ask_phrase']}"

        evs = _str_from_fraction(ev)
        explanation = (
            _ev_explanation_block(xs, probs, ev)
            + f"\n故所得獎金的期望值為 {evs} 元。"
        )

        return _finalize_app_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id="ball_draw",
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            extra_params={"answer_role": "expected_payoff"},
            parameter_tuple=key,
        )
    return None


def _finalize_app_exp_payload(
    *,
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
    scenario_id: str,
    context_id: str,
    question_text: str,
    explanation: str,
    xs: list[int],
    probs: list[tuple[int, int]],
    ev: Fraction,
    extra_params: dict,
    parameter_tuple: tuple,
) -> dict:
    answer = _str_from_fraction(ev)
    choices = _make_ev_choices(ev, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_PROBLEM_TYPE_ID,
        "generator_key": EXPECTATION_WORD_PROBLEM_PROFIT_FAIRNESS_GENERATOR_KEY,
        "answer_type": "expected_value",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "applications_of_expectation",
            "expectation_word_problem_profit_fairness",
            f"scenario:{scenario_id}",
            "weighted_average",
        ],
        "remediation_candidates": [
            "expectation_discrete_basic",
            "expectation_from_distribution",
            "classical_probability_fraction",
        ],
        "source_style_refs": [
            f"tc_b4_ch2_applications_of_expectation_{scenario_id}_01",
            "expectation_word_problem_profit_fairness",
        ],
        "parameters": {
            "scenario_id": scenario_id,
            "context_id": context_id,
            "xs": list(xs),
            "weights": list(probs),
            "ev": str(ev),
            **extra_params,
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    seen.add(parameter_tuple)
    return payload


def expectation_word_problem_profit_fairness(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a textbook-style expectation application problem.

    Phase 6K-D scope:
      - 4 scenario families with seed-driven rotation:
          * lottery_payoff
          * game_fee_net_payoff
          * fair_game_entrance_fee
          * ball_draw_payoff
      - Answer = expected value (rational fraction or integer string).
    """
    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    if seed is not None:
        start_idx = abs(int(seed)) % len(_APP_EXP_SCENARIOS)
    else:
        start_idx = rng.randrange(len(_APP_EXP_SCENARIOS))

    rotated = list(range(len(_APP_EXP_SCENARIOS)))
    rotated = rotated[start_idx:] + rotated[:start_idx]

    builders = {
        "lottery": _build_lottery_payload,
        "game_fee": _build_game_fee_payload,
        "fair_fee": _build_fair_fee_payload,
        "ball_draw": _build_ball_draw_payload,
    }

    for offset in rotated:
        scenario = _APP_EXP_SCENARIOS[offset]
        builder = builders[scenario]
        payload = builder(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
        )
        if payload is not None:
            return payload

    raise RuntimeError(
        "expectation_word_problem_profit_fairness: failed to generate any scenario."
    )


# ════════════════════════════════════════════════════════════════════════════
# B. expectation_assessment_numeric  (MathematicalExpectation)
# ════════════════════════════════════════════════════════════════════════════
#
# 「自評綜合」型，題幹必須貼近高職 B4 課本第 2-3 節常見口吻：
#   硬幣 / 骰子 / 兩次硬幣 / 已整理好的得失分布表
#
# 抽卡 / 圓盤模板僅作為極少量備援（不在主要 scenario 列表中）。

# B.1  硬幣一次得失
_COIN_SINGLE_TEMPLATES = [
    {
        "context_id": "coin_single_a",
        "lead": (
            "擲一枚均勻硬幣一次，若出現正面可得 $30$ 元，"
            "若出現反面須付 $10$ 元（以付出記為負值）。"
        ),
        "xs": [30, -10],
        "weights": [(1, 2), (1, 2)],
    },
    {
        "context_id": "coin_single_b",
        "lead": (
            "擲一枚均勻硬幣一次，若出現正面可得 $50$ 元，"
            "若出現反面須付 $20$ 元（以付出記為負值）。"
        ),
        "xs": [50, -20],
        "weights": [(1, 2), (1, 2)],
    },
    {
        "context_id": "coin_single_c",
        "lead": (
            "擲一枚均勻硬幣一次，若出現正面可得 $100$ 元，"
            "若出現反面須付 $40$ 元（以付出記為負值）。"
        ),
        "xs": [100, -40],
        "weights": [(1, 2), (1, 2)],
    },
]

# B.2  骰子一次得失
_DICE_SINGLE_TEMPLATES = [
    {
        "context_id": "dice_three_band",
        "lead": (
            "擲一顆公正骰子一次：若擲出 $1$ 點可得 $12$ 元，"
            "若擲出 $2$、$3$、$4$ 點須付 $20$ 元（記為 $-20$），"
            "若擲出 $5$、$6$ 點可得 $60$ 元。"
        ),
        "xs": [12, -20, 60],
        "weights": [(1, 6), (3, 6), (2, 6)],
    },
    {
        "context_id": "dice_odd_even",
        "lead": (
            "擲一顆公正骰子一次，若擲出奇數點可得 $100$ 元，"
            "若擲出偶數點須付 $50$ 元（記為 $-50$）。"
        ),
        "xs": [100, -50],
        "weights": [(1, 2), (1, 2)],
    },
    {
        "context_id": "dice_six_special",
        "lead": (
            "擲一顆公正骰子一次，若擲出 $6$ 點可得 $300$ 元，"
            "其餘點數須付 $40$ 元（記為 $-40$）。"
        ),
        "xs": [300, -40],
        "weights": [(1, 6), (5, 6)],
    },
]

# B.3  擲硬幣兩次得失
_COIN_TWO_TEMPLATES = [
    {
        "context_id": "coin_two_a",
        "lead": (
            "擲一枚均勻硬幣 $2$ 次：若出現 $2$ 個正面可得 $400$ 元，"
            "若出現 $1$ 正 $1$ 反可得 $100$ 元，"
            "若出現 $2$ 個反面須付 $500$ 元（記為 $-500$）。"
        ),
        "xs": [400, 100, -500],
        "weights": [(1, 4), (2, 4), (1, 4)],
    },
    {
        "context_id": "coin_two_b",
        "lead": (
            "擲一枚均勻硬幣 $2$ 次：若出現 $2$ 個正面可得 $80$ 元，"
            "若出現 $1$ 正 $1$ 反可得 $20$ 元，"
            "若出現 $2$ 個反面須付 $40$ 元（記為 $-40$）。"
        ),
        "xs": [80, 20, -40],
        "weights": [(1, 4), (2, 4), (1, 4)],
    },
    {
        "context_id": "coin_two_c",
        "lead": (
            "擲一枚均勻硬幣 $2$ 次：若出現 $2$ 個正面可得 $200$ 元，"
            "若出現 $1$ 正 $1$ 反得 $0$ 元，"
            "若出現 $2$ 個反面須付 $100$ 元（記為 $-100$）。"
        ),
        "xs": [200, 0, -100],
        "weights": [(1, 4), (2, 4), (1, 4)],
    },
]

# B.4  已整理好的得失分布表（金額/得分語境，不寫成抽象 X）
_DISTRIBUTION_TABLE_TEMPLATES = [
    {
        "context_id": "table_money_a",
        "lead": (
            "某遊戲一次所得金額 $X$ 的分布如下："
        ),
        "xs": [200, 50, 0],
        "weights": [(1, 6), (2, 6), (3, 6)],
    },
    {
        "context_id": "table_money_b",
        "lead": (
            "某活動一次所得金額 $X$ 的分布如下："
        ),
        "xs": [100, 40, 10, 0],
        "weights": [(1, 10), (2, 10), (3, 10), (4, 10)],
    },
    {
        "context_id": "table_money_c",
        "lead": (
            "某遊戲一次所得金額 $X$（單位：元）的分布如下："
        ),
        "xs": [300, 100, -50],
        "weights": [(1, 5), (2, 5), (2, 5)],
    },
    {
        "context_id": "table_score_a",
        "lead": (
            "某抽獎遊戲一次的所得分數 $X$ 分布如下："
        ),
        "xs": [50, 20, -10],
        "weights": [(1, 4), (2, 4), (1, 4)],
    },
]


_MATH_EXP_SCENARIOS = (
    "coin_single",
    "dice_single",
    "coin_two",
    "distribution_table",
)


def _build_coin_single_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    return _build_simple_assessment_payload(
        rng=rng,
        seen=seen,
        skill_id=skill_id,
        subskill_id=subskill_id,
        difficulty=difficulty,
        multiple_choice=multiple_choice,
        scenario_id="coin_single",
        templates=_COIN_SINGLE_TEMPLATES,
        ask_phrase="試求玩一次所得到金額的期望值 $E(X)$。",
    )


def _build_dice_single_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    return _build_simple_assessment_payload(
        rng=rng,
        seen=seen,
        skill_id=skill_id,
        subskill_id=subskill_id,
        difficulty=difficulty,
        multiple_choice=multiple_choice,
        scenario_id="dice_single",
        templates=_DICE_SINGLE_TEMPLATES,
        ask_phrase="試求擲一次骰子所得金額的期望值 $E(X)$。",
    )


def _build_coin_two_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    return _build_simple_assessment_payload(
        rng=rng,
        seen=seen,
        skill_id=skill_id,
        subskill_id=subskill_id,
        difficulty=difficulty,
        multiple_choice=multiple_choice,
        scenario_id="coin_two",
        templates=_COIN_TWO_TEMPLATES,
        ask_phrase="試求擲 $2$ 次所得金額的期望值 $E(X)$。",
    )


def _build_distribution_table_payload(
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
) -> dict | None:
    """Distribution table format: lead + 列舉 P(X=x) + 求 E(X)。"""
    for _ in range(40):
        tpl = rng.choice(_DISTRIBUTION_TABLE_TEMPLATES)
        xs = list(tpl["xs"])
        probs = [tuple(p) for p in tpl["weights"]]
        prob_sum = sum(Fraction(pn, pd) for pn, pd in probs)
        if prob_sum != 1:
            continue
        ev = _expected_value_frac(xs, probs)
        key = ("distribution_table", tpl["context_id"], tuple(xs), tuple(probs))
        if key in seen:
            continue

        list_parts = [
            f"$P(X={x})={_fraction_str(pn, pd)}$"
            for x, (pn, pd) in zip(xs, probs, strict=True)
        ]
        list_phrase = "；".join(list_parts)

        question_text = (
            f"{tpl['lead']}\n{list_phrase}。\n"
            "試求 $X$ 的期望值 $E(X)$。"
        )
        explanation = _ev_explanation_block(xs, probs, ev)

        return _finalize_math_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id="distribution_table",
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            parameter_tuple=key,
        )
    return None


def _build_simple_assessment_payload(
    *,
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
    scenario_id: str,
    templates: list[dict],
    ask_phrase: str,
) -> dict | None:
    for _ in range(40):
        tpl = rng.choice(templates)
        xs = list(tpl["xs"])
        probs = [tuple(p) for p in tpl["weights"]]
        prob_sum = sum(Fraction(pn, pd) for pn, pd in probs)
        if prob_sum != 1:
            continue
        ev = _expected_value_frac(xs, probs)
        key = (scenario_id, tpl["context_id"], tuple(xs), tuple(probs))
        if key in seen:
            continue

        question_text = f"{tpl['lead']}{ask_phrase}"
        explanation = _ev_explanation_block(xs, probs, ev)

        return _finalize_math_exp_payload(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
            scenario_id=scenario_id,
            context_id=str(tpl["context_id"]),
            question_text=question_text,
            explanation=explanation,
            xs=xs,
            probs=probs,
            ev=ev,
            parameter_tuple=key,
        )
    return None


def _finalize_math_exp_payload(
    *,
    rng: random.Random,
    seen: set,
    skill_id: str,
    subskill_id: str,
    difficulty: int,
    multiple_choice: bool,
    scenario_id: str,
    context_id: str,
    question_text: str,
    explanation: str,
    xs: list[int],
    probs: list[tuple[int, int]],
    ev: Fraction,
    parameter_tuple: tuple,
) -> dict:
    answer = _str_from_fraction(ev)
    choices = _make_ev_choices(ev, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": EXPECTATION_ASSESSMENT_NUMERIC_PROBLEM_TYPE_ID,
        "generator_key": EXPECTATION_ASSESSMENT_NUMERIC_GENERATOR_KEY,
        "answer_type": "expected_value",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "mathematical_expectation",
            "expectation_assessment_numeric",
            f"scenario:{scenario_id}",
            "weighted_average",
        ],
        "remediation_candidates": [
            "expectation_discrete_basic",
            "expectation_from_distribution",
            "expectation_word_problem_profit_fairness",
        ],
        "source_style_refs": [
            f"tc_b4_ch2_mathematical_expectation_{scenario_id}_01",
            "expectation_assessment_numeric",
        ],
        "parameters": {
            "scenario_id": scenario_id,
            "context_id": context_id,
            "xs": list(xs),
            "weights": list(probs),
            "ev": str(ev),
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    seen.add(parameter_tuple)
    return payload


def expectation_assessment_numeric(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a textbook-style 'self-assessment' E(X) problem.

    Phase 6K-D scope:
      - 4 scenario families with seed-driven rotation:
          * coin_single_payoff
          * dice_single_payoff
          * coin_two_times_payoff
          * distribution_table_money
      - Answer = E(X) as rational/integer expected value (no percent accepted).
    """
    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    if seed is not None:
        start_idx = abs(int(seed)) % len(_MATH_EXP_SCENARIOS)
    else:
        start_idx = rng.randrange(len(_MATH_EXP_SCENARIOS))

    rotated = list(range(len(_MATH_EXP_SCENARIOS)))
    rotated = rotated[start_idx:] + rotated[:start_idx]

    builders = {
        "coin_single": _build_coin_single_payload,
        "dice_single": _build_dice_single_payload,
        "coin_two": _build_coin_two_payload,
        "distribution_table": _build_distribution_table_payload,
    }

    for offset in rotated:
        scenario = _MATH_EXP_SCENARIOS[offset]
        builder = builders[scenario]
        payload = builder(
            rng=rng,
            seen=seen,
            skill_id=skill_id,
            subskill_id=subskill_id,
            difficulty=difficulty,
            multiple_choice=multiple_choice,
        )
        if payload is not None:
            return payload

    raise RuntimeError(
        "expectation_assessment_numeric: failed to generate any scenario."
    )
