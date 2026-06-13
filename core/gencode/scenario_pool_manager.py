from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Callable

from core.gencode.answer_format_hint import build_answer_format_suffix
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

QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS: list[dict[str, Any]] = [
    {
        "type": "farmer_fence",
        "parameter_choices": [40, 60, 80, 100, 120],
        "build": lambda L: {
            "text": (
                f"一位農夫想利用 {L} 公尺長的籬笆沿河的一岸圍成一個矩形區域，"
                "靠河的一邊不圍，試求農夫可圍成的最大矩形面積為何？"
            ),
            "answer": Fraction(L**2, 8),
            "note": "L1 填充題 / 數值題 尾綴",
        },
    },
    {
        "type": "commodity_profit",
        "parameter_choices": [10, 20, 30],
        "build": lambda P: {
            "text": (
                f"某商店販售一款文具，若每件定價 {P} 元，每天可賣出 200 件。"
                "已知定價每調升 1 元，每天銷售量就減少 2 件。試求此商品的最大利潤為何？"
            ),
            "answer": Fraction((200 + 2 * P) ** 2, 8),
            "note": "L1 填充題 / 數值題 尾綴",
        },
    },
]


def generate_quadratic_extremum_application(
    seed: int,
    problem_type_id: str = "",
    *,
    require_integer: bool = False,
) -> dict[str, Any]:
    """
    SOP v0.3.1 & v0.3.2 Layer 6 具名全域 Domain 模組。
    專職負責 4457 題等高職數B極值應用題文本隨機化，並在最後一毫秒黏貼中文化答案範例尾綴。
    """
    _ = problem_type_id
    chosen = None
    parameter = 0
    data: dict[str, Any] = {}
    raw_ans = Fraction(0)
    for attempt in range(128):
        rng = random.Random(f"{seed}|quad_ext_app|{attempt}")
        cand = rng.choice(QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS)
        build_fn: Callable[[int], dict[str, Any]] = cand["build"]
        param = rng.choice(list(cand["parameter_choices"]))
        payload = build_fn(param)
        ans = payload.get("answer")
        if not isinstance(ans, Fraction):
            ans = Fraction(ans)
        if require_integer and ans.denominator != 1:
            continue
        chosen, parameter, data, raw_ans = cand, param, payload, ans
        break
    if chosen is None:
        chosen = QUADRATIC_EXTREMUM_APPLICATION_SCENARIOS[0]
        build_fn = chosen["build"]
        parameter = chosen["parameter_choices"][0]
        data = build_fn(parameter)
        raw_ans = Fraction(data["answer"]) if not isinstance(data["answer"], Fraction) else data["answer"]

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
    ac = get_answer_contract(spec)
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

    suffix_body = build_answer_format_suffix(ac)
    if not suffix_body:
        return payload

    if "（答案範例：" in question_text:
        import re

        question_text = re.sub(r"\n?（答案範例：[^）]*）\s*$", "", question_text).rstrip()

    suffix = f"\n{suffix_body}"
    question_text = question_text + suffix
    payload["question_text"] = question_text
    payload["question"] = question_text
    metadata = dict(payload.get("metadata") or {})
    metadata["answer_format_suffix"] = suffix_body
    payload["metadata"] = metadata
    return payload


def finalize_question_text(
    payload: dict[str, Any],
    problem_type_spec: dict[str, Any],
) -> dict[str, Any]:
    return append_answer_format_suffix(payload, problem_type_spec)
