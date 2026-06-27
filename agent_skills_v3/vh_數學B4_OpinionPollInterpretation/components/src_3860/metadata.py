from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_3860"
SKILL_ID: Final[str] = "vh_數學B4_OpinionPollInterpretation"
SOURCE_REF: Final[str] = "src_3860"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 3860
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
DOMAIN_OPERATION: Final[str] = "poll_interval_from_support_and_margin"
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = "poll_interval_from_support_and_margin"

TARGET_TASK: Final[str] = "poll_interval_from_support_and_margin"
TEMPLATE_SLOT: Final[str] = "poll_interval_from_support_and_margin"
PROBLEM_TYPE_ID: Final[str] = "poll_interval_from_support_and_margin"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = "single_choice"
ANSWER_VALUE_TYPE: Final[str] = "choice_label"
ANSWER_TYPE: Final[str] = "single_choice"
LEGACY_ANSWER_TYPE: Final[str] = "single_choice"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = ()

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",
    "equivalence_type": "choice_label",
    "response_mode": "single_choice",
    "interaction_type": "single_choice",
    "answer_value_type": "choice_label",
    "answer_type": "single_choice",
    "module": "core.checkers.choice_label_checker",
}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "民調支持度", "抽樣誤差", "信賴區間",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "poll_support", "margin_of_error", "confidence_interval",
)
TAXONOMY_PATH: Final[str] = "statistics:opinion_poll"
