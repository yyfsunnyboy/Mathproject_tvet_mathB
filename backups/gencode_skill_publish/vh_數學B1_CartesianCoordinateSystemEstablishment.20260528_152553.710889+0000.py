"""Thin runtime wrapper — generation routed by ProblemTypeSpec, not skill-specific logic."""

from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"

GENERATOR_SPECS = [
    {"problem_type_id": "coordinate_quadrant_short_answer"},
    {"problem_type_id": "coordinate_quadrant_single_choice"},
    {"problem_type_id": "symbolic_expression_quadrant_short_answer"},
    {"problem_type_id": "symbolic_expression_quadrant_single_choice"},
    {"problem_type_id": "axis_distance_coordinate_single_choice"},
    {"problem_type_id": "symbolic_quadrant_statement_single_choice"},
]

GENERATOR_KEYS = [f"{SKILL_ID}:{s['problem_type_id']}:spec_v1" for s in GENERATOR_SPECS]


def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)


def check(user_answer: Any, correct_answer: Any):
    return check_answer(user_answer, correct_answer)
