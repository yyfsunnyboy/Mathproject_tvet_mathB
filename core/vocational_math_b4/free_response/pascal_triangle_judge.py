# -*- coding: utf-8 -*-
"""B4 Pascal triangle handwriting payload helpers."""

from __future__ import annotations

from math import comb
from typing import Any


PROBLEM_TYPE_ID = "pascal_triangle_handwriting"
GRADING_MODE = "ai_judged_free_response"
SKILL_ID = "vh_數學B4_PascalTriangle"


def pascal_row(n: int) -> list[int]:
    n_int = int(n)
    if n_int < 0:
        raise ValueError("n must be >= 0")
    return [comb(n_int, k) for k in range(n_int + 1)]


def _term_text(coefficient: int, x_power: int, y_power: int) -> str:
    parts: list[str] = []
    if coefficient != 1 or (x_power == 0 and y_power == 0):
        parts.append(str(coefficient))
    if x_power > 0:
        parts.append("x" if x_power == 1 else f"x^{x_power}")
    if y_power > 0:
        parts.append("y" if y_power == 1 else f"y^{y_power}")
    return "".join(parts) or "1"


def build_binomial_expansion_terms(n: int, sign: str = "+") -> list[dict[str, Any]]:
    n_int = int(n)
    normalized_sign = "-" if str(sign).strip() == "-" else "+"
    terms: list[dict[str, Any]] = []
    for k in range(n_int + 1):
        base_coef = comb(n_int, k)
        term_sign = "+"
        if normalized_sign == "-" and (k % 2 == 1):
            term_sign = "-"
        terms.append(
            {
                "coefficient": int(base_coef),
                "x_power": int(n_int - k),
                "y_power": int(k),
                "sign": term_sign,
                "text_term": _term_text(int(base_coef), int(n_int - k), int(k)),
            }
        )
    return terms


def _render_expected_expansion(terms: list[dict[str, Any]]) -> str:
    out: list[str] = []
    for idx, term in enumerate(terms):
        sign = term.get("sign", "+")
        text_term = str(term.get("text_term") or "")
        if idx == 0:
            out.append(text_term if sign == "+" else f"-{text_term}")
        else:
            out.append(f" {sign} {text_term}")
    return "".join(out).strip()


def build_pascal_triangle_payload(variant: str, index: int | None = None) -> dict[str, Any]:
    normalized_variant = str(variant or "").strip()
    idx = int(index or 0)
    if normalized_variant == "pascal_row_listing":
        row_cycle = [3, 4, 5]
        n = row_cycle[idx % len(row_cycle)]
        return {
            "problem_type_id": PROBLEM_TYPE_ID,
            "skill_id": SKILL_ID,
            "answer_type": "handwriting",
            "grading_mode": GRADING_MODE,
            "variant": normalized_variant,
            "question_text": (
                f"已知巴斯卡三角形第 0 列為 1，第 1 列為 1, 1，第 2 列為 1, 2, 1。"
                f"請寫出第 {n} 列的各項數字。"
            ),
            "n": n,
            "expected_row": pascal_row(n),
            "expected_terms": [],
            "expected_expansion": "",
        }
    if normalized_variant == "pascal_binomial_expansion":
        config_cycle = [
            (3, "+"),
            (4, "-"),
            (5, "+"),
            (2, "-"),
        ]
        n, sign = config_cycle[idx % len(config_cycle)]
        expr = f"(x{sign}y)^{n}".replace("+-", "-")
        terms = build_binomial_expansion_terms(n=n, sign=sign)
        return {
            "problem_type_id": PROBLEM_TYPE_ID,
            "skill_id": SKILL_ID,
            "answer_type": "handwriting",
            "grading_mode": GRADING_MODE,
            "variant": normalized_variant,
            "question_text": (
                "已知巴斯卡三角形第 0 列為 1，第 1 列為 1, 1，第 2 列為 1, 2, 1。"
                f"請利用巴斯卡三角形展開 ${expr}$。"
            ),
            "n": n,
            "expected_row": [],
            "expected_terms": terms,
            "expected_expansion": _render_expected_expansion(terms),
        }
    raise ValueError(f"Unsupported Pascal variant: {variant}")
