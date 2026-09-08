from __future__ import annotations
from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示：
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    if step == 1:
        return "請先閱讀題目：將給定個角化成以度為單位（包含含 π 的弧度與純實數弧度）。"
    if step == 2:
        return "回想換算公式：π 弧度 = 180°，因此 1 弧度 = (180 / π)°。"
    if step == 3:
        return "計算算式：\n(1) 與 (2) 將式中 π 換成 180° 計算整數或分數度數。\n(3) 若為純數字 r（如 4 弧度），直接乘以 180 / π 得到 (r × 180 / π)°。"
    return ""
