from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12965"
SKILL_ID: Final[str] = "gh_LeastSquaresMethodAndRegressionLine"
SOURCE_REF: Final[str] = "src_12965"
SOURCE_KIND: Final[str] = "quiz"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12965
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 20
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "correlation_from_regression_point"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "correlation_from_regression_point"

TARGET_TASK: Final[str] = "correlation_from_regression_point"
TEMPLATE_SLOT: Final[str] = "correlation_from_regression_point"
PROBLEM_TYPE_ID: Final[str] = "correlation_from_regression_point"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "rational"
ANSWER_TYPE: Final[str] = "rational"
LEGACY_ANSWER_TYPE: Final[str] = "rational"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.bivariate_statistics.bivariate_statistics_domain.build_bivariate_statistics_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "rational_checker",
    "equivalence_type": "rational_equivalent",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "rational",
    "answer_type": "rational",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
