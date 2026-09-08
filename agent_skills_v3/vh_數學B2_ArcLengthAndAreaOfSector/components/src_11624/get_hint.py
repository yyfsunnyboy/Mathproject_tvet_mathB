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
    r = givens.get("radius", 6)
    k = givens.get("parts", 3)
    if level == 1:
        return f"提示：圓形花圃的總面積為 \\(\\pi r^2 = \\pi \\times {r}^2\\)。"
    elif level == 2:
        return f"提示：將花圃平分成 {k} 等分，每一等分的扇形面積即為總面積除以 {k}。"
    return f"步驟：每一等分面積 \\(A = \\frac{{\\pi \\times {r}^2}}{{{k}}}\\)。"
