from __future__ import annotations
from typing import Any

def get_hint(step_or_problem: Any = 1, question_payload: Any = None, **kwargs: Any) -> str:
    if isinstance(step_or_problem, dict):
        problem = step_or_problem
        level = kwargs.get("step") or kwargs.get("level") or (question_payload if isinstance(question_payload, int) else 1)
    else:
        level = int(step_or_problem or 1)
        problem = question_payload if isinstance(question_payload, dict) else kwargs.get("problem", {})
    if level == 1:
        return "提示：同界角相差 \\(2\\pi\\) 的整數倍。找出介於 \\(0\\) 到 \\(2\\pi\\) 之間的角即為最小正同界角。"
    elif level == 2:
        return "提示：最小正同界角減去 \\(2\\pi\\) 即為最大負同界角。"
    return "步驟：\n(1) 將弧度寫為 \\(2k\\pi + \\theta\\)（\\(0 < \\theta < 2\\pi\\)）。\n(2) \\(\theta\\) 為最小正同界角，\\(\theta - 2\\pi\\) 為最大負同界角。"
