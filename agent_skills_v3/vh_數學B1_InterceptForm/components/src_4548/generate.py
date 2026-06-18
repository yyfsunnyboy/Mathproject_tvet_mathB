from __future__ import annotations

from fractions import Fraction
import random
from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "intercept_form_from_intercept_sum_and_slope"
TEXTBOOK_EXAMPLE_ID = 4548


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 4548)
    
    pool = [x for x in range(-8, 9) if x != 0]
    while True:
        a = rng.choice(pool)
        b = rng.choice(pool)
        if a != -b:
            break
            
    S = a + b
    m = Fraction(-b, a)
    
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="intercept_form_from_intercept_sum_and_slope",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'intercept_sum': str(S), 'slope': str(m)},
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

