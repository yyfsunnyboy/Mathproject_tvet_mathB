from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_PolynomialFactoring'
GENERATOR_KEYS = ['src_4671', 'src_4672', 'src_4673', 'src_4674', 'src_4675', 'src_4681', 'src_4682', 'src_4683', 'src_4684', 'src_4685', 'src_4694', 'src_4695', 'src_4696', 'src_4697', 'src_4701', 'src_4713', 'src_4714', 'src_4715']
GENERATOR_SPECS = [{'textbook_example_id': 4671, 'component_id': 'src_4671', 'generator_key': 'src_4671', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4671, 'source_order': 4671, 'sampling_weight': 10.0}, {'textbook_example_id': 4672, 'component_id': 'src_4672', 'generator_key': 'src_4672', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4672, 'source_order': 4672, 'sampling_weight': 10.0}, {'textbook_example_id': 4673, 'component_id': 'src_4673', 'generator_key': 'src_4673', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4673, 'source_order': 4673, 'sampling_weight': 10.0}, {'textbook_example_id': 4674, 'component_id': 'src_4674', 'generator_key': 'src_4674', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4674, 'source_order': 4674, 'sampling_weight': 10.0}, {'textbook_example_id': 4675, 'component_id': 'src_4675', 'generator_key': 'src_4675', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4675, 'source_order': 4675, 'sampling_weight': 10.0}, {'textbook_example_id': 4681, 'component_id': 'src_4681', 'generator_key': 'src_4681', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4681, 'source_order': 4681, 'sampling_weight': 10.0}, {'textbook_example_id': 4682, 'component_id': 'src_4682', 'generator_key': 'src_4682', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4682, 'source_order': 4682, 'sampling_weight': 10.0}, {'textbook_example_id': 4683, 'component_id': 'src_4683', 'generator_key': 'src_4683', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4683, 'source_order': 4683, 'sampling_weight': 10.0}, {'textbook_example_id': 4684, 'component_id': 'src_4684', 'generator_key': 'src_4684', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4684, 'source_order': 4684, 'sampling_weight': 10.0}, {'textbook_example_id': 4685, 'component_id': 'src_4685', 'generator_key': 'src_4685', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4685, 'source_order': 4685, 'sampling_weight': 10.0}, {'textbook_example_id': 4694, 'component_id': 'src_4694', 'generator_key': 'src_4694', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4694, 'source_order': 4694, 'sampling_weight': 10.0}, {'textbook_example_id': 4695, 'component_id': 'src_4695', 'generator_key': 'src_4695', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4695, 'source_order': 4695, 'sampling_weight': 10.0}, {'textbook_example_id': 4696, 'component_id': 'src_4696', 'generator_key': 'src_4696', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4696, 'source_order': 4696, 'sampling_weight': 10.0}, {'textbook_example_id': 4697, 'component_id': 'src_4697', 'generator_key': 'src_4697', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4697, 'source_order': 4697, 'sampling_weight': 10.0}, {'textbook_example_id': 4701, 'component_id': 'src_4701', 'generator_key': 'src_4701', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4701, 'source_order': 4701, 'sampling_weight': 10.0}, {'textbook_example_id': 4713, 'component_id': 'src_4713', 'generator_key': 'src_4713', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4713, 'source_order': 4713, 'sampling_weight': 10.0}, {'textbook_example_id': 4714, 'component_id': 'src_4714', 'generator_key': 'src_4714', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4714, 'source_order': 4714, 'sampling_weight': 10.0}, {'textbook_example_id': 4715, 'component_id': 'src_4715', 'generator_key': 'src_4715', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4715, 'source_order': 4715, 'sampling_weight': 10.0}]


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
