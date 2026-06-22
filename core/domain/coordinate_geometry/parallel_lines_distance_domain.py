"""Parallel lines distance domain — pure math, no skill_id branching."""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

from core.gencode.resources.rational_display import fraction_to_plain

_SUPPORTED_OPERATIONS = frozenset(
    {
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice",
        "area_using_parallel_distance",
    }
)


def _format_general_expression(a: int, b: int, c: int) -> str:
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x")
        elif a == -1:
            parts.append("-x")
        else:
            parts.append(f"{a}x")
    if b != 0:
        sign = "+" if b > 0 and parts else ""
        if b == 1:
            parts.append(f"{sign}y")
        elif b == -1:
            parts.append("-y")
        else:
            parts.append(f"{sign}{b}y")
    if c != 0:
        sign = "+" if c > 0 and parts else ""
        parts.append(f"{sign}{c}")
    return "".join(parts) if parts else "0"


def _format_general_form(a: int, b: int, c: int) -> str:
    return f"{_format_general_expression(a, b, c)} = 0"


def _parallel_distance(a: int, b: int, c1: int, c2: int) -> Fraction:
    denom = int(math.isqrt(a * a + b * b))
    return Fraction(abs(c1 - c2), denom)


def _empty_visual() -> dict[str, object]:
    return {
        "kind": "coordinate_plane_spec",
        "points": [],
        "lines": [],
        "x_range": [-8, 8],
        "y_range": [-8, 8],
    }


def _build_distance_between_parallel_lines(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    triples = [(3, 4), (5, 12), (3, 1), (2, 1), (1, 2)]
    a, b = rng.choice(triples)
    c1 = rng.randint(-10, 10)
    c2 = c1 + rng.choice([-8, -5, -3, 3, 5, 8])
    while c1 == c2:
        c2 = c1 + rng.choice([-5, 5])

    dist = _parallel_distance(a, b, c1, c2)
    canonical = fraction_to_plain(dist)
    givens = {
        "line_1": _format_general_form(a, b, c1),
        "line_2": _format_general_form(a, b, c2),
        "coefficients_line_1": {"A": a, "B": b, "C": c1},
        "coefficients_line_2": {"A": a, "B": b, "C": c2},
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c1},
        "distance": canonical,
        "value": canonical,
    }
    return givens, answer


def _build_solve_parameter_from_parallel_distance(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    # L1: 2x+4y-k=0, L2: x+2y+3=0 style — parallel lines, solve k given distance.
    a1, b1 = 2, 4
    a2, b2 = 1, 2
    c2 = rng.choice([-5, 3, 10])
    target_dist_sq = rng.choice([5, 10, 20, 40])
    target_dist = Fraction(math.isqrt(target_dist_sq), 1)
    denom = int(math.isqrt(a1 * a1 + b1 * b1))
    delta_c = int(target_dist * denom)
    k_pos = c2 + delta_c
    k_neg = c2 - delta_c
    sign_constraint = str(constraints.get("parameter_sign") or "").strip().lower()
    if sign_constraint == "negative":
        k_val = min(k_pos, k_neg)
        while k_val >= 0:
            k_val -= 1
    elif sign_constraint == "positive":
        k_val = max(k_pos, k_neg)
        while k_val <= 0:
            k_val += 1
    else:
        k_val = rng.choice([k_pos, k_neg])

    param_name = "k"
    givens = {
        "line_1": f"{_format_general_expression(a1, b1, 0)} - {param_name} = 0",
        "line_2": _format_general_form(a2, b2, c2),
        "target_distance": f"sqrt({target_dist_sq})",
        "parameter_name": param_name,
    }
    canonical = str(k_val)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a1, "B": b1, "C": -k_val},
        "distance": fraction_to_plain(target_dist),
        "parameter": canonical,
        "parameter_name": param_name,
        "value": canonical,
    }
    return givens, answer


def _build_area_using_parallel_distance(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    a, b, c = 3, -4, -1
    x0, y0 = 1, -2
    base_len = 3
    denom = int(math.isqrt(a * a + b * b))
    height = Fraction(abs(a * x0 + b * y0 + c), denom)
    area = Fraction(base_len, 2) * height
    canonical = fraction_to_plain(area)
    givens = {
        "point_a": [x0, y0],
        "line": _format_general_form(a, b, c),
        "segment_length": base_len,
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c},
        "distance": fraction_to_plain(height),
        "area": canonical,
        "value": canonical,
    }
    return givens, answer


def _build_parallel_lines_distance_single_choice(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], list[str]]:
    # ax+4y+k=0, slope 1/2, distance from origin sqrt(5) => a=2, k=-1 => a+k=1
    # Generate isomorphic variants with distractors.
    a = 2
    b = 4
    dist_sq = 5
    dist = Fraction(math.isqrt(dist_sq), 1)
    denom = int(math.isqrt(a * a + b * b))
    k = -rng.choice([1, 2, 3])
    canonical_sum = str(a + k)
    correct_label = rng.choice(["A", "B", "C", "D"])
    distractor_values = [str(a + k + d) for d in (2, 4, 6) if str(a + k + d) != canonical_sum]
    while len(distractor_values) < 3:
        distractor_values.append(str(int(canonical_sum) + len(distractor_values) + 3))
    choices_map = {correct_label: canonical_sum}
    labels = ["A", "B", "C", "D"]
    di = 0
    for label in labels:
        if label == correct_label:
            continue
        choices_map[label] = distractor_values[di]
        di += 1
    givens = {
        "line_expression": f"{a}x+{b}y+k=0",
        "slope": "1/2",
        "origin_distance": f"sqrt({dist_sq})",
        "parameter_name": "k",
    }
    answer = {
        "canonical_form": correct_label,
        "general_form": correct_label,
        "coefficients": {"A": a, "B": b, "C": k},
        "distance": fraction_to_plain(dist),
        "parameter": str(k),
        "parameter_name": "k",
        "sum_a_plus_k": canonical_sum,
        "correct_label": correct_label,
        "value": correct_label,
    }
    distractors = [v for lbl, v in choices_map.items() if lbl != correct_label]
    return givens, answer, distractors


def build_parallel_lines_distance_matrix(
    *,
    seed: int | None,
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
    line_type: str | None = None,  # legacy alias
) -> dict[str, object]:
    """Build Full Matrix Dictionary for parallel-lines distance operations."""
    op = str(domain_operation or line_type or "").strip()
    if op not in _SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported_domain_operation: {op!r}")

    rng = random.Random(0 if seed is None else seed)
    extra = dict(constraints or {})

    if op == "distance_between_parallel_lines":
        givens, answer = _build_distance_between_parallel_lines(rng, extra)
        distractors: list[str] = []
    elif op == "solve_parameter_from_parallel_distance":
        givens, answer = _build_solve_parameter_from_parallel_distance(rng, extra)
        distractors = []
    elif op == "construct_parallel_line_at_distance":
        givens, answer = _build_distance_between_parallel_lines(rng, extra)
        distractors = []
    elif op == "area_using_parallel_distance":
        givens, answer = _build_area_using_parallel_distance(rng, extra)
        distractors = []
    elif op == "parallel_lines_distance_single_choice":
        givens, answer, distractors = _build_parallel_lines_distance_single_choice(rng, extra)
    else:
        raise ValueError(f"unsupported_domain_operation: {op!r}")

    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": [
            "確認兩直線平行（法向量成比例）",
            "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
            "代入計算並化簡",
        ],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "visual_spec": _empty_visual(),
    }
