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
    r = givens.get("radius", 9)
    deg = givens.get("degree", 120)
    if level == 1:
        return f"提示：圓心角化為弧度公式為 \\(\\theta = \\text{{度數}} \\times \\frac{{\\pi}}{{180}}\\) 。"
    elif level == 2:
        return f"提示：弧長公式為 \\(S = r\\theta\\)，扇形面積公式為 \\(A = \\frac{{1}}{{2}}r^2\\theta\\)（其中 \\(\\theta\\) 須為弧度）。"
    return f"步驟：\n(1) \\({deg}^\\circ = {deg} \\times \\frac{{\\pi}}{{180}}\\)。\n(2) \\(S = {r} \\times \\theta\\)。\n(3) \\(A = \\frac{{1}}{{2}} \\times {r}^2 \\times \\theta\\)。"
