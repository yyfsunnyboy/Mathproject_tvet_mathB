from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.domain.trigonometry_angle_domain import calculate_sector_properties

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "arc_length_and_area_of_sector"
TEXTBOOK_EXAMPLE_ID = 11608
DEFAULT_COMPONENT_ID = "src_11608"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # (r, n) where theta = 2pi / n, area = 1/2 * r^2 * (2pi / n) = (r^2 / n) * pi
    candidates = [
        (16, 8), (12, 6), (12, 4), (10, 5), (14, 7), (18, 6),
        (20, 8), (24, 8), (24, 12), (15, 6), (16, 4), (8, 4),
        (18, 9), (20, 10), (12, 8), (16, 6), (10, 8), (9, 6)
    ]
    r, n = rng.choice(candidates)
    a_given = Fraction(r * r, n)

    prop = calculate_sector_properties(r, area_given=a_given)
    theta_latex = prop["theta_latex"]
    s_latex = prop["arc_latex"]
    a_latex = prop["area_latex"]

    question_text = (
        f"設一扇形的半徑為{r}公分，面積為\\({a_latex}\\)平方公分，試求此扇形的：\n"
        f"(1)圓心角。(2)弧長。"
    )

    canonical_answer = f"(1) {theta_latex}; (2) {s_latex}"

    sol_text = (
        f"【解析】\n"
        f"設圓心角為 \\(\\theta\\)，扇形面積 \\(A = \\frac{{1}}{{2}} r^2 \\theta\\)\n"
        f"(1) \\({a_latex} = \\frac{{1}}{{2}} \\times {r}^2 \\times \\theta \\implies \\theta = {theta_latex}\\)\n"
        f"(2) 弧長 \\(S = r\\theta = {r} \\times {theta_latex} = {s_latex}\\) (公分)"
    )

    answer_dict = {
        "part_1": theta_latex,
        "part_2": s_latex,
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
                "expected_answer": theta_latex,
            },
            {
                "key": "part_2",
                "label": "(2)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": s_latex,
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
            "givens": {"radius": r, "area": str(a_given)},
            "target": f"{theta_latex}, {s_latex}",
        },
    }
