from __future__ import annotations

import random
import re
from typing import Any

from core.domain.statistics.descriptive_statistics_core import (
    population_standard_deviation,
    population_variance,
    range_from_values,
    median_from_values,
    mode_from_values,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compute_population_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 3899
DEFAULT_COMPONENT_ID = "src_3899" if TEXTBOOK_EXAMPLE_ID else ""

# Fixed choice labels (subject matter: which statistics change when one value changes)
_CHOICES = [
    {"key": "A", "label": "A", "text": "全距"},
    {"key": "B", "label": "B", "text": "樣本標準差"},
    {"key": "C", "label": "C", "text": "中位數"},
    {"key": "D", "label": "D", "text": "眾數"},
]


def _fmt(v: float) -> str:
    """Format a float as integer string when possible."""
    return str(int(v)) if v == int(v) else str(round(v, 4))


def _determine_correct_label(
    before_vals: list[float],
    after_vals: list[float],
) -> str:
    """Determine which choice label is correct based on actual statistic changes.

    Checks which statistics differ between before/after datasets.
    Returns the label of the first changed statistic matching the fixed choices.

    Choice mapping:
      A → 全距 (range)
      B → 樣本標準差 (population standard deviation — textbook uses 'sample std' phrasing)
      C → 中位數 (median)
      D → 眾數 (mode)
    """
    changed: set[str] = set()
    if range_from_values(before_vals) != range_from_values(after_vals):
        changed.add("A")
    if population_standard_deviation(before_vals) != population_standard_deviation(after_vals):
        changed.add("B")
    if median_from_values(before_vals) != median_from_values(after_vals):
        changed.add("C")
    if set(mode_from_values(before_vals)) != set(mode_from_values(after_vals)):
        changed.add("D")

    # Return the highest-priority changed label; B (standard deviation) is almost always
    # correct when a non-central, non-extreme value changes.
    for label in ("B", "A", "C", "D"):
        if label in changed:
            return label
    return "B"  # fallback: std always changes when any unique value changes


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # Generate 10 data values in realistic small-integer range
    n_list = 10
    raw_list = [float(rng.randint(1, 20)) for _ in range(n_list)]

    # original_value = raw_list[-1]  (the value that will be "changed")
    original_value = raw_list[-1]

    # changed_value: different from original, nearby, in [1, 20]
    delta = rng.choice([-2, -1, 1, 2])
    changed_value = float(max(1, min(20, int(original_value) + delta)))
    # Guarantee different (handles edge clamping)
    if changed_value == original_value:
        changed_value = float(max(1, min(20, int(original_value) - 1 if delta > 0 else int(original_value) + 1)))

    # Build before/after datasets for correct-answer computation
    before_vals = raw_list[:]                       # original list (last = original_value)
    after_vals  = raw_list[:-1] + [changed_value]   # list with last value changed

    # Build question text from fresh values
    list_text = "、".join(_fmt(v) for v in raw_list)
    orig_str  = _fmt(original_value)
    chg_str   = _fmt(changed_value)
    question  = (
        f"假設有一組樣本資料：{list_text}。"
        f"如果最後一個數字由 {orig_str} 更改為 {chg_str}，"
        f"則下列哪些統計量所對應的數值會改變？"
        f" (A) 全距 (B) 樣本標準差 (C) 中位數 (D) 眾數。"
    )

    correct_label = _determine_correct_label(before_vals, after_vals)

    # Build a minimal matrix-style dict compatible with convert_domain_matrix_to_question_payload
    matrix: dict[str, Any] = {
        "question_text": question,
        "givens": {
            "raw_values": raw_list,
            "original_value": original_value,
            "changed_value": changed_value,
            "before_values": before_vals,
            "after_values": after_vals,
            "target_measure": "standard_deviation",
            "question_text": question,
            "source_choices": _CHOICES,
            "source_answer_label": correct_label,
        },
        "answer_value": correct_label,
        "answer_text": correct_label,
        "answer_shape": "single_choice",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "validation_facts": {
            "domain_operation": "compute_population_standard_deviation",
            "target_measure": "standard_deviation",
            "formula": "population_standard_deviation",
            "variance": population_variance(before_vals),
            "standard_deviation": population_standard_deviation(before_vals),
            "answer_shape": "single_choice",
            "original_value": original_value,
            "changed_value": changed_value,
        },
        "explanation_steps": [
            f"原始資料末尾值 = {orig_str}，更改為 {chg_str}",
            f"全距變化：{_fmt(range_from_values(before_vals))} → {_fmt(range_from_values(after_vals))}",
            f"母體標準差變化：{_fmt(population_standard_deviation(before_vals))} → {_fmt(population_standard_deviation(after_vals))}",
            f"中位數變化：{_fmt(median_from_values(before_vals))} → {_fmt(median_from_values(after_vals))}",
            f"正確答案：{correct_label}",
        ],
    }

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="numeric_scalar",
        domain_operation="compute_population_standard_deviation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
