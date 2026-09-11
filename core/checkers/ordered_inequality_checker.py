"""Shared structural checker for ordered comparison chains."""
from __future__ import annotations
from typing import Any


def _parse(value: Any) -> tuple[list[str], list[str]] | None:
    text = str(value or "").replace("\\lt", "<").replace("\\gt", ">").replace(" ", "")
    for token in ("≤", "≥", "<=", ">="):
        if token in text: return None
    operator = "<" if "<" in text else ">" if ">" in text else ""
    if not operator or ("<" in text and ">" in text): return None
    terms = [term for term in text.split(operator) if term]
    return (terms, [operator] * (len(terms)-1)) if len(terms) >= 2 else None


def check_ordered_inequality_answer(student_answer: Any, correct_answer: Any) -> bool:
    student, expected = _parse(student_answer), _parse(correct_answer)
    if student is None or expected is None: return False
    if student == expected: return True
    terms, operators = expected
    inverse = ">" if operators and operators[0] == "<" else "<"
    return student == (list(reversed(terms)), [inverse] * len(operators))
