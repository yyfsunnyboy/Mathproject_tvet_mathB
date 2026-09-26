# -*- coding: utf-8 -*-
"""Plane circle domain for vocational B2 Chapter 4 (exact arithmetic).

Owns mathematical truth for circles in the coordinate plane:
standard form, general form, conversions, validity, and condition solving.

Generation families cover 4-1.1 / 4-1.2 source topologies. Low-level primitives
(center/radius, point–center distance, point–line distance) are reusable for
future 4-2 point/line/tangent families without implementing those families here.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import Any

import sympy as sp

from core.domain.coordinate_geometry.line_equation_domain import get_coordinate_midpoint
from core.gencode.multipart_stem_contract import (
    build_stem_structure,
    stem_structure_to_question_text,
)

# ── operation keys ────────────────────────────────────────────────────────────

IDENTIFY_CR_STANDARD_OP = "identify_center_radius_from_standard"
WRITE_CENTER_RADIUS_OP = "write_circle_from_center_radius"
WRITE_CENTER_POINT_OP = "write_circle_from_center_point"
WRITE_CONDITIONS_MULTI_OP = "write_circle_equations_from_conditions"
LOCUS_CENTER_RADIUS_OP = "interpret_circular_locus_equation"
CIRCLE_FROM_DIAMETER_OP = "circle_from_diameter_endpoints"
EQUAL_RADIUS_ORIGIN_OP = "circle_equal_radius_at_origin"
TRANSLATE_SCALE_OP = "translate_and_scale_circle"
ORIGIN_THROUGH_INTERSECTION_OP = "circle_origin_through_lines_intersection"
SAME_CENTER_AREA_OP = "circle_same_center_scaled_area"
CENTER_TANGENT_LINE_OP = "circle_center_tangent_to_line"
IDENTIFY_CR_GENERAL_OP = "identify_center_radius_from_general"
PARAMETER_RANGE_OP = "solve_circle_parameter_range"
THROUGH_THREE_POINTS_OP = "circle_through_three_points"
CENTER_ON_AXIS_AREA_OP = "circle_center_on_axis_area"
CLASSIFY_GENERAL_GRAPH_OP = "classify_general_circle_graph"
AREA_FROM_GENERAL_OP = "compute_circle_area_from_general"
PRODUCT_FORM_IDENTIFY_OP = "identify_circle_from_product_form"
EVAL_HKR_EXPRESSION_OP = "evaluate_center_radius_expression"

_CORE_OPS = frozenset(
    {
        IDENTIFY_CR_STANDARD_OP,
        WRITE_CENTER_RADIUS_OP,
        WRITE_CENTER_POINT_OP,
        WRITE_CONDITIONS_MULTI_OP,
        LOCUS_CENTER_RADIUS_OP,
        CIRCLE_FROM_DIAMETER_OP,
        EQUAL_RADIUS_ORIGIN_OP,
        TRANSLATE_SCALE_OP,
        ORIGIN_THROUGH_INTERSECTION_OP,
        SAME_CENTER_AREA_OP,
        CENTER_TANGENT_LINE_OP,
        IDENTIFY_CR_GENERAL_OP,
        PARAMETER_RANGE_OP,
        THROUGH_THREE_POINTS_OP,
        CENTER_ON_AXIS_AREA_OP,
        CLASSIFY_GENERAL_GRAPH_OP,
        AREA_FROM_GENERAL_OP,
        PRODUCT_FORM_IDENTIFY_OP,
        EVAL_HKR_EXPRESSION_OP,
    }
)

# Keep string keys here to avoid circular import with circle_plane_gap_coverage.
_GAP_OPS = frozenset(
    {
        "classify_point_vs_circles_multipart",
        "solve_point_circle_parameter_range",
        "identify_point_on_circle_mcq",
        "classify_line_circle_relation",
        "classify_lines_vs_circle_multipart",
        "solve_line_circle_parameter_range",
        "solve_line_circle_tangent_parameter",
        "compute_chord_length",
        "solve_line_circle_relation_ranges_multipart",
        "count_line_circle_intersections",
        "compute_storm_path_length_in_circle",
        "classify_line_circle_relation_mcq",
        "solve_diameter_chord_parameter_mcq",
        "compute_triangle_center_chord_area",
        "solve_axis_tangent_parameter",
        "tangent_at_point_on_circle",
        "tangents_parallel_to_line",
        "tangents_perpendicular_to_line",
        "compute_tangents_from_point_quad_area",
        "compute_tangent_segment_lengths",
        "count_line_vs_two_circles_intersections",
        "compute_tangent_segment_length_mcq",
        "solve_circle_parameter_range_mcq",
        "tangent_at_point_on_circle_mcq",
    }
)

OPS = frozenset(set(_CORE_OPS) | set(_GAP_OPS))


# ── exact display helpers ─────────────────────────────────────────────────────

def canonical_exact(value: Any) -> str:
    """Student-facing exact scalar (no float noise)."""
    from core.gencode.resources.rational_display import (
        compact_float_noise_token,
        fraction_to_plain,
        sanitize_float_noise_in_text,
    )

    if isinstance(value, float):
        if abs(value) < 1e-15:
            return "0"
        try:
            return fraction_to_plain(value)
        except Exception:
            return compact_float_noise_token(str(value))
    expr = sp.simplify(sp.sympify(value))
    if isinstance(expr, sp.Float) or getattr(expr, "is_Float", False):
        try:
            expr = sp.nsimplify(expr, rational=True)
        except Exception:
            pass
    expr = sp.radsimp(expr)
    if expr == 0:
        return "0"
    text = sp.sstr(expr, order="lex")
    return sanitize_float_noise_in_text(text)


def _json_value(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _json_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_value(v) for v in obj]
    if isinstance(obj, Fraction):
        return canonical_exact(sp.Rational(obj.numerator, obj.denominator))
    if isinstance(obj, sp.Basic):
        return canonical_exact(obj)
    if isinstance(obj, float):
        return canonical_exact(sp.nsimplify(obj))
    return obj


def _as_pair(value: Any, *, name: str = "point") -> tuple[sp.Expr, sp.Expr]:
    if isinstance(value, dict):
        if "x" in value and "y" in value:
            return sp.simplify(sp.sympify(value["x"])), sp.simplify(sp.sympify(value["y"]))
        if "h" in value and "k" in value:
            return sp.simplify(sp.sympify(value["h"])), sp.simplify(sp.sympify(value["k"]))
        if "0" in value and "1" in value:
            return sp.simplify(sp.sympify(value["0"])), sp.simplify(sp.sympify(value["1"]))
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return sp.simplify(sp.sympify(value[0])), sp.simplify(sp.sympify(value[1]))
    raise ValueError(f"{name}_must_be_coordinate_pair")


def format_pair(x: Any, y: Any) -> str:
    return f"({canonical_exact(x)}, {canonical_exact(y)})"


def latex_pair(x: Any, y: Any) -> str:
    from core.gencode.resources.rational_display import fraction_to_latex

    try:
        left = fraction_to_latex(x)
    except Exception:
        left = canonical_exact(x)
    try:
        right = fraction_to_latex(y)
    except Exception:
        right = canonical_exact(y)
    return rf"\left( {left},\ {right} \right)"


def _signed_shift_term(var: str, center: Any) -> str:
    """Format (x-h) or (y-k) without double signs: (x-3), (x+2), x."""
    c = sp.simplify(sp.sympify(center))
    if c == 0:
        return var
    plain = canonical_exact(c)
    if plain.startswith("-"):
        return f"({var}+{plain[1:]})"
    return f"({var}-{plain})"


def _latex_signed_shift(var: str, center: Any) -> str:
    c = sp.simplify(sp.sympify(center))
    if c == 0:
        return var
    from core.gencode.resources.rational_display import fraction_to_latex

    try:
        plain = fraction_to_latex(c)
    except Exception:
        plain = canonical_exact(c)
    if str(plain).startswith("-"):
        return rf"\left( {var}+{str(plain)[1:]} \right)"
    return rf"\left( {var}-{plain} \right)"


def format_standard_equation(h: Any, k: Any, r2: Any, *, as_r_squared: bool = True) -> str:
    """Clean classroom standard form, e.g. (x-3)^2+(y+2)^2=25."""
    left = f"{_signed_shift_term('x', h)}^2+{_signed_shift_term('y', k)}^2"
    rhs = canonical_exact(sp.simplify(sp.sympify(r2)))
    if not as_r_squared:
        r = sp.simplify(sp.sqrt(sp.sympify(r2)))
        if sp.simplify(r**2 - sp.sympify(r2)) == 0 and r.is_rational:
            rhs = f"{canonical_exact(r)}^2"
    return f"{left}={rhs}"


def latex_standard_equation(h: Any, k: Any, r2: Any) -> str:
    left = (
        rf"{_latex_signed_shift('x', h)}^{{2}}"
        rf"+{_latex_signed_shift('y', k)}^{{2}}"
    )
    return rf"{left}={canonical_exact(sp.simplify(sp.sympify(r2)))}"


def _coeff_term(coeff: Any, symbol: str) -> str:
    c = sp.simplify(sp.sympify(coeff))
    if c == 0:
        return ""
    plain = canonical_exact(c)
    if plain == "1":
        return f"+{symbol}"
    if plain == "-1":
        return f"-{symbol}"
    if plain.startswith("-"):
        return f"{plain}{symbol}"
    return f"+{plain}{symbol}"


def format_general_equation(d: Any, e: Any, f: Any) -> str:
    """x^2+y^2+Dx+Ey+F=0 with clean coefficients."""
    body = "x^2+y^2"
    body += _coeff_term(d, "x")
    body += _coeff_term(e, "y")
    ff = sp.simplify(sp.sympify(f))
    if ff != 0:
        plain = canonical_exact(ff)
        body += plain if plain.startswith("-") else f"+{plain}"
    return f"{body}=0"


def latex_general_equation(d: Any, e: Any, f: Any) -> str:
    body = "x^{2}+y^{2}"
    dd = sp.simplify(sp.sympify(d))
    ee = sp.simplify(sp.sympify(e))
    ff = sp.simplify(sp.sympify(f))
    for coeff, sym in ((dd, "x"), (ee, "y")):
        if coeff == 0:
            continue
        plain = canonical_exact(coeff)
        if plain == "1":
            body += f"+{sym}"
        elif plain == "-1":
            body += f"-{sym}"
        elif plain.startswith("-"):
            body += f"{plain}{sym}"
        else:
            body += f"+{plain}{sym}"
    if ff != 0:
        plain = canonical_exact(ff)
        body += plain if plain.startswith("-") else f"+{plain}"
    return rf"{body}=0"


def point_distance(p1: Any, p2: Any) -> sp.Expr:
    """Exact Euclidean distance (same formula as coordinate distance domain)."""
    x1, y1 = _as_pair(p1, name="p1")
    x2, y2 = _as_pair(p2, name="p2")
    return sp.simplify(sp.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


def point_line_distance(point: Any, a: Any, b: Any, c: Any) -> sp.Expr:
    """Exact distance from point to Ax+By+C=0."""
    x0, y0 = _as_pair(point, name="point")
    aa, bb, cc = sp.sympify(a), sp.sympify(b), sp.sympify(c)
    return sp.simplify(sp.Abs(aa * x0 + bb * y0 + cc) / sp.sqrt(aa**2 + bb**2))


def lines_intersection(
    a1: Any, b1: Any, c1: Any, a2: Any, b2: Any, c2: Any
) -> tuple[sp.Expr, sp.Expr]:
    """Solve A1x+B1y+C1=0 and A2x+B2y+C2=0."""
    x, y = sp.symbols("x y")
    sols = sp.solve(
        [sp.Eq(sp.sympify(a1) * x + sp.sympify(b1) * y + sp.sympify(c1), 0),
         sp.Eq(sp.sympify(a2) * x + sp.sympify(b2) * y + sp.sympify(c2), 0)],
        [x, y],
        dict=True,
    )
    if not sols:
        raise ValueError("lines_do_not_intersect")
    return sp.simplify(sols[0][x]), sp.simplify(sols[0][y])


# ── canonical circle structure ────────────────────────────────────────────────

def make_circle(*, h: Any, k: Any, r2: Any | None = None, r: Any | None = None) -> dict[str, Any]:
    hh = sp.simplify(sp.sympify(h))
    kk = sp.simplify(sp.sympify(k))
    if r2 is None:
        if r is None:
            raise ValueError("radius_or_r2_required")
        rr = sp.simplify(sp.sympify(r))
        r2_val = sp.simplify(rr**2)
    else:
        r2_val = sp.simplify(sp.sympify(r2))
        rr = sp.simplify(sp.sqrt(r2_val))
    if sp.simplify(r2_val) < 0:
        raise ValueError("negative_radius_squared")
    d = sp.simplify(-2 * hh)
    e = sp.simplify(-2 * kk)
    f = sp.simplify(hh**2 + kk**2 - r2_val)
    return {
        "center": {"h": hh, "k": kk},
        "h": hh,
        "k": kk,
        "radius": rr,
        "r": rr,
        "radius_squared": r2_val,
        "r2": r2_val,
        "general": {"D": d, "E": e, "F": f},
        "D": d,
        "E": e,
        "F": f,
        "standard_form": format_standard_equation(hh, kk, r2_val),
        "general_form": format_general_equation(d, e, f),
        "latex_standard": latex_standard_equation(hh, kk, r2_val),
        "latex_general": latex_general_equation(d, e, f),
    }


def circle_semantic_key(equation_text: Any) -> str:
    """Normalize circle equation text to general-form (D,E,F) for MCQ uniqueness."""
    raw = str(equation_text or "").strip()
    if not raw:
        return ""
    try:
        parsed = parse_circle_equation_to_general(raw)
        d, e, f = parsed["D"], parsed["E"], parsed["F"]
        return f"D={canonical_exact(d)};E={canonical_exact(e)};F={canonical_exact(f)}"
    except Exception:
        cleaned = re.sub(r"\s+", "", raw).casefold()
        return cleaned


def parse_circle_equation_to_general(text: str) -> dict[str, sp.Expr]:
    """Parse classroom circle equation into monic general coefficients D,E,F."""
    src = str(text or "").strip().strip("$")
    src = src.replace(r"\left", "").replace(r"\right", "")
    src = src.replace(r"\,", "").replace(r"\ ", "")
    src = re.sub(r"\^\{?2\}?", "**2", src)
    src = src.replace("{", "").replace("}", "")
    # Insert implicit multiplication: 2x → 2*x, )( → )*(
    src = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", src)
    src = src.replace(")(", ")*(")
    if "=" not in src:
        raise ValueError("equation_missing_equals")
    left, right = src.split("=", 1)
    x, y = sp.symbols("x y")
    expr = sp.expand(sp.sympify(left) - sp.sympify(right))
    poly = sp.Poly(expr, x, y)
    a = poly.coeff_monomial(x**2)
    b = poly.coeff_monomial(y**2)
    if a == 0 and b == 0:
        raise ValueError("not_a_circle_equation")
    scale = a if a != 0 else b
    expr = sp.expand(expr / scale)
    poly = sp.Poly(expr, x, y)
    d = sp.simplify(poly.coeff_monomial(x))
    e = sp.simplify(poly.coeff_monomial(y))
    f = sp.simplify(expr.subs({x: 0, y: 0}))
    return {"D": d, "E": e, "F": f, "expr": expr}


# ── pure mathematical operations ──────────────────────────────────────────────

def circle_from_center_radius(*, center: Any, radius: Any) -> dict[str, Any]:
    h, k = _as_pair(center, name="center")
    r = sp.simplify(sp.sympify(radius))
    if r <= 0:
        raise ValueError("radius_must_be_positive")
    circle = make_circle(h=h, k=k, r=r)
    return {
        **circle,
        "canonical": circle["standard_form"],
        "canonical_parts": {
            "圓心": format_pair(h, k),
            "半徑": canonical_exact(r),
            "標準式": circle["standard_form"],
        },
    }


def center_radius_from_standard(*, h: Any, k: Any, r2: Any, scale: Any = 1) -> dict[str, Any]:
    """Identify center/radius from scaled standard: scale*((x-h)^2+(y-k)^2)=rhs ⇒ r2=rhs/scale."""
    sc = sp.simplify(sp.sympify(scale))
    r2_val = sp.simplify(sp.sympify(r2) / sc)
    if r2_val <= 0:
        raise ValueError("non_positive_radius_squared")
    circle = make_circle(h=h, k=k, r2=r2_val)
    return {
        **circle,
        "canonical_parts": {
            "圓心": format_pair(circle["h"], circle["k"]),
            "半徑": canonical_exact(circle["r"]),
        },
        "canonical": {
            "圓心": format_pair(circle["h"], circle["k"]),
            "半徑": canonical_exact(circle["r"]),
        },
    }


def standard_from_center_point(*, center: Any, point: Any) -> dict[str, Any]:
    h, k = _as_pair(center, name="center")
    px, py = _as_pair(point, name="point")
    r2 = sp.simplify((px - h) ** 2 + (py - k) ** 2)
    if r2 <= 0:
        raise ValueError("point_coincides_with_center")
    circle = make_circle(h=h, k=k, r2=r2)
    return {**circle, "canonical": circle["standard_form"]}


def standard_to_general(*, h: Any, k: Any, r2: Any) -> dict[str, Any]:
    circle = make_circle(h=h, k=k, r2=r2)
    return {
        **circle,
        "canonical": circle["general_form"],
        "coefficients": {"D": circle["D"], "E": circle["E"], "F": circle["F"]},
    }


def center_radius_from_general(*, d: Any, e: Any, f: Any, scale: Any = 1) -> dict[str, Any]:
    """From scale*(x^2+y^2)+... or monic x^2+y^2+Dx+Ey+F=0."""
    sc = sp.simplify(sp.sympify(scale))
    dd = sp.simplify(sp.sympify(d) / sc)
    ee = sp.simplify(sp.sympify(e) / sc)
    ff = sp.simplify(sp.sympify(f) / sc)
    h = sp.simplify(-dd / 2)
    k = sp.simplify(-ee / 2)
    r2 = sp.simplify((dd**2 + ee**2) / 4 - ff)
    validity = circle_validity_from_r2(r2)
    result: dict[str, Any] = {
        "D": dd,
        "E": ee,
        "F": ff,
        "h": h,
        "k": k,
        "radius_squared": r2,
        "r2": r2,
        "validity": validity,
        "canonical_parts": {
            "圓心": format_pair(h, k),
            "半徑": canonical_exact(sp.sqrt(r2)) if validity == "circle" else canonical_exact(0),
        },
    }
    if validity == "circle":
        circle = make_circle(h=h, k=k, r2=r2)
        result.update(circle)
        result["canonical"] = {
            "圓心": format_pair(h, k),
            "半徑": canonical_exact(circle["r"]),
        }
    elif validity == "point":
        result["canonical"] = {
            "圓心": format_pair(h, k),
            "半徑": "0",
        }
        result["radius"] = sp.Integer(0)
    else:
        result["canonical"] = {"圖形": "無圖形"}
        result["radius"] = None
    return result


def circle_validity_from_r2(r2: Any) -> str:
    val = sp.simplify(sp.sympify(r2))
    if val > 0:
        return "circle"
    if val == 0:
        return "point"
    return "empty"


def circle_validity_from_general(*, d: Any, e: Any, f: Any, scale: Any = 1) -> dict[str, Any]:
    extracted = center_radius_from_general(d=d, e=e, f=f, scale=scale)
    label_map = {"circle": "圓", "point": "一點", "empty": "無圖形"}
    validity = extracted["validity"]
    return {
        **extracted,
        "label": label_map[validity],
        "canonical": label_map[validity],
    }


def circle_from_diameter(*, a: Any, b: Any) -> dict[str, Any]:
    ax, ay = _as_pair(a, name="A")
    bx, by = _as_pair(b, name="B")
    # Reuse coordinate midpoint helper with plain tokens (avoids SymPy-Zero parse gaps).
    mid_x, mid_y = get_coordinate_midpoint(
        [canonical_exact(ax), canonical_exact(ay)],
        [canonical_exact(bx), canonical_exact(by)],
    )
    h, k = sp.simplify(sp.sympify(mid_x)), sp.simplify(sp.sympify(mid_y))
    r2 = sp.simplify(((bx - ax) ** 2 + (by - ay) ** 2) / 4)
    if r2 <= 0:
        raise ValueError("degenerate_diameter")
    circle = make_circle(h=h, k=k, r2=r2)
    return {**circle, "canonical": circle["standard_form"], "endpoints": (a, b)}


def circle_through_three_points(*, a: Any, b: Any, c: Any) -> dict[str, Any]:
    ax, ay = _as_pair(a, name="A")
    bx, by = _as_pair(b, name="B")
    cx, cy = _as_pair(c, name="C")
    d, e, f = sp.symbols("D E F")
    eqs = [
        sp.Eq(ax**2 + ay**2 + d * ax + e * ay + f, 0),
        sp.Eq(bx**2 + by**2 + d * bx + e * by + f, 0),
        sp.Eq(cx**2 + cy**2 + d * cx + e * cy + f, 0),
    ]
    sols = sp.solve(eqs, [d, e, f], dict=True)
    if not sols:
        raise ValueError("three_points_not_a_circle")
    sol = sols[0]
    extracted = center_radius_from_general(d=sol[d], e=sol[e], f=sol[f])
    if extracted["validity"] != "circle":
        raise ValueError("three_points_degenerate")
    return {
        **extracted,
        "canonical": extracted["general_form"],
        "canonical_standard": extracted["standard_form"],
    }


def solve_circle_parameter_range(
    *,
    d_expr: Any,
    e_expr: Any,
    f_expr: Any,
    param: str = "k",
    strict: bool = True,
) -> dict[str, Any]:
    """Require r^2 > 0 (strict) for real non-degenerate circle."""
    p = sp.symbols(param)
    dd = sp.simplify(sp.sympify(d_expr))
    ee = sp.simplify(sp.sympify(e_expr))
    ff = sp.simplify(sp.sympify(f_expr))
    r2 = sp.simplify((dd**2 + ee**2) / 4 - ff)
    rel = sp.StrictGreaterThan(r2, 0) if strict else sp.GreaterThan(r2, 0)
    sol = sp.solve_univariate_inequality(rel, p, relational=False)
    return {
        "parameter": param,
        "r2_expr": r2,
        "solution_set": sol,
        "canonical": _format_interval(sol, param),
        "latex_interval": _format_interval(sol, param),
    }


def _format_interval(sol: Any, param: str) -> str:
    from core.gencode.resources.rational_display import sanitize_float_noise_in_text

    if isinstance(sol, sp.Interval):
        left, right = sol.start, sol.end
        left_open, right_open = sol.left_open, sol.right_open
        if left == -sp.oo and right != sp.oo:
            op = "<" if right_open else r"\le "
            return f"{param}{op}{canonical_exact(right)}"
        if right == sp.oo and left != -sp.oo:
            op = ">" if left_open else r"\ge "
            return f"{param}{op}{canonical_exact(left)}"
        return sanitize_float_noise_in_text(f"{param}\\in {sp.sstr(sol)}")
    if isinstance(sol, sp.Union):
        return r"\cup".join(_format_interval(arg, param) for arg in sol.args)
    text = sp.sstr(sol)
    # SymPy set string fallbacks for open rays
    m = re.search(r"Interval\.open\(([^,]+),\s*oo\)", text)
    if m:
        return f"{param}>{canonical_exact(sp.sympify(m.group(1)))}"
    m = re.search(r"Interval\.open\(-oo,\s*([^)]+)\)", text)
    if m:
        return f"{param}<{canonical_exact(sp.sympify(m.group(1)))}"
    return sanitize_float_noise_in_text(text)


# ── sampling helpers ──────────────────────────────────────────────────────────

def _sample_int(rng: random.Random, lo: int = -5, hi: int = 5, *, nonzero: bool = False) -> int:
    vals = [i for i in range(lo, hi + 1) if (not nonzero or i != 0)]
    return rng.choice(vals)


def _sample_point(rng: random.Random, *, nonzero: bool = False) -> list[int]:
    for _ in range(40):
        p = [_sample_int(rng), _sample_int(rng)]
        if nonzero and p == [0, 0]:
            continue
        return p
    return [2, -1]


def _sample_radius(rng: random.Random) -> int:
    return rng.choice([1, 2, 3, 4, 5, 6])


def _sample_r2_perfect(rng: random.Random) -> int:
    r = _sample_radius(rng)
    return r * r


def _mcq_pack(correct: str, distractors: list[str], rng: random.Random) -> dict[str, Any]:
    from core.gencode.choice_contract_validator import choice_semantic_key, infer_choice_answer_shape

    target_shape = infer_choice_answer_shape(correct)

    def _shape_ok(candidate: str) -> bool:
        shape = infer_choice_answer_shape(candidate)
        if target_shape in {"expression", "empty"}:
            return True
        if shape == target_shape:
            return True
        if target_shape == "area_or_pi" and shape in {"area_or_pi", "number"}:
            return True
        if target_shape == "number" and shape == "area_or_pi":
            return True
        return False

    seen = {choice_semantic_key(correct)}
    unique_d: list[str] = []
    for d in distractors:
        if not _shape_ok(d):
            continue
        key = choice_semantic_key(d)
        if not key or key in seen:
            continue
        seen.add(key)
        unique_d.append(d)
        if len(unique_d) >= 3:
            break
    equation_pool = [
        "x^2+y^2=1",
        "x^2+y^2=4",
        "x^2+y^2=9",
        "x^2+y^2=16",
        "x^2+y^2=25",
        "(x-1)^2+(y-1)^2=4",
        "(x+1)^2+(y-1)^2=9",
        "(x-2)^2+(y+3)^2=16",
        "x^2+y^2+2x+2y=0",
        "x^2+y^2-2x+4y-4=0",
    ]
    area_pool = ["4\\pi", "9\\pi", "16\\pi", "25\\pi", "36\\pi", "1\\pi", "8\\pi"]
    number_pool = ["2", "4", "5", "6", "8", "9", "10", "12", "16", "25"]
    param_pool = ["k>0", "k<0", "k>1", "k<-1", "k≥0", "k≤0"]
    class_pool = ["相離", "相切", "相交", "圓內", "圓外", "圓上"]
    if target_shape == "equation":
        filler_pool = equation_pool + number_pool
    elif target_shape == "area_or_pi":
        filler_pool = area_pool + number_pool
    elif target_shape == "number":
        filler_pool = number_pool + area_pool
    elif target_shape == "interval_or_param":
        filler_pool = param_pool + number_pool
    elif target_shape == "classification":
        filler_pool = class_pool + number_pool
    elif target_shape == "coordinate":
        filler_pool = ["(0,0)", "(1,0)", "(0,1)", "(2,2)", "(-1,1)"] + number_pool
    else:
        filler_pool = number_pool + area_pool + param_pool
    for filler in filler_pool:
        if len(unique_d) >= 3:
            break
        if not _shape_ok(filler):
            continue
        key = choice_semantic_key(filler)
        if key and key not in seen:
            seen.add(key)
            unique_d.append(filler)
    if len(unique_d) < 3:
        raise ValueError("insufficient_distinct_mcq_distractors")
    labels = ["A", "B", "C", "D"]
    options = [correct] + unique_d[:3]
    rng.shuffle(options)
    choices = [{"label": labels[i], "value": options[i], "text": options[i]} for i in range(4)]
    correct_key = choice_semantic_key(correct)
    correct_label = next(
        c["label"] for c in choices if choice_semantic_key(c["value"]) == correct_key
    )
    return {
        "choices": choices,
        "correct_label": correct_label,
        "semantic_answer": correct,
        "answer_type": "single_choice",
        "presentation": "single_choice",
        "expected_answer_shape": target_shape,
        "choice_answer_shape": target_shape,
    }


# ── matrix builder ────────────────────────────────────────────────────────────

def build_circle_plane_matrix(
    *,
    operation: str | None = None,
    domain_operation: str | None = None,
    constraints: dict[str, Any] | None = None,
    seed: int | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    **data: Any,
) -> dict[str, Any]:
    op = str(operation or domain_operation or "").strip()
    if op in _GAP_OPS:
        from core.domain.circle_plane_gap_coverage import build_gap_matrix

        return build_gap_matrix(
            operation=op,
            seed=seed,
            constraints=constraints,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            **data,
        )
    if op not in OPS:
        raise ValueError(f"unsupported_circle_plane_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    payload = {**dict(constraints or {}), **data}
    for bookkeeping in (
        "skill_id",
        "phase1_classification",
        "v3_induced_spec",
        "classification_status",
        "source_hash",
        "required_capabilities",
        "answer_contract",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "textbook_example_id",
        "source_example_id",
        "classification_source",
    ):
        payload.pop(bookkeeping, None)

    visual_spec: dict[str, Any] | None = None
    distractors: list[str] = []
    presentation = "short_answer"
    answer_type = "expression"
    parts: dict[str, Any] = {}
    choices: list[dict[str, Any]] | None = None
    correct_label: str | None = None
    semantic_answer: Any = None
    explanation: list[str] = []
    stem_structure: dict[str, Any] | None = None
    part_labels_override: dict[str, str] | None = None

    if op == IDENTIFY_CR_STANDARD_OP:
        items = []
        if "items" in payload:
            items = list(payload["items"])
        else:
            # Three equations: plain, shifted, scaled — mirrors textbook multipart
            h1, k1, r2_1 = 0, 0, rng.choice([4, 9, 16, 25])
            h2, k2 = _sample_int(rng, -4, 4, nonzero=True), _sample_int(rng, -4, 4)
            r2_2 = _sample_r2_perfect(rng)
            h3, k3 = _sample_int(rng, -5, 5, nonzero=True), 0
            scale3 = rng.choice([4, 9])
            r2_3 = rng.choice([1, 4, 9])
            items = [
                {"h": h1, "k": k1, "r2": r2_1, "scale": 1},
                {"h": h2, "k": k2, "r2": r2_2, "scale": 1},
                {"h": h3, "k": k3, "r2": r2_3, "scale": scale3},
            ]
        stem_items: list[dict[str, str]] = []
        part_answers: dict[str, Any] = {}
        for idx, item in enumerate(items, 1):
            sc = sp.sympify(item.get("scale", 1))
            hh, kk, r2 = item["h"], item["k"], item["r2"]
            extracted = center_radius_from_standard(h=hh, k=kk, r2=r2, scale=sc)
            if sc == 1:
                eq_body = f"${latex_standard_equation(hh, kk, r2)}$"
            else:
                hx = _latex_signed_shift("x", hh)
                ky = _latex_signed_shift("y", kk)
                eq_body = (
                    f"${canonical_exact(sc)}{hx}^{{2}}+{canonical_exact(sc)}{ky}^{{2}}"
                    f"={canonical_exact(r2)}$"
                )
            stem_items.append({"group_label": f"({idx})", "text": eq_body})
            part_answers[f"({idx})圓心"] = extracted["canonical_parts"]["圓心"]
            part_answers[f"({idx})半徑"] = extracted["canonical_parts"]["半徑"]
        stem_structure = build_stem_structure(
            "根據下列各圓的方程式，試求該圓的圓心和半徑。",
            stem_items,
        )
        question = stem_structure_to_question_text(stem_structure)
        parts = part_answers
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        explanation = ["將方程式化為標準式後讀出圓心與半徑。"]
        result = {"items": items, "parts": parts}

    elif op == WRITE_CENTER_RADIUS_OP:
        if "center" not in payload:
            payload["center"] = _sample_point(rng)
        if "radius" not in payload:
            payload["radius"] = _sample_radius(rng)
        result = circle_from_center_radius(center=payload["center"], radius=payload["radius"])
        h, k = result["h"], result["k"]
        question = (
            f"試求以點 ${latex_pair(h, k)}$ 為圓心、半徑為 ${canonical_exact(result['r'])}$ 的圓方程式。"
        )
        answer_value = result["standard_form"]
        explanation = [f"標準式為 ${result['latex_standard']}$。"]

    elif op == WRITE_CENTER_POINT_OP:
        if "center" not in payload:
            payload["center"] = _sample_point(rng)
        if "point" not in payload:
            c = payload["center"]
            payload["point"] = [c[0] + rng.choice([2, 3, -2]), c[1] + rng.choice([-1, 2, 3])]
        result = standard_from_center_point(center=payload["center"], point=payload["point"])
        h, k = result["h"], result["k"]
        px, py = _as_pair(payload["point"])
        question = (
            f"試求以點 ${latex_pair(h, k)}$ 為圓心，且通過點 ${latex_pair(px, py)}$ 的圓方程式。"
        )
        answer_value = result["standard_form"]
        explanation = ["半徑平方為圓心到已知點距離平方。"]

    elif op == WRITE_CONDITIONS_MULTI_OP:
        if "center1" not in payload:
            payload["center1"] = _sample_point(rng)
            payload["radius1"] = _sample_radius(rng)
            payload["center2"] = _sample_point(rng)
            c2 = payload["center2"]
            payload["point2"] = [c2[0] + 2, c2[1] - 2]
        r1 = circle_from_center_radius(center=payload["center1"], radius=payload["radius1"])
        r2 = standard_from_center_point(center=payload["center2"], point=payload["point2"])
        h1, k1 = r1["h"], r1["k"]
        h2, k2 = r2["h"], r2["k"]
        px, py = _as_pair(payload["point2"])
        stem_items = [
            {
                "group_label": "(1)",
                "text": (
                    f"以點 ${latex_pair(h1, k1)}$ 為圓心，"
                    f"半徑為 ${canonical_exact(r1['r'])}$ 的圓。"
                ),
            },
            {
                "group_label": "(2)",
                "text": (
                    f"以點 ${latex_pair(h2, k2)}$ 為圓心，"
                    f"且過點 ${latex_pair(px, py)}$ 的圓。"
                ),
            },
        ]
        stem_structure = build_stem_structure("試求滿足下列條件的圓方程式：", stem_items)
        question = stem_structure_to_question_text(stem_structure)
        parts = {"(1)": r1["standard_form"], "(2)": r2["standard_form"]}
        part_labels_override = {"(1)": "方程式", "(2)": "方程式"}
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        result = {"part1": r1, "part2": r2}
        explanation = ["(1) 代入圓心半徑；(2) 以距離平方為半徑平方。"]

    elif op == LOCUS_CENTER_RADIUS_OP:
        if "center" not in payload:
            payload["center"] = _sample_point(rng, nonzero=True)
        if "radius" not in payload:
            payload["radius"] = _sample_radius(rng)
        result = circle_from_center_radius(center=payload["center"], radius=payload["radius"])
        h, k = result["h"], result["k"]
        question = (
            f"一動點與定點 ${latex_pair(h, k)}$ 的距離恆為 ${canonical_exact(result['r'])}$。"
            f"試問：(1) 此動點軌跡是什麼圖形？(2) 此圖形的方程式為何？"
        )
        parts = {"圖形": "圓", "方程式": result["standard_form"]}
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        explanation = ["與定點等距的軌跡為圓。"]

    elif op == CIRCLE_FROM_DIAMETER_OP:
        if "a" not in payload or "b" not in payload:
            payload["a"] = _sample_point(rng)
            for _ in range(30):
                payload["b"] = [
                    payload["a"][0] + rng.choice([-6, -4, -2, 2, 4, 6]),
                    payload["a"][1] + rng.choice([-6, -4, -2, 2, 4, 6]),
                ]
                if payload["b"] != payload["a"]:
                    break
            else:
                payload["b"] = [payload["a"][0] + 4, payload["a"][1] - 2]
        result = circle_from_diameter(a=payload["a"], b=payload["b"])
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        as_mcq = bool(payload.get("as_mcq"))
        question = (
            f"設平面上兩點 $A{latex_pair(ax, ay)}$、$B{latex_pair(bx, by)}$，"
            f"試求以 $\\overline{{AB}}$ 為直徑的圓方程式。"
        )
        answer_value = result["standard_form"]
        if as_mcq:
            distractors = [
                format_standard_equation(result["h"] + 1, result["k"], result["r2"]),
                format_standard_equation(result["h"], result["k"] + 1, result["r2"]),
                format_standard_equation(ax, ay, result["r2"]),
            ]
            pack = _mcq_pack(result["standard_form"], distractors, rng)
            choices, correct_label = pack["choices"], pack["correct_label"]
            semantic_answer = pack["semantic_answer"]
            answer_type = "single_choice"
            presentation = "single_choice"
            answer_value = correct_label
        explanation = ["圓心為中點，半徑為弦長一半。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "points": [
                {"id": "A", "x": float(ax), "y": float(ay)},
                {"id": "B", "x": float(bx), "y": float(by)},
            ],
            "circles": [
                {
                    "h": float(result["h"]),
                    "k": float(result["k"]),
                    "r": float(sp.N(result["r"])),
                }
            ],
            "requirement": "diameter_endpoints",
            "implemented": False,
        }

    elif op == EQUAL_RADIUS_ORIGIN_OP:
        if "ref_h" not in payload:
            payload["ref_h"] = _sample_int(rng, -5, 5, nonzero=True)
            payload["ref_k"] = _sample_int(rng, -5, 5)
            payload["ref_r2"] = _sample_r2_perfect(rng)
        result = make_circle(h=0, k=0, r2=payload["ref_r2"])
        question = (
            f"某圓圓心在原點，半徑與圓 "
            f"$C:{latex_standard_equation(payload['ref_h'], payload['ref_k'], payload['ref_r2'])}$ "
            f"的半徑相等，試求此圓方程式。"
        )
        answer_value = result["standard_form"]
        explanation = ["半徑相同且圓心為原點。"]

    elif op == TRANSLATE_SCALE_OP:
        if "h0" not in payload:
            payload["h0"] = _sample_int(rng, -5, 5, nonzero=True)
            payload["k0"] = _sample_int(rng, -5, 5, nonzero=True)
            payload["r0"] = rng.choice([1, 2, 4])
            payload["dh"] = rng.choice([-2, -1, 1, 2])
            payload["dk"] = rng.choice([-2, -1, 1, 2])
            payload["r_factor"] = rng.choice([sp.Rational(1, 2), sp.Rational(3, 2), 2])
        h0, k0, r0 = payload["h0"], payload["k0"], payload["r0"]
        dh, dk = payload["dh"], payload["dk"]
        factor = sp.simplify(sp.sympify(payload["r_factor"]))
        new_h, new_k = sp.simplify(sp.sympify(h0) + dh), sp.simplify(sp.sympify(k0) + dk)
        new_r = sp.simplify(sp.sympify(r0) * factor)
        result = make_circle(h=new_h, k=new_k, r=new_r)
        form = str(payload.get("answer_form") or "standard")
        answer_value = result["general_form"] if form == "general" else result["standard_form"]
        question = (
            f"圓方程式為 ${latex_standard_equation(h0, k0, sp.Integer(r0) ** 2)}$。"
            f"圓心平移至 ${latex_pair(new_h, new_k)}$，半徑變為原來的 ${canonical_exact(factor)}$ 倍，"
            f"試求新圓方程式"
            + ("（一般式）。" if form == "general" else "。")
        )
        as_mcq = bool(payload.get("as_mcq") or payload.get("force_mcq"))
        if payload.get("force_short"):
            as_mcq = False
        if as_mcq and form != "general":
            distractors = [
                format_standard_equation(new_h + 1, new_k, result["r2"]),
                format_standard_equation(h0, k0, result["r2"]),
                format_standard_equation(new_h, new_k, sp.Integer(r0) ** 2),
            ]
            pack = _mcq_pack(result["standard_form"], distractors, rng)
            choices, correct_label = pack["choices"], pack["correct_label"]
            semantic_answer = pack["semantic_answer"]
            answer_type = "single_choice"
            presentation = "single_choice"
            answer_value = correct_label
        explanation = ["依平移後圓心與縮放後半徑寫出方程式。"]

    elif op == ORIGIN_THROUGH_INTERSECTION_OP:
        if "a1" not in payload:
            # Prefer clean Pythagorean intersection distances from origin
            payload.update({"a1": 3, "b1": 2, "c1": -4, "a2": 2, "b2": 3, "c2": -1})
        ix, iy = lines_intersection(
            payload["a1"], payload["b1"], payload["c1"],
            payload["a2"], payload["b2"], payload["c2"],
        )
        r2 = sp.simplify(ix**2 + iy**2)
        result = make_circle(h=0, k=0, r2=r2)
        question = (
            f"以原點為圓心，通過二直線 "
            f"${canonical_exact(payload['a1'])}x+{canonical_exact(payload['b1'])}y"
            f"={canonical_exact(-sp.sympify(payload['c1']))}$ 與 "
            f"${canonical_exact(payload['a2'])}x+{canonical_exact(payload['b2'])}y"
            f"={canonical_exact(-sp.sympify(payload['c2']))}$ "
            f"交點的圓方程式為"
        )
        distractors = [
            format_standard_equation(0, 0, r2 + 1),
            format_standard_equation(0, 0, r2 - 1 if r2 > 1 else r2 + 2),
            format_standard_equation(0, 0, 2 * r2),
        ]
        pack = _mcq_pack(result["standard_form"], distractors, rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["先求兩直線交點，再以原點到該點距離平方為半徑平方。"]

    elif op == SAME_CENTER_AREA_OP:
        if "h" not in payload:
            payload["h"] = _sample_int(rng, -4, 4, nonzero=True)
            payload["k"] = _sample_int(rng, -4, 4)
            payload["r2"] = 16
            payload["area_factor"] = sp.Rational(1, 2)
        factor = sp.simplify(sp.sympify(payload["area_factor"]))
        new_r2 = sp.simplify(sp.sympify(payload["r2"]) * factor)
        result = make_circle(h=payload["h"], k=payload["k"], r2=new_r2)
        question = (
            f"與 $C_1:{latex_standard_equation(payload['h'], payload['k'], payload['r2'])}$ "
            f"有相同圓心，且面積為圓 $C_1$ 面積的 ${canonical_exact(factor)}$ 的圓方程式為"
        )
        distractors = [
            format_standard_equation(payload["h"], payload["k"], payload["r2"]),
            format_standard_equation(payload["h"], payload["k"], sp.sympify(payload["r2"]) / 4),
            format_standard_equation(0, 0, new_r2),
        ]
        pack = _mcq_pack(result["standard_form"], distractors, rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["面積比等於半徑平方比。"]

    elif op == CENTER_TANGENT_LINE_OP:
        if "center" not in payload:
            # 3x+4y-5=0 style with center (-3,-4) → distance 6
            payload["center"] = [-3, -4]
            payload["a"], payload["b"], payload["c"] = 3, 4, -5
        dist = point_line_distance(payload["center"], payload["a"], payload["b"], payload["c"])
        result = circle_from_center_radius(center=payload["center"], radius=dist)
        h, k = result["h"], result["k"]
        question = (
            f"已知直線 ${canonical_exact(payload['a'])}x+{canonical_exact(payload['b'])}y"
            f"={canonical_exact(-sp.sympify(payload['c']))}$，"
            f"圓心為 ${latex_pair(h, k)}$ 且與該直線相切，則圓方程式為何？"
        )
        distractors = [
            format_standard_equation(h, k, (result["r"] + 1) ** 2),
            format_standard_equation(h, k, (result["r"] - 1) ** 2 if result["r"] > 1 else 4),
            format_standard_equation(0, 0, result["r2"]),
        ]
        pack = _mcq_pack(result["standard_form"], distractors, rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["相切 ⇒ 半徑等於圓心到直線距離。"]

    elif op == IDENTIFY_CR_GENERAL_OP:
        items = payload.get("items")
        if not items:
            items = [
                {"d": -2, "e": 4, "f": -11, "scale": 1},
                {
                    "d": rng.choice([-6, -4, 4, 6]),
                    "e": rng.choice([-6, -2, 2, 6]),
                    "f": rng.choice([-9, -4, 2, 6]),
                    "scale": rng.choice([1, 2, 3, 4]),
                },
            ]
            # Ensure valid circles
            fixed = []
            for it in items:
                for _ in range(30):
                    ext = center_radius_from_general(
                        d=it["d"], e=it["e"], f=it["f"], scale=it.get("scale", 1)
                    )
                    if ext["validity"] == "circle":
                        fixed.append(it)
                        break
                    it = {
                        "d": _sample_int(rng, -8, 8, nonzero=True),
                        "e": _sample_int(rng, -8, 8, nonzero=True),
                        "f": _sample_int(rng, -12, 5),
                        "scale": it.get("scale", 1),
                    }
                else:
                    fixed.append({"d": -4, "e": 2, "f": -4, "scale": 1})
            items = fixed
        stem_items: list[dict[str, str]] = []
        part_answers: dict[str, Any] = {}
        extracted_list = []
        for idx, it in enumerate(items, 1):
            sc = sp.Integer(it.get("scale", 1))
            dd, ee, ff = sp.Integer(it["d"]), sp.Integer(it["e"]), sp.Integer(it["f"])
            if sc == 1:
                eq_body = f"${latex_general_equation(dd, ee, ff)}$"
            else:
                # scale*x^2+scale*y^2+(scale*d? wait: store unscaled D,E,F on monic then multiply
                # Convention: coefficients are for scale*(x^2+y^2) + D_raw x + ... where
                # monic D = D_raw/scale. Display: scale x^2 + scale y^2 + D_raw x + ...
                eq_body = (
                    f"${canonical_exact(sc)}x^{{2}}+{canonical_exact(sc)}y^{{2}}"
                    f"{_coeff_term(dd, 'x')}{_coeff_term(ee, 'y')}"
                    f"{canonical_exact(ff) if str(canonical_exact(ff)).startswith('-') else '+' + canonical_exact(ff)}=0$"
                )
            stem_items.append({"group_label": f"({idx})", "text": eq_body})
            ext = center_radius_from_general(d=dd, e=ee, f=ff, scale=sc)
            extracted_list.append(ext)
            part_answers[f"({idx})圓心"] = ext["canonical_parts"]["圓心"]
            part_answers[f"({idx})半徑"] = ext["canonical_parts"]["半徑"]
        stem_structure = build_stem_structure("試求下列各圓的圓心與半徑：", stem_items)
        question = stem_structure_to_question_text(stem_structure)
        parts = part_answers
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        result = {"items": items, "extracted": extracted_list}
        explanation = ["配方或公式：圓心 $(-D/2,-E/2)$，半徑平方 $(D^2+E^2)/4-F$。"]

    elif op == PARAMETER_RANGE_OP:
        if "pattern" not in payload:
            payload["pattern"] = rng.choice(["E_param", "D_param", "F_param"])
        pattern = payload["pattern"]
        param = str(payload.get("param") or "k")
        if pattern == "E_param":
            # x^2+y^2+4x+2ky+5=0 → r2=4+k^2-5=k^2-1 > 0
            d_expr, e_expr, f_expr = 4, f"2*{param}", 5
        elif pattern == "D_param":
            d_expr, e_expr, f_expr = param, -4, 5
        else:
            d_expr, e_expr, f_expr = 2, -6, param
        result = solve_circle_parameter_range(
            d_expr=d_expr, e_expr=e_expr, f_expr=f_expr, param=param
        )
        question = (
            f"已知方程式 $x^{{2}}+y^{{2}}"
            f"{_coeff_term(d_expr if not isinstance(d_expr, str) else 0, 'x')}"
            # build latex carefully
        )
        # Rebuild stem from pattern
        if pattern == "E_param":
            question = (
                f"已知方程式 $x^{{2}}+y^{{2}}+4x+2{param}y+5=0$ 的圖形為一圓，"
                f"試求 ${param}$ 的範圍。"
            )
        elif pattern == "D_param":
            question = (
                f"已知方程式 $x^{{2}}+y^{{2}}+{param}x-4y+5=0$ 的圖形為一圓，"
                f"試求 ${param}$ 的範圍。"
            )
        else:
            question = (
                f"已知方程式 $x^{{2}}+y^{{2}}+2x-6y+{param}=0$ 的圖形為一圓，"
                f"試求 ${param}$ 的範圍。"
            )
        answer_value = result["canonical"]
        as_mcq = bool(payload.get("as_mcq"))
        if as_mcq:
            correct = result["canonical"].replace(r"\le ", "≤").replace(r"\ge ", "≥")
            # Prefer inequality strings without latex
            correct_plain = result["canonical"]
            distractors = [
                correct_plain.replace("<", ">").replace(">", "<") if "<" in correct_plain or ">" in correct_plain else f"{param}>0",
                f"{param}<0",
                f"{param}>4",
            ]
            # Normalize distractors that may collide
            pack = _mcq_pack(correct_plain, distractors, rng)
            choices, correct_label = pack["choices"], pack["correct_label"]
            semantic_answer = pack["semantic_answer"]
            answer_type = "single_choice"
            presentation = "single_choice"
            answer_value = correct_label
        explanation = [rf"由 $r^2=\dfrac{{D^2+E^2}}{{4}}-F>0$ 解不等式。"]

    elif op == THROUGH_THREE_POINTS_OP:
        if "a" not in payload:
            # Sample a circle then three distinct axis-aligned / compass points on it.
            circ = make_circle(
                h=_sample_int(rng, -3, 3),
                k=_sample_int(rng, -3, 3),
                r=_sample_radius(rng),
            )
            offsets = [(circ["r"], 0), (0, circ["r"]), (-circ["r"], 0), (0, -circ["r"])]
            rng.shuffle(offsets)
            pts = [[circ["h"] + ox, circ["k"] + oy] for ox, oy in offsets[:3]]
            payload["a"], payload["b"], payload["c"] = pts[0], pts[1], pts[2]
        result = circle_through_three_points(a=payload["a"], b=payload["b"], c=payload["c"])
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        cx, cy = _as_pair(payload["c"])
        question = (
            f"設平面上三點 $A{latex_pair(ax, ay)}$、$B{latex_pair(bx, by)}$、"
            f"$C{latex_pair(cx, cy)}$，試求通過這三點的圓方程式。"
        )
        answer_value = result["general_form"]
        as_mcq = bool(payload.get("as_mcq"))
        if as_mcq:
            distractors = [
                format_general_equation(result["D"] + 1, result["E"], result["F"]),
                format_general_equation(result["D"], result["E"] + 2, result["F"]),
                result["standard_form"],
            ]
            pack = _mcq_pack(result["general_form"], distractors, rng)
            choices, correct_label = pack["choices"], pack["correct_label"]
            semantic_answer = pack["semantic_answer"]
            answer_type = "single_choice"
            presentation = "single_choice"
            answer_value = correct_label
        explanation = ["代入一般式聯立解 $D,E,F$。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "points": [
                {"id": "A", "x": float(ax), "y": float(ay)},
                {"id": "B", "x": float(bx), "y": float(by)},
                {"id": "C", "x": float(cx), "y": float(cy)},
            ],
            "requirement": "three_points_on_circle",
            "implemented": False,
        }

    elif op == CENTER_ON_AXIS_AREA_OP:
        # x^2+y^2-6x+2ay-7=0 center on x-axis ⇒ a=0, then area
        if "d" not in payload:
            payload.update({"d": -6, "e_coeff": 2, "f": -7, "axis": "x"})
        param = "a"
        if payload["axis"] == "x":
            # E = e_coeff * a → k = -E/2 = 0 ⇒ a = 0
            a_val = 0
            d, e, f = payload["d"], 0, payload["f"]
        else:
            a_val = 0
            d, e, f = 0, payload.get("e", 4), payload["f"]
        ext = center_radius_from_general(d=d, e=e, f=f)
        area = sp.simplify(sp.pi * ext["r2"])
        result = {**ext, "area": area, "param_value": a_val}
        question = (
            f"若圓 $x^{{2}}+y^{{2}}{ _coeff_term(payload['d'], 'x') }"
            f"+2{param}y{canonical_exact(payload['f']) if str(canonical_exact(payload['f'])).startswith('-') else '+' + canonical_exact(payload['f'])}=0$ "
            f"的圓心在 ${payload['axis']}$ 軸上，則此圓的面積為何？"
        )
        # Fix question formatting for f term
        fplain = canonical_exact(payload["f"])
        fterm = fplain if fplain.startswith("-") else f"+{fplain}"
        question = (
            f"若圓 $x^{{2}}+y^{{2}}{_coeff_term(payload['d'], 'x')}+2ay{fterm}=0$ "
            f"的圓心在 $x$ 軸上，則此圓的面積為何？"
        )
        correct = f"{canonical_exact(ext['r2'])}\\pi"
        distractors = [
            f"{canonical_exact(ext['r2'] + 5)}\\pi",
            f"{canonical_exact(ext['r'] ** 2 if False else 16)}\\pi",
            f"{canonical_exact(4)}\\pi",
        ]
        pack = _mcq_pack(correct, [d for d in distractors if d != correct], rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["圓心在 x 軸 ⇒ k=0 ⇒ 參數確定，再求面積 πr²。"]

    elif op == CLASSIFY_GENERAL_GRAPH_OP:
        items = payload.get("items")
        if not items:
            # One valid circle, one empty set, one point-circle — randomized coefficients.
            c_ok = make_circle(
                h=_sample_int(rng, -3, 3),
                k=_sample_int(rng, -3, 3),
                r=_sample_radius(rng),
            )
            scale = rng.choice([1, 2])
            items = [
                {
                    "d": int(c_ok["D"] * scale),
                    "e": int(c_ok["E"] * scale),
                    "f": int(c_ok["F"] * scale),
                    "scale": scale,
                },
                {
                    "d": _sample_int(rng, -5, 5),
                    "e": _sample_int(rng, -5, 5),
                    "f": int(rng.randint(8, 20)),
                    "scale": 1,
                },
                {
                    "d": _sample_int(rng, -6, 6, nonzero=True) * 2,
                    "e": _sample_int(rng, -6, 6, nonzero=True) * 2,
                    "f": 0,
                    "scale": 1,
                },
            ]
            # Force third item to be a point-circle: F = (D^2+E^2)/4
            d3, e3 = items[2]["d"], items[2]["e"]
            items[2]["f"] = int((d3 * d3 + e3 * e3) // 4)
            rng.shuffle(items)
        labels = []
        part_answers = {}
        stem_items: list[dict[str, str]] = []
        part_label_map: dict[str, str] = {}
        for idx, it in enumerate(items, 1):
            ext = circle_validity_from_general(
                d=it["d"], e=it["e"], f=it["f"], scale=it.get("scale", 1)
            )
            sc = sp.Integer(it.get("scale", 1))
            dd, ee, ff = it["d"], it["e"], it["f"]
            if sc == 1:
                eq = latex_general_equation(dd, ee, ff)
            else:
                fplain = canonical_exact(ff)
                fterm = fplain if fplain.startswith("-") else f"+{fplain}"
                eq = (
                    f"{canonical_exact(sc)}x^{{2}}+{canonical_exact(sc)}y^{{2}}"
                    f"{_coeff_term(dd, 'x')}{_coeff_term(ee, 'y')}{fterm}=0"
                )
            stem_items.append({"group_label": f"({idx})", "text": f"${eq}$"})
            labels.append(f"({idx}) ${eq}$")
            part_key = f"({idx})"
            part_answers[part_key] = ext["label"]
            part_label_map[part_key] = "圖形"
        stem_structure = build_stem_structure("試判斷下列各方程式的圖形：", stem_items)
        question = stem_structure_to_question_text(stem_structure)
        parts = part_answers
        part_labels_override = part_label_map
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        result = {"items": items}
        explanation = ["依 $r^2$ 正、零、負判斷為圓、一點或無圖形。"]

    elif op == AREA_FROM_GENERAL_OP:
        if "d" not in payload:
            circ = make_circle(
                h=_sample_int(rng, -4, 4),
                k=_sample_int(rng, -4, 4),
                r=_sample_radius(rng),
            )
            scale = rng.choice([1, 2])
            payload.update(
                {
                    "d": int(circ["D"] * scale),
                    "e": int(circ["E"] * scale),
                    "f": int(circ["F"] * scale),
                    "scale": scale,
                }
            )
        ext = center_radius_from_general(
            d=payload["d"], e=payload["e"], f=payload["f"], scale=payload.get("scale", 1)
        )
        if ext["validity"] != "circle":
            circ = make_circle(h=1, k=-1, r=2)
            payload.update({"d": int(circ["D"] * 2), "e": int(circ["E"] * 2), "f": int(circ["F"] * 2), "scale": 2})
            ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"], scale=2)
        area = sp.simplify(sp.pi * ext["r2"])
        result = {**ext, "area": area}
        sc = payload.get("scale", 1)
        fplain = canonical_exact(payload["f"])
        fterm = fplain if fplain.startswith("-") else f"+{fplain}"
        if sp.Integer(sc) == 1:
            eq = latex_general_equation(payload["d"], payload["e"], payload["f"])
        else:
            eq = (
                f"{canonical_exact(sc)}x^{{2}}+{canonical_exact(sc)}y^{{2}}"
                f"{_coeff_term(payload['d'], 'x')}{_coeff_term(payload['e'], 'y')}{fterm}=0"
            )
        question = f"假設圓 $C$ 的方程式為 ${eq}$，則圓 $C$ 的面積為"
        answer_value = f"{canonical_exact(ext['r2'])}\\pi"
        explanation = ["先化為一般式求 $r^2$，面積為 $\\pi r^2$。"]

    elif op == PRODUCT_FORM_IDENTIFY_OP:
        # (x+2)(x-2)+(y-4)(y+4)=0 → x^2-4+y^2-16=0 → x^2+y^2=20
        if "h_shift" not in payload:
            payload.update({"ax": 2, "ay": 4})
        ax, ay = int(payload["ax"]), int(payload["ay"])
        # (x+a)(x-a)+(y-b)(y+b)=0 → x^2-a^2+y^2-b^2=0 → center origin r2=a^2+b^2
        r2 = ax * ax + ay * ay
        result = make_circle(h=0, k=0, r2=r2)
        question = (
            f"已知圓方程式 $\\left(x+{ax}\\right)\\left(x-{ax}\\right)"
            f"+\\left(y-{ay}\\right)\\left(y+{ay}\\right)=0$，則下列何者正確？"
        )
        correct = result["standard_form"]
        distractors = [
            format_standard_equation(ax, ay, r2),
            format_general_equation(0, 0, -r2 + 1),
            format_standard_equation(0, 0, ax * ax),
        ]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["展開後得標準／一般式再判斷。"]

    elif op == EVAL_HKR_EXPRESSION_OP:
        if "d" not in payload:
            payload.update({"d": -10, "e": 2, "f": 10})
        ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"])
        h, k, r = ext["h"], ext["k"], ext["r"]
        expr_val = sp.simplify(h - k - r)
        result = {**ext, "expression_value": expr_val}
        question = (
            f"假設圓 $C$ 的方程式為 ${latex_general_equation(payload['d'], payload['e'], payload['f'])}$，"
            f"其圓心為 $\\left(h,\\ k\\right)$、半徑為 $r$，則 $h-k-r=$"
        )
        correct = canonical_exact(expr_val)
        distractors = [
            canonical_exact(expr_val + 2),
            canonical_exact(expr_val - 2),
            canonical_exact(expr_val + 4),
        ]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label = pack["choices"], pack["correct_label"]
        semantic_answer = pack["semantic_answer"]
        answer_type = "single_choice"
        presentation = "single_choice"
        answer_value = correct_label
        explanation = ["先求圓心與半徑，再代入 $h-k-r$。"]

    else:
        raise ValueError(f"unhandled_circle_plane_operation:{op}")

    if choices is not None:
        from core.gencode.choice_contract_validator import choice_semantic_key as _csk

        # Keep structured answer for domain-matrix contract; label lives alongside.
        answer_value_for_block = semantic_answer
        distractor_values = [
            str(c.get("value") or c.get("text") or "").strip()
            for c in choices
            if isinstance(c, dict)
            and _csk(c.get("value") or c.get("text")) != _csk(semantic_answer)
        ]
    else:
        answer_value_for_block = answer_value
        distractor_values = list(distractors)

    answer_block: dict[str, Any] = {
        "value": answer_value_for_block,
        "canonical_form": answer_value_for_block if not isinstance(answer_value_for_block, dict) else "",
        "general_form": answer_value_for_block if not isinstance(answer_value_for_block, dict) else "",
        "coefficients": [],
        "parts": parts if parts else {},
        "part_labels": part_labels_override if part_labels_override is not None else (
            list(parts.keys()) if parts else []
        ),
    }
    if isinstance(answer_value_for_block, dict):
        answer_block["canonical_form"] = answer_value_for_block
        answer_block["general_form"] = answer_value_for_block

    matrix: dict[str, Any] = {
        "domain_key": "circle.plane",
        "domain_operation": op,
        "question": question,
        "question_text": question,
        "answer": answer_block,
        "explanation_steps": explanation,
        "distractors": distractor_values,
        "givens": _json_value(payload),
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "standard",
            "answer_type": answer_type,
            "presentation_mode": presentation,
            "seed": 0 if seed is None else int(seed),
            "result": _json_value(result) if isinstance(result, dict) else {},
        },
        "visual_spec": visual_spec or {"kind": "none"},
    }
    if stem_structure is not None:
        matrix["stem_structure"] = stem_structure
    if choices is not None:
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = semantic_answer
        matrix["canonical_answer"] = semantic_answer
    return matrix


def validate_circle_plane_matrix(matrix: dict[str, Any]) -> bool:
    if not isinstance(matrix, dict):
        return False
    op = str(matrix.get("domain_operation") or "").strip()
    if op not in OPS:
        return False
    if not str(matrix.get("question") or matrix.get("question_text") or "").strip():
        return False
    if "distractors" not in matrix:
        return False
    answer = matrix.get("answer")
    facts = matrix.get("validation_facts")
    if not isinstance(facts, dict):
        return False
    if facts.get("answer_type") == "single_choice":
        choices = matrix.get("choices")
        if not isinstance(choices, list) or len(choices) < 2:
            return False
        if not matrix.get("correct_label"):
            return False
        if not isinstance(answer, dict):
            return False
        return True
    if not isinstance(answer, dict) or answer.get("value") in (None, ""):
        return False
    if facts.get("answer_type") == "multi_part":
        parts = answer.get("parts")
        if not isinstance(parts, dict) or not parts:
            return False
    return True


# ── 4-2 gap coverage wiring ───────────────────────────────────────────────────
# Imported last: the gap module defines GAP_OPS before it imports this module, so
# either import order resolves without a partially-initialised attribute error.
from core.domain.circle_plane_gap_coverage import GAP_OPS  # noqa: E402

OPS = frozenset(set(_CORE_OPS) | set(GAP_OPS))
