import random
PROBLEM_TYPE_ID = "absolute_value_equation_basic"
SKILL_ID = "vh_數學B1_AbsoluteValue"
SUBSKILL_ID = "absolute_value_equation_basic"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = ((int(seed) % 20) + 1) if seed is not None else rng.randint(1, 20)
    question_text = f"解方程式 $|x|={n}$。"
    answer = f"x=-{n} 或 x={n}"
    solution_steps = [f"$|x|={n}$ 表示 $x$ 到 $0$ 的距離為 ${n}$。", f"因此 $x=-{n}$ 或 $x={n}$。"]
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"absolute_value_equation_basic:n={n}:difficulty={difficulty}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["absolute_value_equation", "two_solutions"],
        "prerequisite_subskills": ["absolute_value_numeric_evaluation"],
    }
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "text",
        "checker_type": "exact_string_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\n".join(solution_steps),
        "choices": [],
    }
