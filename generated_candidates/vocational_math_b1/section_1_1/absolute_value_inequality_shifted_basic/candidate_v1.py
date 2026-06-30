from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.interval_checker import check_interval_answer
from core.domain.choices_unique_validator import build_choice_payload
from core.domain.interval_domain_function import count_integer_solutions, make_interval
from core.domain.interval_formatter import format_interval

SKILL_ID = "vh_數學B1_AbsoluteValueInequality"


def _to_interval_answer(lo: Fraction, hi: Fraction, lo_closed: bool, hi_closed: bool) -> str:
    return format_interval(make_interval(lo, hi, lo_closed, hi_closed))


def _solve_abs_linear(a: int, b: int, op: str, c: int) -> str:
    if c < 0:
        if op in {"<", "<="}:
            return "(1,0)"
        return "(-∞,∞)"
    left = Fraction(-c - b, a)
    right = Fraction(c - b, a)
    lo = min(left, right)
    hi = max(left, right)
    if op == "<":
        return _to_interval_answer(lo, hi, False, False)
    if op == "<=":
        return _to_interval_answer(lo, hi, True, True)
    if op == ">":
        return f"(-∞,{lo}) ∪ ({hi},∞)"
    return f"(-∞,{lo}] ∪ [{hi},∞)"

def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    rng = random.Random(seed)
    h = rng.randint(-8, 8)
    if h == 0:
        h = 3
    a = rng.randint(2, 8)
    op = rng.choice(["<", "<=", ">", ">="])
    sign = "-" if h >= 0 else "+"
    question = f"解不等式：$\\left| x {sign} {abs(h)} \\right| {op} {a}$。"
    answer = _solve_abs_linear(1, -h, op, a)
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": "absolute_value_inequality_shifted_basic",
        "subskill_id": "absolute_value_inequality_shifted_basic",
        "question_text": question,
        "question": question,
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "interval_set",
        "checker_type": "interval_checker",
        "answer_contract": {"answer_type": "interval_set", "equivalence_type": "interval_set", "checker_key": "interval_checker"},
        "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
        "solution_steps": ["先視為 |x-h| 型，再轉回 x 的區間。"],
        "difficulty": int(difficulty) if isinstance(difficulty, int) or (isinstance(difficulty, str) and difficulty.isdigit()) else int(level),
        "diagnosis_tags": ["absolute_value", "shifted", "interval_set"],
        "source": "gencode_candidate_v1",
        "metadata": {
            "scenario_family": "absolute_value_inequality_shifted_basic",
            "scenario_id": "s1",
            "parameter_signature": f"shifted:h={h}:a={a}:op={op}",
            "question_pattern_id": "p1",
            "diagnosis_tags": ["absolute_value", "shifted", "interval_set"],
            "prerequisite_subskills": ["absolute_value_numeric_evaluation"],
        },
    }


def check(user_answer: object, correct_answer: object) -> dict[str, Any]:
    return {"correct": check_interval_answer(user_answer, correct_answer)}
