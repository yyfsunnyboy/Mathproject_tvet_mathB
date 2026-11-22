# -*- coding: utf-8 -*-
"""Symbolic remainder-theorem statement generator (no concrete f(x)).

Textbook sources such as src_4638 / src_4664 ask students to *state* the
remainder when an unspecified polynomial f(x) is divided by linear factors,
i.e. answer f(c). This is mathematically deterministic and distinct from
``remainder_theorem_evaluate`` which substitutes a concrete polynomial.
"""

from __future__ import annotations

import random
from typing import Any


def _linear_factor_tex(c: int) -> str:
    """Return LaTeX for the monic linear factor with root c (divisor x−c)."""
    if c == 0:
        return "x"
    if c > 0:
        return f"x-{c}"
    return f"x+{abs(c)}"


def _f_of_c_plain(c: int) -> str:
    return f"f({c})"


def _normalize_f_expr(value: Any) -> str:
    text = str(value or "").strip().replace(" ", "").replace("$", "")
    text = text.replace("{", "").replace("}", "")
    text = text.replace("（", "(").replace("）", ")")
    return text.lower()


def generate_symbolic_remainder_statement(
    seed: int | None = None,
    *,
    skill_id: str = "vh_數學B1_RemainderTheorem",
    problem_type_id: str = "remainder_theorem_state_symbolic",
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    fixed_roots: list[int] | tuple[int, ...] | None = None,
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|remainder_symbolic|{component_id or ''}")
    if fixed_roots and len(fixed_roots) >= 2:
        roots = [int(fixed_roots[0]), int(fixed_roots[1])]
    else:
        pool = [-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6]
        roots = rng.sample(pool, 2)

    parts_answer = {
        "part_1": _f_of_c_plain(roots[0]),
        "part_2": _f_of_c_plain(roots[1]),
    }
    factor_bits = " ".join(
        f"({i + 1}) ${_linear_factor_tex(c)}$" for i, c in enumerate(roots)
    )
    stem = (
        "寫出當多項式 $f(x)$ 除以下列各式時所得的餘式。"
        f"{factor_bits}"
    )
    explanation = (
        "由餘式定理：除以 $(x-c)$ 的餘式等於 $f(c)$。"
        f"故 (1) {_f_of_c_plain(roots[0])}；(2) {_f_of_c_plain(roots[1])}。"
    )
    answer_contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "presentation_mode": "short_answer",
        "parts": [
            {
                "key": "part_1",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "equivalence_type": "exact_string",
                "answer": parts_answer["part_1"],
                "accepted_formats": [parts_answer["part_1"], f"$f({roots[0]})$"],
            },
            {
                "key": "part_2",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "equivalence_type": "exact_string",
                "answer": parts_answer["part_2"],
                "accepted_formats": [parts_answer["part_2"], f"$f({roots[1]})$"],
            },
        ],
        "answer_format_example": f"{parts_answer['part_1']}；{parts_answer['part_2']}",
        "accepted_formats": [
            f"{parts_answer['part_1']}；{parts_answer['part_2']}",
            f"{parts_answer['part_1']},{parts_answer['part_2']}",
        ],
    }
    payload: dict[str, Any] = {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": parts_answer,
        "correct_answer": parts_answer,
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "checker_type": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "answer_contract": answer_contract,
        "presentation_mode": "short_answer",
        "explanation": explanation,
        "explanation_steps": [
            "餘式定理：f(x) 除以 (x−c) 的餘式等於 f(c)。",
            f"(1) 除以 ${_linear_factor_tex(roots[0])}$ → {parts_answer['part_1']}",
            f"(2) 除以 ${_linear_factor_tex(roots[1])}$ → {parts_answer['part_2']}",
        ],
        "metadata": {
            "givens": {"roots": list(roots), "mode": "symbolic_remainder_statement"},
            "target": "state_f_of_c",
            "template_slot": "remainder_theorem_state_symbolic",
            "template_variant": "symbolic_f_of_c",
            "normalize_f_expr": True,
        },
        "source": "remainder_theorem_symbolic",
        "seed": seed,
    }
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = int(textbook_example_id)
    return payload


def answers_equivalent_symbolic_f(user: Any, expected: Any) -> bool:
    return _normalize_f_expr(user) == _normalize_f_expr(expected)
