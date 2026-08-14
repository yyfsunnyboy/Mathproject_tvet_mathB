from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_4530"
SKILL_ID: Final[str] = "vh_數學B1_PropertiesOfParallelLines"
SOURCE_REF: Final[str] = "src_4530"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4530
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "parallel_segments_parameter"
ANSWER_SCHEMA_KEY: Final[str] = "parameter_scalar"
LINE_TYPE: Final[str] = "parallel_segments_parameter"

TARGET_TASK: Final[str] = "parallel_segments_parameter"
TEMPLATE_SLOT: Final[str] = "parallel_segments_parameter"
PROBLEM_TYPE_ID: Final[str] = "parallel_segments_parameter"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = "short_answer"
ANSWER_VALUE_TYPE: Final[str] = "integer"
ANSWER_TYPE: Final[str] = "integer"
LEGACY_ANSWER_TYPE: Final[str] = "integer"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "integer_checker",
    "equivalence_type": "numeric_exact",
    "response_mode": "short_answer",
    "interaction_type": "short_answer",
    "answer_value_type": "integer",
    "answer_type": "integer",
    "module": "core.checkers.structured_text_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    
)
TAXONOMY_PATH: Final[str] = "algebra"
