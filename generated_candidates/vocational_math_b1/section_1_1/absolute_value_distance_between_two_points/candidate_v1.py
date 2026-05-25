import random
PROBLEM_TYPE_ID = "absolute_value_distance_between_two_points"
SKILL_ID = "vh_數學B1_AbsoluteValue"
SUBSKILL_ID = "absolute_value_distance_between_two_points"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    if seed is not None:
        a = (int(seed) % 21) - 10
        b = ((int(seed) * 3 + 5) % 21) - 10
        if a == b:
            b = 10 if a != 10 else -10
    else:
        a = rng.randint(-10, 10)
        b = rng.randint(-10, 10)
        while b == a:
            b = rng.randint(-10, 10)
    dist = abs(b - a)
    question_text = f"已知數線上兩點 $A({a})$、$B({b})$，試求 A、B 兩點的距離。"
    solution_steps = [
        "數線上兩點距離等於兩坐標差的絕對值。",
        f"$|{b}-({a})|=|{b-a}|={dist}$。",
        f"所以 A、B 兩點的距離為 ${dist}$。",
    ]
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"absolute_value_distance_between_two_points:a={a}:b={b}:difficulty={difficulty}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["absolute_value_distance", "number_line_distance", "coordinate_difference"],
        "prerequisite_subskills": ["number_line_basic_position", "absolute_value_numeric_evaluation"],
    }
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": dist,
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": dist,
        "explanation": "\n".join(solution_steps),
        "choices": [],
    }
