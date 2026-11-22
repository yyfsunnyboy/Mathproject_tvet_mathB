from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
GENERATOR_KEYS = ["src_4417", "src_4435", "src_4509", "src_4510"]
GENERATOR_SPECS = [
    {
        "textbook_example_id": 4417,
        "component_id": "src_4417",
        "generator_key": "src_4417",
        "presentation_mode": "single_choice",
        "response_mode": "choice",
        "interaction_type": "choice",
        "source_kind": "example",
        "line_type": "cartesian_coordinate_quadrant_symbol_reasoning",
        "answer_type": "choice",
        "answer_value_type": "choice_label",
        "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
        "display_order": 4417,
        "source_order": 4417,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 4435,
        "component_id": "src_4435",
        "generator_key": "src_4435",
        "presentation_mode": "single_choice",
        "response_mode": "choice",
        "interaction_type": "choice",
        "source_kind": "example",
        "line_type": "cartesian_coordinate_quadrant_symbol_reasoning",
        "answer_type": "choice",
        "answer_value_type": "choice_label",
        "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
        "display_order": 4435,
        "source_order": 4435,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 4509,
        "component_id": "src_4509",
        "generator_key": "src_4509",
        "presentation_mode": "single_choice",
        "response_mode": "choice",
        "interaction_type": "choice",
        "source_kind": "example",
        "line_type": "axis_distance_coordinate_point_numerical_choice",
        "answer_type": "choice",
        "answer_value_type": "choice_label",
        "problem_type_id": "axis_distance_coordinate_point_numerical_choice",
        "display_order": 4509,
        "source_order": 4509,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 4510,
        "component_id": "src_4510",
        "generator_key": "src_4510",
        "presentation_mode": "single_choice",
        "response_mode": "choice",
        "interaction_type": "choice",
        "source_kind": "example",
        "line_type": "quadrant_statement_reasoning_choice",
        "answer_type": "choice",
        "answer_value_type": "choice_label",
        "problem_type_id": "quadrant_statement_reasoning_choice",
        "display_order": 4510,
        "source_order": 4510,
        "sampling_weight": 10.0,
    },
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
