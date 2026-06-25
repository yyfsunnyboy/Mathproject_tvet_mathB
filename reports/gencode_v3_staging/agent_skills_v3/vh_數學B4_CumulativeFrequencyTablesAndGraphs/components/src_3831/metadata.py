from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3831"
SKILL_ID: Final[str] = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
SOURCE_REF: Final[str] = "src_3831"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3831
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "cumulative_frequency_table_construction"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "cumulative_frequency_table_construction"

TARGET_TASK: Final[str] = "cumulative_frequency_table_construction"
TEMPLATE_SLOT: Final[str] = "cumulative_frequency_table_construction"
PROBLEM_TYPE_ID: Final[str] = "cumulative_frequency_table_construction"
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
