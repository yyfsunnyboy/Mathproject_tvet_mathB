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
        return "提示：同界角相差 \\(360^\\circ\\) 的倍數。將角度除以 \\(360^\\circ\\) 找出落在 \\(0^\\circ\\) 到 \\(360^\\circ\\) 的餘數。"
    elif level == 2:
        return "提示：最小正同界角為 \\(\alpha\\)（\\(0 < \\alpha < 360^\\circ\\)），最大負同界角即為 \\(\alpha - 360^\\circ\\)。"
    return "步驟：\n(1) \\(\theta = 360^\\circ \\times k + \\alpha\\)，求出 \\(\alpha\\)。\n(2) 最大負同界角為 \\(\alpha - 360^\\circ\\)。"
