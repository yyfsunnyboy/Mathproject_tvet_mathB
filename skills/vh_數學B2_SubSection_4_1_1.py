from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B2_SubSection_4_1_1'
GENERATOR_KEYS = ['src_11826', 'src_11827', 'src_11828', 'src_11829', 'src_11830', 'src_11831', 'src_11841', 'src_11842', 'src_11843', 'src_11844', 'src_11850', 'src_11877', 'src_11886', 'src_11887', 'src_11890', 'src_11891']
GENERATOR_SPECS = [{'textbook_example_id': 11826, 'component_id': 'src_11826', 'generator_key': 'src_11826', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11826, 'source_order': 11826, 'sampling_weight': 10.0}, {'textbook_example_id': 11827, 'component_id': 'src_11827', 'generator_key': 'src_11827', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11827, 'source_order': 11827, 'sampling_weight': 10.0}, {'textbook_example_id': 11828, 'component_id': 'src_11828', 'generator_key': 'src_11828', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'interpret_circular_locus_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interpret_circular_locus_equation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11828, 'source_order': 11828, 'sampling_weight': 10.0}, {'textbook_example_id': 11829, 'component_id': 'src_11829', 'generator_key': 'src_11829', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_equations_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11829, 'source_order': 11829, 'sampling_weight': 10.0}, {'textbook_example_id': 11830, 'component_id': 'src_11830', 'generator_key': 'src_11830', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11830, 'source_order': 11830, 'sampling_weight': 10.0}, {'textbook_example_id': 11831, 'component_id': 'src_11831', 'generator_key': 'src_11831', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11831, 'source_order': 11831, 'sampling_weight': 10.0}, {'textbook_example_id': 11841, 'component_id': 'src_11841', 'generator_key': 'src_11841', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11841, 'source_order': 11841, 'sampling_weight': 10.0}, {'textbook_example_id': 11842, 'component_id': 'src_11842', 'generator_key': 'src_11842', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_equations_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11842, 'source_order': 11842, 'sampling_weight': 10.0}, {'textbook_example_id': 11843, 'component_id': 'src_11843', 'generator_key': 'src_11843', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_equal_radius_at_origin', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_equal_radius_at_origin', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11843, 'source_order': 11843, 'sampling_weight': 10.0}, {'textbook_example_id': 11844, 'component_id': 'src_11844', 'generator_key': 'src_11844', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11844, 'source_order': 11844, 'sampling_weight': 10.0}, {'textbook_example_id': 11850, 'component_id': 'src_11850', 'generator_key': 'src_11850', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11850, 'source_order': 11850, 'sampling_weight': 10.0}, {'textbook_example_id': 11877, 'component_id': 'src_11877', 'generator_key': 'src_11877', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11877, 'source_order': 11877, 'sampling_weight': 10.0}, {'textbook_example_id': 11886, 'component_id': 'src_11886', 'generator_key': 'src_11886', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_origin_through_lines_intersection', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'circle_origin_through_lines_intersection', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11886, 'source_order': 11886, 'sampling_weight': 10.0}, {'textbook_example_id': 11887, 'component_id': 'src_11887', 'generator_key': 'src_11887', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_same_center_scaled_area', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'circle_same_center_scaled_area', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11887, 'source_order': 11887, 'sampling_weight': 10.0}, {'textbook_example_id': 11890, 'component_id': 'src_11890', 'generator_key': 'src_11890', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_center_tangent_to_line', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'circle_center_tangent_to_line', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11890, 'source_order': 11890, 'sampling_weight': 10.0}, {'textbook_example_id': 11891, 'component_id': 'src_11891', 'generator_key': 'src_11891', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11891, 'source_order': 11891, 'sampling_weight': 10.0}]


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
