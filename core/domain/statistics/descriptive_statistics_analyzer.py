"""Professional semantic analysis for statistics.descriptive_statistics domain."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from core.domain.statistics.descriptive_statistics_domain import DOMAIN_KEY
from core.gencode.v3_presentation_inference import (
    has_abcd_choice_group,
    parse_abcd_choices_from_text,
)
from core.registry.domain_operation_registry import get_domain_spec

_TABLE_TEXT_HINTS = ("完成下表", "填寫", "統計量", "下表")
_FREQUENCY_TEXT_HINTS = ("次數", "頻率", "frequency", "分配表")
_WEIGHT_TEXT_HINTS = ("權重", "加權", "學分", "weight")

_CAPABILITY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"平均(?:數|分|成績|身高)|算術平均|arithmetic\s*mean|\\bar\{x\}|μ", re.I), "arithmetic_mean"),
    (re.compile(r"加權平均|weighted\s*mean|權數|乘以\s*\d+\s*%", re.I), "weighted_mean"),
    (re.compile(r"中位數|median", re.I), "median"),
    (re.compile(r"眾數|mode", re.I), "mode"),
    (re.compile(r"全距|range", re.I), "range"),
    (re.compile(r"四分位距|\bIQR\b", re.I), "interquartile_range"),
    (re.compile(r"四分位數|\bQ1\b|\bQ3\b", re.I), "quartile"),
    (re.compile(r"比較.*離散|離散程度", re.I), "dispersion_comparison"),
    (re.compile(r"樣本變異數|sample\s*variance|s\^2", re.I), "sample_variance"),
    (re.compile(r"樣本標準差|sample\s*standard\s*deviation|\bs(?!²)\b", re.I), "sample_standard_deviation"),
    (re.compile(r"方差|variance|σ\^?2", re.I), "variance"),
    (re.compile(r"標準差|standard\s*deviation|σ(?!²)", re.I), "standard_deviation"),
    (re.compile(r"完成下表|填寫.*表|統計量.*表", re.I), "descriptive_statistics_table_completion"),
    (re.compile(r"常態分配|常態分布|常態分佈|經驗法則|empirical\s*rule|normal\s*distribution", re.I), "empirical_rule_probability"),
)

_PRIMARY_OPERATION_BY_PROBLEM_TYPE: dict[str, str] = {
    "quartiles_and_iqr": "compute_quartiles_and_iqr",
    "quartiles_and_iqr_computation": "compute_quartiles_and_iqr",
    "range_and_iqr": "compute_quartiles_and_iqr",
    "range_and_iqr_computation": "compute_quartiles_and_iqr",
    "dispersion_comparison": "compare_dispersion",
    "dispersion_comparison_computation": "compare_dispersion",
    "conceptual_dispersion_judgment": "conceptual_dispersion_judgment",
    "conceptual_dispersion_judgment_computation": "conceptual_dispersion_judgment",
    "standard_deviation": "compute_population_standard_deviation",
    "standard_deviation_computation": "compute_population_standard_deviation",
    "sample_standard_deviation": "compute_sample_standard_deviation",
    "sample_standard_deviation_computation": "compute_sample_standard_deviation",
    "range": "compute_range",
    "range_computation": "compute_range",
    "variance": "compute_population_variance",
    "variance_computation": "compute_population_variance",
    "sample_variance": "compute_sample_variance",
    "sample_variance_computation": "compute_sample_variance",
    "arithmetic_mean": "compute_arithmetic_mean_from_raw_values",
    "arithmetic_mean_computation": "compute_arithmetic_mean_from_raw_values",
    "weighted_mean": "compute_weighted_mean",
    "weighted_mean_computation": "compute_weighted_mean",
    "median": "compute_median_from_raw_values",
    "median_computation": "compute_median_from_raw_values",
    "mode": "compute_mode_from_raw_values",
    "mode_computation": "compute_mode_from_raw_values",
    "descriptive_statistics_table_completion": "complete_descriptive_statistics_table",
    "descriptive_statistics_table_completion_computation": "complete_descriptive_statistics_table",
    "empirical_rule_probability": "empirical_rule_probability",
    "empirical_rule_probability_computation": "empirical_rule_probability",
    "empirical_rule_population_count": "empirical_rule_population_count",
    "empirical_rule_population_count_computation": "empirical_rule_population_count",
    "compare_distribution_spread": "compare_distribution_spread",
    "compare_distribution_spread_computation": "compare_distribution_spread",
}


@dataclass(frozen=True)
class DescriptiveStatisticsAnalysis:
    status: str
    problem_type_id: str
    required_capabilities: tuple[str, ...]
    selected_operation: str | None
    presentation_mode: str
    answer_shape: str
    missing_capabilities: tuple[str, ...] = ()
    suggested_action: str | None = None
    classification_source: str = "descriptive_statistics_domain_analyzer"
    fixed_domain_key: str = DOMAIN_KEY


def _normalize_capabilities(capabilities: list[str] | tuple[str, ...] | None) -> list[str]:
    caps = list(capabilities or [])
    if "weighted_mean" in caps and "arithmetic_mean" in caps:
        caps = [cap for cap in caps if cap != "arithmetic_mean"]
    if "sample_standard_deviation" in caps and "standard_deviation" in caps:
        caps = [cap for cap in caps if cap != "standard_deviation"]
    if "sample_variance" in caps and "variance" in caps:
        caps = [cap for cap in caps if cap != "variance"]
    if "standard_deviation" in caps and "variance" in caps:
        caps = [cap for cap in caps if cap != "variance"]
    if "sample_standard_deviation" in caps and "sample_variance" in caps:
        caps = [cap for cap in caps if cap != "sample_variance"]
    if {"standard_deviation", "variance", "sample_standard_deviation", "sample_variance"} & set(caps):
        caps = [cap for cap in caps if cap != "arithmetic_mean"]
    return caps


def _registry_capabilities() -> set[str]:
    spec = get_domain_spec(DOMAIN_KEY)
    if spec is None:
        return set()
    return set(spec.capabilities)


def _infer_capabilities_from_text(text: str) -> list[str]:
    normalized = str(text or "")
    caps: list[str] = []
    for pattern, capability in _CAPABILITY_PATTERNS:
        if pattern.search(normalized) and capability not in caps:
            caps.append(capability)
    return _normalize_capabilities(caps)


def _has_domain_signals(text: str) -> bool:
    return bool(_infer_capabilities_from_text(text))


def _infer_answer_shape(
    *,
    presentation_mode: str,
    required_capabilities: list[str],
    question_text: str,
) -> str:
    mode = str(presentation_mode or "short_answer").strip()
    if mode == "single_choice":
        return "single_choice"
    if "descriptive_statistics_table_completion" in required_capabilities and any(
        hint in question_text for hint in _TABLE_TEXT_HINTS
    ):
        return "table_fill"
    if len(required_capabilities) > 1 and any(
        cap in required_capabilities
        for cap in ("dispersion_comparison", "quartile", "interquartile_range", "range")
    ):
        if re.search(r"[\(（]\s*(?:1|2|女生|男生)", question_text):
            return "multi_part"
    if any(cap in required_capabilities for cap in ("empirical_rule_probability", "empirical_rule_population_count")):
        if re.search(r"[\(（]\s*(?:1|2)\s*[\)）]", question_text) or mode == "multi_blank":
            return "multi_blank"
    return "single_numeric"


def _infer_task_classification(
    *,
    question_text: str,
    combined_text: str,
    presentation_mode: str,
) -> tuple[str, list[str]] | None:
    text = str(combined_text or "")
    stem = str(question_text or "")
    mode = str(presentation_mode or "short_answer").strip()

    is_normal = bool(re.search(r"常態分配|常態分布|常態分佈|normal\s*distribution", text))
    is_compare_spread = bool(re.search(r"如圖所示|成績直方圖", stem) and re.search(r"平均.*較大|標準差.*較大|平均比|標準差比", text))
    if is_normal or is_compare_spread:
        if is_compare_spread or re.search(r"如圖|比較|圖中|標準差較大|標準差大小|離散程度", text):
            return "compare_distribution_spread", ["compare_distribution_spread"]
        if re.search(r"人|個|戶|隻|個數|人數", stem) and re.search(r"幾|多少|約有|求|為何", stem):
            return "empirical_rule_population_count", ["empirical_rule_population_count"]
        return "empirical_rule_probability", ["empirical_rule_probability"]

    if mode == "single_choice":
        if re.search(r"哪一種統計量|應用了下列哪一種|觀念", stem) and re.search(
            r"價差|全距|離散|分散|標準差|四分位",
            text,
        ):
            if not re.search(r"母體標準差|計算.*標準差|分別為", stem):
                return "conceptual_dispersion_judgment", ["conceptual_dispersion_judgment"]
        if re.search(r"母體標準差|標準差", text) and re.search(r"\d", stem):
            return "standard_deviation_computation", ["standard_deviation"]

    if any(hint in stem for hint in _TABLE_TEXT_HINTS) and re.search(r"表|統計量", stem):
        return "descriptive_statistics_table_completion", ["descriptive_statistics_table_completion"]

    has_iqr = bool(re.search(r"IQR|四分位距", text, re.I))
    has_range = bool(re.search(r"全距|\bR\b", text))
    has_two_groups = bool(re.search(r"[\(（]\s*2\s*[\)）]|女生|男生|兩組", stem))
    has_compare = bool(re.search(r"比較.*離散|離散程度", text))

    if has_iqr and has_range:
        caps = ["range", "quartile", "interquartile_range"]
        if has_compare or (
            has_two_groups
            and re.search(r"女生|男生|桌球|籃球|體重|身高", stem)
            and not re.search(r"試求下列兩組", stem)
        ):
            return "dispersion_comparison", ["dispersion_comparison", *caps]
        return "quartiles_and_iqr_computation", caps
    if has_iqr and re.search(r"\bR\b", stem):
        caps = ["range", "quartile", "interquartile_range"]
        if has_compare or (
            has_two_groups
            and re.search(r"女生|男生|桌球|籃球|體重|身高", stem)
            and not re.search(r"試求下列兩組", stem)
        ):
            return "dispersion_comparison", ["dispersion_comparison", *caps]
        return "quartiles_and_iqr_computation", caps

    caps = _infer_capabilities_from_text(text)
    if not caps:
        return None

    priority = (
        "conceptual_dispersion_judgment",
        "dispersion_comparison",
        "descriptive_statistics_table_completion",
        "weighted_mean",
        "sample_standard_deviation",
        "sample_variance",
        "standard_deviation",
        "variance",
        "median",
        "mode",
        "interquartile_range",
        "quartile",
        "range",
        "arithmetic_mean",
    )
    for cap in priority:
        if cap in caps:
            if cap in {
                "conceptual_dispersion_judgment",
                "dispersion_comparison",
                "descriptive_statistics_table_completion",
            }:
                return cap, list(caps)
            return f"{cap}_computation", list(caps)
    return f"{caps[0]}_computation", caps


def resolve_descriptive_operation(
    *,
    required_capabilities: list[str] | tuple[str, ...],
    problem_type_id: str = "",
    question_text: str = "",
    presentation_mode: str = "",
    answer_shape: str = "",
    field_specs: list[dict[str, Any]] | None = None,
) -> str | None:
    """Select a registered descriptive-statistics operation; never default to table completion."""
    spec = get_domain_spec(DOMAIN_KEY)
    if spec is None:
        return None

    required = _normalize_capabilities(list(required_capabilities))
    registry_caps = set(spec.capabilities)
    required = [cap for cap in required if cap in registry_caps]
    if not required:
        return None

    required_set = set(required)
    if "empirical_rule_probability" in required_set:
        return "empirical_rule_probability"
    if "empirical_rule_population_count" in required_set:
        return "empirical_rule_population_count"
    if "compare_distribution_spread" in required_set:
        return "compare_distribution_spread"

    allowed = set(spec.operations.keys())
    pt = str(problem_type_id or "").strip().lower()
    primary = _PRIMARY_OPERATION_BY_PROBLEM_TYPE.get(pt)
    if not primary and pt.endswith("_computation"):
        primary = _PRIMARY_OPERATION_BY_PROBLEM_TYPE.get(pt[: -len("_computation")])

    if primary and primary in allowed:
        provided = set(spec.operations[primary].provided_capabilities or ())
        if set(required).issubset(provided):
            return primary

    required_set = set(required)
    if "conceptual_dispersion_judgment" in required_set:
        op = "conceptual_dispersion_judgment"
        if op in allowed:
            return op
    if "dispersion_comparison" in required_set:
        op = "compare_dispersion"
        if op in allowed:
            return op
    if {"quartile", "interquartile_range"} & required_set or "interquartile_range" in required_set:
        op = "compute_quartiles_and_iqr"
        if op in allowed and set(required).issubset(set(spec.operations[op].provided_capabilities or ())):
            return op
    if required_set <= {"sample_standard_deviation", "sample_variance"} and "sample_standard_deviation" in required_set:
        op = "compute_sample_standard_deviation"
        if op in allowed:
            return op
    if required_set == {"median", "range"}:
        return "compute_linear_transform_median_and_range" if "compute_linear_transform_median_and_range" in allowed else None
    if required_set == {"sample_variance"}:
        return "compute_sample_variance" if "compute_sample_variance" in allowed else None
    if required_set <= {"standard_deviation", "variance"} and "standard_deviation" in required_set:
        op = "compute_population_standard_deviation"
        if op in allowed:
            return op
    if required_set == {"variance"}:
        return "compute_population_variance" if "compute_population_variance" in allowed else None
    if required_set == {"range"}:
        return "compute_range" if "compute_range" in allowed else None
    if required_set == {"arithmetic_mean"}:
        question = str(question_text or "")
        if any(hint in question for hint in _FREQUENCY_TEXT_HINTS):
            op = "compute_arithmetic_mean_from_frequency_table"
        else:
            op = "compute_arithmetic_mean_from_raw_values"
        if op in allowed:
            return op
    if required_set == {"weighted_mean"}:
        return "compute_weighted_mean" if "compute_weighted_mean" in allowed else None
    if required_set == {"median"}:
        return "compute_median_from_raw_values" if "compute_median_from_raw_values" in allowed else None
    if required_set == {"mode"}:
        question = str(question_text or "")
        if any(hint in question for hint in _FREQUENCY_TEXT_HINTS):
            op = "compute_mode_from_frequency_table"
        else:
            op = "compute_mode_from_raw_values"
        if op in allowed:
            return op

    question = str(question_text or "")
    if (
        "descriptive_statistics_table_completion" in required_set
        and (field_specs or str(answer_shape or "").strip() in {"table_fill", "multi_blank"})
        and any(hint in question for hint in _TABLE_TEXT_HINTS)
    ):
        op = "complete_descriptive_statistics_table"
        if op in allowed:
            return op

    candidates: list[tuple[str, set[str]]] = []
    for op_key, op_spec in spec.operations.items():
        provided = set(op_spec.provided_capabilities or ())
        if not required_set.issubset(provided):
            continue
        if op_key == "complete_descriptive_statistics_table":
            if "descriptive_statistics_table_completion" not in required_set:
                continue
            if not any(hint in question for hint in _TABLE_TEXT_HINTS):
                continue
        candidates.append((op_key, provided))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][0]

    scored: list[tuple[int, str]] = []
    for op_key, provided in candidates:
        score = len(required_set & provided)
        if op_key == "complete_descriptive_statistics_table":
            score -= 100
        if op_key in {
            "compute_quartiles_and_iqr",
            "compare_dispersion",
            "conceptual_dispersion_judgment",
        }:
            score += 30
        if "frequency_table" in op_key and any(hint in question for hint in _FREQUENCY_TEXT_HINTS):
            score += 20
        if "weighted_mean" in op_key and any(hint in question for hint in _WEIGHT_TEXT_HINTS):
            score += 20
        scored.append((score, op_key))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][1]


def _missing_capabilities(required: list[str], operation: str | None) -> list[str]:
    spec = get_domain_spec(DOMAIN_KEY)
    if spec is None or not operation:
        return list(required)
    op_spec = spec.operations.get(operation)
    if op_spec is None:
        return list(required)
    provided = set(op_spec.provided_capabilities or ())
    return sorted(set(required) - provided)


def analyze_textbook_row(
    row: dict[str, Any],
    *,
    presentation_mode: str = "short_answer",
) -> DescriptiveStatisticsAnalysis | None:
    """Analyze one textbook row; None when stem is outside descriptive statistics."""
    question_text = str(row.get("problem_text") or "")
    answer_text = str(row.get("correct_answer") or "")
    explanation_text = str(row.get("detailed_solution") or row.get("explanation") or "")
    combined_text = " ".join(part for part in (question_text, answer_text, explanation_text) if part)
    if not combined_text.strip():
        return None
    if not _has_domain_signals(combined_text):
        return None

    task = _infer_task_classification(
        question_text=question_text,
        combined_text=combined_text,
        presentation_mode=presentation_mode,
    )
    if task is None:
        return None
    problem_type_id, required_caps = task
    answer_shape = _infer_answer_shape(
        presentation_mode=presentation_mode,
        required_capabilities=required_caps,
        question_text=question_text,
    )
    selected_operation = resolve_descriptive_operation(
        required_capabilities=required_caps,
        problem_type_id=problem_type_id,
        question_text=question_text,
        presentation_mode=presentation_mode,
        answer_shape=answer_shape,
    )
    missing = _missing_capabilities(required_caps, selected_operation)
    if missing or not selected_operation:
        return DescriptiveStatisticsAnalysis(
            status="gap",
            problem_type_id=problem_type_id,
            required_capabilities=tuple(required_caps),
            selected_operation=selected_operation,
            presentation_mode=presentation_mode,
            answer_shape=answer_shape,
            missing_capabilities=tuple(missing or required_caps),
            suggested_action="extend_existing_domain",
        )
    return DescriptiveStatisticsAnalysis(
        status="resolved",
        problem_type_id=problem_type_id,
        required_capabilities=tuple(required_caps),
        selected_operation=selected_operation,
        presentation_mode=presentation_mode,
        answer_shape=answer_shape,
    )


def classify_textbook_example(source: Any) -> dict[str, Any] | None:
    """Classifier hook for v3_example_semantic_classifier (fixed descriptive domain)."""
    row = {
        "problem_text": getattr(source, "question_text", "") or "",
        "correct_answer": getattr(source, "answer", "") or "",
        "detailed_solution": getattr(source, "explanation", "") or "",
    }
    presentation_mode = str(getattr(source, "presentation_mode", None) or "short_answer")
    analysis = analyze_textbook_row(row, presentation_mode=presentation_mode)
    if analysis is None:
        return None
    if analysis.status == "gap":
        return None
    answer_type = "single_choice" if analysis.presentation_mode == "single_choice" else "expression"
    if analysis.answer_shape == "multi_part":
        answer_type = "multi_part"
    elif analysis.answer_shape == "multi_blank":
        answer_type = "multi_blank"
    return {
        "selected_operation": analysis.selected_operation,
        "problem_type_id": analysis.problem_type_id,
        "math_family": "descriptive_statistics",
        "task_intent": analysis.problem_type_id,
        "presentation_mode": analysis.presentation_mode,
        "answer_type": answer_type,
        "answer_shape": analysis.answer_shape,
        "required_domain_capabilities": list(analysis.required_capabilities),
        "required_capabilities": list(analysis.required_capabilities),
        "confidence": 1.0,
        "classification_source": analysis.classification_source,
        "fixed_domain_key": DOMAIN_KEY,
    }


def extract_textbook_constraints(row: dict[str, Any] | None) -> dict[str, Any]:
    """Extract textbook datasets / choice material for matrix generation."""
    if not isinstance(row, dict):
        return {}
    problem_text = str(row.get("problem_text") or "")
    if not problem_text.strip():
        return {}

    out: dict[str, Any] = {"question_text": problem_text}
    correct_answer = str(row.get("correct_answer") or "").strip()
    if correct_answer and correct_answer not in {"略", "无", "無", "N/A", "n/a"}:
        out["source_answer_text"] = correct_answer

    label_map = {"1": "組別1", "2": "組別2", "女生": "女生", "男生": "男生"}
    group_re = re.compile(
        r"[\(（]\s*(?P<label>\d+|女生|男生)\s*[\)）]\s*(?:[：:])?\s*(?P<data>[\d\s,，、.+-]+)"
    )
    datasets: list[dict[str, Any]] = []
    for match in group_re.finditer(problem_text):
        label = label_map.get(str(match.group("label")), f"組別{match.group('label')}")
        nums = [float(token) for token in re.findall(r"-?\d+(?:\.\d+)?", str(match.group("data") or ""))]
        if nums:
            datasets.append({"label": label, "raw_values": nums})
    if datasets:
        out["datasets"] = datasets

    if re.search(r"母體標準差|標準差|變異數", problem_text):
        score_tokens = re.findall(r"(\d+)\s*分", problem_text)
        if score_tokens:
            out["raw_values"] = [float(token) for token in score_tokens]
        else:
            # Only extract the data segment after the data-list delimiter (：/: followed by numbers)
            # This prevents narrative numbers like "10 位", "2025 年", "例題 7" from leaking in.
            data_segment_match = re.search(
                r"[：:﹕]\s*([\d\s,，、.+\-]+?)(?:[，。]|試求|求|則|$)", problem_text
            )
            if data_segment_match:
                nums = [
                    float(t) for t in re.findall(r"-?\d+(?:\.\d+)?", data_segment_match.group(1))
                ]
                if 3 <= len(nums) <= 15:
                    out["raw_values"] = nums
                    # Carry the expected count so domain builder can validate length
                    count_match = re.search(r"(\d+)\s*(?:位|人|名|個|筆)", problem_text)
                    if count_match:
                        stated_count = int(count_match.group(1))
                        # Only trust stated count when it matches extracted length
                        if stated_count == len(nums):
                            out["count"] = stated_count

    if has_abcd_choice_group(problem_text):
        choices = parse_abcd_choices_from_text(problem_text)
        if choices:
            out["source_choices"] = choices
            answer_label = correct_answer.strip().upper()
            if re.fullmatch(r"[A-D]", answer_label):
                out["source_answer_label"] = answer_label
                stem = re.split(r"[\(（]\s*A\s*[\)）]", problem_text, maxsplit=1)[0].strip()
                if re.search(r"哪一種統計量|應用了下列哪一種", problem_text):
                    out["concept_scenarios"] = [
                        {
                            "story": stem,
                            "target_statistic": "range",
                            "correct_label": answer_label,
                            "choices": choices,
                        }
                    ]
    return out
