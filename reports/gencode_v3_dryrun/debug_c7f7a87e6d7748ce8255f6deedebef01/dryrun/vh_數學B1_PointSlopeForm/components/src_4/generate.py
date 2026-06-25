from __future__ import annotations

from typing import Any


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question_text": "mock question 4",
        "answer": "mock answer",
        "correct_answer": "mock answer",
        "component_id": "src_4",
        "metadata": {"component_id": "src_4"},
    }


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> bool:
    return str(user_answer) == str(correct_answer)
