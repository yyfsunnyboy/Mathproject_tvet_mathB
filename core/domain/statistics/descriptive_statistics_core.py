"""Pure math core for descriptive statistics domain (population formulas)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


@dataclass
class DescriptiveDataInput:
    """Generic input model for descriptive statistics operations."""

    raw_values: list[float] = field(default_factory=list)
    value_frequency_pairs: list[tuple[float, int]] = field(default_factory=list)
    grouped_frequency_table: list[dict[str, Any]] = field(default_factory=list)
    weights: list[tuple[float, float]] = field(default_factory=list)
    target_measure: str = ""
    rounding_policy: dict[str, Any] = field(default_factory=dict)
    expected_answer_shape: str = "single_numeric"

    @property
    def expanded_values(self) -> list[float]:
        if self.raw_values:
            return [float(v) for v in self.raw_values]
        expanded: list[float] = []
        for value, freq in self.value_frequency_pairs:
            count = max(0, int(freq))
            expanded.extend([float(value)] * count)
        for row in self.grouped_frequency_table:
            midpoint = float(row.get("class_midpoint") or row.get("midpoint") or 0)
            freq = max(0, int(row.get("frequency") or row.get("count") or 0))
            expanded.extend([midpoint] * freq)
        return expanded


def _round_value(value: float, policy: dict[str, Any] | None) -> float | int:
    policy = policy or {}
    decimals = int(policy.get("decimal_places", 2))
    as_integer = bool(policy.get("prefer_integer", False))
    if as_integer and abs(value - round(value)) < 1e-9:
        return int(round(value))
    quant = Decimal(str(value)).quantize(Decimal("1." + "0" * decimals), rounding=ROUND_HALF_UP)
    if as_integer and quant == quant.to_integral_value():
        return int(quant)
    return float(quant)


def format_numeric_answer(value: float | int, policy: dict[str, Any] | None = None) -> str:
    policy = policy or {}
    rounded = _round_value(float(value), policy)
    if isinstance(rounded, int):
        return str(rounded)
    decimals = int(policy.get("decimal_places", 2))
    text = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    return text or "0"


def arithmetic_mean_from_raw(values: list[float]) -> float:
    if not values:
        raise ValueError("empty_values")
    return sum(values) / len(values)


def arithmetic_mean_from_frequency(pairs: list[tuple[float, int]]) -> float:
    total_freq = sum(max(0, int(f)) for _, f in pairs)
    if total_freq <= 0:
        raise ValueError("empty_frequency")
    weighted_sum = sum(float(v) * max(0, int(f)) for v, f in pairs)
    return weighted_sum / total_freq


def weighted_mean_from_pairs(pairs: list[tuple[float, float]]) -> float:
    total_weight = sum(float(w) for _, w in pairs)
    if total_weight <= 0:
        raise ValueError("invalid_weights")
    return sum(float(v) * float(w) for v, w in pairs) / total_weight


def median_from_values(values: list[float]) -> float:
    if not values:
        raise ValueError("empty_values")
    ordered = sorted(float(v) for v in values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def mode_from_values(values: list[float]) -> list[float]:
    if not values:
        raise ValueError("empty_values")
    counts: dict[float, int] = {}
    for value in values:
        key = float(value)
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return []
    max_count = max(counts.values())
    if max_count <= 1 and len(counts) == len(values):
        return []
    modes = sorted(k for k, c in counts.items() if c == max_count)
    return modes


def range_from_values(values: list[float]) -> float:
    if not values:
        raise ValueError("empty_values")
    return max(values) - min(values)


def _median_sorted(ordered: list[float]) -> float:
    n = len(ordered)
    if n == 0:
        raise ValueError("empty_values")
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def quartiles_from_values(values: list[float]) -> tuple[float, float, float]:
    """Return (Q1, Q3, IQR) using the inclusive median split used in TW textbooks."""
    ordered = sorted(float(v) for v in values)
    n = len(ordered)
    if n < 2:
        raise ValueError("insufficient_values")
    if n % 2 == 1:
        lower = ordered[: n // 2 + 1]
        upper = ordered[n // 2 :]
    else:
        lower = ordered[: n // 2]
        upper = ordered[n // 2 :]
    q1 = _median_sorted(lower)
    q3 = _median_sorted(upper)
    return q1, q3, q3 - q1


def range_and_iqr_summary(values: list[float], *, rounding_policy: dict[str, Any] | None = None) -> dict[str, str | float]:
    policy = dict(rounding_policy or {"decimal_places": 0, "prefer_integer": True})
    ordered = sorted(float(v) for v in values)
    r = range_from_values(ordered)
    q1, q3, iqr = quartiles_from_values(ordered)
    return {
        "range": r,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "range_text": format_numeric_answer(r, policy),
        "iqr_text": format_numeric_answer(iqr, policy),
    }


def population_variance(values: list[float]) -> float:
    if not values:
        raise ValueError("empty_values")
    mean = arithmetic_mean_from_raw(values)
    return sum((float(v) - mean) ** 2 for v in values) / len(values)


def population_standard_deviation(values: list[float]) -> float:
    return math.sqrt(population_variance(values))


def sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("insufficient_values")
    mean = arithmetic_mean_from_raw(values)
    return sum((float(v) - mean) ** 2 for v in values) / (len(values) - 1)


def sample_standard_deviation(values: list[float]) -> float:
    return math.sqrt(sample_variance(values))


def generate_raw_values(rng: random.Random, *, count: int, low: int = 1, high: int = 20) -> list[int]:
    n = max(3, int(count))
    return [rng.randint(low, high) for _ in range(n)]


def generate_frequency_pairs(rng: random.Random, *, distinct: int = 4) -> list[tuple[int, int]]:
    values = sorted({rng.randint(1, 15) for _ in range(max(2, distinct))})
    freqs = [rng.randint(1, 5) for _ in values]
    return list(zip(values, freqs, strict=True))


def generate_weighted_pairs(rng: random.Random, *, subjects: int = 4) -> list[tuple[int, int]]:
    labels = list(range(subjects))
    weights = [rng.randint(2, 6) for _ in labels]
    scores = [rng.randint(60, 95) for _ in labels]
    return list(zip(scores, weights, strict=True))


def build_numeric_distractor_candidates(
    correct_value: float | int | str,
    *,
    rounding_policy: dict[str, Any] | None = None,
    auxiliary_values: list[float] | None = None,
    max_distractors: int = 3,
) -> list[str]:
    """Produce plausible wrong numeric options for descriptive-statistics MC items."""
    policy = dict(rounding_policy or {"decimal_places": 0, "prefer_integer": True})
    try:
        numeric = float(correct_value)
    except (TypeError, ValueError):
        return []

    canonical = format_numeric_answer(numeric, policy)
    candidates: list[str] = []
    seen = {canonical.casefold()}

    def _add(value: float) -> None:
        text = format_numeric_answer(value, policy)
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            candidates.append(text)

    if math.isfinite(numeric):
        if abs(numeric - round(numeric)) < 1e-9:
            base = int(round(numeric))
            for delta in (1, -1, 2, -2, 3, -3):
                _add(float(base + delta))
        else:
            step = 10 ** (-int(policy.get("decimal_places", 1) or 1))
            for delta in (step, -step, step * 2, -step * 2, 0.5, -0.5):
                _add(numeric + delta)

        if auxiliary_values:
            for raw in auxiliary_values:
                try:
                    value = float(raw)
                except (TypeError, ValueError):
                    continue
                if abs(value - numeric) < 1e-9:
                    continue
                _add(value)

        total = sum(float(v) for v in (auxiliary_values or []) if isinstance(v, (int, float)))
        count = len([v for v in (auxiliary_values or []) if isinstance(v, (int, float))])
        if count > 1 and total:
            _add(total)
            _add(total / max(1, count - 1))

    return candidates[: max(1, int(max_distractors))]


def empirical_rule_central_probability(k: float | int) -> float:
    k_abs = abs(k)
    if abs(k_abs - 1) < 1e-9:
        return 0.68
    elif abs(k_abs - 2) < 1e-9:
        return 0.95
    elif abs(k_abs - 3) < 1e-9:
        return 0.997
    raise ValueError(f"Unsupported standard deviation multiplier k={k}")


def empirical_rule_one_tail_probability(k: float | int) -> float:
    central_prob = empirical_rule_central_probability(k)
    return round((1.0 - central_prob) / 2.0, 5)


def empirical_rule_cumulative_probability(k: float | int, direction: str) -> float:
    k_val = float(k)
    if abs(k_val) < 1e-9:
        return 0.5
    
    central_prob = empirical_rule_central_probability(k_val)
    half_central = central_prob / 2.0
    
    if direction == "below":
        if k_val > 0:
            prob = 0.5 + half_central
        else:
            prob = 0.5 - half_central
    elif direction == "above":
        if k_val > 0:
            prob = 0.5 - half_central
        else:
            prob = 0.5 + half_central
    else:
        raise ValueError(f"Unknown direction: {direction}")
    
    return round(prob, 5)


def population_count_from_probability(total: float | int, probability: float) -> int:
    return int(round(total * probability))

