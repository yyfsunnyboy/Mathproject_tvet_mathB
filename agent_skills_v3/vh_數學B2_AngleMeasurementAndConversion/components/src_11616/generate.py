from __future__ import annotations
from typing import Any

PRESENTATION_MODE = "table_fill_in"
ANSWER_TYPE = "table"
PROBLEM_TYPE_ID = "angle_measurement_and_conversion"
TEXTBOOK_EXAMPLE_ID = 11616
DEFAULT_COMPONENT_ID = "src_11616"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    """Component blocked: source incomplete (table fill-in with 7 empty cells, no answer key in DB)."""
    raise RuntimeError("component_blocked:source_incomplete (table fill-in requires interactive schema, no answer in DB)")
