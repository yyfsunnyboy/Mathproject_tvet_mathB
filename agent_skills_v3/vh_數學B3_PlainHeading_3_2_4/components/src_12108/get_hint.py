from __future__ import annotations
from typing import Any


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = [
        "先把條件寫成等式或不等式，並標出未知數。",
        "交點、同側異側與目標函數都用精確分數計算。",
        "代回每條限制，確認點在可行區域內。",
    ]
    idx = max(0, min(int(step) - 1, len(steps) - 1))
    return steps[idx]
