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
        n_val = givens.get("slices", "n")
        return f"請先閱讀題目：半徑為 {r_val} 公分的圓形披薩，切成 {n_val} 等份大小相同的扇形。求每一塊扇形的 (1) 面積 A 與 (2) 弧長 S。"

    if step == 2:
        return "回想扇形公式：圓心角為全圓 (2π 弧度) 的 1/n，即 θ = 2π / n。扇形面積 A = (1/2) * r² * θ，扇形弧長 S = r * θ。"

    if step == 3:
        return "代入數值計算：\n(1) 每一塊扇形面積 A = (圓面積 πr²) / n = (1/2) * r² * θ。\n(2) 每一塊扇形弧長 S = (圓周長 2πr) / n = r * θ。"

    return ""
