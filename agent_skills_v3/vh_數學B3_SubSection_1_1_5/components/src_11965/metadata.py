from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_11965"
SKILL_ID: Final[str] = 'vh_數學B3_SubSection_1_1_5'
SOURCE_REF: Final[str] = "src_11965"
SOURCE_KIND: Final[str] = 'test'
TEXTBOOK_EXAMPLE_ID: Final[int] = 11965
IS_REQUIRED_CORE: Final[bool] = True

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = 'arithmetic_series_sum_given'
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = 'arithmetic_series_sum_given'

TARGET_TASK: Final[str] = 'arithmetic_series_sum_given'
TEMPLATE_SLOT: Final[str] = 'arithmetic_series_sum_given'
PROBLEM_TYPE_ID: Final[str] = 'arithmetic_series_sum_given'
PRESENTATION_MODE: Final[str] = 'short_answer'
RESPONSE_MODE: Final[str] = 'short_answer'
INTERACTION_TYPE: Final[str] = 'short_answer'
ANSWER_VALUE_TYPE: Final[str] = 'expression'
ANSWER_TYPE: Final[str] = 'expression'
LEGACY_ANSWER_TYPE: Final[str] = 'expression'

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.sequence_series_domain.build_sequence_series_matrix",
)
