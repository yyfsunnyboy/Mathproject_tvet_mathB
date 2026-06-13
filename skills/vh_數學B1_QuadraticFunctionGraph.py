from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_QuadraticFunctionGraph'
GENERATOR_KEYS = ['vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_translation_fill_blank:draft_v1', 'vh_數學B1_QuadraticFunctionGraph:rational_quadratic_graph_translation_fill_blank:draft_v1', 'vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_properties_choice:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'integer_quadratic_graph_translation_fill_blank', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'generator_readiness': 'runtime_ready', 'answer_type': 'text_short', 'template_slot': 'quadratic_graph_translation_fill_blank', 'base_problem_type_id': 'quadratic_graph_translation_fill_blank', 'value_type_prefix': 'integer', 'presentation_mode': 'short_answer', 'answer_shape': 'text_short'}, {'problem_type_id': 'rational_quadratic_graph_translation_fill_blank', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'generator_readiness': 'runtime_ready', 'answer_type': 'text_short', 'template_slot': 'quadratic_graph_translation_fill_blank', 'base_problem_type_id': 'quadratic_graph_translation_fill_blank', 'value_type_prefix': 'rational', 'presentation_mode': 'short_answer', 'answer_shape': 'text_short'}, {'problem_type_id': 'integer_quadratic_graph_properties_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'generator_readiness': 'runtime_ready', 'answer_type': 'single_choice', 'template_slot': 'quadratic_vertex_form_properties', 'base_problem_type_id': 'quadratic_graph_properties_choice', 'value_type_prefix': 'integer', 'presentation_mode': 'single_choice', 'answer_shape': 'single_choice'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
