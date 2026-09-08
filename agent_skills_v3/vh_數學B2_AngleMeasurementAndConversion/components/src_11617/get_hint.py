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
        d1 = givens.get("deg1", "450")
        d2 = givens.get("deg2", "560")
        return f"請先閱讀題目：將給定的度度量角 {d1}° 與 {d2}° 化成以弧度為單位。"
    if step == 2:
        return "回想換算公式：180° = π 弧度，故 1° = (π / 180) 弧度。"
    if step == 3:
        return "將各角度乘以 (π / 180) 並將分數約分至最簡形式（保留 π）。"
    return ""
