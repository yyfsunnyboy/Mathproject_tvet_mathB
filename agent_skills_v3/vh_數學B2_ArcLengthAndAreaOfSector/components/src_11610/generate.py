from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.domain.trigonometry_angle_domain import calculate_sector_properties

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "arc_length_and_area_of_sector"
TEXTBOOK_EXAMPLE_ID = 11610
DEFAULT_COMPONENT_ID = "src_11610"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    candidates = [
        (10, 15), (8, 12), (12, 18), (6, 9), (10, 25), (12, 15),
        (14, 21), (16, 20), (20, 30), (8, 14), (15, 20), (16, 24)
    ]
    r, s = rng.choice(candidates)

    prop = calculate_sector_properties(r, arc_given=s)
    theta_str = prop["theta_str"]
    area_str = prop["area_str"]

    question_text = (
        f"SDG 14 保育海洋生態\n"
        f"如圖，此海域劃分之扇形保護區半徑為{r}浬，弧長為{s}浬，試求：\n"
        f"(1)保護區扇形圓心角θ。(2)保護區扇形面積。"
    )

    canonical_answer = f"(1) {theta_str}; (2) {area_str}"

    sol_text = (
        f"【解析】\n"
        f"(1) 由 \\(S = r\\theta\\) 得 \\({s} = {r}\\theta \\implies \\theta = {theta_str}\\) (弧度)\n"
        f"(2) 面積 \\(A = \\frac{{1}}{{2}} r S = \\frac{{1}}{{2}} \\times {r} \\times {s} = {area_str}\\) (平方浬)"
    )

    answer_dict = {
        "part_1": theta_str,
        "part_2": area_str,
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
                "expected_answer": theta_str,
            },
            {
                "key": "part_2",
                "label": "(2)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": area_str,
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
            "givens": {"radius": r, "arc_length": s},
            "target": f"{theta_str}, {area_str}",
        },
    }
