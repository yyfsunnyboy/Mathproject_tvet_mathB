from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.domain.trigonometry_angle_domain import (
    degree_to_radian,
    radian_to_degree,
)

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "angle_measurement_and_conversion"
TEXTBOOK_EXAMPLE_ID = 11606
DEFAULT_COMPONENT_ID = "src_11606"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    deg_candidates = [30, 45, 60, 120, 135, 150, 210, 225, 240, 300, 315, 330]
    deg = rng.choice(deg_candidates)
    res_deg = degree_to_radian(deg)

    rad_fractions = [
        Fraction(1, 6), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2),
        Fraction(2, 3), Fraction(3, 4), Fraction(5, 6), Fraction(7, 6),
        Fraction(5, 4), Fraction(4, 3), Fraction(3, 2), Fraction(5, 3),
        Fraction(7, 4), Fraction(11, 6)
    ]
    rad_f = rng.choice(rad_fractions)
    res_rad = radian_to_degree(rad_f)

    target_rad_latex = res_deg["latex"]
    target_deg_val = res_rad["degree"]
    rad_prompt_latex = res_rad["degree_latex"]  # degree latex representation for solution

    from core.domain.trigonometry_angle_domain import format_pi_fraction_latex
    rad_input_latex = format_pi_fraction_latex(rad_f)

    question_text = (
        f"(1)試將{deg}°化為弧度。(2)試將\\({rad_input_latex}\\)化為度。"
    )

    canonical_answer = f"(1) {target_rad_latex}; (2) {target_deg_val}"

    sol_text = (
        f"【解析】\n"
        f"(1) \\({deg}^\\circ = {deg} \\times \\frac{{\\pi}}{{180}} = {target_rad_latex}\\)\n"
        f"(2) \\({rad_input_latex} = {rad_f.numerator} \\times \\frac{{180^\\circ}}{{{rad_f.denominator}}} = {target_deg_val}^\\circ\\)"
    )

    answer_dict = {
        "part_1": target_rad_latex,
        "part_2": str(target_deg_val),
    }

    answer_contract = {
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "answer_equivalence": "multi_part_answer",
        "equivalence_type": "multi_part_answer",
        "parts": [
            {
                "key": "part_1",
                "label": "(1)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": target_rad_latex,
            },
            {
                "key": "part_2",
                "label": "(2)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": str(target_deg_val),
            },
        ],
    }

    return {
        "question_text": question_text,
        "answer": answer_dict,
        "canonical_answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "answer_contract": answer_contract,
        "math_core": {
            "givens": {"source_deg": deg, "source_rad": str(rad_f), "target_deg": target_deg_val},
            "target": f"{target_rad_latex}, {target_deg_val}",
        },
    }
