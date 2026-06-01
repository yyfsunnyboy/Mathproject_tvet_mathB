import random
from typing import Any

PROBLEM_TYPE_ID = "integer_numeric_evaluate_function_notation"
SKILL_ID = "vh_數學B1_LinearFunction"
SUBSKILL_ID = "integer_numeric_evaluate_function_notation"

def generate(seed: int | None = None, difficulty: str | int | None = "easy", **kwargs) -> dict[str, Any]:
    rng = random.Random(seed)
    
    # Generate f(x) = ax + b
    # Ensure non-zero slope and integer coordinates/results
    a = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    b = rng.randint(-10, 10)
    c = rng.randint(-5, 5)
    
    answer = a * c + b
    
    # Format linear expression nicely
    sign = "+" if b >= 0 else "-"
    b_abs = abs(b)
    if b == 0:
        expr = f"{a}x"
    else:
        expr = f"{a}x {sign} {b_abs}"
        
    question_text = f"設線型函數 $f(x) = {expr}$，求 $f({c})$ 的值。"
    solution_steps = [
        f"將 $x = {c}$ 代入線型函數 $f(x) = {expr}$ 中：",
        f"$f({c}) = {a} \\times ({c}) {sign} {b_abs}$",
        f"$f({c}) = {a * c} {sign} {b_abs} = {answer}$。",
        f"因此，答案為 {answer}。"
    ]
    
    answer_contract = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
        "answer_type": "integer",
        "answer_shape": "scalar",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [str(answer)],
        "checker_key": "integer_checker",
        "equivalence_type": "numeric_exact",
    }
    
    metadata = {
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{rng.randint(1, 9)}",
        "parameter_signature": f"integer_numeric_evaluate_function_notation:a={a}:b={b}:c={c}",
        "question_pattern_id": f"p{rng.randint(1, 4)}",
        "diagnosis_tags": ["function_evaluation", "linear_function"],
        "prerequisite_subskills": [],
    }
    
    return {
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": str(answer),
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": str(answer),
        "explanation": "\n".join(solution_steps),
        "choices": [],
        "answer_contract": answer_contract,
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    ua = str(user_answer).strip()
    ca = str(correct_answer).strip()
    try:
        ok = float(ua) == float(ca)
    except Exception:
        ok = ua == ca
    return {"correct": ok}
