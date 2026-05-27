from __future__ import annotations

from typing import Any

SKILL_ID = 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning'
GENERATOR_KEYS = ['vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning:absolute_value_inequality_linear_expression_basic:draft_v1', 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning:absolute_value_inequality_geometric_meaning:draft_v1']

def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    problem_type_id = GENERATOR_KEYS[0].split(':')[1] if GENERATOR_KEYS else 'draft_pending_problem_type'
    return {
        'skill_id': SKILL_ID,
        'problem_type_id': problem_type_id,
        'question_text': '[DRAFT] generator draft pending implementation',
        'question': '[DRAFT] generator draft pending implementation',
        'answer': '',
        'correct_answer': '',
        'answer_contract': {'type': 'draft_pending'},
        'source': 'gencode_phase3_draft',
    }

def check(user_answer: Any, correct_answer: Any):
    return str(user_answer).strip() == str(correct_answer).strip()
