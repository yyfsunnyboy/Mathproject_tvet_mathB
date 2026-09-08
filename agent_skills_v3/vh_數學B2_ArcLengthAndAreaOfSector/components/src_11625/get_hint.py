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
    w = givens.get("width", 20)
    deg = givens.get("degree", 80)
    if level == 1:
        return f"提示：摺扇橋橫跨 {w} 公尺寬，即扇形半徑 \\(r = {w}\\) 公尺，最大展開角 \\(\\theta = {deg}^\\circ\\)。"
    elif level == 2:
        return f"提示：先把角度化為弧度 \\(\\theta = {deg} \\times \\frac{{\\pi}}{{180}}\\)，再利用扇形面積公式 \\(A = \\frac{{1}}{{2}}r^2\\theta\\)。"
    return f"步驟：\\(A = \\frac{{1}}{{2}} \\times {w}^2 \\times \\frac{{{deg}\\pi}}{{180}}\\) 平方公尺。"
