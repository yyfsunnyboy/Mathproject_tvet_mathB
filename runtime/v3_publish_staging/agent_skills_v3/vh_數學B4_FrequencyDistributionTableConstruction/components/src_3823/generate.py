from __future__ import annotations

import random
from typing import Any


PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "frequency_table_construction_review"
TEXTBOOK_EXAMPLE_ID = 3823


def _answer_contract() -> dict[str, Any]:
    return {
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "answer_equivalence": "exact_integer",
        "equivalence": "exact_integer",
    }


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)
    freqs = [rng.randint(3, 12) for _ in range(5)]
    total = sum(freqs)
    
    known_rows = [(40, 49, freqs[0]), (50, 59, freqs[1]), (60, 69, freqs[2]), (70, 79, freqs[3])]
    table_text = "、".join(f"{lo}～{hi}分：{freq}人" for lo, hi, freq in known_rows)
    
    component_id = str(kwargs.get("component_id") or "src_3823")
    question_text = (
        f"會計科三年甲班{total}人數學模擬考分成5組。"
        f"已知前四組次數為：{table_text}。"
        "請問最後一組 80～89 分的次數是多少？"
    )
    answer = str(freqs[4])
    
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": answer,
        "correct_answer": answer,
        "display_answer": answer,
        "semantic_answer": answer,
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "domain_operation": "frequency_table_construction_review",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "answer_value_type": "integer",
        "seed": seed,
        "metadata": {
            "component_id": component_id,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "problem_type_id": PROBLEM_TYPE_ID,
            "domain_operation": "frequency_table_construction_review",
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "template_id": "missing_frequency_from_total",
            "semantic_answer": answer,
            "total_frequency": total,
            "known_frequencies": freqs[:4],
            "target_frequency": freqs[4],
            "answer_dependencies": ["frequency_table"],
            "visible_evidence": {
                "frequency_table": {
                    "field": "question_text",
                    "values": table_text,
                }
            },
        },
        "answer_contract": _answer_contract(),
        "checker": "integer_checker",
        "checker_type": "integer_checker",
        "equivalence": "exact_integer",
    }
