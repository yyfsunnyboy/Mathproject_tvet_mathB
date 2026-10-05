"""Predicate checker: the answer is any rational strictly between two exact bounds.

The bounds come from the answer contract (``lower`` / ``upper``); a canonical
example answer is never used for equality.  Any exact rational notation is
accepted (fraction, LaTeX fraction, integer, finite or repeating decimal) unless
the contract sets ``required_form="fraction"``.  Comparison is exact.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any


def parse_rational_answer(text: Any, *, required_form: str = "") -> Fraction | None:
    from core.checkers.math_input_normalization import parse_exact_number
    from core.checkers.repeating_decimal_checker import parse_decimal_expansion
    from core.checkers.simplest_fraction_checker import parse_fraction_form

    if isinstance(text, bool) or text is None:
        return None
    if required_form == "fraction":
        form = parse_fraction_form(text)
        return form.value if form is not None else None
    exact = parse_exact_number(text)
    if exact is not None:
        return exact
    expansion = parse_decimal_expansion(text)
    return expansion.value if expansion is not None else None


def check_rational_between_bounds_answer(
    student_answer: Any,
    *,
    answer_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.checkers.math_input_normalization import parse_exact_number

    contract = answer_contract if isinstance(answer_contract, dict) else {}
    lower, upper = parse_exact_number(contract.get("lower")), parse_exact_number(contract.get("upper"))
    relation = str(contract.get("relation") or "strict_between")
    if lower is None or upper is None or not lower < upper or relation != "strict_between":
        return {"correct": False, "reason": "bounds_contract_invalid", "system_error": True}
    value = parse_rational_answer(student_answer, required_form=str(contract.get("required_form") or ""))
    if value is None:
        return {"correct": False, "reason": "unparseable_rational"}
    if not lower < value < upper:
        return {"correct": False, "reason": "outside_bounds"}
    return {"correct": True, "reason": "correct", "normalized_student_answer": f"{value.numerator}/{value.denominator}"}
