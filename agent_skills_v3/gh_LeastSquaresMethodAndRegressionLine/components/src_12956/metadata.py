from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12956"
SKILL_ID: Final[str] = "gh_LeastSquaresMethodAndRegressionLine"
SOURCE_REF: Final[str] = "src_12956"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12956
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "true_false_bivariate"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "true_false_bivariate"

TARGET_TASK: Final[str] = "true_false_bivariate"
TEMPLATE_SLOT: Final[str] = "true_false_bivariate"
PROBLEM_TYPE_ID: Final[str] = "true_false_bivariate"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.bivariate_statistics.bivariate_statistics_domain.build_bivariate_statistics_matrix",
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
