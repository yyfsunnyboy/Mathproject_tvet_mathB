from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_CommonSeriesSummationFormulas'
GENERATOR_KEYS = ['src_12732', 'src_12733', 'src_12734', 'src_12736', 'src_12737', 'src_12738', 'src_12740', 'src_12741', 'src_12742']
GENERATOR_SPECS = [{'textbook_example_id': 12732, 'component_id': 'src_12732', 'generator_key': 'src_12732', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'power_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'power_sums', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12732, 'source_order': 12732, 'sampling_weight': 10.0}, {'textbook_example_id': 12733, 'component_id': 'src_12733', 'generator_key': 'src_12733', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'power_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'power_sums', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12733, 'source_order': 12733, 'sampling_weight': 10.0}, {'textbook_example_id': 12734, 'component_id': 'src_12734', 'generator_key': 'src_12734', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'power_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'power_sums', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12734, 'source_order': 12734, 'sampling_weight': 10.0}, {'textbook_example_id': 12736, 'component_id': 'src_12736', 'generator_key': 'src_12736', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'power_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'power_sums', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12736, 'source_order': 12736, 'sampling_weight': 10.0}, {'textbook_example_id': 12737, 'component_id': 'src_12737', 'generator_key': 'src_12737', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'power_sums', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'power_sums', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12737, 'source_order': 12737, 'sampling_weight': 10.0}, {'textbook_example_id': 12738, 'component_id': 'src_12738', 'generator_key': 'src_12738', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'power_sums', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'power_sums', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12738, 'source_order': 12738, 'sampling_weight': 10.0}, {'textbook_example_id': 12740, 'component_id': 'src_12740', 'generator_key': 'src_12740', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'series_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'series_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12740, 'source_order': 12740, 'sampling_weight': 10.0}, {'textbook_example_id': 12741, 'component_id': 'src_12741', 'generator_key': 'src_12741', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'power_sums', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'power_sums', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12741, 'source_order': 12741, 'sampling_weight': 10.0}, {'textbook_example_id': 12742, 'component_id': 'src_12742', 'generator_key': 'src_12742', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'power_sums', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'power_sums', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12742, 'source_order': 12742, 'sampling_weight': 10.0}]


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
