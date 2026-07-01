from __future__ import annotations

import random
import re
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.domain.choices_unique_validator import validate_choices_unique
from core.domain.coordinate_geometry.cartesian_coordinate_domain import build_cartesian_coordinate_matrix

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PROBLEM_TYPE_ID = "cartesian_coordinate_quadrant_symbol_reasoning"
SUBSKILL_ID = "cartesian_coordinate_quadrant_symbol_reasoning"

def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    rng = random.Random(seed)
    
    templates = [
        ("a > 0, b > 0, a < b", "a - b", "a**2 * b"),
        ("a < b < 0", "a * b", "a + b"),
        ("a > 0, b < 0", "a - b", "b**2"),
        ("a < 0", "a**2", "-a"),
        ("a > 0, b > 0, a < b", "a * b", "b - a"),
        ("a < b < 0", "b - a", "a * b"),
        ("a > 0, b < 0", "a * b", "a - b"),
        ("a > 0, b > 0, b < a", "b - a", "a * b"),
        ("a < 0, b < 0", "-a", "-b"),
        ("a > 0, b < 0", "-a", "b"),
    ]
    cond_tmpl, x_tmpl, y_tmpl = rng.choice(templates)
    
    # Choose variable names
    vars_pool = [
        ('a', 'b'),
        ('u', 'v'),
        ('m', 'n'),
        ('p', 'q'),
        ('c', 'd'),
        ('s', 't'),
    ]
    v1, v2 = rng.choice(vars_pool)
    
    def repl(s: str) -> str:
        s = re.sub(r'\ba\b', v1, s)
        s = re.sub(r'\bb\b', v2, s)
        return s
        
    cond = repl(cond_tmpl)
    x_expr = repl(x_tmpl)
    y_expr = repl(y_tmpl)
    
    matrix = build_cartesian_coordinate_matrix(
        seed=seed,
        domain_operation=PROBLEM_TYPE_ID,
        constraints={
            "variable_conditions": cond,
            "x_expression": x_expr,
            "y_expression": y_expr,
        }
    )
    
    quadrant = matrix["answer"]["canonical_form"]
    distractors = matrix["distractors"]
    options = [quadrant] + distractors
    options.sort()
    
    answer_label = "ABCD"[options.index(quadrant)]
    
    x_disp = x_expr.replace("**", "^").replace(" * ", "").replace("*", "")
    y_disp = y_expr.replace("**", "^").replace(" * ", "").replace("*", "")
    cond_disp = cond.replace("a**2", "a^2").replace("b**2", "b^2")
    cond_disp = cond_disp.replace(f"{v1}**2", f"{v1}^2").replace(f"{v2}**2", f"{v2}^2")
    
    # Keep textbook format
    question = f"設 ${v1}$、${v2}$ 為實數，且滿足條件：{cond_disp}。則平面上的點 $Q({x_disp}, {y_disp})$ 在第幾象限？"
    if cond_tmpl == "a < 0":
        question = f"設 ${v1}$ 為實數，且滿足條件：{cond_disp}。則平面上的點 $Q({x_disp}, {y_disp})$ 在第幾象限？"
        
    solution_steps = matrix["explanation_steps"]
    
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "subskill_id": SUBSKILL_ID,
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
        "difficulty": int(difficulty) if isinstance(difficulty, int) or (isinstance(difficulty, str) and difficulty.isdigit()) else int(level),
        "diagnosis_tags": ["coordinate_plane", "quadrant", "symbolic_reasoning"],
        "source": "gencode_candidate_v1",
        "metadata": {
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": f"s{rng.randint(1, 99)}",
            "parameter_signature": f"quadrant_reasoning:cond={cond}:x={x_expr}:y={y_expr}",
            "question_pattern_id": f"p{rng.randint(1, 99)}",
            "diagnosis_tags": ["coordinate_plane", "quadrant", "symbolic_reasoning"],
            "prerequisite_subskills": [],
        },
    }

def check(user_answer: object, correct_answer: object, choices: list[str] | None = None) -> dict[str, Any]:
    pool = choices if choices is not None else ["A", "B", "C", "D"]
    return {"correct": bool(check_choice_label(user_answer, correct_answer, pool))}
