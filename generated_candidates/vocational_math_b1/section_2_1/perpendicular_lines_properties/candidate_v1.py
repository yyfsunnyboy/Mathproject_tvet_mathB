import random
from typing import Any
from fractions import Fraction

PROBLEM_TYPE_ID = "perpendicular_lines_properties"
SKILL_ID = "vh_數學B1_PropertiesOfPerpendicularLines"
SUBSKILL_ID = "perpendicular_lines_properties"

def generate(seed: int | None = None, difficulty: str | int | None = "easy", **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # Choose two components for slope: m1 = a/b, m2 = -b/a
    pairs = [
        (1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2),
        (-1, 1), (-1, 2), (-2, 1), (-1, 3), (-3, 1), (-2, 3), (-3, 2)
    ]
    a, b = rng.choice(pairs)
    
    m1 = Fraction(a, b)
    m2 = Fraction(-b, a)
    
    x1 = rng.randint(-5, 5)
    y1 = rng.randint(-5, 5)
    k = rng.choice([-1, 1])
    x2 = x1 + b * k
    y2 = y1 + a * k
    
    x3 = rng.randint(-5, 5)
    while x3 == x1 or x3 == x2:
        x3 = rng.randint(-5, 5)
    y3 = rng.randint(-5, 5)
    
    j = rng.choice([-1, 1])
    x4 = x3 + a * j
    y4 = y3 - b * j
    
    template_type = rng.randint(1, 3)
    var_name = rng.choice(['x', 'a', 'k'])
    
    if template_type == 1:
        # y4 is unknown (var_name)
        val = y4
        question_text = f"設$A\\left( {x1},{y1} \\right)$、$B\\left( {x2},{y2} \\right)$與$C\\left( {x3},{y3} \\right)$、$D\\left( {x4},{var_name} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$垂直，試求{var_name}之值。"
        
        m_ab_str = f"\\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {m1}"
        m_cd_str = f"\\frac{{{var_name} - ({y3})}}{{{x4} - ({x3})}}"
        
        solution_steps = [
            f"因為$\\overline{{AB}}$與$\\overline{{CD}}$垂直，所以它們的斜率乘積為 $-1$。",
            f"直線AB的斜率為 $m_{{AB}} = {m_ab_str}$。",
            f"直線CD的斜率為 $m_{{CD}} = {m_cd_str}$。",
            f"由 $m_{{AB}} \\cdot m_{{CD}} = -1$ 可得：${m1} \\cdot \\frac{{{var_name} - ({y3})}}{{{x4 - x3}}} = -1$，",
            f"解得 {var_name} = {val}。"
        ]
    elif template_type == 2:
        # x4 is unknown (var_name)
        val = x4
        question_text = f"設$A\\left( {x1},{y1} \\right)$、$B\\left( {x2},{y2} \\right)$與$C\\left( {x3},{y3} \\right)$、$D\\left( {var_name},{y4} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$垂直，試求{var_name}之值。"
        
        m_ab_str = f"\\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {m1}"
        m_cd_str = f"\\frac{{{y4} - ({y3})}}{{{var_name} - ({x3})}}"
        
        solution_steps = [
            f"因為$\\overline{{AB}}$與$\\overline{{CD}}$垂直，所以它們的斜率乘積為 $-1$。",
            f"直線AB的斜率為 $m_{{AB}} = {m_ab_str}$。",
            f"直線CD的斜率為 $m_{{CD}} = {m_cd_str}$。",
            f"由 $m_{{AB}} \\cdot m_{{CD}} = -1$ 可得：${m1} \\cdot \\frac{{{y4 - y3}}}{{{var_name} - ({x3})}} = -1$，",
            f"解得 {var_name} = {val}。"
        ]
    else:
        # y1 is unknown (var_name)
        val = y1
        question_text = f"設$A\\left( {x1},{var_name} \\right)$、$B\\left( {x2},{y2} \\right)$與$C\\left( {x3},{y3} \\right)$、$D\\left( {x4},{y4} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$垂直，試求{var_name}之值。"
        
        m_ab_str = f"\\frac{{{y2} - {var_name}}}{{{x2} - ({x1})}}"
        m_cd_str = f"\\frac{{{y4} - ({y3})}}{{{x4} - ({x3})}} = {m2}"
        
        solution_steps = [
            f"因為$\\overline{{AB}}$與$\\overline{{CD}}$垂直，所以它們的斜率乘積為 $-1$。",
            f"直線AB的斜率為 $m_{{AB}} = {m_ab_str}$。",
            f"直線CD的斜率為 $m_{{CD}} = {m_cd_str}$。",
            f"由 $m_{{AB}} \\cdot m_{{CD}} = -1$ 可得：\\frac{{{y2} - {var_name}}}{{{x2 - x1}}} \\cdot ({m2}) = -1，",
            f"解得 {var_name} = {val}。"
        ]

    answer = str(val)
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
        "parameter_signature": f"m1={m1}:template={template_type}:answer={answer}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["perpendicular_lines_slope_product"],
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
