import random
PROBLEM_TYPE_ID = "absolute_value_distance_from_zero"
SKILL_ID = "vh_數學B1_AbsoluteValue"
SUBSKILL_ID = "absolute_value_distance_from_zero"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = -(((int(seed) % 20) + 1)) if seed is not None else -rng.randint(1, 20)
    question_text = f"下列哪一項是 $|{n}|$ 的正確意義？"
    correct = f"數線上 ${n}$ 到 $0$ 的距離"
    choices = [correct, f"數線上 ${abs(n)}$ 到 ${n}$ 的距離", f"${n}$ 本身", "一個負數"]
    solution_steps = ["絕對值表示數線上該數到 $0$ 的距離。", f"因此 $|{n}|$ 表示 ${n}$ 到 $0$ 的距離。"]
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"absolute_value_distance_from_zero:n={n}:pattern=meaning",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["absolute_value_meaning", "distance_from_zero"],
        "prerequisite_subskills": ["number_line_basic_position"],
    }
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "choices": choices,
        "answer": correct,
        "answer_type": "choice",
        "checker_type": "choice_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": correct,
        "explanation": "\n".join(solution_steps),
    }
