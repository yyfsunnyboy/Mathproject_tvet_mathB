from __future__ import annotations

import importlib
from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer

SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
GENERATOR_KEYS = [
    "src_4420",
    "src_4421",
    "src_4423",
    "src_4427",
    "src_4438",
    "src_4512",
    "src_4513",
]
GENERATOR_SPECS = [
    {"component_id": "src_4420", "problem_type_id": "compute_internal_division_point_coordinates"},
    {"component_id": "src_4421", "problem_type_id": "compute_internal_division_point_coordinates"},
    {"component_id": "src_4423", "problem_type_id": "compute_centroid_coordinates"},
    {"component_id": "src_4427", "problem_type_id": "compute_internal_division_point_coordinates"},
    {"component_id": "src_4438", "problem_type_id": "compute_internal_division_point_coordinates"},
    {"component_id": "src_4512", "problem_type_id": "compute_internal_division_point_coordinates"},
    {"component_id": "src_4513", "problem_type_id": "compute_section_point_distance_from_origin"},
]
_cursor = 0


def _component_module(component_id: str, module_name: str):
    return importlib.import_module(
        f"agent_skills_v3.{SKILL_ID}.components.{component_id}.{module_name}"
    )


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    global _cursor
    component_id = str(kwargs.pop("component_id", "") or "")
    problem_type_id = str(kwargs.pop("problem_type_id", "") or "")
    if not component_id:
        candidates = [
            row["component_id"]
            for row in GENERATOR_SPECS
            if not problem_type_id or row["problem_type_id"] == problem_type_id
        ]
        if not candidates:
            raise KeyError(f"unknown_problem_type_id:{problem_type_id}")
        component_id = candidates[_cursor % len(candidates)]
        _cursor += 1
    if component_id not in GENERATOR_KEYS:
        raise KeyError(f"unknown_component_id:{component_id}")
    return _component_module(component_id, "generate").generate(
        level=level,
        seed=seed,
        component_id=component_id,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return check_answer(user_answer, correct_answer, payload=question_payload)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    component_id = str(payload.get("component_id") or "")
    if component_id not in GENERATOR_KEYS:
        return ""
    return _component_module(component_id, "get_hint").get_hint(step, payload)
