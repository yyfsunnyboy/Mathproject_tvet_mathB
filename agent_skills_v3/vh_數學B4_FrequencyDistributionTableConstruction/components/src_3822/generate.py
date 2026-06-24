from __future__ import annotations

import random
from typing import Any


PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "frequency_table_construction_review"
TEXTBOOK_EXAMPLE_ID = 3822


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
    raw_scores = [rng.randint(32, 96) for _ in range(40)]
    display_scores = sorted(raw_scores)
    intervals = [(32, 41), (42, 51), (52, 61), (62, 71), (72, 81), (82, 91), (92, 101)]
    group_count = len(intervals)
    target_lower, target_upper = intervals[rng.randrange(group_count)]
    target_frequency = sum(1 for score in raw_scores if target_lower <= score <= target_upper)
    scores_text = "\u3001".join(str(score) for score in display_scores)
    component_id = str(kwargs.get("component_id") or "src_3822")
    question_text = (
        f"\u570b\u8cbf\u79d1\u4e09\u5e74\u7532\u73ed{len(raw_scores)}\u4eba"
        f"\u82f1\u6587\u6a21\u64ec\u8003\u6210\u7e3e\u5982\u4e0b\uff1a{scores_text}\u3002"
        f"\u5c07\u6210\u7e3e\u5206\u6210{group_count}\u7d44\uff0c"
        f"\u5176\u4e2d\u4e00\u7d44\u70ba{target_lower}\uff5e{target_upper}\u5206\uff0c"
        "\u8acb\u554f\u6b64\u7d44\u7684\u6b21\u6578\u662f\u591a\u5c11\uff1f"
    )
    answer = str(target_frequency)
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
            "template_id": "raw_scores_interval_count",
            "semantic_answer": answer,
            "raw_scores": display_scores,
            "group_count": group_count,
            "target_interval": {
                "lower": target_lower,
                "upper": target_upper,
                "inclusive": True,
            },
            "target_frequency": target_frequency,
            "answer_dependencies": ["raw_scores"],
            "visible_evidence": {
                "raw_scores": {
                    "field": "question_text",
                    "values": display_scores,
                    "separator": "\u3001",
                }
            },
        },
        "answer_contract": _answer_contract(),
        "checker": "integer_checker",
        "checker_type": "integer_checker",
        "equivalence": "exact_integer",
    }
