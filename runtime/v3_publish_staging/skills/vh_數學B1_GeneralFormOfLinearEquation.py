from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_GeneralFormOfLinearEquation'
GENERATOR_KEYS = ['src_4565', 'src_4566', 'src_4567', 'src_4572', 'src_4573', 'src_4574', 'src_4581', 'src_4582', 'src_4585', 'src_4592', 'src_4593', 'src_4594', 'src_4595', 'src_4596', 'src_4597', 'src_4598', 'src_4599']
GENERATOR_SPECS = [{'textbook_example_id': 4565, 'component_id': 'src_4565', 'generator_key': 'src_4565', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4565', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4565, 'source_order': 4565, 'sampling_weight': 10.0}, {'textbook_example_id': 4566, 'component_id': 'src_4566', 'generator_key': 'src_4566', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4566', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4566, 'source_order': 4566, 'sampling_weight': 10.0}, {'textbook_example_id': 4567, 'component_id': 'src_4567', 'generator_key': 'src_4567', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4567', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4567, 'source_order': 4567, 'sampling_weight': 10.0}, {'textbook_example_id': 4572, 'component_id': 'src_4572', 'generator_key': 'src_4572', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4572', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4572, 'source_order': 4572, 'sampling_weight': 10.0}, {'textbook_example_id': 4573, 'component_id': 'src_4573', 'generator_key': 'src_4573', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4573', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4573, 'source_order': 4573, 'sampling_weight': 10.0}, {'textbook_example_id': 4574, 'component_id': 'src_4574', 'generator_key': 'src_4574', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4574', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4574, 'source_order': 4574, 'sampling_weight': 10.0}, {'textbook_example_id': 4581, 'component_id': 'src_4581', 'generator_key': 'src_4581', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4581', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4581, 'source_order': 4581, 'sampling_weight': 10.0}, {'textbook_example_id': 4582, 'component_id': 'src_4582', 'generator_key': 'src_4582', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4582', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4582, 'source_order': 4582, 'sampling_weight': 10.0}, {'textbook_example_id': 4585, 'component_id': 'src_4585', 'generator_key': 'src_4585', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4585', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4585, 'source_order': 4585, 'sampling_weight': 10.0}, {'textbook_example_id': 4592, 'component_id': 'src_4592', 'generator_key': 'src_4592', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4592', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4592, 'source_order': 4592, 'sampling_weight': 10.0}, {'textbook_example_id': 4593, 'component_id': 'src_4593', 'generator_key': 'src_4593', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4593', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4593, 'source_order': 4593, 'sampling_weight': 10.0}, {'textbook_example_id': 4594, 'component_id': 'src_4594', 'generator_key': 'src_4594', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4594', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4594, 'source_order': 4594, 'sampling_weight': 10.0}, {'textbook_example_id': 4595, 'component_id': 'src_4595', 'generator_key': 'src_4595', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4595', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4595, 'source_order': 4595, 'sampling_weight': 10.0}, {'textbook_example_id': 4596, 'component_id': 'src_4596', 'generator_key': 'src_4596', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4596', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4596, 'source_order': 4596, 'sampling_weight': 10.0}, {'textbook_example_id': 4597, 'component_id': 'src_4597', 'generator_key': 'src_4597', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4597', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4597, 'source_order': 4597, 'sampling_weight': 10.0}, {'textbook_example_id': 4598, 'component_id': 'src_4598', 'generator_key': 'src_4598', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4598', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4598, 'source_order': 4598, 'sampling_weight': 10.0}, {'textbook_example_id': 4599, 'component_id': 'src_4599', 'generator_key': 'src_4599', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4599', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4599, 'source_order': 4599, 'sampling_weight': 10.0}]


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
