from __future__ import annotations
from typing import Any


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = [
        "先辨識這是等差還是等比，以及已知條件是哪幾個。",
        "寫出對應公式：a_n 或 S_n，再代入已知求未知。",
        "檢查答案是否滿足原條件（正負、項數、公比/公差）。",
    ]
    idx = max(0, min(int(step) - 1, len(steps) - 1))
    return steps[idx]
