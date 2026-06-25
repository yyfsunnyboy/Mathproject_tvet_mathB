"""Validation gates for cumulative-frequency generator payloads."""

from __future__ import annotations

import base64
import re
from typing import Any

from core.domain.statistics.cumulative_frequency import (
    validate_greater_than_sequence,
    validate_less_than_sequence,
)

_GRAPH_OPS = frozenset(
    {
        "cumulative_frequency_graph_reading",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
    }
)


def _requires_graph_image(payload: dict[str, Any], op: str) -> bool:
    vf = payload.get("validation_facts") if isinstance(payload.get("validation_facts"), dict) else {}
    topology = str(vf.get("task_topology") or "").strip()
    if topology in {"cumulative_table_blank_fill", "bidirectional_table"}:
        return False
    if op in _GRAPH_OPS:
        return True
    if op == "class_frequency_from_cumulative_difference" and topology == "interval_difference":
        return True
    return False

_STEM_GRAPH_MARKERS = ("如下圖", "下圖", "如右", "如右圖")
_STEM_TABLE_MARKERS = ("如下表", "下表", "完成下方")


def _decode_base64_png(payload: str) -> bool:
    raw = str(payload or "").strip()
    if not raw:
        return False
    if raw.startswith("data:image"):
        raw = raw.split(",", 1)[-1]
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception:
        return False
    return len(data) > 8 and data[:8].startswith(b"\x89PNG\r\n\x1a\n")


def _choice_values(choices: list[Any]) -> list[str]:
    values: list[str] = []
    for choice in choices:
        if isinstance(choice, dict):
            values.append(str(choice.get("text", choice.get("value", ""))))
        else:
            values.append(str(choice))
    return [v for v in values if v]


def validate_cumulative_frequency_payload(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for cumulative-frequency runtime payloads."""
    errors: list[str] = []
    op = str(payload.get("domain_operation") or payload.get("problem_type_id") or "").strip()
    question_text = str(payload.get("question_text") or "")
    image_base64 = str(payload.get("image_base64") or "")
    table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    subquestions = payload.get("subquestions") if isinstance(payload.get("subquestions"), list) else []
    answer_type = str(payload.get("answer_type") or "").strip()
    visual_spec = payload.get("visual_spec") if isinstance(payload.get("visual_spec"), dict) else {}

    if _requires_graph_image(payload, op):
        if not image_base64:
            errors.append("CUMULATIVE_GRAPH_MISSING_IMAGE: graph question requires image_base64")
        elif not _decode_base64_png(image_base64):
            errors.append("CUMULATIVE_IMAGE_BASE64_DECODE_FAIL: image_base64 is not valid PNG")

    if any(marker in question_text for marker in _STEM_GRAPH_MARKERS):
        if not image_base64 and _requires_graph_image(payload, op):
            errors.append("STEM_REFERENCES_GRAPH_BUT_MISSING: stem mentions graph but image_base64 is empty")

    if any(marker in question_text for marker in _STEM_TABLE_MARKERS):
        if not table_data and visual_spec.get("type") != "cumulative_frequency_table":
            errors.append("STEM_REFERENCES_TABLE_BUT_MISSING: stem mentions table but table_data is empty")

    direction = str(
        visual_spec.get("cumulative_direction")
        or payload.get("validation_facts", {}).get("cumulative_direction")
        or ""
    ).strip().lower()
    data_points = visual_spec.get("data_points") or visual_spec.get("graph_points") or []
    if data_points and direction in {"less_than", "below"}:
        ys = [int(p.get("y", p.get("cumulative_count", 0))) for p in data_points]
        total = int(payload.get("validation_facts", {}).get("total_students") or max(ys))
        ok, reason = validate_less_than_sequence(ys, total)
        if not ok:
            errors.append(f"CUMULATIVE_LESS_THAN_SEQUENCE_INVALID:{reason}")
    if data_points and direction in {"greater_than", "above"}:
        ys = [int(p.get("y", p.get("cumulative_count", 0))) for p in data_points]
        total = int(payload.get("validation_facts", {}).get("total_students") or max(ys))
        ok, reason = validate_greater_than_sequence(ys, total)
        if not ok:
            errors.append(f"CUMULATIVE_GREATER_THAN_SEQUENCE_INVALID:{reason}")

    if image_base64 and data_points:
        rendered_points = [
            (float(p.get("x")), int(p.get("y")))
            for p in data_points
            if p.get("x") is not None and p.get("y") is not None
        ]
        spec_points = visual_spec.get("data_points") or []
        if spec_points and len(rendered_points) != len(spec_points):
            errors.append("VISUAL_SPEC_IMAGE_DATA_MISMATCH: data point count differs from visual_spec")

    if answer_type == "multi_part":
        semantic = payload.get("semantic_answer") or payload.get("answer")
        if isinstance(semantic, list):
            if len(semantic) != len(subquestions):
                errors.append("MULTI_PART_ANSWER_INCOMPLETE: subquestion count mismatch")
        elif not subquestions:
            errors.append("MULTI_PART_SUBQUESTIONS_MISSING")

    if answer_type == "single_choice" or choices:
        values = _choice_values(choices)
        if len(values) != len(set(values)):
            errors.append("MCQ_DUPLICATE_CHOICES: choices must be unique")
        semantic = payload.get("validation_facts", {}).get("semantic_answer")
        if semantic is not None and str(semantic) not in values:
            errors.append("MCQ_MISSING_CORRECT_CHOICE: semantic answer not in choices")

    vf = payload.get("validation_facts") if isinstance(payload.get("validation_facts"), dict) else {}
    answer_value = vf.get("answer_value")
    if answer_value is None and op not in {"cumulative_frequency_table_construction"}:
        errors.append("ANSWER_NOT_DETERMINABLE: validation_facts missing answer_value")

    if op == "class_frequency_from_cumulative_difference":
        interval = vf.get("interval_low"), vf.get("interval_high")
        if interval[0] is not None and isinstance(answer_value, int) and answer_value < 0:
            errors.append("INTERVAL_FREQUENCY_NEGATIVE")

    blank_cells = table_data.get("blank_cells") if isinstance(table_data, dict) else []
    if blank_cells and isinstance(answer_value, dict):
        lt = answer_value.get("less_than_cumulative")
        gt = answer_value.get("greater_than_cumulative")
        if not lt or not gt:
            errors.append("TABLE_BLANK_CELLS_ANSWER_MISMATCH: expected cumulative columns in answer")

    if re.search(r"負\s*\d+", str(payload.get("explanation") or "")):
        errors.append("EXPLANATION_NEGATIVE_FREQUENCY")

    return sorted(set(errors))
