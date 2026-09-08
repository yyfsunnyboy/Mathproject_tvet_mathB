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
TEXTBOOK_EXAMPLE_ID = 11614
DEFAULT_COMPONENT_ID = "src_11614"

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

    # Subproblem 1: large positive degree
    k1 = rng.choice([2, 3, 4])
    r1 = rng.choice([30, 45, 60, 120, 150, 210, 240, 300, 330])
    deg1 = 360 * k1 + r1
    pos1 = r1
    neg1 = r1 - 360

    # Subproblem 2: negative degree
    k2 = rng.choice([2, 3, 4])
    r2 = rng.choice([50, 70, 80, 100, 110, 140, 200, 250, 310])
    deg2 = -360 * k2 - (360 - r2)
    pos2 = r2
    neg2 = r2 - 360

    # Subproblem 3: radian angle > 2pi
    q3 = rng.choice([3, 4, 5, 6])
    rem_p = rng.choice([p for p in range(1, 2 * q3) if math.gcd(p, q3) == 1])
    k3 = rng.choice([2, 4, 6])
    p3 = k3 * q3 + rem_p
    rad_f = Fraction(p3, q3)
    rad_latex = _format_radian_latex(rad_f)
    pos_rad_f = Fraction(rem_p, q3)
    neg_rad_f = pos_rad_f - 2
    pos_rad_latex = _format_radian_latex(pos_rad_f)
    neg_rad_latex = _format_radian_latex(neg_rad_f)

    question_text = (
        f"試求下列各角的最小正同界角與最大負同界角：\n"
        f"(1)\\({deg1}^\\circ\\) (2)\\({deg2}^\\circ\\) (3)\\({rad_latex}\\)"
    )

    canonical_answer = (
        f"(1) {pos1}^\\circ, {neg1}^\\circ; "
        f"(2) {pos2}^\\circ, {neg2}^\\circ; "
        f"(3) {pos_rad_latex}, {neg_rad_latex}"
    )

    sol_text = (
        f"【解析】\n"
        f"(1) \\({deg1}^\\circ = 360^\\circ \\times {k1} + {pos1}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos1}^\\circ\\)，最大負同界角為 \\({pos1}^\\circ - 360^\\circ = {neg1}^\\circ\\)。\n"
        f"(2) \\({deg2}^\\circ = 360^\\circ \\times (-{k2 + 1}) + {pos2}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos2}^\\circ\\)，最大負同界角為 \\({pos2}^\\circ - 360^\\circ = {neg2}^\\circ\\)。\n"
        f"(3) \\({rad_latex} = 2\\pi \\times {k3 // 2} + {pos_rad_latex}\\)，\n"
        f"    最小正同界角為 \\({pos_rad_latex}\\)，最大負同界角為 \\({pos_rad_latex} - 2\\pi = {neg_rad_latex}\\)。"
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
                "deg1": deg1, "pos1": pos1, "neg1": neg1,
                "deg2": deg2, "pos2": pos2, "neg2": neg2,
                "rad3": str(rad_f), "pos3": str(pos_rad_f), "neg3": str(neg_rad_f),
            },
            "target": canonical_answer,
        },
    }


def _clean_token(s: str) -> str:
    res = s.strip()
    res = res.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    res = res.replace(r"\pi", "pi").replace("π", "pi")
    res = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", res)
    return res
