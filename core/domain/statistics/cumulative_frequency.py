"""Reusable cumulative-frequency helpers for statistics.frequency_distribution."""

from __future__ import annotations

from typing import Any, Literal

CumulativeDirection = Literal["below", "above"]


def build_less_than_cumulative_frequencies(class_frequencies: list[int]) -> list[int]:
    """Build below-or-equal cumulative counts from class frequencies (low-to-high)."""
    values = [max(0, int(x)) for x in class_frequencies]
    cumulative: list[int] = []
    running = 0
    for freq in values:
        running += freq
        cumulative.append(running)
    return cumulative


def build_greater_than_cumulative_frequencies(class_frequencies: list[int]) -> list[int]:
    """Build above-or-equal cumulative counts from class frequencies (high-to-low)."""
    values = [max(0, int(x)) for x in class_frequencies]
    cumulative: list[int] = []
    running = 0
    for freq in reversed(values):
        running += freq
        cumulative.append(running)
    cumulative.reverse()
    return cumulative


def recover_class_frequencies_from_cumulative(
    cumulative: list[int],
    *,
    direction: CumulativeDirection,
) -> list[int]:
    """Recover class frequencies from a monotone cumulative sequence."""
    values = [max(0, int(x)) for x in cumulative]
    if not values:
        return []
    if direction == "below":
        class_freqs: list[int] = []
        prev = 0
        for value in values:
            class_freqs.append(max(0, value - prev))
            prev = value
        return class_freqs
    class_freqs = []
    for index, value in enumerate(values):
        if index == len(values) - 1:
            class_freqs.append(value)
        else:
            class_freqs.append(max(0, value - values[index + 1]))
    return class_freqs


def cumulative_frequency_graph_points(
    class_bounds: list[str],
    cumulative: list[int],
    *,
    direction: CumulativeDirection,
) -> list[dict[str, Any]]:
    """Build polyline anchor points for a cumulative frequency graph."""
    if len(class_bounds) != len(cumulative):
        raise ValueError("class_bounds_cumulative_length_mismatch")
    points: list[dict[str, Any]] = []
    for bound, value in zip(class_bounds, cumulative, strict=True):
        points.append(
            {
                "class_bound": str(bound),
                "cumulative_count": int(value),
                "direction": direction,
            }
        )
    return points


def validate_cumulative_monotonicity(
    cumulative: list[int],
    *,
    direction: CumulativeDirection,
) -> bool:
    """Return True when cumulative values are monotone in the expected direction."""
    values = [int(x) for x in cumulative]
    if len(values) < 2:
        return True
    if direction == "below":
        return all(values[i] <= values[i + 1] for i in range(len(values) - 1))
    return all(values[i] >= values[i + 1] for i in range(len(values) - 1))


def read_cumulative_value(cumulative: list[int], index: int) -> int:
    """Read one cumulative count by class index."""
    if index < 0 or index >= len(cumulative):
        raise IndexError("cumulative_index_out_of_range")
    return int(cumulative[index])


def read_interval_frequency_from_cumulative(
    cumulative: list[int],
    low_index: int,
    high_index: int,
    *,
    direction: CumulativeDirection,
) -> int:
    """Recover interval class frequency from adjacent cumulative counts."""
    if low_index < 0 or high_index < 0 or low_index >= len(cumulative) or high_index >= len(cumulative):
        raise IndexError("cumulative_index_out_of_range")
    lo = int(cumulative[low_index])
    hi = int(cumulative[high_index])
    if direction == "below":
        return abs(hi - lo)
    return abs(lo - hi)


def lookup_cumulative_at_bound(
    points: list[dict[str, Any]],
    bound: int | float,
) -> int:
    """Read cumulative count at an upper class boundary from graph anchor points."""
    target = int(float(bound))
    for point in points:
        x_raw = point.get("x", point.get("class_bound"))
        if x_raw is None:
            continue
        if int(float(x_raw)) == target:
            y_raw = point.get("y", point.get("cumulative_count"))
            if y_raw is None:
                raise ValueError(f"cumulative_value_missing_at_bound:{bound}")
            return int(y_raw)
    raise ValueError(f"cumulative_bound_not_found:{bound}")


def infer_fail_count_from_less_than(
    points: list[dict[str, Any]],
    *,
    threshold: int | float,
) -> int:
    """Below cumulative graph: fail count equals cumulative at pass threshold."""
    return lookup_cumulative_at_bound(points, threshold)


def infer_fail_count_from_greater_than(
    points: list[dict[str, Any]],
    *,
    threshold: int | float,
    total: int,
) -> int:
    """Above cumulative graph: fail count = total - above cumulative at threshold."""
    return int(total) - lookup_cumulative_at_bound(points, threshold)


def infer_at_least_count_from_less_than(
    points: list[dict[str, Any]],
    *,
    threshold: int | float,
    total: int,
) -> int:
    """Below cumulative graph: at-least count = total - below cumulative at threshold."""
    return int(total) - lookup_cumulative_at_bound(points, threshold)


def infer_at_least_count_from_greater_than(
    points: list[dict[str, Any]],
    *,
    threshold: int | float,
) -> int:
    """Above cumulative graph: at-least count equals above cumulative at threshold."""
    return lookup_cumulative_at_bound(points, threshold)


def recover_interval_frequency_from_less_than(
    points: list[dict[str, Any]],
    *,
    low_bound: int | float,
    high_bound: int | float,
) -> int:
    """Interval [low, high) frequency from below cumulative: C(high) - C(low)."""
    return lookup_cumulative_at_bound(points, high_bound) - lookup_cumulative_at_bound(points, low_bound)


def recover_interval_frequency_from_greater_than(
    points: list[dict[str, Any]],
    *,
    low_bound: int | float,
    high_bound: int | float,
) -> int:
    """Interval [low, high) frequency from above cumulative: G(low) - G(high)."""
    return lookup_cumulative_at_bound(points, low_bound) - lookup_cumulative_at_bound(points, high_bound)


def build_bidirectional_cumulative_table(
    class_frequencies: list[int],
    class_bounds: list[str] | None = None,
) -> dict[str, Any]:
    """Build less-than and greater-than cumulative columns from class frequencies."""
    frequencies = [max(0, int(x)) for x in class_frequencies]
    less_than = build_less_than_cumulative_frequencies(frequencies)
    greater_than = build_greater_than_cumulative_frequencies(frequencies)
    return {
        "class_bounds": list(class_bounds or []),
        "class_frequencies": frequencies,
        "less_than_cumulative": less_than,
        "greater_than_cumulative": greater_than,
        "total": sum(frequencies),
    }


def validate_less_than_sequence(
    sequence: list[int],
    total: int,
) -> tuple[bool, str]:
    """Validate below cumulative: monotone increasing and terminal equals total."""
    values = [int(x) for x in sequence]
    if not values:
        return False, "empty_sequence"
    if any(v < 0 for v in values):
        return False, "negative_value"
    if not all(values[i] <= values[i + 1] for i in range(len(values) - 1)):
        return False, "not_monotone_increasing"
    if values[-1] != int(total):
        return False, "terminal_not_equal_total"
    return True, ""


def validate_greater_than_sequence(
    sequence: list[int],
    total: int,
) -> tuple[bool, str]:
    """Validate above cumulative: monotone decreasing and initial equals total."""
    values = [int(x) for x in sequence]
    if not values:
        return False, "empty_sequence"
    if any(v < 0 for v in values):
        return False, "negative_value"
    if not all(values[i] >= values[i + 1] for i in range(len(values) - 1)):
        return False, "not_monotone_decreasing"
    if values[0] != int(total):
        return False, "initial_not_equal_total"
    return True, ""
