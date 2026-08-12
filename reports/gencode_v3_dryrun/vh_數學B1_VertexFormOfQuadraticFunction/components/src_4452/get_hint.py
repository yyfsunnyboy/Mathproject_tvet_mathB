from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    givens = meta.get("givens") or []
    if step == 1:
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return f"先找出已知條件：{given_text}。用一句話說明要求什麼。"
    if step == 2:
        target = str(meta.get("target") or "未知量")
        return f"把條件轉成數學關係，目標是求：{target}。"
    if step == 3:
        derivation = meta.get("derivation") or []
        if derivation:
            return "依序思考：" + " → ".join(str(d) for d in derivation)
        return "寫出核心公式，代入已知數值後化簡得到答案。"
    return ""
