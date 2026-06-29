"""Statistics domain functions for frequency-distribution-table construction."""

from __future__ import annotations

import random
import re
from typing import Any

from core.domain.statistics.cumulative_frequency import (
    build_bidirectional_cumulative_table,
    build_greater_than_cumulative_frequencies,
    build_less_than_cumulative_frequencies,
    cumulative_frequency_graph_points,
    infer_at_least_count_from_greater_than,
    infer_at_least_count_from_less_than,
    infer_fail_count_from_greater_than,
    infer_fail_count_from_less_than,
    lookup_cumulative_at_bound,
    read_cumulative_value,
    read_interval_frequency_from_cumulative,
    recover_class_frequencies_from_cumulative,
    recover_interval_frequency_from_greater_than,
    recover_interval_frequency_from_less_than,
    validate_cumulative_monotonicity,
    validate_greater_than_sequence,
    validate_less_than_sequence,
)
from core.domain.statistics.cumulative_frequency_renderer import (
    render_cumulative_frequency_graph,
    render_cumulative_frequency_table,
)

_CUMULATIVE_OPERATIONS = frozenset(
    {
        "cumulative_frequency_table_construction",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
        "class_frequency_from_cumulative_difference",
        "cumulative_frequency_graph_reading",
    }
)


def _threshold_from_subquestion(sq: dict[str, Any], default: int) -> int:
    if sq.get("threshold") is not None:
        return int(sq["threshold"])
    if sq.get("bound") is not None:
        return int(sq["bound"])
    inference = str(sq.get("inference") or "")
    match = re.search(r"_at_(\d+)", inference)
    if match:
        return int(match.group(1))
    return default


def _merge_constraints(constraints: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(constraints or {})
    nested = merged.get("domain_constraints")
    if isinstance(nested, dict):
        base = dict(nested)
        base.update({k: v for k, v in merged.items() if k != "domain_constraints"})
        return base
    return merged


def _normalize_direction_key(raw: str) -> str:
    key = str(raw or "").strip().lower()
    if key in {"below", "less_than", "以下"}:
        return "below"
    if key in {"above", "greater_than", "以上"}:
        return "above"
    if key == "both":
        return "both"
    return key


def _graph_points_from_constraints(constraints: dict[str, Any]) -> list[dict[str, Any]]:
    if constraints.get("graph_points"):
        return [
            {
                "class_bound": p.get("class_bound", p.get("x")),
                "cumulative_count": p.get("cumulative_count", p.get("y")),
                "x": p.get("x", p.get("class_bound")),
                "y": p.get("y", p.get("cumulative_count")),
            }
            for p in constraints["graph_points"]
        ]
    if constraints.get("data_points"):
        return [
            {
                "class_bound": p.get("x"),
                "cumulative_count": p.get("y"),
                "x": p.get("x"),
                "y": p.get("y"),
            }
            for p in constraints["data_points"]
        ]
    return []


def _infer_task_topology(domain_operation: str, constraints: dict[str, Any]) -> str:
    explicit = str(constraints.get("task_topology") or "").strip()
    if explicit:
        return explicit
    if constraints.get("cumulative_table_blank_fill") or constraints.get("task_topology") == "cumulative_table_blank_fill":
        return "cumulative_table_blank_fill"
    render_mode = str(constraints.get("render_mode") or "").strip().lower()
    direction = _normalize_direction_key(str(constraints.get("cumulative_direction") or ""))
    if render_mode == "fill_table" or direction == "both":
        return "bidirectional_table"
    if render_mode == "multiple_choice" or constraints.get("presentation_mode") == "single_choice":
        return "graph_mcq"
    if domain_operation == "class_frequency_from_cumulative_difference":
        return "interval_difference"
    if constraints.get("sub_questions") or render_mode == "multi_part":
        if direction == "above":
            return "above_graph_multi_part"
        return "below_graph_multi_part"
    if domain_operation == "cumulative_frequency_table_construction":
        return "bidirectional_table"
    if domain_operation == "greater_than_cumulative_frequency_reading":
        return "above_graph_multi_part"
    if domain_operation in {"less_than_cumulative_frequency_reading", "cumulative_frequency_graph_reading"}:
        return "below_graph_multi_part"
    return "below_graph_multi_part"


def _default_score_bounds(rng: random.Random) -> list[str]:
  del rng
  return ["40~50", "50~60", "60~70", "70~80", "80~90", "90~100"]


def _default_score_marks() -> list[int]:
    return [40, 50, 60, 70, 80, 90, 100]


def _ensure_class_frequencies(
    rng: random.Random,
    class_bounds: list[str],
    constraints: dict[str, Any],
) -> list[int]:
    class_frequencies = constraints.get("class_frequencies") or constraints.get("frequencies")
    if class_frequencies is not None:
        return [int(x) for x in class_frequencies]
    total = int(constraints.get("total_students") or rng.randint(30, 50))

    class_count = len(class_bounds)
    minimum_total = class_count * 1
    if total < minimum_total:
        from core.exceptions import RetryableSamplingError
        raise RetryableSamplingError(
            f"Sampling constraints unsatisfied: total_students={total} is less than minimum_total={minimum_total} for class_count={class_count}",
            total_students=total,
            class_count=class_count,
            minimum_total=minimum_total,
            operation="_ensure_class_frequencies",
        )

    raw = [rng.randint(2, 9) for _ in class_bounds]
    scale = total / max(1, sum(raw))
    freqs = [max(1, int(round(x * scale))) for x in raw]
    
    attempts = 0
    while sum(freqs) != total and attempts < 100:
        attempts += 1
        idx = rng.randrange(len(freqs))
        if sum(freqs) < total:
            freqs[idx] += 1
        elif freqs[idx] > 1:
            freqs[idx] -= 1

    if sum(freqs) != total:
        from core.exceptions import RetryableSamplingError
        raise RetryableSamplingError(
            f"Failed to adjust frequencies to total: sum(freqs)={sum(freqs)} != total={total} after {attempts} attempts",
            total_students=total,
            class_count=class_count,
            minimum_total=minimum_total,
            operation="_ensure_class_frequencies",
        )
    return freqs


def _build_render_points(
    *,
    class_bounds: list[str],
    class_frequencies: list[int],
    direction_key: str,
    constraints: dict[str, Any],
) -> list[dict[str, Any]]:
    provided = _graph_points_from_constraints(constraints)
    if provided:
        return provided
    if direction_key == "above":
        cumulative = build_greater_than_cumulative_frequencies(class_frequencies)
    else:
        cumulative = build_less_than_cumulative_frequencies(class_frequencies)
    marks = list(constraints.get("class_marks") or _default_score_marks())
    if len(marks) != len(cumulative):
        marks = list(range(40, 40 + 10 * len(cumulative), 10))
    return [
        {"class_bound": marks[i], "cumulative_count": cumulative[i], "x": marks[i], "y": cumulative[i]}
        for i in range(len(cumulative))
    ]


def _integer_distractors(correct: int, rng: random.Random, count: int = 3) -> list[int]:
    options = {int(correct)}
    attempts = 0
    while len(options) < count + 1 and attempts < 50:
        delta = rng.randint(-8, 8)
        if delta == 0:
            delta = rng.choice([-3, 3, 5, -5])
        candidate = max(0, int(correct) + delta)
        options.add(candidate)
        attempts += 1
    return sorted(x for x in options if x != int(correct))[:count]


def _build_matrix_shell(
    *,
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
    givens: dict[str, Any],
    answer_value: Any,
    answer_type: str,
    explanation_steps: list[str],
    validation_facts: dict[str, Any],
    visual_spec: dict[str, Any],
    question_text: str,
    image_base64: str = "",
    table_data: dict[str, Any] | None = None,
    choices: list[dict[str, str]] | None = None,
    subquestions: list[dict[str, Any]] | None = None,
    distractors: list[Any] | None = None,
    visual_aids: list[Any] | None = None,
    ui_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    explanation = " ".join(str(step) for step in explanation_steps)
    if isinstance(answer_value, list):
        canonical = ",".join(str(x) for x in answer_value)
    elif isinstance(answer_value, dict):
        canonical = str(answer_value)
    else:
        canonical = str(answer_value)
    coefficients: dict[str, Any] = {}
    if isinstance(answer_value, int):
        coefficients = {"frequency": answer_value}
    return {
        "question_text": question_text,
        "answer": {
            "canonical_form": canonical,
            "general_form": canonical,
            "coefficients": coefficients,
            "value": answer_value,
        },
        "answer_type": answer_type,
        "explanation": explanation,
        "problem_type_id": domain_operation,
        "domain_operation": domain_operation,
        "visual_spec": visual_spec,
        "image_base64": image_base64,
        "table_data": table_data or {},
        "visual_aids": visual_aids or [],
        "choices": choices or [],
        "subquestions": subquestions or [],
        "ui_contract": ui_contract or {},
        "givens": givens,
        "distractors": distractors or [],
        "explanation_steps": explanation_steps,
        "validation_facts": validation_facts,
    }


def _build_cumulative_table_blank_fill_matrix(
    *,
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Table with labeled blank cells (e.g. a,b,c,d) and below-cumulative semantics."""
    table_rows = list(constraints.get("table_rows") or [])
    if not table_rows:
        raise ValueError("table_rows_required_for_blank_fill")
    blank_fields = [str(x) for x in (constraints.get("blank_fields") or constraints.get("blank_variables") or [])]
    expected = dict(constraints.get("expected_answers") or {})
    headers = list(
        constraints.get("table_columns")
        or ["成績(分)", "次數(人)", "以下累積次數(人)"]
    )
    total = int(constraints.get("total_students") or expected.get("d") or 40)
    blank_cells: list[tuple[int, int]] = []
    for row_idx, row in enumerate(table_rows):
        for col_idx, cell in enumerate(row):
            if str(cell) in blank_fields:
                blank_cells.append((row_idx, col_idx))

    table_render = render_cumulative_frequency_table(
        headers=headers,
        rows=table_rows,
        blank_cells=blank_cells,
        title="次數分配表與以下累積次數分配表",
    )
    subquestions: list[dict[str, Any]] = []
    part_answers: list[int] = []
    explanation_steps: list[str] = []
    for var in blank_fields:
        value = int(expected[var])
        part_answers.append(value)
        subquestions.append(
            {
                "part": var,
                "prompt": f"求 {var} 的值",
                "expected_answer": value,
                "unit": "人",
            }
        )
    if "a" in expected:
        explanation_steps.append(f"a = 以下累積(40) - 以下累積(20) = 12 - 4 = {expected['a']}。")
    if "b" in expected:
        explanation_steps.append(f"b = 以下累積(60) = 4 + {expected.get('a', 'a')} + 10 = {expected['b']}。")
    if "c" in expected:
        explanation_steps.append(f"c = 總數 - 以下累積(80) = {total} - 34 = {expected['c']}。")
    if "d" in expected:
        explanation_steps.append(f"d = 總數 = {expected['d']}。")

    question_text = str(
        constraints.get("question_text")
        or "依下表完成次數分配表與以下累積次數分配表，試求 a, b, c, d。"
    )
    validation_facts = {
        "domain_operation": domain_operation,
        "task_topology": "cumulative_table_blank_fill",
        "cumulative_direction": "below",
        "blank_fields": blank_fields,
        "expected_answers": expected,
        "answer_value": part_answers,
        "total_students": total,
    }
    return _build_matrix_shell(
        domain_operation=domain_operation,
        curriculum_profile=curriculum_profile,
        difficulty_profile=difficulty_profile,
        givens={
            "table_rows": table_rows,
            "blank_fields": blank_fields,
            "total_students": total,
            "cumulative_direction": "below",
        },
        answer_value=part_answers,
        answer_type="multi_part",
        explanation_steps=explanation_steps,
        validation_facts=validation_facts,
        visual_spec=table_render["visual_spec"],
        question_text=question_text,
        table_data=table_render["table_data"],
        subquestions=subquestions,
        ui_contract={"response_mode": "multi_part", "text_input_enabled": True},
    )


def build_cumulative_frequency_matrix(
    *,
    seed: int | None = None,
    domain_operation: str = "cumulative_frequency_table_construction",
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build cumulative-frequency matrices with deterministic renderer output."""
    rng = random.Random(seed)
    constraints = _merge_constraints(constraints)
    topology = _infer_task_topology(domain_operation, constraints)
    if topology == "cumulative_table_blank_fill":
        return _build_cumulative_table_blank_fill_matrix(
            domain_operation=domain_operation,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            constraints=constraints,
        )

    class_bounds = list(
        constraints.get("class_bounds")
        or constraints.get("categories")
        or _default_score_bounds(rng)
    )
    if len(class_bounds) < 3:
        raise ValueError("class_bounds_must_have_at_least_three_items")

    class_frequencies = _ensure_class_frequencies(rng, class_bounds, constraints)
    if len(class_frequencies) != len(class_bounds):
        raise ValueError("class_frequencies_length_mismatch")

    direction_raw = str(constraints.get("cumulative_direction") or "").strip().lower()
    if domain_operation in {
        "less_than_cumulative_frequency_reading",
        "cumulative_frequency_graph_reading",
    } and not direction_raw:
        direction_raw = "below"
    if domain_operation == "greater_than_cumulative_frequency_reading" and not direction_raw:
        direction_raw = "above"
    if domain_operation == "cumulative_frequency_table_construction" and not direction_raw:
        direction_raw = "both"

    direction_key = _normalize_direction_key(direction_raw or "below")
    story = str(constraints.get("story_context") or "某班學生")
    unit = str(constraints.get("variable_unit") or "分")
    total = int(constraints.get("total_students") or sum(class_frequencies))

    bidirectional = build_bidirectional_cumulative_table(class_frequencies, class_bounds)
    less_than = bidirectional["less_than_cumulative"]
    greater_than = bidirectional["greater_than_cumulative"]

    if topology == "bidirectional_table":
        headers = list(
            constraints.get("table_columns")
            or ["成績(分)", "次數(人)", "以下累積次數(人)", "以上累積次數(人)"]
        )
        rows = [
            [class_bounds[i], class_frequencies[i], less_than[i], greater_than[i]]
            for i in range(len(class_bounds))
        ]
        blank_cells = [(i, 2) for i in range(len(class_bounds))] + [(i, 3) for i in range(len(class_bounds))]
        table_render = render_cumulative_frequency_table(
            headers=headers,
            rows=rows,
            blank_cells=blank_cells,
            title="累積次數分配表",
        )
        subquestions = []
        for i, bound in enumerate(class_bounds):
            subquestions.append(
                {
                    "part": f"lt_{i + 1}",
                    "prompt": f"{bound} 的以下累積次數",
                    "expected_answer": less_than[i],
                    "unit": "人",
                }
            )
            subquestions.append(
                {
                    "part": f"gt_{i + 1}",
                    "prompt": f"{bound} 的以上累積次數",
                    "expected_answer": greater_than[i],
                    "unit": "人",
                }
            )
        answer_value = {
            "less_than_cumulative": less_than,
            "greater_than_cumulative": greater_than,
        }
        question_text = str(
            constraints.get("question_text")
            or "試完成下方之累積次數分配表。"
        )
        explanation_steps = [
            "依各組次數由低到高累加，得到以下累積次數。",
            "依各組次數由高到低累加，得到以上累積次數。",
            f"總次數為 {total}，最後一列以下累積與第一列以上累積皆應等於 {total}。",
        ]
        validation_facts = {
            "domain_operation": domain_operation,
            "task_topology": topology,
            "cumulative_direction": "both",
            "class_frequencies": class_frequencies,
            "less_than_cumulative": less_than,
            "greater_than_cumulative": greater_than,
            "answer_value": answer_value,
            "total_students": total,
        }
        return _build_matrix_shell(
            domain_operation=domain_operation,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            givens={
                "class_bounds": class_bounds,
                "class_frequencies": class_frequencies,
                "cumulative_direction": "both",
                "total_students": total,
                "curriculum_profile": curriculum_profile,
                "difficulty_profile": difficulty_profile,
            },
            answer_value=answer_value,
            answer_type="multi_part",
            explanation_steps=explanation_steps,
            validation_facts=validation_facts,
            visual_spec=table_render["visual_spec"],
            question_text=question_text,
            table_data=table_render["table_data"],
            subquestions=subquestions,
            ui_contract={"response_mode": "multi_part", "text_input_enabled": True},
        )

    if direction_key == "above":
        cumulative = greater_than
        render_direction = "greater_than"
        chart_phrase = "以上累積次數分配折線圖"
    else:
        cumulative = less_than
        render_direction = "less_than"
        chart_phrase = "以下累積次數分配折線圖"

    graph_points = _build_render_points(
        class_bounds=class_bounds,
        class_frequencies=class_frequencies,
        direction_key=direction_key,
        constraints=constraints,
    )
    if constraints.get("total_students"):
        total = int(constraints["total_students"])
    elif direction_key == "below" and graph_points:
        total = int(graph_points[-1].get("cumulative_count", graph_points[-1].get("y", total)))
    elif direction_key == "above" and graph_points:
        total = int(graph_points[0].get("cumulative_count", graph_points[0].get("y", total)))

    cumulative_values = [int(p["cumulative_count"]) for p in graph_points]
    if direction_key == "below":
        ok, reason = validate_less_than_sequence(cumulative_values, total)
    else:
        ok, reason = validate_greater_than_sequence(cumulative_values, total)
    if not ok:
        raise ValueError(f"cumulative_sequence_invalid:{reason}")

    x_ticks = [float(p["x"]) for p in graph_points]
    y_ticks = sorted(set(cumulative_values))
    graph_render = render_cumulative_frequency_graph(
        data_points=graph_points,
        cumulative_direction=render_direction,
        title=chart_phrase,
        x_label=f"成績（{unit}）",
        x_ticks=x_ticks,
        y_ticks=y_ticks,
        seed=seed,
    )
    image_base64 = graph_render["image_base64"]
    visual_spec = graph_render["visual_spec"]

    if topology == "interval_difference":
        low_bound = int(constraints.get("low_bound") or constraints.get("interval_low") or 70)
        high_bound = int(constraints.get("high_bound") or constraints.get("interval_high") or 80)
        if direction_key == "below":
            answer_value = recover_interval_frequency_from_less_than(
                graph_points, low_bound=low_bound, high_bound=high_bound
            )
            explanation_steps = [
                f"讀取 {high_bound}{unit} 的以下累積次數。",
                f"讀取 {low_bound}{unit} 的以下累積次數。",
                f"區間 [{low_bound}, {high_bound}) 次數 = C({high_bound}) - C({low_bound}) = {answer_value}。",
            ]
        else:
            answer_value = recover_interval_frequency_from_greater_than(
                graph_points, low_bound=low_bound, high_bound=high_bound
            )
            explanation_steps = [
                f"讀取 {low_bound}{unit} 的以上累積次數。",
                f"讀取 {high_bound}{unit} 的以上累積次數。",
                f"區間 [{low_bound}, {high_bound}) 次數 = G({low_bound}) - G({high_bound}) = {answer_value}。",
            ]
        if answer_value < 0:
            raise ValueError("interval_frequency_negative")
        question_text = str(
            constraints.get("question_text")
            or f"已知{story}的{chart_phrase}如下圖所示，成績在{low_bound}～{high_bound}{unit}有多少人？"
        )
        return _build_matrix_shell(
            domain_operation=domain_operation,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            givens={
                "class_bounds": class_bounds,
                "class_frequencies": class_frequencies,
                "graph_points": graph_points,
                "cumulative_direction": direction_key,
                "total_students": total,
                "interval_low": low_bound,
                "interval_high": high_bound,
            },
            answer_value=answer_value,
            answer_type="integer",
            explanation_steps=explanation_steps,
            validation_facts={
                "domain_operation": domain_operation,
                "task_topology": topology,
                "cumulative_direction": direction_key,
                "interval_low": low_bound,
                "interval_high": high_bound,
                "answer_value": answer_value,
                "total_students": total,
            },
            visual_spec=visual_spec,
            question_text=question_text,
            image_base64=image_base64,
        )

    if topology == "graph_mcq":
        threshold = int(constraints.get("threshold") or 60)
        if direction_key == "below":
            answer_value = infer_fail_count_from_less_than(graph_points, threshold=threshold)
        else:
            answer_value = infer_fail_count_from_greater_than(
                graph_points, threshold=threshold, total=total
            )
        distractor_values = _integer_distractors(answer_value, rng)
        choices = [
            {"label": "A", "text": str(distractor_values[0])},
            {"label": "B", "text": str(distractor_values[1])},
            {"label": "C", "text": str(answer_value)},
            {"label": "D", "text": str(distractor_values[2])},
        ]
        rng.shuffle(choices)
        labels = ["A", "B", "C", "D"]
        for idx, choice in enumerate(choices):
            choice["label"] = labels[idx]
        correct_label = next(c["label"] for c in choices if int(c["text"]) == int(answer_value))
        explanation_steps = [
            f"讀取 {threshold}{unit} 的{'以下' if direction_key == 'below' else '以上'}累積次數。",
            (
                f"不及格人數 = C({threshold}) = {answer_value}。"
                if direction_key == "below"
                else f"不及格人數 = 總數 - G({threshold}) = {total} - {lookup_cumulative_at_bound(graph_points, threshold)} = {answer_value}。"
            ),
        ]
        question_text = str(
            constraints.get("question_text")
            or f"已知{story}的{chart_phrase}如下圖所示，以{threshold}{unit}為準，不及格者有多少人？"
        )
        return _build_matrix_shell(
            domain_operation=domain_operation,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            givens={
                "graph_points": graph_points,
                "cumulative_direction": direction_key,
                "threshold": threshold,
                "total_students": total,
            },
            answer_value=correct_label,
            answer_type="single_choice",
            explanation_steps=explanation_steps,
            validation_facts={
                "domain_operation": domain_operation,
                "task_topology": topology,
                "cumulative_direction": direction_key,
                "threshold": threshold,
                "semantic_answer": answer_value,
                "answer_value": answer_value,
                "total_students": total,
            },
            visual_spec=visual_spec,
            question_text=question_text,
            image_base64=image_base64,
            choices=choices,
            distractors=distractor_values,
            ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
        )

    # multi-part graph reading (below or above)
    sub_questions = list(constraints.get("sub_questions") or [])
    if not sub_questions:
        thresholds = list(constraints.get("thresholds") or [60, 70 + rng.randint(0, 2) * 10])
        if direction_key == "above":
            sub_questions = [
                {
                    "part": "(1)",
                    "prompt": f"以{thresholds[0]}{unit}為標準，不及格的人數有幾人",
                    "inference": "total_minus_above_cumulative",
                    "threshold": thresholds[0],
                },
                {
                    "part": "(2)",
                    "prompt": (
                        "80分以上的人數有幾人"
                        if len(thresholds) < 2
                        else f"至少{thresholds[1]}{unit}的人數有幾人"
                    ),
                    "inference": "read_above_cumulative",
                    "threshold": thresholds[1] if len(thresholds) > 1 else 80,
                },
            ]
        else:
            sub_questions = [
                {
                    "part": "(1)",
                    "prompt": f"以{thresholds[0]}{unit}為標準，不及格的人數有幾人",
                    "inference": "read_below_cumulative",
                    "threshold": thresholds[0],
                },
                {
                    "part": "(2)",
                    "prompt": f"至少{thresholds[1]}{unit}的人數有幾人",
                    "inference": "total_minus_below_cumulative",
                    "threshold": thresholds[1],
                },
            ]

    part_answers: list[int] = []
    part_explanations: list[str] = []
    subquestions: list[dict[str, Any]] = []
    for idx, sq in enumerate(sub_questions):
        inference = str(sq.get("inference") or "").strip()
        threshold = _threshold_from_subquestion(
            sq,
            default=60 if idx == 0 else (80 if direction_key == "above" else 70),
        )
        if inference in {
            "read_below_cumulative",
            "read_below_cumulative_at_60",
            "fail_below",
            "read_below_cumulative_at_threshold",
        }:
            value = infer_fail_count_from_less_than(graph_points, threshold=threshold)
            part_explanations.append(f"({idx + 1}) 不及格人數 = C({threshold}) = {value}。")
        elif inference in {
            "total_minus_below_cumulative",
            "total_minus_below_cumulative_at_70",
            "at_least",
        }:
            value = infer_at_least_count_from_less_than(graph_points, threshold=threshold, total=total)
            part_explanations.append(
                f"({idx + 1}) 至少 {threshold}{unit} 人數 = 總數 - C({threshold}) = {total} - {lookup_cumulative_at_bound(graph_points, threshold)} = {value}。"
            )
        elif inference in {
            "total_minus_above_cumulative",
            "total_minus_above_cumulative_at_60",
        }:
            value = infer_fail_count_from_greater_than(graph_points, threshold=threshold, total=total)
            part_explanations.append(
                f"({idx + 1}) 不及格人數 = 總數 - G({threshold}) = {total} - {lookup_cumulative_at_bound(graph_points, threshold)} = {value}。"
            )
        elif inference in {
            "read_above_cumulative",
            "read_above_cumulative_at_80",
            "read_above_cumulative_at_threshold",
        }:
            value = infer_at_least_count_from_greater_than(graph_points, threshold=threshold)
            part_explanations.append(f"({idx + 1}) {threshold}{unit} 以上人數 = G({threshold}) = {value}。")
        elif sq.get("expected_answer") is not None:
            value = int(sq["expected_answer"])
            part_explanations.append(f"({idx + 1}) 答案為 {value}。")
        else:
            value = read_cumulative_value(cumulative, min(idx, len(cumulative) - 1))
            part_explanations.append(f"({idx + 1}) 累積次數為 {value}。")
        part_answers.append(value)
        subquestions.append(
            {
                "part": sq.get("part") or f"({idx + 1})",
                "prompt": sq.get("prompt") or f"小題 {idx + 1}",
                "expected_answer": value,
                "unit": sq.get("unit") or "人",
            }
        )

    question_text = str(
        constraints.get("question_text")
        or f"已知{story}的{chart_phrase}如下圖所示，試問："
        + " ".join(f"{sq.get('part', f'({i+1})')}{sq.get('prompt', '')}" for i, sq in enumerate(sub_questions))
    )
    return _build_matrix_shell(
        domain_operation=domain_operation,
        curriculum_profile=curriculum_profile,
        difficulty_profile=difficulty_profile,
        givens={
            "class_bounds": class_bounds,
            "class_frequencies": class_frequencies,
            "graph_points": graph_points,
            "cumulative_direction": direction_key,
            "total_students": total,
        },
        answer_value=part_answers,
        answer_type="multi_part",
        explanation_steps=part_explanations,
        validation_facts={
            "domain_operation": domain_operation,
            "task_topology": topology,
            "cumulative_direction": direction_key,
            "answer_value": part_answers,
            "total_students": total,
            "graph_points": graph_points,
        },
        visual_spec=visual_spec,
        question_text=question_text,
        image_base64=image_base64,
        subquestions=subquestions,
        ui_contract={"response_mode": "multi_part", "text_input_enabled": True},
    )


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
    op = str(domain_operation or "").strip()
    if op in _CUMULATIVE_OPERATIONS:
        return build_cumulative_frequency_matrix(
            seed=seed,
            domain_operation=op,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            constraints=constraints,
        )
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

    # Build matplotlib table + grids or histograms depending on operation
    import io
    import base64
    import matplotlib.pyplot as plt

    # Set up matplotlib image generation for visual_aids/image_base64
    image_b64 = ""
    visual_aids = []
    distractor_values: list[int] = []

    # Map operation custom specifications
    if domain_operation == "frequency_distribution_chart_construction":
        # Draw the table and coordinates/grid for student to draw graph
        fig, (ax_tbl, ax_grid) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=120)
        try:
            # 1. Left side: Table
            ax_tbl.axis("off")
            tbl_title = str(constraints.get("title") or "次數分配表")
            ax_tbl.set_title(tbl_title, fontsize=12, fontweight="bold", pad=10)
            headers = ["組別", "次數"]
            rows_data = [[label, f"{frequency_map[label]} 人"] for label in categories]
            tbl = ax_tbl.table(cellText=rows_data, colLabels=headers, loc="center", cellLoc="center")
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1.0, 1.6)

            # 2. Right side: Empty Grid coordinates for drawing
            ax_grid.set_title("請在此繪製直方圖與折線圖", fontsize=11, fontweight="bold", pad=10)
            # Determine suitable limits
            y_max = max(frequencies) + 2
            ax_grid.set_xlim(-0.5, len(categories) - 0.5)
            ax_grid.set_ylim(0, y_max)
            ax_grid.set_xticks(range(len(categories)))
            ax_grid.set_xticklabels(categories, fontsize=9)
            ax_grid.set_ylabel("次數 (人)", fontsize=10)
            ax_grid.set_xlabel("組別", fontsize=10)
            ax_grid.grid(True, which="both", linestyle="--", alpha=0.5)
            ax_grid.set_axisbelow(True)

            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        finally:
            plt.close(fig)

        # Correct answer format for sketch-drawing question type is descriptive or empty (graded by teacher review/manual or coordinate equivalence, here we match textbook answer representation)
        ans_text = "直方圖與折線圖已繪製於畫布。"
        ans_val = ans_text
        explanation_steps = [
            "1. 依據次數分配表，橫軸標示各組組界，縱軸標示次數，繪製相連的長方形直方圖。",
            "2. 取各長方形頂部中點，並在左右兩端次數為 0 處各取一點（通常為相鄰組中點），用線段依序連接，即為次數分配折線圖。"
        ]
    elif domain_operation == "histogram_distribution_update":
        # 3829: Given initial histogram, show changes, student answers the new group frequencies
        # Initial table data (heights distribution of kids)
        # 100~105: 2, 105~110: 5, 110~115: 8, 115~120: 7, 120~125: 3
        # If seed changes, we randomize slightly but keep 25 total.
        init_freqs = list(frequencies)
        if len(init_freqs) < 5:
            init_freqs = [rng.randint(2, 6) for _ in range(5)]
        
        # Ensure 115~120 (index 3) has at least 2 so that decrement by 1 results in at least 1
        if init_freqs[3] < 2:
            init_freqs[3] = 2

        # Adjust frequencies to look like heights of 25 kids
        if sum(init_freqs) > 25 and (init_freqs[3] + 4) > 25:
            from core.exceptions import RetryableSamplingError
            raise RetryableSamplingError(
                f"Sampling constraints unsatisfied: target total 25 cannot be reached by decrementing because fixed index 3 frequency is {init_freqs[3]} (min possible sum is {init_freqs[3] + 4})",
                total_students=25,
                class_count=5,
                minimum_total=init_freqs[3] + 4,
                operation="histogram_distribution_update",
            )

        attempts = 0
        while sum(init_freqs) != 25 and attempts < 100:
            attempts += 1
            idx = rng.choice([0, 1, 2, 4]) # Do not change index 3 so it stays stable >= 2
            if sum(init_freqs) < 25:
                init_freqs[idx] += 1
            elif init_freqs[idx] > 1:
                init_freqs[idx] -= 1

        if sum(init_freqs) != 25:
            from core.exceptions import RetryableSamplingError
            raise RetryableSamplingError(
                f"Failed to adjust histogram frequencies to 25: sum(init_freqs)={sum(init_freqs)} != 25 after {attempts} attempts",
                total_students=25,
                class_count=5,
                minimum_total=init_freqs[3] + 4,
                operation="histogram_distribution_update",
            )

        height_bins = ["100~105", "105~110", "110~115", "115~120", "120~125"]
        init_map = dict(zip(height_bins, init_freqs, strict=True))

        # We transfer out one kid of 117 cm (belongs to 115~120) -> freq decreases by 1
        # We transfer in one kid of 112 cm (belongs to 110~115) -> freq increases by 1
        trans_out_val = constraints.get("trans_out_val", 117)
        trans_in_val = constraints.get("trans_in_val", 112)

        out_bin = "115~120"
        in_bin = "110~115"

        final_freqs = list(init_freqs)
        final_freqs[3] -= 1 # 115~120 index is 3
        final_freqs[2] += 1 # 110~115 index is 2
        final_map = dict(zip(height_bins, final_freqs, strict=True))

        # Draw the initial histogram
        fig, ax = plt.subplots(figsize=(6, 3.8), dpi=120)
        try:
            ax.bar(height_bins, init_freqs, width=0.9, color="skyblue", edgecolor="black", alpha=0.8)
            ax.set_title("小朋友身高分佈直方圖", fontsize=11, fontweight="bold")
            ax.set_xlabel("身高 (cm)", fontsize=9)
            ax.set_ylabel("人數 (人)", fontsize=9)
            y_max = max(init_freqs) + 2
            ax.set_ylim(0, y_max)
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        finally:
            plt.close(fig)

        ans_text = f"{out_bin}組次數減1，{in_bin}組次數加1"
        ans_val = ans_text
        explanation_steps = [
            f"1. 轉出一位身高 {trans_out_val} 公分的小朋友，屬於 {out_bin} 組，因此該組人數減少 1 人（{init_map[out_bin]} -> {final_map[out_bin]} 人）。",
            f"2. 轉入一位身高 {trans_in_val} 公分的小朋友，屬於 {in_bin} 組，因此該組人數增加 1 人（{init_map[in_bin]} -> {final_map[in_bin]} 人）。",
            f"3. 其餘各組人數不變。"
        ]
        # Override table rows for 3829 visual spec
        categories = height_bins
        frequency_map = init_map
        frequencies = init_freqs
    else:
        ans_val = answer_value
        explanation_steps = [
            "依資料分類整理各組出現次數。",
            f"查看 {target_label} 的次數。",
            f"{target_label} 的次數為 {answer_value}。",
        ]

    if image_b64:
        visual_aids = [{"type": "image/png", "value": image_b64}]

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
            "canonical_form": str(ans_val),
            "general_form": str(ans_val),
            "coefficients": {"frequency": ans_val} if isinstance(ans_val, int) else {},
            "value": ans_val,
            "unit": "次" if isinstance(ans_val, int) else "",
        },
        "distractors": [str(x) for x in distractor_values[:3]],
        "explanation_steps": explanation_steps,
        "validation_facts": {
            "domain_operation": domain_operation,
            "task_type": domain_operation,
            "frequency_map": frequency_map,
            "target_label": target_label,
            "answer_value": ans_val,
            "total_frequency": total,
        },
        "visual_spec": {
            "type": "table",
            "title": "次數分配表" if domain_operation != "histogram_distribution_update" else "身高分佈直方圖",
            "headers": ["組別", "次數"],
            "rows": [[label, frequency_map[label]] for label in categories],
        },
        "visual_aids": visual_aids,
        "image_base64": image_b64,
    }

