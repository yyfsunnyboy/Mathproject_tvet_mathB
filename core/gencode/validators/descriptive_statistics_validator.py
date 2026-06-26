"""Integrity checks for descriptive statistics domain payloads."""

from __future__ import annotations

import math
from typing import Any

from core.domain.statistics.descriptive_statistics_core import (
    arithmetic_mean_from_frequency,
    arithmetic_mean_from_raw,
    median_from_values,
    mode_from_values,
    population_standard_deviation,
    population_variance,
    range_and_iqr_summary,
    range_from_values,
    weighted_mean_from_pairs,
    sample_variance,
    sample_standard_deviation,
)
from core.gencode.checker_registry import CHECKER_CAPABILITIES
from core.gencode.descriptive_statistics_answer_contract import (
    NO_MODE_SENTINEL,
    validate_contract_dispatchable,
)

_DESCRIPTIVE_OPS = frozenset(
    {
        "compute_arithmetic_mean_from_raw_values",
        "compute_arithmetic_mean_from_frequency_table",
        "compute_weighted_mean",
        "compute_median_from_raw_values",
        "compute_mode_from_raw_values",
        "compute_mode_from_frequency_table",
        "compute_range",
        "compute_population_variance",
        "compute_population_standard_deviation",
        "compute_sample_variance",
        "compute_sample_standard_deviation",
        "complete_descriptive_statistics_table",
        "compute_quartiles_and_iqr",
        "compare_dispersion",
        "conceptual_dispersion_judgment",
    }
)


def _givens(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    givens = meta.get("givens") if isinstance(meta.get("givens"), dict) else {}
    return givens


def _facts(payload: dict[str, Any]) -> dict[str, Any]:
    facts = payload.get("validation_facts")
    if isinstance(facts, dict):
        return facts
    math_core = payload.get("math_core")
    if isinstance(math_core, dict) and isinstance(math_core.get("validation_facts"), dict):
        return math_core["validation_facts"]
    return {}


def _operation(payload: dict[str, Any]) -> str:
    return str(
        payload.get("domain_operation")
        or payload.get("selected_operation")
        or payload.get("problem_type_id")
        or _facts(payload).get("domain_operation")
        or ""
    ).strip()


def validate_descriptive_statistics_payload(payload: dict[str, Any]) -> list[str]:
    op = _operation(payload)
    if op not in _DESCRIPTIVE_OPS:
        return []

    errors: list[str] = []
    givens = _givens(payload)
    facts = _facts(payload)
    question = str(payload.get("question_text") or givens.get("question_text") or "")
    answer_shape = str(payload.get("answer_shape") or facts.get("answer_shape") or "")
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}

    for field in ("question_text", "answer", "answer_type", "answer_contract", "presentation_mode", "metadata"):
        if payload.get(field) in (None, "", {}):
            errors.append(f"required_payload_fields: missing {field}")

    if not str(payload.get("fixed_domain_key") or meta.get("fixed_domain_key") or "").strip():
        errors.append("required_payload_fields: missing fixed_domain_key")
    if not str(payload.get("selected_operation") or meta.get("selected_operation") or "").strip():
        errors.append("required_payload_fields: missing selected_operation")

    resolution = payload.get("domain_resolution") or meta.get("domain_resolution")
    if not isinstance(resolution, dict) or not resolution.get("fixed_domain_key"):
        errors.append("domain_evidence_complete: domain_resolution missing")
    else:
        req_caps = resolution.get("required_capabilities") or []
        supported_caps = {
            "arithmetic_mean",
            "weighted_mean",
            "median",
            "mode",
            "range",
            "variance",
            "standard_deviation",
            "sample_variance",
            "sample_standard_deviation",
            "descriptive_statistics_table_completion",
            "descriptive_statistics",
            "dispersion_comparison",
            "conceptual_dispersion_judgment",
            "frequency_weighted_statistics",
        }
        for cap in req_caps:
            if cap not in supported_caps:
                errors.append(f"unresolved_capability: {cap}")

    if ("變異數" in question) and ("標準差" in question):
        if answer_shape != "multi_field" and answer_shape != "multi_part":
            errors.append("answer_shape_consistency: both variance and standard deviation requested, must use multi_field/multi_part")

    checker_key = str(ac.get("checker_key") or ac.get("checker") or "").strip()
    if not checker_key or checker_key not in CHECKER_CAPABILITIES:
        errors.append("answer_contract_registered: checker_key missing or unknown")
    else:
        errors.extend(f"checker_dispatchable:{item}" for item in validate_contract_dispatchable(ac))

    if answer_shape == "single_numeric" and checker_key in {"expression_checker", "text_short_checker"}:
        errors.append("answer_shape_consistency: single_numeric must not use expression/text checker")

    if answer_shape == "unordered_set" and checker_key not in {
        "unordered_set_checker",
        "solution_set_checker",
        "set_checker",
    }:
        errors.append("answer_shape_consistency: unordered_set requires set checker")

    if answer_shape == "text_short":
        answer_text = str(payload.get("answer") or payload.get("correct_answer") or "")
        if not answer_text.strip():
            errors.append("answer_shape_consistency: text_short answer empty")
        if answer_text.strip() in {"[]", "none", "None", "無"}:
            errors.append("answer_shape_consistency: text_short must use canonical sentinel")

    raw_values = givens.get("raw_values") or []
    if raw_values and not givens.get("value_frequency_pairs"):
        visible = any(
            str(int(v)) in question or format(float(v), "g") in question
            for v in raw_values[: min(5, len(raw_values))]
        )
        if not visible:
            errors.append("givens_visible_in_question: raw_values must appear in question_text")

    pairs = givens.get("value_frequency_pairs") or []
    if pairs and op == "compute_arithmetic_mean_from_frequency_table":
        if not any(str(int(v)) in question for v, _ in pairs[:3]):
            errors.append("givens_visible_in_question: frequency table must appear in question_text")

    weights = givens.get("weights") or []
    if weights and op == "compute_weighted_mean":
        if not any(str(int(v)) in question for v, _ in weights[:2]):
            errors.append("givens_visible_in_question: weights must appear in question_text")

    derivation = meta.get("derivation") or []
    if not derivation:
        errors.append("derivation_consistency: metadata.derivation required")

    rounding = givens.get("rounding_policy") or payload.get("rounding_policy") or ac.get("rounding_policy")
    if ac.get("equivalence_type") == "decimal_tolerance" and not rounding:
        errors.append("rounding_policy_consistency: tolerance contract requires rounding_policy")

    if answer_shape in {"multi_blank", "table_fill", "multi_part"}:
        parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
        field_specs = givens.get("field_specs") if isinstance(givens.get("field_specs"), list) else []
        expected_count = len(field_specs) or int((payload.get("ui_contract") or {}).get("blank_count") or 0)
        if expected_count and len(parts) != expected_count:
            errors.append("field_count_consistency: parts count mismatch")
        keys = [str(part.get("field_key") or part.get("key") or "") for part in parts]
        if keys and len(set(keys)) != len(keys):
            errors.append("field_id_uniqueness: duplicate field keys")

    if isinstance(resolution, dict):
        for key in ("fixed_domain_key", "selected_operation", "required_capabilities", "matched_capabilities"):
            if resolution.get(key) in (None, "", []):
                errors.append(f"domain_evidence_complete: missing {key}")

    try:
        if op == "compute_arithmetic_mean_from_raw_values" and raw_values:
            expected = arithmetic_mean_from_raw([float(v) for v in raw_values])
            if abs(float(facts.get("mean", expected)) - expected) > 1e-6:
                errors.append("mean_consistency: mean mismatch")
        elif op == "compute_arithmetic_mean_from_frequency_table" and pairs:
            norm = [(float(v), int(f)) for v, f in pairs]
            expected = arithmetic_mean_from_frequency(norm)
            if abs(float(facts.get("mean", expected)) - expected) > 1e-6:
                errors.append("mean_consistency: frequency mean mismatch")
        elif op == "compute_weighted_mean" and weights:
            norm = [(float(v), float(w)) for v, w in weights]
            expected = weighted_mean_from_pairs(norm)
            if abs(float(facts.get("mean", expected)) - expected) > 1e-6:
                errors.append("weighted_mean_consistency: weighted mean mismatch")
        elif op == "compute_median_from_raw_values" and raw_values:
            expected = median_from_values([float(v) for v in raw_values])
            if abs(float(facts.get("median", expected)) - expected) > 1e-6:
                errors.append("median_consistency: median mismatch")
        elif op in {"compute_mode_from_raw_values", "compute_mode_from_frequency_table"}:
            values = [float(v) for v in raw_values] if raw_values else []
            if not values and pairs:
                expanded: list[float] = []
                for v, f in pairs:
                    expanded.extend([float(v)] * int(f))
                values = expanded
            if values:
                expected = mode_from_values(values)
                if list(facts.get("modes") or []) != expected:
                    errors.append("mode_consistency: mode mismatch")
                if not expected and str(payload.get("answer") or "") != NO_MODE_SENTINEL:
                    errors.append("mode_consistency: no-mode must use canonical sentinel")
                if len(expected) > 1 and checker_key not in {
                    "unordered_set_checker",
                    "solution_set_checker",
                    "set_checker",
                }:
                    errors.append("answer_shape_consistency: multi-mode requires unordered set checker")
        elif op == "compute_range" and raw_values:
            expected = range_from_values([float(v) for v in raw_values])
            if abs(float(facts.get("range", expected)) - expected) > 1e-6:
                errors.append("range_consistency: range mismatch")
        elif op == "compute_population_variance" and raw_values:
            vals = [float(v) for v in raw_values]
            expected = population_variance(vals)
            if abs(float(facts.get("variance", expected)) - expected) > 1e-6:
                errors.append("variance_consistency: variance mismatch")
        elif op == "compute_population_standard_deviation" and raw_values:
            vals = [float(v) for v in raw_values]
            var = population_variance(vals)
            std = population_standard_deviation(vals)
            if abs(float(facts.get("variance", var)) - var) > 1e-6:
                errors.append("variance_consistency: variance mismatch in stddev payload")
            if abs(float(facts.get("standard_deviation", std)) - std) > 1e-6:
                errors.append("standard_deviation_consistency: stddev mismatch")
            if abs(std - math.sqrt(var)) > 1e-6:
                errors.append("standard_deviation_consistency: sqrt(variance) mismatch")
        elif op == "compute_sample_variance" and raw_values:
            vals = [float(v) for v in raw_values]
            expected = sample_variance(vals)
            if abs(float(facts.get("sample_variance", expected)) - expected) > 1e-6:
                errors.append("sample_variance_consistency: sample variance mismatch")
        elif op == "compute_sample_standard_deviation" and raw_values:
            vals = [float(v) for v in raw_values]
            var = sample_variance(vals)
            std = sample_standard_deviation(vals)
            if abs(float(facts.get("sample_variance", var)) - var) > 1e-6:
                errors.append("sample_variance_consistency: sample variance mismatch in stddev payload")
            if abs(float(facts.get("sample_standard_deviation", std)) - std) > 1e-6:
                errors.append("sample_standard_deviation_consistency: sample stddev mismatch")
            if abs(std - math.sqrt(var)) > 1e-6:
                errors.append("sample_standard_deviation_consistency: sqrt(sample_variance) mismatch")
        elif op in {"compute_quartiles_and_iqr", "compare_dispersion"}:
            datasets = givens.get("datasets") or facts.get("group_summaries") or []
            if isinstance(datasets, list) and datasets:
                for item in datasets:
                    values = [float(v) for v in (item.get("raw_values") or [])]
                    if not values:
                        continue
                    summary = range_and_iqr_summary(values)
                    if abs(float(item.get("range", summary["range"])) - float(summary["range"])) > 1e-6:
                        errors.append("range_consistency: grouped range mismatch")
                    if abs(float(item.get("iqr", summary["iqr"])) - float(summary["iqr"])) > 1e-6:
                        errors.append("iqr_consistency: grouped iqr mismatch")
    except Exception as exc:
        errors.append(f"descriptive_statistics_validation_error:{exc}")

    return errors
