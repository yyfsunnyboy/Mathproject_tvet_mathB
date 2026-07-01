from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4416"
SKILL_ID: Final[str] = "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
SOURCE_REF: Final[str] = "src_4416"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4416
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "absolute_value_inequality_interval_interpretation"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "absolute_value_inequality_interval_interpretation"

TARGET_TASK: Final[str] = "absolute_value_inequality_interval_interpretation"
TEMPLATE_SLOT: Final[str] = "absolute_value_inequality_interval_interpretation"
PROBLEM_TYPE_ID: Final[str] = "absolute_value_inequality_interval_interpretation"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice"
ANSWER_TYPE: Final[str] = "choice"
LEGACY_ANSWER_TYPE: Final[str] = "choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.absolute_value_domain.build_absolute_value_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice",
    "answer_type": "choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "絕對值", "絕對值方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "absolute_value", "equation",
)
TAXONOMY_PATH: Final[str] = "algebra:absolute_value"
