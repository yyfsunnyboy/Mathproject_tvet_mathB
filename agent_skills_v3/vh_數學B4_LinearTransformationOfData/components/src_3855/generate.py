from __future__ import annotations

import random
from typing import Any

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "compute_population_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 3855
DEFAULT_COMPONENT_ID = "src_3855" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else 3855)
    
    # 1. Randomize parameters
    if seed is None:
        m = 47500
        s = 3000
        k = 5000
    else:
        m = rng.choice([35000, 38000, 40000, 42000, 45000, 48000, 50000, 52000])
        s = rng.choice([2000, 2500, 3000, 3500, 4000, 5000])
        k = rng.choice([-4000, -3000, -2000, 2000, 3000, 4000, 5000])

    adj_str = f"增加 {k} 元" if k > 0 else f"減少 {abs(k)} 元"

    # 2. Formulate question text
    question_text = (
        f"某公司全體員工隔年月薪皆{adj_str}。已知調薪前全體員工月薪的平均數為 {m} 元、"
        f"母體標準差為 {s} 元。若調薪後平均數為 \\(\\mu_y\\) 元、母體標準差為 \\(\\sigma_y\\) 元，"
        f"則下列敘述何者正確？"
    )

    new_m = m + k
    new_s = s

    # 3. Create 4 choices
    correct_text = f"\\(\\mu_y = {new_m}\\)，\\(\\sigma_y = {new_s}\\)"
    opt2 = f"\\(\\mu_y = {m}\\)，\\(\\sigma_y = {s}\\)"
    opt3 = f"\\(\\mu_y = {new_m}\\)，\\(\\sigma_y = {s + abs(k)}\\)"
    opt4 = f"\\(\\mu_y = {m - k}\\)，\\(\\sigma_y = {s}\\)"

    options_pool = [
        {"text": correct_text, "is_correct": True},
        {"text": opt2, "is_correct": False},
        {"text": opt3, "is_correct": False},
        {"text": opt4, "is_correct": False},
    ]

    # Deduplicate in case parameter combinations make options identical (e.g. k=0 which is not in our pool anyway)
    # Ensure options are distinct
    seen = set()
    unique_options = []
    for opt in options_pool:
        if opt["text"] not in seen:
            seen.add(opt["text"])
            unique_options.append(opt)
    
    # Fallback to make sure we have exactly 4 choices
    while len(unique_options) < 4:
        dummy_m = new_m + rng.choice([-1000, 1000, 2000])
        dummy_s = new_s + rng.choice([-500, 500, 1000])
        if dummy_s <= 0:
            dummy_s = 500
        text = f"\\(\\mu_y = {dummy_m}\\)，\\(\\sigma_y = {dummy_s}\\)"
        if text not in seen:
            seen.add(text)
            unique_options.append({"text": text, "is_correct": False})

    # Shuffle choices
    rng.shuffle(unique_options)

    labels = ["A", "B", "C", "D"]
    choices = []
    answer_label = "A"
    
    for label, opt in zip(labels, unique_options):
        choices.append({
            "key": label,
            "label": label,
            "text": opt["text"],
        })
        if opt["is_correct"]:
            answer_label = label

    explanation = (
        f"根據線性變換的性質，當所有數值資料皆增加（或減少）常數 \\(b\\) 時，\n"
        f"新的平均數會增加（或減少）常數 \\(b\\)，即 \\(\\mu_y = \\mu_x + b\\)；\n"
        f"而標準差不會受到平移變換的影響，保持不變，即 \\(\\sigma_y = \\sigma_x\\)。\n\n"
        f"本題中，調薪前平均數 \\(\\mu_x = {m}\\) 元，母體標準差 \\(\\sigma_x = {s}\\) 元，\n"
        f"每位員工月薪皆{adj_str}（即 \\(b = {k}\\)），\n"
        f"因此，調薪後：\n"
        f"平均數 \\(\\mu_y = {m} {'+ ' + str(k) if k >= 0 else '- ' + str(abs(k))} = {new_m}\\) 元，\n"
        f"母體標準差 \\(\\sigma_y = \\sigma_x = {new_s}\\) 元。\n"
        f"故正確答案為 ({answer_label})。"
    )

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")

    payload = {
        "skill_id": "vh_數學B4_LinearTransformationOfData",
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "domain_operation": "compute_population_standard_deviation",
        "selected_operation": "compute_population_standard_deviation",
        "fixed_domain_key": "statistics.descriptive_statistics",
        "source_kind": "quiz",
        "presentation_mode": "single_choice",
        "answer_type": "choice_label",
        "answer_shape": "single_choice",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "question_text": question_text,
        "explanation": explanation,
        "seed": seed,
        "choices": choices,
        "options": [c["text"] for c in choices],
        "answer": answer_label,
        "correct_answer": answer_label,
        "display_answer": answer_label,
        "answer_contract": {
            "presentation_mode": "single_choice",
            "answer_type": "choice_label",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": answer_label,
        },
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "metadata": {
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "component_id": component_id,
            "presentation_mode": "single_choice",
            "answer_type": "choice_label",
            "problem_type_id": PROBLEM_TYPE_ID,
            "source_kind": "quiz",
            "semantic_answer": answer_label,
        },
    }

    return payload
