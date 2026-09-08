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
        r_val = givens.get("radius", "r")
        deg_val = givens.get("degree", "θ")
        return f"請先閱讀題目：扇形半徑為 {r_val}，圓心角為 {deg_val}°。試求此扇形的 (1) 弧長 S 與 (2) 面積 A。"

    if step == 2:
        return "回想公式：先將圓心角化為弧度 θ = (角度 × π) / 180。弧長公式 S = r * θ，面積公式 A = (1/2) * r² * θ。"

    if step == 3:
        return "代入數值化簡：\n(1) 弧長 S = 半徑 × 圓心角弧度 = r * θ。\n(2) 面積 A = (1/2) × 半徑平方 × 圓心角弧度 = (1/2) * r² * θ。請將分數約分至最簡並保留 π。"

    return ""
