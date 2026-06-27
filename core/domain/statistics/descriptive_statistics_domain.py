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
    sample_variance,
    sample_standard_deviation,
    empirical_rule_central_probability,
    empirical_rule_one_tail_probability,
    empirical_rule_cumulative_probability,
    population_count_from_probability,
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


def _perturb_raw_values(rng: random.Random, orig_values: list[float], is_choice: bool = False) -> list[float]:
    if not orig_values:
        return orig_values
    shift = rng.randint(2, 8)
    if rng.random() < 0.5:
        shift = -shift
    if is_choice:
        return [float(int(v + shift)) for v in orig_values]
    else:
        perturbed = []
        for v in orig_values:
            val = v + shift + rng.randint(-2, 2)
            perturbed.append(float(int(val)))
        return perturbed


def _build_variance(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    raw = constraints.get("raw_values")
    q_template_v = str(constraints.get("question_text") or "")
    if q_template_v:
        # question_text present: use seed-driven generation (avoids narrative-number contamination)
        low_v, high_v = _infer_value_range(constraints)
        count_v = int(constraints.get("count") or 0) or _infer_count(constraints, raw, fallback=rng.randint(4, 6))
        values = [float(v) for v in generate_raw_values(rng, count=count_v, low=low_v, high=high_v)]
    elif raw:
        # No question_text: safe to use provided raw_values directly (no narrative contamination)
        values = [float(v) for v in raw]
    else:
        count_v = int(constraints.get("count") or 0) or rng.randint(4, 6)
        values = [float(v) for v in generate_raw_values(rng, count=count_v)]
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 0, "prefer_integer": True})
    var = population_variance(values)
    answer_text = format_numeric_answer(var, rounding)
    sep_v = "、"
    values_text = sep_v.join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    if q_template_v:
        q_updated_v = re.sub(
            r"([\uff1a:\uff1a]\s*)[\d\s,\uff0c\u3001.+\-]+?(?=[,\u3002\u300d\uff01]|\u8a66\u6c42|\u6c42|\u5247|$)",
            lambda m: m.group(1) + values_text,
            q_template_v, count=1,
        )
        question = q_updated_v if q_updated_v != q_template_v else q_template_v
    else:
        question = f"\u8cc7\u6599 {values_text}\uff0c\u6c42\u6bcd\u9ad4\u8b8a\u7570\u6578\u3002"
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

# ── Semantic helpers (no tid / component_id references) ─────────────────────

def _infer_value_range(constraints: dict[str, Any]) -> tuple[int, int]:
    """Derive a plausible (low, high) data range from question semantics.

    Uses ``data_range`` if explicitly provided, otherwise infers from
    keywords in the question text.  Never references textbook_example_id.
    """
    if "data_range" in constraints:
        lo, hi = constraints["data_range"]
        return int(lo), int(hi)
    q = str(constraints.get("question_text") or "")
    if re.search(r"身高", q):          # height context
        return 160, 200
    if re.search(r"體重", q):          # body-weight context
        return 30, 70
    if re.search(r"成績|分數|月考|科[室-模]?", q):  # exam-score context
        return 50, 100
    return 1, 20                          # default: small integers


def _infer_count(
    constraints: dict[str, Any],
    raw: list | None,
    *,
    fallback: int,
) -> int:
    """Derive the expected data-point count from constraints.

    Priority: explicit ``count`` key > stated count in question text > fallback.
    Never uses textbook_example_id.
    """
    if constraints.get("count"):
        return int(constraints["count"])
    q = str(constraints.get("question_text") or "")
    # Stated count: "10 位", "六位", "12 人", etc.
    m = re.search(r"(\d+)\s*(?:位|人|名|個|筆)", q)
    if m:
        n = int(m.group(1))
        if 3 <= n <= 20:
            return n
    zh_map = {"六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    for ch, n in zh_map.items():
        if re.search(ch + r"\s*(?:位|人|名|個|筆|科|員)", q):
            return n
    if raw and 3 <= len(raw) <= 20:
        return len(raw)
    return fallback


def _build_stddev(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    raw = constraints.get("raw_values")
    q_tmpl_s = str(constraints.get("question_text") or "")
    if q_tmpl_s:
        # question_text present: seed-driven to avoid narrative-number contamination
        low, high = _infer_value_range(constraints)
        count = int(constraints.get("count") or 0) or _infer_count(constraints, raw, fallback=rng.randint(4, 6))
        values = [float(v) for v in generate_raw_values(rng, count=count, low=low, high=high)]
    elif raw:
        values = [float(v) for v in raw]
    else:
        low, high = _infer_value_range(constraints)
        count = int(constraints.get("count") or 0) or rng.randint(4, 6)
        values = [float(v) for v in generate_raw_values(rng, count=count, low=low, high=high)]
    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 0, "prefer_integer": True})
    var = population_variance(values)
    std = population_standard_deviation(values)
    sep = "、"
    values_text = sep.join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    # Build question from stored template, substituting the fresh data list in-place.
    q_template = str(constraints.get("question_text") or "")
    if q_template:
        q_updated = re.sub(
            r"([：:﹕]\s*)[\d\s,，、.+\-]+?(?=[，。]|試求|求|則|$)",
            lambda m: m.group(1) + values_text,
            q_template,
            count=1,
        )
        question = q_updated if q_updated != q_template else q_template
    else:
        question = f"資料 {values_text}，求母體標準差。"
    presentation_mode = str(constraints.get("presentation_mode") or "short_answer")
    # multi_part when question explicitly requests both variance and standard deviation
    wants_both = bool(re.search(r"變異數.*標準差|標準差.*變異數", question))
    if wants_both:
        answer_shape = "multi_part"
        answer_type = "multi_part"
        field_specs = [
            {
                "field_key": "population_variance",
                "label": "母體變異數",
                "expected_answer": var,
                "answer_shape": "single_numeric",
                "rounding_policy": rounding,
            },
            {
                "field_key": "population_standard_deviation",
                "label": "母體標準差",
                "expected_answer": std,
                "answer_shape": "single_numeric",
                "rounding_policy": rounding,
            }
        ]
        answer_value = {"population_variance": var, "population_standard_deviation": std}
        answer_text = f"{format_numeric_answer(var, rounding)}, {format_numeric_answer(std, rounding)}"
        return _matrix_shell(
            givens={
                "raw_values": values,
                "target_measure": "population_standard_deviation",
                "rounding_policy": rounding,
                "question_text": question,
                "field_specs": field_specs,
            },
            answer_value=answer_value,
            answer_text=answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "population_standard_deviation",
                "formula": "population_standard_deviation",
                "variance": var,
                "standard_deviation": std,
                "answer_shape": answer_shape,
            },
            explanation_steps=[
                f"平均數 = {format_numeric_answer(arithmetic_mean_from_raw(values), rounding)}",
                f"母體變異數 σ² = {format_numeric_answer(var, rounding)}",
                f"母體標準差 σ = {format_numeric_answer(std, rounding)}",
            ],
            answer_shape=answer_shape,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
        )
    else:
        answer_shape = "single_choice" if presentation_mode == "single_choice" else "single_numeric"
        answer_type = "single_choice" if presentation_mode == "single_choice" else "expression"
        answer_text = format_numeric_answer(std, rounding)
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
            explanation_steps=[
                f"母體變異數 σ² = {format_numeric_answer(var, rounding)}",
                f"母體標準差 σ = {answer_text}"
            ],
            answer_shape=answer_shape,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
        )


def _build_sample_variance(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    tid = constraints.get("textbook_example_id") or constraints.get("source_example_id")
    is_choice = (str(constraints.get("presentation_mode") or "") == "single_choice")
    raw = constraints.get("raw_values")
    q_tmpl2 = str(constraints.get("question_text") or "")
    if q_tmpl2:
        low2, high2 = _infer_value_range(constraints)
        count2 = int(constraints.get("count") or 0) or _infer_count(constraints, raw, fallback=rng.randint(4, 6))
        values = [float(v) for v in generate_raw_values(rng, count=count2, low=low2, high=high2)]
    elif raw:
        values = [float(v) for v in raw]
    else:
        low2, high2 = _infer_value_range(constraints)
        count2 = int(constraints.get("count") or 0) or rng.randint(4, 6)
        values = [float(v) for v in generate_raw_values(rng, count=count2, low=low2, high=high2)]

    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 1, "prefer_integer": True})
    var = sample_variance(values)
    answer_text = format_numeric_answer(var, rounding)
    sep2 = "、"
    values_text = sep2.join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    q_tmpl2 = str(constraints.get("question_text") or "")
    if q_tmpl2:
        q_up2 = re.sub(
            r"([\uff1a:\uff1a]\s*)[\d\s,\uff0c\u3001.+\-]+?(?=[,\u3002\u300d\uff01]|\u8a66\u6c42|\u6c42|\u5247|$)",
            lambda m: m.group(1) + values_text,
            q_tmpl2, count=1,
        )
        question = q_up2 if q_up2 != q_tmpl2 else q_tmpl2
    else:
        question = f"\u8cc7\u6599 {values_text}\uff0c\u6c42\u6a23\u672c\u8b8a\u7570\u6578\u3002"
    mean = arithmetic_mean_from_raw(values)
    return _matrix_shell(
        givens={"raw_values": values, "target_measure": "sample_variance", "rounding_policy": rounding, "question_text": question},
        answer_value=var,
        answer_text=answer_text,
        validation_facts={
            "domain_operation": op,
            "target_measure": "sample_variance",
            "formula": "sample_variance",
            "mean": mean,
            "sample_variance": var,
            "n": len(values),
            "answer_shape": "single_numeric",
        },
        explanation_steps=[f"平均數 = {format_numeric_answer(mean, rounding)}", f"樣本變異數 s² = {answer_text}"],
        answer_shape="single_numeric",
    )


def _build_sample_stddev(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    tid = constraints.get("textbook_example_id") or constraints.get("source_example_id")
    is_choice = (str(constraints.get("presentation_mode") or "") == "single_choice")
    raw = constraints.get("raw_values")
    q_tmpl3 = str(constraints.get("question_text") or "")
    if q_tmpl3:
        low3, high3 = _infer_value_range(constraints)
        count3 = int(constraints.get("count") or 0) or _infer_count(constraints, raw, fallback=rng.randint(4, 6))
        values = [float(v) for v in generate_raw_values(rng, count=count3, low=low3, high=high3)]
    elif raw:
        values = [float(v) for v in raw]
    else:
        low3, high3 = _infer_value_range(constraints)
        count3 = int(constraints.get("count") or 0) or rng.randint(4, 6)
        values = [float(v) for v in generate_raw_values(rng, count=count3, low=low3, high=high3)]

    rounding = dict(constraints.get("rounding_policy") or {"decimal_places": 1, "prefer_integer": True})
    var = sample_variance(values)
    std = sample_standard_deviation(values)
    sep3 = "、"
    values_text = sep3.join(format_numeric_answer(v, {"decimal_places": 0, "prefer_integer": True}) for v in values)
    q_tmpl3 = str(constraints.get("question_text") or "")
    if q_tmpl3:
        q_up3 = re.sub(
            r"([\uff1a:\uff1a]\s*)[\d\s,\uff0c\u3001.+\-]+?(?=[,\u3002\u300d\uff01]|\u8a66\u6c42|\u6c42|\u5247|$)",
            lambda m: m.group(1) + values_text,
            q_tmpl3, count=1,
        )
        question = q_up3 if q_up3 != q_tmpl3 else q_tmpl3
    else:
        question = f"\u8cc7\u6599 {values_text}\uff0c\u6c42\u6a23\u672c\u6a19\u6e96\u5dee\u3002"
    presentation_mode = str(constraints.get("presentation_mode") or "short_answer")
    wants_both_s = bool(re.search(r"\u6a23\u672c\u8b8a\u7570\u6578.*\u6a23\u672c\u6a19\u6e96\u5dee|\u6a23\u672c\u6a19\u6e96\u5dee.*\u6a23\u672c\u8b8a\u7570\u6578", question))
    if wants_both_s:
        answer_shape = "multi_part"
        answer_type = "multi_part"
        field_specs = [
            {
                "field_key": "sample_variance",
                "label": "樣本變異數",
                "expected_answer": var,
                "answer_shape": "single_numeric",
                "rounding_policy": rounding,
            },
            {
                "field_key": "sample_standard_deviation",
                "label": "樣本標準差",
                "expected_answer": std,
                "answer_shape": "single_numeric",
                "rounding_policy": rounding,
            }
        ]
        answer_value = {"sample_variance": var, "sample_standard_deviation": std}
        answer_text = f"{format_numeric_answer(var, rounding)}, {format_numeric_answer(std, rounding)}"
        return _matrix_shell(
            givens={
                "raw_values": values,
                "target_measure": "sample_standard_deviation",
                "rounding_policy": rounding,
                "question_text": question,
                "field_specs": field_specs,
            },
            answer_value=answer_value,
            answer_text=answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "sample_standard_deviation",
                "formula": "sample_standard_deviation",
                "sample_variance": var,
                "sample_standard_deviation": std,
                "answer_shape": answer_shape,
            },
            explanation_steps=[
                f"平均數 = {format_numeric_answer(arithmetic_mean_from_raw(values), rounding)}",
                f"樣本變異數 s² = {format_numeric_answer(var, rounding)}",
                f"樣本標準差 s = {format_numeric_answer(std, rounding)}",
            ],
            answer_shape=answer_shape,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
        )
    else:
        answer_shape = "single_choice" if presentation_mode == "single_choice" else "single_numeric"
        answer_type = "single_choice" if presentation_mode == "single_choice" else "expression"
        answer_text = format_numeric_answer(std, rounding)
        return _matrix_shell(
            givens={
                "raw_values": values,
                "target_measure": "sample_standard_deviation",
                "rounding_policy": rounding,
                "question_text": question,
                "source_choices": list(constraints.get("source_choices") or []),
                "source_answer_label": str(constraints.get("source_answer_label") or "").strip(),
            },
            answer_value=std if presentation_mode != "single_choice" else str(constraints.get("source_answer_label") or answer_text),
            answer_text=str(constraints.get("source_answer_label") or answer_text) if presentation_mode == "single_choice" else answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "sample_standard_deviation",
                "formula": "sample_standard_deviation",
                "sample_variance": var,
                "sample_standard_deviation": std,
                "answer_shape": answer_shape,
            },
            explanation_steps=[
                f"樣本變異數 s² = {format_numeric_answer(var, rounding)}",
                f"樣本標準差 s = {answer_text}"
            ],
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


def _build_linear_transform_median_and_range(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    # We want flat linear transform: y = x + shift
    # Shift should vary by seed: rng.choice([-50, -40, -30, -20, 20, 30, 40, 50])
    shift = rng.choice([-80, -60, -50, -40, -30, -20, 20, 30, 40, 50, 60, 80])
    count = rng.randint(10, 30)

    # Let's generate base values
    base_values = [float(v) for v in generate_raw_values(rng, count=count, low=10, high=100)]
    orig_median = median_from_values(base_values)
    orig_range = range_from_values(base_values)

    new_median = orig_median + shift
    new_range = orig_range

    shift_sign = "+" if shift > 0 else "-"
    shift_abs = abs(shift)

    question = f"有{count}筆資料，在計算時，若把所有數值都{ '加上' if shift > 0 else '減去' }{shift_abs}以後，再計算中位數和全距，則下列何者正確？"

    # Single choice options:
    # A: 新的中位數和全距與原來的都相同
    # B: 新的中位數和全距與原來的都不相同
    # C: 新的中位數與原來的相同，但全距不相同
    # D: 新的全距與原來的相同，但中位數不同
    # Correct is always D since median is shifted (new_median != orig_median), range is same (new_range == orig_range).
    correct_label = "D"
    choices = [
        {"label": "A", "text": "新的中位數和全距與原來的都相同"},
        {"label": "B", "text": "新的中位數和全距與原來的都不相同"},
        {"label": "C", "text": "新的中位數與原來的相同，但全距不相同"},
        {"label": "D", "text": "新的全距與原來的相同，但中位數不同"},
    ]

    return _matrix_shell(
        givens={
            "raw_values": base_values,
            "shift_value": shift,
            "original_median": orig_median,
            "original_range": orig_range,
            "transformed_median": new_median,
            "transformed_range": new_range,
            "question_text": question,
            "choices": choices,
            "source_choices": choices,
            "source_answer_label": correct_label,
            "answer": correct_label,
            "distractors": ["A", "B", "C"],
            "visual_spec": {},
        },
        answer_value=correct_label,
        answer_text=correct_label,
        validation_facts={
            "domain_operation": op,
            "target_measure": "compute_linear_transform_median_and_range",
            "semantic_answer": correct_label,
            "answer_shape": "single_choice",
            "transformed_median": new_median,
            "transformed_range": new_range,
            "original_median": orig_median,
            "original_range": orig_range,
        },
        explanation_steps=[
            f"將所有數值進行平移：y = x {'+' if shift > 0 else '-'} {shift_abs}",
            "新的中位數會隨之平移（改變），即新中位數 = 原中位數 + 平移量",
            "全距代表離散程度（差值），平移後全距保持不變，即新全距 = 原全距",
            "因此，新的全距與原來的相同，但中位數不同，答案選 (D)",
        ],
        answer_shape="single_choice",
        presentation_mode="single_choice",
        answer_type="single_choice",
        ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
    )


def _parse_empirical_params(constraints: dict[str, Any], rng: random.Random) -> tuple[int, float, float]:
    q = str(constraints.get("question_text") or "")
    
    # Try to extract total N (e.g., 2000, 1000, 500)
    m_total = re.search(r"(\d+)\s*(?:個學生|人|名學生|位|名)", q)
    total = int(m_total.group(1)) if m_total else rng.choice([500, 1000, 2000, 5000])
    
    # Try to extract mean (e.g., 平均 55, 平均是 58, 平均為 62)
    m_mean = re.search(r"平均(?:數)?(?:是|為)?\s*(\d+(?:\.\d+)?)", q)
    mean = float(m_mean.group(1)) if m_mean else rng.choice([60.0, 70.0, 80.0])
    
    # Try to extract std (e.g., 標準差 5, 標準差是 4, 標準差為 8)
    m_std = re.search(r"標準差(?:是|為)?\s*(\d+(?:\.\d+)?)", q)
    std = float(m_std.group(1)) if m_std else rng.choice([5.0, 8.0, 10.0])
    
    return total, mean, std


def _build_empirical_rule_probability(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    q_tmpl = str(constraints.get("question_text") or "")
    mu = rng.choice([60, 65, 70, 75, 80, 100])
    sd = rng.choice([5, 8, 10, 12, 15])
    
    if "正負 1" in q_tmpl or "1 個標準差" in q_tmpl or "within_1sd" in q_tmpl:
        question = "常態分配的經驗法則中，落在平均數正負 1 個標準差內的資料約占百分之幾？"
        ans = 68
        explanation = "依據 68-95-99.7 經驗法則，平均數 ±1 個標準差內約含 68% 的資料。"
    elif "正負 2" in q_tmpl or "2 個標準差" in q_tmpl or "within_2sd" in q_tmpl:
        question = "常態分配的經驗法則中，落在平均數正負 2 個標準差內的資料約占百分之幾？"
        ans = 95
        explanation = "依據 68-95-99.7 經驗法則，平均數 ±2 個標準差內約含 95% 的資料。"
    elif "正負 3" in q_tmpl or "3 個標準差" in q_tmpl or "within_3sd" in q_tmpl:
        question = "常態分配的經驗法則中，落在平均數正負 3 個標準差內的資料約占百分之幾（取整數近似）？"
        ans = 99
        explanation = "依據 68-95-99.7 經驗法則，平均數 ±3 個標準差內約含 99.7%（取整數為 99）的資料。"
    elif "之間" in q_tmpl or "percentage" in q_tmpl:
        sd_count = rng.choice([1, 2, 3])
        lo = mu - sd_count * sd
        hi = mu + sd_count * sd
        pct_map = {1: 68, 2: 95, 3: 99}
        ans = pct_map[sd_count]
        question = f"某資料呈常態分配，平均數為 {mu}，標準差為 {sd}。依經驗法則，落在 {lo} 到 {hi} 之間的資料約占百分之幾？"
        explanation = f"區間 [{lo}, {hi}] = 平均數 ±{sd_count} 個標準差，依 68-95-99.7 法則約占 {ans}%。"
    else:
        question = "常態分配的經驗法則中，落在平均數正負 1 個標準差內的資料約占百分之幾？"
        ans = 68
        explanation = "依據 68-95-99.7 經驗法則，平均數 ±1 個標準差內約含 68% 的資料。"

    ans_str = str(ans)
    
    return _matrix_shell(
        givens={
            "question_text": question,
            "target_measure": "empirical_rule_probability",
        },
        answer_value=ans,
        answer_text=ans_str,
        validation_facts={
            "domain_operation": op,
            "target_measure": "empirical_rule_probability",
            "answer_shape": "single_numeric",
        },
        explanation_steps=[explanation],
        answer_shape="single_numeric",
    )


def _build_empirical_rule_population_count(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    q_tmpl = str(constraints.get("question_text") or "")
    total, mean, std = _parse_empirical_params(constraints, rng)
    
    if "50~60" in q_tmpl or "(3) 低於" in q_tmpl or "3856" in str(constraints.get("textbook_example_id", "")):
        lo1 = int(mean - std)
        hi1 = int(mean + std)
        hi2 = int(mean + std)
        lo3 = int(mean - 3 * std)
        
        prob_1 = empirical_rule_central_probability(1)
        prob_2 = empirical_rule_cumulative_probability(1, "above")
        prob_3 = empirical_rule_cumulative_probability(-3, "below")
        
        ans_1 = population_count_from_probability(total, prob_1)
        ans_2 = population_count_from_probability(total, prob_2)
        ans_3 = population_count_from_probability(total, prob_3)
        
        question = f"某校 {total} 個學生，英文成績呈常態分配，平均 {int(mean)} 分，標準差 {int(std)} 分。求：(1) {lo1}~{hi1} 分人數；(2) {hi2} 分以上人數；(3) 低於 {lo3} 分人數。"
        
        field_specs = [
            {"field_key": "part_1", "label": f"{lo1}~{hi1}分人數", "expected_answer": str(ans_1), "input_type": "number"},
            {"field_key": "part_2", "label": f"{hi2}分以上人數", "expected_answer": str(ans_2), "input_type": "number"},
            {"field_key": "part_3", "label": f"低於{lo3}分人數", "expected_answer": str(ans_3), "input_type": "number"},
        ]
        
        answer_val = {"part_1": ans_1, "part_2": ans_2, "part_3": ans_3}
        answer_text = f"(1) {ans_1} 人；(2) {ans_2} 人；(3) {ans_3} 人"
        
        explanation_steps = [
            f"(1) {lo1}~{hi1} 分為平均數 ±1 個標準差內，佔 {int(prob_1*100)}%，人數為 {total} × {prob_1} = {ans_1} 人。",
            f"(2) {hi2} 分以上為平均數 +1 個標準差以上，佔 (1 - 0.68)/2 = {int(prob_2*100)}%，人數為 {total} × {prob_2} = {ans_2} 人。",
            f"(3) 低於 {lo3} 分為平均數 -3 個標準差以下，佔 (1 - 0.997)/2 = {prob_3*100}%，人數為 {total} × {prob_3} = {ans_3} 人。"
        ]
        
        return _matrix_shell(
            givens={
                "question_text": question,
                "field_specs": field_specs,
            },
            answer_value=answer_val,
            answer_text=answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "empirical_rule_population_count",
                "answer_shape": "multi_blank",
            },
            explanation_steps=explanation_steps,
            answer_shape="multi_blank",
            presentation_mode="multi_blank",
            answer_type="multi_part",
            ui_contract={"blank_count": 3, "labels": ["(1)", "(2)", "(3)"], "response_mode": "multi_blank"},
            subquestions=[{"field_key": spec["field_key"], "label": spec["label"], "expected_answer": spec["expected_answer"]} for spec in field_specs],
        )
        
    elif "低於 60" in q_tmpl or "50 分以下" in q_tmpl or "高於 60" in q_tmpl:
        mean_int = int(mean)
        lo2 = int(mean - std)
        lo3 = int(mean - std)
        hi3 = int(mean + std)
        
        prob_1 = 0.5
        prob_2 = empirical_rule_cumulative_probability(-1, "below")
        prob_3 = empirical_rule_central_probability(1)
        
        ans_1 = population_count_from_probability(total, prob_1)
        ans_2 = population_count_from_probability(total, prob_2)
        ans_3 = population_count_from_probability(total, prob_3)
        
        question = f"某校 {total} 個學生，英文成績呈常態分配，平均 {mean_int} 分，標準差 {int(std)} 分。求：(1) 低於 {mean_int} 人數；(2) {lo2} 分以下人數；(3) {lo3}~{hi3} 人數。"
        
        field_specs = [
            {"field_key": "part_1", "label": f"低於{mean_int}人數", "expected_answer": str(ans_1), "input_type": "number"},
            {"field_key": "part_2", "label": f"{lo2}分以下人數", "expected_answer": str(ans_2), "input_type": "number"},
            {"field_key": "part_3", "label": f"{lo3}~{hi3}人數", "expected_answer": str(ans_3), "input_type": "number"},
        ]
        
        answer_val = {"part_1": ans_1, "part_2": ans_2, "part_3": ans_3}
        answer_text = f"(1) {ans_1} 人；(2) {ans_2} 人；(3) {ans_3} 人"
        
        explanation_steps = [
            f"(1) 低於平均數 {mean_int} 分佔 50%，人數為 {total} × 0.5 = {ans_1} 人。",
            f"(2) {lo2} 分以下為平均數 -1 個標準差以下，佔 (1 - 0.68)/2 = 16%，人數為 {total} × 0.16 = {ans_2} 人。",
            f"(3) {lo3}~{hi3} 分為平均數 ±1 個標準差內，佔 68%，人數為 {total} × 0.68 = {ans_3} 人。"
        ]
        
        return _matrix_shell(
            givens={
                "question_text": question,
                "field_specs": field_specs,
            },
            answer_value=answer_val,
            answer_text=answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "empirical_rule_population_count",
                "answer_shape": "multi_blank",
            },
            explanation_steps=explanation_steps,
            answer_shape="multi_blank",
            presentation_mode="multi_blank",
            answer_type="multi_part",
            ui_contract={"blank_count": 3, "labels": ["(1)", "(2)", "(3)"], "response_mode": "multi_blank"},
            subquestions=[{"field_key": spec["field_key"], "label": spec["label"], "expected_answer": spec["expected_answer"]} for spec in field_specs],
        )

    elif "45~65" in q_tmpl or "45到65" in q_tmpl or "65" in q_tmpl:
        lo1 = int(mean - 2 * std)
        hi1 = int(mean + 2 * std)
        lo2 = int(mean - std)
        
        prob_1 = empirical_rule_central_probability(2)
        prob_2 = empirical_rule_cumulative_probability(-1, "below")
        
        ans_1 = population_count_from_probability(total, prob_1)
        ans_2 = population_count_from_probability(total, prob_2)
        
        question = f"某校 {total} 個學生，英文成績呈常態分配，平均 {int(mean)} 分，標準差 {int(std)} 分。求：(1) {lo1}~{hi1} 分人數；(2) {lo2} 分以下人數。"
        
        field_specs = [
            {"field_key": "part_1", "label": f"{lo1}~{hi1}分人數", "expected_answer": str(ans_1), "input_type": "number"},
            {"field_key": "part_2", "label": f"{lo2}分以下人數", "expected_answer": str(ans_2), "input_type": "number"},
        ]
        
        answer_val = {"part_1": ans_1, "part_2": ans_2}
        answer_text = f"(1) {ans_1} 人；(2) {ans_2} 人"
        
        explanation_steps = [
            f"(1) {lo1}~{hi1} 分為平均數 ±2 個標準差內，佔 95%，人數為 {total} × 0.95 = {ans_1} 人。",
            f"(2) {lo2} 分以下為平均數 -1 個標準差以下，佔 (1 - 0.68)/2 = 16%，人數為 {total} × 0.16 = {ans_2} 人。"
        ]
        
        return _matrix_shell(
            givens={
                "question_text": question,
                "field_specs": field_specs,
            },
            answer_value=answer_val,
            answer_text=answer_text,
            validation_facts={
                "domain_operation": op,
                "target_measure": "empirical_rule_population_count",
                "answer_shape": "multi_blank",
            },
            explanation_steps=explanation_steps,
            answer_shape="multi_blank",
            presentation_mode="multi_blank",
            answer_type="multi_part",
            ui_contract={"blank_count": 2, "labels": ["(1)", "(2)"], "response_mode": "multi_blank"},
            subquestions=[{"field_key": spec["field_key"], "label": spec["label"], "expected_answer": spec["expected_answer"]} for spec in field_specs],
        )

    elif "之間" in q_tmpl or "介於" in q_tmpl or "到" in q_tmpl:
        lo = int(mean - std)
        hi = int(mean + std)
        
        prob = empirical_rule_central_probability(1)
        ans = population_count_from_probability(total, prob)
        
        question = f"某{total}名學生第一次數學段考成績平均是{int(mean)}，標準差是{int(std)}，若成績呈常態分配，則成績在{lo}分到{hi}分之間的學生約有幾人？"
        
        choices = [
            {"label": "A", "text": str(population_count_from_probability(total, 0.34))},
            {"label": "B", "text": str(population_count_from_probability(total, 0.50))},
            {"label": "C", "text": str(ans)},
            {"label": "D", "text": str(population_count_from_probability(total, 0.80))},
        ]
        correct_label = "C"
        
        explanation = f"成績在 {lo}~{hi} 分之間為平均數 ±1 個標準差內，佔約 68%。學生人數約有 {total} × 0.68 = {ans} 人。故選 (C)。"
        
        return _matrix_shell(
            givens={
                "question_text": question,
                "choices": choices,
                "source_choices": choices,
                "source_answer_label": correct_label,
            },
            answer_value=correct_label,
            answer_text=correct_label,
            validation_facts={
                "domain_operation": op,
                "target_measure": "empirical_rule_population_count",
                "answer_shape": "single_choice",
            },
            explanation_steps=[explanation],
            answer_shape="single_choice",
            presentation_mode="single_choice",
            answer_type="single_choice",
            ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
        )

    else:
        # Default Template E (including src_3898)
        hi = int(mean + std)
        prob = empirical_rule_cumulative_probability(1, "below")
        ans = population_count_from_probability(total, prob)
        
        question = f"某數學考試共 {total} 人參加。若成績呈常態分配，平均為 {int(mean)}，標準差為 {int(std)}，則成績低於 {hi} 分的約有幾人？"
        
        choices = [
            {"label": "A", "text": f"{ans-259}人到{ans-180}人"},
            {"label": "B", "text": f"{ans-179}人到{ans-100}人"},
            {"label": "C", "text": f"{ans-99}人到{ans-20}人"},
            {"label": "D", "text": f"{ans-19}人到{ans+60}人"},
        ]
        correct_label = "D"
        
        explanation = f"成績低於 {hi} 分即低於平均數 +1 個標準差（{int(mean)} + {int(std)} = {hi}）。由經驗法則，低於此分數的資料約占 50% + 34% = 84%。人數為 {total} × 0.84 = {ans} 人，落在 {ans-19}~{ans+60} 的區間。故選 (D)。"
        
        return _matrix_shell(
            givens={
                "question_text": question,
                "choices": choices,
                "source_choices": choices,
                "source_answer_label": correct_label,
            },
            answer_value=correct_label,
            answer_text=correct_label,
            validation_facts={
                "domain_operation": op,
                "target_measure": "empirical_rule_population_count",
                "answer_shape": "single_choice",
            },
            explanation_steps=[explanation],
            answer_shape="single_choice",
            presentation_mode="single_choice",
            answer_type="single_choice",
            ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
        )


def _build_compare_distribution_spread(rng: random.Random, constraints: dict[str, Any], op: str) -> dict[str, Any]:
    import matplotlib.pyplot as plt
    import io
    import base64
    import math
    
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=120)
    try:
        xs = [40.0 + i * 0.3 for i in range(201)]
        ys_a = [(1.0 / (6.0 * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - 70.0) / 6.0) ** 2) for x in xs]
        ys_b = [(1.0 / (12.0 * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - 70.0) / 12.0) ** 2) for x in xs]
        
        ax.plot(xs, ys_a, label="甲班", color="blue", linewidth=2)
        ax.plot(xs, ys_b, label="乙班", color="red", linewidth=2, linestyle="--")
        
        ax.set_title("甲、乙兩班成績分布圖")
        ax.set_xlabel("成績")
        ax.set_ylabel("機率密度")
        ax.legend(loc="upper right")
        ax.grid(linestyle="--", alpha=0.5)
        
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        image_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    finally:
        plt.close(fig)
        
    question = "某學校期末考，甲、乙兩班成績分布呈常態分配，如圖所示。下列關於甲、乙兩班成績的敘述何者正確？"
    
    choices = [
        {"label": "A", "text": "甲班的平均數較大"},
        {"label": "B", "text": "乙班的平均數較大"},
        {"label": "C", "text": "甲班的標準差較大"},
        {"label": "D", "text": "乙班的標準差較大"},
    ]
    correct_label = "D"
    
    return _matrix_shell(
        givens={
            "question_text": question,
            "choices": choices,
            "source_choices": choices,
            "source_answer_label": correct_label,
            "image_base64": image_base64,
        },
        answer_value=correct_label,
        answer_text=correct_label,
        validation_facts={
            "domain_operation": op,
            "target_measure": "compare_distribution_spread",
            "semantic_answer": correct_label,
            "answer_shape": "single_choice",
        },
        explanation_steps=[
            "觀察圖形，甲班與乙班的對稱中心都在 70，表示兩班的平均數相同。",
            "乙班的分布較甲班平緩且分散，表示乙班成績的離散程度較大。",
            "因此，乙班的標準差較大，答案選 (D)。",
        ],
        answer_shape="single_choice",
        presentation_mode="single_choice",
        answer_type="single_choice",
        ui_contract={"response_mode": "single_choice", "text_input_enabled": False},
        table_data={"image_base64": image_base64},
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
    "compute_sample_variance": _build_sample_variance,
    "compute_sample_standard_deviation": _build_sample_stddev,
    "complete_descriptive_statistics_table": _build_table_completion,
    "compute_quartiles_and_iqr": _build_quartiles_and_iqr,
    "compare_dispersion": _build_compare_dispersion,
    "conceptual_dispersion_judgment": _build_conceptual_dispersion_judgment,
    "compute_linear_transform_median_and_range": _build_linear_transform_median_and_range,
    "empirical_rule_probability": _build_empirical_rule_probability,
    "empirical_rule_population_count": _build_empirical_rule_population_count,
    "compare_distribution_spread": _build_compare_distribution_spread,
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
        "compute_sample_variance": ("sample_variance",),
        "compute_sample_standard_deviation": ("sample_standard_deviation", "sample_variance"),
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
        "compute_linear_transform_median_and_range": ("median", "range"),
        "empirical_rule_probability": ("empirical_rule_probability",),
        "empirical_rule_population_count": ("empirical_rule_population_count",),
        "compare_distribution_spread": ("compare_distribution_spread",),
    }
    return mapping.get(operation, ("descriptive_statistics",))
