"""Shared checker: an unordered set of linear relations in x and y.

Each item is an equation (``=``) or an inequality (``<``, ``<=``, ``>``, ``>=`` and the ``≤ ≥``
signs).  An item is reduced to ``a x + b y + c  (op)  0`` with coprime integer coefficients and a
positive leading coefficient (the operator flips with a negative scale), so ``2x+y-6≤0`` equals
``-2x-y+6≥0`` and ``4x+2y=12`` equals ``2x+y-6=0``.  The answer is correct when both sides hold
exactly the same set of relations, in any order.  Unreadable input is reported as invalid input,
never as a wrong answer.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from core.checkers.linear_equation_equivalent_checker import (
    _BAD_PATTERN,
    _normalize_text,
    _parse_linear_polynomial,
    _to_integer_triple,
)

_FLIP = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "=": "="}
_OPERATOR_RE = re.compile(r"(<=|>=|=|<|>)")


def _clean(text: str) -> str:
    out = str(text or "")
    # LaTeX wrappers first: ``\left`` / ``\right`` contain ``\le`` / ``\ri`` prefixes of the operator macros.
    for src, dst in (
        ("\\left\\{", ""), ("\\right.", ""), ("\\left", ""), ("\\right", ""), ("\\{", ""), ("\\}", ""),
        ("\\begin{array}{l}", ","), ("\\end{array}", ","), ("\\\\", ","),
        ("\\leqslant", "<="), ("\\geqslant", ">="), ("\\leq", "<="), ("\\geq", ">="), ("\\le", "<="), ("\\ge", ">="),
        ("\\lt", "<"), ("\\gt", ">"), ("≤", "<="), ("≥", ">="), ("＜", "<"), ("＞", ">"), ("＝", "="), ("$", ""),
        ("，", ","), ("；", ","), (";", ","), ("、", ","), ("且", ","), ("或", ","), ("\n", ","),
    ):
        out = out.replace(src, dst)
    out = re.sub(r"\band\b|\bor\b", ",", out, flags=re.IGNORECASE)
    return out.replace("{", "").replace("}", "")


def parse_relation(text: str) -> tuple[int, int, int, str] | None:
    normalized = _normalize_text(text)
    if not normalized or _BAD_PATTERN.search(normalized):
        return None
    parts = _OPERATOR_RE.split(normalized)
    if len(parts) != 3:
        return None
    left, op, right = parts
    left_poly, right_poly = _parse_linear_polynomial(left), _parse_linear_polynomial(right)
    if left_poly is None or right_poly is None:
        return None
    triple = tuple(a - b for a, b in zip(left_poly, right_poly))
    if triple[0] == 0 and triple[1] == 0:
        return None
    integer = _to_integer_triple(triple)  # type: ignore[arg-type]
    if integer is None:
        return None
    a, b, c = integer
    lead = a if a != 0 else b
    if lead < 0:
        a, b, c, op = -a, -b, -c, _FLIP[op]
    return a, b, c, op


def parse_relation_set(value: Any) -> frozenset[tuple[int, int, int, str]] | None:
    if isinstance(value, (list, tuple, set, frozenset)):
        items = [str(v) for v in value]
    else:
        items = _clean(str(value or "")).split(",")
    relations: set[tuple[int, int, int, str]] = set()
    seen = 0
    for item in items:
        item = item.strip()
        if not item:
            continue
        seen += 1
        parsed = parse_relation(_clean(item).replace(",", ""))
        if parsed is None:
            return None
        relations.add(parsed)
    return frozenset(relations) if seen else None


def check_linear_relation_set_answer(user_answer: Any, correct_answer: Any, *, answer_contract: dict | None = None) -> dict[str, Any]:
    expected = parse_relation_set(correct_answer)
    if expected is None:
        return {"correct": False, "system_error": True, "reason": "expected_relation_set_unreadable"}
    student = parse_relation_set(user_answer)
    if student is None:
        return {"correct": False, "invalid_input": True, "reason": "student_relation_set_unreadable"}
    return {"correct": student == expected}
