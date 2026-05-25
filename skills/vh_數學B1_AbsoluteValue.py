"""Thin runtime wrapper for vocational B1 absolute value skill."""

from __future__ import annotations

from core.vocational_math_b1.generated_candidate_loader import generate_from_verified_candidate

SKILL_ID = "vh_數學B1_AbsoluteValue"


def generate(level=1, **kwargs):
    seed = kwargs.get("seed")
    difficulty = kwargs.get("difficulty", "easy")
    return generate_from_verified_candidate(SKILL_ID, seed=seed, difficulty=difficulty)


def generate_question(*args, **kwargs):
    return generate(**kwargs)


def get_question(*args, **kwargs):
    return generate(**kwargs)


def check(user_answer, correct_answer):
    user_text = str(user_answer).strip()
    correct_text = str(correct_answer).strip()
    if user_text == correct_text:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}
