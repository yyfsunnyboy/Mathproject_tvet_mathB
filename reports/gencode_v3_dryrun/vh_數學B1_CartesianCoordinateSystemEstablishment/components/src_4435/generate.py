from __future__ import annotations
import random
from typing import Any
from core.checkers.choice_label_checker import check_choice_label
from core.domain.coordinate_geometry.cartesian_coordinate_domain import build_cartesian_coordinate_matrix

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "cartesian_coordinate_quadrant_symbol_reasoning"
TEXTBOOK_EXAMPLE_ID = 4435
DEFAULT_COMPONENT_ID = "src_4435"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)
    
    vars_pool = [
        ('a', 'b'),
        ('u', 'v'),
        ('m', 'n'),
        ('p', 'q'),
        ('c', 'd'),
        ('s', 't'),
    ]
    v1, v2 = rng.choice(vars_pool)
    
    cond = f"{v1} < {v2} < 0"
    x_expr = f"{v1} * {v2}"
    y_expr = f"{v1} + {v2}"
    
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
    
    x_disp = f"{v1}{v2}"
    y_disp = f"{v1} + {v2}"
    
    question = f"設 ${v1}$、${v2}$ 為實數，且 ${v1} < {v2} < 0$，則點 $Q({x_disp}, {y_disp})$ 在第幾象限？"
    solution_steps = matrix["explanation_steps"]
    
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
        "diagnosis_tags": ["coordinate_plane", "quadrant", "symbolic_reasoning"],
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
