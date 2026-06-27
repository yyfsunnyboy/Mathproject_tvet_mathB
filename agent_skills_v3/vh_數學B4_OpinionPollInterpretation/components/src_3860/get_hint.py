from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    givens = (payload.get("math_core") or {}).get("givens") or payload.get("validation_facts") or {}
    p = givens.get("support_percent")
    e = givens.get("margin_percent")

    if step == 1:
        return (
            "先找出題目的支持度 p 與抽樣誤差 e。"
            f"{'目前支持度為 ' + str(p) + '%，抽樣誤差為 ±' + str(e) + ' 個百分點。' if p is not None and e is not None else ''}"
            "思考：支持度可能落在哪些百分比之間？"
        )
    if step == 2:
        return "支持度可能範圍應以 p 為中心，左右各延伸 e 個百分點。"
    if step == 3:
        return "列出 (p-e)% ～ (p+e)%，再與四個選項比對。"
    return ""
