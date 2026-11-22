# -*- coding: utf-8 -*-
"""B1 NumberLine native generator: inequality operation fill-in table.

Faithful to textbook ``src_4401`` structure (multiply/divide both sides by
positive and negative constants). Oracle is deterministic from the seed —
Stage-1 DB ``correct_answer`` is not required.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any


def _fmt_num(value: Fraction | int) -> str:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        sign = "-" if value < 0 else ""
        return f"{sign}{abs(value.numerator)}/{value.denominator}"
    return str(int(value))


def _cmp_token(left: Fraction, right: Fraction) -> str:
    if left > right:
        return ">"
    if left < right:
        return "<"
    return "="


def generate_inequality_operation_table(
    seed: int | None = None,
    *,
    skill_id: str = "vh_數學B1_NumberLine",
    problem_type_id: str = "inequality_operation_table",
    component_id: str | None = "src_4401",
    textbook_example_id: int | None = 4401,
) -> dict[str, Any]:
    rng = random.Random(f"{seed}|ineq_op_table|{component_id or ''}")
    # Prefer textbook-like positive > negative seed pair, then generalise.
    for _ in range(64):
        left0 = rng.randint(-12, 12)
        right0 = rng.randint(-12, 12)
        if left0 == right0:
            continue
        factor = rng.choice([2, 3, 4, 5, 6])
        if left0 % factor == 0 and right0 % factor == 0:
            break
    else:
        left0, right0, factor = 10, -5, 5

    left = Fraction(left0)
    right = Fraction(right0)
    ops = [
        ("兩邊同乘以", Fraction(factor), False),
        ("兩邊同乘以", Fraction(-factor), True),
        ("兩邊同除以", Fraction(factor), False),
        ("兩邊同除以", Fraction(-factor), True),
    ]

    parts: dict[str, str] = {}
    rows_tex: list[str] = []
    part_specs: list[dict[str, Any]] = []
    idx = 1
    for label, k, _flip in ops:
        new_l = left * k if "乘" in label else left / k
        new_r = right * k if "乘" in label else right / k
        # Division by negative k already flips via arithmetic; multiply too.
        cmp = _cmp_token(new_l, new_r)
        k_tex = _fmt_num(k) if k > 0 else f"\\left( {_fmt_num(k)} \\right)"
        rows_tex.append(f"{label}${k_tex}$")
        for key_suffix, value in (
            ("left", _fmt_num(new_l)),
            ("right", _fmt_num(new_r)),
            ("cmp", cmp),
        ):
            part_key = f"part_{idx}"
            parts[part_key] = value
            part_specs.append(
                {
                    "key": part_key,
                    "role": key_suffix,
                    "checker": "text_short_checker",
                    "checker_key": "text_short_checker",
                    "equivalence_type": "exact_string",
                    "answer": value,
                    "accepted_formats": [value],
                }
            )
            idx += 1

    seed_cmp = _cmp_token(left, right)
    stem = (
        f"已知 ${_fmt_num(left)} {seed_cmp} {_fmt_num(right)}$，完成下列表格。"
        f"對每一列依序填入：不等式左邊、不等式右邊、比較大小（$>$、$<$ 或 $=$）。"
        f"列依序為：" + "；".join(rows_tex) + "。"
    )
    explanation = (
        "同乘／同除以正數，不等號方向不變；同乘／同除以負數，不等號方向相反。"
        "逐列計算左右兩側數值後比較即可。"
    )
    answer_contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "presentation_mode": "short_answer",
        "parts": part_specs,
        "answer_format_example": "；".join(parts[f"part_{i}"] for i in range(1, 13)),
    }
    payload: dict[str, Any] = {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": stem,
        "question": stem,
        "choices": [],
        "answer": parts,
        "correct_answer": parts,
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "checker_type": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "answer_contract": answer_contract,
        "presentation_mode": "short_answer",
        "explanation": explanation,
        "metadata": {
            "givens": {
                "left0": left0,
                "right0": right0,
                "factor": factor,
                "seed_cmp": seed_cmp,
            },
            "target": "inequality_operation_table_12_cells",
            "template_slot": "inequality_operation_table",
            "textbook_fidelity_status": "NATIVE_COVERED",
        },
        "textbook_fidelity_status": "NATIVE_COVERED",
        "source_coverage_status": "COVERED_BY_NATIVE_GENERATOR",
        "bootstrap_mode": False,
        "source": "numberline_inequality_table",
        "seed": seed,
    }
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = int(textbook_example_id)
    return payload
