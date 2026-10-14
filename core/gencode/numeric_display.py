"""Display-only formatting for numeric values used in question stems."""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Any


def format_display_number(value: Any, *, decimal_places: int | None = None) -> str:
    """Return a compact decimal display without changing answer semantics."""
    if decimal_places is not None:
        if decimal_places < 0:
            raise ValueError("decimal_places_must_be_non_negative")
        return f"{Decimal(str(value)):.{decimal_places}f}"
    if isinstance(value, float):
        if not math.isfinite(value):
            return str(value)
        if value.is_integer():
            return str(int(value))
        return format(value, ".15g")
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return str(int(value))
        return format(value.normalize(), "f")
    return str(value)
