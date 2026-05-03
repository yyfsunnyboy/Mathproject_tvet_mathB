"""Legacy runtime wrapper for B4 combination applications skill."""

from __future__ import annotations

from core.vocational_math_b4.services.question_router import generate_for_skill


def generate(level=1, **kwargs):
    """Generate a question payload through the B4 question router."""
    payload = generate_for_skill(
        skill_id="vh_數學B4_CombinationApplications",
        level=level,
        seed=kwargs.get("seed"),
        seen_parameter_tuples=kwargs.get("seen_parameter_tuples"),
        multiple_choice=True,
        problem_type_id=kwargs.get("problem_type_id"),
    )
    required_keys = [
        "question_text",
        "answer",
        "correct_answer",
        "choices",
        "explanation",
        "skill_id",
        "subskill_id",
        "problem_type_id",
        "generator_key",
        "difficulty",
        "diagnosis_tags",
        "remediation_candidates",
        "source_style_refs",
        "parameters",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"Wrapper payload missing required keys: {', '.join(missing)}")
    return payload


def check(user_answer, correct_answer):
    """Compare user answer and correct answer with integer-aware normalization."""
    user_text = str(user_answer).strip()
    correct_text = str(correct_answer).strip()

    try:
        is_correct = int(user_text) == int(correct_text)
    except ValueError:
        is_correct = user_text == correct_text

    if is_correct:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}
