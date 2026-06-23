from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_DistanceBetweenTwoParallelLines'
GENERATOR_KEYS = ['src_4570', 'src_4571', 'src_4577', 'src_4578', 'src_4579', 'src_4580', 'src_4583', 'src_4584', 'src_4588', 'src_4589', 'src_4608']
GENERATOR_SPECS = [{'textbook_example_id': 4570, 'component_id': 'src_4570', 'generator_key': 'src_4570', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_between_parallel_lines', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_between_parallel_lines', 'display_order': 4570, 'source_order': 4570, 'sampling_weight': 1.0}, {'textbook_example_id': 4571, 'component_id': 'src_4571', 'generator_key': 'src_4571', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_parameter_from_parallel_distance', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_parameter_from_parallel_distance', 'display_order': 4571, 'source_order': 4571, 'sampling_weight': 1.0}, {'textbook_example_id': 4577, 'component_id': 'src_4577', 'generator_key': 'src_4577', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_between_parallel_lines', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_between_parallel_lines', 'display_order': 4577, 'source_order': 4577, 'sampling_weight': 1.0}, {'textbook_example_id': 4578, 'component_id': 'src_4578', 'generator_key': 'src_4578', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'distance_between_parallel_lines', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_between_parallel_lines', 'display_order': 4578, 'source_order': 4578, 'sampling_weight': 1.0}, {'textbook_example_id': 4579, 'component_id': 'src_4579', 'generator_key': 'src_4579', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_parameter_from_parallel_distance', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_parameter_from_parallel_distance', 'display_order': 4579, 'source_order': 4579, 'sampling_weight': 1.0}, {'textbook_example_id': 4580, 'component_id': 'src_4580', 'generator_key': 'src_4580', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'solve_parameter_from_parallel_distance', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_parameter_from_parallel_distance', 'display_order': 4580, 'source_order': 4580, 'sampling_weight': 1.0}, {'textbook_example_id': 4583, 'component_id': 'src_4583', 'generator_key': 'src_4583', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'example', 'line_type': 'area_using_parallel_distance', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'area_using_parallel_distance', 'display_order': 4583, 'source_order': 4583, 'sampling_weight': 1.0}, {'textbook_example_id': 4584, 'component_id': 'src_4584', 'generator_key': 'src_4584', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'parallel_lines_distance_single_choice', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'parallel_lines_distance_single_choice', 'display_order': 4584, 'source_order': 4584, 'sampling_weight': 1.0}, {'textbook_example_id': 4588, 'component_id': 'src_4588', 'generator_key': 'src_4588', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'distance_between_parallel_lines', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_between_parallel_lines', 'display_order': 4588, 'source_order': 4588, 'sampling_weight': 1.0}, {'textbook_example_id': 4589, 'component_id': 'src_4589', 'generator_key': 'src_4589', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'quiz', 'line_type': 'solve_parameter_from_parallel_distance', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_parameter_from_parallel_distance', 'display_order': 4589, 'source_order': 4589, 'sampling_weight': 1.0}, {'textbook_example_id': 4608, 'component_id': 'src_4608', 'generator_key': 'src_4608', 'presentation_mode': 'short_answer', 'response_mode': 'expression', 'interaction_type': 'expression', 'source_kind': 'test', 'line_type': 'distance_between_parallel_lines', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distance_between_parallel_lines', 'display_order': 4608, 'source_order': 4608, 'sampling_weight': 1.0}]
for _spec in GENERATOR_SPECS:
    if _spec.get("problem_type_id") in {
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "area_using_parallel_distance",
    }:
        _spec["answer_type"] = "numeric_or_radical"
        _spec["answer_value_type"] = "numeric_or_radical"


def _resolve_v3_package_root() -> str:
    """Resolve V3 house root from this facade location: skills/ -> <root>/agent_skills_v3."""
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
