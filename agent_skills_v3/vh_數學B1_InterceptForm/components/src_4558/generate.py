from __future__ import annotations

import random
from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "linear_equation"
PROBLEM_TYPE_ID = "triangle_area_bisector_line_equation"
TEXTBOOK_EXAMPLE_ID = 4558


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 4558)
    
    success = False
    xa, ya, xb, yb, xc, yc = 0, 0, 0, 0, 0, 0
    for _ in range(100):
        xa = rng.randint(-10, 10)
        ya = rng.randint(-10, 10)
        
        xc = rng.choice([x for x in range(-10, 11) if x % 2 == xa % 2])
        yc = rng.choice([y for y in range(-10, 11) if y % 2 == ya % 2])
        
        xd = (xa + xc) // 2
        yd = (ya + yc) // 2
        
        xb = rng.randint(-10, 10)
        yb = rng.randint(-10, 10)
        
        if xb == xd and yb == yd:
            continue
            
        area = xa * (yb - yc) + xb * (yc - ya) + xc * (ya - yb)
        if area != 0:
            success = True
            break
            
    if not success:
        xa, ya = 2, 2
        xc, yc = 0, 0
        xb, yb = 5, -3
        
    vertex = {'label': 'B', 'x': str(xb), 'y': str(yb)}
    edge_p1 = {'label': 'A', 'x': str(xa), 'y': str(ya)}
    edge_p2 = {'label': 'C', 'x': str(xc), 'y': str(yc)}
    
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="triangle_area_bisector_line_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'vertex': vertex, 'edge_p1': edge_p1, 'edge_p2': edge_p2},
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

