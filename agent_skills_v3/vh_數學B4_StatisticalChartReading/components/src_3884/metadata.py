from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3884"
SKILL_ID: Final[str] = "vh_數學B4_StatisticalChartReading"
SOURCE_REF: Final[str] = "src_3884"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3884
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "cumulative_above_fail_count"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "cumulative_above_fail_count"

TARGET_TASK: Final[str] = "cumulative_above_fail_count"
TEMPLATE_SLOT: Final[str] = "cumulative_above_fail_count"
PROBLEM_TYPE_ID: Final[str] = "cumulative_above_fail_count"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "integer"
SEMANTIC_ANSWER_TYPE: Final[str] = "integer"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.table_chart_domain.build_statistical_chart_reading_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "single_choice",
    "semantic_answer_type": "integer",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "累積次數分配折線圖", "以上累積次數",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "cumulative_frequency_polygon", "statistical_chart",
)
TAXONOMY_PATH: Final[str] = "statistics:table_chart"
