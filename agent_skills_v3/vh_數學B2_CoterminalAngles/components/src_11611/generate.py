from __future__ import annotations

import random
from typing import Any

from core.domain.trigonometry_angle_domain import check_is_coterminal

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11611
DEFAULT_COMPONENT_ID = "src_11611"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    base_choices = [30, 45, 50, 60, 70, 80, 110, 120, 135, 140, 150, 210, 220, 240, 300, 315]
    base_deg = rng.choice(base_choices)

    k_pool = [-3, -2, -1, 1, 2, 3]
    rng.shuffle(k_pool)
    k1, k2 = k_pool[0], k_pool[1]
    coterm1 = base_deg + 360 * k1
    coterm2 = base_deg + 360 * k2

    k3 = k_pool[2]
    offset = rng.choice([-150, -120, -90, -50, 50, 80, 100, 120, 150])
    non_coterm = base_deg + 360 * k3 + offset

    options = [
        {"angle": coterm1},
        {"angle": coterm2},
        {"angle": non_coterm},
    ]
    rng.shuffle(options)

    correct_indices: list[int] = []
    sol_steps: list[str] = []
    opt_texts: list[str] = []

    for idx, opt in enumerate(options, 1):
        ang = opt["angle"]
        opt_texts.append(f"({idx})\\({ang}^\\circ\\)")
        is_coterm, k_val = check_is_coterminal(ang, base_deg, unit="degree")
        diff = ang - base_deg
        if is_coterm:
            correct_indices.append(idx)
            sol_steps.append(
                f"({idx}) \\({ang}^\\circ - {base_deg}^\\circ = {diff}^\\circ = 360^\\circ \\times ({k_val})\\) 為同界角"
            )
        else:
            sol_steps.append(
                f"({idx}) \\({ang}^\\circ - {base_deg}^\\circ = {diff}^\\circ\\) 不是 \\(360^\\circ\\) 的倍數，故非同界角"
            )

    canonical_answer = "".join(f"({i})" for i in correct_indices)

    question_text = (
        f"下列何者與\\({base_deg}^\\circ\\)互為同界角？\n" + " ".join(opt_texts)
    )

    sol_text = (
        f"【解析】\n"
        f"兩角若為同界角，則其差必為 \\(360^\\circ\\) 的整數倍。\n"
        + "\n".join(sol_steps) + "\n"
        + f"故選 {canonical_answer}。"
    )

    answer_contract = {
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "checker": "solution_set_checker",
        "checker_key": "solution_set_checker",
        "answer_equivalence": "unordered_solution_set",
        "equivalence_type": "unordered_solution_set",
        "expected_answer": canonical_answer,
    }

    return {
        "question_text": question_text,
        "answer": canonical_answer,
        "canonical_answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "answer_contract": answer_contract,
        "math_core": {
            "givens": {"base_deg": base_deg, "correct_indices": correct_indices},
            "target": canonical_answer,
        },
    }
