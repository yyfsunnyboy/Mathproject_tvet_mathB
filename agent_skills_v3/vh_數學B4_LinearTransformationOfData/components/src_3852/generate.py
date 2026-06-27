from __future__ import annotations

import random
from typing import Any

from core.gencode.descriptive_statistics_answer_contract import normalize_answer_contract

PRESENTATION_MODE = "multi_blank"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "compute_population_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 3852
DEFAULT_COMPONENT_ID = "src_3852" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 3852)
    
    # 1. Randomize parameters while maintaining original textbook spirit (mean=20, std=5)
    if seed is None:
        mean = 20
        std = 5
        k1 = 5
        k2 = 3
        k3 = 2
        k4 = -10
    else:
        mean = rng.choice([15, 20, 25, 30, 35, 40, 45, 50])
        std = rng.choice([3, 4, 5, 6, 8, 10])
        k1 = rng.choice([-15, -10, -5, -3, 2, 3, 5, 8, 10, 15])
        k2 = rng.choice([2, 3, 4, 5])
        k3 = rng.choice([2, 3, 4])
        k4 = rng.choice([-20, -15, -10, -5, 5, 10, 15, 20])

    k1_str = f"+ {k1}" if k1 >= 0 else f"- {abs(k1)}"
    k4_str = f"+ {k4}" if k4 >= 0 else f"- {abs(k4)}"

    # 2. Group labels for subquestions
    group_label_1 = "(1)"
    group_label_2 = "(2)"
    group_label_3 = "(3)"

    # 3. Calculate answers
    mean_1 = mean + k1
    std_1 = std

    mean_2 = k2 * mean
    std_2 = k2 * std

    mean_3 = k3 * mean + k4
    std_3 = k3 * std

    answers = [mean_1, std_1, mean_2, std_2, mean_3, std_3]

    # 4. Formulate texts
    question_text = (
        f"已知一組資料的算術平均數為 {mean}，標準差為 {std}，"
        f"試求下列各組資料的平均數與標準差："
        f"(1) \\(y_i = x_i {k1_str}\\)；(2) \\(y_i = {k2}x_i\\)；(3) \\(y_i = {k3}x_i {k4_str}\\)。"
    )

    explanation = (
        f"根據線性變換的性質，若新資料為 \\(y_i = a x_i + b\\)，"
        f"則新平均數 \\(\\mu_y = a \\mu_x + b\\)，新標準差 \\(\\sigma_y = |a| \\sigma_x\\)。\n\n"
        f"(1) 對於 {group_label_1}：\n"
        f"平均數 \\(\\mu_{{y1}} = \\mu_x {k1_str} = {mean} {k1_str} = {mean_1}\\)\n"
        f"標準差 \\(\\sigma_{{y1}} = \\sigma_x = {std_1}\\)\n\n"
        f"(2) 對於 {group_label_2}：\n"
        f"平均數 \\(\\mu_{{y2}} = {k2} \\mu_x = {k2} \\times {mean} = {mean_2}\\)\n"
        f"標準差 \\(\\sigma_{{y2}} = {k2} \\sigma_x = {k2} \\times {std} = {std_2}\\)\n\n"
        f"(3) 對於 {group_label_3}：\n"
        f"平均數 \\(\\mu_{{y3}} = {k3} \\mu_x {k4_str} = {k3} \\times {mean} {k4_str} = {mean_3}\\)\n"
        f"標準差 \\(\\sigma_{{y3}} = {k3} \\sigma_x = {k3} \\times {std} = {std_3}\\)"
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

