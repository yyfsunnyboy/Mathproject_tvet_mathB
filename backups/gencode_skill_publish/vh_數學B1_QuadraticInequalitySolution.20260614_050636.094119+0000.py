from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_QuadraticInequalitySolution'
GENERATOR_KEYS = ['vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality:draft_v1', 'vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality:draft_v1', 'vh_數學B1_QuadraticInequalitySolution:text_short_factor_quadratic_by_cross_multiplication:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'generator_readiness': 'runtime_ready', 'answer_type': 'interval', 'template_slot': 'solve_quadratic_inequality', 'base_problem_type_id': 'solve_quadratic_inequality', 'value_type_prefix': 'integer', 'target_task': 'solve_quadratic_inequality', 'presentation_mode': 'short_answer', 'answer_shape': 'interval_or_union'}, {'problem_type_id': 'rational_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'generator_readiness': 'runtime_ready', 'answer_type': 'interval', 'template_slot': 'solve_quadratic_inequality', 'base_problem_type_id': 'solve_quadratic_inequality', 'value_type_prefix': 'rational', 'target_task': 'solve_quadratic_inequality', 'presentation_mode': 'short_answer', 'answer_shape': 'interval_or_union'}, {'problem_type_id': 'text_short_factor_quadratic_by_cross_multiplication', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'generator_readiness': 'runtime_ready', 'answer_type': 'expression', 'template_slot': 'factor_quadratic_by_cross_multiplication', 'base_problem_type_id': 'factor_quadratic_by_cross_multiplication', 'value_type_prefix': 'text_short', 'target_task': 'factor_quadratic_by_cross_multiplication', 'presentation_mode': 'short_answer', 'answer_shape': 'factored_expression'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
