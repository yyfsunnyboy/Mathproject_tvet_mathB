from __future__ import annotations

from typing import Any


def get_component_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    operation = str(payload.get("operation") or "")
    if step == 1:
        return "先整理兩端點、分點與線段比例，確認題目要求的是座標、重心或到原點的距離。"
    if step == 2:
        if operation == "compute_centroid_coordinates":
            return "三角形重心的兩個坐標，分別是三個頂點對應坐標的平均數。"
        return "若 AP:PB=m:n，內分點 P=(nA+mB)/(m+n)。"
    if step == 3:
        derivation = metadata.get("derivation") or []
        if derivation:
            return f"依序計算：{' → '.join(str(item) for item in derivation)}"
        return "代入坐標與比例；若要求 OP，再計算 sqrt(x_P^2+y_P^2)。"
    return ""
