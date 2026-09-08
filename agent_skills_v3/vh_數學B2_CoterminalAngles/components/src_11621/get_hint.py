from __future__ import annotations
from typing import Any

def get_hint(step_or_problem: Any = 1, question_payload: Any = None, **kwargs: Any) -> str:
    if isinstance(step_or_problem, dict):
        problem = step_or_problem
        level = kwargs.get("step") or kwargs.get("level") or (question_payload if isinstance(question_payload, int) else 1)
    else:
        level = int(step_or_problem or 1)
        problem = question_payload if isinstance(question_payload, dict) else kwargs.get("problem", {})
    givens = problem.get("math_core", {}).get("givens", {})
    base = givens.get("base_deg", 60)
    if level == 1:
        return f"提示：與 {base}° 互為同界角，表示該角與 {base}° 的差必須是 360° 的整數倍。"
    elif level == 2:
        return f"提示：計算各選項與 {base}° 相減後的差，檢查能否被 360 整除。"
    return f"步驟：設選項角度為 \\(\theta\\)，若 \\(\frac{{\\theta - {base}}}{{360}}\\) 為整數，則為同界角。"
