from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_QuadraticFunctionGraph'
GENERATOR_KEYS = ['vh_數學B1_QuadraticFunctionGraph:text_short_contextual_application:draft_v1', 'vh_數學B1_QuadraticFunctionGraph:choice_contextual_application:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'text_short_contextual_application', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'generator_readiness': 'runtime_ready'}, {'problem_type_id': 'choice_contextual_application', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'generator_readiness': 'runtime_ready'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
