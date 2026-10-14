from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_CoterminalAngles'
GENERATOR_KEYS = ['src_11611', 'src_11612', 'src_11613', 'src_11614', 'src_11615', 'src_11621', 'src_11622', 'src_11623']
GENERATOR_SPECS = [{'textbook_example_id': 11611, 'component_id': 'src_11611', 'generator_key': 'src_11611', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set', 'display_order': 11611, 'source_order': 11611, 'sampling_weight': 1.0}, {'textbook_example_id': 11612, 'component_id': 'src_11612', 'generator_key': 'src_11612', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set', 'display_order': 11612, 'source_order': 11612, 'sampling_weight': 1.0}, {'textbook_example_id': 11613, 'component_id': 'src_11613', 'generator_key': 'src_11613', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11613, 'source_order': 11613, 'sampling_weight': 1.0}, {'textbook_example_id': 11614, 'component_id': 'src_11614', 'generator_key': 'src_11614', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11614, 'source_order': 11614, 'sampling_weight': 1.0}, {'textbook_example_id': 11615, 'component_id': 'src_11615', 'generator_key': 'src_11615', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'coterminal_angles', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 11615, 'source_order': 11615, 'sampling_weight': 1.0}, {'textbook_example_id': 11621, 'component_id': 'src_11621', 'generator_key': 'src_11621', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'solution_set_checker', 'equivalence_type': 'unordered_solution_set', 'display_order': 11621, 'source_order': 11621, 'sampling_weight': 1.0}, {'textbook_example_id': 11622, 'component_id': 'src_11622', 'generator_key': 'src_11622', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11622, 'source_order': 11622, 'sampling_weight': 1.0}, {'textbook_example_id': 11623, 'component_id': 'src_11623', 'generator_key': 'src_11623', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coterminal_angles', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coterminal_angles', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 11623, 'source_order': 11623, 'sampling_weight': 1.0}]


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
