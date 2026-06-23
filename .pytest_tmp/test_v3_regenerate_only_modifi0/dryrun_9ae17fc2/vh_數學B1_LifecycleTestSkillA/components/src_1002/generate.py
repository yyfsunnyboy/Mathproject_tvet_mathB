from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question_text": f"Compute 1 + 1 (seed={seed})",
        "presentation_mode": "single_choice",
        "answer_contract": {
            "answer_type": "single_choice",
            "checker_key": "exact_match",
        },
        "correct_answer": "2",
        "choices": ["1", "2", "3", "4"],
        "metadata": {"component_id": "src_1002"},
    }
