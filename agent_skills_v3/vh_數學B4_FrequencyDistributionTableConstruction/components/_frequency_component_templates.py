from __future__ import annotations

import random
from typing import Any


def _contract() -> dict[str, Any]:
    return {
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "answer_equivalence": "exact_integer",
        "equivalence": "exact_integer",
    }


def _payload(
    *,
    component_id: str,
    textbook_example_id: int,
    question_text: str,
    answer: int,
    seed: int | None,
    template_id: str,
    metadata_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": "frequency_table_construction_review",
        "domain_operation": "frequency_table_construction_review",
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "template_id": template_id,
        "semantic_answer": str(answer),
    }
    if metadata_extra:
        metadata.update(metadata_extra)

    return {
        "question_text": question_text,
        "question": question_text,
        "answer": str(answer),
        "correct_answer": str(answer),
        "display_answer": str(answer),
        "semantic_answer": str(answer),
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": "frequency_table_construction_review",
        "domain_operation": "frequency_table_construction_review",
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "answer_value_type": "integer",
        "seed": seed,
        "metadata": metadata,
        "answer_contract": _contract(),
        "checker": "integer_checker",
        "checker_type": "integer_checker",
        "equivalence": "exact_integer",
    }


def generate_component_payload(
    *,
    component_id: str,
    textbook_example_id: int,
    seed: int | None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    if textbook_example_id == 3822:
        scores = [rng.randint(32, 96) for _ in range(40)]
        display_scores = sorted(scores)
        intervals = [(32, 41), (42, 51), (52, 61), (62, 71), (72, 81), (82, 91), (92, 101)]
        group_count = len(intervals)
        interval = intervals[rng.randrange(len(intervals))]
        answer = sum(1 for value in scores if interval[0] <= value <= interval[1])
        scores_text = "、".join(str(value) for value in display_scores)
        question_text = (
            f"國貿科三年甲班{len(scores)}人英文模擬考成績如下："
            f"{scores_text}。"
            f"將成績分成{group_count}組，其中一組為"
            f"{interval[0]}～{interval[1]}分，"
            "請問此組的次數是多少？"
        )
        return _payload(
            component_id=component_id,
            textbook_example_id=textbook_example_id,
            question_text=question_text,
            answer=answer,
            seed=seed,
            template_id="raw_scores_interval_count",
            metadata_extra={
                "raw_scores": display_scores,
                "group_count": group_count,
                "target_interval": {
                    "lower": interval[0],
                    "upper": interval[1],
                    "inclusive": True,
                },
                "target_frequency": answer,
                "answer_dependencies": ["raw_scores"],
                "visible_evidence": {
                    "raw_scores": {
                        "field": "question_text",
                        "values": display_scores,
                        "separator": "、",
                    }
                },
            },
        )

    if textbook_example_id == 3823:
        known_rows = [(40, 49, 4), (50, 59, 8), (60, 69, 12), (70, 79, 11)]
        total = 45
        known_total = sum(row[2] for row in known_rows)
        answer = total - known_total
        table_text = "、".join(f"{lo}～{hi}分：{freq}人" for lo, hi, freq in known_rows)
        question_text = (
            "會計科三年甲班45人數學模擬考分成5組。"
            f"已知前四組次數為：{table_text}。"
            "請問最後一組 80～89 分的次數是多少？"
        )
        return _payload(component_id=component_id, textbook_example_id=textbook_example_id, question_text=question_text, answer=answer, seed=seed, template_id="missing_frequency_from_total")

    if textbook_example_id == 3824:
        values = [60, 64, 66, 68, 73, 75, 76, 85]
        answer = max(values) - min(values)
        question_text = (
            "有一組數值資料為 60、64、66、68、73、75、76、85。"
            "請問這組資料的全距是多少？"
        )
        return _payload(component_id=component_id, textbook_example_id=textbook_example_id, question_text=question_text, answer=answer, seed=seed, template_id="range_from_raw_values")

    if textbook_example_id == 3825:
        ages = [25, 26, 27, 28, 28, 30, 31, 31, 32, 35, 36, 36, 37, 37, 38, 39, 39, 40, 42, 44]
        intervals = [(25, 29), (30, 34), (35, 39), (40, 44)]
        interval = intervals[rng.randrange(len(intervals))]
        answer = sum(1 for value in ages if interval[0] <= value <= interval[1])
        question_text = (
            "某公司企劃部20位員工年齡資料依組距5分成4組，"
            f"最小一組為25～29歲。請問 {interval[0]}～{interval[1]} 歲這一組的次數是多少？"
        )
        return _payload(component_id=component_id, textbook_example_id=textbook_example_id, question_text=question_text, answer=answer, seed=seed, template_id="age_interval_count")

    raise ValueError(f"unsupported_textbook_example_id:{textbook_example_id}")
