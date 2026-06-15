from __future__ import annotations

import random
from typing import Any
from fractions import Fraction
from core.checkers.choice_label_checker import check_choice_label

PROBLEM_TYPE_ID = "triangle_right_angle_verification"
SKILL_ID = "vh_數學B1_PropertiesOfPerpendicularLines"
SUBSKILL_ID = "perpendicular_lines_properties"

def generate(level: int = 1, seed: int | None = None, difficulty: str | int | None = None, **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # 50% probability of being a right-angled triangle at the vertex being tested
    is_right_angle = rng.choice([True, False])
    
    # Randomly choose which vertex to test: A, B, or C
    test_vertex = rng.choice(["A", "B", "C"])
    
    while True:
        # Start with generating coordinates for a right angle at the test vertex
        # Let's call the test vertex V, and the other two U and W
        v_x = rng.randint(-5, 5)
        v_y = rng.randint(-5, 5)
        
        # Vector VU = (dx1, dy1) and vector VW = (dx2, dy2)
        # We want dx1 * dx2 + dy1 * dy2 = 0 for the right angle
        a = rng.choice([x for x in range(-4, 5) if x != 0])
        b = rng.choice([x for x in range(-4, 5) if x != 0])
        k = rng.choice([-2, -1, 1, 2])
        j = rng.choice([-2, -1, 1, 2])
        
        dx1 = a * k
        dy1 = b * k
        dx2 = -b * j
        dy2 = a * j
        
        u_x = v_x + dx1
        u_y = v_y + dy1
        w_x = v_x + dx2
        w_y = v_y + dy2
        
        if not is_right_angle:
            # Perturb W to break the perpendicularity
            perturb_y = rng.choice([-2, -1, 1, 2])
            w_y += perturb_y
            dy2 = w_y - v_y
            
        # Check slopes are well-defined: non-vertical and non-horizontal
        # VU slope: dy1 / dx1
        # VW slope: dy2 / dx2
        # UW slope: (u_y - w_y) / (u_x - w_x)
        if dx1 == 0 or dy1 == 0 or dx2 == 0 or dy2 == 0:
            continue
        if u_x == w_x or u_y == w_y:
            continue
            
        # Map back to A, B, C
        if test_vertex == "A":
            ax, ay = v_x, v_y
            bx, by = u_x, u_y
            cx, cy = w_x, w_y
            # We are testing angle A
            m1_num, m1_den = by - ay, bx - ax
            m2_num, m2_den = cy - ay, cx - ax
            line1_name, line2_name = "AB", "AC"
        elif test_vertex == "B":
            bx, by = v_x, v_y
            ax, ay = u_x, u_y
            cx, cy = w_x, w_y
            # We are testing angle B
            m1_num, m1_den = ay - by, ax - bx
            m2_num, m2_den = cy - by, cx - bx
            line1_name, line2_name = "AB", "BC"
        else: # C
            cx, cy = v_x, v_y
            ax, ay = u_x, u_y
            bx, by = w_x, w_y
            # We are testing angle C
            m1_num, m1_den = ay - cy, ax - cx
            m2_num, m2_den = by - cy, bx - cx
            line1_name, line2_name = "AC", "BC"
            
        # Double check slopes are not collinear
        if m1_num * m2_den == m2_num * m1_den:
            continue
            
        break
        
    m1 = Fraction(m1_num, m1_den)
    m2 = Fraction(m2_num, m2_den)
    slope_product = m1 * m2
    
    # Calculate answer
    answer_text = "是" if is_right_angle else "否"
    options = ["是", "否"]
    
    # Find label: A for "是", B for "否"
    correct_label = "A" if answer_text == "是" else "B"
    
    # Format formula and solution steps
    # We must format using $...$ for formulas to pass LaTeX constraints.
    question_text = f"在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( {ax},{ay} \\right)$、$B\\left( {bx},{by} \\right)$、$C\\left( {cx},{cy} \\right)$。試問 $\\triangle ABC$ 是否在頂點 ${test_vertex}$ 處為直角？"
    
    solution_steps = [
        f"欲驗證 $\\triangle ABC$ 在頂點 ${test_vertex}$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        f"計算與頂點 ${test_vertex}$ 相連的兩條邊的斜率：",
        f"邊段 ${line1_name}$ 的斜率 $m_{{{line1_name}}} = \\frac{{{m1_num}}}{{{m1_den}}} = {m1}$，",
        f"邊段 ${line2_name}$ 的斜率 $m_{{{line2_name}}} = \\frac{{{m2_num}}}{{{m2_den}}} = {m2}$。",
        f"計算兩斜率的乘積：$m_{{{line1_name}}} \\cdot m_{{{line2_name}}} = {m1} \\cdot \\left( {m2} \\right) = {slope_product}$。",
    ]
    if is_right_angle:
        solution_steps.append(f"因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 ${test_vertex}$ 處為直角。答案為「是」。")
    else:
        solution_steps.append(f"因為斜率乘積為 ${slope_product} \\ne -1$，故 $\\triangle ABC$ 在頂點 ${test_vertex}$ 處不為直角。答案為「否」。")
        
    answer_contract = {
        "choices_required": True,
        "choice_count": 2,
        "correct_choice_count": 1,
        "frontend_render_choices": True,
        "answer_type": "choice",
        "answer_shape": "choice_label",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
        "accepted_formats": [correct_label],
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
    }
    
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"A=({ax},{ay}):B=({bx},{by}):C=({cx},{cy}):test={test_vertex}:answer={correct_label}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["perpendicular_lines_right_angle_verification"],
        "prerequisite_subskills": [],
        "givens": [f"A({ax},{ay})", f"B({bx},{by})", f"C({cx},{cy})", f"test_vertex={test_vertex}"],
        "target": "right_angle_verification",
        "derivation": solution_steps,
    }
    
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": correct_label,
        "answer_type": "choice_label",
        "checker_type": "choice_label_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": correct_label,
        "explanation": "\n".join(solution_steps),
        "choices": options,
        "answer_contract": answer_contract,
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    pool = ["A", "B"]
    return {"correct": bool(check_choice_label(user_answer, correct_answer, pool))}
