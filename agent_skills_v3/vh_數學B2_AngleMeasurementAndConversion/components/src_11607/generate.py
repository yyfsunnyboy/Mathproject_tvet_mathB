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
PROBLEM_TYPE_ID = "angle_measurement_and_conversion"
TEXTBOOK_EXAMPLE_ID = 11607
DEFAULT_COMPONENT_ID = "src_11607"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _format_radian_latex(f: Fraction) -> str:
    p, q = f.numerator, f.denominator
    sign = "-" if p < 0 else ""
    abs_p = abs(p)
    if q == 1:
        if abs_p == 1:
            return f"{sign}\\pi"
        return f"{sign}{abs_p}\\pi"
    else:
        if abs_p == 1:
            return f"{sign}\\frac{{\\pi}}{{{q}}}"
        return f"{sign}\\frac{{{abs_p}\\pi}}{{{q}}}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # Subproblem 1: negative/large degree to radian
    deg_pool = [-570, -420, -390, -330, -300, -240, -210, -150, -135, -120, -60, -45, -30, 480, 510, 570, 600]
    deg_val = rng.choice(deg_pool)
    rad_frac = Fraction(deg_val, 180)
    ans1_latex = _format_radian_latex(rad_frac)

    # Subproblem 2: radian to degree
    rad_pool = [(5, 6), (7, 6), (11, 6), (2, 3), (4, 3), (5, 3), (3, 4), (5, 4), (7, 4), (-5, 6), (-7, 6), (-2, 3), (-4, 3)]
    a, b = rng.choice(rad_pool)
    rad_input_frac = Fraction(a, b)
    rad_input_latex = _format_radian_latex(rad_input_frac)
    deg_ans = int(rad_input_frac * 180)

    question_text = (
        f"試求下列各角的度度量與弧度量換算：\n"
        f"(1) 試將 ${deg_val}^\\circ$ 化為弧度。\n"
        f"(2) 試將 ${rad_input_latex}$ 化為度。"
    )

    combined_answer = f"(1) {ans1_latex}；(2) {deg_ans}^\\circ"

    detailed_solution = (
        f"(1) 由 $180^\\circ = \\pi$ 弧度，${deg_val}^\\circ = {deg_val} \\times \\frac{{\\pi}}{{180}} = {ans1_latex}$。\n"
        f"(2) 由 $\\pi$ 弧度 $= 180^\\circ$，${rad_input_latex} = {rad_input_frac.numerator} \\times \\frac{{180^\\circ}}{{{rad_input_frac.denominator}}} = {deg_ans}^\\circ$。"
    )

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)

    payload: dict[str, Any] = {
        "question_text": question_text,
        "answer": combined_answer,
        "correct_answer": combined_answer,
        "display_answer": combined_answer,
        "detailed_solution": detailed_solution,
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "equivalence": "multi_part_answer",
        "equivalence_type": "multi_part_answer",
        "answer_contract": {
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "equivalence": "multi_part_answer",
            "equivalence_type": "multi_part_answer",
        },
        "math_core": {
            "givens": {
                "deg_input": deg_val,
                "rad_input": rad_input_latex,
                "target_rad_num": rad_frac.numerator,
                "target_rad_den": rad_frac.denominator,
                "target_deg": deg_ans,
            },
            "target": f"{ans1_latex}, {deg_ans}^\\circ",
            "math_objects": ["angle", "radian", "degree"],
            "derivation": [
                f"{deg_val} * (pi/180) = {ans1_latex}",
                f"{rad_input_latex} * (180/pi) = {deg_ans}",
            ],
        },
        "metadata": {
            "component_id": component_id,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "problem_type_id": PROBLEM_TYPE_ID,
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "givens": {
                "deg_input": deg_val,
                "rad_input": rad_input_latex,
            },
        },
        "seed": seed,
    }
    return payload


def _parse_math_expr(s: str) -> Any:
    t = str(s or "").strip()
    t = (
        t.replace("$", "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("π", "pi")
        .replace("度", "")
        .replace("°", "")
        .replace("^\\circ", "")
        .replace("^{\\circ}", "")
    )
    for _ in range(4):
        t = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"((\1)/(\2))", t)
        t = re.sub(r"frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"((\1)/(\2))", t)
    t = t.replace("\\pi", "pi").replace("\\", "")
    t = re.sub(r"\)\s*pi", r")*pi", t)
    t = re.sub(r"(\d)\s*pi", r"\1*pi", t)
    return parse_expr(t, local_dict={"pi": pi}, transformations=_TRANSFORMATIONS)
