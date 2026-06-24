from __future__ import annotations

import random
from typing import Any


PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "integer"
PROBLEM_TYPE_ID = "frequency_table_construction_review"
TEXTBOOK_EXAMPLE_ID = 3825


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
    ages = [rng.randint(25, 44) for _ in range(20)]
    display_ages = sorted(ages)
    
    intervals = [(25, 29), (30, 34), (35, 39), (40, 44)]
    target_lower, target_upper = intervals[rng.randrange(len(intervals))]
    target_frequency = sum(1 for age in ages if target_lower <= age <= target_upper)
    
    ages_text = "、".join(str(a) for a in display_ages)
    
    component_id = str(kwargs.get("component_id") or "src_3825")
    question_text = (
        "某公司企劃部20位員工年齡資料如下：\n"
        f"{ages_text}。\n"
        "將資料依組距5分成4組，最小一組為25～29歲。\n"
        f"請問{target_lower}～{target_upper}歲這一組的次數是多少？"
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
            "template_id": "age_interval_count",
            "semantic_answer": answer,
            "values": display_ages,
            "group_count": len(intervals),
            "target_interval": {
                "lower": target_lower,
                "upper": target_upper,
                "inclusive": True,
            },
            "target_frequency": target_frequency,
            "answer_dependencies": ["values"],
            "visible_evidence": {
                "values": {
                    "field": "question_text",
                    "values": display_ages,
                    "separator": "、",
                }
            },
        },
        "answer_contract": _answer_contract(),
        "checker": "integer_checker",
        "checker_type": "integer_checker",
        "equivalence": "exact_integer",
    }
