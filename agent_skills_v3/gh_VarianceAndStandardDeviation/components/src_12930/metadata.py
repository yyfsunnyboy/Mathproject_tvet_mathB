from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12930"
SKILL_ID: Final[str] = "gh_VarianceAndStandardDeviation"
SOURCE_REF: Final[str] = "src_12930"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12930
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "grade_distribution_read"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "grade_distribution_read"

TARGET_TASK: Final[str] = "grade_distribution_read"
TEMPLATE_SLOT: Final[str] = "grade_distribution_read"
PROBLEM_TYPE_ID: Final[str] = "grade_distribution_read"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.univariate_statistics.univariate_statistics_domain.build_univariate_statistics_matrix",
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
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
