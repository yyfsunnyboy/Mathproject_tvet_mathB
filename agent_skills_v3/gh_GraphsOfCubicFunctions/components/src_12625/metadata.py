from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_12625"
SKILL_ID: Final[str] = "gh_GraphsOfCubicFunctions"
SOURCE_REF: Final[str] = "src_12625"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 12625
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "cubic_center_form"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "cubic_center_form"

TARGET_TASK: Final[str] = "cubic_center_form"
TEMPLATE_SLOT: Final[str] = "cubic_center_form"
PROBLEM_TYPE_ID: Final[str] = "cubic_center_form"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "coordinate_pair"
ANSWER_TYPE: Final[str] = "coordinate_pair"
LEGACY_ANSWER_TYPE: Final[str] = "coordinate_pair"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.promoted.function_cubic.cubic_domain.build_cubic_graph_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "coordinate_pair_checker",
    "equivalence_type": "coordinate_pair_equivalence",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "coordinate_pair",
    "answer_type": "coordinate_pair",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
