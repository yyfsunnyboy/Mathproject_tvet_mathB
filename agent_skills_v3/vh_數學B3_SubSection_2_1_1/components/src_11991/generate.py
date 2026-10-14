from __future__ import annotations

from typing import Any

from core.domain.equation_solving_domain import build_equation_solving_matrix
from core.gencode.equation_solving_capability_adapter import adapt_equation_solving_matrix

PRESENTATION_MODE = 'short_answer'
ANSWER_TYPE = 'multi_part'
PROBLEM_TYPE_ID = 'linear_word_three_shares'
TEXTBOOK_EXAMPLE_ID = 11991
DEFAULT_COMPONENT_ID = "src_11991"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    difficulty_profile = "easy"
    if difficulty := kwargs.get("difficulty"):
        try:
            d = int(difficulty)
            difficulty_profile = "hard" if d >= 3 else ("medium" if d == 2 else "easy")
        except Exception:
            difficulty_profile = str(difficulty)
    constraints = {
        "skill_id": 'vh_數學B3_SubSection_2_1_1',
        "problem_type_id": PROBLEM_TYPE_ID,
        "required_capabilities": [PROBLEM_TYPE_ID],
        "source_example_id": TEXTBOOK_EXAMPLE_ID,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
    }
    matrix = build_equation_solving_matrix(
        operation=PROBLEM_TYPE_ID,
        domain_operation=PROBLEM_TYPE_ID,
        constraints=constraints,
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile=difficulty_profile,
    )
    payload = adapt_equation_solving_matrix(
        matrix,
        domain_operation=PROBLEM_TYPE_ID,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID),
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        seed=seed,
    )
    payload["component_id"] = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    payload["seed"] = seed
    payload["domain_matrix"] = matrix
    return payload
