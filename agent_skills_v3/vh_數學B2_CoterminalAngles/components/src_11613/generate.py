from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

from core.domain.trigonometry_angle_domain import (
    find_min_positive_max_negative,
    format_pi_fraction_latex,
)

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11613
DEFAULT_COMPONENT_ID = "src_11613"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # Subproblem 1: large positive degree
    k1 = rng.choice([2, 3, 4, 5])
    r1 = rng.choice([30, 45, 60, 90, 120, 135, 150, 210, 240, 270, 300, 315, 330])
    deg1 = 360 * k1 + r1
    res1 = find_min_positive_max_negative(deg1, unit="degree")

    # Subproblem 2: negative degree
    k2 = rng.choice([2, 3, 4, 5])
    r2 = rng.choice([20, 40, 50, 70, 80, 100, 110, 140, 200, 250, 340])
    deg2 = -360 * k2 - (360 - r2)
    res2 = find_min_positive_max_negative(deg2, unit="degree")

    # Subproblem 3: radian angle > 2pi
    q3 = rng.choice([3, 4, 6])
    rem_p = rng.choice([p for p in range(1, 2 * q3) if math.gcd(p, q3) == 1])
    k3 = rng.choice([2, 4, 6])
    p3 = k3 * q3 + rem_p
    rad_f = Fraction(p3, q3)
    rad_latex = format_pi_fraction_latex(rad_f)
    res3 = find_min_positive_max_negative(rad_f, unit="radian")

    pos1, neg1 = res1["min_positive"], res1["max_negative"]
    pos2, neg2 = res2["min_positive"], res2["max_negative"]
    pos3_latex, neg3_latex = res3["min_pos_latex"], res3["max_neg_latex"]

    question_text = (
        f"試求下列各角的最小正同界角與最大負同界角：\n"
        f"(1)\\({deg1}^\\circ\\) (2)\\({deg2}^\\circ\\) (3)\\({rad_latex}\\)"
    )

    ans_part1 = f"{pos1}^\\circ, {neg1}^\\circ"
    ans_part2 = f"{pos2}^\\circ, {neg2}^\\circ"
    ans_part3 = f"{pos3_latex}, {neg3_latex}"

    canonical_answer = f"(1) {ans_part1}; (2) {ans_part2}; (3) {ans_part3}"

    sol_text = (
        f"【解析】\n"
        f"(1) \\({deg1}^\\circ = 360^\\circ \\times {k1} + {pos1}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos1}^\\circ\\)，最大負同界角為 \\({pos1}^\\circ - 360^\\circ = {neg1}^\\circ\\)。\n"
        f"(2) \\({deg2}^\\circ = 360^\\circ \\times (-{k2 + 1}) + {pos2}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos2}^\\circ\\)，最大負同界角為 \\({pos2}^\\circ - 360^\\circ = {neg2}^\\circ\\)。\n"
        f"(3) \\({rad_latex} = 2\\pi \\times {k3 // 2} + {pos3_latex}\\)，\n"
        f"    最小正同界角為 \\({pos3_latex}\\)，最大負同界角為 \\({pos3_latex} - 2\\pi = {neg3_latex}\\)。"
    )

    answer_dict = {
        "part_1": ans_part1,
        "part_2": ans_part2,
        "part_3": ans_part3,
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
                "expected_answer": ans_part1,
            },
            {
                "key": "part_2",
                "label": "(2)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": ans_part2,
            },
            {
                "key": "part_3",
                "label": "(3)",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "equivalence_type": "expression_equivalence",
                "expected_answer": ans_part3,
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
            "givens": {
                "deg1": deg1, "pos1": pos1, "neg1": neg1,
                "deg2": deg2, "pos2": pos2, "neg2": neg2,
                "rad3": str(rad_f), "pos3": str(res3["min_positive"]), "neg3": str(res3["max_negative"]),
            },
            "target": canonical_answer,
        },
    }
