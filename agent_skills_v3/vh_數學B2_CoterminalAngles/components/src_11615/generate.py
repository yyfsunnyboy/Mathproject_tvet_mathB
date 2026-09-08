from __future__ import annotations

import random
import re
from typing import Any

PRESENTATION_MODE = "multiple_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11615
DEFAULT_COMPONENT_ID = "src_11615"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    candidates = [
        2019, 1425, 1780, 2150, 1070, 2530, 1995, 2240, 1850, 2024, 2110, 1340, 1630
    ]
    deg = rng.choice(candidates)

    rem = deg % 360
    hour = rem // 30
    if hour == 0:
        correct_desc = "分針指在12 跟1 之間"
    else:
        next_hour = (hour + 1) if (hour + 1) <= 12 else 1
        correct_desc = f"分針指在{hour} 跟{next_hour} 之間"

    wrong_hours = [h for h in range(12) if h != hour]
    rng.shuffle(wrong_hours)
    wrong_descs: list[str] = []
    for wh in wrong_hours[:3]:
        if wh == 0:
            wrong_descs.append("分針指在12 跟1 之間")
        else:
            w_next = (wh + 1) if (wh + 1) <= 12 else 1
            wrong_descs.append(f"分針指在{wh} 跟{w_next} 之間")

    all_options = [
        {"desc": correct_desc, "is_correct": True},
        {"desc": wrong_descs[0], "is_correct": False},
        {"desc": wrong_descs[1], "is_correct": False},
        {"desc": wrong_descs[2], "is_correct": False},
    ]
    rng.shuffle(all_options)

    letters = ["(A)", "(B)", "(C)", "(D)"]
    correct_letter = ""
    opt_lines: list[str] = []
    for i, opt in enumerate(all_options):
        letter = letters[i]
        opt_lines.append(f"{letter} {opt['desc']}")
        if opt["is_correct"]:
            correct_letter = letter

    question_text = (
        f"假設分針原始指在時鐘12 的位置，現將分針依順時針的方向轉了{deg}°。試問下列敘述何者正確？\n"
        + "\n".join(opt_lines)
    )

    canonical_answer = correct_letter

    k = deg // 360
    sol_text = (
        f"【解析】\n"
        f"(1) 時鐘每大格（1小時）所對應之圓心角為 \\(360^\\circ \\div 12 = 30^\\circ\\)。\n"
        f"(2) 分針轉了 \\({deg}^\\circ = 360^\\circ \\times {k} + {rem}^\\circ\\)。\n"
        f"(3) 因為 \\({hour * 30}^\\circ < {rem}^\\circ < {((hour + 1)) * 30}^\\circ\\)，\n"
        f"    故分針位置落在 {correct_desc.replace('分針指在', '')}。\n"
        f"故選 {correct_letter}。"
    )

    return {
        "question_text": question_text,
        "answer": canonical_answer,
        "solution": sol_text,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": DEFAULT_COMPONENT_ID,
        "options": [opt["desc"] for opt in all_options],
        "math_core": {
            "givens": {"rotation_deg": deg, "remainder": rem, "hour": hour},
            "target": correct_letter,
        },
    }
