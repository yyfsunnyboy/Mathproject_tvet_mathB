from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import Any

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "solution_set"
PROBLEM_TYPE_ID = "coterminal_angles"
TEXTBOOK_EXAMPLE_ID = 11612
DEFAULT_COMPONENT_ID = "src_11612"


def _format_pi_fraction_latex(f: Fraction) -> str:
    p, q = f.numerator, f.denominator
    sign = "-" if p < 0 else ""
    abs_p = abs(p)
    if q == 1:
        if abs_p == 1:
            return rf"{sign}\pi"
        return rf"{sign}{abs_p}\pi"
    else:
        if abs_p == 1:
            return rf"{sign}\frac{{\pi}}{{{q}}}"
        return rf"{sign}\frac{{{abs_p}\pi}}{{{q}}}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed)

    base_fractions = [
        Fraction(1, 6), Fraction(1, 4), Fraction(1, 3),
        Fraction(2, 3), Fraction(3, 4), Fraction(5, 6)
    ]
    base_f = rng.choice(base_fractions)
    base_latex = _format_pi_fraction_latex(base_f)

    # 1 coterminal option: base + 2k*pi (k in [-3, 3] \ {0})
    k_coterm = rng.choice([-3, -2, -1, 2, 3, 6])
    cand_coterm = base_f + 2 * k_coterm

    # 2 non-coterminal options: base + (odd)*pi or base + non-integer pi
    cand_non1 = base_f + rng.choice([-1, 1, 3, -3])
    cand_non2 = base_f + Fraction(rng.choice([1, 3, 5]), 2)

    options_data = [
        {"frac": cand_coterm, "is_coterm": True, "k": k_coterm},
        {"frac": cand_non1, "is_coterm": False},
        {"frac": cand_non2, "is_coterm": False},
    ]
    rng.shuffle(options_data)

    correct_indices: list[int] = []
    opt_texts: list[str] = []
    sol_steps: list[str] = []

    for idx, opt in enumerate(options_data, 1):
        f = opt["frac"]
        latex_str = _format_pi_fraction_latex(f)
        opt_texts.append(f"({idx})\\({latex_str}\\)")
        diff = f - base_f
        diff_latex = _format_pi_fraction_latex(diff)
        if opt["is_coterm"]:
            correct_indices.append(idx)
            sol_steps.append(
                f"({idx}) \\({latex_str} - {base_latex} = {diff_latex} = 2({opt['k']})\\pi\\) 為同界角"
            )
        else:
            sol_steps.append(
                f"({idx}) \\({latex_str} - {base_latex} = {diff_latex}\\) 不是 \\(2\\pi\\) 的整數倍，故不為同界角"
            )

    question_text = (
        f"下列何者與\\({base_latex}\\)互為同界角？\n" + " ".join(opt_texts)
    )

    canonical_answer = "".join(f"({i})" for i in correct_indices)

    sol_text = (
        f"【解析】\n"
        f"與 \\({base_latex}\\) 為同界角之條件為兩角之差為 \\(2k\\pi\\)（\\(k \\in \\mathbb{{Z}}\\)。\n"
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
            "givens": {
                "base_angle": str(base_f),
                "correct_indices": correct_indices,
            },
            "target": canonical_answer,
        },
    }
