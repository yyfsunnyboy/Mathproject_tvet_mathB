from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    meta = (question_payload or {}).get("metadata") or {}
    if step == 1:
        return "先辨識自變數與應變數，確認這是函數求值題。"
    if step == 2:
        return "依定義域選對應公式，再代入數值。"
    if step == 3:
        der = meta.get("derivation") or []
        return " → ".join(str(x) for x in der) if der else "代入後計算差額或函數值。"
    return ""
