from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3822"
SKILL_ID: Final[str] = "vh_數學B4_FrequencyDistributionTableConstruction"
SOURCE_REF: Final[str] = "src_3822"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3822
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "frequency_table_construction_review"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "frequency_table_construction_review"

TARGET_TASK: Final[str] = "frequency_table_construction_review"
TEMPLATE_SLOT: Final[str] = "frequency_table_construction_review"
PROBLEM_TYPE_ID: Final[str] = "frequency_table_construction_review"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.frequency_distribution_domain.build_frequency_distribution_table_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "expression",
    "answer_type": "expression",
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
