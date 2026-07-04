"""Isolated implementation candidate for a graph/intercepts/line-equation operation."""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any


def _fraction(value: object, field: str) -> Fraction:
    if isinstance(value, bool):
        raise ValueError(f"{field}_must_be_rational")
    try:
        result = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{field}_must_be_rational") from exc
    return result


def _plain(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _signed_term(coefficient: Fraction, variable: str, *, first: bool) -> str:
    if coefficient == 0:
        return ""
    sign = "-" if coefficient < 0 else ("" if first else "+")
    magnitude = abs(coefficient)
    coefficient_text = "" if magnitude == 1 else _plain(magnitude)
    return f"{sign}{coefficient_text}{variable}"


def _affine_expression(slope: Fraction, intercept: Fraction) -> str:
    expression = _signed_term(slope, "x", first=True)
    if intercept:
        sign = "+" if intercept > 0 and expression else ""
        expression += f"{sign}{_plain(intercept)}"
    return expression or "0"


def _axis_range(
    x_intercept: Fraction | None,
    y_intercept: Fraction | None,
) -> dict[str, int]:
    x_values = [Fraction(-2), Fraction(2)]
    y_values = [Fraction(-2), Fraction(2)]
    if x_intercept is not None:
        x_values.extend([x_intercept - 2, x_intercept + 2])
    if y_intercept is not None:
        y_values.extend([y_intercept - 2, y_intercept + 2])
    return {
        "x_min": min(value.numerator // value.denominator for value in x_values),
        "x_max": max(-((-value.numerator) // value.denominator) for value in x_values),
        "y_min": min(value.numerator // value.denominator for value in y_values),
        "y_max": max(-((-value.numerator) // value.denominator) for value in y_values),
    }


def _coefficients(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[Fraction, Fraction, Fraction]:
    supplied = constraints.get("coefficients")
    if supplied is not None:
        if not isinstance(supplied, (list, tuple)) or len(supplied) != 3:
            raise ValueError("coefficients_must_be_A_B_C")
        return tuple(
            _fraction(value, field)
            for value, field in zip(supplied, ("A", "B", "C"))
        )

    line_kind = str(constraints.get("line_kind") or "oblique").strip().lower()
    if line_kind not in {"oblique", "horizontal", "vertical", "random"}:
        raise ValueError("unsupported_line_kind")
    if line_kind == "random":
        line_kind = rng.choice(["oblique", "horizontal", "vertical"])

    if line_kind == "oblique":
        if "x_intercept" in constraints or "y_intercept" in constraints:
            x_intercept = _fraction(constraints.get("x_intercept"), "x_intercept")
            y_intercept = _fraction(constraints.get("y_intercept"), "y_intercept")
        else:
            nonzero = [value for value in range(-8, 9) if value]
            x_intercept = Fraction(rng.choice(nonzero))
            y_intercept = Fraction(rng.choice(nonzero))
        if x_intercept == 0 or y_intercept == 0:
            raise ValueError("oblique_intercepts_must_be_nonzero")
        return y_intercept, x_intercept, -(x_intercept * y_intercept)

    offset = _fraction(
        constraints.get("axis_offset", rng.choice([value for value in range(-8, 9) if value])),
        "axis_offset",
    )
    if offset == 0:
        raise ValueError("axis_coincident_line_is_degenerate")
    if line_kind == "horizontal":
        return Fraction(0), Fraction(1), -offset
    return Fraction(1), Fraction(0), -offset


def build_graph_intercepts_and_linear_equation_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a graph-reading matrix for a non-degenerate line."""
    normalized_constraints = dict(constraints or {})
    rng = random.Random(seed)
    coefficient_a, coefficient_b, coefficient_c = _coefficients(rng, normalized_constraints)
    if coefficient_a == 0 and coefficient_b == 0:
        raise ValueError("invalid_line_zero_normal")

    x_intercept = (
        -coefficient_c / coefficient_a if coefficient_a != 0 else None
    )
    y_intercept = (
        -coefficient_c / coefficient_b if coefficient_b != 0 else None
    )
    if coefficient_a == 0 and y_intercept == 0:
        raise ValueError("axis_coincident_line_is_degenerate")
    if coefficient_b == 0 and x_intercept == 0:
        raise ValueError("axis_coincident_line_is_degenerate")

    if coefficient_b == 0:
        slope: Fraction | None = None
        equation = f"x={_plain(x_intercept)}"
        graph_kind = "vertical"
    else:
        slope = -coefficient_a / coefficient_b
        intercept = -coefficient_c / coefficient_b
        expression = _affine_expression(slope, intercept)
        equation = f"f(x)={expression}"
        graph_kind = "horizontal" if slope == 0 else "oblique"

    canonical_answer = {
        "x_intercept": _plain(x_intercept) if x_intercept is not None else None,
        "y_intercept": _plain(y_intercept) if y_intercept is not None else None,
        "function_equation": equation if graph_kind != "vertical" else None,
        "line_equation": equation,
    }
    points: list[list[str]] = []
    if x_intercept is not None:
        points.append([_plain(x_intercept), "0"])
    if y_intercept is not None:
        point = ["0", _plain(y_intercept)]
        if point not in points:
            points.append(point)

    visual_spec = {
        "kind": "coordinate_line_graph",
        "drawable_primitives": [
            {
                "type": "line",
                "equation": {
                    "A": _plain(coefficient_a),
                    "B": _plain(coefficient_b),
                    "C": _plain(coefficient_c),
                },
            },
            {"type": "axes"},
        ],
        "axis_range": _axis_range(x_intercept, y_intercept),
        "labels": {
            "x_axis": "x",
            "y_axis": "y",
            "line": "y=f(x)" if graph_kind != "vertical" else equation,
        },
        "points": points,
    }
    requested = ["x_intercept", "y_intercept", "function_equation"]
    if graph_kind == "vertical":
        requested = ["x_intercept", "y_intercept", "line_equation"]

    return {
        "givens": {
            "graph_type": "linear_function" if graph_kind != "vertical" else "linear_relation",
            "coefficients": {
                "A": _plain(coefficient_a),
                "B": _plain(coefficient_b),
                "C": _plain(coefficient_c),
            },
            "points": points,
        },
        "answer": {
            "canonical_form": canonical_answer,
            "general_form": {
                "A": _plain(coefficient_a),
                "B": _plain(coefficient_b),
                "C": _plain(coefficient_c),
            },
            "coefficients": {
                "A": _plain(coefficient_a),
                "B": _plain(coefficient_b),
                "C": _plain(coefficient_c),
            },
        },
        "distractors": [],
        "explanation_steps": [
            "Read each finite axis intercept from the graph.",
            "Use the line coefficients to derive the canonical equation.",
        ],
        "validation_facts": {
            "line_kind": graph_kind,
            "slope": _plain(slope) if slope is not None else None,
            "x_intercept": canonical_answer["x_intercept"],
            "y_intercept": canonical_answer["y_intercept"],
            "equation": equation,
        },
        "visual_spec": visual_spec,
        "question": "依圖回答：(1) 求 x、y 截距；(2) 求此直線的方程式。",
        "semantic_answer": canonical_answer,
        "answer_type": "multi_part",
        "presentation_mode": "graph_multi_part",
        "topology_tags": [
            "graph_reading",
            "two_axis_intercepts",
            "equation_from_graph",
            "multi_part",
        ],
        "requested": requested,
    }
