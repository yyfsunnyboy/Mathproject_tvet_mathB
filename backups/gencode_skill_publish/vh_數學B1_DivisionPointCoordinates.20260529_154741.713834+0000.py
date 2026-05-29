from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_DivisionPointCoordinates'
GENERATOR_KEYS = ['vh_數學B1_DivisionPointCoordinates:ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi_2:draft_v1', 'vh_數學B1_DivisionPointCoordinates:ordered_pair_compute_centroid_coordinates_short_answer_two_coordinate_points_sec_2:draft_v1', 'vh_數學B1_DivisionPointCoordinates:single_choice_compute_internal_division_point_coordinates_two_coordinate_points__2:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi_2', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'coordinate_pair_equivalence', 'generator_readiness': 'runtime_ready'}, {'problem_type_id': 'ordered_pair_compute_centroid_coordinates_short_answer_two_coordinate_points_sec_2', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'coordinate_pair_equivalence', 'generator_readiness': 'runtime_ready'}, {'problem_type_id': 'single_choice_compute_internal_division_point_coordinates_two_coordinate_points__2', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'generator_readiness': 'runtime_ready'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
