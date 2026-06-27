from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    givens = (payload.get("math_core") or {}).get("givens") or payload.get("validation_facts") or {}
    lower = givens.get("lower_bound")
    upper = givens.get("upper_bound")

    if step == 1:
        return (
            "先讀懂題目给出的支持度可能範圍。"
            f"{'目前區間為 ' + str(lower) + '%～' + str(upper) + '%。' if lower is not None and upper is not None else ''}"
            "題目要求的是支持度 p，不是區間寬度。"
        )
    if step == 2:
        return "信賴區間的中點就是點估計的支持度 p。"
    if step == 3:
        return "計算 p = (下限 + 上限) / 2，再與四個選項比對。"
    return ""
