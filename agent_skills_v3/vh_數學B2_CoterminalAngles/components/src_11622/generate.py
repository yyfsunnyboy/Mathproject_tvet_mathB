from __future__ import annotations

import random
import re
from typing import Any

from sympy import simplify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11622
DEFAULT_COMPONENT_ID = "src_11622"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    # Subproblem 1: positive degree > 360
    k1 = rng.choice([1, 2, 3, 4])
    r1 = rng.choice([30, 45, 60, 90, 120, 150, 210, 240, 300, 330])
    deg1 = 360 * k1 + r1
    pos1 = r1
    neg1 = r1 - 360

    # Subproblem 2: negative degree < -360
    k2 = rng.choice([2, 3, 4, 5])
    r2 = rng.choice([40, 70, 80, 110, 130, 160, 220, 260, 310])
    deg2 = -360 * k2 - (360 - r2)
    pos2 = r2
    neg2 = r2 - 360

    question_text = (
        f"試求下列各角的最小正同界角與最大負同界角：\n"
        f"(1)\\({deg1}^\\circ\\) (2)\\({deg2}^\\circ\\)"
    )

    canonical_answer = f"(1) {pos1}^\\circ, {neg1}^\\circ; (2) {pos2}^\\circ, {neg2}^\\circ"

    sol_text = (
        f"【解析】\n"
        f"(1) \\({deg1}^\\circ = 360^\\circ \\times {k1} + {pos1}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos1}^\\circ\\)，最大負同界角為 \\({pos1}^\\circ - 360^\\circ = {neg1}^\\circ\\)。\n"
        f"(2) \\({deg2}^\\circ = 360^\\circ \\times (-{k2 + 1}) + {pos2}^\\circ\\)，\n"
        f"    最小正同界角為 \\({pos2}^\\circ\\)，最大負同界角為 \\({pos2}^\\circ - 360^\\circ = {neg2}^\\circ\\)。"
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
            },
            "target": canonical_answer,
        },
    }


def _clean_deg(s: str) -> str:
    res = s.strip()
    res = res.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    return res
