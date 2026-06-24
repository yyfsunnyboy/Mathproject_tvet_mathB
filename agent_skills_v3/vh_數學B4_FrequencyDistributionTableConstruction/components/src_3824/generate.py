from __future__ import annotations

import random
from typing import Any


PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "frequency_table_construction_review"
TEXTBOOK_EXAMPLE_ID = 3824


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
    values = [rng.randint(30, 99) for _ in range(8)]
    display_values = sorted(values)
    
    values_text = "、".join(str(v) for v in display_values)
    
    component_id = str(kwargs.get("component_id") or "src_3824")
    question_text = (
        f"有一組數值資料為 {values_text}。"
        "請問這組資料的全距是多少？"
    )
    answer = str(max(display_values) - min(display_values))
    
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
            "template_id": "range_from_raw_values",
            "semantic_answer": answer,
            "values": display_values,
            "range": int(answer),
            "answer_dependencies": ["values"],
            "visible_evidence": {
                "values": {
                    "field": "question_text",
                    "values": display_values,
                    "separator": "、",
                }
            },
        },
        "answer_contract": _answer_contract(),
        "checker": "integer_checker",
        "checker_type": "integer_checker",
        "equivalence": "exact_integer",
    }
