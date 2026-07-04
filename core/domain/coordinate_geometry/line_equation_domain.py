"""Line equation domain operators — pure math, no administrative coupling."""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

from core.gencode.resources.rational_display import (
    fraction_to_plain,
    normalize_fraction_value,
    normalize_linear_expression_display,
)

_SUPPORTED_LINE_TYPES = frozenset(
    {
        "two_points",
        "point_slope",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
        "slope_intercept_equation",
        "slope_intercept_find_x_intercept",
        "slope_intercept_read_slope_and_intercept",
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
        # New V3 General Form types:
        "slope_from_general_or_intercept_form",
        "slope_from_general_form",
        "slope_of_horizontal_or_vertical_line",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "parallel_line_slope",
        "perpendicular_line_slope",
        "parallel_condition_parameter",
        "perpendicular_condition_parameter",
        "compare_line_slopes",
        "line_through_intersection_parallel_to_line",
        "line_through_point_perpendicular_to_segment",
        "perpendicular_bisector_application",
        "coordinate_geometry_word_problem",
        # New distance V3 types:
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances", "graph_intercepts_and_linear_equation",
        "draw_constant_function_graph",
        "draw_linear_function_graph",
        "graph_based_linear_application_inverse",
        "linear_equation_from_two_points_choice",
        "linear_graph_feasibility_choice",
        "graph_based_linear_model_equation",
        "robust_budget_feasibility_choice",
    }
)


def build_line_equation_matrix(
    *,
    seed: int | None,
    line_type: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a full problem matrix for a line-equation scenario."""
    normalized_type = str(line_type or "").strip()
    if normalized_type == "graph_intercepts_and_linear_equation":
        return build_graph_intercepts_and_linear_equation_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "draw_constant_function_graph":
        return build_draw_constant_function_graph_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "draw_linear_function_graph":
        return build_draw_linear_function_graph_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "graph_based_linear_application_inverse":
        return build_graph_based_linear_application_inverse_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "linear_equation_from_two_points_choice":
        return build_linear_equation_from_two_points_choice_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "linear_graph_feasibility_choice":
        return build_linear_graph_feasibility_choice_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "graph_based_linear_model_equation":
        return build_graph_based_linear_model_equation_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type == "robust_budget_feasibility_choice":
        return build_robust_budget_feasibility_choice_matrix(
            seed=seed,
            constraints=constraints,
        )
    if normalized_type not in _SUPPORTED_LINE_TYPES:
        raise ValueError(f"Unsupported line_type: {line_type!r}")

    rng = random.Random(0 if seed is None else seed)
    profile = str(curriculum_profile or "").strip()
    difficulty = str(difficulty_profile or "").strip()
    extra = dict(constraints or {})

    coord_min, coord_max = _resolve_coord_bounds(profile, difficulty, extra)
    x_range, y_range = _resolve_visual_ranges(profile, difficulty, extra)

    if normalized_type == "two_points":
        givens, answer, actual_type = _build_two_points(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "point_slope":
        givens, answer, actual_type = _build_point_slope(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "horizontal_line":
        givens, answer, actual_type = _build_horizontal_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "vertical_line":
        givens, answer, actual_type = _build_vertical_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "slope_intercept_equation":
        givens, answer, actual_type = _build_slope_intercept_equation(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "slope_intercept_find_x_intercept":
        givens, answer, actual_type = _build_slope_intercept_find_x_intercept(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "slope_intercept_read_slope_and_intercept":
        givens, answer, actual_type = _build_slope_intercept_read_slope_and_intercept(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type in {
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
    }:
        givens, answer, actual_type = _build_intercept_form_problem(
            rng,
            coord_min,
            coord_max,
            extra,
            task_type=normalized_type,
        )
    elif normalized_type == "slope_from_general_or_intercept_form":
        givens, answer, actual_type = _build_slope_from_general_or_intercept_form(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "slope_from_general_form":
        givens, answer, actual_type = _build_slope_from_general_form(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "slope_of_horizontal_or_vertical_line":
        givens, answer, actual_type = _build_slope_of_horizontal_or_vertical_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "line_through_point_parallel_to_line":
        givens, answer, actual_type = _build_line_through_point_parallel_to_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "line_through_point_perpendicular_to_line":
        givens, answer, actual_type = _build_line_through_point_perpendicular_to_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "parallel_line_slope":
        givens, answer, actual_type = _build_parallel_line_slope(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "perpendicular_line_slope":
        givens, answer, actual_type = _build_perpendicular_line_slope(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "parallel_condition_parameter":
        givens, answer, actual_type = _build_parallel_condition_parameter(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "perpendicular_condition_parameter":
        givens, answer, actual_type = _build_perpendicular_condition_parameter(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "compare_line_slopes":
        givens, answer, actual_type = _build_compare_line_slopes(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "line_through_intersection_parallel_to_line":
        givens, answer, actual_type = _build_line_through_intersection_parallel_to_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "line_through_point_perpendicular_to_segment":
        givens, answer, actual_type = _build_line_through_point_perpendicular_to_segment(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "perpendicular_bisector_application" or normalized_type == "coordinate_geometry_word_problem":
        givens, answer, actual_type = _build_perpendicular_bisector_application(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "distance_from_point_to_line":
        givens, answer, actual_type = _build_distance_from_point_to_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "distance_from_point_to_line_parameter":
        givens, answer, actual_type = _build_distance_from_point_to_line_parameter(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "distance_from_point_to_line_parameter_single_choice_scalar":
        givens, answer, actual_type = _build_distance_from_point_to_line_parameter_single_choice_scalar(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "compare_point_to_line_distances":
        givens, answer, actual_type = _build_compare_point_to_line_distances(
            rng, coord_min, coord_max, extra
        )
    else:
        givens, answer, actual_type = _build_oblique_line(
            rng, coord_min, coord_max, extra
        )

    coeffs = answer["coefficients"]
    assert isinstance(coeffs, dict)
    a_int = int(coeffs["A"])
    b_int = int(coeffs["B"])
    c_int = int(coeffs["C"])

    if "general_form" not in answer:
        answer["general_form"] = _format_general_form(a_int, b_int, c_int)

    validation_facts: dict[str, object] = {
        "line_type": actual_type,
        "coefficients": {"A": a_int, "B": b_int, "C": c_int},
        "is_vertical": actual_type == "vertical_line",
        "is_horizontal": actual_type == "horizontal_line",
        "task_type": normalized_type,
        "points_satisfy_line": _collect_points_on_line(givens, a_int, b_int, c_int),
    }

    visual_spec = _build_visual_spec(
        givens=givens,
        answer=answer,
        actual_type=actual_type,
        x_range=x_range,
        y_range=y_range,
    )
    distractors = _build_distractors(
        rng=rng,
        answer=answer,
        actual_type=actual_type,
        givens=givens,
        coord_min=coord_min,
        coord_max=coord_max,
        task_type=normalized_type,
    )
    explanation_steps = _build_explanation_steps(
        line_type=normalized_type,
        actual_type=actual_type,
        givens=givens,
        answer=answer,
    )

    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": explanation_steps,
        "validation_facts": validation_facts,
        "visual_spec": visual_spec,
    }


def _resolve_coord_bounds(
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object],
) -> tuple[int, int]:
    if curriculum_profile == "vocational_high_b":
        lo, hi = -8, 8
    else:
        lo, hi = -6, 6

    if difficulty_profile in {"hard", "advanced"}:
        lo, hi = lo - 2, hi + 2
    elif difficulty_profile in {"easy", "basic"}:
        lo, hi = max(lo, -6), min(hi, 6)

    if "coord_min" in constraints:
        lo = int(constraints["coord_min"])  # type: ignore[arg-type]
    if "coord_max" in constraints:
        hi = int(constraints["coord_max"])  # type: ignore[arg-type]
    return lo, hi


def _resolve_visual_ranges(
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object],
) -> tuple[list[int], list[int]]:
    lo, hi = _resolve_coord_bounds(curriculum_profile, difficulty_profile, constraints)
    margin = 2 if difficulty_profile in {"hard", "advanced"} else 0
    x_range = [lo - margin, hi + margin]
    y_range = [lo - margin, hi + margin]
    if isinstance(constraints.get("x_range"), list) and len(constraints["x_range"]) == 2:
        x_range = [int(constraints["x_range"][0]), int(constraints["x_range"][1])]  # type: ignore[index]
    if isinstance(constraints.get("y_range"), list) and len(constraints["y_range"]) == 2:
        y_range = [int(constraints["y_range"][0]), int(constraints["y_range"][1])]  # type: ignore[index]
    return x_range, y_range


def _pick_slope(rng: random.Random, *, allow_fraction: bool = True) -> Fraction:
    if allow_fraction and rng.random() < 0.35:
        numerators = [1, 2, 3, -1, -2, -3]
        denominators = [2, 3]
        slope = Fraction(rng.choice(numerators), rng.choice(denominators))
        if slope == 0:
            return Fraction(1, 2)
        return slope
    candidates = [i for i in range(-5, 6) if i != 0]
    return Fraction(rng.choice(candidates), 1)


def _build_two_points(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_pair(constraints):
        x1, y1, x2, y2 = _read_point_pair(constraints)
    else:
        for _ in range(200):
            x1 = rng.randint(coord_min, coord_max)
            y1 = rng.randint(coord_min, coord_max)
            x2 = rng.randint(coord_min, coord_max)
            y2 = rng.randint(coord_min, coord_max)
            if x1 != x2 or y1 != y2:
                break
        else:
            x1, y1, x2, y2 = -3, 1, 2, 4

    givens: dict[str, object] = {
        "point_a": [x1, y1],
        "point_b": [x2, y2],
    }

    if x1 == x2:
        answer, actual_type = _line_from_vertical(x1)
    elif y1 == y2:
        answer, actual_type = _line_from_horizontal(y1)
    else:
        slope = Fraction(y2 - y1, x2 - x1)
        answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _build_point_slope(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_and_slope(constraints):
        x1, y1, slope = _read_point_and_slope(constraints)
        if slope is None:
            raise ValueError("point_slope requires a non-vertical slope.")
    else:
        x1 = rng.randint(coord_min, coord_max)
        y1 = rng.randint(coord_min, coord_max)
        slope = _pick_slope(rng)

    if slope is None:
        raise ValueError("point_slope cannot produce a vertical line.")

    givens: dict[str, object] = {
        "point": [x1, y1],
        "slope": _format_number(slope),
    }
    answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _build_horizontal_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if "y_intercept" in constraints:
        y_val = int(constraints["y_intercept"])  # type: ignore[arg-type]
    elif "k" in constraints:
        y_val = int(constraints["k"])  # type: ignore[arg-type]
    else:
        y_val = rng.randint(coord_min, coord_max)

    x1 = rng.randint(coord_min, coord_max)
    for _ in range(200):
        x2 = rng.randint(coord_min, coord_max)
        if x2 != x1:
            break
    else:
        x2 = x1 + 1 if x1 < coord_max else x1 - 1

    givens: dict[str, object] = {
        "point_a": [x1, y_val],
        "point_b": [x2, y_val],
    }
    answer, actual_type = _line_from_horizontal(y_val)
    return givens, answer, actual_type


def _build_vertical_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if "x_intercept" in constraints:
        x_val = int(constraints["x_intercept"])  # type: ignore[arg-type]
    elif "k" in constraints:
        x_val = int(constraints["k"])  # type: ignore[arg-type]
    else:
        x_val = rng.randint(coord_min, coord_max)

    y1 = rng.randint(coord_min, coord_max)
    for _ in range(200):
        y2 = rng.randint(coord_min, coord_max)
        if y2 != y1:
            break
    else:
        y2 = y1 + 1 if y1 < coord_max else y1 - 1

    givens: dict[str, object] = {
        "point_a": [x_val, y1],
        "point_b": [x_val, y2],
    }
    answer, actual_type = _line_from_vertical(x_val)
    return givens, answer, actual_type


def _build_oblique_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_and_slope(constraints):
        x1, y1, slope = _read_point_and_slope(constraints)
        if slope is None or slope == 0:
            raise ValueError("oblique_line requires a non-zero, non-vertical slope.")
    else:
        x1 = rng.randint(coord_min, coord_max)
        y1 = rng.randint(coord_min, coord_max)
        slope = _pick_slope(rng, allow_fraction=True)
        while slope == 0:
            slope = _pick_slope(rng, allow_fraction=True)

    givens: dict[str, object] = {
        "point": [x1, y1],
        "slope": _format_number(slope),
    }
    answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _build_slope_intercept_equation(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    _ = constraints
    slope = _pick_nonzero_slope_intercept_slope(rng)
    y_intercept = _pick_slope_intercept_b(rng, coord_min, coord_max)
    answer, _ = _line_from_slope_intercept(slope, y_intercept)
    givens: dict[str, object] = {
        "slope": _format_number(slope),
        "y_intercept": _format_number(y_intercept),
    }
    return givens, answer, "slope_intercept_equation"


def _build_slope_intercept_find_x_intercept(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    _ = constraints
    slope = _pick_nonzero_slope_intercept_slope(rng)
    y_intercept = _pick_slope_intercept_b(rng, coord_min, coord_max, allow_zero=False)
    if y_intercept == 0:
        y_intercept = Fraction(2, 1)
    line_answer, _ = _line_from_slope_intercept(slope, y_intercept)
    x_intercept = -y_intercept / slope
    answer = dict(line_answer)
    answer["canonical_form"] = _format_number(x_intercept)
    answer["x_intercept"] = _format_number(x_intercept)
    answer["line_equation"] = line_answer["canonical_form"]
    givens: dict[str, object] = {
        "slope": _format_number(slope),
        "y_intercept": _format_number(y_intercept),
    }
    return givens, answer, "slope_intercept_find_x_intercept"


def _build_slope_intercept_read_slope_and_intercept(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    _ = constraints
    slope = _pick_nonzero_slope_intercept_slope(rng)
    y_intercept = _pick_slope_intercept_b(rng, coord_min, coord_max)
    answer, _ = _line_from_slope_intercept(slope, y_intercept)
    answer = dict(answer)
    answer["canonical_form"] = (
        f"m = {_format_number(slope)}, b = {_format_number(y_intercept)}"
    )
    answer["line_equation"] = _format_slope_intercept(slope, y_intercept)
    givens: dict[str, object] = {
        "equation": answer["line_equation"],
    }
    return givens, answer, "slope_intercept_read_slope_and_intercept"


def _build_intercept_form_problem(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
    *,
    task_type: str,
) -> tuple[dict[str, object], dict[str, object], str]:
    if task_type == "triangle_area_bisector_line_equation":
        built = build_triangle_area_bisector_line(
            constraints.get("vertex"),
            constraints.get("edge_p1"),
            constraints.get("edge_p2"),
        )
        givens = {
            "vertex": built["vertex"],
            "edge_p1": built["edge_p1"],
            "edge_p2": built["edge_p2"],
            "midpoint": built["midpoint"],
        }
        answer = {
            "canonical_form": built["general_form"],
            "general_form": built["general_form"],
            "display_equation": built["display_equation"],
            "coefficients": built["coefficients"],
            "slope": built["slope"],
            "intercept": built["intercept"],
            "line_equation": built["general_form"],
            "midpoint": built["midpoint"],
        }
        return givens, answer, task_type

    if task_type == "parabola_secant_parallel_line_choice":
        p = _parse_fraction(constraints.get("p"))
        q = _parse_fraction(constraints.get("q"))
        choices = constraints.get("choices")
        if not isinstance(choices, list):
            raise ValueError("unsupported_choices_generator:parabola_secant_choices_missing")
        built = build_parabola_secant_parallel_line_choice(p, q, choices)
        givens = {
            "parabola": "y = x^2",
            "p": _format_number(p),
            "q": _format_number(q),
            "choices": built["choices"],
        }
        answer = {
            "canonical_form": built["semantic_answer"],
            "general_form": _format_general_form(*_normalize_fraction_coefficients(_parse_fraction(built["slope"]), Fraction(-1, 1), Fraction(0, 1))),
            "coefficients": dict(zip(("A", "B", "C"), _normalize_fraction_coefficients(_parse_fraction(built["slope"]), Fraction(-1, 1), Fraction(0, 1)), strict=True)),
            "slope": built["slope"],
            "intercept": 0,
            "line_equation": built["semantic_answer"],
            "choices": built["choices"],
            "correct_label": built["correct_answer"],
            "semantic_answer": built["semantic_answer"],
            "point_a": built["point_a"],
            "point_b": built["point_b"],
        }
        return givens, answer, task_type

    if task_type == "intercept_form_from_intercept_sum_and_slope":
        built = build_intercept_form_from_intercept_sum_and_slope(
            constraints.get("intercept_sum"),
            constraints.get("slope"),
        )
        x_intercept = _parse_fraction(built["x_intercept"])
        y_intercept = _parse_fraction(built["y_intercept"])
        source_equation = ""
    elif "equation_coefficients" in constraints:
        coeffs = constraints["equation_coefficients"]
        if not isinstance(coeffs, dict):
            raise ValueError("equation_coefficients must be a dict.")
        a_coeff = _parse_fraction(coeffs.get("A"))
        b_coeff = _parse_fraction(coeffs.get("B"))
        c_coeff = _parse_fraction(coeffs.get("C"))
        if a_coeff == 0 or b_coeff == 0 or c_coeff == 0:
            raise ValueError("intercept_form_requires_nonzero_axis_intercepts")
        x_intercept = -c_coeff / a_coeff
        y_intercept = -c_coeff / b_coeff
        source_equation = _format_general_form(
            *_normalize_fraction_coefficients(a_coeff, b_coeff, c_coeff)
        )
    else:
        x_intercept = _read_intercept_or_pick(
            rng,
            constraints,
            keys=("x_intercept", "a"),
            coord_min=coord_min,
            coord_max=coord_max,
        )
        y_intercept = _read_intercept_or_pick(
            rng,
            constraints,
            keys=("y_intercept", "b"),
            coord_min=coord_min,
            coord_max=coord_max,
        )
        if x_intercept == 0 or y_intercept == 0:
            raise ValueError("intercept_form_requires_nonzero_axis_intercepts")
        source_equation = ""

    if task_type != "intercept_form_from_intercept_sum_and_slope":
        built = build_intercept_form_from_intercepts(x_intercept, y_intercept)
    area = build_intercept_triangle_area(x_intercept, y_intercept)
    answer = {
        "canonical_form": built["general_form"],
        "general_form": built["general_form"],
        "display_equation": built["display_equation"],
        "intercept_form": built["canonical_equation"],
        "coefficients": built["coefficients"],
        "slope": built["slope"],
        "intercept": built["y_intercept"],
        "x_intercept": built["x_intercept"],
        "y_intercept": built["y_intercept"],
        "triangle_area": _format_number(area),
        "line_equation": built["general_form"],
    }
    if task_type == "intercept_form_triangle_area":
        answer["canonical_form"] = _format_number(area)
    elif task_type == "intercept_form_equation_and_triangle_area":
        answer["canonical_form"] = build_intercept_form_equation_and_area(
            x_intercept,
            y_intercept,
        )

    givens: dict[str, object] = {
        "x_intercept": _format_number(x_intercept),
        "y_intercept": _format_number(y_intercept),
    }
    if task_type == "intercept_form_from_intercept_sum_and_slope":
        givens["intercept_sum"] = _format_number(_parse_fraction(constraints.get("intercept_sum")))
        givens["slope"] = _format_number(_parse_fraction(constraints.get("slope")))
    if source_equation:
        givens["equation"] = source_equation
    return givens, answer, task_type


def build_intercept_form_from_intercepts(
    x_intercept: object,
    y_intercept: object,
) -> dict[str, object]:
    a = _parse_fraction(x_intercept)
    b = _parse_fraction(y_intercept)
    if a == 0 or b == 0:
        raise ValueError("intercept_form_requires_nonzero_axis_intercepts")
    coeff_x, coeff_y, coeff_c = _normalize_fraction_coefficients(
        Fraction(1, 1) / a,
        Fraction(1, 1) / b,
        Fraction(-1, 1),
    )
    general = _format_general_form(coeff_x, coeff_y, coeff_c)
    display = f"x/{_format_number(a)} + y/{_format_number(b)} = 1"
    display = display.replace("+ y/-", "- y/")
    slope = -b / a
    return {
        "canonical_equation": display,
        "display_equation": display,
        "general_form": general,
        "coefficients": {"A": coeff_x, "B": coeff_y, "C": coeff_c},
        "x_intercept": _format_number(a),
        "y_intercept": _format_number(b),
        "slope": _format_number(slope),
    }


def build_intercept_triangle_area(
    x_intercept: object,
    y_intercept: object,
) -> Fraction:
    a = _parse_fraction(x_intercept)
    b = _parse_fraction(y_intercept)
    if a == 0 or b == 0:
        raise ValueError("intercept_form_requires_nonzero_axis_intercepts")
    return abs(a * b) / 2


def build_intercept_form_equation_and_area(
    x_intercept: object,
    y_intercept: object,
) -> dict[str, object]:
    equation = build_intercept_form_from_intercepts(x_intercept, y_intercept)
    area = build_intercept_triangle_area(x_intercept, y_intercept)
    return {
        "equation": equation["general_form"],
        "area": _format_number(area),
    }


def get_coordinate_midpoint(p1: object, p2: object) -> tuple[str, str]:
    x1, y1 = _read_coordinate_point(p1)
    x2, y2 = _read_coordinate_point(p2)
    return _format_number((x1 + x2) / 2), _format_number((y1 + y2) / 2)


def build_triangle_area_bisector_line(
    vertex: object,
    edge_p1: object,
    edge_p2: object,
) -> dict[str, object]:
    vx, vy = _read_coordinate_point(vertex)
    midpoint_x, midpoint_y = get_coordinate_midpoint(edge_p1, edge_p2)
    mx = _parse_fraction(midpoint_x)
    my = _parse_fraction(midpoint_y)
    line, actual_type = _line_from_two_fraction_points(vx, vy, mx, my)
    return {
        "vertex": _format_coordinate_point(vx, vy),
        "edge_p1": _format_coordinate_point(*_read_coordinate_point(edge_p1)),
        "edge_p2": _format_coordinate_point(*_read_coordinate_point(edge_p2)),
        "midpoint": _format_coordinate_point(mx, my),
        "line_type": actual_type,
        "canonical_form": line["canonical_form"],
        "display_equation": line["canonical_form"],
        "general_form": line["general_form"],
        "coefficients": line["coefficients"],
        "slope": line["slope"],
        "intercept": line["intercept"],
    }


def build_intercept_form_from_intercept_sum_and_slope(
    intercept_sum: object,
    slope: object,
) -> dict[str, object]:
    total = _parse_fraction(intercept_sum)
    m = _parse_fraction(slope)
    if m == 1:
        raise ValueError("intercept_sum_and_slope_degenerate")
    x_intercept = total / (1 - m)
    y_intercept = total - x_intercept
    return build_intercept_form_from_intercepts(x_intercept, y_intercept)


def compute_parabola_y_equals_x_squared_point(x: object) -> tuple[str, str]:
    x_value = _parse_fraction(x)
    y_value = x_value * x_value
    return _format_number(x_value), _format_number(y_value)


def compute_secant_slope_on_y_equals_x_squared(p: object, q: object) -> Fraction:
    p_value = _parse_fraction(p)
    q_value = _parse_fraction(q)
    if p_value == q_value:
        raise ValueError("parabola_secant_requires_distinct_x_values")
    return p_value + q_value


def build_parabola_secant_parallel_line_choice(
    p: object,
    q: object,
    choices: list[object],
) -> dict[str, object]:
    slope = compute_secant_slope_on_y_equals_x_squared(p, q)
    normalized_choices: list[dict[str, str]] = []
    correct_label = ""
    semantic_answer = ""
    for index, raw_choice in enumerate(choices):
        if isinstance(raw_choice, dict):
            label = str(raw_choice.get("label") or chr(ord("A") + index)).strip()
            text = str(raw_choice.get("text") or raw_choice.get("value") or "").strip()
        else:
            label = chr(ord("A") + index)
            text = str(raw_choice or "").strip()
        if not label or not text:
            continue
        normalized_choices.append({"label": label, "text": normalize_linear_expression_display(text)})
        choice_slope = _slope_from_origin_line_equation(text)
        if choice_slope == slope:
            correct_label = label
            semantic_answer = normalize_linear_expression_display(text)
    if not correct_label:
        raise ValueError("unsupported_choices_generator:no_parallel_line_choice")
    if len({choice["text"] for choice in normalized_choices}) != len(normalized_choices):
        raise ValueError("unsupported_choices_generator:duplicate_choices")
    point_a = compute_parabola_y_equals_x_squared_point(p)
    point_b = compute_parabola_y_equals_x_squared_point(q)
    return {
        "point_a": point_a,
        "point_b": point_b,
        "slope": _format_number(slope),
        "choices": normalized_choices,
        "correct_answer": correct_label,
        "semantic_answer": semantic_answer,
    }


def _slope_from_origin_line_equation(value: object) -> Fraction | None:
    text = normalize_linear_expression_display(str(value or ""))
    compact = text.replace(" ", "")
    if not compact.startswith("y="):
        return None
    rhs = compact.split("=", 1)[1]
    if not rhs.endswith("x"):
        return None
    coeff = rhs[:-1]
    if coeff in {"", "+"}:
        return Fraction(1, 1)
    if coeff == "-":
        return Fraction(-1, 1)
    return _parse_fraction(coeff)


def _read_coordinate_point(value: object) -> tuple[Fraction, Fraction]:
    if isinstance(value, dict):
        if "x" not in value or "y" not in value:
            raise ValueError("coordinate_point_requires_x_y")
        return _parse_fraction(value["x"]), _parse_fraction(value["y"])
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return _parse_fraction(value[0]), _parse_fraction(value[1])
    raise ValueError("coordinate_point_must_be_pair_or_dict")


def _format_coordinate_point(x_value: Fraction, y_value: Fraction) -> dict[str, str]:
    return {"x": _format_number(x_value), "y": _format_number(y_value)}


def _line_from_two_fraction_points(
    x1: Fraction,
    y1: Fraction,
    x2: Fraction,
    y2: Fraction,
) -> tuple[dict[str, object], str]:
    if x1 == x2 and y1 == y2:
        raise ValueError("line_requires_distinct_points")
    if x1 == x2:
        a_int, b_int, c_int = _normalize_fraction_coefficients(
            Fraction(1, 1),
            Fraction(0, 1),
            -x1,
        )
        general = _format_general_form(a_int, b_int, c_int)
        return (
            {
                "canonical_form": f"x = {_format_number(x1)}",
                "general_form": general,
                "coefficients": {"A": a_int, "B": b_int, "C": c_int},
                "slope": None,
                "intercept": None,
            },
            "vertical_line",
        )
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    line, actual_type = _line_from_slope_intercept(slope, intercept)
    line["line_equation"] = line["general_form"]
    return line, actual_type


def parse_or_canonicalize_intercept_form_equation(value: object) -> str | None:
    from core.checkers.linear_equation_equivalent_checker import canonicalize_linear_equation

    canonical = canonicalize_linear_equation(value)
    if canonical is None:
        return None
    return _format_general_form(*canonical)


def _line_from_slope_intercept(
    slope: Fraction,
    intercept: Fraction,
) -> tuple[dict[str, object], str]:
    a_int, b_int, c_int = _normalize_fraction_coefficients(
        slope,
        Fraction(-1, 1),
        intercept,
    )
    canonical = _format_slope_intercept(slope, intercept)
    general = _format_general_form(a_int, b_int, c_int)
    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": _format_fraction_or_int(slope),
            "intercept": _format_fraction_or_int(intercept),
        },
        "oblique_line" if slope != 0 else "horizontal_line",
    )


def _read_slope_or_pick(
    rng: random.Random,
    constraints: dict[str, object],
    *,
    allow_zero: bool = True,
) -> Fraction:
    raw = constraints.get("slope")
    if raw is not None:
        slope = _parse_fraction(raw)
    else:
        slope = _pick_slope(rng)
    if not allow_zero and slope == 0:
        return Fraction(1, 1)
    return slope


def _pick_nonzero_slope_intercept_slope(rng: random.Random) -> Fraction:
    slope = _pick_slope(rng, allow_fraction=True)
    while slope == 0:
        slope = _pick_slope(rng, allow_fraction=True)
    return slope


def _pick_slope_intercept_b(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    *,
    allow_zero: bool = True,
) -> Fraction:
    if rng.random() < 0.35:
        numerator = rng.choice([1, 2, 3, 4, 5, -1, -2, -3, -4, -5])
        denominator = rng.choice([2, 3, 4])
        value = Fraction(numerator, denominator)
    else:
        value = Fraction(rng.randint(coord_min, coord_max), 1)
    if not allow_zero:
        attempts = 0
        while value == 0 and attempts < 20:
            attempts += 1
            value = _pick_slope_intercept_b(rng, coord_min, coord_max)
        if value == 0:
            value = Fraction(1, 1)
    return value


def _read_intercept_or_pick(
    rng: random.Random,
    constraints: dict[str, object],
    *,
    keys: tuple[str, ...],
    coord_min: int,
    coord_max: int,
) -> Fraction:
    for key in keys:
        if key in constraints:
            return _parse_fraction(constraints[key])
    return Fraction(rng.randint(coord_min, coord_max), 1)


def _parse_fraction(value: object) -> Fraction:
    try:
        return normalize_fraction_value(value)
    except Exception as exc:
        raise ValueError(f"unsupported numeric token: {value!r}") from exc


def re_match_latex_fraction(text: str) -> Fraction | None:
    import re

    match = re.fullmatch(r"-?\\frac\{(-?\d+)\}\{(-?\d+)\}", text)
    if not match:
        return None
    return normalize_fraction_value(text)


def _format_fraction_or_int(value: Fraction) -> str | int:
    if value.denominator == 1:
        return value.numerator
    return _format_number(value)


def _line_from_vertical(x_val: int) -> tuple[dict[str, object], str]:
    a_int, b_int, c_int = _normalize_coefficients(1, 0, -x_val)
    canonical = f"x = {x_val}"
    general = _format_general_form(a_int, b_int, c_int)
    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": None,
            "intercept": None,
        },
        "vertical_line",
    )


def _line_from_horizontal(y_val: int) -> tuple[dict[str, object], str]:
    a_int, b_int, c_int = _normalize_coefficients(0, 1, -y_val)
    canonical = f"y = {y_val}"
    general = _format_general_form(a_int, b_int, c_int)
    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": 0,
            "intercept": y_val,
        },
        "horizontal_line",
    )


def _line_from_point_slope(
    x1: int, y1: int, slope: Fraction
) -> tuple[dict[str, object], str]:
    if slope.denominator == 0:
        raise ValueError("Slope denominator must not be zero.")

    b_frac = Fraction(y1, 1) - slope * Fraction(x1, 1)
    a_int, b_int, c_int = _normalize_fraction_coefficients(
        slope, Fraction(-1, 1), b_frac
    )

    canonical = _format_slope_intercept(slope, b_frac)
    general = _format_general_form(a_int, b_int, c_int)
    intercept_value: str | int
    if b_frac.denominator == 1:
        intercept_value = b_frac.numerator
    else:
        intercept_value = _format_number(b_frac)

    slope_value: str | int
    if slope.denominator == 1:
        slope_value = slope.numerator
    else:
        slope_value = _format_number(slope)

    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": slope_value,
            "intercept": intercept_value,
        },
        "oblique_line",
    )


def _normalize_fraction_coefficients(
    a: Fraction, b: Fraction, c: Fraction
) -> tuple[int, int, int]:
    denoms = [a.denominator, b.denominator, c.denominator]
    lcm = 1
    for d in denoms:
        lcm = lcm * d // math.gcd(lcm, d)
    a_int = int(a * lcm)
    b_int = int(b * lcm)
    c_int = int(c * lcm)
    return _normalize_coefficients(a_int, b_int, c_int)


def _normalize_coefficients(a: int, b: int, c: int) -> tuple[int, int, int]:
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    if g:
        a //= g
        b //= g
        c //= g
    if a < 0:
        a, b, c = -a, -b, -c
    elif a == 0 and b < 0:
        b, c = -b, -c
    return a, b, c


def _format_general_expression(a: int, b: int, c: int) -> str:
    terms: list[str] = []

    def append_term(coeff: int, var: str) -> None:
        if coeff == 0:
            return
        if not terms:
            if coeff == 1:
                terms.append(var)
            elif coeff == -1:
                terms.append(f"-{var}")
            else:
                terms.append(f"{coeff}{var}")
            return
        if coeff > 0:
            if coeff == 1:
                terms.append(f" + {var}")
            else:
                terms.append(f" + {coeff}{var}")
        elif coeff == -1:
            terms.append(f" - {var}")
        else:
            terms.append(f" - {abs(coeff)}{var}")

    append_term(a, "x")
    append_term(b, "y")
    if c != 0 or not terms:
        if not terms:
            terms.append(str(c))
        elif c > 0:
            terms.append(f" + {c}")
        else:
            terms.append(f" - {abs(c)}")
    return "".join(terms)


def _format_general_form(a: int, b: int, c: int) -> str:
    return f"{_format_general_expression(a, b, c)} = 0"


def _format_number(value: Fraction) -> str:
    return fraction_to_plain(value)


def _format_slope_intercept(slope: Fraction, intercept: Fraction) -> str:
    m_text = _format_slope_term(slope)
    if intercept == 0:
        return normalize_linear_expression_display(f"y = {m_text}x")
    sign = "+" if intercept > 0 else "-"
    b_abs = abs(intercept)
    b_text = fraction_to_plain(b_abs)
    return normalize_linear_expression_display(f"y = {m_text}x {sign} {b_text}")


def _format_slope_term(slope: Fraction) -> str:
    if slope == 1:
        return ""
    if slope == -1:
        return "-"
    return fraction_to_plain(slope)


def _has_point_pair(constraints: dict[str, object]) -> bool:
    return "point_a" in constraints and "point_b" in constraints


def _read_point_pair(constraints: dict[str, object]) -> tuple[int, int, int, int]:
    pa = constraints["point_a"]
    pb = constraints["point_b"]
    if not isinstance(pa, (list, tuple)) or not isinstance(pb, (list, tuple)):
        raise ValueError("point_a and point_b must be coordinate pairs.")
    return int(pa[0]), int(pa[1]), int(pb[0]), int(pb[1])


def _has_point_and_slope(constraints: dict[str, object]) -> bool:
    return "point" in constraints and "slope" in constraints


def _read_point_and_slope(constraints: dict[str, object]) -> tuple[int, int, Fraction | None]:
    pt = constraints["point"]
    if not isinstance(pt, (list, tuple)):
        raise ValueError("point must be a coordinate pair.")
    x1, y1 = int(pt[0]), int(pt[1])
    slope_raw = constraints["slope"]
    if slope_raw is None:
        return x1, y1, None
    if isinstance(slope_raw, int) and not isinstance(slope_raw, bool):
        return x1, y1, Fraction(slope_raw, 1)
    if isinstance(slope_raw, str):
        text = slope_raw.strip()
        if "/" in text:
            num, den = text.split("/", 1)
            return x1, y1, Fraction(int(num), int(den))
        return x1, y1, Fraction(int(text), 1)
    raise ValueError("slope must be int, str, or None.")


def _collect_points_on_line(
    givens: dict[str, object],
    a: int,
    b: int,
    c: int,
) -> list[list[int]]:
    points: list[list[int]] = []
    for key in ("point_a", "point_b", "point"):
        raw = givens.get(key)
        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            try:
                x_val, y_val = int(raw[0]), int(raw[1])
            except (TypeError, ValueError):
                continue
            if a * x_val + b * y_val + c == 0:
                points.append([x_val, y_val])
    return points


def _build_visual_spec(
    *,
    givens: dict[str, object],
    answer: dict[str, object],
    actual_type: str,
    x_range: list[int],
    y_range: list[int],
) -> dict[str, object]:
    points: list[dict[str, object]] = []
    lines: list[dict[str, object]] = []

    if "point_a" in givens and "point_b" in givens:
        pa = givens["point_a"]
        pb = givens["point_b"]
        if isinstance(pa, (list, tuple)) and isinstance(pb, (list, tuple)):
            points.append({"x": int(pa[0]), "y": int(pa[1]), "label": "A"})
            points.append({"x": int(pb[0]), "y": int(pb[1]), "label": "B"})
            lines.append({"through_points": ["A", "B"], "label": "L"})
    elif "point" in givens:
        pt = givens["point"]
        if isinstance(pt, (list, tuple)):
            try:
                points.append({"x": int(pt[0]), "y": int(pt[1]), "label": "P"})
                lines.append({"through_points": ["P"], "label": "L"})
            except (TypeError, ValueError):
                lines.append({"label": "L"})
    elif actual_type == "horizontal_line":
        y_val = int(givens.get("y_intercept", 0))  # type: ignore[arg-type]
        lines.append({"type": "horizontal", "y": y_val, "label": "L"})
    elif actual_type == "vertical_line":
        x_val = int(givens.get("x_intercept", 0))  # type: ignore[arg-type]
        lines.append({"type": "vertical", "x": x_val, "label": "L"})

    if actual_type == "oblique_line" or str(actual_type).startswith("slope_intercept"):
        slope = answer.get("slope")
        intercept = answer.get("intercept")
        line_entry: dict[str, object] = {"label": "L"}
        if isinstance(slope, int) and isinstance(intercept, int):
            line_entry.update({"type": "slope_intercept", "m": slope, "b": intercept})
        else:
            line_entry.update(
                {
                    "type": "slope_intercept",
                    "m": slope,
                    "b": intercept,
                }
            )
        if points:
            line_entry["through_points"] = [str(p.get("label", "")) for p in points]
        lines = [line_entry]

    return {
        "kind": "coordinate_plane_spec",
        "points": points,
        "lines": lines,
        "x_range": x_range,
        "y_range": y_range,
    }


def _build_distractors(
    *,
    rng: random.Random,
    answer: dict[str, object],
    actual_type: str,
    givens: dict[str, object],
    coord_min: int,
    coord_max: int,
    task_type: str = "",
) -> list[str]:
    if "distractors" in answer:
        return [str(d) for d in answer["distractors"]]
    if "choices" in answer:
        return [str(choice.get("text") if isinstance(choice, dict) else choice) for choice in answer["choices"]]
    canonical = str(answer["canonical_form"])
    candidates: list[str] = []

    numeric_tasks = {
        "slope_from_general_or_intercept_form",
        "slope_from_general_form",
        "slope_of_horizontal_or_vertical_line",
        "parallel_line_slope",
        "perpendicular_line_slope",
        "perpendicular_condition_parameter",
        "parallel_condition_parameter",
        "intercept_form_triangle_area",
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
    }

    if "或" in canonical:
        parts = canonical.split(" 或 ")
        try:
            v1 = int(parts[0])
            v2 = int(parts[1])
            perturbations = [
                f"{v1 + 2} 或 {v2 - 2}",
                f"{v1 - 2} 或 {v2 + 2}",
                f"{-v1} 或 {-v2}",
                f"{v1} 或 {-v2}",
                f"{-v1} 或 {v2}",
            ]
            candidates.extend(perturbations)
        except Exception:
            pass

    elif task_type in numeric_tasks or not any(char in canonical for char in ("x", "y", "=")):
        # Generate numeric/fraction distractors
        val = 0
        try:
            val = Fraction(canonical)
        except Exception:
            try:
                val = Fraction(int(canonical))
            except Exception:
                pass
        
        # Perturb numeric value
        perturbations = [
            val + 1,
            val - 1,
            -val,
            val + Fraction(1, 2) if val != 0 else Fraction(3, 2),
            val - Fraction(1, 2) if val != 0 else Fraction(-3, 2),
        ]
        for p in perturbations:
            candidates.append(fraction_to_plain(p))
        candidates.extend(["無", "0", "1", "-1"])

    if actual_type == "vertical_line":
        if "=" in canonical:
            x_val = _extract_vertical_k(canonical)
            for delta in (-2, -1, 1, 2, 3):
                candidates.append(f"x = {x_val + delta}")
            candidates.extend([f"y = {rng.randint(coord_min, coord_max)}" for _ in range(3)])
        else:
            candidates = ["0", "1", "-1", "2"]
    elif actual_type == "horizontal_line":
        if "=" in canonical:
            y_val = _extract_horizontal_k(canonical)
            for delta in (-2, -1, 1, 2, 3):
                candidates.append(f"y = {y_val + delta}")
            candidates.extend([f"x = {rng.randint(coord_min, coord_max)}" for _ in range(3)])
        else:
            candidates = ["無", "1", "-1", "2"]
    else:
        slope = answer.get("slope")
        intercept = answer.get("intercept")
        base_m = _parse_numeric_token(slope)
        base_b = _parse_numeric_token(intercept)
        perturbations = [
            (base_m + 1, base_b),
            (base_m - 1, base_b),
            (base_m, base_b + 1),
            (base_m, base_b - 1),
            (-base_m, base_b),
            (base_m, -base_b),
        ]
        for m_val, b_val in perturbations:
            candidates.append(_format_slope_intercept(Fraction(m_val), Fraction(b_val)))

        pt = givens.get("point")
        if isinstance(pt, (list, tuple)):
            x1, y1 = int(pt[0]), int(pt[1])
            wrong_b = y1 + 1
            candidates.append(_format_slope_intercept(Fraction(base_m), Fraction(wrong_b)))

    unique: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        text = item.strip()
        if not text or text == canonical or text in seen:
            continue
        seen.add(text)
        unique.append(text)
        if len(unique) >= 3:
            break

    attempt = 0
    while len(unique) < 3:
        attempt += 1
        fake = f"y = {rng.randint(coord_min, coord_max)}x + {rng.randint(coord_min, coord_max)}"
        if fake != canonical and fake not in seen:
            seen.add(fake)
            unique.append(fake)
        if attempt > 50:
            for filler in ("y = x + 99", "y = -x - 99", "y = 2x + 5"):
                if filler != canonical and filler not in seen:
                    seen.add(filler)
                    unique.append(filler)
            break

    return unique


def _extract_vertical_k(canonical: str) -> int:
    parts = canonical.split("=", 1)
    return int(parts[1].strip())


def _extract_horizontal_k(canonical: str) -> int:
    parts = canonical.split("=", 1)
    return int(parts[1].strip())


def _parse_numeric_token(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip()
        if "/" in text:
            num, den = text.split("/", 1)
            return int(Fraction(int(num), int(den)))
        return int(text)
    return 0


def _build_explanation_steps(
    *,
    line_type: str,
    actual_type: str,
    givens: dict[str, object],
    answer: dict[str, object],
) -> list[str]:
    canonical = str(answer["canonical_form"])
    if line_type == "two_points":
        return [
            "以兩點座標計算斜率或判斷是否為水平/鉛直線",
            "代入點斜式或特殊式整理",
            f"化簡得 {canonical}",
        ]
    if line_type == "point_slope":
        return [
            "寫出點斜式",
            "展開並移項整理",
            f"化簡得 {canonical}",
        ]
    if actual_type == "horizontal_line":
        return [
            "觀察兩點的 y 座標相同，判斷為水平線",
            "水平線斜率為 0",
            f"直接寫成 {canonical}",
        ]
    if actual_type == "vertical_line":
        return [
            "觀察兩點的 x 座標相同，判斷為鉛直線",
            "鉛直線斜率不存在",
            f"直接寫成 {canonical}",
        ]
    return [
        "確認斜率與截距",
        "寫成斜截式",
        f"化簡得 {canonical}",
    ]


def _build_slope_from_general_form(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    A = rng.randint(coord_min, coord_max)
    while A == 0:
        A = rng.randint(coord_min, coord_max)
    B = rng.randint(coord_min, coord_max)
    while B == 0:
        B = rng.randint(coord_min, coord_max)
    C = rng.randint(coord_min, coord_max)
    
    a_int, b_int, c_int = _normalize_coefficients(A, B, C)
    m = Fraction(-a_int, b_int)
    
    givens = {
        "equation": _format_general_form(a_int, b_int, c_int),
    }
    answer = {
        "canonical_form": _format_number(m),
        "slope": _format_number(m),
        "coefficients": {"A": a_int, "B": b_int, "C": c_int},
        "intercept": _format_number(Fraction(-c_int, b_int)),
    }
    return givens, answer, "oblique_line"


def _build_slope_from_general_or_intercept_form(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    form_type = rng.choice([0, 1])
    if form_type == 0:
        return _build_slope_from_general_form(rng, coord_min, coord_max, constraints)
    else:
        a = rng.randint(1, coord_max)
        if rng.random() < 0.5:
            a = -a
        b = rng.randint(1, coord_max)
        if rng.random() < 0.5:
            b = -b
            
        m = Fraction(-b, a)
        coeff_x, coeff_y, coeff_c = _normalize_fraction_coefficients(
            Fraction(1, a),
            Fraction(1, b),
            Fraction(-1, 1),
        )
        
        a_str = f"\\frac{{x}}{{{a}}}" if a > 0 else f"-\\frac{{x}}{{{abs(a)}}}"
        if b > 0:
            eq_str = f"{a_str} + \\frac{{y}}{{{b}}} = 1"
        else:
            eq_str = f"{a_str} - \\frac{{y}}{{{abs(b)}}} = 1"
            
        givens = {
            "equation": eq_str,
        }
        answer = {
            "canonical_form": _format_number(m),
            "slope": _format_number(m),
            "coefficients": {"A": coeff_x, "B": coeff_y, "C": coeff_c},
            "intercept": _format_number(Fraction(-coeff_c, coeff_y)),
        }
        return givens, answer, "oblique_line"


def _build_slope_of_horizontal_or_vertical_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    sub_type = rng.choice(["horizontal", "vertical", "general"])
    if sub_type == "horizontal":
        k = rng.randint(coord_min, coord_max)
        while k == 0:
            k = rng.randint(coord_min, coord_max)
        givens = {"equation": f"y = {k}"}
        answer = {
            "canonical_form": "0",
            "slope": 0,
            "coefficients": {"A": 0, "B": 1, "C": -k},
            "intercept": k,
        }
        return givens, answer, "horizontal_line"
    elif sub_type == "vertical":
        h = rng.randint(coord_min, coord_max)
        while h == 0:
            h = rng.randint(coord_min, coord_max)
        givens = {"equation": f"x = {h}"}
        answer = {
            "canonical_form": "無",
            "slope": "無",
            "coefficients": {"A": 1, "B": 0, "C": -h},
            "intercept": None,
        }
        return givens, answer, "vertical_line"
    else:
        return _build_slope_from_general_form(rng, coord_min, coord_max, constraints)


def _build_line_through_point_parallel_to_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    A = rng.randint(coord_min, coord_max)
    while A == 0:
        A = rng.randint(coord_min, coord_max)
    B = rng.randint(coord_min, coord_max)
    while B == 0:
        B = rng.randint(coord_min, coord_max)
    C = rng.randint(coord_min, coord_max)
    
    x0 = rng.randint(coord_min, coord_max)
    y0 = rng.randint(coord_min, coord_max)
    
    A, B, C = _normalize_coefficients(A, B, C)
    K = -(A * x0 + B * y0)
    
    givens = {
        "point": [x0, y0],
        "equation": _format_general_form(A, B, C),
    }
    canonical = _format_general_form(A, B, K)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": K},
        "slope": _format_number(Fraction(-A, B)),
        "intercept": _format_number(Fraction(-K, B)),
    }
    return givens, answer, "oblique_line"


def _build_line_through_point_perpendicular_to_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    A = rng.randint(coord_min, coord_max)
    while A == 0:
        A = rng.randint(coord_min, coord_max)
    B = rng.randint(coord_min, coord_max)
    while B == 0:
        B = rng.randint(coord_min, coord_max)
    C = rng.randint(coord_min, coord_max)
    
    x0 = rng.randint(coord_min, coord_max)
    y0 = rng.randint(coord_min, coord_max)
    
    A, B, C = _normalize_coefficients(A, B, C)
    pA, pB, pK = _normalize_coefficients(B, -A, -(B * x0 - A * y0))
    
    givens = {
        "point": [x0, y0],
        "equation": _format_general_form(A, B, C),
    }
    canonical = _format_general_form(pA, pB, pK)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": pA, "B": pB, "C": pK},
        "slope": _format_number(Fraction(-pA, pB)) if pB != 0 else "無",
        "intercept": _format_number(Fraction(-pK, pB)) if pB != 0 else None,
    }
    return givens, answer, "oblique_line"


def _build_parallel_line_slope(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    return _build_slope_from_general_form(rng, coord_min, coord_max, constraints)


def _build_perpendicular_line_slope(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    A = rng.randint(coord_min, coord_max)
    while A == 0:
        A = rng.randint(coord_min, coord_max)
    B = rng.randint(coord_min, coord_max)
    while B == 0:
        B = rng.randint(coord_min, coord_max)
    C = rng.randint(coord_min, coord_max)
    
    A, B, C = _normalize_coefficients(A, B, C)
    m = Fraction(B, A)
    
    givens = {
        "equation": _format_general_form(A, B, C),
    }
    answer = {
        "canonical_form": _format_number(m),
        "slope": _format_number(m),
        "coefficients": {"A": A, "B": B, "C": C},
        "intercept": _format_number(Fraction(-C, B)),
    }
    return givens, answer, "oblique_line"


def _build_parallel_condition_parameter(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    b2 = rng.randint(1, 5)
    if rng.random() < 0.5:
        b2 = -b2
    factor = rng.randint(1, 3)
    if rng.random() < 0.5:
        factor = -factor
    b1 = b2 * factor
    
    a2 = rng.randint(coord_min, coord_max)
    while a2 == 0:
        a2 = rng.randint(coord_min, coord_max)
    a1 = a2 * factor
    
    c1 = rng.randint(coord_min, coord_max)
    c2 = rng.randint(coord_min, coord_max)
    while c1 * b2 == c2 * b1:
        c2 = rng.randint(coord_min, coord_max)
        
    givens = {
        "equation_1": f"ax + {b1}y + {c1} = 0" if b1 > 0 else f"ax - {abs(b1)}y + {c1} = 0",
        "equation_2": _format_general_form(a2, b2, c2),
    }
    givens["equation_1"] = givens["equation_1"].replace("+ -", "- ").replace("+ +", "+ ")
    
    answer = {
        "canonical_form": str(a1),
        "parameter": a1,
        "coefficients": {"A": a1, "B": b1, "C": c1},
        "slope": _format_number(Fraction(-a1, b1)),
        "intercept": _format_number(Fraction(-c1, b1)),
    }
    return givens, answer, "oblique_line"


def _build_perpendicular_condition_parameter(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    a2 = rng.choice([1, 2, 3, 4, -1, -2, -3, -4])
    factor = rng.randint(1, 3)
    if rng.random() < 0.5:
        factor = -factor
    b1 = a2 * factor
    
    b2 = rng.randint(coord_min, coord_max)
    while b2 == 0:
        b2 = rng.randint(coord_min, coord_max)
        
    a1 = -b1 * b2 // a2
    c1 = rng.randint(coord_min, coord_max)
    c2 = rng.randint(coord_min, coord_max)
    
    givens = {
        "equation_1": f"ax + {b1}y + {c1} = 0" if b1 > 0 else f"ax - {abs(b1)}y + {c1} = 0",
        "equation_2": _format_general_form(a2, b2, c2),
    }
    givens["equation_1"] = givens["equation_1"].replace("+ -", "- ").replace("+ +", "+ ")
    
    answer = {
        "canonical_form": str(a1),
        "parameter": a1,
        "coefficients": {"A": a1, "B": b1, "C": c1},
        "slope": _format_number(Fraction(-a1, b1)),
        "intercept": _format_number(Fraction(-c1, b1)),
    }
    return givens, answer, "oblique_line"


def _build_compare_line_slopes(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    slopes = []
    while len(slopes) < 4:
        s = _pick_slope(rng, allow_fraction=True)
        if s not in slopes:
            slopes.append(s)
            
    labels = ["A", "B", "C", "D"]
    choices = []
    
    max_val = max(slopes)
    correct_idx = slopes.index(max_val)
    correct_label = labels[correct_idx]
    
    for i, m in enumerate(slopes):
        lbl = labels[i]
        b = rng.randint(-3, 3)
        while b == 0:
            b = rng.randint(-3, 3)
            
        if i == 0:
            text = _format_slope_intercept(m, Fraction(b, 1))
        elif i == 1:
            x1 = rng.randint(-3, 3)
            y1 = int(m * x1 + b)
            y_term = f"y - {y1}" if y1 > 0 else (f"y + {abs(y1)}" if y1 < 0 else "y")
            x_term = f"x - {x1}" if x1 > 0 else (f"x + {abs(x1)}" if x1 < 0 else "x")
            m_term = _format_slope_term(m)
            text = f"{y_term} = {m_term}({x_term})"
        elif i == 2:
            b_val = b
            a_val = Fraction(-b_val, m)
            a_str = fraction_to_plain(a_val)
            b_str = str(b_val)
            text = f"x/{a_str} + y/{b_str} = 1"
        else:
            A, B, C = _normalize_fraction_coefficients(m, Fraction(-1, 1), Fraction(b, 1))
            text = _format_general_form(A, B, C)
            
        choices.append({"label": lbl, "text": text})
        
    givens = {
        "choices": choices,
    }
    answer = {
        "canonical_form": correct_label,
        "correct_label": correct_label,
        "choices": choices,
        "coefficients": {"A": 1, "B": -1, "C": 0},
        "slope": max_val,
        "intercept": 0,
    }
    return givens, answer, "oblique_line"


def _build_line_through_point_perpendicular_to_segment(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    xA = rng.randint(coord_min, coord_max)
    yA = rng.randint(coord_min, coord_max)
    
    xC = rng.randint(coord_min, coord_max)
    while xC == xA:
        xC = rng.randint(coord_min, coord_max)
    yC = rng.randint(coord_min, coord_max)
    while yC == yA:
        yC = rng.randint(coord_min, coord_max)
        
    mAC = Fraction(yC - yA, xC - xA)
    mPerp = -1 / mAC
    
    xB = rng.randint(coord_min, coord_max)
    yB = rng.randint(coord_min, coord_max)
    
    b_frac = Fraction(yB, 1) - mPerp * Fraction(xB, 1)
    A, B, C = _normalize_fraction_coefficients(mPerp, Fraction(-1, 1), b_frac)
    
    givens = {
        "point_b": [xB, yB],
        "point_a": [xA, yA],
        "point_c": [xC, yC],
    }
    canonical = _format_general_form(A, B, C)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": C},
        "slope": _format_number(mPerp),
        "intercept": _format_number(b_frac),
    }
    return givens, answer, "oblique_line"


def _build_line_through_intersection_parallel_to_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    x0 = rng.randint(-3, 3)
    y0 = rng.randint(-3, 3)
    
    A1 = rng.randint(-4, 4)
    while A1 == 0:
        A1 = rng.randint(-4, 4)
    B1 = rng.randint(-4, 4)
    while B1 == 0:
        B1 = rng.randint(-4, 4)
    C1 = -(A1 * x0 + B1 * y0)
    
    A2 = rng.randint(-4, 4)
    while A2 == 0 or A2 * B1 == A1:
        A2 = rng.randint(-4, 4)
    B2 = rng.randint(-4, 4)
    while B2 == 0 or A1 * B2 == A2 * B1:
        B2 = rng.randint(-4, 4)
    C2 = -(A2 * x0 + B2 * y0)
    
    A4 = rng.randint(-4, 4)
    while A4 == 0:
        A4 = rng.randint(-4, 4)
    B4 = rng.randint(-4, 4)
    while B4 == 0:
        B4 = rng.randint(-4, 4)
    C4 = rng.randint(-4, 4)
    
    A1, B1, C1 = _normalize_coefficients(A1, B1, C1)
    A2, B2, C2 = _normalize_coefficients(A2, B2, C2)
    A4, B4, C4 = _normalize_coefficients(A4, B4, C4)
    
    A3, B3, C3 = _normalize_coefficients(A4, B4, -(A4 * x0 + B4 * y0))
    
    givens = {
        "equation_1": _format_general_form(A1, B1, C1),
        "equation_2": _format_general_form(A2, B2, C2),
        "equation_3": _format_general_form(A4, B4, C4),
    }
    canonical = _format_general_form(A3, B3, C3)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A3, "B": B3, "C": C3},
        "slope": _format_number(Fraction(-A3, B3)),
        "intercept": _format_number(Fraction(-C3, B3)),
    }
    return givens, answer, "oblique_line"


def _build_perpendicular_bisector_application(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    xA = rng.randint(coord_min, coord_max)
    yA = rng.randint(coord_min, coord_max)
    
    xB = rng.randint(coord_min, coord_max)
    while xB == xA:
        xB = rng.randint(coord_min, coord_max)
    yB = rng.randint(coord_min, coord_max)
    while yB == yA:
        yB = rng.randint(coord_min, coord_max)
        
    mid_x = Fraction(xA + xB, 2)
    mid_y = Fraction(yA + yB, 2)
    
    mAB = Fraction(yB - yA, xB - xA)
    mPerp = -1 / mAB
    
    b_frac = mid_y - mPerp * mid_x
    A, B, C = _normalize_fraction_coefficients(mPerp, Fraction(-1, 1), b_frac)
    
    givens = {
        "point_a": [xA, yA],
        "point_b": [xB, yB],
    }
    canonical = _format_general_form(A, B, C)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": C},
        "slope": _format_number(mPerp),
        "intercept": _format_number(b_frac),
    }
    return givens, answer, "oblique_line"


def _build_distance_from_point_to_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    triples = [(3, 4), (5, 12), (8, 15), (7, 24)]
    base_a, base_b = rng.choice(triples)
    A = base_a * rng.choice([1, -1])
    B = base_b * rng.choice([1, -1])
    C = rng.randint(coord_min, coord_max)
    while C == 0:
        C = rng.randint(coord_min, coord_max)
        
    x0 = rng.randint(coord_min, coord_max)
    y0 = rng.randint(coord_min, coord_max)
    
    denom = int(math.isqrt(A*A + B*B))
    numer = abs(A*x0 + B*y0 + C)
    dist_frac = Fraction(numer, denom)
    
    givens = {
        "point": [x0, y0],
        "line_expression": _format_general_expression(A, B, C),
        "equation": _format_general_form(A, B, C),
    }
    canonical = fraction_to_plain(dist_frac)
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": C},
        "distance": canonical,
        "value": canonical,
    }
    return givens, answer, "oblique_line"


def _build_distance_from_point_to_line_parameter(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    triples = [(3, 4), (5, 12), (8, 15), (7, 24)]
    base_a, base_b = rng.choice(triples)
    A = base_a * rng.choice([1, -1])
    B = base_b * rng.choice([1, -1])
    D = int(math.isqrt(A*A + B*B))
    
    x0 = rng.randint(coord_min, coord_max)
    y0 = rng.randint(coord_min, coord_max)
    d = rng.randint(1, 5)
    
    param_name = rng.choice(["k", "a"])
    V = A * x0 + B * y0
    k1 = -V + d * D
    k2 = -V - d * D
    if k1 == 0: k1 = k2
    if k2 == 0: k2 = k1
    
    givens = {
        "point": [x0, y0],
        "line_expression": _format_general_expression(A, B, 0),
        "equation": f"{_format_general_expression(A, B, 0)} + {param_name} = 0",
        "distance": d,
    }
    canonical = f"{min(k1, k2)} 或 {max(k1, k2)}"
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": 0},
        "distance": d,
        "parameter": canonical,
        "parameter_name": param_name,
        "value": canonical,
    }
    return givens, answer, "oblique_line"


def _build_distance_from_point_to_line_parameter_single_choice_scalar(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    A, B, D = 3, 4, 5
    x0 = rng.randint(min(coord_min, -6), -1)
    distance_unit = rng.randint(1, 5)
    distance_value = 4 * distance_unit
    target_value = 5 * distance_unit
    C = -A * x0
    param_name = str(constraints.get("parameter_name") or "a")
    line_expression = _format_general_expression(A, B, C)
    distractor_values = [
        target_value - 2,
        target_value - 1,
        target_value + 1,
        target_value + 2,
        -target_value,
    ]
    choices = [target_value]
    for value in distractor_values:
        if value != target_value and value not in choices:
            choices.append(value)
        if len(choices) == 4:
            break
    rng.shuffle(choices)
    labels = ["A", "B", "C", "D"]
    correct_label = labels[choices.index(target_value)]
    choice_rows = [
        {"label": label, "text": str(value), "value": value}
        for label, value in zip(labels, choices, strict=True)
    ]
    givens = {
        "point": [x0, param_name],
        "point_parameter": param_name,
        "quadrant": "II",
        "line_expression": line_expression,
        "equation": f"{line_expression} = 0",
        "distance": distance_value,
        "choices": choice_rows,
    }
    canonical = str(target_value)
    answer = {
        "canonical_form": correct_label,
        "general_form": canonical,
        "coefficients": {"A": A, "B": B, "C": C},
        "distance": distance_value,
        "parameter": canonical,
        "parameter_name": param_name,
        "solution_cardinality": "single",
        "choice_value_shape": "scalar",
        "correct_label": correct_label,
        "choices": choice_rows,
        "value": canonical,
    }
    return givens, answer, "oblique_line"


def _build_compare_point_to_line_distances(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    triples = [(3, 4), (5, 12), (8, 15), (7, 24)]
    
    # Line 1
    base_a1, base_b1 = rng.choice(triples)
    A1 = base_a1 * rng.choice([1, -1])
    B1 = base_b1 * rng.choice([1, -1])
    C1 = rng.randint(coord_min, coord_max)
    while C1 == 0:
        C1 = rng.randint(coord_min, coord_max)
        
    # Line 2
    base_a2, base_b2 = rng.choice(triples)
    A2 = base_a2 * rng.choice([1, -1])
    B2 = base_b2 * rng.choice([1, -1])
    C2 = rng.randint(coord_min, coord_max)
    while C2 == 0:
        C2 = rng.randint(coord_min, coord_max)
        
    x0 = rng.randint(coord_min, coord_max)
    y0 = rng.randint(coord_min, coord_max)
    
    D1 = int(math.isqrt(A1*A1 + B1*B1))
    D2 = int(math.isqrt(A2*A2 + B2*B2))
    
    d1 = Fraction(abs(A1*x0 + B1*y0 + C1), D1)
    d2 = Fraction(abs(A2*x0 + B2*y0 + C2), D2)
    
    while d1 == d2:
        C2 = rng.randint(coord_min, coord_max)
        while C2 == 0:
            C2 = rng.randint(coord_min, coord_max)
        d2 = Fraction(abs(A2*x0 + B2*y0 + C2), D2)
        
    target_direction = str(constraints.get("target_direction") or "closer").strip().lower()
    if target_direction not in {"closer", "farther", "relation"}:
        target_direction = "closer"
    givens = {
        "point": [x0, y0],
        "equation_1": _format_general_form(A1, B1, C1),
        "equation_2": _format_general_form(A2, B2, C2),
        "target_direction": target_direction,
    }
    
    if d1 < d2:
        closer_line = "L_1"
        farther_line = "L_2"
        distractors = ["L_2", "一樣近", "無法比較"]
    else:
        closer_line = "L_2"
        farther_line = "L_1"
        distractors = ["L_1", "一樣近", "無法比較"]
    comparison_relation = "d(P,L_1) < d(P,L_2)" if d1 < d2 else "d(P,L_1) > d(P,L_2)"
    if target_direction == "farther":
        canonical = farther_line
    elif target_direction == "relation":
        canonical = comparison_relation
    else:
        canonical = closer_line
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": A1, "B": B1, "C": C1},
        "target_direction": target_direction,
        "closer_line": closer_line,
        "farther_line": farther_line,
        "comparison_relation": comparison_relation,
        "comparison_result": canonical,
        "distances": {
            "L_1": fraction_to_plain(d1),
            "L_2": fraction_to_plain(d2),
        },
        "value": canonical,
        "distractors": distractors,
    }
    return givens, answer, "oblique_line"


# Canonical domain_operation aliases -> legacy line_type tokens used inside builders.
DOMAIN_OPERATION_LINE_TYPE: dict[str, str] = {
    "point_to_line_distance": "distance_from_point_to_line",
    "parallel_lines_distance": "distance_from_point_to_line",
    "find_parameter_from_distance": "distance_from_point_to_line_parameter",
    "find_parameter_from_point_line_distance": "distance_from_point_to_line_parameter",
    "foot_of_perpendicular": "line_through_point_perpendicular_to_segment",
    "point_reflection_across_line": "perpendicular_bisector_application",
    "distance_comparison": "compare_point_to_line_distances",
}


def resolve_line_type_for_domain_operation(domain_operation: str) -> str:
    """Map external domain_operation key to internal line_type."""
    key = str(domain_operation or "").strip()
    if not key:
        raise ValueError("domain_operation must be provided.")
    return DOMAIN_OPERATION_LINE_TYPE.get(key, key)


def build_coordinate_geometry_matrix(
    *,
    seed: int | None,
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Domain entrypoint keyed by domain_operation (no skill_id branching)."""
    line_type = resolve_line_type_for_domain_operation(domain_operation)
    return build_line_equation_matrix(
        seed=seed,
        line_type=line_type,
        curriculum_profile=curriculum_profile,
        difficulty_profile=difficulty_profile,
        constraints=constraints,
    )







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


def build_draw_constant_function_graph_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a canvas task for a constant function's horizontal graph."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    constant = int(
        normalized.get(
            "constant",
            rng.choice([value for value in range(-6, 7) if value]),
        )
    )
    extent = max(5, abs(constant) + 2)
    equation = f"y={constant}"
    expected_spec = {
        "drawing_type": "line_graph",
        "graph_kind": "constant_function",
        "equation": equation,
        "slope": 0,
        "y_intercept": constant,
        "expected_line": {
            "points": [[-extent, constant], [extent, constant]],
            "horizontal": True,
            "spans_graph_width": True,
        },
        "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {
            "x_min": -extent,
            "x_max": extent,
            "y_min": -extent,
            "y_max": extent,
        },
        "tolerance": {"slope": 0.08, "y_intercept": 0.35},
    }
    return {
        "question": f"請在坐標平面上畫出常數函數 $f(x)={constant}$ 的圖形。",
        "givens": {
            "constant": constant,
            "constant_function_equation": equation,
        },
        "answer": expected_spec,
        "semantic_answer": expected_spec,
        "distractors": [],
        "answer_type": "drawing",
        "presentation_mode": "canvas",
        "expected_drawing_spec": expected_spec,
        "visual_spec": {
            "kind": "cartesian_canvas",
            "axis_range": dict(expected_spec["axis_range"]),
            "show_grid": True,
            "editable": True,
        },
        "explanation_steps": [
            f"常數函數對所有 x 都有相同函數值 {constant}。",
            f"圖形是通過 (0,{constant}) 且平行 x 軸的水平直線。",
        ],
        "validation_facts": {
            "constant": constant,
            "slope": 0,
            "y_intercept": constant,
            "horizontal": True,
        },
        "topology_tags": [
            "graph_construction",
            "horizontal_line",
            "constant_function",
        ],
    }


def build_draw_linear_function_graph_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a canvas task for a non-constant linear function graph."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    slope = int(
        normalized.get("slope", rng.choice([-3, -2, -1, 1, 2, 3]))
    )
    intercept = int(normalized.get("intercept", rng.randint(-4, 4)))
    if slope == 0:
        raise ValueError("linear_function_slope_must_be_nonzero")
    x_extent = 6
    endpoint_values = [
        slope * -x_extent + intercept,
        slope * x_extent + intercept,
    ]
    y_extent = max(6, *(abs(value) + 2 for value in endpoint_values))
    expression = f"{slope}x"
    if intercept > 0:
        expression += f"+{intercept}"
    elif intercept < 0:
        expression += str(intercept)
    equation = f"y={expression}"
    points = [[-x_extent, endpoint_values[0]], [x_extent, endpoint_values[1]]]
    expected_spec = {
        "drawing_type": "line_graph",
        "graph_kind": "linear_function",
        "equation": equation,
        "slope": slope,
        "y_intercept": intercept,
        "expected_line": {
            "points": points,
            "horizontal": False,
            "spans_graph_width": True,
        },
        "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {
            "x_min": -x_extent,
            "x_max": x_extent,
            "y_min": -y_extent,
            "y_max": y_extent,
        },
        "tolerance": {"slope": 0.08, "y_intercept": 0.35},
    }
    return {
        "question": f"請在坐標平面上畫出一次函數 $f(x)={expression}$ 的圖形。",
        "givens": {
            "slope": slope,
            "y_intercept": intercept,
            "linear_function_equation": equation,
        },
        "answer": expected_spec,
        "semantic_answer": expected_spec,
        "distractors": [],
        "answer_type": "drawing",
        "presentation_mode": "canvas",
        "expected_drawing_spec": expected_spec,
        "visual_spec": {
            "kind": "cartesian_canvas",
            "axis_range": dict(expected_spec["axis_range"]),
            "show_grid": True,
            "editable": True,
        },
        "explanation_steps": [
            f"圖形斜率為 {slope}，y 截距為 {intercept}。",
            "取兩個符合函數式的點並連成直線。",
        ],
        "validation_facts": {
            "slope": slope,
            "y_intercept": intercept,
            "points": points,
            "collinear": True,
        },
        "topology_tags": [
            "graph_construction",
            "linear_function",
            "two_point_plotting",
        ],
    }


def build_graph_based_linear_application_inverse_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build an inverse-evaluation task from a non-constant linear model."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    slope = int(normalized.get("slope", rng.choice([2, 3, 4, 5])))
    intercept = int(normalized.get("intercept", rng.randint(5, 30)))
    input_min = int(normalized.get("input_min", 1))
    input_max = int(normalized.get("input_max", 12))
    if slope == 0 or input_min >= input_max:
        raise ValueError("invalid_inverse_linear_model_constraints")
    target_input = int(
        normalized.get("target_input", rng.randint(input_min, input_max))
    )
    if not input_min <= target_input <= input_max:
        raise ValueError("target_input_out_of_range")
    known_output = slope * target_input + intercept
    return {
        "question": (
            f"某方案的輸入量 x 與總費用 y 關係為 $y={slope}x+{intercept}$，"
            f"其圖形如下。若總費用為 {known_output}，求輸入量 x。"
        ),
        "givens": {
            "slope": slope,
            "intercept": intercept,
            "input_min": input_min,
            "input_max": input_max,
            "known_output": known_output,
        },
        "answer": {"canonical_form": target_input},
        "semantic_answer": target_input,
        "distractors": [],
        "explanation_steps": [
            f"由 {known_output}={slope}x+{intercept} 反解 x。",
            f"x=({known_output}-{intercept})/{slope}={target_input}。",
        ],
        "validation_facts": {
            "slope": slope,
            "intercept": intercept,
            "input_min": input_min,
            "input_max": input_max,
            "target_input": target_input,
            "known_output": known_output,
            "forward_output": slope * target_input + intercept,
            "inverse_solution": (known_output - intercept) // slope,
            "unique_solution": True,
        },
        "visual_spec": {
            "kind": "linear_application_graph",
            "x_range": [input_min, input_max],
            "line": {
                "slope": slope,
                "intercept": intercept,
                "points": [
                    [input_min, slope * input_min + intercept],
                    [input_max, slope * input_max + intercept],
                ],
            },
            "known_output": known_output,
        },
        "answer_type": "numeric",
        "presentation_mode": "graph_short_answer",
        "topology_tags": [
            "contextual_application",
            "graph_reading",
            "inverse_evaluation",
        ],
    }


def build_linear_equation_from_two_points_choice_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a four-choice line equation task from two points."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    line_kind = str(
        normalized.get(
            "line_kind",
            rng.choice(["vertical", "horizontal", "oblique"]),
        )
    )
    offset = int(
        normalized.get(
            "offset",
            rng.choice([value for value in range(-6, 7) if value]),
        )
    )
    if line_kind == "vertical":
        point_1, point_2 = (offset, -2), (offset, 3)
        slope: int | None = None
        equation = f"x={offset}"
        option_values = [
            equation,
            f"y={offset}",
            f"x={offset + 1}",
            f"y={offset + 1}",
        ]
    elif line_kind == "horizontal":
        point_1, point_2 = (-2, offset), (3, offset)
        slope = 0
        equation = f"y={offset}"
        option_values = [
            equation,
            f"x={offset}",
            f"y={offset + 1}",
            f"x={offset + 1}",
        ]
    elif line_kind == "oblique":
        slope = int(
            normalized.get("slope", rng.choice([-3, -2, -1, 1, 2, 3]))
        )
        if slope == 0:
            raise ValueError("oblique_slope_must_be_nonzero")
        point_1 = (-2, slope * -2 + offset)
        point_2 = (3, slope * 3 + offset)
        expression = f"{slope}x"
        if offset > 0:
            expression += f"+{offset}"
        elif offset < 0:
            expression += str(offset)
        equation = f"y={expression}"
        option_values = [
            equation,
            f"y={slope + 1}x{offset:+d}",
            f"y={slope}x{offset + 1:+d}",
            f"y={-slope}x{offset:+d}",
        ]
    else:
        raise ValueError("unsupported_line_kind")
    if len(set(option_values)) != 4:
        raise ValueError("choice_generation_not_unique")
    rng.shuffle(option_values)
    labels = ["A", "B", "C", "D"]
    choices = [
        {"label": label, "text": value, "value": value}
        for label, value in zip(labels, option_values)
    ]
    correct_label = labels[option_values.index(equation)]
    return {
        "question": f"通過點 {point_1}、{point_2} 的直線方程式為何？",
        "givens": {"point_1": point_1, "point_2": point_2},
        "answer": {"correct_label": correct_label},
        "semantic_answer": equation,
        "distractors": [value for value in option_values if value != equation],
        "choices": choices,
        "explanation_steps": [
            "由兩點判斷直線型態與斜率，再代入其中一點求方程式。"
        ],
        "validation_facts": {
            "point_1": point_1,
            "point_2": point_2,
            "line_kind": line_kind,
            "slope": slope,
            "intercept": offset if line_kind != "vertical" else None,
            "x_constant": offset if line_kind == "vertical" else None,
            "equation": equation,
            "correct_label": correct_label,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {"kind": "no_visual"},
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "topology_tags": [
            "two_points",
            "slope_then_intercept",
            "single_choice",
        ],
    }


def build_linear_graph_feasibility_choice_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build graph candidates with exactly one violating a line-family condition."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    required_intercept = int(
        normalized.get(
            "required_intercept",
            rng.choice([value for value in range(-6, 7) if value]),
        )
    )
    feasible_slopes = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4], 3)
    wrong_intercept = required_intercept + rng.choice([-2, -1, 1, 2])
    candidates = [
        {
            "equation": f"y={slope}x{required_intercept:+d}",
            "slope": slope,
            "y_intercept": required_intercept,
            "feasible": True,
        }
        for slope in feasible_slopes
    ]
    impossible_slope = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    impossible_equation = f"y={impossible_slope}x{wrong_intercept:+d}"
    candidates.append(
        {
            "equation": impossible_equation,
            "slope": impossible_slope,
            "y_intercept": wrong_intercept,
            "feasible": False,
        }
    )
    rng.shuffle(candidates)
    labels = ["A", "B", "C", "D"]
    choices = [
        {
            "label": label,
            "text": candidate["equation"],
            "value": candidate["equation"],
        }
        for label, candidate in zip(labels, candidates)
    ]
    correct_label = next(
        label
        for label, candidate in zip(labels, candidates)
        if not candidate["feasible"]
    )
    graph_condition = {
        "required_y_intercept": required_intercept,
        "slope_must_be_nonzero": True,
    }
    return {
        "question": (
            f"下列何者不可能是函數族 $f(x)=ax{required_intercept:+d}$"
            "（a≠0）的圖形？"
        ),
        "givens": {"graph_condition": graph_condition},
        "answer": {"correct_label": correct_label},
        "semantic_answer": impossible_equation,
        "distractors": [
            candidate["equation"]
            for candidate in candidates
            if candidate["feasible"]
        ],
        "choices": choices,
        "explanation_steps": [
            f"此函數族所有圖形的 y 截距都必須是 {required_intercept}。",
            f"{impossible_equation} 的 y 截距不符，因此不可能。",
        ],
        "validation_facts": {
            "graph_condition": graph_condition,
            "candidate_lines": candidates,
            "feasibility_by_equation": {
                candidate["equation"]: candidate["feasible"]
                for candidate in candidates
            },
            "impossible_equation": impossible_equation,
            "correct_label": correct_label,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {
            "kind": "line_graph_choices",
            "graph_condition": graph_condition,
            "candidates": candidates,
        },
        "answer_type": "single_choice",
        "presentation_mode": "graph_single_choice",
        "topology_tags": [
            "intercept_constraint",
            "graph_family",
            "feasibility",
            "single_choice",
        ],
    }


def build_robust_budget_feasibility_choice_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a choice whose one plan stays within budget under either price assignment."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    lower_cost = int(normalized.get("lower_cost", rng.randrange(80, 151, 10)))
    higher_cost = int(
        normalized.get("higher_cost", lower_cost + rng.randrange(20, 81, 10))
    )
    first_quantity = int(normalized.get("first_quantity", rng.randint(8, 20)))
    second_quantity = int(normalized.get("second_quantity", rng.randint(8, 20)))

    def assignment_costs(first: int, second: int) -> list[int]:
        return [
            lower_cost * first + higher_cost * second,
            higher_cost * first + lower_cost * second,
        ]

    baseline_costs = assignment_costs(first_quantity, second_quantity)
    budget = int(
        normalized.get("budget", max(baseline_costs) + rng.randrange(lower_cost))
    )
    quantity_pairs = [
        [first_quantity, second_quantity],
        [first_quantity + 1, second_quantity + 1],
        [first_quantity + 2, second_quantity + 2],
        [first_quantity + 3, second_quantity + 3],
    ]
    rng.shuffle(quantity_pairs)
    labels = ["A", "B", "C", "D"]
    candidates: list[dict[str, object]] = []
    choices: list[dict[str, str]] = []
    for label, pair in zip(labels, quantity_pairs):
        costs = assignment_costs(*pair)
        robust_feasible = max(costs) <= budget
        value = f"({pair[0]},{pair[1]})"
        candidates.append(
            {
                "quantities": pair,
                "assignment_costs": costs,
                "worst_case_cost": max(costs),
                "robust_feasible": robust_feasible,
                "value": value,
            }
        )
        choices.append({"label": label, "text": value, "value": value})
    correct_index = next(
        index
        for index, candidate in enumerate(candidates)
        if candidate["robust_feasible"]
    )
    correct_label = labels[correct_index]
    semantic_answer = str(candidates[correct_index]["value"])
    return {
        "question": (
            f"預算為 {budget} 元，兩種商品單價分別可能為 "
            f"{lower_cost} 元與 {higher_cost} 元，但尚不確定何者較貴。"
            "下列哪一組購買數量在兩種單價安排下都一定不超過預算？"
        ),
        "givens": {
            "budget": budget,
            "possible_unit_costs": [lower_cost, higher_cost],
            "cost_model": "c1*x+c2*y",
        },
        "answer": {"correct_label": correct_label},
        "semantic_answer": semantic_answer,
        "choices": choices,
        "distractors": [
            candidate["value"]
            for candidate in candidates
            if not candidate["robust_feasible"]
        ],
        "explanation_steps": [
            "每組數量都要計算兩種單價互換時的成本。",
            f"{semantic_answer} 的最壞情況成本仍不超過預算。",
        ],
        "validation_facts": {
            "budget_condition": {"operator": "<=", "limit": budget},
            "cost_model": {
                "possible_unit_costs": [lower_cost, higher_cost],
                "assignments": [
                    [lower_cost, higher_cost],
                    [higher_cost, lower_cost],
                ],
            },
            "candidate_plans": candidates,
            "feasibility_by_value": {
                str(candidate["value"]): candidate["robust_feasible"]
                for candidate in candidates
            },
            "correct_label": correct_label,
            "semantic_answer": semantic_answer,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {"kind": "no_visual"},
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "topology_tags": [
            "linear_inequality",
            "uncertain_assignment",
            "robust_feasibility",
            "single_choice",
        ],
    }


def _format_slope_intercept_equation(slope: Fraction, intercept: int) -> str:
    slope_value = Fraction(slope).limit_denominator()
    if slope_value == 1:
        body = "x"
    elif slope_value == -1:
        body = "-x"
    else:
        body = f"{fraction_to_plain(slope_value)}x"
    if intercept > 0:
        return f"y={body}+{intercept}"
    if intercept < 0:
        return f"y={body}{intercept}"
    return f"y={body}"


def build_graph_based_linear_model_equation_matrix(
    *,
    seed: int | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a contextual linear-model choice task from graph intercepts."""
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    intercept = int(
        normalized.get(
            "intercept",
            rng.choice([40, 50, 60, 80]),
        )
    )
    if intercept <= 0:
        raise ValueError("graph_intercept_must_be_positive")
    x_end = int(
        normalized.get(
            "x_end",
            normalized.get("sample_x", rng.choice([200, 400, 500, 800])),
        )
    )
    if x_end <= 0:
        raise ValueError("graph_x_end_must_be_positive")
    slope = Fraction(-intercept, x_end)
    points = [[0, intercept], [x_end, 0]]
    equation = _format_slope_intercept_equation(slope, intercept)
    general_gcd = math.gcd(intercept, x_end)
    coefficient_a = intercept // general_gcd
    coefficient_b = x_end // general_gcd
    constant_c = -(intercept * x_end) // general_gcd
    general_form = f"{coefficient_a}x+{coefficient_b}y{constant_c:+d}=0"
    distractor_slopes = [
        -slope,
        Fraction(-intercept * 2, x_end),
        Fraction(-intercept, x_end * 2) if x_end > 1 else Fraction(-intercept - 1, x_end),
    ]
    option_values = [equation]
    for distractor_slope in distractor_slopes:
        candidate = _format_slope_intercept_equation(distractor_slope, intercept)
        if candidate not in option_values:
            option_values.append(candidate)
        if len(option_values) == 4:
            break
    wrong_intercept = intercept + rng.choice([10, 20, -10])
    if wrong_intercept == intercept or wrong_intercept <= 0:
        wrong_intercept = intercept + 10
    while len(option_values) < 4:
        candidate = _format_slope_intercept_equation(slope, wrong_intercept)
        if candidate not in option_values:
            option_values.append(candidate)
        wrong_intercept += 10
        if wrong_intercept > intercept + 100:
            raise ValueError("choice_generation_not_unique")
    if len(set(option_values)) != 4:
        raise ValueError("choice_generation_not_unique")
    rng.shuffle(option_values)
    labels = ["A", "B", "C", "D"]
    choices = [
        {"label": label, "text": value, "value": value}
        for label, value in zip(labels, option_values)
    ]
    correct_label = labels[option_values.index(equation)]
    x_pad = max(20, x_end // 10)
    y_pad = max(5, intercept // 10)
    axis_range = {
        "x_min": -x_pad,
        "x_max": x_end + x_pad,
        "y_min": -y_pad,
        "y_max": intercept + y_pad,
    }
    return {
        "question": (
            "汽車加滿油後開始行駛，圖中 x 表示行駛距離，y 表示剩餘油量。"
            "依圖求 x 與 y 的關係式。"
        ),
        "givens": {
            "context": "driving_distance_and_remaining_fuel",
            "x_quantity": "行駛距離",
            "y_quantity": "剩餘油量",
            "graph_points": points,
        },
        "answer": {"correct_label": correct_label},
        "semantic_answer": equation,
        "distractors": [value for value in option_values if value != equation],
        "choices": choices,
        "explanation_steps": [
            f"圖形通過 (0,{intercept}) 與 ({x_end},0)。",
            f"斜率為 ({0}-{intercept})/({x_end}-0)={fraction_to_plain(slope)}。",
            f"所以關係式為 {equation}。",
        ],
        "validation_facts": {
            "graph_points": points,
            "slope": fraction_to_plain(slope),
            "intercept": intercept,
            "x_end": x_end,
            "equation": equation,
            "general_form": general_form,
            "correct_label": correct_label,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
            "context": "driving_distance_and_remaining_fuel",
        },
        "visual_spec": {
            "kind": "linear_application_graph",
            "x_label": "行駛距離",
            "y_label": "剩餘油量",
            "points": points,
            "line": {
                "slope": fraction_to_plain(slope),
                "intercept": intercept,
            },
            "axis_range": axis_range,
            "drawable_primitives": [
                {
                    "type": "line",
                    "equation": {
                        "A": coefficient_a,
                        "B": coefficient_b,
                        "C": constant_c,
                    },
                },
                {"type": "axes"},
            ],
        },
        "answer_type": "single_choice",
        "presentation_mode": "graph_single_choice",
        "topology_tags": [
            "contextual_application",
            "graph_reading",
            "equation_from_graph",
            "single_choice",
        ],
    }





def _equivalent_scalar(actual: object, expected: object) -> bool:
    if actual is None or expected is None:
        return actual is expected
    try:
        return Fraction(str(actual).strip()) == Fraction(str(expected).strip())
    except (ValueError, ZeroDivisionError):
        return str(actual).replace(" ", "") == str(expected).replace(" ", "")


def check_multi_part_answer(
    user_answer: object,
    canonical_answer: dict[str, object],
) -> bool:
    if not isinstance(user_answer, dict):
        return False
    required = ("x_intercept", "y_intercept", "function_equation")
    if canonical_answer.get("function_equation") is None:
        required = ("x_intercept", "y_intercept", "line_equation")
    return all(
        key in user_answer
        and _equivalent_scalar(user_answer.get(key), canonical_answer.get(key))
        for key in required
    )

