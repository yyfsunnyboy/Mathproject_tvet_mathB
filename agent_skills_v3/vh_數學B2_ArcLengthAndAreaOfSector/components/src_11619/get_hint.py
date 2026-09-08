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
    r = givens.get("radius", 12)
    deg = givens.get("degree", 135)
    if level == 1:
        return f"提示：先把圓心角 {deg}° 化為弧度 \\(\\theta = {deg} \\times \\frac{{\\pi}}{{180}}\\) 。"
    elif level == 2:
        return f"提示：弧長 \\(S = r\\theta\\)，面積 \\(A = \\frac{{1}}{{2}}r^2\\theta\\) 。"
    return f"步驟：\\(r = {r}\\)，\\(\\theta = \\frac{{{deg}\\pi}}{{180}}\\)，分別代入 \\(S = r\\theta\\) 與 \\(A = \\frac{{1}}{{2}}r^2\\theta\\)。"
