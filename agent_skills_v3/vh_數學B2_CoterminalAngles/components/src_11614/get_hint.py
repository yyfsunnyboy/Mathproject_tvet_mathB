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
        return "提示：同界角相差 \\(360^\\circ\\) 的倍數（或 \\(2\\pi\\) 的倍數）。最小正同界角介於 \\(0^\\circ\\) 到 \\(360^\\circ\\) 之間（或 \\(0\\) 到 \\(2\\pi\\) 之間）。"
    elif level == 2:
        return "提示：求出最小正同界角後，減去 \\(360^\\circ\\)（或 \\(2\\pi\\)）即可得到最大負同界角。"
    return "步驟：\\(\theta = 360^\\circ \\times k + \\alpha\\)（\\(0 < \\alpha < 360^\\circ\\)），則 \\(\alpha\\) 為最小正同界角，\\(\alpha - 360^\\circ\\) 為最大負同界角。"
