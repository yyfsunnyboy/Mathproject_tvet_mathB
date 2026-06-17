from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PointSlopeForm'
GENERATOR_KEYS = ['src_4540', 'src_4541', 'src_4542', 'src_4543', 'src_4546', 'src_4549', 'src_4550', 'src_4551', 'src_4552', 'src_4556', 'src_4557', 'src_4560', 'src_4561', 'src_4606']
GENERATOR_SPECS = [{'textbook_example_id': 4540, 'component_id': 'src_4540', 'generator_key': 'src_4540', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4540', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4540, 'source_order': 4540, 'sampling_weight': 10.0}, {'textbook_example_id': 4541, 'component_id': 'src_4541', 'generator_key': 'src_4541', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4541', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4541, 'source_order': 4541, 'sampling_weight': 10.0}, {'textbook_example_id': 4542, 'component_id': 'src_4542', 'generator_key': 'src_4542', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4542', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4542, 'source_order': 4542, 'sampling_weight': 10.0}, {'textbook_example_id': 4543, 'component_id': 'src_4543', 'generator_key': 'src_4543', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4543', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4543, 'source_order': 4543, 'sampling_weight': 10.0}, {'textbook_example_id': 4546, 'component_id': 'src_4546', 'generator_key': 'src_4546', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4546', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4546, 'source_order': 4546, 'sampling_weight': 10.0}, {'textbook_example_id': 4549, 'component_id': 'src_4549', 'generator_key': 'src_4549', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4549', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4549, 'source_order': 4549, 'sampling_weight': 10.0}, {'textbook_example_id': 4550, 'component_id': 'src_4550', 'generator_key': 'src_4550', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4550', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4550, 'source_order': 4550, 'sampling_weight': 10.0}, {'textbook_example_id': 4551, 'component_id': 'src_4551', 'generator_key': 'src_4551', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4551', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4551, 'source_order': 4551, 'sampling_weight': 10.0}, {'textbook_example_id': 4552, 'component_id': 'src_4552', 'generator_key': 'src_4552', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4552', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4552, 'source_order': 4552, 'sampling_weight': 10.0}, {'textbook_example_id': 4556, 'component_id': 'src_4556', 'generator_key': 'src_4556', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4556', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4556, 'source_order': 4556, 'sampling_weight': 10.0}, {'textbook_example_id': 4557, 'component_id': 'src_4557', 'generator_key': 'src_4557', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4557', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4557, 'source_order': 4557, 'sampling_weight': 10.0}, {'textbook_example_id': 4560, 'component_id': 'src_4560', 'generator_key': 'src_4560', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4560', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4560, 'source_order': 4560, 'sampling_weight': 10.0}, {'textbook_example_id': 4561, 'component_id': 'src_4561', 'generator_key': 'src_4561', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4561', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4561, 'source_order': 4561, 'sampling_weight': 10.0}, {'textbook_example_id': 4606, 'component_id': 'src_4606', 'generator_key': 'src_4606', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4606', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4606, 'source_order': 4606, 'sampling_weight': 10.0}]


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
