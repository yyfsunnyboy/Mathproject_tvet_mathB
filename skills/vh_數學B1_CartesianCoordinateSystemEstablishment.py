from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
GENERATOR_KEYS = ["src_4417", "src_4435", "src_4509", "src_4510"]
GENERATOR_SPECS = [
    {
        "textbook_example_id": example_id,
        "component_id": component_id,
        "generator_key": component_id,
        "presentation_mode": "single_choice",
        "response_mode": "choice",
        "interaction_type": "choice",
        "source_kind": "example",
        "line_type": problem_type_id,
        "answer_type": "choice",
        "answer_value_type": "choice_label",
        "problem_type_id": problem_type_id,
        "display_order": example_id,
        "source_order": example_id,
        "sampling_weight": 10.0,
    }
    for example_id, component_id, problem_type_id in (
        (4417, "src_4417", "cartesian_coordinate_quadrant_symbol_reasoning"),
        (4435, "src_4435", "cartesian_coordinate_quadrant_symbol_reasoning"),
        (4509, "src_4509", "axis_distance_coordinate_point_numerical_choice"),
        (4510, "src_4510", "quadrant_statement_reasoning_choice"),
    )
]


def _resolve_v3_package_root() -> str:
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID,
        GENERATOR_KEYS,
        GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level,
        seed=seed,
        difficulty=difficulty,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return dispatch_check(
        user_answer,
        correct_answer,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )
