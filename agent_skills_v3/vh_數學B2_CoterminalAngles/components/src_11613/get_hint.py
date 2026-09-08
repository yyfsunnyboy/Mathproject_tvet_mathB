from __future__ import annotations
from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示：
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    if step == 1:
        return "請先閱讀題目：求給定角（度度量或弧度量）的「最小正同界角」與「最大負同界角」。"

    if step == 2:
        return (
            "同界角相差 360°（或 2π）的整數倍。\n"
            "最小正同界角介於 0° 到 360° 之間（或 0 到 2π 之間）；\n"
            "最大負同界角介於 -360° 到 0° 之間（或 -2π 到 0 之間）。\n"
            "最大負同界角 = 最小正同界角 - 360°（或 - 2π）。"
        )

    if step == 3:
        return (
            "計算步驟：\n"
            "1. 將角度除以 360°（或 2π），寫成 360° × k + r 的形式，使 0° < r ≤ 360°。\n"
            "2. 最小正同界角即為 r。\n"
            "3. 最大負同界角即為 r - 360°（或 r - 2π）。"
        )

    return ""
