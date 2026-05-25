import random

PROBLEM_TYPE_ID = "number_line_point_value_reading"
SKILL_ID = "vh_數學B1_NumberLine"

def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    scenario_id = rng.randint(1, 5)
    if PROBLEM_TYPE_ID == "number_line_integer_ordering":
        nums = rng.sample(range(-20, 21), 4)
        q = f"將下列整數由小到大排列：$" + ", ".join(str(n) for n in nums) + "$"
        answer = ",".join(str(n) for n in sorted(nums))
        steps = ["比較正負與絕對值大小。", "依序排列得到答案。"]
    elif PROBLEM_TYPE_ID == "number_line_point_value_reading":
        x = rng.randint(-15, 15)
        q = f"數線上點 $P$ 對應到整數 ${x}$，已知 $P$ 在 ${x}$，求其數值。".replace("{x}", str(x))
        answer = str(x)
        steps = ["直接讀取數線上點的對應整數。"]
    elif PROBLEM_TYPE_ID == "absolute_value_numeric_evaluation":
        a = rng.randint(-20, 20)
        q = f"求 $|{a}|$ 的值。".replace("{a}", str(a))
        answer = str(abs(a))
        steps = ["絕對值表示到 0 的距離。", f"因此 $|{a}|={{ans}}$。".replace("{a}", str(a)).replace("{ans}", str(abs(a)))]
    elif PROBLEM_TYPE_ID == "absolute_value_distance_interpretation":
        a = rng.randint(-15, 15)
        b = rng.randint(-15, 15)
        q = f"在數線上，${a}$ 與 ${b}$ 的距離為多少？".replace("{a}", str(a)).replace("{b}", str(b))
        answer = str(abs(a - b))
        steps = ["兩點距離為差的絕對值。", f"$|{a}-{b}|={{ans}}$".replace("{a}", str(a)).replace("{b}", str(b)).replace("{ans}", str(abs(a-b)))]
    elif PROBLEM_TYPE_ID == "absolute_value_equation_basic":
        n = rng.randint(1, 12)
        q = f"解方程式：$|x|={{n}}$".replace("{n}", str(n))
        answer = f"x={n} 或 x={-n}"
        steps = ["絕對值方程有兩個對稱解。", f"$x={{n}}$ 或 $x=-{{n}}$".replace("{n}", str(n))]
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_less_than_basic":
        n = rng.randint(1, 12)
        q = f"解不等式：$|x|<{{n}}$".replace("{n}", str(n))
        answer = f"-{n}<x<{n}"
        steps = ["由絕對值小於型態得雙邊不等式。"]
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_greater_than_basic":
        n = rng.randint(1, 12)
        q = f"解不等式：$|x|>{{n}}$".replace("{n}", str(n))
        answer = f"x<{-n} 或 x>{n}"
        steps = ["由絕對值大於型態得兩側區間聯集。"]
    else:
        n = rng.randint(1, 12)
        q = f"將解集寫成區間：$|x|\leq {{n}}$".replace("{n}", str(n))
        answer = f"[{-n},{n}]"
        steps = ["絕對值小於等於轉成閉區間。"]

    payload = {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "question_text": q,
        "answer": answer,
        "answer_type": "choice" if "選擇" in q else "numeric_or_expression",
        "checker_type": "deterministic_checker",
        "solution_steps": steps,
        "metadata": {
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": scenario_id,
            "parameter_signature": f"{PROBLEM_TYPE_ID}:{scenario_id}:{difficulty}",
            "question_pattern_id": f"p{scenario_id}",
        },
    }
    return payload
