from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_LinearFunction'
GENERATOR_KEYS = ['vh_數學B1_LinearFunction:integer_evaluate_function_value:draft_v1', 'vh_數學B1_LinearFunction:expression_interpret_function_notation:draft_v1', 'vh_數學B1_LinearFunction:expression_evaluate_function_value:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'integer_evaluate_function_value', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'generator_readiness': 'runtime_ready'}, {'problem_type_id': 'expression_interpret_function_notation', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'generator_readiness': 'runtime_ready'}, {'problem_type_id': 'expression_evaluate_function_value', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'generator_readiness': 'runtime_ready'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
