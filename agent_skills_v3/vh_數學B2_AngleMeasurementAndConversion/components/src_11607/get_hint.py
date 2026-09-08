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
        d_val = givens.get("deg_input", "-570")
        r_val = givens.get("rad_input", "5π/6")
        return f"請先閱讀題目：第 (1) 小題將度度量 {d_val}° 化為以弧度為單位（注意負號）；第 (2) 小題將弧度量 {r_val} 化為以度為單位。"

    if step == 2:
        return "換算關係：180° = π 弧度。負角的換算方式相同，只需保留負號。"

    if step == 3:
        return "計算算式：\n(1) 度化弧度：度數乘以 (π / 180)，分數約分至最簡。\n(2) 弧度化度：將式中 π 換成 180° 後計算得到度數。"

    return ""
