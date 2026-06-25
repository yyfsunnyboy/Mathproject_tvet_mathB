from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3886"
SKILL_ID: Final[str] = "vh_數學B4_StatisticalChartReading"
SOURCE_REF: Final[str] = "src_3886"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3886
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "compare_category_values"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "compare_category_values"

TARGET_TASK: Final[str] = "compare_category_values"
TEMPLATE_SLOT: Final[str] = "compare_category_values"
PROBLEM_TYPE_ID: Final[str] = "compare_category_values"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "integer"
ANSWER_TYPE: Final[str] = "integer"
LEGACY_ANSWER_TYPE: Final[str] = "integer"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.table_chart_domain.build_statistical_chart_reading_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "integer",
    "answer_type": "integer",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
