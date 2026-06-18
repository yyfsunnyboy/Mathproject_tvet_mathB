from __future__ import annotations

from fractions import Fraction
import random
from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "parabola_secant_parallel_line_choice"
TEXTBOOK_EXAMPLE_ID = 4559


def format_origin_line(k: Fraction) -> str:
    if k.denominator == 1:
        val = k.numerator
        if val == 1:
            return "y=x"
        elif val == -1:
            return "y=-x"
        else:
            return f"y={val}x"
    else:
        return f"y=\\frac{{{k.numerator}}}{{{k.denominator}}}x"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 4559)
    
    pool = [x for x in range(-5, 6)]
    while True:
        p = rng.choice(pool)
        q = rng.choice(pool)
        if p != q and p + q != 0:
            break
            
    m = Fraction(p + q, 1)
    
    slopes = [m]
    candidates = [
        -m,
        Fraction(1, m) if m != 0 else Fraction(2, 1),
        Fraction(-1, m) if m != 0 else Fraction(-2, 1),
        m * 2,
        -m * 2,
        Fraction(m.numerator, m.denominator * 2),
        Fraction(-m.numerator, m.denominator * 2),
    ]
    for cand in candidates:
        if cand not in slopes:
            slopes.append(cand)
            if len(slopes) == 4:
                break
                
    offset = 1
    while len(slopes) < 4:
        cand = m + offset
        if cand not in slopes:
            slopes.append(cand)
        offset += 1
        
    choices_list = [{"label": "", "text": format_origin_line(k)} for k in slopes]
    rng.shuffle(choices_list)
    for idx, item in enumerate(choices_list):
        item["label"] = chr(ord("A") + idx)
        
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="parabola_secant_parallel_line_choice",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'p': str(p), 'q': str(q), 'choices': choices_list},
    )
    component_id = str(kwargs.get("component_id") or "")
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload

