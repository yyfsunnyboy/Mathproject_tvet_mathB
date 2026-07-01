from __future__ import annotations
from typing import Any
from core.domain.coordinate_geometry.distance_between_two_points_domain import build_distance_between_two_points_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "text_short"
PROBLEM_TYPE_ID = "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2"
TEXTBOOK_EXAMPLE_ID = 4436
DEFAULT_COMPONENT_ID = "src_4436"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_distance_between_two_points_matrix(
        seed=seed,
        line_type="compute_distance_between_two_points",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="distance_scalar",
        domain_operation="compute_distance_between_two_points",
        seed=seed,
    )
    payload["problem_type_id"] = PROBLEM_TYPE_ID
    payload["skill_id"] = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
    payload["subskill_id"] = PROBLEM_TYPE_ID
    payload["answer_type"] = ANSWER_TYPE
    payload["checker_type"] = "text_short_checker"
    payload["question"] = payload["question_text"]
    payload["correct_answer"] = payload["answer"]
    payload["solution_steps"] = [str(step) for step in matrix.get("explanation_steps", [])]
    payload["explanation"] = "\n".join(payload["solution_steps"])
    payload.setdefault("metadata", {})["parameter_signature"] = f"{PROBLEM_TYPE_ID}:seed={seed}"
    return payload


def check(given: Any, expected: Any) -> dict[str, bool]:
    return {"correct": True}
