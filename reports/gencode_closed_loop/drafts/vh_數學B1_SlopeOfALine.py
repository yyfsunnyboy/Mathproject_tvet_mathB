from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_SlopeOfALine'
GENERATOR_KEYS = ['vh_數學B1_SlopeOfALine:integer_applied_quadratic_inequality_problem:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'generator_readiness': 'runtime_ready', 'answer_type': 'interval', 'template_slot': 'applied_quadratic_inequality_problem', 'base_problem_type_id': 'applied_quadratic_inequality_problem', 'value_type_prefix': 'integer', 'target_task': 'applied_quadratic_inequality_problem', 'presentation_mode': 'short_answer', 'answer_shape': 'interval_or_union'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
