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
        return "提示：兩個角互為同界角，其差必須為 \\(2\\pi\\) 的整數倍（即 \\(2k\\pi\\)，\\(k \\in \\mathbb{Z}\\)）。"
    elif level == 2:
        return "提示：將各選項的角度減去基準角，檢查相減後的係數是否為偶數整數。"
    return "步驟：計算各選項與基準角之差，看其相差是否為 \\(2\\pi, 4\\pi, 6\\pi, \\dots\\) 或其負數。"
