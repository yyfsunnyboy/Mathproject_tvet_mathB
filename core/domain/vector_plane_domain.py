# -*- coding: utf-8 -*-
"""Plane vector domain for vocational B2 Chapter 3 (exact arithmetic).

Operations cover coordinate representation, arithmetic, scalar multiples,
parallelism, unit vectors, and dot-product / perpendicular relations.
Diagram families reuse coordinate_plane visual_spec (+ arrows); geometric path /
section / composite topologies live in vector_plane_gap_coverage.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

import sympy as sp

# ── operation keys ────────────────────────────────────────────────────────────

COMPONENTS_MAGNITUDE_OP = "compute_vector_components_and_magnitude"
EQUAL_VECTORS_OP = "solve_equal_vector_coordinates"
DIRECTED_SEGMENT_OP = "compute_directed_segment_and_magnitude"
PARALLELOGRAM_VERTEX_OP = "solve_parallelogram_fourth_vertex"
TRIANGLE_PERIMETER_OP = "compute_triangle_perimeter_from_two_vectors"
VECTOR_ADD_SUB_OP = "compute_vector_sum_difference"
POINTS_LINEAR_COMBO_OP = "compute_point_vectors_linear_combination"
SCALAR_MULTIPLE_OP = "compute_scalar_multiple_coordinates"
PARALLEL_PARAM_OP = "solve_parallel_vector_parameter"
UNIT_VECTOR_OP = "compute_unit_vector"
DOT_COORD_OP = "compute_dot_product_coordinates"
DOT_MAG_ANGLE_OP = "compute_dot_product_from_magnitudes_angle"
PERPENDICULAR_PARAM_OP = "solve_perpendicular_vector_parameter"
COSINE_FROM_DOT_OP = "compute_cosine_of_angle_from_dot"
LINEAR_COMBO_OP = "compute_vector_linear_combination"
SCALED_DIRECTION_OP = "compute_scaled_direction_vector"
TRIANGLE_CHAIN_OP = "compute_triangle_chain_and_perimeter"

_CORE_OPS = frozenset(
    {
        COMPONENTS_MAGNITUDE_OP,
        EQUAL_VECTORS_OP,
        DIRECTED_SEGMENT_OP,
        PARALLELOGRAM_VERTEX_OP,
        TRIANGLE_PERIMETER_OP,
        VECTOR_ADD_SUB_OP,
        POINTS_LINEAR_COMBO_OP,
        SCALAR_MULTIPLE_OP,
        PARALLEL_PARAM_OP,
        UNIT_VECTOR_OP,
        DOT_COORD_OP,
        DOT_MAG_ANGLE_OP,
        PERPENDICULAR_PARAM_OP,
        COSINE_FROM_DOT_OP,
        LINEAR_COMBO_OP,
        SCALED_DIRECTION_OP,
        TRIANGLE_CHAIN_OP,
    }
)

# Declared here to avoid circular import with vector_plane_gap_coverage.
_GAP_OPS = frozenset(
    {
        "simplify_vector_path_expression",
        "express_named_vectors_in_given_basis",
        "solve_scalar_multiple_relation_fill",
        "express_section_point_vector",
        "solve_section_coefficient_pair",
        "identify_equal_vector_mcq",
        "identify_resultant_path_mcq",
        "construct_linear_combination_choice",
        "express_linear_combination_from_givens",
        "compute_directed_segment_mixed_multipart",
        "compute_chain_closure_vector_mcq",
        "solve_point_from_vector_combination",
        "solve_collinear_ratio_mcq",
        "solve_unknown_vector_linear_equation",
        "solve_parallel_then_magnitude_mcq",
        "identify_unit_vector_mcq",
        "solve_navigation_heading_correction",
        "classify_angle_quality_from_dot_mcq",
        "compute_regular_polygon_edge_dot",
        "compute_dot_identity_multipart",
        "plot_navigation_points_coordinates",
        "compute_midpoint_dot_product",
        "solve_dot_product_parameter_mcq",
        "solve_perpendicular_composite_parameter",
        "classify_dot_sign_from_diagram_mcq",
        "expand_perpendicular_dot_product",
        "solve_angle_from_magnitude_identity",
    }
)

OPS = frozenset(set(_CORE_OPS) | set(_GAP_OPS))



def canonical_exact(value: Any) -> str:
    """Student-facing exact scalar/display string (does not alter symbolic math objects).

    Floats are nsimplified before printing so IEEE noise like ``4.00000000000000``
    never reaches stems/MCQ text. Checker comparisons should use labels/semantic
    values, not these display strings' float tails.
    """
    from core.gencode.resources.rational_display import (
        compact_float_noise_token,
        fraction_to_plain,
        sanitize_float_noise_in_text,
    )

    if isinstance(value, float):
        if abs(value) < 1e-15:
            return "0"
        # Prefer exact classroom rationals when the float is an exact simple number.
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


def _as_pair(value: Any, *, name: str = "vector") -> tuple[sp.Expr, sp.Expr]:
    if isinstance(value, dict):
        if "x" in value and "y" in value:
            return sp.simplify(sp.sympify(value["x"])), sp.simplify(sp.sympify(value["y"]))
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


def magnitude(x: Any, y: Any) -> sp.Expr:
    return sp.simplify(sp.sqrt(sp.simplify(sp.sympify(x) ** 2 + sp.sympify(y) ** 2)))


# ── pure math ops ─────────────────────────────────────────────────────────────

def compute_vector_components_and_magnitude(*, vector: Any) -> dict[str, Any]:
    x, y = _as_pair(vector, name="vector")
    mag = magnitude(x, y)
    return {
        "x": x,
        "y": y,
        "components": (x, y),
        "magnitude": mag,
        "canonical_components": format_pair(x, y),
        "canonical_magnitude": canonical_exact(mag),
        "canonical": {
            "x_component": canonical_exact(x),
            "y_component": canonical_exact(y),
            "magnitude": canonical_exact(mag),
        },
    }


def solve_equal_vector_coordinates(
    *,
    left: Any,
    right: Any,
) -> dict[str, Any]:
    """Solve left == right for free symbols; left/right are coordinate pairs of expressions."""
    lx, ly = _as_pair(left, name="left")
    rx, ry = _as_pair(right, name="right")
    eqs = [sp.Eq(lx, rx), sp.Eq(ly, ry)]
    symbols = sorted(eqs[0].free_symbols.union(eqs[1].free_symbols), key=str)
    if not symbols:
        if sp.simplify(lx - rx) == 0 and sp.simplify(ly - ry) == 0:
            return {"solution": {}, "canonical": {}}
        raise ValueError("equal_vectors_inconsistent")
    sols = sp.solve(eqs, symbols, dict=True)
    if not sols:
        raise ValueError("equal_vectors_no_solution")
    sol = sols[0]
    canonical = {str(sym): canonical_exact(val) for sym, val in sol.items()}
    return {"solution": sol, "canonical": canonical, "symbols": [str(s) for s in symbols]}


def compute_directed_segment_and_magnitude(*, start: Any, end: Any) -> dict[str, Any]:
    x1, y1 = _as_pair(start, name="start")
    x2, y2 = _as_pair(end, name="end")
    vx, vy = sp.simplify(x2 - x1), sp.simplify(y2 - y1)
    mag = magnitude(vx, vy)
    return {
        "vector": (vx, vy),
        "magnitude": mag,
        "canonical_vector": format_pair(vx, vy),
        "canonical_magnitude": canonical_exact(mag),
        "canonical": {
            "vector": format_pair(vx, vy),
            "magnitude": canonical_exact(mag),
        },
    }


def solve_parallelogram_fourth_vertex(
    *,
    a: Any,
    b: Any,
    c: Any,
    missing: str = "D",
    convention: str = "AB_equals_DC",
) -> dict[str, Any]:
    """Find missing vertex of parallelogram ABCD.

    AB_equals_DC: D = A + C - B  (vector AB = vector DC ⇒ D-C = B-A? wait)
    Standard: ABCD parallelogram with AB // DC and AD // BC:
      D = A + C - B  when using diagonal AC midpoint = BD midpoint
      Midpoint of AC = Midpoint of BD ⇒ D = A+C-B
    """
    ax, ay = _as_pair(a, name="A")
    bx, by = _as_pair(b, name="B")
    cx, cy = _as_pair(c, name="C")
    convention = str(convention or "AB_equals_DC").strip()
    # Default textbook: A,B,C given consecutive; D = A+C-B (parallelogram law / diagonal midpoint)
    dx, dy = sp.simplify(ax + cx - bx), sp.simplify(ay + cy - by)
    if convention == "AD_equals_BC":
        # Same midpoint identity for labeled ABCD.
        pass
    return {
        "missing": missing,
        "point": (dx, dy),
        "canonical": format_pair(dx, dy),
        "canonical_parts": {"x": canonical_exact(dx), "y": canonical_exact(dy)},
    }


def compute_triangle_perimeter_from_two_vectors(*, ab: Any, ac: Any) -> dict[str, Any]:
    abx, aby = _as_pair(ab, name="AB")
    acx, acy = _as_pair(ac, name="AC")
    bcx, bcy = sp.simplify(acx - abx), sp.simplify(acy - aby)
    len_ab = magnitude(abx, aby)
    len_ac = magnitude(acx, acy)
    len_bc = magnitude(bcx, bcy)
    peri = sp.simplify(len_ab + len_ac + len_bc)
    return {
        "lengths": {"AB": len_ab, "AC": len_ac, "BC": len_bc},
        "perimeter": peri,
        "canonical": canonical_exact(peri),
    }


def compute_vector_sum_difference(*, a: Any, b: Any, mode: str = "sum") -> dict[str, Any]:
    ax, ay = _as_pair(a, name="a")
    bx, by = _as_pair(b, name="b")
    mode = str(mode or "sum").strip().lower()
    if mode in {"sum", "add", "+"}:
        rx, ry = sp.simplify(ax + bx), sp.simplify(ay + by)
        label = "a+b"
    elif mode in {"difference", "sub", "-"}:
        rx, ry = sp.simplify(ax - bx), sp.simplify(ay - by)
        label = "a-b"
    else:
        raise ValueError(f"unsupported_vector_mode:{mode}")
    return {
        "mode": mode,
        "result": (rx, ry),
        "label": label,
        "canonical": format_pair(rx, ry),
        "magnitude": magnitude(rx, ry),
        "canonical_magnitude": canonical_exact(magnitude(rx, ry)),
    }


def compute_point_vectors_linear_combination(
    *,
    points: dict[str, Any],
    expression: str = "AB+CD",
) -> dict[str, Any]:
    """Evaluate a simple sum/difference of directed segments among named points."""
    pts = {str(k): _as_pair(v, name=str(k)) for k, v in dict(points or {}).items()}
    expr = str(expression or "").replace(" ", "")
    # Parse tokens like AB+CD, AB-CD, AB+BC
    import re

    parts = re.findall(r"[+-]?[A-Za-z]{2}", expr if expr[:1] in "+-" else f"+{expr}")
    if not parts:
        raise ValueError("invalid_point_vector_expression")
    rx = sp.Integer(0)
    ry = sp.Integer(0)
    for token in parts:
        sign = -1 if token.startswith("-") else 1
        name = token.lstrip("+-")
        if len(name) != 2:
            raise ValueError(f"invalid_segment:{name}")
        start, end = name[0], name[1]
        if start not in pts or end not in pts:
            raise ValueError(f"missing_point_for_segment:{name}")
        sx, sy = pts[start]
        ex, ey = pts[end]
        rx = sp.simplify(rx + sign * (ex - sx))
        ry = sp.simplify(ry + sign * (ey - sy))
    return {
        "expression": expression,
        "result": (rx, ry),
        "canonical": format_pair(rx, ry),
    }


def compute_scalar_multiple_coordinates(*, vector: Any, scalar: Any) -> dict[str, Any]:
    x, y = _as_pair(vector, name="vector")
    k = sp.simplify(sp.sympify(scalar))
    rx, ry = sp.simplify(k * x), sp.simplify(k * y)
    return {
        "scalar": k,
        "result": (rx, ry),
        "canonical": format_pair(rx, ry),
        "canonical_scalar": canonical_exact(k),
    }


def solve_parallel_vector_parameter(*, a: Any, b: Any, parameter: str = "k") -> dict[str, Any]:
    ax, ay = _as_pair(a, name="a")
    bx, by = _as_pair(b, name="b")
    # a ∥ b ⇔ ax*by - ay*bx = 0
    eq = sp.Eq(sp.simplify(ax * by - ay * bx), 0)
    sym = sp.Symbol(str(parameter or "k"))
    sols = sp.solve(eq, sym)
    if not sols and eq == True:  # noqa: E712
        return {"parameter": str(sym), "solutions": [], "canonical": [], "identity": True}
    if not sols:
        raise ValueError("parallel_no_solution")
    canonical = [canonical_exact(s) for s in sols]
    return {
        "parameter": str(sym),
        "solutions": sols,
        "canonical": canonical if len(canonical) > 1 else canonical[0],
        "equation": canonical_exact(ax * by - ay * bx),
    }


def compute_unit_vector(*, vector: Any, direction: str = "same") -> dict[str, Any]:
    x, y = _as_pair(vector, name="vector")
    mag = magnitude(x, y)
    if mag == 0:
        raise ValueError("zero_vector_has_no_unit")
    ux, uy = sp.simplify(x / mag), sp.simplify(y / mag)
    if str(direction or "same").strip() in {"opposite", "reverse", "-"}:
        ux, uy = sp.simplify(-ux), sp.simplify(-uy)
    return {
        "unit": (ux, uy),
        "magnitude": mag,
        "canonical": format_pair(ux, uy),
        "canonical_magnitude": canonical_exact(mag),
    }


def compute_dot_product_coordinates(*, a: Any, b: Any) -> dict[str, Any]:
    ax, ay = _as_pair(a, name="a")
    bx, by = _as_pair(b, name="b")
    dot = sp.simplify(ax * bx + ay * by)
    return {"dot": dot, "canonical": canonical_exact(dot)}


def compute_dot_product_from_magnitudes_angle(
    *,
    mag_a: Any,
    mag_b: Any,
    angle_degrees: Any,
) -> dict[str, Any]:
    ma = sp.simplify(sp.sympify(mag_a))
    mb = sp.simplify(sp.sympify(mag_b))
    ang = sp.simplify(sp.sympify(angle_degrees))
    dot = sp.simplify(ma * mb * sp.cos(sp.rad(ang)))
    return {
        "dot": dot,
        "canonical": canonical_exact(dot),
        "angle_degrees": ang,
    }


def solve_perpendicular_vector_parameter(*, a: Any, b: Any, parameter: str = "k") -> dict[str, Any]:
    ax, ay = _as_pair(a, name="a")
    bx, by = _as_pair(b, name="b")
    eq = sp.Eq(sp.simplify(ax * bx + ay * by), 0)
    sym = sp.Symbol(str(parameter or "k"))
    sols = sp.solve(eq, sym)
    if not sols:
        raise ValueError("perpendicular_no_solution")
    canonical = [canonical_exact(s) for s in sols]
    return {
        "parameter": str(sym),
        "solutions": sols,
        "canonical": canonical if len(canonical) > 1 else canonical[0],
    }


def compute_cosine_of_angle_from_dot(*, a: Any, b: Any) -> dict[str, Any]:
    ax, ay = _as_pair(a, name="a")
    bx, by = _as_pair(b, name="b")
    dot = sp.simplify(ax * bx + ay * by)
    ma = magnitude(ax, ay)
    mb = magnitude(bx, by)
    if ma == 0 or mb == 0:
        raise ValueError("zero_vector_angle_undefined")
    cosv = sp.simplify(dot / (ma * mb))
    return {
        "cosine": cosv,
        "dot": dot,
        "canonical": canonical_exact(cosv),
        "canonical_dot": canonical_exact(dot),
    }


def compute_vector_linear_combination(*, terms: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate sum coeff_i * vector_i."""
    rx = sp.Integer(0)
    ry = sp.Integer(0)
    for term in list(terms or []):
        coeff = sp.simplify(sp.sympify(term.get("coeff", 1)))
        vx, vy = _as_pair(term.get("vector"), name="term_vector")
        rx = sp.simplify(rx + coeff * vx)
        ry = sp.simplify(ry + coeff * vy)
    return {"result": (rx, ry), "canonical": format_pair(rx, ry)}


def compute_scaled_direction_vector(
    *,
    vector: Any,
    length: Any,
    direction: str = "same",
) -> dict[str, Any]:
    unit = compute_unit_vector(vector=vector, direction=direction)
    L = sp.simplify(sp.sympify(length))
    ux, uy = unit["unit"]
    rx, ry = sp.simplify(L * ux), sp.simplify(L * uy)
    return {
        "unit": unit["unit"],
        "result": (rx, ry),
        "canonical_unit": unit["canonical"],
        "canonical": format_pair(rx, ry),
        "length": L,
    }


def _scaled_direction_distractors(
    *,
    correct: tuple[Any, Any],
    vector: Any,
    length: Any,
    direction: str,
    rng: random.Random,
) -> list[str]:
    """Pedagogical distractors for same/opposite scaled-direction MCQ (display-safe)."""
    cx, cy = correct
    vx, vy = _as_pair(vector, name="vector")
    L = sp.simplify(sp.sympify(length))
    correct_text = format_pair(cx, cy)
    wrong_dir = "opposite" if str(direction) == "same" else "same"
    flipped = compute_scaled_direction_vector(vector=(vx, vy), length=L, direction=wrong_dir)
    other_len = sp.Integer(int(L) + 1) if getattr(L, "is_integer", False) else sp.simplify(L + 1)
    if other_len == 0:
        other_len = sp.Integer(2)
    wrong_mag = compute_scaled_direction_vector(
        vector=(vx, vy), length=other_len, direction=direction
    )
    candidates = [
        format_pair(*flipped["result"]),
        format_pair(vx, vy),
        format_pair(*wrong_mag["result"]),
        format_pair(cy, cx),
        format_pair(-cx, cy),
        format_pair(cx, -cy),
        format_pair(0, -L if cy != 0 or cx == 0 else L),
        format_pair(-L if cx != 0 or cy == 0 else L, 0),
    ]
    unique: list[str] = []
    seen = {correct_text}
    for text in candidates:
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
        if len(unique) >= 3:
            break
    filler_idx = 0
    while len(unique) < 3:
        filler_idx += 1
        cand = format_pair(cx + filler_idx, cy - filler_idx)
        if cand in seen:
            continue
        seen.add(cand)
        unique.append(cand)
    rng.shuffle(unique)
    return unique[:3]


def compute_triangle_chain_and_perimeter(*, ab: Any, bc: Any) -> dict[str, Any]:
    abx, aby = _as_pair(ab, name="AB")
    bcx, bcy = _as_pair(bc, name="BC")
    acx, acy = sp.simplify(abx + bcx), sp.simplify(aby + bcy)
    len_ab = magnitude(abx, aby)
    len_bc = magnitude(bcx, bcy)
    len_ac = magnitude(acx, acy)
    peri = sp.simplify(len_ab + len_bc + len_ac)
    return {
        "ac": (acx, acy),
        "canonical_ac": format_pair(acx, acy),
        "perimeter": peri,
        "canonical_perimeter": canonical_exact(peri),
        "canonical": {
            "AC": format_pair(acx, acy),
            "perimeter": canonical_exact(peri),
        },
    }


# ── sampling ──────────────────────────────────────────────────────────────────

def _rand_int(rng: random.Random, lo: int = -6, hi: int = 6, *, nonzero: bool = False) -> int:
    choices = [i for i in range(lo, hi + 1) if (not nonzero or i != 0)]
    return int(rng.choice(choices))


def _sample_pair(rng: random.Random, *, nonzero: bool = True) -> tuple[int, int]:
    for _ in range(40):
        x, y = _rand_int(rng), _rand_int(rng)
        if nonzero and x == 0 and y == 0:
            continue
        return x, y
    return 3, 4


def _choice_payload(canonical: str, distractors: list[str], rng: random.Random) -> dict[str, Any]:
    options = [canonical]
    for d in distractors:
        dd = str(d)
        if dd and dd not in options:
            options.append(dd)
    while len(options) < 4:
        options.append(canonical_exact(sp.Integer(len(options) + 2)))
    options = options[:4]
    rng.shuffle(options)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": labels[i], "text": f"${options[i]}$", "value": options[i]} for i in range(4)]
    correct = next(c["label"] for c in choices if c["value"] == canonical)
    return {"choices": choices, "correct_label": correct, "semantic_answer": canonical}


# ── matrix builder ────────────────────────────────────────────────────────────

def build_vector_plane_matrix(
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
        from core.domain.vector_plane_gap_coverage import build_gap_matrix

        return build_gap_matrix(
            operation=op,
            seed=seed,
            constraints=constraints,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            **data,
        )
    if op not in OPS:
        raise ValueError(f"unsupported_vector_plane_operation:{op}")
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

    distractors: list[str] = []
    choice_meta: dict[str, Any] = {}
    presentation = "short_answer"
    answer_type = "expression"
    parts: dict[str, Any] = {}
    result: dict[str, Any]

    if op == COMPONENTS_MAGNITUDE_OP:
        if "vector" not in payload:
            payload["vector"] = list(_sample_pair(rng))
        result = compute_vector_components_and_magnitude(vector=payload["vector"])
        vx, vy = result["x"], result["y"]
        question = (
            f"在坐標平面上，設 $\\vec{{a}}={latex_pair(vx, vy)}$，試求："
            f"(1) $\\vec{{a}}$ 的 $x$ 分量與 $y$ 分量；"
            f"(2) $\\left|\\vec{{a}}\\right|$。"
        )
        parts = {
            "x_component": result["canonical"]["x_component"],
            "y_component": result["canonical"]["y_component"],
            "magnitude": result["canonical"]["magnitude"],
        }
        answer_value = parts
        answer_type = "multi_part"
        explanation = [
            f"$x$ 分量為 ${parts['x_component']}$，$y$ 分量為 ${parts['y_component']}$。",
            rf"$\left|\vec{{a}}\right|=\sqrt{{({parts['x_component']})^2+({parts['y_component']})^2}}={parts['magnitude']}$。",
        ]

    elif op == EQUAL_VECTORS_OP:
        if "left" not in payload or "right" not in payload:
            # Classic textbook patterns.
            if rng.random() < 0.5:
                payload["left"] = ["x+2", -5]
                payload["right"] = [5, "y-1"]
            else:
                payload["left"] = ["x-y", "x+y"]
                payload["right"] = [4, 6]
        result = solve_equal_vector_coordinates(left=payload["left"], right=payload["right"])
        lx, ly = payload["left"][0], payload["left"][1]
        rx, ry = payload["right"][0], payload["right"][1]
        question = (
            f"設 $\\vec{{a}}=\\left( {lx},\\ {ly} \\right)$、"
            f"$\\vec{{b}}=\\left( {rx},\\ {ry} \\right)$，若 $\\vec{{a}}=\\vec{{b}}$，試求未知數之值。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["由對應分量相等列出方程組並求解。"]

    elif op == DIRECTED_SEGMENT_OP:
        if "start" not in payload or "end" not in payload:
            payload["start"] = list(_sample_pair(rng, nonzero=False))
            payload["end"] = list(_sample_pair(rng, nonzero=False))
            if payload["start"] == payload["end"]:
                payload["end"] = [payload["start"][0] + 3, payload["start"][1] - 4]
        result = compute_directed_segment_and_magnitude(start=payload["start"], end=payload["end"])
        sx, sy = _as_pair(payload["start"])
        ex, ey = _as_pair(payload["end"])
        question = (
            f"設 $A{latex_pair(sx, sy)}$、$B{latex_pair(ex, ey)}$ 為坐標平面上兩點，試求："
            f"(1) $\\overrightarrow{{AB}}$ 的坐標表示；"
            f"(2) $\\left|\\overrightarrow{{AB}}\\right|$。"
        )
        parts = {
            "vector": result["canonical"]["vector"],
            "magnitude": result["canonical"]["magnitude"],
        }
        answer_value = parts
        answer_type = "multi_part"
        explanation = [
            rf"$\overrightarrow{{AB}}={result['canonical']['vector']}$。",
            rf"$\left|\overrightarrow{{AB}}\right|={result['canonical']['magnitude']}$。",
        ]

    elif op == PARALLELOGRAM_VERTEX_OP:
        if not {"a", "b", "c"} <= set(payload):
            payload["a"] = list(_sample_pair(rng, nonzero=False))
            payload["b"] = list(_sample_pair(rng, nonzero=False))
            payload["c"] = list(_sample_pair(rng, nonzero=False))
        result = solve_parallelogram_fourth_vertex(
            a=payload["a"], b=payload["b"], c=payload["c"], missing=str(payload.get("missing") or "D")
        )
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        cx, cy = _as_pair(payload["c"])
        question = (
            f"已知平行四邊形 $ABCD$ 的三個頂點為 $A{latex_pair(ax, ay)}$、"
            f"$B{latex_pair(bx, by)}$、$C{latex_pair(cx, cy)}$，試求頂點 $D$ 的坐標。"
        )
        parts = {"D": result["canonical"]}
        answer_value = result["canonical"]
        answer_type = "expression"
        explanation = ["由對角線中點重合：$D=A+C-B$。"]

    elif op == TRIANGLE_PERIMETER_OP:
        if "ab" not in payload or "ac" not in payload:
            payload["ab"] = [3, 4]
            payload["ac"] = [0, 2]
        result = compute_triangle_perimeter_from_two_vectors(ab=payload["ab"], ac=payload["ac"])
        abx, aby = _as_pair(payload["ab"])
        acx, acy = _as_pair(payload["ac"])
        question = (
            f"在 $\\triangle ABC$ 中，向量 $\\overrightarrow{{AB}}={latex_pair(abx, aby)}$、"
            f"$\\overrightarrow{{AC}}={latex_pair(acx, acy)}$，則 $\\triangle ABC$ 之周長為何？"
        )
        answer_value = result["canonical"]
        distractors = [
            canonical_exact(result["perimeter"] + 1),
            canonical_exact(result["perimeter"] - 1),
            canonical_exact(magnitude(abx, aby) + magnitude(acx, acy)),
        ]
        choice_meta = _choice_payload(str(answer_value), distractors, rng)
        presentation = "single_choice"
        answer_type = "single_choice"
        parts = {"perimeter": answer_value}
        explanation = ["周長 $=|AB|+|AC|+|BC|$。"]

    elif op == VECTOR_ADD_SUB_OP:
        if "a" not in payload or "b" not in payload:
            payload["a"] = list(_sample_pair(rng))
            payload["b"] = list(_sample_pair(rng))
        mode = str(payload.get("mode") or "sum")
        result = compute_vector_sum_difference(a=payload["a"], b=payload["b"], mode=mode)
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        op_sym = "+" if mode in {"sum", "add", "+"} else "-"
        question = (
            f"設 $\\vec{{a}}={latex_pair(ax, ay)}$、$\\vec{{b}}={latex_pair(bx, by)}$，"
            f"試求 $\\vec{{a}}{op_sym}\\vec{{b}}$。"
        )
        if payload.get("with_magnitude"):
            parts = {
                "vector": result["canonical"],
                "magnitude": result["canonical_magnitude"],
            }
            answer_value = parts
            answer_type = "multi_part"
        else:
            parts = {"vector": result["canonical"]}
            answer_value = result["canonical"]
            answer_type = "expression"
            rx, ry = result["result"]
            wrong_mode = "difference" if mode in {"sum", "add", "+"} else "sum"
            flipped = compute_vector_sum_difference(a=payload["a"], b=payload["b"], mode=wrong_mode)
            distractors = [
                format_pair(-rx, -ry),
                format_pair(rx, -ry),
                format_pair(-rx, ry),
                flipped["canonical"],
                format_pair(ry, rx),
            ]
        explanation = ["分量分別相加（或相減）。"]

    elif op == POINTS_LINEAR_COMBO_OP:
        if "points" not in payload:
            payload["points"] = {
                "A": list(_sample_pair(rng, nonzero=False)),
                "B": list(_sample_pair(rng, nonzero=False)),
                "C": list(_sample_pair(rng, nonzero=False)),
                "D": list(_sample_pair(rng, nonzero=False)),
            }
            payload["expression"] = rng.choice(["AB+CD", "AB-CD", "AC+BD", "AD+BC"])
        result = compute_point_vectors_linear_combination(
            points=payload["points"], expression=str(payload.get("expression") or "AB+CD")
        )
        question = (
            "設平面上四點坐標如題，試求 "
            f"${str(payload.get('expression') or 'AB+CD')}$ 的坐標表示。"
        )
        if payload.get("question_text"):
            question = str(payload["question_text"])
        # Include concrete coordinates in stem when not overridden.
        if not payload.get("question_text"):
            pts = payload["points"]
            bits = "、".join(
                f"${lab}={latex_pair(*_as_pair(xy))}$" for lab, xy in pts.items()
            )
            question = (
                f"設 {bits}，試求 ${str(payload.get('expression') or 'AB+CD')}$ 的坐標表示。"
            )
        parts = {"vector": result["canonical"]}
        answer_value = result["canonical"]
        answer_type = "expression"
        explanation = ["將各有向線段寫成終點減起點後相加。"]

    elif op == SCALAR_MULTIPLE_OP:
        if "vector" not in payload:
            payload["vector"] = list(_sample_pair(rng))
        if "scalar" not in payload:
            payload["scalar"] = _rand_int(rng, -4, 4, nonzero=True)
        result = compute_scalar_multiple_coordinates(
            vector=payload["vector"], scalar=payload["scalar"]
        )
        vx, vy = _as_pair(payload["vector"])
        k = canonical_exact(payload["scalar"])
        question = (
            f"設 $\\vec{{a}}={latex_pair(vx, vy)}$，試求 ${k}\\vec{{a}}$。"
        )
        answer_value = result["canonical"]
        parts = {"vector": result["canonical"]}
        answer_type = "expression"
        explanation = [f"各分量乘以 ${k}$。"]

    elif op == PARALLEL_PARAM_OP:
        if "a" not in payload or "b" not in payload:
            # Construct b = t * a with one unknown component so a solution always exists.
            ax, ay = _sample_pair(rng)
            t = _rand_int(rng, -4, 4, nonzero=True)
            if rng.random() < 0.5:
                payload["a"] = [ax, ay]
                payload["b"] = ["k", t * ay]
                # Parallel: ax*(t*ay) - ay*k = 0 ⇒ k = t*ax (when ay!=0). If ay==0, k free /
                # force ay nonzero.
                if ay == 0:
                    ay = _rand_int(rng, -5, 5, nonzero=True)
                    payload["a"] = [ax, ay]
                    payload["b"] = ["k", t * ay]
            else:
                if ax == 0:
                    ax = _rand_int(rng, -5, 5, nonzero=True)
                payload["a"] = [ax, ay]
                payload["b"] = [t * ax, "k"]
        result = solve_parallel_vector_parameter(
            a=payload["a"], b=payload["b"], parameter=str(payload.get("parameter") or "k")
        )
        ax, ay = payload["a"][0], payload["a"][1]
        bx, by = payload["b"][0], payload["b"][1]
        question = (
            f"設 $\\vec{{a}}=\\left( {ax},\\ {ay} \\right)$、"
            f"$\\vec{{b}}=\\left( {bx},\\ {by} \\right)$，"
            f"若 $\\vec{{a}}$ 與 $\\vec{{b}}$ 平行，試求參數之值。"
        )
        answer_value = result["canonical"]
        parts = {"k": result["canonical"] if not isinstance(result["canonical"], list) else result["canonical"][0]}
        if isinstance(result["canonical"], list):
            answer_type = "multi_part"
            parts = {f"k{i+1}": v for i, v in enumerate(result["canonical"])}
            answer_value = parts
        else:
            answer_type = "expression"
        explanation = [r"平行條件：$a_x b_y - a_y b_x = 0$。"]

    elif op == UNIT_VECTOR_OP:
        if "vector" not in payload:
            # Prefer Pythagorean triples for clean answers.
            payload["vector"] = list(rng.choice([[3, 4], [5, 12], [6, 8], [8, 15], [7, 24], [9, 12]]))
            if rng.random() < 0.5:
                payload["vector"][0] *= -1
            if rng.random() < 0.5:
                payload["vector"][1] *= -1
        if "direction" not in payload:
            payload["direction"] = rng.choice(["same", "opposite"])
        direction = str(payload.get("direction") or "same")
        result = compute_unit_vector(vector=payload["vector"], direction=direction)
        vx, vy = _as_pair(payload["vector"])
        question = (
            f"設 $\\vec{{a}}={latex_pair(vx, vy)}$，試求與 $\\vec{{a}}$ "
            f"{'同方向' if direction == 'same' else '反方向'}的單位向量。"
        )
        answer_value = result["canonical"]
        parts = {"unit": result["canonical"]}
        answer_type = "expression"
        explanation = [r"單位向量 $=\vec{a}/|\vec{a}|$。"]

    elif op == DOT_COORD_OP:
        if "a" not in payload or "b" not in payload:
            payload["a"] = list(_sample_pair(rng))
            payload["b"] = list(_sample_pair(rng))
        result = compute_dot_product_coordinates(a=payload["a"], b=payload["b"])
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        question = (
            f"若 $\\vec{{a}}={latex_pair(ax, ay)}$、$\\vec{{b}}={latex_pair(bx, by)}$，"
            f"試求 $\\vec{{a}}\\cdot\\vec{{b}}$。"
        )
        answer_value = result["canonical"]
        parts = {"dot": result["canonical"]}
        answer_type = "expression"
        explanation = [r"$\vec{a}\cdot\vec{b}=a_x b_x+a_y b_y$。"]

    elif op == DOT_MAG_ANGLE_OP:
        if not {"mag_a", "mag_b", "angle_degrees"} <= set(payload):
            payload["mag_a"] = rng.choice([2, 3, 4, 5, 6])
            payload["mag_b"] = rng.choice([2, 3, 4, 5])
            payload["angle_degrees"] = rng.choice([30, 45, 60, 90, 120, 150])
        result = compute_dot_product_from_magnitudes_angle(
            mag_a=payload["mag_a"],
            mag_b=payload["mag_b"],
            angle_degrees=payload["angle_degrees"],
        )
        question = (
            f"設 $\\left|\\vec{{a}}\\right|={canonical_exact(payload['mag_a'])}$、"
            f"$\\left|\\vec{{b}}\\right|={canonical_exact(payload['mag_b'])}$，"
            f"且兩向量夾角為 ${canonical_exact(payload['angle_degrees'])}^\\circ$，"
            f"試求 $\\vec{{a}}\\cdot\\vec{{b}}$。"
        )
        answer_value = result["canonical"]
        parts = {"dot": result["canonical"]}
        answer_type = "expression"
        explanation = [r"$\vec{a}\cdot\vec{b}=|\vec{a}||\vec{b}|\cos\theta$。"]

    elif op == PERPENDICULAR_PARAM_OP:
        if "a" not in payload or "b" not in payload:
            k_slot = rng.choice(["x", "y"])
            known = _rand_int(rng, -5, 5, nonzero=True)
            shift = _rand_int(rng, -3, 3, nonzero=True)
            if k_slot == "x":
                payload["a"] = ["k", known]
                payload["b"] = [f"k+{shift}" if shift > 0 else f"k{shift}", _rand_int(rng, -4, 4, nonzero=True)]
            else:
                payload["a"] = [known, "k"]
                payload["b"] = [_rand_int(rng, -4, 4, nonzero=True), f"k+{shift}" if shift > 0 else f"k{shift}"]
        result = solve_perpendicular_vector_parameter(
            a=payload["a"], b=payload["b"], parameter=str(payload.get("parameter") or "k")
        )
        ax, ay = payload["a"][0], payload["a"][1]
        bx, by = payload["b"][0], payload["b"][1]
        question = (
            f"設 $\\vec{{a}}=\\left( {ax},\\ {ay} \\right)$、"
            f"$\\vec{{b}}=\\left( {bx},\\ {by} \\right)$，"
            f"若 $\\vec{{a}}\\perp\\vec{{b}}$，試求參數之值。"
        )
        answer_value = result["canonical"]
        if isinstance(result["canonical"], list):
            parts = {f"k{i+1}": v for i, v in enumerate(result["canonical"])}
            answer_value = parts
            answer_type = "multi_part"
        else:
            parts = {"k": result["canonical"]}
            answer_type = "expression"
        explanation = [r"垂直條件：$\vec{a}\cdot\vec{b}=0$。"]

    elif op == COSINE_FROM_DOT_OP:
        if "a" not in payload or "b" not in payload:
            payload["a"] = list(_sample_pair(rng))
            payload["b"] = list(_sample_pair(rng))
        result = compute_cosine_of_angle_from_dot(a=payload["a"], b=payload["b"])
        ax, ay = _as_pair(payload["a"])
        bx, by = _as_pair(payload["b"])
        question = (
            f"已知 $\\vec{{a}}={latex_pair(ax, ay)}$、$\\vec{{b}}={latex_pair(bx, by)}$，"
            f"試求 $\\cos\\theta$，其中 $\\theta$ 為兩向量夾角。"
        )
        answer_value = result["canonical"]
        parts = {"cosine": result["canonical"]}
        answer_type = "expression"
        explanation = [r"$\cos\theta=(\vec{a}\cdot\vec{b})/(|\vec{a}||\vec{b}|)$。"]

    elif op == LINEAR_COMBO_OP:
        if "terms" not in payload:
            n_terms = rng.choice([2, 3])
            payload["terms"] = [
                {"coeff": _rand_int(rng, -4, 4, nonzero=True), "vector": list(_sample_pair(rng))}
                for _ in range(n_terms)
            ]
        result = compute_vector_linear_combination(terms=payload["terms"])
        term_bits = []
        for term in payload["terms"]:
            c = canonical_exact(term.get("coeff", 1))
            vx, vy = _as_pair(term["vector"])
            term_bits.append(f"{c}{latex_pair(vx, vy)}")
        question = "試以坐標表示向量 $" + "+".join(term_bits).replace("+-", "-") + "$。"
        answer_value = result["canonical"]
        parts = {"vector": result["canonical"]}
        answer_type = "expression"
        explanation = ["各向量分量分別乘係數後相加。"]

    elif op == SCALED_DIRECTION_OP:
        if "vector" not in payload:
            payload["vector"] = list(_sample_pair(rng))
        if "length" not in payload:
            payload["length"] = rng.choice([1, 2, 3, 4, 5])
        if "direction" not in payload:
            payload["direction"] = rng.choice(["same", "opposite"])
        direction = str(payload.get("direction") or "same")
        result = compute_scaled_direction_vector(
            vector=payload["vector"], length=payload["length"], direction=direction
        )
        vx, vy = _as_pair(payload["vector"])
        L = canonical_exact(payload["length"])
        question = (
            f"設 $\\vec{{a}}={latex_pair(vx, vy)}$，試求與 $\\vec{{a}}$ "
            f"{'同方向' if direction == 'same' else '反方向'}且長度為 ${L}$ 的向量。"
        )
        distractors = _scaled_direction_distractors(
            correct=result["result"],
            vector=payload["vector"],
            length=payload["length"],
            direction=direction,
            rng=rng,
        )
        if payload.get("with_unit"):
            parts = {"unit": result["canonical_unit"], "vector": result["canonical"]}
            answer_value = parts
            answer_type = "multi_part"
        else:
            answer_value = result["canonical"]
            parts = {"vector": result["canonical"]}
            answer_type = "expression"
        explanation = ["先求單位向量，再乘上指定長度。"]

    elif op == TRIANGLE_CHAIN_OP:
        if "ab" not in payload or "bc" not in payload:
            payload["ab"] = list(_sample_pair(rng))
            payload["bc"] = list(_sample_pair(rng))
        result = compute_triangle_chain_and_perimeter(ab=payload["ab"], bc=payload["bc"])
        abx, aby = _as_pair(payload["ab"])
        bcx, bcy = _as_pair(payload["bc"])
        question = (
            f"$\\triangle ABC$ 中，已知 $\\overrightarrow{{AB}}={latex_pair(abx, aby)}$、"
            f"$\\overrightarrow{{BC}}={latex_pair(bcx, bcy)}$，試求："
            f"(1) $\\overrightarrow{{AC}}$；(2) $\\triangle ABC$ 之周長。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"$\overrightarrow{AC}=\overrightarrow{AB}+\overrightarrow{BC}$，周長為三邊長和。"]

    else:
        raise ValueError(f"unsupported_vector_plane_operation:{op}")

    if payload.get("question_text"):
        question = str(payload["question_text"])

    if choice_meta:
        presentation = "single_choice"
        answer_type = "single_choice"
        answer_value = choice_meta["semantic_answer"]

    givens = _json_value({k: v for k, v in payload.items() if k != "question_text"})
    matrix = {
        "givens": givens,
        "answer": {
            "value": answer_value,
            "canonical_form": answer_value,
            "general_form": answer_value,
            "coefficients": [],
            "parts": parts,
        },
        "question_text": question,
        "question": question,
        "explanation_steps": explanation,
        "distractors": distractors,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "presentation_mode": presentation,
            "answer_type": answer_type,
            "seed": 0 if seed is None else int(seed),
        },
        "visual_spec": {"kind": "none"},
        "domain_result": _json_value(result),
    }
    if choice_meta:
        matrix["choices"] = choice_meta["choices"]
        matrix["correct_label"] = choice_meta["correct_label"]
        matrix["semantic_answer"] = choice_meta["semantic_answer"]
        if not matrix.get("distractors"):
            semantic = str(choice_meta.get("semantic_answer") or "")
            matrix["distractors"] = [
                str(c.get("value") or c.get("text") or "").strip().strip("$")
                for c in choice_meta.get("choices") or []
                if isinstance(c, dict)
                and str(c.get("value") or c.get("text") or "").strip().strip("$") != semantic
            ]
    return matrix


def validate_vector_plane_matrix(matrix: dict[str, Any]) -> bool:
    try:
        facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
        op = facts["domain_operation"]
        givens = dict(matrix.get("givens") or {})
        seed = facts.get("seed", givens.pop("seed", None))
        rebuilt = build_vector_plane_matrix(operation=op, seed=seed, **givens)
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
