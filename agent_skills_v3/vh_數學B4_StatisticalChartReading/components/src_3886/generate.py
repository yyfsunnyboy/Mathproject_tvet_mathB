from __future__ import annotations

from typing import Any

from core.domain.statistics.table_chart_domain import build_statistical_chart_reading_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "cumulative_below_interval_count"
TEXTBOOK_EXAMPLE_ID = 3886
DEFAULT_COMPONENT_ID = "src_3886"

# 原題 3886：40 名員工年齡「以下累積次數分配折線圖」，求 30～40 歲人數
SOURCE_CONSTRAINTS: dict[str, Any] = {
    "chart_type": "cumulative_frequency_polygon_below",
    "cumulative_direction": "below",
    "story_context": "某公司員工年齡",
    "variable_unit": "歲",
    "total_population": 40,
    "interval_low": 30,
    "interval_high": 40,
    "task_kind": "interval_count",
    "source_style_ref": "B4_Ch3_self_assessment_7_age_below_cumulative",
    "class_marks": [20, 30, 40, 50, 60],
}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_statistical_chart_reading_matrix(
        seed=seed,
        domain_operation="cumulative_below_interval_count",
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
        domain_operation="cumulative_below_interval_count",
    )
    payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
