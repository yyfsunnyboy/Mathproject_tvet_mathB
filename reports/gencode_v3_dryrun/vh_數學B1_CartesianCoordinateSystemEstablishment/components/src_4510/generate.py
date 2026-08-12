from __future__ import annotations
import random
from typing import Any
from core.checkers.choice_label_checker import check_choice_label

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice"
PROBLEM_TYPE_ID = "quadrant_statement_reasoning_choice"
TEXTBOOK_EXAMPLE_ID = 4510
DEFAULT_COMPONENT_ID = "src_4510"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)
    
    vars_pool = [
        ('a', 'b'),
        ('u', 'v'),
        ('m', 'n'),
        ('p', 'q'),
    ]
    v1, v2 = rng.choice(vars_pool)
    
    options = [
        f"A點$A(-{v1}, {v2})$在第一象限",
        f"B點$B(|{v1}{v2}|, -{v1}^2{v2})$在第二象限",
        f"C點$C({v1}^2/{v2}, -{v2})$在第三象限",
        f"D點$D(-{v1}^2, {v2}^2)$在第二象限",
    ]
    correct_str = options[3]
    options.sort()
    
    answer_label = "ABCD"[options.index(correct_str)]
    
    question = f"已知點 $P({v1}-{v2}, {v1}{v2})$ 在坐標平面的第四象限，則下列敘述何者正確？"
    
    solution_steps = [
        f"點 $P({v1}-{v2}, {v1}{v2})$ 在第四象限，代表其 $x$ 坐標為正，$y$ 坐標為負，即：${v1}-{v2} > 0$ 且 ${v1}{v2} < 0$。",
        f"由 ${v1}{v2} < 0$ 可知 ${v1}$、${v2}$ 異號；由 ${v1}-{v2} > 0$ 即 ${v1} > {v2}$，可知 ${v1} > 0$ 且 ${v2} < 0$。",
        f"分析選項D：點 $D(-{v1}^2, {v2}^2)$，其 $x$ 坐標 $-{v1}^2 < 0$，$y$ 坐標 ${v2}^2 > 0$，故在第二象限，此敘述正確。"
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
        "diagnosis_tags": ["coordinate_plane", "quadrant", "symbolic_reasoning"],
        "metadata": {
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": f"s{rng.randint(1, 99)}",
            "parameter_signature": f"quadrant_reasoning_statement:v1={v1}:v2={v2}",
            "question_pattern_id": f"p{rng.randint(1, 99)}",
            "diagnosis_tags": ["coordinate_plane", "quadrant", "symbolic_reasoning"],
            "prerequisite_subskills": [],
        },
    }

def check(user_answer: object, correct_answer: object, choices: list[str] | None = None) -> dict[str, Any]:
    pool = choices if choices is not None else ["A", "B", "C", "D"]
    return {"correct": bool(check_choice_label(user_answer, correct_answer, pool))}
