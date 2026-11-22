# -*- coding: utf-8 -*-
"""Textbook src_4550: equal-distance locus = perpendicular bisector application."""
from __future__ import annotations

from typing import Any

from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = "vh_數學B1_PointSlopeForm"
PROBLEM_TYPE_ID = "write_perpendicular_bisector_from_two_points"
TEXTBOOK_EXAMPLE_ID = 4550
DEFAULT_COMPONENT_ID = "src_4550"
PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "equation"

_BASE_SPEC: dict[str, Any] = {
    "problem_type_id": PROBLEM_TYPE_ID,
    "target_task": "write_perpendicular_bisector_from_two_points",
    "template_slot": "perpendicular_bisector_from_two_points",
    "task_family": "line_equation_family",
    "presentation_mode": PRESENTATION_MODE,
    "presentation_variant": "perpendicular_bisector_equal_distance",
    "answer_contract": {
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "answer_shape": "linear_equation",
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "equivalence_type": "linear_equation_equivalent",
        "answer_equivalence": "linear_equation_equivalent",
    },
}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    _ = level
    payload = generate_from_problem_type_spec(SKILL_ID, dict(_BASE_SPEC), seed=seed)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["seed"] = seed
    payload.setdefault("problem_type_id", PROBLEM_TYPE_ID)
    payload.setdefault("presentation_mode", PRESENTATION_MODE)
    payload.setdefault("answer_type", ANSWER_TYPE)
    payload.setdefault("line_type", "perpendicular_bisector")
    return payload
