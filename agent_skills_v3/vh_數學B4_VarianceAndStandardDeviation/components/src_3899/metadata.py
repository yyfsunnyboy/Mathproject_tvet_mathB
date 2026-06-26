from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3899"
SKILL_ID: Final[str] = "vh_數學B4_VarianceAndStandardDeviation"
SOURCE_REF: Final[str] = "src_3899"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3899
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "compute_population_standard_deviation"
ANSWER_SCHEMA_KEY: Final[str] = "numeric_scalar"
LINE_TYPE: Final[str] = "compute_population_standard_deviation"

TARGET_TASK: Final[str] = "compute_population_standard_deviation"
TEMPLATE_SLOT: Final[str] = "compute_population_standard_deviation"
PROBLEM_TYPE_ID: Final[str] = "compute_population_standard_deviation"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.descriptive_statistics_domain.build_descriptive_statistics_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
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
