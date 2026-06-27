from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3829"
SKILL_ID: Final[str] = "vh_數學B4_HistogramsAndFrequencyPolygons"
SOURCE_REF: Final[str] = "src_3829"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3829
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "histogram_distribution_update"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "histogram_distribution_update"

TARGET_TASK: Final[str] = "histogram_distribution_update"
TEMPLATE_SLOT: Final[str] = "histogram_distribution_update"
PROBLEM_TYPE_ID: Final[str] = "histogram_distribution_update"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.frequency_distribution_domain.build_frequency_distribution_table_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "choice_label",
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
