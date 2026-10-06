from core.gencode.runtime_skill_wrapper import generate_for_skill, check_answer

SKILL_ID = "vh_數學B1_AbsoluteValue"
GENERATOR_KEYS = [
    "vh_數學B1_AbsoluteValue:absolute_value_distance_from_zero:draft_v1"
]
GENERATOR_SPECS = [
    {
        "problem_type_id": "absolute_value_distance_from_zero",
        "checker_key": "choice_checker",
        "equivalence_type": "exact_string",
        "generator_readiness": "runtime_ready",
        "answer_type": "choice"
    }
]

def generate(level=1, seed=None, difficulty=None, **kwargs):
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty, **kwargs)

def check(user_answer, correct_answer, question_payload=None):
    return check_answer(user_answer, correct_answer, payload=question_payload)