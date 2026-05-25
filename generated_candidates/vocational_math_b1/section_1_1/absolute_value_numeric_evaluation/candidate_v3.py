import random

PROBLEM_TYPE_ID = "absolute_value_numeric_evaluation"
SKILL_ID = "vh_數學B1_AbsoluteValue"
SUBSKILL_ID = "absolute_value_numeric_evaluation"

def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = rng.randint(-20, 20)
    answer = abs(n)
    question_text = f"求 $|{n}|$ 的值。"
    solution_steps = ["絕對值表示到 0 的距離。", f"因此 $|{n}|={{ans}}$。".replace("{ans}", str(answer))]
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"absolute_value_numeric_evaluation:n={n}:difficulty={difficulty}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["absolute_value_definition", "sign_error"],
        "prerequisite_subskills": [],
    }
    payload = {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
    }
    return payload
