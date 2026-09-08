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
TEXTBOOK_EXAMPLE_ID = 11609
DEFAULT_COMPONENT_ID = "src_11609"

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
        (9, 120), (6, 60), (12, 150), (15, 72), (10, 144),
        (8, 135), (12, 210), (18, 40), (6, 120), (9, 40),
        (12, 45), (10, 36), (15, 120), (8, 90), (14, 90)
    ]
    r, deg = rng.choice(candidates)

    theta_frac = Fraction(deg, 180)
    s_frac = r * theta_frac
    a_frac = Fraction(1, 2) * (r * r) * theta_frac

    theta_latex = _format_pi_fraction_latex(theta_frac)
    s_latex = _format_pi_fraction_latex(s_frac)
    a_latex = _format_pi_fraction_latex(a_frac)

    question_text = (
        f"設一扇形半徑為{r}公分，所對應的圓心角為{deg}°，試求：\n"
        f"(1)將圓心角化為弧度。 (2)此扇形弧長S。 (3)此扇形面積A。"
    )

    canonical_answer = f"(1) {theta_latex}; (2) {s_latex}; (3) {a_latex}"

    sol_text = (
        f"【解析】\n"
        f"(1) \\(\\theta = {deg}^\\circ = {deg} \\times \\frac{{\\pi}}{{180}} = {theta_latex}\\)\n"
        f"(2) \\(S = r\\theta = {r} \\times {theta_latex} = {s_latex}\\) (公分)\n"
        f"(3) \\(A = \\frac{{1}}{{2}}r^2\\theta = \\frac{{1}}{{2}} \\times {r}^2 \\times {theta_latex} = {a_latex}\\) (平方公分)"
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
            "target": f"{theta_latex}, {s_latex}, {a_latex}",
            "theta_frac": str(theta_frac),
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
