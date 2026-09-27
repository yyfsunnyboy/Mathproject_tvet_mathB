from __future__ import annotations
from typing import Any


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = [
        "先確認未知數，並把條件寫成等式或不等式。",
        "用精確分數運算；移項時注意係數正負與不等號方向。",
        "代回原條件，確認解的個數與範圍。",
    ]
    idx = max(0, min(int(step) - 1, len(steps) - 1))
    return steps[idx]
