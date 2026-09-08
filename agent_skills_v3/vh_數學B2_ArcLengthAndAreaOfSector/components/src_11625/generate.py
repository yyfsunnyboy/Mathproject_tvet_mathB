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

PRESENTATION_MODE = "single_input"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "arc_length_and_area_of_sector"
TEXTBOOK_EXAMPLE_ID = 11625
DEFAULT_COMPONENT_ID = "src_11625"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)
NOTES_DATA = '{"question_anchor": {"anchor_id": "vocational_math_B2_1-1_advanced_exercise_010_020", "anchor_key": "vocational|longteng|math_B2|1|1-1|advanced_exercise|10|20", "curriculum": "vocational", "publisher": "longteng", "volume": "數學B2", "chapter": "1", "section": "1-1", "question_type": "advanced_exercise", "question_number": "10", "source_order": 20, "block_index": 19, "occurrence_index": 1, "question_label": "1-1習題 進階題10", "source_type": "advanced_exercise", "text_fingerprint": "45c8381693a42bdd8f1df4c0101852ea5b4b63d5d2df9c6f5cd6060bbc3da1b1"}, "image_assets": [{"asset_type": "pdf_visual_crop", "asset_slot": "pdf_visual_01", "source": "pdf", "path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題10_vocation_fig1.png", "display_path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題10_vocation_fig1.png", "page_index": 13, "source_page": 14, "bbox": [361, 369, 530, 602], "needs_crop_review": false, "needs_image_conversion": false, "reason": "audited_B2_1-1_source_figure", "image_description": "helpful", "visual_type": "diagram", "visual_classification": "helpful", "match_method": "audited_B2_1-1_pdf_sha256", "match_score": 1.0, "question_anchor": "vocational_math_B2_1-1_advanced_exercise_010_020", "width": 477, "height": 655, "file_size": 249319, "sha256": "82ab409c4631b37b1bf7b33819fe8b77734714a0b552c1a9f5cf7f039ae34f1e", "dpi": 200}], "has_image": true, "needs_image_review": false}'


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
        (20, 80), (15, 60), (18, 40), (24, 75), (30, 80),
        (20, 90), (12, 120), (25, 72), (16, 45), (20, 45),
        (18, 50), (24, 60), (15, 80), (21, 60), (30, 45)
    ]
    w, deg = rng.choice(candidates)

    theta_frac = Fraction(deg, 180)
    ans_frac = Fraction(1, 2) * (w * w) * theta_frac
    ans_latex = _format_pi_fraction_latex(ans_frac)

    question_text = (
        f"英國有一座「摺扇橋」橫跨在{w}公尺寬的帕丁頓 大聯盟運河上。它是由英國著名橋梁設計專家騎士建築事務所設計，"
        f"它的設計靈感來源於日本傳統的摺扇，它是全球唯一一座可以像摺扇一般開合自如的大橋，其最大的展開角為{deg}度。"
        f"請問在最大展開時的扇形面積為何？"
    )

    canonical_answer = ans_latex

    sol_text = (
        f"【解析】\n"
        f"由題意可知，扇形半徑 \\(r = {w}\\) 公尺，中心角 \\(\\theta = {deg}^\\circ = \\frac{{{deg}\\pi}}{{180}} = {_format_pi_fraction_latex(theta_frac)}\\)。\n"
        f"展開時扇形面積為：\n"
        f"\\[ A = \\frac{{1}}{{2}}r^2\\theta = \\frac{{1}}{{2}} \\times {w}^2 \\times {_format_pi_fraction_latex(theta_frac)} = {ans_latex} \\text{{ (平方公尺)}} \\]"
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
            "givens": {"width": w, "degree": deg},
            "target": ans_latex,
            "area_frac": str(ans_frac),
        },
    }


def _clean_expr(expr_str: str) -> str:
    s = expr_str.strip()
    s = s.replace("°", "").replace("^{\\circ}", "").replace("^\\circ", "").replace("度", "")
    s = s.replace(r"\pi", "pi").replace("π", "pi")
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    return s
