from __future__ import annotations

import random
import re
from typing import Any

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11621
DEFAULT_COMPONENT_ID = "src_11621"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    base_choices = [30, 45, 60, 120, 150, 210, 240, 300]
    base_deg = rng.choice(base_choices)

    # 2 coterminal angles
    k_pool = [-4, -3, -2, -1, 1, 2, 3, 4]
    rng.shuffle(k_pool)
    k1, k2 = k_pool[0], k_pool[1]
    coterm1 = base_deg + 360 * k1
    coterm2 = base_deg + 360 * k2

    # 1 non-coterminal angle
    offset = rng.choice([-160, -100, -80, -40, 40, 80, 100, 160])
    k3 = k_pool[2]
    non_coterm = base_deg + 360 * k3 + offset

    options_data = [
        {"deg": coterm1, "is_coterm": True, "k": k1},
        {"deg": coterm2, "is_coterm": True, "k": k2},
        {"deg": non_coterm, "is_coterm": False, "offset": offset},
    ]
    rng.shuffle(options_data)

    correct_indices: list[int] = []
    opt_texts: list[str] = []
    sol_steps: list[str] = []

    for idx, opt in enumerate(options_data, 1):
        ang = opt["deg"]
        opt_texts.append(f"({idx})\\({ang}^\\circ\\)")
        diff = ang - base_deg
        if opt["is_coterm"]:
            correct_indices.append(idx)
            sol_steps.append(
                f"({idx}) \\({ang}^\\circ - {base_deg}^\\circ = {diff}^\\circ = 360^\\circ \\times ({opt['k']})\\) 為同界角"
            )
        else:
            sol_steps.append(
                f"({idx}) \\({ang}^\\circ - {base_deg}^\\circ = {diff}^\\circ\\) 不能被 360 整除，故不為同界角"
            )

    question_text = (
        f"下列何者為\\({base_deg}^\\circ\\)的同界角？\n" + " ".join(opt_texts)
    )

    canonical_answer = "".join(f"({i})" for i in correct_indices)

    sol_text = (
        f"【解析】\n"
        f"與 \\({base_deg}^\\circ\\) 為同界角之條件為兩角之差為 \\(360^\\circ\\) 的整數倍。\n"
        + "\n".join(sol_steps) + "\n"
        + f"故選 {canonical_answer}。"
    )

    return {
        "question_text": question_text,
        "answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "math_core": {
            "givens": {"base_deg": base_deg, "correct_indices": correct_indices},
            "target": canonical_answer,
        },
    }
