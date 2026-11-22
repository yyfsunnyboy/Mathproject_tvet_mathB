from __future__ import annotations

from typing import Any

from core.gencode.remainder_theorem_symbolic import generate_symbolic_remainder_statement

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "remainder_theorem_state_symbolic"
TEXTBOOK_EXAMPLE_ID = 4638
DEFAULT_COMPONENT_ID = "src_4638"
FIXED_ROOTS = [-1, 2]


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    _ = level
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    return generate_symbolic_remainder_statement(
        seed,
        skill_id="vh_數學B1_RemainderTheorem",
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        fixed_roots=FIXED_ROOTS,
    )
