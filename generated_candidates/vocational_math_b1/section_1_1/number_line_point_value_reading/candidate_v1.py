import random

PROBLEM_TYPE_ID = "number_line_point_value_reading"
SKILL_ID = "vh_數學B1_NumberLine"

def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    scenario_id = rng.randint(1, 5)

    if PROBLEM_TYPE_ID == "absolute_value_numeric_evaluation":
        n = rng.randint(-20, 20)
        question_text = f"求 $|{n}|$ 的值。"
        answer = str(abs(n))
        answer_type = "integer"
        checker_type = "integer_checker"
        solution_steps = ["絕對值表示到 0 的距離。", f"因此 $|{n}|={{ans}}$。".replace("{ans}", str(abs(n)))]
        parameter_signature = f"{PROBLEM_TYPE_ID}:n={n}:difficulty={difficulty}"
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_greater_than_basic":
        n = rng.randint(1, 12)
        question_text = f"解不等式：$|x|>{n}$"
        answer = f"x<{-n} 或 x>{n}"
        answer_type = "numeric_or_expression"
        checker_type = "deterministic_checker"
        solution_steps = ["解集為兩側區間聯集。"]
        parameter_signature = f"{PROBLEM_TYPE_ID}:n={n}:difficulty={difficulty}"
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_interval_interpretation":
        n = rng.randint(1, 12)
        question_text = f"將解集寫成區間：$|x|\leq {n}$"
        answer = f"[{-n},{n}]"
        answer_type = "numeric_or_expression"
        checker_type = "deterministic_checker"
        solution_steps = ["轉為閉區間。"]
        parameter_signature = f"{PROBLEM_TYPE_ID}:n={n}:difficulty={difficulty}"
    else:
        x = rng.randint(-15, 15)
        question_text = f"數線上點 $P$ 對應整數 ${x}$，求點 $P$ 的數值。"
        answer = str(x)
        answer_type = "numeric_or_expression"
        checker_type = "deterministic_checker"
        solution_steps = ["直接讀值。"]
        parameter_signature = f"{PROBLEM_TYPE_ID}:x={x}:difficulty={difficulty}"

    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": answer_type,
        "checker_type": checker_type,
        "solution_steps": solution_steps,
        "metadata": {
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": scenario_id,
            "parameter_signature": parameter_signature,
            "question_pattern_id": f"p{scenario_id}",
        },
    }
