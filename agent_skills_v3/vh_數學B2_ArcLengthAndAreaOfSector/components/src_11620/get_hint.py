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
    L = givens.get("length", 12)
    half_angle = givens.get("half_angle", 15)
    total_deg = 2 * half_angle
    if level == 1:
        return f"提示：鐘擺左右各擺動 {half_angle}°，因此總擺角為 \\({half_angle}^\\circ \\times 2 = {total_deg}^\\circ\\)。"
    elif level == 2:
        return f"提示：總擺角化為弧度 \\(\\theta = {total_deg} \\times \\frac{{\\pi}}{{180}}\\)，鐘擺長即為扇形半徑 \\(r = {L}\\)。"
    return f"步驟：最大面積 \\(A = \\frac{{1}}{{2}}r^2\\theta\\)，底端揮出的最大弧長 \\(S = r\\theta\\)。"
