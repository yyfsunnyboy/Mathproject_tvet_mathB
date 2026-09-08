from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示 — 強制語意骨架。
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    payload = question_payload or {}
    story_ctx = str(payload.get("story_context") or "")
    math_core = payload.get("math_core") or {}
    givens = math_core.get("givens") or payload.get("metadata", {}).get("givens") or []

    if step == 1:
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return (
            f"請先閱讀題目，找出已知條件與要求的量。"
            f"{'情境：' + story_ctx if story_ctx else ''}"
            f"目前已知：{given_text}。請用一句話說明「要求什麼」。"
        )

    if step == 2:
        target = str(math_core.get("target") or payload.get("metadata", {}).get("target") or "未知量")
        objects = math_core.get("math_objects") or []
        obj_text = "、".join(str(o) for o in objects) if objects else "適當的數學關係"
        return (
            f"將文字條件轉成數學語言：設定變數，並指出此題屬於「{obj_text}」類型。"
            f"目標是求：{target}。"
        )

    if step == 3:
        derivation = math_core.get("derivation") or payload.get("metadata", {}).get("derivation") or []
        if derivation:
            return f"依序思考：{' → '.join(str(d) for d in derivation)}。寫出關鍵算式後再化簡。"
        return "寫出本題適用的核心公式，代入已知數值，逐步化簡得到答案。"

    return ""
