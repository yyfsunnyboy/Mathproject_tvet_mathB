from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4500"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "src_4500"
SOURCE_KIND: Final[str] = "test"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4500
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 30
DIFFICULTY_LEVEL: Final[str] = "hard"
DOMAIN_OPERATION: Final[str] = "graph_based_linear_model_equation"
ANSWER_SCHEMA_KEY: Final[str] = "choice_label"
LINE_TYPE: Final[str] = "graph_based_linear_model_equation"

TARGET_TASK: Final[str] = "graph_based_linear_model_equation"
TEMPLATE_SLOT: Final[str] = "graph_based_linear_model_equation"
PROBLEM_TYPE_ID: Final[str] = "graph_based_linear_model_equation"
PRESENTATION_MODE: Final[str] = "graph_single_choice"
RESPONSE_MODE: Final[str] = "graph_single_choice"
INTERACTION_TYPE: Final[str] = "graph_single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "graph_single_choice",
    "interaction_type": "graph_single_choice",
    "answer_value_type": "choice",
    "answer_type": "single_choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
