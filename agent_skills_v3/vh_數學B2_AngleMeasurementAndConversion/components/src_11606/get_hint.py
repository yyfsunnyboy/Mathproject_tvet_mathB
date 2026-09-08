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
        d_val = givens.get("deg_input", "給定度數")
        r_val = givens.get("rad_input", "給定弧度")
        return f"請先閱讀題目：第 (1) 小題要將度度量 {d_val}° 化為以弧度為單位；第 (2) 小題要將弧度量 {r_val} 化為以度為單位。"

    if step == 2:
        return "回想度度量與弧度量的換算關係：180° = π 弧度。因此 1° = (π / 180) 弧度，1 弧度 = (180 / π)°。"

    if step == 3:
        return "計算算式：\n(1) 度化弧度：將度數乘以 (π / 180)，並將分數約分至最簡。\n(2) 弧度化度：將式中的 π 替換成 180° 後進行乘除計算求出整數或分數度數。"

    return ""
