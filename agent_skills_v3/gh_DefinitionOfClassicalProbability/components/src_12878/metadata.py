from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12878"
SKILL_ID: Final[str] = "gh_DefinitionOfClassicalProbability"
SOURCE_REF: Final[str] = "src_12878"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12878
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "urn_draw_probability"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "urn_draw_probability"

TARGET_TASK: Final[str] = "urn_draw_probability"
TEMPLATE_SLOT: Final[str] = "urn_draw_probability"
PROBLEM_TYPE_ID: Final[str] = "urn_draw_probability"
PRESENTATION_MODE: Final[str] = "multiple_inputs"
RESPONSE_MODE: Final[str] = "multiple_inputs"
INTERACTION_TYPE: Final[str] = "multiple_inputs"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.classical_probability.classical_probability_domain.build_classical_probability_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "multi_part_answer_checker",
    "equivalence_type": "multi_part_answer",
    "response_mode": "multiple_inputs",
    "interaction_type": "multiple_inputs",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.multi_part_answer_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
