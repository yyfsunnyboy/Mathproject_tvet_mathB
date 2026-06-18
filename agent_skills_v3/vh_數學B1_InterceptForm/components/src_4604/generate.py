from __future__ import annotations

import math
import random
from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "intercept_form_triangle_area"
TEXTBOOK_EXAMPLE_ID = 4604


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 4604)
    
    # Sample non-zero intercepts a, b in [-8, 8]
    intercept_pool = [x for x in range(-8, 9) if x != 0]
    a = rng.choice(intercept_pool)
    b = rng.choice(intercept_pool)
    
    A = b
    B = a
    C = -a * b
    
    g = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
    A //= g
    B //= g
    C //= g
    
    if A < 0:
        A = -A
        B = -B
        C = -C
        
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="intercept_form_triangle_area",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'equation_coefficients': {'A': A, 'B': B, 'C': C}},
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

