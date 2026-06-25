from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3834"
SKILL_ID: Final[str] = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
SOURCE_REF: Final[str] = "src_3834"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3834
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "class_frequency_from_cumulative_difference"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "class_frequency_from_cumulative_difference"

TARGET_TASK: Final[str] = "class_frequency_from_cumulative_difference"
TEMPLATE_SLOT: Final[str] = "class_frequency_from_cumulative_difference"
PROBLEM_TYPE_ID: Final[str] = "class_frequency_from_cumulative_difference"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "integer"
ANSWER_TYPE: Final[str] = "integer"
LEGACY_ANSWER_TYPE: Final[str] = "integer"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.frequency_distribution_domain.build_frequency_distribution_table_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "integer",
    "answer_type": "integer",
    "module": "core.checkers.linear_equation_equivalent_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
