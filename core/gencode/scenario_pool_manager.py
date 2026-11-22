from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Callable

from core.gencode.answer_format_hint import build_answer_format_suffix_for_stem
from core.gencode.answer_payload import answer_type_family
from core.gencode.problem_type_spec import get_answer_contract

# ── Layer 6 Template Domain：二次函數極值素養情境文本池 ─────────────────────────

QUADRATIC_EXTREMUM_LITERACY_SCENARIOS: list[tuple[str, str]] = [
    (
        "store_profit",
        "某商店販售商品時，利潤與售價 $x$ 的關係為二次函數 {equation}。"
        "請依二次函數極值概念，求此商店可獲得的{extreme_label}。",
    ),
    (
        "projectile_height",
        "某物體拋出後，高度與時間 $t$ 的關係為二次函數 {equation}。"
        "請求該物體所能達到的{extreme_label}。",
    ),
    (
        "garden_area",
        "用一段圍籬圍成矩形區域，面積與一邊長 $x$ 的關係為二次函數 {equation}。"
        "請求此區域的{extreme_label}。",
    ),
    (
        "tour_revenue",
        "某旅行團收入與參加人數的關係為二次函數 {equation}。"
        "為使收入最佳，請求此情境下的{extreme_label}。",
    ),
]

def _build_farmer_fence(L: int) -> dict[str, Any]:
    return {
        "text": (
            f"一位農夫想利用 {L} 公尺長的籬笆沿河的一岸圍成一個矩形區域，"
            "靠河的一邊不圍，試求農夫可圍成的最大矩形面積為何？"
        ),
        "answer": Fraction(L**2, 8),
        "answer_type": "integer",
        "note": "L1 填充題 / 數值題 尾綴",
    }


def _build_commodity_profit(P: int) -> dict[str, Any]:
    return {
        "text": (
            f"某商店販售一款文具，若每件定價 {P} 元，每天可賣出 200 件。"
            "已知定價每調升 1 元，每天銷售量就減少 2 件。試求此商品的最大利潤為何？"
        ),
        "answer": Fraction((200 + 2 * P) ** 2, 8),
        "answer_type": "integer",
        "note": "L1 填充題 / 數值題 尾綴",
    }


def _build_group_buy_multi(params: tuple[int, int, int]) -> dict[str, Any]:
    """團購促銷：回傳增加人數／單價／總金額（對應 src_4465 多小題結構）。"""
    base_n, price, drop = params
    # y=(price-drop*x)(base_n+x); vertex x*=(price-drop*base_n)/(2*drop)
    numer = price - drop * base_n
    if drop <= 0 or numer <= 0 or numer % (2 * drop) != 0:
        raise ValueError("group_buy_params_invalid")
    x_star = numer // (2 * drop)
    unit = price - drop * x_star
    total = unit * (base_n + x_star)
    return {
        "text": (
            f"某電信行想利用網路團購手機促銷活動（每人限購1支），預定人數為 {base_n} 人，"
            f"且每支手機售價 {price} 元，若達 {base_n} 人以上，每增加 1 人，則每支手機減收 {drop} 元，"
            "試問整個促銷方案應增加多少人，才能使手機有最大的銷售金額？"
            "此時手機價格為何？銷售總金額為多少元？"
            "（請依序填：增加人數、單價、總金額）"
        ),
        "answer": {
            "part_1": str(x_star),
            "part_2": str(unit),
            "part_3": str(total),
        },
        "answer_type": "multi_part",
        "note": "多小題：人數／單價／總額",
        "parameter": {"base_n": base_n, "price": price, "drop": drop, "x_star": x_star},
    }


def _build_tour_revenue_multi(params: tuple[int, int, int]) -> dict[str, Any]:
    """旅行社人數折扣：回傳增加人數／最多金額（對應 src_4471）。"""
    base_n, price, drop = params
    numer = price - drop * base_n
    if drop <= 0 or numer <= 0 or numer % (2 * drop) != 0:
        raise ValueError("tour_params_invalid")
    x_star = numer // (2 * drop)
    total = (price - drop * x_star) * (base_n + x_star)
    return {
        "text": (
            f"旅行社舉辦旅遊活動，預定 {base_n} 人出團，每人收費 {price} 元，"
            f"超過 {base_n} 人以後，每增加 1 人，每人收費可減少 {drop} 元。"
            "試問增加多少人時，旅行社可收到最多的錢？且最多可收到多少錢？"
            "（請依序填：增加人數、最多金額）"
        ),
        "answer": {
            "part_1": str(x_star),
            "part_2": str(total),
        },
        "answer_type": "multi_part",
        "note": "多小題：人數／最多金額",
        "parameter": {"base_n": base_n, "price": price, "drop": drop, "x_star": x_star},
    }


QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS: list[dict[str, Any]] = [
    {
        "type": "farmer_fence",
        "parameter_choices": [40, 60, 80, 100, 120],
        "build": _build_farmer_fence,
        "arity": "single",
    },
    {
        "type": "commodity_profit",
        "parameter_choices": [10, 20, 30],
        "build": _build_commodity_profit,
        "arity": "single",
    },
    {
        "type": "group_buy_multi",
        "parameter_choices": [
            (20, 6000, 100),
            (30, 8000, 200),
            (40, 9000, 150),
            (25, 5000, 100),
        ],
        "build": _build_group_buy_multi,
        "arity": "multi_part",
    },
    {
        "type": "tour_revenue_multi",
        "parameter_choices": [
            (20, 3000, 100),
            (15, 4000, 100),
            (25, 3500, 50),
            (10, 5000, 200),
        ],
        "build": _build_tour_revenue_multi,
        "arity": "multi_part",
    },
]

_SCENARIO_ALIASES = {
    "group_buy": "group_buy_multi",
    "group_buy_multi_part": "group_buy_multi",
    "telecom_group_buy": "group_buy_multi",
    "tour": "tour_revenue_multi",
    "tour_group": "tour_revenue_multi",
    "tour_revenue": "tour_revenue_multi",
    "farmer": "farmer_fence",
    "fence": "farmer_fence",
}


def generate_quadratic_extremum_application(
    seed: int,
    problem_type_id: str = "",
    *,
    require_integer: bool = False,
    preferred_scenario: str | None = None,
) -> dict[str, Any]:
    """
    SOP v0.3.1 & v0.3.2 Layer 6 具名全域 Domain 模組。
    專職負責 4457 題等高職數B極值應用題文本隨機化，並在最後一毫秒黏貼中文化答案範例尾綴。
    """
    _ = problem_type_id
    preferred = str(preferred_scenario or "").strip()
    preferred = _SCENARIO_ALIASES.get(preferred, preferred)

    by_type = {str(row["type"]): row for row in QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS}
    pool = (
        [by_type[preferred]]
        if preferred in by_type
        else [row for row in QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS if row.get("arity") == "single"]
    )

    chosen = None
    parameter: Any = 0
    data: dict[str, Any] = {}
    for attempt in range(128):
        rng = random.Random(f"{seed}|quad_ext_app|{attempt}|{preferred}")
        cand = rng.choice(pool)
        build_fn: Callable[[Any], dict[str, Any]] = cand["build"]
        param = rng.choice(list(cand["parameter_choices"]))
        try:
            payload = build_fn(param)
        except ValueError:
            continue
        ans = payload.get("answer")
        if payload.get("answer_type") == "multi_part":
            chosen, parameter, data = cand, param, payload
            break
        if not isinstance(ans, Fraction):
            ans = Fraction(ans)
        if require_integer and ans.denominator != 1:
            continue
        chosen, parameter, data = cand, param, payload
        break
    if chosen is None:
        chosen = pool[0]
        build_fn = chosen["build"]
        parameter = chosen["parameter_choices"][0]
        data = build_fn(parameter)

    if data.get("answer_type") == "multi_part":
        parts = dict(data["answer"])
        part_specs = [
            {
                "key": key,
                "checker": "integer_checker",
                "checker_key": "integer_checker",
                "equivalence_type": "numeric_exact",
                "answer": value,
                "accepted_formats": [str(value)],
            }
            for key, value in parts.items()
        ]
        return {
            "question_text": str(data["text"]).strip(),
            "answer": parts,
            "correct_answer": parts,
            "choices": [],
            "answer_type": "multi_part",
            "checker_key": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "presentation_mode": "short_answer",
            "answer_contract": {
                "answer_type": "multi_part",
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
                "equivalence_type": "multi_part_answer",
                "presentation_mode": "short_answer",
                "parts": part_specs,
                "answer_format_example": "；".join(str(v) for v in parts.values()),
            },
            "metadata": {
                "givens": {
                    "parameter": parameter,
                    "scenario_type": chosen["type"],
                    **(data.get("parameter") if isinstance(data.get("parameter"), dict) else {}),
                },
                "target": "application_multi_part_extremum",
                "derivation": ["Solved via quadratic revenue model vertex."],
                "scenario_pool": "quadratic_extremum_application",
                "format_note": data.get("note", ""),
            },
        }

    raw_ans = data.get("answer")
    if not isinstance(raw_ans, Fraction):
        raw_ans = Fraction(raw_ans)
    final_ans = int(raw_ans) if raw_ans.denominator == 1 else raw_ans
    question_text = str(data["text"]).strip()
    return {
        "question_text": question_text,
        "answer": final_ans,
        "correct_answer": final_ans,
        "choices": [],
        "checker_key": "integer_checker" if require_integer else "rational_checker",
        "equivalence_type": "numeric_exact" if require_integer else "rational_equivalent",
        "presentation_mode": "short_answer",
        "metadata": {
            "givens": {"parameter": parameter, "scenario_type": chosen["type"]},
            "target": "application_max_value",
            "derivation": ["Solved deterministically via standard quadratic optimization modeling."],
            "scenario_pool": "quadratic_extremum_application",
            "format_note": data.get("note", ""),
        },
    }


def should_use_literacy_scenario(skill_id: str, problem_type_id: str) -> bool:
    sid = str(skill_id or "")
    pt = str(problem_type_id or "")
    return "QuadraticFunctionExtremum" in sid or pt == "integer_compute_quadratic_vertex"


def should_use_application_scenario(skill_id: str, problem_type_id: str) -> bool:
    return should_use_literacy_scenario(skill_id, problem_type_id)


def pick_quadratic_extremum_scenario(
    *,
    seed: int | None,
    problem_type_id: str,
) -> tuple[str, str]:
    rng = random.Random(f"{seed}|quadratic_extremum_scenario|{problem_type_id}")
    return rng.choice(QUADRATIC_EXTREMUM_LITERACY_SCENARIOS)


def build_quadratic_extremum_literacy_stem(
    *,
    equation_display: str,
    extreme_label: str,
    template: str,
) -> str:
    return template.format(equation=equation_display, extreme_label=extreme_label)


def format_answer_example_text(answer: Any) -> str:
    if isinstance(answer, Fraction):
        return str(int(answer)) if answer.denominator == 1 else f"{answer.numerator}/{answer.denominator}"
    if isinstance(answer, bool) or answer is None:
        return ""
    return str(answer).strip()


def append_answer_format_suffix(
    payload: dict[str, Any],
    problem_type_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """SOP §4.3.6: append contract-shaped Chinese answer example suffix at question tail."""
    spec = problem_type_spec if isinstance(problem_type_spec, dict) else {}
    # Prefer payload-embedded contract when present (component-level fidelity overrides).
    embedded = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else None
    ac = embedded if (isinstance(embedded, dict) and str(embedded.get("answer_type") or "").strip()) else get_answer_contract(spec)
    if not ac and isinstance(payload.get("answer_contract"), dict):
        ac = payload["answer_contract"]
    pm = str(ac.get("presentation_mode", "")).strip()
    at_family = answer_type_family(str(ac.get("answer_type", "")))
    choices = payload.get("choices")
    if pm == "single_choice" or at_family == "single_choice":
        return payload
    if isinstance(choices, list) and choices:
        return payload

    question_text = str(payload.get("question_text") or payload.get("question") or "").strip()
    if not question_text:
        return payload

    if "（答案範例：" in question_text:
        import re

        question_text = re.sub(r"\n?（答案範例：[^）]*）\s*$", "", question_text).rstrip()

    suffix_body, suppressed_reason = build_answer_format_suffix_for_stem(ac, question_text)
    metadata = dict(payload.get("metadata") or {})
    if suppressed_reason:
        metadata["answer_format_suffix_suppressed"] = suppressed_reason
        payload["metadata"] = metadata
    if not suffix_body:
        return payload

    question_text = question_text + suffix_body
    payload["question_text"] = question_text
    payload["question"] = question_text
    metadata["answer_format_suffix"] = suffix_body
    payload["metadata"] = metadata
    return payload


def finalize_question_text(
    payload: dict[str, Any],
    problem_type_spec: dict[str, Any],
) -> dict[str, Any]:
    return append_answer_format_suffix(payload, problem_type_spec)
