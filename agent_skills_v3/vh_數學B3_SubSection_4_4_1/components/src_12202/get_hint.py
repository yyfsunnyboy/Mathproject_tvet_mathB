from __future__ import annotations
from typing import Any

from core.domain.exponential_logarithmic_domain import hint_steps

PROBLEM_TYPE_ID = 'log_compare_values'


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = hint_steps(PROBLEM_TYPE_ID)
    idx = max(0, min(int(step) - 1, len(steps) - 1))
    return steps[idx]
