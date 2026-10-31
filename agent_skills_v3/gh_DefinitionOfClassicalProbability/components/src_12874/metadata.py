from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12874"
SKILL_ID: Final[str] = "gh_DefinitionOfClassicalProbability"
SOURCE_REF: Final[str] = "src_12874"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12874
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "classical_claim"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "classical_claim"

TARGET_TASK: Final[str] = "classical_claim"
TEMPLATE_SLOT: Final[str] = "classical_claim"
PROBLEM_TYPE_ID: Final[str] = "classical_claim"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "choice_label"
LEGACY_ANSWER_TYPE: Final[str] = "choice_label"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.classical_probability.classical_probability_domain.build_classical_probability_matrix",
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
