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
TEXTBOOK_EXAMPLE_ID = 11618
DEFAULT_COMPONENT_ID = "src_11618"

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

    rad_pool1 = [(6, 5), (7, 5), (8, 5), (9, 5), (3, 5), (4, 5)]
    rad_pool2 = [(5, 3), (4, 3), (2, 3), (7, 3), (5, 6), (7, 6)]
    num_pool = [2, 3, 4, 5]

    a1, b1 = rng.choice(rad_pool1)
    a2, b2 = rng.choice(rad_pool2)
    val3 = rng.choice(num_pool)

    f1 = Fraction(a1, b1)
    f2 = Fraction(a2, b2)

    rad1_latex = _format_radian_latex(f1)
    rad2_latex = _format_radian_latex(f2)

    deg1 = int(f1 * 180)
    deg2 = int(f2 * 180)
    ans3_num = val3 * 180
    ans3_latex = f"\\frac{{{ans3_num}^\\circ}}{{\\pi}}"

    question_text = (
        f"將下列各角化成以度為單位：（提示：$1 = \\frac{{180^\\circ}}{{\\pi}}$）\n"
        f"(1) ${rad1_latex} = $\n"
        f"(2) ${rad2_latex} = $\n"
        f"(3) ${val3} = $"
    )

    combined_answer = f"(1) {deg1}^\\circ；(2) {deg2}^\\circ；(3) {ans3_latex}"

    detailed_solution = (
        f"(1) ${rad1_latex} = {a1} \\times \\frac{{180^\\circ}}{{{b1}}} = {deg1}^\\circ$。\n"
        f"(2) ${rad2_latex} = {a2} \\times \\frac{{180^\\circ}}{{{b2}}} = {deg2}^\\circ$。\n"
        f"(3) 由 $1$ 弧度 $= \\frac{{180^\\circ}}{{\\pi}}$，知 ${val3} = {val3} \\times \\frac{{180^\\circ}}{{\\pi}} = {ans3_latex}$。"
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
                "rad1": rad1_latex,
                "rad2": rad2_latex,
                "val3": val3,
                "target1_deg": deg1,
                "target2_deg": deg2,
                "target3_num": ans3_num,
            },
            "target": combined_answer,
            "math_objects": ["angle", "radian", "degree"],
            "derivation": [
                f"{rad1_latex} * (180/pi) = {deg1}",
                f"{rad2_latex} * (180/pi) = {deg2}",
                f"{val3} * (180/pi) = {ans3_latex}",
            ],
        },
        "metadata": {
            "component_id": component_id,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "problem_type_id": PROBLEM_TYPE_ID,
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "givens": {
                "rad1": rad1_latex,
                "rad2": rad2_latex,
                "val3": val3,
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
