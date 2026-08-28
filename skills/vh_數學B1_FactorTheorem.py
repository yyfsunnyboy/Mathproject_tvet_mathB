from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_FactorTheorem'
GENERATOR_KEYS = ['src_4646', 'src_4647', 'src_4648', 'src_4649', 'src_4650', 'src_4651', 'src_4652', 'src_4653', 'src_4654', 'src_4660', 'src_4661', 'src_4662', 'src_4663']
GENERATOR_SPECS = [{'textbook_example_id': 4646, 'component_id': 'src_4646', 'generator_key': 'src_4646', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4646, 'source_order': 4646, 'sampling_weight': 10.0}, {'textbook_example_id': 4647, 'component_id': 'src_4647', 'generator_key': 'src_4647', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4647, 'source_order': 4647, 'sampling_weight': 10.0}, {'textbook_example_id': 4648, 'component_id': 'src_4648', 'generator_key': 'src_4648', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4648, 'source_order': 4648, 'sampling_weight': 10.0}, {'textbook_example_id': 4649, 'component_id': 'src_4649', 'generator_key': 'src_4649', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4649, 'source_order': 4649, 'sampling_weight': 10.0}, {'textbook_example_id': 4650, 'component_id': 'src_4650', 'generator_key': 'src_4650', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4650, 'source_order': 4650, 'sampling_weight': 10.0}, {'textbook_example_id': 4651, 'component_id': 'src_4651', 'generator_key': 'src_4651', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4651, 'source_order': 4651, 'sampling_weight': 10.0}, {'textbook_example_id': 4652, 'component_id': 'src_4652', 'generator_key': 'src_4652', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4652, 'source_order': 4652, 'sampling_weight': 10.0}, {'textbook_example_id': 4653, 'component_id': 'src_4653', 'generator_key': 'src_4653', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4653, 'source_order': 4653, 'sampling_weight': 10.0}, {'textbook_example_id': 4654, 'component_id': 'src_4654', 'generator_key': 'src_4654', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4654, 'source_order': 4654, 'sampling_weight': 10.0}, {'textbook_example_id': 4660, 'component_id': 'src_4660', 'generator_key': 'src_4660', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4660, 'source_order': 4660, 'sampling_weight': 10.0}, {'textbook_example_id': 4661, 'component_id': 'src_4661', 'generator_key': 'src_4661', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4661, 'source_order': 4661, 'sampling_weight': 10.0}, {'textbook_example_id': 4662, 'component_id': 'src_4662', 'generator_key': 'src_4662', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4662, 'source_order': 4662, 'sampling_weight': 10.0}, {'textbook_example_id': 4663, 'component_id': 'src_4663', 'generator_key': 'src_4663', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'factor_theorem_root_factor', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'factor_theorem_root_factor', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4663, 'source_order': 4663, 'sampling_weight': 10.0}]


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
