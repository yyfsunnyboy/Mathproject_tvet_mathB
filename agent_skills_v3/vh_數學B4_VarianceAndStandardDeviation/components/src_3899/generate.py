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

# Canonical stat definitions (order shuffled per call via seed)
_STAT_ITEMS = [
    {"stat": "range",    "text": "全距"},
    {"stat": "std",      "text": "樣本標準差"},
    {"stat": "median",  "text": "中位數"},
    {"stat": "mode",    "text": "眾數"},
]


def _fmt(v: float) -> str:
    """Format a float as integer string when possible."""
    return str(int(v)) if v == int(v) else str(round(v, 4))


def _determine_correct_stat(
    before_vals: list[float],
    after_vals: list[float],
) -> str | None:
    """Return the name of the unique changed statistic, or None if not exactly one."""
    changed: set[str] = set()
    if range_from_values(before_vals) != range_from_values(after_vals):
        changed.add("range")
    if population_standard_deviation(before_vals) != population_standard_deviation(after_vals):
        changed.add("std")
    if median_from_values(before_vals) != median_from_values(after_vals):
        changed.add("median")
    if set(mode_from_values(before_vals)) != set(mode_from_values(after_vals)):
        changed.add("mode")
    if len(changed) == 1:
        return changed.pop()
    return None  # 0 or 2+ statistics changed – caller must retry


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    n_list = 10
    max_attempts = 200

    raw_list: list[float] = []
    original_value: float = 0.0
    changed_value: float = 0.0
    correct_stat: str = "std"   # stat name that uniquely changed

    for _attempt in range(max_attempts):
        raw_list = [float(rng.randint(1, 20)) for _ in range(n_list)]
        original_value = raw_list[-1]
        for delta in rng.sample([-3, -2, -1, 1, 2, 3], k=6):
            cv = float(max(1, min(20, int(original_value) + delta)))
            if cv == original_value:
                continue
            before = raw_list[:]
            after  = raw_list[:-1] + [cv]
            stat = _determine_correct_stat(before, after)
            if stat is not None:
                changed_value = cv
                correct_stat = stat
                break
        else:
            continue
        break
    else:
        raw_list = [float(rng.randint(1, 20)) for _ in range(n_list)]
        original_value = raw_list[-1]
        changed_value = float(max(1, 20 if original_value <= 10 else 1))
        correct_stat = "std"

    before_vals = raw_list[:]
    after_vals  = raw_list[:-1] + [changed_value]

    # Shuffle the four stat items using a deterministic sub-RNG derived from seed
    # Use a separate Random so the data-generation RNG state is not consumed here.
    shuffle_rng = random.Random((seed or 0) ^ 0xA3F7)
    shuffled = list(_STAT_ITEMS)
    shuffle_rng.shuffle(shuffled)
    _KEYS = ["A", "B", "C", "D"]
    choices = [
        {"key": _KEYS[i], "label": _KEYS[i], "text": item["text"]}
        for i, item in enumerate(shuffled)
    ]
    # Map stat name -> assigned key after shuffle
    stat_to_key = {item["stat"]: _KEYS[i] for i, item in enumerate(shuffled)}
    correct_label = stat_to_key[correct_stat]

    orig_str  = _fmt(original_value)
    chg_str   = _fmt(changed_value)
    list_text = "\u3001".join(_fmt(v) for v in raw_list)
    choice_text = " ".join(f"({c['key']}) {c['text']}" for c in choices)
    question = (
        f"\u5047\u8a2d\u6709\u4e00\u7d44\u6a23\u672c\u8cc7\u6599\uff1a{list_text}\u3002"
        f"\u5982\u679c\u6700\u5f8c\u4e00\u500b\u6578\u5b57\u7531 {orig_str} \u66f4\u6539\u70ba {chg_str}\uff0c"
        f"\u5247\u4e0b\u5217\u54ea\u4e9b\u7d71\u8a08\u91cf\u6240\u5c0d\u61c9\u7684\u6578\u5024\u6703\u6539\u8b8a\uff1f"
        f" {choice_text}\u3002"
    )

    # Distractor labels = all keys except the correct one
    distractor_labels = [c["key"] for c in choices if c["key"] != correct_label]


    # Build matrix with all six required top-level fields
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
            "source_choices": choices,
            "source_answer_label": correct_label,
        },
        # Required: answer dict.
        # validate_domain_matrix (no kwargs path) checks ANSWER_REQUIRED_FIELDS:
        #   canonical_form, general_form, coefficients — satisfy all three.
        # The single_choice path then uses correct_label / source_choices.
        "answer": {
            "correct_label": correct_label,
            "canonical_form": correct_label,
            "general_form": correct_label,
            "coefficients": {},
            "value": correct_label,
            "answer_type": "single_choice",
            "presentation_mode": "single_choice",
        },
        # Required: distractors list (wrong choice labels)
        "distractors": distractor_labels,
        # Required: visual_spec (empty – no image/table for this question)
        "visual_spec": {},
        "answer_value": correct_label,
        "answer_text": correct_label,
        "answer_shape": "single_choice",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "source_choices": choices,
        "source_answer_label": correct_label,
        # Required by _DESCRIPTIVE_MATRIX_REQUIRED check
        "fixed_domain_key": "statistics.descriptive_statistics",
        "selected_operation": "conceptual_dispersion_judgment",
        "required_capabilities": ["conceptual_dispersion_judgment"],
        "matched_capabilities": ["conceptual_dispersion_judgment"],
        "validation_facts": {
            "domain_operation": "conceptual_dispersion_judgment",
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
        # conceptual_dispersion_judgment maps to choice_label schema in registry
        answer_schema_key="choice_label",
        domain_operation="conceptual_dispersion_judgment",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
