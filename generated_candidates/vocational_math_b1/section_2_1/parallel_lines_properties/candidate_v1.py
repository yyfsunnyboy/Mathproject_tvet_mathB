import random
from typing import Any

PROBLEM_TYPE_ID = "parallel_lines_properties"
SKILL_ID = "vh_數學B1_PropertiesOfParallelLines"
SUBSKILL_ID = "parallel_lines_properties"

def generate(seed: int | None = None, difficulty: str | int | None = "easy", **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    m = rng.choice([-3, -2, -1, 1, 2, 3])
    
    x1 = rng.randint(-5, 5)
    y1 = rng.randint(-5, 5)
    dx1 = rng.choice([-3, -2, -1, 1, 2, 3])
    x2 = x1 + dx1
    y2 = y1 + m * dx1
    
    x3 = rng.randint(-5, 5)
    while x3 == x1 or x3 == x2:
        x3 = rng.randint(-5, 5)
    y3 = rng.randint(-5, 5)
    
    dx2 = rng.choice([-3, -2, -1, 1, 2, 3])
    x4 = x3 + dx2
    y4 = y3 + m * dx2
    
    template_type = rng.randint(1, 3)
    var_name = rng.choice(['x', 'a'])
    
    # Formatting helper for var_name - y3
    if y3 < 0:
        var_minus_y3 = f"{var_name} + {abs(y3)}"
    elif y3 > 0:
        var_minus_y3 = f"{var_name} - {y3}"
    else:
        var_minus_y3 = var_name

    # Formatting helper for y4 - var_name
    if y4 == 0:
        y4_minus_var = f"-{var_name}"
    else:
        y4_minus_var = f"{y4} - {var_name}"
        
    if template_type == 1:
        val = y4
        question_text = f"設$A\\left( {x1},{y1} \\right)$、$B\\left( {x2},{y2} \\right)$指標和$C\\left( {x3},{y3} \\right)$、$D\\left( {x4},{var_name} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$平行，試求{var_name}之值。"
        # We replace the text slightly to align with expected textbook format
        question_text = f"設$A\\left( {x1},{y1} \\right)$、$B\\left( {x2},{y2} \\right)$、$C\\left( {x3},{y3} \\right)$、$D\\left( {x4},{var_name} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$平行，試求{var_name}之值。"
        solution_steps = [
            f"因為$\\overline{{AB}}$與$\\overline{{CD}}$平行，所以它們的斜率相等。",
            f"直線AB的斜率為 $m_{{AB}} = \\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {m}$。",
            f"直線CD的斜率為 $m_{{CD}} = \\frac{{{var_minus_y3}}}{{{x4} - ({x3})}} = \\frac{{{var_minus_y3}}}{{{dx2}}}$。",
            f"由 $m_{{AB}} = m_{{CD}}$ 可得：$\\frac{{{var_minus_y3}}}{{{dx2}}} = {m}$，",
            f"所以 ${var_minus_y3} = {m * dx2}$，解得 {var_name} = {val}。"
        ]
    elif template_type == 2:
        val = y3
        question_text = f"設$A\\left( {x1},{y1} \\right)$、$B\\left( {x2},{y2} \\right)$、$C\\left( {x3},{var_name} \\right)$、$D\\left( {x4},{y4} \\right)$，若$\\overline{{AB}}$與$\\overline{{CD}}$平行，試求{var_name}之值。"
        solution_steps = [
            f"因為$\\overline{{AB}}$與$\\overline{{CD}}$平行，所以它們的斜率相等。",
            f"直線AB的斜率為 $m_{{AB}} = \\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {m}$。",
            f"直線CD的斜率為 $m_{{CD}} = \\frac{{{y4_minus_var}}}{{{x4} - ({x3})}} = \\frac{{{y4_minus_var}}}{{{dx2}}}$。",
            f"由 $m_{{AB}} = m_{{CD}}$ 可得：$\\frac{{{y4_minus_var}}}{{{dx2}}} = {m}$，",
            f"所以 ${y4_minus_var} = {m * dx2}$，解得 {var_name} = {val}。"
        ]
    else:
        val = y4
        question_text = f"平面上過兩點$\\left( {x1},{y1} \\right)$、$\\left( {x2},{y2} \\right)$的直線和過另兩點$\\left( {x3},{y3} \\right)$、$\\left( {x4},{var_name} \\right)$的直線平行，則{var_name} = "
        solution_steps = [
            f"因為兩直線平行，所以它們的斜率相等。",
            f"第一條直線的斜率為 $m_1 = \\frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {m}$。",
            f"第二條直線的斜率為 $m_2 = \\frac{{{var_minus_y3}}}{{{x4} - ({x3})}} = \\frac{{{var_minus_y3}}}{{{dx2}}}$。",
            f"由 $m_1 = m_2$ 可得：$\\frac{{{var_minus_y3}}}{{{dx2}}} = {m}$，",
            f"所以 ${var_minus_y3} = {m * dx2}$，解得 {var_name} = {val}。"
        ]

    answer = str(val)
    answer_contract = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
        "answer_type": "integer",
        "answer_shape": "scalar",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [answer],
        "checker_key": "integer_checker",
        "equivalence_type": "numeric_exact",
    }
    
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"m={m}:template={template_type}:answer={answer}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["parallel_lines_slope_equality"],
        "prerequisite_subskills": [],
    }
    
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\n".join(solution_steps),
        "choices": [],
        "answer_contract": answer_contract,
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        ok = int(str(user_answer).strip()) == int(str(correct_answer).strip())
    except Exception:
        ok = str(user_answer).strip() == str(correct_answer).strip()
    return {"correct": ok}
