from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'gh_Mean'
GENERATOR_KEYS = ['src_12912', 'src_12913', 'src_12914', 'src_12915', 'src_12916', 'src_12917', 'src_12931', 'src_12936', 'src_12937']
GENERATOR_SPECS = [{'textbook_example_id': 12912, 'component_id': 'src_12912', 'generator_key': 'src_12912', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12912, 'source_order': 12912, 'sampling_weight': 10.0}, {'textbook_example_id': 12913, 'component_id': 'src_12913', 'generator_key': 'src_12913', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'weighted_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'weighted_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12913, 'source_order': 12913, 'sampling_weight': 10.0}, {'textbook_example_id': 12914, 'component_id': 'src_12914', 'generator_key': 'src_12914', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_growth_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_growth_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12914, 'source_order': 12914, 'sampling_weight': 10.0}, {'textbook_example_id': 12915, 'component_id': 'src_12915', 'generator_key': 'src_12915', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12915, 'source_order': 12915, 'sampling_weight': 10.0}, {'textbook_example_id': 12916, 'component_id': 'src_12916', 'generator_key': 'src_12916', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'weighted_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'weighted_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12916, 'source_order': 12916, 'sampling_weight': 10.0}, {'textbook_example_id': 12917, 'component_id': 'src_12917', 'generator_key': 'src_12917', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_growth_unknown', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_growth_unknown', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12917, 'source_order': 12917, 'sampling_weight': 10.0}, {'textbook_example_id': 12931, 'component_id': 'src_12931', 'generator_key': 'src_12931', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'true_false_stat', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'true_false_stat', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12931, 'source_order': 12931, 'sampling_weight': 10.0}, {'textbook_example_id': 12936, 'component_id': 'src_12936', 'generator_key': 'src_12936', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'weighted_mean_unknown', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'weighted_mean_unknown', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12936, 'source_order': 12936, 'sampling_weight': 10.0}, {'textbook_example_id': 12937, 'component_id': 'src_12937', 'generator_key': 'src_12937', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_growth_mean', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_growth_mean', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12937, 'source_order': 12937, 'sampling_weight': 10.0}]


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
