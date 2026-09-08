from __future__ import annotations
from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示：
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    payload = question_payload or {}
    math_core = payload.get("math_core") or {}
    givens = math_core.get("givens") or payload.get("metadata", {}).get("givens") or {}

    if step == 1:
        base_angle = givens.get("base_angle", "θ")
        return f"請先閱讀題目：判斷各選項中，何者與 {base_angle}° 互為同界角。"

    if step == 2:
        return "同界角的定義：兩角若相差 360° 的整數倍（即 α - β = 360° × k，k 為整數），則兩角互為同界角。"

    if step == 3:
        return "將各選項的角度減去目標角，檢驗其差值是否能被 360° 整除。若能整除即互為同界角。"

    return ""
