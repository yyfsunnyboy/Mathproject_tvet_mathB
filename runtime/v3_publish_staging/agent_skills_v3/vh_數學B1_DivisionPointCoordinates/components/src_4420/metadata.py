from typing import Final
COMPONENT_ID: Final[str] = "src_4420"
SKILL_ID: Final[str] = "vh_數學B1_DivisionPointCoordinates"
SOURCE_REF: Final[str] = "src_4420"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4420
PROBLEM_TYPE_ID: Final[str] = "compute_internal_division_point_coordinates"
TARGET_TASK: Final[str] = PROBLEM_TYPE_ID
DOMAIN_OPERATION: Final[str] = PROBLEM_TYPE_ID
TEMPLATE_SLOT: Final[str] = "division_point_coordinates"
PRESENTATION_MODE: Final[str] = "short_answer"
RESPONSE_MODE: Final[str] = "short_answer"
INTERACTION_TYPE: Final[str] = RESPONSE_MODE
ANSWER_VALUE_TYPE: Final[str] = "coordinate_pair"
ANSWER_TYPE: Final[str] = ANSWER_VALUE_TYPE
GENERATOR_KEY: Final[str] = f"{SKILL_ID}:{PROBLEM_TYPE_ID}:draft_v1"
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {"checker_key": "coordinate_pair_checker", "equivalence_type": "coordinate_pair_equivalence", "response_mode": RESPONSE_MODE, "interaction_type": INTERACTION_TYPE, "answer_value_type": ANSWER_VALUE_TYPE, "answer_type": ANSWER_TYPE}
GENERATOR_READINESS: Final[str] = "verified"
