from __future__ import annotations

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
TEXTBOOK_EXAMPLE_ID = 11617
DEFAULT_COMPONENT_ID = "src_11617"

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

    pool = [450, 560, 480, 540, 600, 630, 720, 840, 400, 500, 520, 640, 750]
    deg1 = rng.choice([450, 480, 540, 630, 720, 420])
    deg2 = rng.choice([560, 400, 500, 520, 640, 700])

    f1 = Fraction(deg1, 180)
    f2 = Fraction(deg2, 180)
    ans1_latex = _format_radian_latex(f1)
    ans2_latex = _format_radian_latex(f2)

    question_text = (
        f"將下列各角化成以弧度為單位：\n"
        f"(1) ${deg1}^\\circ = $\n"
        f"(2) ${deg2}^\\circ = $"
    )

    combined_answer = f"(1) {ans1_latex}；(2) {ans2_latex}"

    detailed_solution = (
        f"(1) ${deg1}^\\circ = {deg1} \\times \\frac{{\\pi}}{{180}} = {ans1_latex}$。\n"
        f"(2) ${deg2}^\\circ = {deg2} \\times \\frac{{\\pi}}{{180}} = {ans2_latex}$。"
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
                "deg1": deg1,
                "deg2": deg2,
                "target1_num": f1.numerator,
                "target1_den": f1.denominator,
                "target2_num": f2.numerator,
                "target2_den": f2.denominator,
            },
            "target": f"{ans1_latex}, {ans2_latex}",
            "math_objects": ["angle", "radian", "degree"],
            "derivation": [
                f"{deg1} * (pi/180) = {ans1_latex}",
                f"{deg2} * (pi/180) = {ans2_latex}",
            ],
        },
        "metadata": {
            "component_id": component_id,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "problem_type_id": PROBLEM_TYPE_ID,
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "givens": {
                "deg1": deg1,
                "deg2": deg2,
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
