from __future__ import annotations
from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示：
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    if step == 1:
        return "請先閱讀題目：完成常用特別角之度度量與弧度量對照表。"
    if step == 2:
        return "利用 180° = π 弧度，計算各特別角對應的弧度量。"
    if step == 3:
        return "將各角度乘以 (π / 180) 並約分至最簡分數。"
    return ""
