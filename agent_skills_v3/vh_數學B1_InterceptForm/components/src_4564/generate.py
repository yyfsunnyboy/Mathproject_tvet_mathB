from __future__ import annotations

import random
from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "intercept_form_equation_and_triangle_area"
TEXTBOOK_EXAMPLE_ID = 4564


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 4564)
    
    intercept_pool = [x for x in range(-8, 9) if x != 0]
    a = rng.choice(intercept_pool)
    b = rng.choice(intercept_pool)
    
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="intercept_form_equation_and_triangle_area",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'x_intercept': str(a), 'y_intercept': str(b)},
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

