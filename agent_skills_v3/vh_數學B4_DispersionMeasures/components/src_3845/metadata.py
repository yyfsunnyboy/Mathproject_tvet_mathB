from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3845"
SKILL_ID: Final[str] = "vh_數學B4_DispersionMeasures"
SOURCE_REF: Final[str] = "src_3845"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3845
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "compute_quartiles_and_iqr"
ANSWER_SCHEMA_KEY: Final[str] = "numeric_scalar"
LINE_TYPE: Final[str] = "compute_quartiles_and_iqr"

TARGET_TASK: Final[str] = "compute_quartiles_and_iqr"
TEMPLATE_SLOT: Final[str] = "compute_quartiles_and_iqr"
PROBLEM_TYPE_ID: Final[str] = "compute_quartiles_and_iqr"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "expression"
INTERACTION_TYPE: Final[str] = "expression"
ANSWER_VALUE_TYPE: Final[str] = "expression"
ANSWER_TYPE: Final[str] = "expression"
LEGACY_ANSWER_TYPE: Final[str] = "expression"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.statistics.descriptive_statistics_domain.build_descriptive_statistics_matrix",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence_type": "linear_equation_equivalent",
    "response_mode": "expression",
    "interaction_type": "expression",
    "answer_value_type": "expression",
    "answer_type": "expression",
    "module": "core.checkers.linear_equation_equivalent_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率", "直線方程式",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point", "linear_equation",
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
