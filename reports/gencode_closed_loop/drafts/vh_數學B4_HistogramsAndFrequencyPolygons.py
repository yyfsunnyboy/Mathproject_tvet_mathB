from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B4_HistogramsAndFrequencyPolygons'
GENERATOR_KEYS = ['vh_數學B4_HistogramsAndFrequencyPolygons:frequency_distribution_chart_construction:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'frequency_distribution_chart_construction', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': 'drawing_equivalence', 'generator_readiness': 'runtime_ready', 'answer_type': 'drawing', 'template_slot': 'frequency_distribution_chart_construction', 'base_problem_type_id': 'frequency_distribution_chart_construction', 'target_task': 'frequency_distribution_chart_construction', 'presentation_mode': 'short_answer', 'answer_shape': 'drawing', 'max_attempts': 10, 'hard_constraints': [{'left': {'var': 'total_frequency'}, 'operator': '>=', 'right': {'value': 12}}]}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
