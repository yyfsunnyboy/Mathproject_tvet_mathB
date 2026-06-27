from __future__ import annotations

import random
from typing import Any

from core.gencode.descriptive_statistics_answer_contract import normalize_answer_contract

PRESENTATION_MODE = "multi_blank"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "compute_population_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 3854
DEFAULT_COMPONENT_ID = "src_3854" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 3854)
    
    # 1. Randomize parameters
    if seed is None:
        mean = 5
        std = 4
        a1, b1 = 1, -2
        a2, b2 = 3, 0
        a3, b3 = -2, 15
    else:
        mean = rng.choice([5, 6, 8, 10, 12, 15, 20])
        std = rng.choice([2, 3, 4, 5, 6])
        # Group 1: Translation (a=1)
        a1 = 1
        b1 = rng.choice([-10, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 10])
        # Group 2: Positive coefficient, no translation (a>0, b=0)
        a2 = rng.choice([2, 3, 4, 5])
        b2 = 0
        # Group 3: Negative coefficient (a<0)
        a3 = rng.choice([-5, -4, -3, -2, -1])
        b3 = rng.choice([-10, -5, 5, 10, 12, 15, 20, 25, 30])

    def make_eq_str(a: int, b: int) -> str:
        if a == 1:
            a_part = "x_i"
        elif a == -1:
            a_part = "-x_i"
        else:
            a_part = f"{a}x_i"
            
        if b == 0:
            return a_part
        elif b > 0:
            return f"{a_part} + {b}"
        else:
            return f"{a_part} - {abs(b)}"

    eq1_str = make_eq_str(a1, b1)
    eq2_str = make_eq_str(a2, b2)
    eq3_str = make_eq_str(a3, b3)

    # 2. Group labels for subquestions (just (1), (2), (3) to avoid repeating formula in answers)
    group_label_1 = "(1)"
    group_label_2 = "(2)"
    group_label_3 = "(3)"

    # 3. Calculate answers
    mean_1 = a1 * mean + b1
    std_1 = abs(a1) * std

    mean_2 = a2 * mean + b2
    std_2 = abs(a2) * std

    mean_3 = a3 * mean + b3
    std_3 = abs(a3) * std

    answers = [mean_1, std_1, mean_2, std_2, mean_3, std_3]

    # 4. Formulate texts
    question_text = (
        f"已知一組資料的算術平均數為 {mean}，標準差為 {std}，"
        f"試求下列各組資料的平均數與標準差："
        f"(1) \\(y_i = {eq1_str}\\)；(2) \\(y_i = {eq2_str}\\)；(3) \\(y_i = {eq3_str}\\)。"
    )

    explanation = (
        f"根據線性變換的性質，若新資料為 \\(y_i = a x_i + b\\)，"
        f"則新平均數 \\(\\mu_y = a \\mu_x + b\\)，新標準差 \\(\\sigma_y = |a| \\sigma_x\\)。\n\n"
        f"(1) 對於 \\(y_i = {eq1_str}\\)：\n"
        f"平均數 \\(\\mu_{{y1}} = {a1} \\times {mean} {'+ ' + str(b1) if b1 >= 0 else '- ' + str(abs(b1))} = {mean_1}\\)\n"
        f"標準差 \\(\\sigma_{{y1}} = |{a1}| \\times {std} = {std_1}\\)\n\n"
        f"(2) 對於 \\(y_i = {eq2_str}\\)：\n"
        f"平均數 \\(\\mu_{{y2}} = {a2} \\times {mean} = {mean_2}\\)\n"
        f"標準差 \\(\\sigma_{{y2}} = |{a2}| \\times {std} = {std_2}\\)\n\n"
        f"(3) 對於 \\(y_i = {eq3_str}\\)：\n"
        f"平均數 \\(\\mu_{{y3}} = {a3} \\times {mean} {'+ ' + str(b3) if b3 >= 0 else '- ' + str(abs(b3))} = {mean_3}\\)\n"
        f"標準差 \\(\\sigma_{{y3}} = |{a3}| \\times {std} = {std_3}\\)"
    )

    # 5. Build subquestions, field specs, and ui contract
    field_specs = [
        {
            "field_key": "y1_mean",
            "label": "平均數",
            "group_label": group_label_1,
            "expected_answer": mean_1,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
        {
            "field_key": "y1_std",
            "label": "標準差",
            "group_label": group_label_1,
            "expected_answer": std_1,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
        {
            "field_key": "y2_mean",
            "label": "平均數",
            "group_label": group_label_2,
            "expected_answer": mean_2,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
        {
            "field_key": "y2_std",
            "label": "標準差",
            "group_label": group_label_2,
            "expected_answer": std_2,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
        {
            "field_key": "y3_mean",
            "label": "平均數",
            "group_label": group_label_3,
            "expected_answer": mean_3,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
        {
            "field_key": "y3_std",
            "label": "標準差",
            "group_label": group_label_3,
            "expected_answer": std_3,
            "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
            "input_type": "number",
        },
    ]

    subquestions = [
        {
            "field_key": "y1_mean",
            "part": group_label_1,
            "prompt": "平均數",
            "input_type": "number",
            "expected_answer": mean_1,
        },
        {
            "field_key": "y1_std",
            "part": group_label_1,
            "prompt": "標準差",
            "input_type": "number",
            "expected_answer": std_1,
        },
        {
            "field_key": "y2_mean",
            "part": group_label_2,
            "prompt": "平均數",
            "input_type": "number",
            "expected_answer": mean_2,
        },
        {
            "field_key": "y2_std",
            "part": group_label_2,
            "prompt": "標準差",
            "input_type": "number",
            "expected_answer": std_2,
        },
        {
            "field_key": "y3_mean",
            "part": group_label_3,
            "prompt": "平均數",
            "input_type": "number",
            "expected_answer": mean_3,
        },
        {
            "field_key": "y3_std",
            "part": group_label_3,
            "prompt": "標準差",
            "input_type": "number",
            "expected_answer": std_3,
        },
    ]

    ui_contract = {
        "response_mode": "multi_blank",
        "text_input_enabled": True,
        "field_groups": [
            {
                "group_label": group_label_1,
                "fields": ["y1_mean", "y1_std"],
            },
            {
                "group_label": group_label_2,
                "fields": ["y2_mean", "y2_std"],
            },
            {
                "group_label": group_label_3,
                "fields": ["y3_mean", "y3_std"],
            },
        ],
    }

    answer_contract = normalize_answer_contract(
        answer=answers,
        expected_answer_shape="multi_blank",
        rounding_policy={"decimal_places": 0, "prefer_integer": True},
        field_specs=field_specs,
    )
    answer_contract["ui_contract"].update(ui_contract)

    display_answer = [
        {"key": "y1_mean", "display_answer": str(mean_1)},
        {"key": "y1_std", "display_answer": str(std_1)},
        {"key": "y2_mean", "display_answer": str(mean_2)},
        {"key": "y2_std", "display_answer": str(std_2)},
        {"key": "y3_mean", "display_answer": str(mean_3)},
        {"key": "y3_std", "display_answer": str(std_3)},
    ]

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")

    payload = {
        "skill_id": "vh_數學B4_LinearTransformationOfData",
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "domain_operation": "compute_population_standard_deviation",
        "selected_operation": "compute_population_standard_deviation",
        "fixed_domain_key": "statistics.descriptive_statistics",
        "source_kind": "example",
        "presentation_mode": "multi_blank",
        "answer_type": "multi_part",
        "answer_shape": "multi_blank",
        "interaction_type": "multi_blank",
        "auto_checkable": True,
        "grading_mode": "auto",
        "question_text": question_text,
        "explanation": explanation,
        "seed": seed,
        "choices": [],
        "options": [],
        "answer": answers,
        "correct_answer": answers,
        "display_answer": display_answer,
        "answer_contract": answer_contract,
        "ui_contract": answer_contract["ui_contract"],
        "subquestions": subquestions,
        "validation_facts": {
            "domain_operation": "compute_population_standard_deviation",
            "target_measure": "standard_deviation",
            "answer_shape": "multi_blank",
            "statistics": answers,
        },
        "metadata": {
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "component_id": component_id,
            "presentation_mode": "multi_blank",
            "answer_type": "multi_part",
            "problem_type_id": PROBLEM_TYPE_ID,
            "source_kind": "example",
            "semantic_answer": answers,
        },
        "checker_key": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "rounding_policy": {"decimal_places": 0, "prefer_integer": True},
    }

    return payload
