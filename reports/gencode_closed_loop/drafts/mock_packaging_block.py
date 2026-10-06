from core.gencode.runtime_skill_wrapper import generate_for_skill, check_answer

SKILL_ID = "vh_數學B1_AbsoluteValue"
GENERATOR_KEYS = [
    "vh_數學B1_AbsoluteValue:absolute_value_numeric_evaluation:draft_v1"
]
GENERATOR_SPECS = [
    {
        "problem_type_id": "absolute_value_numeric_evaluation",
        "checker_key": "integer_checker",
        "equivalence_type": "exact_match",
        "generator_readiness": "runtime_ready",
        "answer_type": "integer",
        "metadata": {
            "scenario_family": "standard",
            "scenario_id": "absolute_value_numeric_evaluation_std",
            "parameter_signature": "numeric_eval_v1",
            "question_pattern_id": "abs_eval_num",
            "diagnosis_tags": ["absolute_value_concept"],
            "prerequisite_subskills": ["absolute_value_basic"]
        },
        "givens": {
            "expression": "|x|"
        },
        "target": "evaluation"
    }
]

def generate(level=1, seed=None, difficulty=None, **kwargs):
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty, **kwargs)

def check(user_answer, correct_answer, question_payload=None):
    return check_answer(user_answer, correct_answer, payload=question_payload)