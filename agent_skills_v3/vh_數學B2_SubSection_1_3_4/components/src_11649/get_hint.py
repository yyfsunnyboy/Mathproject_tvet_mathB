from __future__ import annotations
from typing import Any
from core.gencode.b2_13_component_payload import get_b2_13_hint

def get_hint(payload: dict[str, Any] | None = None, *, stage: int = 1, **kwargs: Any) -> str:
    return get_b2_13_hint(payload, stage=stage, **kwargs)

