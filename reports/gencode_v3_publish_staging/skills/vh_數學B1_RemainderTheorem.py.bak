from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_RemainderTheorem'
GENERATOR_KEYS = ['src_4638', 'src_4639', 'src_4640', 'src_4641', 'src_4642', 'src_4643', 'src_4644', 'src_4645', 'src_4656', 'src_4657', 'src_4658', 'src_4659', 'src_4664', 'src_4665', 'src_4666', 'src_4667', 'src_4668', 'src_4669', 'src_4670', 'src_4722']
GENERATOR_SPECS = [{'textbook_example_id': 4638, 'component_id': 'src_4638', 'generator_key': 'src_4638', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4638, 'source_order': 4638, 'sampling_weight': 10.0}, {'textbook_example_id': 4639, 'component_id': 'src_4639', 'generator_key': 'src_4639', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4639, 'source_order': 4639, 'sampling_weight': 10.0}, {'textbook_example_id': 4640, 'component_id': 'src_4640', 'generator_key': 'src_4640', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4640, 'source_order': 4640, 'sampling_weight': 10.0}, {'textbook_example_id': 4641, 'component_id': 'src_4641', 'generator_key': 'src_4641', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4641, 'source_order': 4641, 'sampling_weight': 10.0}, {'textbook_example_id': 4642, 'component_id': 'src_4642', 'generator_key': 'src_4642', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4642, 'source_order': 4642, 'sampling_weight': 10.0}, {'textbook_example_id': 4643, 'component_id': 'src_4643', 'generator_key': 'src_4643', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4643, 'source_order': 4643, 'sampling_weight': 10.0}, {'textbook_example_id': 4644, 'component_id': 'src_4644', 'generator_key': 'src_4644', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4644, 'source_order': 4644, 'sampling_weight': 10.0}, {'textbook_example_id': 4645, 'component_id': 'src_4645', 'generator_key': 'src_4645', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4645, 'source_order': 4645, 'sampling_weight': 10.0}, {'textbook_example_id': 4656, 'component_id': 'src_4656', 'generator_key': 'src_4656', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4656, 'source_order': 4656, 'sampling_weight': 10.0}, {'textbook_example_id': 4657, 'component_id': 'src_4657', 'generator_key': 'src_4657', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4657, 'source_order': 4657, 'sampling_weight': 10.0}, {'textbook_example_id': 4658, 'component_id': 'src_4658', 'generator_key': 'src_4658', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4658, 'source_order': 4658, 'sampling_weight': 10.0}, {'textbook_example_id': 4659, 'component_id': 'src_4659', 'generator_key': 'src_4659', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4659, 'source_order': 4659, 'sampling_weight': 10.0}, {'textbook_example_id': 4664, 'component_id': 'src_4664', 'generator_key': 'src_4664', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4664, 'source_order': 4664, 'sampling_weight': 10.0}, {'textbook_example_id': 4665, 'component_id': 'src_4665', 'generator_key': 'src_4665', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4665, 'source_order': 4665, 'sampling_weight': 10.0}, {'textbook_example_id': 4666, 'component_id': 'src_4666', 'generator_key': 'src_4666', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4666, 'source_order': 4666, 'sampling_weight': 10.0}, {'textbook_example_id': 4667, 'component_id': 'src_4667', 'generator_key': 'src_4667', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4667, 'source_order': 4667, 'sampling_weight': 10.0}, {'textbook_example_id': 4668, 'component_id': 'src_4668', 'generator_key': 'src_4668', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4668, 'source_order': 4668, 'sampling_weight': 10.0}, {'textbook_example_id': 4669, 'component_id': 'src_4669', 'generator_key': 'src_4669', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4669, 'source_order': 4669, 'sampling_weight': 10.0}, {'textbook_example_id': 4670, 'component_id': 'src_4670', 'generator_key': 'src_4670', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4670, 'source_order': 4670, 'sampling_weight': 10.0}, {'textbook_example_id': 4722, 'component_id': 'src_4722', 'generator_key': 'src_4722', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4722, 'source_order': 4722, 'sampling_weight': 10.0}]


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
