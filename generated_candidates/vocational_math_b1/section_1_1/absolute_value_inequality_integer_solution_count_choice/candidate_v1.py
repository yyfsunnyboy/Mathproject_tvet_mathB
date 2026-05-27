from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.domain.choices_unique_validator import validate_choices_unique
from core.domain.interval_domain_function import count_integer_solutions, make_interval
from core.domain.interval_formatter import format_interval

SKILL_ID = "vh_數學B1_AbsoluteValueInequality"


def _solve_abs_le_interval(a: int, b: int, c: int) -> tuple[Fraction, Fraction]:
    left = Fraction(-c - b, a)
    right = Fraction(c - b, a)
    return min(left, right), max(left, right)


def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    rng = random.Random(seed)
    a = rng.choice([1, 2, 3])
    b = rng.randint(-6, 6)
    c = rng.randint(2, 9)
    lo, hi = _solve_abs_le_interval(a, b, c)
    iv = make_interval(lo, hi, True, True)
    cnt = count_integer_solutions(iv)
    correct_count = int(cnt if cnt is not None else 0)

    option_values = {correct_count, max(0, correct_count - 1), correct_count + 1, correct_count + 2}
    while len(option_values) < 4:
        option_values.add(correct_count + rng.randint(3, 7))
    options = [str(x) for x in sorted(option_values)]
    rng.shuffle(options)
    if not validate_choices_unique(options):
        raise RuntimeError("choices must be unique")
    answer_label = "ABCD"[options.index(str(correct_count))]

    question = f"若 $\\left| {a}x {'+' if b >= 0 else '-'} {abs(b)} \\right| \\le {c}$，滿足的整數 $x$ 有幾個？"
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "question_text": question,
        "question": question,
        "choices": options,
        "answer": answer_label,
        "correct_answer": answer_label,
        "answer_type": "choice_label",
        "answer_contract": {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"},
        "explanation": f"先解得區間 {format_interval(iv)}，再計算整數點個數。",
        "difficulty": int(difficulty if difficulty is not None else level),
        "diagnosis_tags": ["absolute_value", "integer_count", "choice_label"],
        "source": "gencode_candidate_v1",
    }


def check(user_answer: object, correct_answer: object, choices: list[str] | None = None) -> dict[str, Any]:
    pool = choices if choices is not None else ["A", "B", "C", "D"]
    return {"correct": bool(check_choice_label(user_answer, correct_answer, pool))}
