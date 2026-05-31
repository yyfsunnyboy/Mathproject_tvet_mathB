from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_LinearFunction'
GENERATOR_KEYS = ['vh_數學B1_LinearFunction:numeric_interpret_function_notation_short_answer:spec_v1']
GENERATOR_SPECS = [{'problem_type_id': 'numeric_interpret_function_notation_short_answer', 'checker_key': 'numeric_checker', 'equivalence_type': 'numeric_exact', 'generator_readiness': 'runtime_ready'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
