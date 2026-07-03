from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_MidpointCoordinates'
GENERATOR_KEYS = ['vh_數學B1_MidpointCoordinates:ordered_tuple_compute_midpoint_coordinates:draft_v1', 'vh_數學B1_MidpointCoordinates:ordered_tuple_compute_centroid_coordinates:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'ordered_tuple_compute_midpoint_coordinates', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'ordered_tuple_exact', 'generator_readiness': 'runtime_ready', 'answer_type': 'coordinate_pair', 'template_slot': 'division_point_coordinates', 'base_problem_type_id': 'ordered_tuple_compute_midpoint_coordinates', 'target_task': 'compute_midpoint_coordinates', 'presentation_mode': 'short_answer', 'answer_shape': 'coordinate_pair'}, {'problem_type_id': 'ordered_tuple_compute_centroid_coordinates', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'ordered_tuple_exact', 'generator_readiness': 'runtime_ready', 'answer_type': 'coordinate_pair', 'template_slot': 'division_point_coordinates', 'base_problem_type_id': 'ordered_tuple_compute_centroid_coordinates', 'target_task': 'compute_centroid_coordinates', 'presentation_mode': 'short_answer', 'answer_shape': 'coordinate_pair'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty, **kwargs)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
