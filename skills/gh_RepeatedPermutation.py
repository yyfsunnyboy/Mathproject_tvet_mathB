from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_RepeatedPermutation'
GENERATOR_KEYS = ['src_12804', 'src_12805', 'src_12806', 'src_12807', 'src_12808', 'src_12809', 'src_12810', 'src_12811']
GENERATOR_SPECS = [{'textbook_example_id': 12804, 'component_id': 'src_12804', 'generator_key': 'src_12804', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'distribute_distinct', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distribute_distinct', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12804, 'source_order': 12804, 'sampling_weight': 10.0}, {'textbook_example_id': 12805, 'component_id': 'src_12805', 'generator_key': 'src_12805', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'distribute_distinct', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distribute_distinct', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12805, 'source_order': 12805, 'sampling_weight': 10.0}, {'textbook_example_id': 12806, 'component_id': 'src_12806', 'generator_key': 'src_12806', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'distribute_distinct', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distribute_distinct', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12806, 'source_order': 12806, 'sampling_weight': 10.0}, {'textbook_example_id': 12807, 'component_id': 'src_12807', 'generator_key': 'src_12807', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'distribute_distinct', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distribute_distinct', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12807, 'source_order': 12807, 'sampling_weight': 10.0}, {'textbook_example_id': 12808, 'component_id': 'src_12808', 'generator_key': 'src_12808', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12808, 'source_order': 12808, 'sampling_weight': 10.0}, {'textbook_example_id': 12809, 'component_id': 'src_12809', 'generator_key': 'src_12809', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identical_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'identical_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12809, 'source_order': 12809, 'sampling_weight': 10.0}, {'textbook_example_id': 12810, 'component_id': 'src_12810', 'generator_key': 'src_12810', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'distribute_distinct', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distribute_distinct', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12810, 'source_order': 12810, 'sampling_weight': 10.0}, {'textbook_example_id': 12811, 'component_id': 'src_12811', 'generator_key': 'src_12811', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'distribute_distinct', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distribute_distinct', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12811, 'source_order': 12811, 'sampling_weight': 10.0}]


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
