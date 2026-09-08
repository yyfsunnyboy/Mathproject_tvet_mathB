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
TEXTBOOK_EXAMPLE_ID = 11624
DEFAULT_COMPONENT_ID = "src_11624"

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)
NOTES_DATA = '{"question_anchor": {"anchor_id": "vocational_math_B2_1-1_advanced_exercise_009_019", "anchor_key": "vocational|longteng|math_B2|1|1-1|advanced_exercise|9|19", "curriculum": "vocational", "publisher": "longteng", "volume": "數學B2", "chapter": "1", "section": "1-1", "question_type": "advanced_exercise", "question_number": "9", "source_order": 19, "block_index": 18, "occurrence_index": 1, "question_label": "1-1習題 進階題9", "source_type": "advanced_exercise", "text_fingerprint": "faec138c008de182f4868214ea30de3bb080bf839961d8819a284f4cc8914db1"}, "image_assets": [{"asset_type": "pdf_visual_crop", "asset_slot": "pdf_visual_01", "source": "pdf", "path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題9_vocation_fig1.png", "display_path": "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題9_vocation_fig1.png", "page_index": 13, "source_page": 14, "bbox": [408, 232, 528, 352], "needs_crop_review": false, "needs_image_conversion": false, "reason": "audited_B2_1-1_source_figure", "image_description": "helpful", "visual_type": "diagram", "visual_classification": "helpful", "match_method": "audited_B2_1-1_pdf_sha256", "match_score": 1.0, "question_anchor": "vocational_math_B2_1-1_advanced_exercise_009_019", "width": 342, "height": 342, "file_size": 101450, "sha256": "da0a1dc10e9b215ad41b129f8d5f20660a6996ec0d66236b5156345000b14f3b", "dpi": 200}], "has_image": true, "needs_image_review": false}'


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
        (6, 3), (9, 3), (12, 3), (8, 4), (10, 4),
        (12, 4), (12, 6), (18, 6), (15, 5), (6, 4),
        (9, 6), (15, 3), (8, 2), (10, 5), (14, 4)
    ]
    r, k = rng.choice(candidates)

    ans_frac = Fraction(r * r, k)
    ans_latex = _format_pi_fraction_latex(ans_frac)

    question_text = (
        f"如圖所示：校門口有一個半徑{r}公尺的圓形花圃，農藝科同學打算將花圃平分成{k}等分的面積來種植不同的花卉，"
        f"作為校園園藝造景的景觀設計，請問每一等分的扇形面積為多少？"
    )

    canonical_answer = ans_latex

    sol_text = (
        f"【解析】\n"
        f"整個圓形花圃的面積為 \\(\\pi r^2 = \\pi \\times {r}^2 = {r*r}\\pi\\) 平方公尺。\n"
        f"平分成 {k} 等分，每一等分的扇形面積為：\n"
        f"\\[ \\frac{{{r*r}\\pi}}{{{k}}} = {ans_latex} \\text{{ (平方公尺)}} \\]"
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
            "givens": {"radius": r, "parts": k},
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
