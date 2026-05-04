"""Runtime wrapper for B4 combination skill."""

from __future__ import annotations

from core.vocational_math_b4.services.question_router import generate_for_skill


def generate(level=1, **kwargs):
    return generate_for_skill(
        skill_id="vh_數學B4_Combination",
        level=level,
        seed=kwargs.get("seed"),
        seen_parameter_tuples=kwargs.get("seen_parameter_tuples"),
        multiple_choice=True,
        problem_type_id=kwargs.get("problem_type_id"),
    )


def check(user_answer, correct_answer):
    user_text = str(user_answer).strip()
    correct_text = str(correct_answer).strip()

    try:
        is_correct = int(user_text) == int(correct_text)
    except ValueError:
        is_correct = user_text == correct_text

    if is_correct:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}
