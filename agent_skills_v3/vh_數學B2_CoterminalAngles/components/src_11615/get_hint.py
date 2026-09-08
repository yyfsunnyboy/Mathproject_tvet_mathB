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
    deg = givens.get("rotation_deg", 2019)
    if level == 1:
        return f"提示：時鐘一整圈為 \\(360^\\circ\\)，先計算 {deg}° 除以 360° 的餘數，即可得知相對於 12 點順時針旋轉的角度。"
    elif level == 2:
        return "提示：時鐘上每大格（1小時）對應的圓心角為 \\(360^\\circ \\div 12 = 30^\\circ\\)。"
    return f"步驟：{deg}° \\(= 360^\\circ \\times k + r^\\circ\\)，再看餘數 \\(r^\\circ\\) 落在哪些鐘面數字 \\(30^\\circ \\times h\\) 與 \\(30^\\circ \\times (h+1)\\) 之間。"
