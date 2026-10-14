"""Exact checker for answers that must be written as a (repeating) decimal expansion.

Accepted notation: finite decimals (``0.375``), parenthesised repetends
(``0.(3)``, ``0.4(09)``) and LaTeX overlines (``0.\\overline{3}``,
``0.4\\overline{09}``).  Both sides are converted to exact ``Fraction`` values;
no float and no raw string equality is involved.  A fraction such as ``1/3``
is a correct value in the wrong form and is rejected.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

_DASHES = {"\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2010": "-", "\u2011": "-"}
_DELIMITERS = re.compile(r"\$|\\\(|\\\)|\\\[|\\\]|\\left(?![A-Za-z])|\\right(?![A-Za-z])")
_OVERLINE_GROUP = re.compile(r"\\overline\s*\{\s*([0-9\s]*)\}")
_OVERLINE_BARE = re.compile(r"\\overline\s*([0-9])")
_EXPANSION = re.compile(r"^([+-]?)(\d*)(?:\.(\d*)(?:\((\d+)\))?)?$")


@dataclass(frozen=True)
class DecimalExpansion:
    sign: int
    whole: str
    nonrepeating: str
    cycle: str

    @property
    def value(self) -> Fraction:
        base = Fraction(int(self.whole or "0"))
        if self.nonrepeating:
            base += Fraction(int(self.nonrepeating), 10 ** len(self.nonrepeating))
        if self.cycle:
            base += Fraction(int(self.cycle), (10 ** len(self.cycle) - 1) * 10 ** len(self.nonrepeating))
        return self.sign * base


def _normalize_text(text: Any) -> str:
    s = unicodedata.normalize("NFKC", str(text if text is not None else ""))
    for src, dst in _DASHES.items():
        s = s.replace(src, dst)
    s = _DELIMITERS.sub("", s)
    s = _OVERLINE_GROUP.sub(lambda m: "(" + re.sub(r"\s+", "", m.group(1)) + ")", s)
    s = _OVERLINE_BARE.sub(r"(\1)", s)
    return re.sub(r"[\s{}]+", "", s)


def parse_decimal_expansion(text: Any) -> DecimalExpansion | None:
    """Parse decimal-expansion notation; returns None for fractions or anything else."""
    if isinstance(text, bool) or not isinstance(text, (str, int)):
        return None
    m = _EXPANSION.fullmatch(_normalize_text(text))
    if not m:
        return None
    sign, whole, nonrepeating, cycle = m.group(1), m.group(2), m.group(3), m.group(4)
    if not whole and not nonrepeating and not cycle:
        return None
    return DecimalExpansion(
        sign=-1 if sign == "-" else 1,
        whole=whole or "0",
        nonrepeating=nonrepeating or "",
        cycle=cycle or "",
    )


def _primitive_cycle(cycle: str) -> str:
    for size in range(1, len(cycle) + 1):
        if len(cycle) % size == 0 and cycle[:size] * (len(cycle) // size) == cycle:
            return cycle[:size]
    return cycle


def _finite_expansion(value: Fraction, digits: int) -> tuple[str, str]:
    scaled = abs(value) * 10 ** digits
    if scaled.denominator != 1:
        raise ValueError("value is not finite at the requested precision")
    text = str(scaled.numerator).rjust(digits + 1, "0")
    whole, fraction = (text[:-digits], text[-digits:]) if digits else (text, "")
    return str(int(whole)), fraction.rstrip("0")


def canonical_form(expansion: DecimalExpansion) -> DecimalExpansion:
    """Shortest notation for the same value: minimal pre-period and repetend, no (0)/(9)."""
    nonrepeating, cycle = expansion.nonrepeating, expansion.cycle
    if cycle:
        cycle = _primitive_cycle(cycle)
        while nonrepeating and nonrepeating[-1] == cycle[-1]:
            nonrepeating, cycle = nonrepeating[:-1], cycle[-1] + cycle[:-1]
    value = expansion.value
    if cycle == "9":
        whole, nonrepeating = _finite_expansion(value, len(nonrepeating))
        cycle = ""
    else:
        whole = str(int(expansion.whole or "0"))
        if cycle == "0":
            cycle = ""
        if not cycle:
            nonrepeating = nonrepeating.rstrip("0")
    sign = 1 if value == 0 else expansion.sign
    return DecimalExpansion(sign=sign, whole=whole, nonrepeating=nonrepeating, cycle=cycle)


def _as_written(expansion: DecimalExpansion) -> DecimalExpansion:
    """Written notation with only the harmless padding (trailing finite zeros, leading whole zeros) removed."""
    nonrepeating = expansion.nonrepeating if expansion.cycle else expansion.nonrepeating.rstrip("0")
    sign = 1 if expansion.value == 0 else expansion.sign
    return DecimalExpansion(sign=sign, whole=str(int(expansion.whole or "0")), nonrepeating=nonrepeating, cycle=expansion.cycle)


def format_decimal_expansion(expansion: DecimalExpansion) -> str:
    text = ("-" if expansion.sign < 0 else "") + expansion.whole
    if expansion.nonrepeating or expansion.cycle:
        text += "." + expansion.nonrepeating
    if expansion.cycle:
        text += f"({expansion.cycle})"
    return text


def _looks_like_fraction(text: Any) -> bool:
    from core.checkers.math_input_normalization import latex_to_plain, parse_exact_number

    plain = latex_to_plain(text)
    return "/" in plain and parse_exact_number(plain) is not None


def check_decimal_expansion_answer(
    student_answer: Any,
    expected_answer: Any,
    *,
    answer_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = answer_contract if isinstance(answer_contract, dict) else {}
    expected = parse_decimal_expansion(expected_answer)
    if expected is None:
        return {"correct": False, "reason": "expected_answer_unparseable", "system_error": True}
    student = parse_decimal_expansion(student_answer)
    if student is None:
        reason = "decimal_expansion_required" if _looks_like_fraction(student_answer) else "unparseable_decimal_expansion"
        return {"correct": False, "reason": reason}
    if student.value != expected.value:
        return {"correct": False, "reason": "value_mismatch"}
    if not contract.get("allow_noncanonical_repetend") and _as_written(student) != canonical_form(student):
        return {"correct": False, "reason": "noncanonical_repetend"}
    return {
        "correct": True,
        "reason": "correct",
        "normalized_student_answer": format_decimal_expansion(canonical_form(student)),
        "normalized_correct_answer": format_decimal_expansion(canonical_form(expected)),
    }
