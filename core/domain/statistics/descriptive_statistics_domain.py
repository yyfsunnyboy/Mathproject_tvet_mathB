"""Descriptive statistics domain — reusable central tendency and dispersion operations."""

from __future__ import annotations

import random
import re
from typing import Any

from core.domain.statistics.descriptive_statistics_core import (
    DescriptiveDataInput,
    arithmetic_mean_from_frequency,
    arithmetic_mean_from_raw,
    build_numeric_distractor_candidates,
    format_numeric_answer,
    generate_frequency_pairs,
    generate_raw_values,
    generate_weighted_pairs,
    median_from_values,
    mode_from_values,
    population_standard_deviation,
    population_variance,
    range_and_iqr_summary,
    range_from_values,
    weighted_mean_from_pairs,
)
from core.gencode.descriptive_statistics_answer_contract import NO_MODE_SENTINEL

DOMAIN_KEY = "statistics.descriptive_statistics"
ENTRYPOINT = "build_descriptive_statistics_matrix"

_STORY_CONTEXTS = (
    "某班學生",
    "調查樣本",
    "測驗成績",
    "商品售價",
    "實驗量測",
)


def _rng(seed: int | None) -> random.Random:
    return random.Random(0 if seed is None else int(seed))


def _matrix_shell(
    *,
    givens: dict[str, Any],
    answer_value: Any,
    answer_text: str,
    validation_facts: dict[str, Any],
    explanation_steps: list[str],
    answer_shape: str,
    presentation_mode: str = "short_answer",
    answer_type: str = "expression",
    ui_contract: dict[str, Any] | None = None,
    subquestions: list[dict[str, Any]] | None = None,
    table_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "givens": givens,
        "answer": {
            "canonical_form": answer_text,
            "general_form": answer_text,
            "coefficients": {},
            "value": answer_value,
        },
        "distractors": [],
        "explanation_steps": explanation_steps,
        "validation_facts": validation_facts,
        "visual_spec": table_data or {},
        "answer_shape": answer_shape,
        "presentation_mode": presentation_mode,
        "answer_type": answer_type,
        "ui_contract": ui_contract or {},
        "subquestions": subquestions or [],
        "table_data": table_data or {},
        "fixed_domain_key": DOMAIN_KEY,
    }


def _default_rounding(rng: random.Random) -> dict[str, Any]:
    if rng.random() < 0.5:
        return {"decimal_places": 0, "prefer_integer": True}
    return {"decimal_places": 1 if rng.random() < 0.5 else 2, "prefer_integer": False}


def _build_mean_raw(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = list(constraints.get("raw_values") or [])
    if not values:
        values = generate_raw_values(rng, count=int(constraints.get("count") or rng.randint(4, 8)))
    values = [float(v) for v in values]
    rounding = dict(constraints.get("rounding_policy") or _default_rounding(rng))
    mean_val = arithmetic_mean_from_raw(values)
    answer_text = format_numeric_answer(mean_val, rounding)
    story = str(constraints.get("story_context") or rng.choice(_STORY_CONTEXTS))
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"已知 {story} 的資料為 {values_text}，求平均數。"
    return _matrix_shell(
        givens={
            "raw_values": values,
            "story_context": story,
            "target_measure": "arithmetic_mean",
            "rounding_policy": rounding,
            "question_text": question,
        },
        answer_value=mean_val,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "arithmetic_mean",
            "formula": "population_mean",
            "n": len(values),
            "sum": sum(values),
            "mean": mean_val,
            "answer_shape": "single_numeric",
        },
        explanation_steps=[
            f"資料共 {len(values)} 筆，總和 = {sum(values)}",
            f"平均數 = {sum(values)} / {len(values)} = {answer_text}",
        ],
        answer_shape="single_numeric",
        answer_type="expression",
    )


def _build_mean_frequency(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    pairs = list(constraints.get("value_frequency_pairs") or [])
    if not pairs:
        pairs = generate_frequency_pairs(rng)
    norm_pairs = [(float(v), int(f)) for v, f in pairs]
    rounding = dict(constraints.get("rounding_policy") or _default_rounding(rng))
    mean_val = arithmetic_mean_from_frequency(norm_pairs)
    answer_text = format_numeric_answer(mean_val, rounding)
    rows = [[str(v), str(f)] for v, f in norm_pairs]
    table = {"type": "table", "headers": ["數值", "次數"], "rows": rows}
    freq_text = "；".join(f"{int(v)} 出現 {int(f)} 次" for v, f in norm_pairs)
    question = f"已知次數分配：{freq_text}。求平均數。"
    return _matrix_shell(
        givens={
            "value_frequency_pairs": norm_pairs,
            "target_measure": "arithmetic_mean",
            "rounding_policy": rounding,
            "question_text": question,
        },
        answer_value=mean_val,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "arithmetic_mean",
            "formula": "frequency_weighted_mean",
            "total_frequency": sum(f for _, f in norm_pairs),
            "mean": mean_val,
            "answer_shape": "single_numeric",
        },
        explanation_steps=[
            f"總次數 = {sum(f for _, f in norm_pairs)}",
            f"加權和 = {sum(v * f for v, f in norm_pairs)}",
            f"平均數 = {answer_text}",
        ],
        answer_shape="single_numeric",
        table_data=table,
    )


def _build_weighted_mean(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    pairs = list(constraints.get("weights") or constraints.get("value_weight_pairs") or [])
    if not pairs:
        pairs = generate_weighted_pairs(rng)
    norm_pairs = [(float(v), float(w)) for v, w in pairs]
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 1, "prefer_integer": False})
    mean_val = weighted_mean_from_pairs(norm_pairs)
    answer_text = format_numeric_answer(mean_val, rounding)
    detail = "、".join(
        f"({int(v)}, 權重 {format_numeric_answer(w, {'decimal_places': 0, 'prefer_integer': True})})"
        for v, w in norm_pairs
    )
    question = f"已知各項成績與權重為 {detail}，求加權平均數。"
    return _matrix_shell(
        givens={"weights": norm_pairs, "target_measure": "weighted_mean", "rounding_policy": rounding, "question_text": question},
        answer_value=mean_val,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "weighted_mean",
            "total_weight": sum(w for _, w in norm_pairs),
            "weighted_sum": sum(v * w for v, w in norm_pairs),
            "mean": mean_val,
            "answer_shape": "single_numeric",
        },
        explanation_steps=[
            f"加權和 = {sum(v * w for v, w in norm_pairs)}",
            f"權重和 = {sum(w for _, w in norm_pairs)}",
            f"加權平均 = {answer_text}",
        ],
        answer_shape="single_numeric",
    )


def _build_median_raw(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = [
        float(v)
        for v in (constraints.get("raw_values") or generate_raw_values(rng, count=int(constraints.get("count") or rng.randint(5, 9))))
    ]
    rounding = dict(constraints.get("rounding_policy") or _default_rounding(rng))
    med = median_from_values(values)
    answer_text = format_numeric_answer(med, rounding)
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"資料 {values_text}，求中位數。"
    return _matrix_shell(
        givens={"raw_values": values, "target_measure": "median", "rounding_policy": rounding, "question_text": question},
        answer_value=med,
        answer_text=answer_text,
        validation_facts={"domain_operation": op, "target_measure": "median", "median": med, "n": len(values), "answer_shape": "single_numeric"},
        explanation_steps=["先由小到大排序", f"中位數 = {answer_text}"],
        answer_shape="single_numeric",
    )


def _build_mode_raw(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    force_multi = bool(constraints.get("force_multi_mode"))
    force_none = bool(constraints.get("force_no_mode"))
    if force_none:
        values = list(dict.fromkeys(generate_raw_values(rng, count=6)))
    elif force_multi:
        base = rng.randint(2, 8)
        values = [base, base, base + 1, base + 1, base + 2, rng.randint(9, 12)]
    else:
        base = rng.randint(2, 8)
        values = [base, base, base, rng.randint(9, 15), rng.randint(16, 20)]
    values = [float(v) for v in (constraints.get("raw_values") or values)]
    modes = mode_from_values(values)
    if not modes:
        answer_text = NO_MODE_SENTINEL
        answer_shape = "text_short"
        answer_type = "text_short"
    elif len(modes) == 1:
        answer_text = format_numeric_answer(modes[0], {"decimal_places": 0, "prefer_integer": True})
        answer_shape = "single_numeric"
        answer_type = "expression"
    else:
        answer_text = ", ".join(format_numeric_answer(m, {"decimal_places": 0, "prefer_integer": True}) for m in modes)
        answer_shape = "unordered_set"
        answer_type = "unordered_set"
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"資料 {values_text}，求眾數。"
    return _matrix_shell(
        givens={"raw_values": values, "target_measure": "mode", "question_text": question},
        answer_value=modes if len(modes) != 1 else modes[0],
        answer_text=answer_text,
        validation_facts={"domain_operation": op, "target_measure": "mode", "modes": modes, "answer_shape": answer_shape},
        explanation_steps=[f"眾數 = {answer_text}"],
        answer_shape=answer_shape,
        answer_type=answer_type,
    )


def _build_mode_frequency(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    pairs = [(float(v), int(f)) for v, f in (constraints.get("value_frequency_pairs") or generate_frequency_pairs(rng))]
    data = DescriptiveDataInput(value_frequency_pairs=pairs)
    modes = mode_from_values(data.expanded_values)
    if not modes:
        answer_text = NO_MODE_SENTINEL
        answer_shape = "text_short"
    elif len(modes) == 1:
        answer_text = format_numeric_answer(modes[0], {"decimal_places": 0, "prefer_integer": True})
        answer_shape = "single_numeric"
    else:
        answer_text = ", ".join(format_numeric_answer(m, {"decimal_places": 0, "prefer_integer": True}) for m in modes)
        answer_shape = "unordered_set"
    freq_text = "；".join(f"{int(v)}:{int(f)}" for v, f in pairs)
    question = f"次數分配 {freq_text}，求眾數。"
    return _matrix_shell(
        givens={"value_frequency_pairs": pairs, "target_measure": "mode", "question_text": question},
        answer_value=modes,
        answer_text=answer_text,
        validation_facts={"domain_operation": op, "target_measure": "mode", "modes": modes, "answer_shape": answer_shape},
        explanation_steps=[f"眾數 = {answer_text}"],
        answer_shape=answer_shape,
    )


def _build_range(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = [
        float(v)
        for v in (constraints.get("raw_values") or generate_raw_values(rng, count=int(constraints.get("count") or rng.randint(5, 8))))
    ]
    r = range_from_values(values)
    answer_text = format_numeric_answer(r, {"decimal_places": 0, "prefer_integer": True})
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"資料 {values_text}，求全距。"
    return _matrix_shell(
        givens={"raw_values": values, "target_measure": "range", "question_text": question},
        answer_value=r,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "range",
            "max": max(values),
            "min": min(values),
            "range": r,
            "answer_shape": "single_numeric",
        },
        explanation_steps=[f"全距 = {max(values)} - {min(values)} = {answer_text}"],
        answer_shape="single_numeric",
    )


def _build_variance(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = [
        float(v)
        for v in (constraints.get("raw_values") or generate_raw_values(rng, count=int(constraints.get("count") or rng.randint(4, 6))))
    ]
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 0, "prefer_integer": True})
    var = population_variance(values)
    answer_text = format_numeric_answer(var, rounding)
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"資料 {values_text}，求母體變異數。"
    mean = arithmetic_mean_from_raw(values)
    return _matrix_shell(
        givens={"raw_values": values, "target_measure": "variance", "rounding_policy": rounding, "question_text": question},
        answer_value=var,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "variance",
            "formula": "population_variance",
            "mean": mean,
            "variance": var,
            "n": len(values),
            "answer_shape": "single_numeric",
        },
        explanation_steps=[f"平均數 μ = {format_numeric_answer(mean, rounding)}", f"母體變異數 σ² = {answer_text}"],
        answer_shape="single_numeric",
    )


def _build_stddev(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = [
        float(v)
        for v in (
            constraints.get("raw_values")
            or generate_raw_values(rng, count=int(constraints.get("count") or rng.randint(4, 6)))
        )
    ]
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 0, "prefer_integer": True})
    var = population_variance(values)
    std = population_standard_deviation(values)
    answer_text = format_numeric_answer(std, rounding)
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = str(
        constraints.get("question_text")
        or f"資料 {values_text}，求母體標準差。"
    )
    presentation_mode = str(constraints.get("presentation_mode") or "short_answer")
    answer_shape = "single_choice" if presentation_mode == "single_choice" else "single_numeric"
    answer_type = "single_choice" if presentation_mode == "single_choice" else "expression"
    return _matrix_shell(
        givens={
            "raw_values": values,
            "target_measure": "standard_deviation",
            "rounding_policy": rounding,
            "question_text": question,
            "source_choices": list(constraints.get("source_choices") or []),
            "source_answer_label": str(constraints.get("source_answer_label") or "").strip(),
        },
        answer_value=std if presentation_mode != "single_choice" else str(constraints.get("source_answer_label") or answer_text),
        answer_text=str(constraints.get("source_answer_label") or answer_text) if presentation_mode == "single_choice" else answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "standard_deviation",
            "formula": "population_standard_deviation",
            "variance": var,
            "standard_deviation": std,
            "answer_shape": answer_shape,
        },
        explanation_steps=[f"母體變異數 σ² = {format_numeric_answer(var, rounding)}", f"母體標準差 σ = {answer_text}"],
        answer_shape=answer_shape,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
    )


def _build_table_completion(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    values = [float(v) for v in (constraints.get("raw_values") or generate_raw_values(rng, count=6))]
    mean_val = arithmetic_mean_from_raw(values)
    med = median_from_values(values)
    r = range_from_values(values)
    var = population_variance(values)
    std = population_standard_deviation(values)
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 1, "prefer_integer": False})
    answers = {
        "mean": format_numeric_answer(mean_val, rounding),
        "median": format_numeric_answer(med, rounding),
        "range": format_numeric_answer(r, {"decimal_places": 0, "prefer_integer": True}),
        "variance": format_numeric_answer(var, rounding),
        "standard_deviation": format_numeric_answer(std, rounding),
    }
    field_specs = [
        {"field_key": "field_mean", "label": "平均數", "expected_answer": answers["mean"], "rounding_policy": rounding},
        {"field_key": "field_median", "label": "中位數", "expected_answer": answers["median"], "rounding_policy": rounding},
        {"field_key": "field_range", "label": "全距", "expected_answer": answers["range"], "rounding_policy": {"decimal_places": 0, "prefer_integer": True}},
        {"field_key": "field_variance", "label": "變異數", "expected_answer": answers["variance"], "rounding_policy": rounding},
        {"field_key": "field_standard_deviation", "label": "標準差", "expected_answer": answers["standard_deviation"], "rounding_policy": rounding},
    ]
    values_text = ", ".join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    question = f"資料 {values_text}，完成下表各統計量。"
    display_rows = [
        ["平均數", ""],
        ["中位數", ""],
        ["全距", ""],
        ["變異數", ""],
        ["標準差", ""],
    ]
    blank_cells = [
        {"row": idx, "col": 1, "field_key": spec["field_key"], "expected_answer": spec["expected_answer"], "input_type": "number"}
        for idx, spec in enumerate(field_specs)
    ]
    table = {
        "type": "table",
        "headers": ["統計量", "數值"],
        "rows": display_rows,
        "blank_cells": blank_cells,
    }
    answer_text = "; ".join(f"{spec['field_key']}={spec['expected_answer']}" for spec in field_specs)
    return _matrix_shell(
        givens={
            "raw_values": values,
            "target_measure": "descriptive_statistics_table",
            "rounding_policy": rounding,
            "question_text": question,
            "field_specs": field_specs,
        },
        answer_value=answers,
        answer_text=answer_text,
        validation_facts={"domain_operation": op, "target_measure": "table_completion", "statistics": answers, "answer_shape": "table_fill"},
        explanation_steps=["依序計算平均數、中位數、全距、母體變異數與母體標準差"],
        answer_shape="table_fill",
        presentation_mode="table_fill",
        answer_type="multi_part",
        ui_contract={"blank_count": len(field_specs), "labels": [spec["label"] for spec in field_specs], "response_mode": "table_fill"},
        table_data=table,
        subquestions=[{"field_key": spec["field_key"], "label": spec["label"], "expected_answer": spec["expected_answer"]} for spec in field_specs],
    )


def _build_multi_group_range_iqr(
    rng: random.Random,
    constraints: dict[str, Any],
    op: str,
    *,
    compare_groups: bool,
) -> dict[str, Any]:
    datasets = list(constraints.get("datasets") or [])
    if not datasets:
        count = 2 if compare_groups else 2
        datasets = [
            {"label": f"第{i + 1}組", "raw_values": generate_raw_values(rng, count=rng.randint(7, 11))}
            for i in range(count)
        ]
    rounding = dict(constraints.get("rounding_policy") or _default_rounding(rng))
    integer_rounding = {"decimal_places": 0, "prefer_integer": True}
    field_specs: list[dict[str, Any]] = []
    subquestions: list[dict[str, Any]] = []
    field_groups: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    answer_map: dict[str, Any] = {}
    for index, dataset in enumerate(datasets[:2], start=1):
        values = [float(v) for v in dataset.get("raw_values") or generate_raw_values(rng)]
        summary = range_and_iqr_summary(values, rounding_policy=rounding)
        group_label = str(dataset.get("label") or f"第{index}組")
        range_key = f"group_{index}_range"
        iqr_key = f"group_{index}_iqr"
        range_answer = summary["range_text"]
        iqr_answer = summary["iqr_text"]
        field_specs.extend(
            [
                {
                    "field_key": range_key,
                    "label": "全距",
                    "group_label": group_label,
                    "expected_answer": range_answer,
                    "rounding_policy": integer_rounding,
                    "input_type": "number",
                },
                {
                    "field_key": iqr_key,
                    "label": "四分位距",
                    "group_label": group_label,
                    "expected_answer": iqr_answer,
                    "rounding_policy": rounding,
                    "input_type": "number",
                },
            ]
        )
        subquestions.extend(
            [
                {
                    "field_key": range_key,
                    "part": group_label,
                    "prompt": "全距",
                    "input_type": "number",
                    "expected_answer": range_answer,
                },
                {
                    "field_key": iqr_key,
                    "part": group_label,
                    "prompt": "四分位距",
                    "input_type": "number",
                    "expected_answer": iqr_answer,
                },
            ]
        )
        field_groups.append(
            {
                "group_label": group_label,
                "fields": [range_key, iqr_key],
            }
        )
        answer_map[range_key] = summary["range"]
        answer_map[iqr_key] = summary["iqr"]
        summaries.append({"label": group_label, "raw_values": values, **summary})
    answer_text = "，".join(
        f"{item['label']}：R={item['range_text']}，IQR={item['iqr_text']}"
        for item in summaries
    )
    if compare_groups:
        question = "比較下列兩組資料的離散程度，分別求全距 R 與四分位距 IQR。"
    else:
        question = "試求下列兩組資料的全距 R 與四分位距 IQR。"
    detail = "；".join(
        f"({idx}) {item['label']}：R={item['range_text']}，IQR={item['iqr_text']}"
        for idx, item in enumerate(summaries, start=1)
    )
    question = str(constraints.get("question_text") or f"{question}{detail}")
    return _matrix_shell(
        givens={
            "datasets": summaries,
            "target_measure": "range_and_iqr",
            "rounding_policy": rounding,
            "question_text": question,
            "field_specs": field_specs,
            "compare_groups": compare_groups,
        },
        answer_value=answer_map,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "range_and_iqr",
            "answer_shape": "multi_part",
            "group_summaries": summaries,
        },
        explanation_steps=[
            "各組資料先排序",
            "全距 = 最大值 - 最小值",
            "IQR = Q3 - Q1",
        ],
        answer_shape="multi_part",
        presentation_mode="short_answer",
        answer_type="multi_part",
        ui_contract={
            "response_mode": "multi_part",
            "text_input_enabled": True,
            "field_groups": field_groups,
        },
        subquestions=subquestions,
    )


def _build_quartiles_and_iqr(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    return _build_multi_group_range_iqr(rng, constraints, op, compare_groups=False)


def _build_compare_dispersion(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    merged = dict(constraints)
    if not merged.get("datasets"):
        merged["datasets"] = [
            {"label": "女生", "raw_values": generate_raw_values(rng, count=rng.randint(7, 9))},
            {"label": "男生", "raw_values": generate_raw_values(rng, count=rng.randint(8, 10))},
        ]
    return _build_multi_group_range_iqr(rng, merged, op, compare_groups=True)


def _build_conceptual_dispersion_judgment(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    scenarios = list(constraints.get("concept_scenarios") or [])
    if scenarios:
        scenario = dict(scenarios[rng.randrange(len(scenarios))])
    else:
        spread = rng.randint(80, 200)
        scenario = {
            "story": f"某商品在{rng.randint(4, 8)}家商家的價差在{spread}元以內",
            "target_statistic": "range",
            "correct_label": "B",
            "choices": [
                {"label": "A", "text": "四分位距"},
                {"label": "B", "text": "全距"},
                {"label": "C", "text": "標準差"},
                {"label": "D", "text": "算術平均數"},
            ],
        }
    choices = list(scenario.get("choices") or [])
    correct_label = str(scenario.get("correct_label") or "B").strip().upper()
    question = str(
        constraints.get("question_text")
        or f"{scenario.get('story', '觀察敘述')}。試問應用了下列哪一種統計量？"
    )
    return _matrix_shell(
        givens={
            "concept_scenario": scenario,
            "target_statistic": str(scenario.get("target_statistic") or "range"),
            "question_text": question,
            "choices": choices,
            "source_answer_label": correct_label,
        },
        answer_value=correct_label,
        answer_text=correct_label,
        validation_facts={
            "domain_operation": op,
            "target_measure": "conceptual_dispersion_judgment",
            "semantic_answer": correct_label,
            "answer_shape": "single_choice",
        },
        explanation_steps=["依敘述中的統計概念判斷對應統計量"],
        answer_shape="single_choice",
        presentation_mode="single_choice",
        answer_type="single_choice",
        ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
    )


_HANDLERS = {
    "compute_arithmetic_mean_from_raw_values": _build_mean_raw,
    "compute_arithmetic_mean_from_frequency_table": _build_mean_frequency,
    "compute_weighted_mean": _build_weighted_mean,
    "compute_median_from_raw_values": _build_median_raw,
    "compute_mode_from_raw_values": _build_mode_raw,
    "compute_mode_from_frequency_table": _build_mode_frequency,
    "compute_range": _build_range,
    "compute_population_variance": _build_variance,
    "compute_population_standard_deviation": _build_stddev,
    "complete_descriptive_statistics_table": _build_table_completion,
    "compute_quartiles_and_iqr": _build_quartiles_and_iqr,
    "compare_dispersion": _build_compare_dispersion,
    "conceptual_dispersion_judgment": _build_conceptual_dispersion_judgment,
}


def _auxiliary_values_from_givens(givens: dict[str, Any]) -> list[float]:
    aux: list[float] = []
    raw_values = givens.get("raw_values")
    if isinstance(raw_values, list):
        aux.extend(float(v) for v in raw_values)
    pairs = givens.get("value_frequency_pairs") or givens.get("weights")
    if isinstance(pairs, list):
        for item in pairs:
            if isinstance(item, (list, tuple)) and item:
                aux.append(float(item[0]))
    return aux


def _apply_single_choice_presentation(
    matrix: dict[str, Any],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    mode = str(
        constraints.get("presentation_mode")
        or matrix.get("presentation_mode")
        or ""
    ).strip()
    if mode != "single_choice":
        return matrix

    givens = matrix.get("givens") if isinstance(matrix.get("givens"), dict) else {}
    source_choices = list(
        constraints.get("source_choices")
        or givens.get("source_choices")
        or givens.get("choices")
        or []
    )
    source_answer_label = str(
        constraints.get("source_answer_label")
        or givens.get("source_answer_label")
        or ""
    ).strip()
    if source_choices and re.fullmatch(r"[A-D]", source_answer_label.upper()):
        givens["source_choices"] = source_choices
        givens["choices"] = source_choices
        givens["source_answer_label"] = source_answer_label.upper()
        matrix["givens"] = givens
        matrix["presentation_mode"] = "single_choice"
        matrix["answer_type"] = "single_choice"
        matrix["answer_shape"] = "single_choice"
        matrix["ui_contract"] = {
            "response_mode": "single_choice",
            "text_input_enabled": False,
        }
        validation_facts = dict(matrix.get("validation_facts") or {})
        validation_facts["semantic_answer"] = source_answer_label.upper()
        validation_facts["answer_shape"] = "single_choice"
        matrix["validation_facts"] = validation_facts
        matrix["answer"] = {
            "value": source_answer_label.upper(),
            "canonical_form": source_answer_label.upper(),
            "general_form": source_answer_label.upper(),
            "coefficients": {},
            "correct_label": source_answer_label.upper(),
        }
        return matrix

    answer_obj = matrix.get("answer") if isinstance(matrix.get("answer"), dict) else {}
    givens = matrix.get("givens") if isinstance(matrix.get("givens"), dict) else {}
    validation_facts = dict(matrix.get("validation_facts") or {})
    rounding = dict(givens.get("rounding_policy") or constraints.get("rounding_policy") or {})
    answer_value = answer_obj.get("value", answer_obj.get("canonical_form"))
    answer_text = str(answer_obj.get("canonical_form") or format_numeric_answer(answer_value, rounding))
    auxiliary = _auxiliary_values_from_givens(givens)
    distractors = list(matrix.get("distractors") or validation_facts.get("distractor_candidates") or [])
    if not distractors:
        distractors = build_numeric_distractor_candidates(
            answer_value,
            rounding_policy=rounding,
            auxiliary_values=auxiliary,
        )

    matrix["distractors"] = distractors
    matrix["presentation_mode"] = "single_choice"
    matrix["answer_type"] = "single_choice"
    matrix["ui_contract"] = {
        "response_mode": "single_choice",
        "text_input_enabled": False,
    }
    validation_facts["distractor_candidates"] = distractors
    validation_facts["semantic_answer"] = answer_text
    matrix["validation_facts"] = validation_facts
    matrix["answer"] = {
        **answer_obj,
        "canonical_form": answer_text,
        "value": answer_value,
    }
    return matrix


def build_descriptive_statistics_matrix(
    *,
    seed: int | None = None,
    domain_operation: str | None = None,
    line_type: str | None = None,
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "medium",
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Full Matrix for a descriptive statistics operation."""
    op = str(domain_operation or line_type or "").strip()
    if not op:
        raise ValueError("domain_operation_required")
    handler = _HANDLERS.get(op)
    if handler is None:
        raise ValueError(f"unsupported_domain_operation:{op}")
    rng = _rng(seed)
    merged = dict(constraints or {})
    merged.setdefault("curriculum_profile", curriculum_profile)
    merged.setdefault("difficulty_profile", difficulty_profile)
    matrix = handler(rng, merged, op)
    matrix["domain_operation"] = op
    matrix["selected_operation"] = op
    matrix["required_capabilities"] = list(_operation_capabilities(op))
    matrix = _apply_single_choice_presentation(matrix, merged)
    return matrix


def _operation_capabilities(operation: str) -> tuple[str, ...]:
    mapping = {
        "compute_arithmetic_mean_from_raw_values": ("arithmetic_mean",),
        "compute_arithmetic_mean_from_frequency_table": ("arithmetic_mean", "frequency_weighted_statistics"),
        "compute_weighted_mean": ("weighted_mean",),
        "compute_median_from_raw_values": ("median",),
        "compute_mode_from_raw_values": ("mode",),
        "compute_mode_from_frequency_table": ("mode", "frequency_weighted_statistics"),
        "compute_range": ("range",),
        "compute_population_variance": ("variance",),
        "compute_population_standard_deviation": ("standard_deviation", "variance"),
        "complete_descriptive_statistics_table": (
            "descriptive_statistics_table_completion",
            "arithmetic_mean",
            "median",
            "range",
            "variance",
            "standard_deviation",
        ),
        "compute_quartiles_and_iqr": ("range", "quartile", "interquartile_range"),
        "compare_dispersion": ("dispersion_comparison", "range", "quartile", "interquartile_range"),
        "conceptual_dispersion_judgment": ("conceptual_dispersion_judgment",),
    }
    return mapping.get(operation, ("descriptive_statistics",))
