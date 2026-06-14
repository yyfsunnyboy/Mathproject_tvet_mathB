import random
from typing import Any
from fractions import Fraction

PROBLEM_TYPE_ID = "text_short_slope_of_line_problems"
SKILL_ID = "vh_數學B1_SlopeOfALine"
SUBSKILL_ID = "text_short_slope_of_line_problems"

def generate(seed: int | None = None, difficulty: str | int | None = "easy", **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # We support 4 variants based on a random choice
    variant = rng.randint(0, 3)
    
    if variant == 0:
        # Variant 0: Calculate slope, integer answer
        # m = (y2 - y1) / (x2 - x1)
        # Choose x1, x2, and integer slope m.
        m = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        x1 = rng.randint(-10, 10)
        x2 = x1 + rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        y1 = rng.randint(-10, 10)
        y2 = y1 + m * (x2 - x1)
        
        question_text = f"試求過兩點 $A({x1}, {y1})$ 與 $B({x2}, {y2})$ 的直線斜率。"
        answer_val = Fraction(m, 1)
        solution_steps = [
            f"已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{{y_2 - y_1}}{{x_2 - x_1}}$。",
            f"將點 $A({x1}, {y1})$ 與 $B({x2}, {y2})$ 代入公式中：",
            f"$m = \\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}}$",
            f"$m = \\frac{{{y2 - y1}}}{{{x2 - x1}}} = {m}$。",
            f"因此，直線的斜率為 {m}。"
        ]
        
    elif variant == 1:
        # Variant 1: Calculate slope, fraction answer (non-integer)
        # Choose x1, x2, and y1, y2 such that slope is not an integer.
        while True:
            x1 = rng.randint(-10, 10)
            x2 = x1 + rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            y1 = rng.randint(-10, 10)
            y2 = rng.randint(-10, 10)
            if (y2 - y1) % (x2 - x1) != 0:
                break
        
        answer_val = Fraction(y2 - y1, x2 - x1)
        question_text = f"試求過兩點 $A({x1}, {y1})$ 與 $B({x2}, {y2})$ 的直線斜率。"
        solution_steps = [
            f"已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{{y_2 - y_1}}{{x_2 - x_1}}$。",
            f"將點 $A({x1}, {y1})$ 與 $B({x2}, {y2})$ 代入公式中：",
            f"$m = \\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}}$",
            f"$m = \\frac{{{y2 - y1}}}{{{x2 - x1}}} = {answer_val}$。",
            f"因此，直線的斜率為 {answer_val}。"
        ]
        
    elif variant == 2:
        # Variant 2: Find unknown coordinate given integer slope
        # A(x1, a), B(x2, y2), slope is m. Find a.
        # m = (y2 - a) / (x2 - x1) -> a = y2 - m * (x2 - x1)
        m = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        x1 = rng.randint(-10, 10)
        x2 = x1 + rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        y2 = rng.randint(-10, 10)
        a = y2 - m * (x2 - x1)
        
        question_text = f"若直線通過點 $A({x1}, a)$ 與 $B({x2}, {y2})$，且其斜率為 {m}，試求 $a$ 之值。"
        answer_val = Fraction(a, 1)
        solution_steps = [
            f"根據直線斜率公式，斜率 $m = \\frac{{y_2 - y_1}}{{x_2 - x_1}}$。",
            f"將點 $A({x1}, a)$ 與 $B({x2}, {y2})$ 以及斜率 $m = {m}$ 代入：",
            f"${m} = \\frac{{{y2} - a}}{{{x2} - ({x1})}}$",
            f"${m} = \\frac{{{y2} - a}}{{{x2 - x1}}}$",
            f"兩邊同乘以 {x2 - x1} 得：",
            f"${m * (x2 - x1)} = {y2} - a$",
            f"解得 $a = {y2} - ({m * (x2 - x1)}) = {a}$。",
            f"因此，$a$ 的值為 {a}。"
        ]
        
    else:
        # Variant 3: Three collinear points
        # A(x1, y1), B(x2, k), C(x3, y3) are collinear. Find k.
        # Slope AB = Slope AC
        # We construct a line y = mx + c.
        # Choose m as Fraction
        while True:
            m_num = rng.choice([-3, -2, -1, 1, 2, 3])
            m_den = rng.choice([2, 3, 4])
            m = Fraction(m_num, m_den)
            # Choose integer x1, x2, x3 such that they are multiples of m_den (or mod m_den is same)
            # so that y coordinates are integers.
            x1 = rng.randint(-3, 3) * m_den
            x2 = rng.randint(-3, 3) * m_den
            x3 = rng.randint(-3, 3) * m_den
            if len({x1, x2, x3}) == 3:
                break
        
        # Ensure x1 < x2 < x3 for nicer order
        x1, x2, x3 = sorted([x1, x2, x3])
        c = rng.randint(-5, 5)
        y1 = int(m * x1 + c)
        y2 = int(m * x2 + c)
        y3 = int(m * x3 + c)
        
        # Variable is k at B's y coordinate
        k = y2
        
        question_text = f"若三點 $A({x1}, {y1})$、$B({x2}, k)$、$C({x3}, {y3})$ 共線，試求 $k$ 之值。"
        answer_val = Fraction(k, 1)
        slope_ac = Fraction(y3 - y1, x3 - x1)
        solution_steps = [
            f"因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{{AB}} = m_{{AC}}$)。",
            f"首先計算直線 $AC$ 的斜率：",
            f"$m_{{AC}} = \\frac{{{y3} - ({y1})}}{{{x3} - ({x1})}} = \\frac{{{y3 - y1}}}{{{x3 - x1}}} = {slope_ac}$。",
            f"接著利用 $m_{{AB}} = m_{{AC}}$ 列出等式：",
            f"$\\frac{{k - ({y1})}}{{{x2} - ({x1})}} = {slope_ac}$",
            f"$\\frac{{k - ({y1})}}{{{x2 - x1}}} = {slope_ac}$",
            f"兩邊同乘以 {x2 - x1} 得：",
            f"$k - ({y1}) = {slope_ac * (x2 - x1)}$",
            f"解得 $k = {int(slope_ac * (x2 - x1) + y1)}$。",
            f"因此，$k$ 的值為 {k}。"
        ]

    answer = str(answer_val)
    
    answer_contract = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
        "answer_type": "rational",
        "answer_shape": "scalar",
        "answer_equivalence": "rational_equivalent",
        "checker": "rational_checker",
        "accepted_formats": [answer],
        "checker_key": "rational_checker",
        "equivalence_type": "rational_equivalent",
    }
    
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"variant={variant}:answer={answer}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["slope_calculation", "collinearity"],
        "prerequisite_subskills": [],
    }
    
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "rational",
        "checker_type": "rational_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\n".join(solution_steps),
        "choices": [],
        "answer_contract": answer_contract,
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    def parse_val(v):
        s = str(v).strip()
        if "/" in s:
            parts = s.split("/")
            return Fraction(int(parts[0]), int(parts[1]))
        return Fraction(int(s), 1)
    try:
        ok = parse_val(user_answer) == parse_val(correct_answer)
    except Exception:
        ok = str(user_answer).strip() == str(correct_answer).strip()
    return {"correct": ok}
