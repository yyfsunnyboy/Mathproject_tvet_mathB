"""Thin runtime wrapper for vocational B1 absolute value skill."""

from __future__ import annotations

import re

from core.checkers.choice_label_checker import check_choice_label, choice_value_to_label
from core.checkers.solution_set_checker import check_solution_set_answer, parse_solution_set_answer
from core.vocational_math_b1.generated_candidate_loader import generate_from_verified_candidate
from core.domain.choices_unique_validator import repair_choice_payload

SKILL_ID = "vh_數學B1_AbsoluteValue"


def generate(level=1, **kwargs):
    seed = kwargs.get("seed")
    difficulty = kwargs.get("difficulty", "easy")
    payload = generate_from_verified_candidate(SKILL_ID, seed=seed, difficulty=difficulty)
    if str(payload.get("answer_type", "")).strip() in {"choice", "choice_label"}:
        choices = list(payload.get("choices") or [])
        label = choice_value_to_label(payload.get("answer", ""), choices)
        if label is not None:
            payload["answer"] = label
            payload["correct_answer"] = label
    if str(payload.get("answer_type", "")).strip() in {"choice", "choice_label"}:
        payload = repair_choice_payload(payload, seed=seed)
    return payload


def generate_question(*args, **kwargs):
    return generate(**kwargs)


def get_question(*args, **kwargs):
    return generate(**kwargs)


def _is_absolute_value_equation_solution_format(text: object) -> bool:
    s = str(text or "")
    if not s.strip():
        return False
    parsed = parse_solution_set_answer(s)
    if len(parsed) != 2:
        return False
    vals = sorted(parsed)
    if vals[0] + vals[1] != 0:
        return False
    return bool(re.search(r"[xX]|±|\+\-|或|\{|\}|,|，", s))


def check(user_answer, correct_answer, current_question=None):
    user_text = str(user_answer).strip()
    correct_text = str(correct_answer).strip()
    if correct_text in {"A", "B", "C", "D"}:
        q = current_question if isinstance(current_question, dict) else {}
        choices = list(q.get("choices") or [])
        if not choices:
            choices = ["A", "B", "C", "D"]
        if check_choice_label(user_text, correct_text, choices):
            return {"correct": True, "result": "答對了"}
    if _is_absolute_value_equation_solution_format(correct_text):
        if check_solution_set_answer(user_text, correct_text):
            return {"correct": True, "result": "答對了"}
    if user_text == correct_text:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}
