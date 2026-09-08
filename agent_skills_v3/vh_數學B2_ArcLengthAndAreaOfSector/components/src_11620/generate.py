from __future__ import annotations

import json
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
TEXTBOOK_EXAMPLE_ID = 11620
DEFAULT_COMPONENT_ID = "src_11620"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)
NOTES_DATA = '{"question_anchor": {"anchor_id": "vocational_math_B2_1-1_exercise_005_015", "anchor_key": "vocational|longteng|math_B2|1|1-1|exercise|5|15", "curriculum": "vocational", "publisher": "longteng", "volume": "數學B2", "chapter": "1", "section": "1-1", "question_type": "exercise", "question_number": "5", "source_order": 15, "block_index": 14, "occurrence_index": 1, "question_label": "1-1習題 基礎題5", "source_type": "textbook_exercise", "text_fingerprint": "6a67fc9b4524781e3fc78310146367df6493203ea998de4240d7a823cb5af695"}, "image_assets": [{"asset_type": "pdf_visual_crop", "asset_slot": "pdf_visual_01", "source": "pdf", "path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/textbook_exercise_1-1習題_基礎題5_vocation_fig1.png", "display_path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/textbook_exercise_1-1習題_基礎題5_vocation_fig1.png", "page_index": 12, "source_page": 13, "bbox": [315, 533, 389, 606], "needs_crop_review": false, "needs_image_conversion": false, "reason": "audited_B2_1-1_source_figure", "image_description": "helpful", "visual_type": "diagram", "visual_classification": "helpful", "match_method": "audited_B2_1-1_pdf_sha256", "match_score": 1.0, "question_anchor": "vocational_math_B2_1-1_exercise_005_015", "width": 214, "height": 210, "file_size": 10336, "sha256": "dddaa4a81e6c84110a59ccd3b077b9e446b6bb28b461c4931f2c158892ef4cf2", "dpi": 200}], "has_image": true, "needs_image_review": false}'


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
        (12, 15), (18, 15), (12, 30), (24, 15), (16, 45),
        (10, 18), (15, 24), (20, 18), (12, 45), (18, 30),
        (30, 12), (24, 30), (14, 45), (20, 45), (15, 36)
    ]
    L, half_deg = rng.choice(candidates)
    total_deg = half_deg * 2

    theta_frac = Fraction(total_deg, 180)
    a_frac = Fraction(1, 2) * (L * L) * theta_frac
    s_frac = L * theta_frac

    a_latex = _format_pi_fraction_latex(a_frac)
    s_latex = _format_pi_fraction_latex(s_frac)

    question_text = (
        f"爺爺收藏的古典時鐘，是一個下方有鐘擺的掛鐘，若鐘擺長為{L}公分，左右最大擺角各為{half_deg}°，試求：\n"
        f"(1)鐘擺掃出的最大面積。\n"
        f"(2)鐘擺底端揮出的最大弧長。"
    )

    canonical_answer = f"(1) {a_latex}; (2) {s_latex}"

    sol_text = (
        f"【解析】\n"
        f"最大總擺角 \\(\\theta = {half_deg}^\\circ \\times 2 = {total_deg}^\\circ = \\frac{{{total_deg}\\pi}}{{180}} = {_format_pi_fraction_latex(theta_frac)}\\)\n"
        f"半徑 \\(r = {L}\\) 公分\n"
        f"(1) 掃出最大面積 \\(A = \\frac{{1}}{{2}}r^2\\theta = \\frac{{1}}{{2}} \\times {L}^2 \\times {_format_pi_fraction_latex(theta_frac)} = {a_latex}\\) (平方公分)\n"
        f"(2) 底端最大弧長 \\(S = r\\theta = {L} \\times {_format_pi_fraction_latex(theta_frac)} = {s_latex}\\) (公分)"
    )

    notes_dict = {}
    try:
        notes_dict = json.loads(NOTES_DATA)
    except Exception:
        pass

    return {
        "question_text": question_text,
        "answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "notes": notes_dict,
        "has_image": True,
        "math_core": {
            "givens": {"length": L, "half_angle": half_deg, "total_deg": total_deg},
            "target": f"{a_latex}, {s_latex}",
            "a_frac": str(a_frac),
            "s_frac": str(s_frac),
        },
    }


def _clean_expr(expr_str: str) -> str:
    s = expr_str.strip()
    s = s.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    s = s.replace(r"\pi", "pi").replace("π", "pi")
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    return s
