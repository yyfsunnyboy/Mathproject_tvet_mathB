"""Statistics domain functions for frequency-distribution-table construction."""

from __future__ import annotations

import random
from typing import Any


def build_frequency_distribution_table_matrix(
    *,
    seed: int | None = None,
    domain_operation: str = "frequency_table_construction_review",
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build a reusable Full Matrix Dictionary for frequency table construction."""
    rng = random.Random(seed)
    constraints = dict(constraints or {})
    categories = list(constraints.get("categories") or ["A組", "B組", "C組", "D組"])
    if len(categories) < 3:
        raise ValueError("categories_must_have_at_least_three_items")
    frequencies = constraints.get("frequencies")
    if frequencies is None:
        frequencies = [rng.randint(3, 9) for _ in categories]
    frequencies = [int(x) for x in frequencies]
    if len(frequencies) != len(categories):
        raise ValueError("frequencies_length_mismatch")
    if any(x < 0 for x in frequencies):
        raise ValueError("frequency_must_be_non_negative")

    frequency_map = dict(zip(categories, frequencies, strict=True))
    target_label = str(constraints.get("target_label") or rng.choice(categories))
    if target_label not in frequency_map:
        target_label = categories[0]
    answer_value = frequency_map[target_label]
    total = sum(frequencies)

    distractor_values: list[int] = []
    for candidate in (answer_value + 1, answer_value - 1, total, max(frequencies), min(frequencies)):
        if candidate >= 0 and candidate != answer_value and candidate not in distractor_values:
            distractor_values.append(candidate)
    while len(distractor_values) < 3:
        candidate = rng.randint(0, max(total, 3))
        if candidate != answer_value and candidate not in distractor_values:
            distractor_values.append(candidate)

    return {
        "givens": {
            "categories": categories,
            "frequencies": frequencies,
            "frequency_map": frequency_map,
            "target_label": target_label,
            "total_frequency": total,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "answer": {
            "canonical_form": str(answer_value),
            "general_form": str(answer_value),
            "coefficients": {"frequency": answer_value},
            "value": answer_value,
            "unit": "次",
        },
        "distractors": [str(x) for x in distractor_values[:3]],
        "explanation_steps": [
            "依資料分類整理各組出現次數。",
            f"查看 {target_label} 的次數。",
            f"{target_label} 的次數為 {answer_value}。",
        ],
        "validation_facts": {
            "domain_operation": domain_operation,
            "task_type": domain_operation,
            "frequency_map": frequency_map,
            "target_label": target_label,
            "answer_value": answer_value,
            "total_frequency": total,
        },
        "visual_spec": {
            "type": "table",
            "title": "次數分配表",
            "headers": ["組別", "次數"],
            "rows": [[label, frequency_map[label]] for label in categories],
        },
    }
