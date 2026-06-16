from __future__ import annotations

from typing import Any

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="vertical_line",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'line_type': 'vertical_line'},
    )
    payload = convert_line_equation_matrix_to_question_payload(matrix)
    payload["component_id"] = kwargs.get("component_id")
    payload["seed"] = seed
    return payload
