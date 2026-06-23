"""Parallel lines distance domain: pure math, no skill_id branching."""

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


def _expr_text(value: Any) -> str:
    import sympy

    return str(sympy.simplify(value))


def _normalize_line(a: int, b: int, c: int) -> tuple[int, int, Fraction]:
    gcd_ab = math.gcd(abs(a), abs(b))
    if gcd_ab == 0:
        raise ValueError("invalid_line_coefficients")
    if a < 0 or (a == 0 and b < 0):
        gcd_ab = -gcd_ab
    return a // gcd_ab, b // gcd_ab, Fraction(c, gcd_ab)


def _parallel_distance_expr(a1: int, b1: int, c1: int, a2: int, b2: int, c2: int) -> Any:
    import sympy

    na1, nb1, nc1 = _normalize_line(a1, b1, c1)
    na2, nb2, nc2 = _normalize_line(a2, b2, c2)
    if (na1, nb1) != (na2, nb2):
        raise ValueError("lines_are_not_parallel_after_normalization")
    if nc1 == nc2:
        raise ValueError("parallel_lines_are_coincident")
    c1_expr = sympy.Rational(nc1.numerator, nc1.denominator)
    c2_expr = sympy.Rational(nc2.numerator, nc2.denominator)
    return sympy.simplify(sympy.Abs(c1_expr - c2_expr) / sympy.sqrt(na1 * na1 + nb1 * nb1))


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
    normal_pairs = [(3, 4), (5, 12), (3, 1), (2, 1), (1, 2), (1, -2), (2, -3)]
    a, b = rng.choice(normal_pairs)
    c1 = rng.randint(-10, 10)
    c2 = c1 + rng.choice([-8, -5, -3, 3, 5, 8])
    scale = rng.choice([-3, -2, -1, 1, 2, 3])
    a2, b2, c2_scaled = a * scale, b * scale, c2 * scale

    dist = _parallel_distance_expr(a, b, c1, a2, b2, c2_scaled)
    canonical = _expr_text(dist)
    givens = {
        "line_1": _format_general_form(a, b, c1),
        "line_2": _format_general_form(a2, b2, c2_scaled),
        "coefficients_line_1": {"A": a, "B": b, "C": c1},
        "coefficients_line_2": {"A": a2, "B": b2, "C": c2_scaled},
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
    import sympy

    a1, b1 = 2, 4
    a2, b2 = 1, 2
    c2 = rng.choice([-5, 3, 10])
    target_dist_sq = rng.choice([5, 10, 20, 40])
    target_distance = sympy.sqrt(target_dist_sq)

    norm_a1, norm_b1, _ = _normalize_line(a1, b1, 0)
    g1 = abs(math.gcd(a1, b1))
    _, _, normalized_c2 = _normalize_line(a2, b2, c2)
    normalized_c2_expr = sympy.Rational(normalized_c2.numerator, normalized_c2.denominator)
    center = sympy.simplify(-g1 * normalized_c2_expr)
    delta_c = sympy.simplify(g1 * target_distance * sympy.sqrt(norm_a1 * norm_a1 + norm_b1 * norm_b1))
    lower = sympy.simplify(center - delta_c)
    upper = sympy.simplify(center + delta_c)

    branch = str(constraints.get("parameter_branch") or rng.choice(["upper", "lower"])).strip().lower()
    if branch == "upper":
        k_val = upper
        condition = f"k > {_expr_text(center)}"
    else:
        k_val = lower
        condition = f"k < {_expr_text(center)}"

    param_name = "k"
    canonical = _expr_text(k_val)
    givens = {
        "line_1": f"{_format_general_expression(a1, b1, 0)} - {param_name} = 0",
        "line_2": _format_general_form(a2, b2, c2),
        "target_distance": _expr_text(target_distance),
        "parameter_name": param_name,
        "parameter_condition": condition,
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a1, "B": b1, "C": canonical},
        "distance": _expr_text(target_distance),
        "parameter": canonical,
        "parameter_name": param_name,
        "parameter_condition": condition,
        "value": canonical,
    }
    return givens, answer


def _build_area_using_parallel_distance(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    import sympy

    a, b = rng.choice([(3, -4), (5, 12), (3, 1), (2, 1), (1, 2), (1, -1)])
    c = rng.randint(-10, 10)
    x0, y0 = rng.randint(-6, 6), rng.randint(-6, 6)
    while a * x0 + b * y0 + c == 0:
        x0, y0 = rng.randint(-6, 6), rng.randint(-6, 6)
    base_len = rng.randint(2, 8)
    height = sympy.simplify(sympy.Abs(a * x0 + b * y0 + c) / sympy.sqrt(a * a + b * b))
    area = sympy.simplify(sympy.Rational(base_len, 2) * height)
    canonical = _expr_text(area)
    givens = {
        "point_a": [x0, y0],
        "line": _format_general_form(a, b, c),
        "segment_length": base_len,
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c},
        "distance": _expr_text(height),
        "area": canonical,
        "value": canonical,
    }
    return givens, answer


def _build_parallel_lines_distance_single_choice(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], list[str]]:
    import sympy

    a = rng.choice([1, 2, 3])
    b = 2 * a
    k = rng.choice([2, 3, 4, 5])
    slope = Fraction(-1, 2)
    distance = sympy.simplify(sympy.Rational(k, 1) / sympy.sqrt(a * a + b * b))
    correct_value = a + k
    canonical_sum = str(correct_value)
    correct_label = rng.choice(["A", "B", "C", "D"])
    distractor_values = [str(correct_value + d) for d in (-3, -2, -1, 1, 2, 3) if correct_value + d > 0]
    rng.shuffle(distractor_values)
    while len(distractor_values) < 3:
        distractor_values.append(str(correct_value + len(distractor_values) + 3))

    choices_map = {correct_label: canonical_sum}
    labels = ["A", "B", "C", "D"]
    di = 0
    for label in labels:
        if label == correct_label:
            continue
        choices_map[label] = distractor_values[di]
        di += 1

    givens = {
        "line_expression": "ax+2ay+k=0",
        "slope": fraction_to_plain(slope),
        "origin_distance": _expr_text(distance),
        "parameter_name": "k",
        "a_value": a,
        "b_value": b,
    }
    answer = {
        "canonical_form": correct_label,
        "general_form": correct_label,
        "coefficients": {"A": a, "B": b, "C": k},
        "distance": _expr_text(distance),
        "parameter": str(k),
        "parameter_name": "k",
        "sum_a_plus_k": canonical_sum,
        "correct_label": correct_label,
        "choices": [{"label": label, "text": text} for label, text in sorted(choices_map.items())],
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
    line_type: str | None = None,
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
            "Normalize proportional parallel-line equations to the same A and B.",
            "Use distance |C1-C2|/sqrt(A^2+B^2) after normalization.",
            "For parameter problems, solve the absolute-value equation and apply the stated branch condition.",
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
