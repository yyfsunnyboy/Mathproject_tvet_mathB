import random
from typing import Any
from math import gcd
from fractions import Fraction

PROBLEM_TYPE_ID = "perpendicular_line_equation"
SKILL_ID = "vh_數學B1_PropertiesOfPerpendicularLines"
SUBSKILL_ID = "perpendicular_lines_properties"

def generate(seed: int | None = None, difficulty: str | int | None = "easy", **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # Generate line equation L: ax + by + c = 0
    # a, b must be non-zero integers to avoid horizontal/vertical line edge cases.
    a = rng.choice([x for x in range(-6, 7) if x != 0])
    b = rng.choice([x for x in range(-6, 7) if x != 0])
    c = rng.choice([x for x in range(-15, 16) if x != 0])
    
    # Given point P(x0, y0)
    x0 = rng.randint(-8, 8)
    y0 = rng.randint(-8, 8)
    
    # L' passes through P(x0, y0) and is perpendicular to L.
    # The slope of L is -a/b.
    # The slope of L' is b/a.
    # L' equation: b(x - x0) - a(y - y0) = 0 => bx - ay + (ay0 - bx0) = 0.
    A_prime = b
    B_prime = -a
    C_prime = a * y0 - b * x0
    
    # Simplify L' equation Ax + By + C = 0
    g = gcd(gcd(abs(A_prime), abs(B_prime)), abs(C_prime))
    if g == 0:
        g = 1
    A_final = A_prime // g
    B_final = B_prime // g
    C_final = C_prime // g
    
    # Standardize so A_final >= 0 (if A_final == 0, B_final > 0)
    if A_final < 0 or (A_final == 0 and B_final < 0):
        A_final = -A_final
        B_final = -B_final
        C_final = -C_final
        
    # Construct string representation of answer
    # bx - ay + c = 0
    parts = []
    if A_final == 1:
        parts.append("x")
    elif A_final > 1:
        parts.append(f"{A_final}x")
        
    # Y term
    if B_final == 1:
        parts.append("+y" if parts else "y")
    elif B_final == -1:
        parts.append("-y")
    elif B_final > 1:
        parts.append(f"+{B_final}y" if parts else f"{B_final}y")
    elif B_final < -1:
        parts.append(f"{B_final}y")
        
    # Constant term
    if C_final > 0:
        parts.append(f"+{C_final}")
    elif C_final < 0:
        parts.append(f"{C_final}")
    elif C_final == 0 and not parts:
        parts.append("0")
        
    answer = "".join(parts) + "=0"
    
    # Construct L display
    parts_L = []
    if a == 1:
        parts_L.append("x")
    elif a == -1:
        parts_L.append("-x")
    elif a > 1 or a < -1:
        parts_L.append(f"{a}x")
        
    if b == 1:
        parts_L.append("+y" if parts_L else "y")
    elif b == -1:
        parts_L.append("-y")
    elif b > 1:
        parts_L.append(f"+{b}y" if parts_L else f"{b}y")
    elif b < -1:
        parts_L.append(f"{b}y")
        
    if c > 0:
        parts_L.append(f"+{c}")
    elif c < 0:
        parts_L.append(f"{c}")
    L_equation_str = "".join(parts_L) + "=0"
    
    question_text = f"在坐標平面上，設直線$L$的方程式為${L_equation_str}$。試求通過點$P\\left( {x0},{y0} \\right)$且與直線$L$垂直的直線方程式。"
    
    solution_steps = [
        f"已知與直線 $L: {L_equation_str}$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        f"直線 $L$ 的斜率為 $m = -\\frac{{{a}}}{{{b}}} = {Fraction(-a, b) if b != 0 else 0}$。",
        f"因此，所求直線 $L'$ 的斜率為 $m' = \\frac{{{b}}}{{{a}}} = {Fraction(b, a) if a != 0 else 0}$。",
        f"利用點斜式，通過點 $P({x0},{y0})$ 且斜率為 $m'$ 的直線方程式為：",
        f"$y - ({y0}) = \\frac{{{b}}}{{{a}}} \\cdot (x - ({x0}))$，",
        f"整理化簡為一般式後可得：${answer}$。"
    ]
    
    answer_contract = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [answer],
        "checker_key": "text_short_checker",
        "equivalence_type": "exact_string",
    }
    
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"a={a}:b={b}:c={c}:answer={answer}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["perpendicular_line_equation"],
        "prerequisite_subskills": [],
        "givens": [f"L: {L_equation_str}", f"P({x0},{y0})"],
        "target": "perpendicular_line_equation",
        "derivation": solution_steps,
    }
    
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "text_short",
        "checker_type": "text_short_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\n".join(solution_steps),
        "choices": [],
        "answer_contract": answer_contract,
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    def clean(v):
        return str(v).replace(" ", "").replace("＝", "=").lower().strip()
    u = clean(user_answer)
    c = clean(correct_answer)
    if u == c:
        return {"correct": True}
    if u.replace("=0", "") == c.replace("=0", ""):
        return {"correct": True}
    if u.replace("0=", "") == c.replace("=0", ""):
        return {"correct": True}
    return {"correct": False}
