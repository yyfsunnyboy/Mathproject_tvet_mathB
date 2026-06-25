"""Validate generated payloads preserve source-example structure."""

from __future__ import annotations

import re
from typing import Any

GENERATION_NOT_SOURCE_ISOMORPHIC = "GENERATION_NOT_SOURCE_ISOMORPHIC"

def _build_generic_table_chart_ops() -> frozenset:
    """Generic (non-cumulative) table chart operations derived from the registry.

    These are the operations that do NOT require a cumulative-frequency-polygon
    source.  When a generated payload uses one of these ops for a source that
    expected a cumulative operation, it is flagged as a degradation.
    """
    from core.registry.domain_operation_registry import get_domain_spec
    spec = get_domain_spec("statistics.table_chart")
    if spec is None:
        return frozenset({
            "read_category_value",
            "compare_category_values",
            "calculate_total_ratio_percent",
            "validate_chart_statement",
        })
    return frozenset(
        op_key
        for op_key, op_spec in spec.operations.items()
        if not op_spec.required_source_features
    )


_GENERIC_TABLE_CHART_OPS: frozenset = _build_generic_table_chart_ops()

_GENERIC_CATEGORY_MARKERS = frozenset({"A", "B", "C", "D"})


def _is_cumulative_source_text(text: str) -> bool:
    return any(token in text for token in ("累積", "累積次數", "cumulative"))



def validate_source_isomorphism(
    payload: dict[str, Any],
    *,
    induced_spec: dict[str, Any] | None = None,
    source_topology: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return {passed, blockers, error_code}."""
    spec = induced_spec or {}
    topology = source_topology or spec.get("source_topology") or {}
    if not topology:
        return {"passed": True, "blockers": [], "error_code": None}

    blockers: list[str] = []
    example_id = int(topology.get("source_example_id") or spec.get("textbook_example_id") or 0)
    expected_op = str(topology.get("exact_task_operation") or spec.get("domain_operation") or "").strip()
    actual_op = str(
        payload.get("domain_operation")
        or payload.get("problem_type_id")
        or (payload.get("metadata") or {}).get("domain_operation")
        or ""
    ).strip()

    if expected_op and actual_op and expected_op != actual_op:
        blockers.append(f"operation_mismatch:expected={expected_op},actual={actual_op}")

    source_question_text = str(topology.get("source_question_text") or "")
    if _is_cumulative_source_text(source_question_text) and actual_op == "frequency_polygon_reading":
        blockers.append("cumulative_stem_matched_frequency_polygon_reading")

    if actual_op in _GENERIC_TABLE_CHART_OPS and expected_op not in _GENERIC_TABLE_CHART_OPS:
        blockers.append(f"degraded_to_generic_operation:{actual_op}")

    question_text = str(payload.get("question_text") or "")
    if "閱讀下列統計表" in question_text and "累積次數" in str(topology.get("source_question_text") or ""):
        blockers.append("degraded_to_generic_table_stem")

    story = str(topology.get("story_context") or "")
    if story:
        story_tokens = [tok for tok in ("公司", "員工", "年齡", "成績", "段考", "英文") if tok in story]
        if story_tokens:
            if not all(tok in question_text for tok in story_tokens):
                blockers.append(f"missing_story_context:{story}")
        elif story not in question_text:
            blockers.append(f"missing_story_context:{story}")

    invariants = topology.get("invariants") or []
    chart_type = str(topology.get("chart_type") or "")
    if chart_type.startswith("cumulative_frequency_polygon"):
        if "累積" not in question_text and "折線圖" not in question_text:
            blockers.append("missing_cumulative_polygon_wording_in_stem")

    givens = (payload.get("metadata") or {}).get("givens") or {}
    categories = list(givens.get("categories") or [])
    if categories and set(str(c) for c in categories) == _GENERIC_CATEGORY_MARKERS:
        if chart_type.startswith("cumulative_frequency_polygon"):
            blockers.append("generic_abcd_category_placeholder")

    visual_spec = payload.get("visual_spec") or {}
    visual_type = str(visual_spec.get("type") or "")
    has_chart = bool(
        visual_type.startswith("cumulative_frequency")
        or payload.get("image_base64")
        or payload.get("visual_aids")
        or (visual_spec.get("rows") and visual_type in {"table", "table_chart", "cumulative_frequency_table"})
    )
    deps = topology.get("displayed_data_dependencies") or []
    if deps and not has_chart:
        blockers.append("answer_dependencies_not_displayed")

    if topology.get("total_population") and example_id == 3886:
        total = str(topology.get("total_population"))
        if total not in question_text:
            blockers.append("missing_total_population_in_stem")

    if topology.get("interval_low") is not None and topology.get("interval_high") is not None:
        low = int(topology["interval_low"])
        high = int(topology["interval_high"])
        interval_pattern = rf"{low}\s*[～~\-]\s*{high}"
        if not re.search(interval_pattern, question_text):
            blockers.append(f"missing_interval_wording:{low}~{high}")

    source_choices = topology.get("source_choices") or []
    payload_choices = payload.get("choices") or []
    if source_choices and payload_choices:
        if len(source_choices) != len(payload_choices):
            blockers.append("choice_topology_count_mismatch")

    for inv in invariants:
        inv_s = str(inv)
        if inv_s.startswith("linked_prior_example="):
            linked = inv_s.split("=", 1)[1]
            if example_id == 3885 and linked not in question_text and "接續" not in question_text:
                blockers.append("missing_linked_prior_example_reference")

    passed = not blockers
    return {
        "passed": passed,
        "blockers": blockers,
        "error_code": None if passed else GENERATION_NOT_SOURCE_ISOMORPHIC,
    }
