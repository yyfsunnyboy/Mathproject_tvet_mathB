from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4655"
SKILL_ID: Final[str] = "vh_數學B1_FactorTheorem"
SOURCE_REF: Final[str] = "src_4655"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4655
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "factor_theorem_root_factor"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "factor_theorem_root_factor"

TARGET_TASK: Final[str] = "factor_theorem_root_factor"
TEMPLATE_SLOT: Final[str] = "factor_theorem_root_factor"
PROBLEM_TYPE_ID: Final[str] = "factor_theorem_root_factor"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.polynomial_domain.build_polynomial_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice",
    "answer_type": "single_choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "verified"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
