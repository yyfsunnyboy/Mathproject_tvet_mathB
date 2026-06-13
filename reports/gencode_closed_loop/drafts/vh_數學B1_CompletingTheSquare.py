from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_CompletingTheSquare'
GENERATOR_KEYS = ['vh_數學B1_CompletingTheSquare:integer_quadratic_vertex_or_parameter_computation:draft_v1', 'vh_數學B1_CompletingTheSquare:integer_quadratic_graph_vertex_axis_choice:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'quadratic_vertex_or_parameter_computation', 'checker_key': 'rational_checker', 'equivalence_type': 'rational_equivalent', 'generator_readiness': 'contract_slot_mismatch', 'answer_type': 'rational', 'template_slot': 'quadratic_vertex_or_parameter_computation', 'base_problem_type_id': 'quadratic_vertex_or_parameter_computation', 'value_type_prefix': 'integer', 'presentation_mode': 'short_answer', 'answer_shape': 'scalar'}, {'problem_type_id': 'integer_quadratic_graph_vertex_axis_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'generator_readiness': 'runtime_ready', 'answer_type': 'single_choice', 'template_slot': 'quadratic_graph_vertex_axis_choice', 'base_problem_type_id': 'quadratic_graph_vertex_axis_choice', 'value_type_prefix': 'integer', 'presentation_mode': 'single_choice', 'answer_shape': 'single_choice'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
