from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_DistanceBetweenTwoPointsInPlane'
GENERATOR_KEYS = ['vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:draft_v1', 'vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set', 'generator_readiness': 'runtime_ready', 'answer_type': 'solution_set', 'template_slot': 'two_point_distance_solution_set', 'base_problem_type_id': 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2', 'target_task': 'solve_unknown_coordinate_from_two_point_distance', 'presentation_mode': 'short_answer', 'answer_shape': 'unordered_set'}, {'problem_type_id': 'short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'generator_readiness': 'runtime_ready', 'answer_type': 'text_short', 'template_slot': 'two_point_distance_compute', 'base_problem_type_id': 'short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2', 'target_task': 'compute_distance_between_two_points', 'presentation_mode': 'short_answer', 'answer_shape': 'text_short'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
