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
PROBLEM_TYPE_ID = "arc_length_and_area_of_sector"
TEXTBOOK_EXAMPLE_ID = 11619
DEFAULT_COMPONENT_ID = "src_11619"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _format_pi_fraction_latex(f: Fraction) -> str:
    p, q = f.numerator, f.denominator
    if q == 1:
        if p == 1:
            return r"\pi"
        return rf"{p}\pi"
    else:
        if p == 1:
            return rf"\frac{{\pi}}{{{q}}}"
        return rf"\frac{{{p}\pi}}{{{q}}}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    candidates = [
        (12, 135), (8, 45), (16, 225), (6, 150), (10, 108),
        (15, 120), (14, 90), (20, 72), (18, 100), (9, 160),
        (12, 75), (8, 135), (10, 144), (16, 45), (6, 210)
    ]
    r, deg = rng.choice(candidates)

    theta_frac = Fraction(deg, 180)
    s_frac = r * theta_frac
    a_frac = Fraction(1, 2) * (r * r) * theta_frac

    s_latex = _format_pi_fraction_latex(s_frac)
    a_latex = _format_pi_fraction_latex(a_frac)

    question_text = (
        f"設一扇形半徑為{r}公分，所對應的圓心角為{deg}°，試求：\n"
        f"(1)此扇形弧長S。 (2)此扇形面積A。"
    )

    canonical_answer = f"(1) {s_latex}; (2) {a_latex}"

    sol_text = (
        f"【解析】\n"
        f"圓心角 \\(\\theta = {deg}^\\circ = \\frac{{{deg}\\pi}}{{180}} = {_format_pi_fraction_latex(theta_frac)}\\)\n"
        f"(1) 弧長 \\(S = r\\theta = {r} \\times {_format_pi_fraction_latex(theta_frac)} = {s_latex}\\) (公分)\n"
        f"(2) 面積 \\(A = \\frac{{1}}{{2}}r^2\\theta = \\frac{{1}}{{2}} \\times {r}^2 \\times {_format_pi_fraction_latex(theta_frac)} = {a_latex}\\) (平方公分)"
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
            "givens": {"radius": r, "degree": deg},
            "target": f"{s_latex}, {a_latex}",
            "s_frac": str(s_frac),
            "a_frac": str(a_frac),
        },
    }


def _clean_expr(expr_str: str) -> str:
    s = expr_str.strip()
    s = s.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    s = s.replace(r"\pi", "pi").replace("π", "pi")
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    return s
