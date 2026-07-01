from __future__ import annotations
import random
from typing import Any
from core.checkers.choice_label_checker import check_choice_label

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "axis_distance_coordinate_point_numerical_choice"
TEXTBOOK_EXAMPLE_ID = 4509
DEFAULT_COMPONENT_ID = "src_4509"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # Distance to x-axis (absolute y coordinate) and y-axis (absolute x coordinate)
    dist_x = rng.randint(2, 6) # e.g. 3
    dist_y = rng.randint(2, 6) # e.g. 4
    while dist_x == dist_y:
        dist_y = rng.randint(2, 6)
        
    # Possible points are (±dist_y, ±dist_x)
    correct_point = (rng.choice([-dist_y, dist_y]), rng.choice([-dist_x, dist_x]))
    
    correct_str = f"({correct_point[0]},{correct_point[1]})"
    
    # Distractors (e.g. wrong order or wrong absolute values)
    all_wrong_options = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            candidate = f"({sx*dist_x},{sy*dist_y})"
            if candidate != correct_str:
                all_wrong_options.append(candidate)
    
    # Select exactly 3 wrong options
    selected_wrongs = rng.sample(all_wrong_options, min(3, len(all_wrong_options)))
    all_options = {correct_str} | set(selected_wrongs)
    
    while len(all_options) < 4:
        cand = f"({rng.randint(-7, 7)},{rng.randint(-7, 7)})"
        if cand != correct_str:
            all_options.add(cand)
        
    options = sorted(list(all_options))
    answer_label = "ABCD"[options.index(correct_str)]
    
    question = f"設 A 點為坐標平面上一點，且 A 點到 $x$ 軸及 $y$ 軸之距離分別為 {dist_x} 和 {dist_y}，則下列何者可能為 A 點之坐標？"
    
    solution_steps = [
        f"點 A 到 $x$ 軸的距離為 {dist_x}，代表其 $y$ 坐標的絕對值為 {dist_x}，即 $y = \\pm {dist_x}$。",
        f"點 A 到 $y$ 軸的距離為 {dist_y}，代表其 $x$ 坐標的絕對值為 {dist_y}，即 $x = \\pm {dist_y}$。",
        f"因此 A 點的所有可能坐標為：$(\\pm {dist_y}, \\pm {dist_x})$。",
        f"觀察選項，只有 {correct_str} 符合此條件。"
    ]
    
    return {
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "problem_type_id": PROBLEM_TYPE_ID,
        "subskill_id": PROBLEM_TYPE_ID,
        "question_text": question,
        "question": question,
        "choices": options,
        "answer": answer_label,
        "correct_answer": answer_label,
        "answer_type": "choice",
        "checker_type": "choice_label_checker",
        "answer_contract": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker"
        },
        "explanation": "\n".join(solution_steps),
        "solution_steps": solution_steps,
        "difficulty": "easy",
        "diagnosis_tags": ["coordinate_plane", "axis_distance", "numerical_coordinates"],
        "metadata": {
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": f"s{rng.randint(1, 99)}",
            "parameter_signature": f"axis_distance:dist_x={dist_x}:dist_y={dist_y}",
            "question_pattern_id": f"p{rng.randint(1, 99)}",
            "diagnosis_tags": ["coordinate_plane", "axis_distance", "numerical_coordinates"],
            "prerequisite_subskills": [],
        },
    }

def check(user_answer: object, correct_answer: object, choices: list[str] | None = None) -> dict[str, Any]:
    pool = choices if choices is not None else ["A", "B", "C", "D"]
    return {"correct": bool(check_choice_label(user_answer, correct_answer, pool))}
