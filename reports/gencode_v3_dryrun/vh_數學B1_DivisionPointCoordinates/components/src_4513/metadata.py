from typing import Final
COMPONENT_ID: Final[str] = "src_4513"
SKILL_ID: Final[str] = "vh_數學B1_DivisionPointCoordinates"
SOURCE_REF: Final[str] = "src_4513"
SOURCE_KIND: Final[str] = "example"
TEXTBOOK_EXAMPLE_ID: Final[int] = 4513
PROBLEM_TYPE_ID: Final[str] = "compute_section_point_distance_from_origin"
TARGET_TASK: Final[str] = PROBLEM_TYPE_ID
DOMAIN_OPERATION: Final[str] = PROBLEM_TYPE_ID
TEMPLATE_SLOT: Final[str] = "division_point_coordinates"
PRESENTATION_MODE: Final[str] = "single_choice"
RESPONSE_MODE: Final[str] = "single_choice"
INTERACTION_TYPE: Final[str] = RESPONSE_MODE
ANSWER_VALUE_TYPE: Final[str] = "single_choice"
ANSWER_TYPE: Final[str] = ANSWER_VALUE_TYPE
GENERATOR_KEY: Final[str] = f"{SKILL_ID}:{PROBLEM_TYPE_ID}:draft_v1"
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {"checker_key": "choice_label_checker", "equivalence_type": "choice_label", "response_mode": RESPONSE_MODE, "interaction_type": INTERACTION_TYPE, "answer_value_type": ANSWER_VALUE_TYPE, "answer_type": ANSWER_TYPE}
GENERATOR_READINESS: Final[str] = "verified"
