# -*- coding: utf-8 -*-
"""Shared exact operations for positive similar-triangle proportions."""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any


OPERATION = "solve_similar_triangle_proportion"


def _positive_fraction(value: Any, *, name: str) -> Fraction:
    try:
        result = value if isinstance(value, Fraction) else Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name}_must_be_rational") from exc
    if result <= 0:
        raise ValueError(f"{name}_must_be_positive")
    return result


def canonical_rational(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def solve_proportion(terms: list[Any | None] | tuple[Any | None, ...]) -> Fraction:
    """Solve a/b=c/d when exactly one positive term is unknown."""
    if not isinstance(terms, (list, tuple)) or len(terms) != 4:
        raise ValueError("proportion_requires_four_terms")
    missing = [index for index, value in enumerate(terms) if value is None]
    if len(missing) != 1:
        raise ValueError("proportion_requires_exactly_one_unknown")
    values = [None if value is None else _positive_fraction(value, name=f"term_{i}") for i, value in enumerate(terms)]
    index = missing[0]
    a, b, c, d = values
    if index == 0:
        result = b * c / d
    elif index == 1:
        result = a * d / c
    elif index == 2:
        result = a * d / b
    else:
        result = b * c / a
    return _positive_fraction(result, name="solution")


def build_geometry_similarity_matrix(
    *,
    seed: int | None,
    line_type: str | None = None,
    domain_operation: str | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    op = str(domain_operation or line_type or "").strip()
    if op != OPERATION:
        raise ValueError(f"Unsupported geometry.similarity operation: {op!r}")
    rng = random.Random(0 if seed is None else seed)
    data = dict(constraints or {})
    terms = data.get("terms")
    if terms is None:
        small_a, small_b = rng.choice(((3, 4), (4, 5), (5, 8), (6, 7)))
        scale = rng.choice((2, 3, 4))
        terms = [small_a, small_b, small_a * scale, None]
    solution = solve_proportion(terms)
    unknown_index = list(terms).index(None)
    canonical = canonical_rational(solution)
    names = ("a", "b", "c", "d")
    shown = ["x" if value is None else canonical_rational(_positive_fraction(value, name=names[i])) for i, value in enumerate(terms)]
    question = f"已知兩個相似三角形的對應邊滿足 {shown[0]}/{shown[1]}={shown[2]}/{shown[3]}，求 x。"
    return {
        "givens": {
            "question_text": question,
            "proportion_terms": list(terms),
            "unknown_index": unknown_index,
        },
        "answer": {
            "canonical_form": canonical,
            "general_form": canonical,
            "coefficients": [],
            "value": canonical,
        },
        "distractors": [],
        "explanation_steps": ["相似三角形的對應邊成比例。", "以交叉相乘解出唯一未知正邊長。"],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "ratio_invariant": True,
        },
        "visual_spec": {"kind": "none", "points": [], "lines": []},
        "question_text": question,
        "question": question,
    }


def validate_similarity_matrix(matrix: dict[str, Any]) -> bool:
    try:
        givens = matrix["givens"]
        expected = solve_proportion(givens["proportion_terms"])
        actual = Fraction(str(matrix["answer"]["canonical_form"]))
        terms = list(givens["proportion_terms"])
        terms[int(givens["unknown_index"])] = actual
        a, b, c, d = (_positive_fraction(v, name="term") for v in terms)
        return actual == expected and a * d == b * c
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False
