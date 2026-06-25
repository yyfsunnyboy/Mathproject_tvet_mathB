"""Statistics domain functions for reusable table/chart reading tasks."""

from __future__ import annotations

import base64
import io
import random
from typing import Any

_CUMULATIVE_OPS = frozenset(
    {
        "cumulative_above_fail_count",
        "cumulative_above_interval_count",
        "cumulative_below_interval_count",
    }
)


def _default_categories() -> list[str]:
    return ["A", "B", "C", "D"]


def _render_cumulative_polygon_png(
    *,
    marks: list[int],
    cumulative_values: list[int],
    title: str,
    x_label: str,
    y_label: str,
    direction: str,
) -> str:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.5, 4.0), dpi=120)
    try:
        dir_label = "以上累積次數" if direction == "above" else "以下累積次數"
        ax.plot(marks, cumulative_values, marker="o", color="#2563eb", linewidth=2)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(f"{dir_label}（人）", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        return base64.b64encode(buf.getvalue()).decode("ascii")
    finally:
        plt.close(fig)


def _random_positive_partition(rng: random.Random, total: int, parts: int) -> list[int]:
    if parts <= 0:
        raise ValueError("parts_must_be_positive")
    if total < parts:
        raise ValueError("total_too_small_for_parts")
    if parts == 1:
        return [total]
    cut_points = sorted(rng.sample(range(1, total), parts - 1))
    values: list[int] = []
    prev = 0
    for point in cut_points:
        values.append(point - prev)
        prev = point
    values.append(total - prev)
    return values


def _build_cumulative_frequency_polygon_matrix(
    *,
    rng: random.Random,
    constraints: dict[str, Any],
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
) -> dict[str, Any]:
    direction = str(constraints.get("cumulative_direction") or "above").strip()
    if domain_operation == "cumulative_below_interval_count":
        direction = "below"
    elif domain_operation in {"cumulative_above_fail_count", "cumulative_above_interval_count"}:
        direction = "above"

    story = str(constraints.get("story_context") or "統計資料")
    unit = str(constraints.get("variable_unit") or "")
    x_label = f"成績（{unit}）" if unit == "分" else f"年齡（{unit}）" if unit == "歲" else "組界"

    total = int(constraints.get("total_population") or rng.randint(30, 50))
    marks = list(constraints.get("class_marks") or [])
    if not marks:
        if unit == "分":
            marks = [40, 50, 60, 70, 80, 90, 100]
        elif unit == "歲":
            marks = [20, 30, 40, 50, 60]
        else:
            marks = [10, 20, 30, 40, 50]

    frequencies = list(constraints.get("class_frequencies") or [])
    if not frequencies:
        frequencies = _random_positive_partition(rng, total, len(marks))
    frequencies = [max(0, int(x)) for x in frequencies]
    if len(frequencies) != len(marks):
        raise ValueError("class_frequencies_length_mismatch")
    if sum(frequencies) != total:
        frequencies = _random_positive_partition(rng, total, len(marks))

    if direction == "above":
        cumulative: list[int] = []
        running = total
        for freq in frequencies:
            cumulative.append(running)
            running -= freq
    else:
        cumulative = []
        running = 0
        for freq in frequencies:
            running += freq
            cumulative.append(running)

    mark_to_cum = dict(zip(marks, cumulative, strict=True))

    if domain_operation == "cumulative_above_fail_count":
        threshold = int(constraints.get("threshold") or 60)
        cum_at_threshold = mark_to_cum.get(threshold)
        if cum_at_threshold is None:
            threshold = min(marks, key=lambda m: abs(m - threshold))
            cum_at_threshold = mark_to_cum[threshold]
        answer_value = total - cum_at_threshold
        question_focus = f"以{threshold}{unit}為準，不及格者有多少人"
        explanation_steps = [
            f"讀取折線圖在 {threshold}{unit} 處的以上累積次數為 {cum_at_threshold} 人（及格人數）。",
            f"全班共 {total} 人，不及格人數 = {total} − {cum_at_threshold} = {answer_value} 人。",
        ]
        task_kind = "fail_count_below_threshold"
    else:
        interval_low = int(constraints.get("interval_low") or (70 if unit == "分" else 30))
        interval_high = int(constraints.get("interval_high") or (80 if unit == "分" else 40))
        low_mark = min(marks, key=lambda m: abs(m - interval_low))
        high_mark = min(marks, key=lambda m: abs(m - interval_high))
        if direction == "above":
            answer_value = mark_to_cum[low_mark] - mark_to_cum[high_mark]
            explanation_steps = [
                f"讀取 {interval_low}{unit} 的以上累積次數：{mark_to_cum[low_mark]} 人。",
                f"讀取 {interval_high}{unit} 的以上累積次數：{mark_to_cum[high_mark]} 人。",
                f"介於 {interval_low}～{interval_high}{unit} 的人數 = {mark_to_cum[low_mark]} − {mark_to_cum[high_mark]} = {answer_value} 人。",
            ]
        else:
            answer_value = mark_to_cum[high_mark] - mark_to_cum[low_mark]
            explanation_steps = [
                f"讀取 {interval_high}{unit} 的以下累積次數：{mark_to_cum[high_mark]} 人。",
                f"讀取 {interval_low}{unit} 的以下累積次數：{mark_to_cum[low_mark]} 人。",
                f"介於 {interval_low}～{interval_high}{unit} 的人數 = {mark_to_cum[high_mark]} − {mark_to_cum[low_mark]} = {answer_value} 人。",
            ]
        question_focus = f"{interval_low}～{interval_high}{unit}有多少人"
        task_kind = "interval_count"

    chart_title = f"{story}的{'以上' if direction == 'above' else '以下'}累積次數分配折線圖"
    image_b64 = _render_cumulative_polygon_png(
        marks=marks,
        cumulative_values=cumulative,
        title=chart_title,
        x_label=x_label,
        y_label="人數",
        direction=direction,
    )
    dir_label = "以上累積次數" if direction == "above" else "以下累積次數"
    table_rows = [[str(m), cumulative[i]] for i, m in enumerate(marks)]
    distractors = _numeric_distractors(answer_value, frequencies, total)

    return {
        "givens": {
            "story_context": story,
            "variable_unit": unit,
            "total_population": total,
            "class_marks": marks,
            "class_frequencies": frequencies,
            "cumulative_direction": direction,
            "cumulative_map": mark_to_cum,
            "cumulative_values": cumulative,
            "task_kind": task_kind,
            "question_focus": question_focus,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "answer": {
            "canonical_form": str(answer_value),
            "general_form": str(answer_value),
            "coefficients": {"value": answer_value},
            "value": answer_value,
            "unit": "人",
        },
        "distractors": distractors,
        "explanation_steps": explanation_steps,
        "validation_facts": {
            "domain_operation": domain_operation,
            "task_type": domain_operation,
            "cumulative_direction": direction,
            "total_population": total,
            "class_marks": marks,
            "cumulative_map": mark_to_cum,
            "answer_value": answer_value,
            "task_kind": task_kind,
        },
        "visual_spec": {
            "type": "cumulative_frequency_polygon",
            "direction": direction,
            "title": chart_title,
            "headers": [x_label, dir_label],
            "rows": table_rows,
            "marks": marks,
            "cumulative_values": cumulative,
        },
        "visual_aids": [{"type": "image/png", "value": image_b64}],
        "image_base64": image_b64,
    }


def build_statistical_chart_reading_matrix(
    *,
    seed: int | None = None,
    domain_operation: str = "read_category_value",
    line_type: str | None = None,
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build reusable facts for reading and reasoning about simple statistical charts."""
    rng = random.Random(seed)
    constraints = dict(constraints or {})
    operation = str(line_type or domain_operation or "read_category_value").strip()
    if operation in _CUMULATIVE_OPS:
        return _build_cumulative_frequency_polygon_matrix(
            rng=rng,
            constraints=constraints,
            domain_operation=operation,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
        )

    categories = [str(x) for x in (constraints.get("categories") or _default_categories())]
    if len(categories) < 2:
        raise ValueError("categories_must_have_at_least_two_items")

    values = constraints.get("values")
    if values is None:
        values = [rng.randint(5, 24) for _ in categories]
    values = [int(x) for x in values]
    if len(values) != len(categories):
        raise ValueError("values_length_mismatch")
    if any(v < 0 for v in values):
        raise ValueError("chart_values_must_be_non_negative")

    value_map = dict(zip(categories, values, strict=True))
    total = sum(values)
    target_label = str(constraints.get("target_label") or rng.choice(categories))
    if target_label not in value_map:
        target_label = categories[0]
    compare_a = str(constraints.get("compare_a") or categories[0])
    compare_b = str(constraints.get("compare_b") or categories[1])
    if compare_a not in value_map or compare_b not in value_map or compare_a == compare_b:
        compare_a, compare_b = categories[0], categories[1]

    statement = ""
    if operation == "compare_category_values":
        diff = abs(value_map[compare_a] - value_map[compare_b])
        larger = compare_a if value_map[compare_a] >= value_map[compare_b] else compare_b
        answer_value: int | str = diff
        canonical = str(diff)
        explanation_steps = [
            f"Read {compare_a} as {value_map[compare_a]} and {compare_b} as {value_map[compare_b]}.",
            f"{larger} is larger; the difference is {diff}.",
        ]
    elif operation == "calculate_total_ratio_percent":
        percent = 0 if total == 0 else round(value_map[target_label] / total * 100, 2)
        answer_value = percent
        canonical = str(percent)
        explanation_steps = [
            f"Add all category values to get total {total}.",
            f"{target_label} has value {value_map[target_label]}, so its percentage is {percent}%.",
        ]
    elif operation == "validate_chart_statement":
        stated_label = str(constraints.get("statement_label") or target_label)
        stated_value = int(constraints.get("statement_value") or value_map[stated_label])
        statement = f"{stated_label} has value {stated_value}."
        answer_value = stated_value == value_map[stated_label]
        canonical = "true" if answer_value else "false"
        explanation_steps = [
            f"Read {stated_label} directly from the chart as {value_map[stated_label]}.",
            f"The statement is {'correct' if answer_value else 'incorrect'}.",
        ]
    else:
        operation = "read_category_value"
        answer_value = value_map[target_label]
        canonical = str(answer_value)
        explanation_steps = [
            f"Locate category {target_label} in the table or chart.",
            f"The corresponding value is {answer_value}.",
        ]

    distractors = _numeric_distractors(answer_value, values, total)

    return {
        "givens": {
            "categories": categories,
            "values": values,
            "value_map": value_map,
            "target_label": target_label,
            "compare_a": compare_a,
            "compare_b": compare_b,
            "total": total,
            "statement": statement,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "answer": {
            "canonical_form": canonical,
            "general_form": canonical,
            "coefficients": {"value": answer_value} if isinstance(answer_value, (int, float)) else {},
            "value": answer_value,
            "unit": str(constraints.get("unit") or ""),
        },
        "distractors": distractors,
        "explanation_steps": explanation_steps,
        "validation_facts": {
            "domain_operation": operation,
            "task_type": operation,
            "value_map": value_map,
            "target_label": target_label,
            "compare_a": compare_a,
            "compare_b": compare_b,
            "total": total,
            "answer_value": answer_value,
            "statement": statement,
        },
        "visual_spec": {
            "type": str(constraints.get("chart_type") or "table_chart"),
            "title": str(constraints.get("title") or "Statistical chart"),
            "headers": ["category", "value"],
            "rows": [[label, value_map[label]] for label in categories],
        },
    }


def _numeric_distractors(answer_value: int | float | str | bool, values: list[int], total: int) -> list[str]:
    if isinstance(answer_value, bool):
        return ["false" if answer_value else "true", str(total), str(max(values) if values else 0)]
    if not isinstance(answer_value, (int, float)):
        return [str(total), str(max(values) if values else 0), str(min(values) if values else 0)]

    candidates: list[int | float] = []
    for candidate in (
        total,
        max(values) if values else 0,
        min(values) if values else 0,
        answer_value + 1,
        max(0, answer_value - 1),
        answer_value + 2,
    ):
        if candidate != answer_value and candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) >= 3:
            break
    while len(candidates) < 3:
        filler = answer_value + len(candidates) + 3
        if filler != answer_value and filler not in candidates:
            candidates.append(filler)
    return [str(x) for x in candidates[:3]]
