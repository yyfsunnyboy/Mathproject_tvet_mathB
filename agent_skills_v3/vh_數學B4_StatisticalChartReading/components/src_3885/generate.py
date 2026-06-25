from __future__ import annotations

from typing import Any

from core.domain.statistics.table_chart_domain import build_statistical_chart_reading_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "cumulative_above_interval_count"
TEXTBOOK_EXAMPLE_ID = 3885
DEFAULT_COMPONENT_ID = "src_3885"

# 原題 3885：接續 3884 同一折線圖，求 70～80 分人數
SOURCE_CONSTRAINTS: dict[str, Any] = {
    "chart_type": "cumulative_frequency_polygon_above",
    "cumulative_direction": "above",
    "story_context": "某班英文段考成績",
    "variable_unit": "分",
    "interval_low": 70,
    "interval_high": 80,
    "task_kind": "interval_count",
    "linked_source_example_id": 3884,
    "source_style_ref": "B4_Ch3_self_assessment_6_exam_interval",
    "class_marks": [40, 50, 60, 70, 80, 90, 100],
}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_statistical_chart_reading_matrix(
        seed=seed,
        domain_operation="cumulative_above_interval_count",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints=dict(SOURCE_CONSTRAINTS),
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        answer_schema_key="",
        domain_operation="cumulative_above_interval_count",
    )
    payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
