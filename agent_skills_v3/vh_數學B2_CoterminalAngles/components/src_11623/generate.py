from __future__ import annotations

import math
import random
import re
from fractions import Fraction
from typing import Any

from sympy import pi, simplify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11623
DEFAULT_COMPONENT_ID = "src_11623"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _format_radian_latex(f: Fraction) -> str:
    p, q = f.numerator, f.denominator
    sign = "-" if p < 0 else ""
    abs_p = abs(p)
    if q == 1:
        if abs_p == 1:
            return rf"{sign}\pi"
        return rf"{sign}{abs_p}\pi"
    else:
        if abs_p == 1:
            return rf"{sign}\frac{{\pi}}{{{q}}}"
        return rf"{sign}\frac{{{abs_p}\pi}}{{{q}}}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # Subproblem 1: positive radian > 2pi
    q1 = rng.choice([3, 4, 6])
    rem_p1 = rng.choice([p for p in range(1, 2 * q1) if math.gcd(p, q1) == 1])
    k1 = rng.choice([2, 4, 6])
    p1 = k1 * q1 + rem_p1
    rad_f1 = Fraction(p1, q1)
    pos1_f = Fraction(rem_p1, q1)
    neg1_f = pos1_f - 2

    rad1_latex = _format_radian_latex(rad_f1)
    pos1_latex = _format_radian_latex(pos1_f)
    neg1_latex = _format_radian_latex(neg1_f)

    # Subproblem 2: negative radian < -2pi
    q2 = rng.choice([3, 4, 6])
    rem_p2 = rng.choice([p for p in range(1, 2 * q2) if math.gcd(p, q2) == 1])
    k2 = rng.choice([2, 4, 6])
    p2 = -k2 * q2 - (2 * q2 - rem_p2)
    rad_f2 = Fraction(p2, q2)
    pos2_f = Fraction(rem_p2, q2)
    neg2_f = pos2_f - 2

    rad2_latex = _format_radian_latex(rad_f2)
    pos2_latex = _format_radian_latex(pos2_f)
    neg2_latex = _format_radian_latex(neg2_f)

    question_text = (
        f"試求下列各角的最小正同界角與最大負同界角：\n"
        f"(1)\\({rad1_latex}\\) (2)\\({rad2_latex}\\)"
    )

    canonical_answer = (
        f"(1) {pos1_latex}, {neg1_latex}; "
        f"(2) {pos2_latex}, {neg2_latex}"
    )

    sol_text = (
        f"【解析】\n"
        f"(1) \\({rad1_latex} = 2\\pi \\times {k1 // 2} + {pos1_latex}\\)，\n"
        f"    最小正同界角為 \\({pos1_latex}\\)，最大負同界角為 \\({pos1_latex} - 2\\pi = {neg1_latex}\\)。\n"
        f"(2) \\({rad2_latex} = 2\\pi \\times (-{(abs(p2) // (2*q2)) + 1}) + {pos2_latex}\\)，\n"
        f"    最小正同界角為 \\({pos2_latex}\\)，最大負同界角為 \\({pos2_latex} - 2\\pi = {neg2_latex}\\)。"
    )

    return {
        "question_text": question_text,
        "answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "math_core": {
            "givens": {
                "rad1": str(rad_f1), "pos1": str(pos1_f), "neg1": str(neg1_f),
                "rad2": str(rad_f2), "pos2": str(pos2_f), "neg2": str(neg2_f),
            },
            "target": canonical_answer,
        },
    }


def _clean_rad(s: str) -> str:
    res = s.strip()
    res = res.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    res = res.replace(r"\pi", "pi").replace("π", "pi")
    res = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", res)
    return res
