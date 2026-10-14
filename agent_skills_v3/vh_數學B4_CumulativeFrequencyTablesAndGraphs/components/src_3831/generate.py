from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.cumulative_component_runtime import generate_cumulative_component_payload
from core.gencode.generated_answer_contract_alignment import align_generated_answer_to_contract

_COMPONENT_DIR = Path(__file__).resolve().parent
TEXTBOOK_EXAMPLE_ID = 3831


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    payload = generate_cumulative_component_payload(
        _COMPONENT_DIR,
        seed=seed,
        level=level,
        textbook_example_id=int(kwargs.get("textbook_example_id") or TEXTBOOK_EXAMPLE_ID),
        component_id=str(kwargs.get("component_id") or _COMPONENT_DIR.name),
    )
    return align_generated_answer_to_contract(payload)
