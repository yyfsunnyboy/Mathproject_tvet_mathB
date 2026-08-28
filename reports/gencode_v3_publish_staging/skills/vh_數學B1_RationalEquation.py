from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_RationalEquation'
GENERATOR_KEYS = ['src_4678', 'src_4679', 'src_4687', 'src_4688', 'src_4689', 'src_4690', 'src_4693', 'src_4698', 'src_4699', 'src_4700', 'src_4705']
GENERATOR_SPECS = [{'textbook_example_id': 4678, 'component_id': 'src_4678', 'generator_key': 'src_4678', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4678, 'source_order': 4678, 'sampling_weight': 10.0}, {'textbook_example_id': 4679, 'component_id': 'src_4679', 'generator_key': 'src_4679', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4679, 'source_order': 4679, 'sampling_weight': 10.0}, {'textbook_example_id': 4687, 'component_id': 'src_4687', 'generator_key': 'src_4687', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4687, 'source_order': 4687, 'sampling_weight': 10.0}, {'textbook_example_id': 4688, 'component_id': 'src_4688', 'generator_key': 'src_4688', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4688, 'source_order': 4688, 'sampling_weight': 10.0}, {'textbook_example_id': 4689, 'component_id': 'src_4689', 'generator_key': 'src_4689', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4689, 'source_order': 4689, 'sampling_weight': 10.0}, {'textbook_example_id': 4690, 'component_id': 'src_4690', 'generator_key': 'src_4690', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4690, 'source_order': 4690, 'sampling_weight': 10.0}, {'textbook_example_id': 4693, 'component_id': 'src_4693', 'generator_key': 'src_4693', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4693, 'source_order': 4693, 'sampling_weight': 10.0}, {'textbook_example_id': 4698, 'component_id': 'src_4698', 'generator_key': 'src_4698', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4698, 'source_order': 4698, 'sampling_weight': 10.0}, {'textbook_example_id': 4699, 'component_id': 'src_4699', 'generator_key': 'src_4699', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4699, 'source_order': 4699, 'sampling_weight': 10.0}, {'textbook_example_id': 4700, 'component_id': 'src_4700', 'generator_key': 'src_4700', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4700, 'source_order': 4700, 'sampling_weight': 10.0}, {'textbook_example_id': 4705, 'component_id': 'src_4705', 'generator_key': 'src_4705', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'rational_equation_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'rational_equation_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4705, 'source_order': 4705, 'sampling_weight': 10.0}]


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
