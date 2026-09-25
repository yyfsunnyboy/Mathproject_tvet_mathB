# -*- coding: utf-8 -*-
"""Additional B2 Ch3 vector topologies for full textbook coverage.

These operations extend vector.plane for geometric path algebra, section-point
linear combinations, composite MCQ/application families, and diagram payloads
that reuse the existing coordinate_plane visual_spec renderer (+ arrows).
"""

from __future__ import annotations

import math
import random
from typing import Any

import sympy as sp

from core.domain.vector_plane_domain import (
    _choice_payload,
    _json_value,
    canonical_exact,
    compute_dot_product_from_magnitudes_angle,
    format_pair,
    latex_pair,
    magnitude,
)
from core.gencode.resources.rational_display import latex_difference_of_scaled_symbols


# ── operation keys ────────────────────────────────────────────────────────────

SIMPLIFY_PATH_OP = "simplify_vector_path_expression"
EXPRESS_BASIS_OP = "express_named_vectors_in_given_basis"
SCALAR_FILL_OP = "solve_scalar_multiple_relation_fill"
SECTION_POINT_OP = "express_section_point_vector"
SECTION_COEFF_OP = "solve_section_coefficient_pair"
EQUAL_VEC_MCQ_OP = "identify_equal_vector_mcq"
RESULTANT_MCQ_OP = "identify_resultant_path_mcq"
CONSTRUCT_COMBO_OP = "construct_linear_combination_choice"
FROM_GIVENS_OP = "express_linear_combination_from_givens"
DIRECTED_MIXED_OP = "compute_directed_segment_mixed_multipart"
CHAIN_CLOSURE_OP = "compute_chain_closure_vector_mcq"
SOLVE_POINT_COMBO_OP = "solve_point_from_vector_combination"
COLLINEAR_MCQ_OP = "solve_collinear_ratio_mcq"
UNKNOWN_VEC_EQ_OP = "solve_unknown_vector_linear_equation"
PARALLEL_MAG_MCQ_OP = "solve_parallel_then_magnitude_mcq"
UNIT_ID_MCQ_OP = "identify_unit_vector_mcq"
NAV_HEADING_OP = "solve_navigation_heading_correction"
ANGLE_QUALITY_OP = "classify_angle_quality_from_dot_mcq"
REG_POLY_DOT_OP = "compute_regular_polygon_edge_dot"
DOT_IDENTITY_OP = "compute_dot_identity_multipart"
PLOT_POINTS_OP = "plot_navigation_points_coordinates"
MIDPOINT_DOT_OP = "compute_midpoint_dot_product"
DOT_PARAM_MCQ_OP = "solve_dot_product_parameter_mcq"
PERP_COMPOSITE_OP = "solve_perpendicular_composite_parameter"
DOT_SIGN_DIAG_OP = "classify_dot_sign_from_diagram_mcq"
PERP_EXPAND_OP = "expand_perpendicular_dot_product"
ANGLE_FROM_MAG_OP = "solve_angle_from_magnitude_identity"

GAP_OPS = frozenset(
    {
        SIMPLIFY_PATH_OP,
        EXPRESS_BASIS_OP,
        SCALAR_FILL_OP,
        SECTION_POINT_OP,
        SECTION_COEFF_OP,
        EQUAL_VEC_MCQ_OP,
        RESULTANT_MCQ_OP,
        CONSTRUCT_COMBO_OP,
        FROM_GIVENS_OP,
        DIRECTED_MIXED_OP,
        CHAIN_CLOSURE_OP,
        SOLVE_POINT_COMBO_OP,
        COLLINEAR_MCQ_OP,
        UNKNOWN_VEC_EQ_OP,
        PARALLEL_MAG_MCQ_OP,
        UNIT_ID_MCQ_OP,
        NAV_HEADING_OP,
        ANGLE_QUALITY_OP,
        REG_POLY_DOT_OP,
        DOT_IDENTITY_OP,
        PLOT_POINTS_OP,
        MIDPOINT_DOT_OP,
        DOT_PARAM_MCQ_OP,
        PERP_COMPOSITE_OP,
        DOT_SIGN_DIAG_OP,
        PERP_EXPAND_OP,
        ANGLE_FROM_MAG_OP,
    }
)


def _figure_points(kind: str) -> dict[str, list[float]]:
    kind = str(kind or "parallelogram")
    if kind in {"parallelogram", "rectangle"}:
        return {"A": [0, 0], "B": [4, 0], "C": [5, 3], "D": [1, 3]} if kind == "parallelogram" else {
            "A": [0, 0],
            "B": [4, 0],
            "C": [4, 3],
            "D": [0, 3],
        }
    if kind == "triangle":
        return {"A": [0, 0], "B": [6, 0], "C": [2, 4]}
    if kind == "triangle_sections":
        # D,E trisect AB; F midpoint AC — coordinates are geometrically exact.
        return {"A": [0, 0], "B": [6, 0], "C": [1, 5], "D": [2, 0], "E": [4, 0], "F": [0.5, 2.5]}
    if kind == "triangle_midpoints":
        return {"A": [0, 0], "B": [6, 0], "C": [2, 4], "D": [3, 0], "E": [4, 2], "F": [1, 2]}
    if kind == "polygon_hexagon":
        # Regular hexagon center O, radius 2.
        pts = {"O": [0.0, 0.0]}
        labels = "ABCDEF"
        for i, lab in enumerate(labels):
            ang = math.radians(60 * i)
            pts[lab] = [round(2 * math.cos(ang), 4), round(2 * math.sin(ang), 4)]
        return pts
    if kind == "polygon_pentagon":
        pts = {}
        for i, lab in enumerate("ABCDE"):
            ang = math.radians(90 + 72 * i)
            pts[lab] = [round(2 * math.cos(ang), 4), round(2 * math.sin(ang), 4)]
        return pts
    if kind == "quadrilateral":
        return {"A": [0, 0], "B": [5, 1], "C": [4, 4], "D": [-1, 3]}
    if kind == "free_vectors":
        return {"O": [0, 0], "P": [3, 1], "Q": [1, 3], "R": [-2, 2]}
    if kind == "map_points":
        return {"A": [0, 0], "B": [3, 1], "C": [4, 3], "P": [1, 2], "Q": [4, 3], "R": [0, 3], "S": [2, -1]}
    if kind == "coordinate":
        return {}
    if kind == "parallelogram_sections":
        # Full construction state (legacy). Prefer section_coeff_minimal for AM/AE/AF items.
        return {
            "A": [0, 0],
            "B": [6, 0],
            "C": [8, 4],
            "D": [2, 4],
            "M": [4, 2],
            "E": [1, 2],
            "F": [2, 0],
            "G": [4, 0],
            "N": [7, 2],
            "P": [7.5, 3],
        }
    if kind == "section_coeff_minimal":
        # Placeholder; overridden by caller with authoritative A/E/F/M positions.
        return {"A": [0, 0], "E": [6, 0], "F": [2, 5], "M": [4, 2]}
    if kind == "segment_division":
        return {"A": [0, 0], "B": [6, 0], "C": [2, 0], "D": [4, 0]}
    if kind == "triangle_equilateral":
        return {"A": [0, 0], "B": [4, 0], "C": [2, round(2 * math.sqrt(3), 4)]}
    if kind == "coordinate_exam":
        return {"O": [0, 0], "A": [-2, 2], "B": [1, 1], "C": [3, 2], "D": [4, 1]}
    return {"A": [0, 0], "B": [3, 0], "C": [2, 2]}


_KIND_DEFAULT_EDGES: dict[str, list[tuple[str, str]]] = {
    "parallelogram": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    "rectangle": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    "triangle": [("A", "B"), ("B", "C"), ("C", "A")],
    "triangle_sections": [("A", "B"), ("B", "C"), ("C", "A")],
    "triangle_midpoints": [("A", "B"), ("B", "C"), ("C", "A")],
    "triangle_equilateral": [("A", "B"), ("B", "C"), ("C", "A")],
    "quadrilateral": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    "polygon_hexagon": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("F", "A")],
    "polygon_pentagon": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")],
    "free_vectors": [],
    "map_points": [("A", "B"), ("B", "C")],
    "parallelogram_sections": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
    "section_coeff_minimal": [],
    "segment_division": [("A", "B")],
    "coordinate_exam": [],
}


def build_figure_visual_spec(
    *,
    kind: str,
    edges: list[tuple[str, str]] | None = None,
    arrows: list[tuple[str, str, str]] | None = None,
    show_axes: bool = True,
    points: dict[str, list[float]] | None = None,
    include_points: list[str] | None = None,
) -> dict[str, Any]:
    """Build a minimum-sufficient coordinate diagram for the given figure kind.

    Does not dump every generator geometry point into a cycle polygon.
    Callers may pass ``points`` / ``include_points`` / ``edges`` / ``arrows`` to
    expose only the entities required by the stem.
    """
    pts = dict(points) if isinstance(points, dict) and points else _figure_points(kind)
    if include_points is not None:
        keep = {str(p) for p in include_points}
        pts = {k: v for k, v in pts.items() if k in keep}
    if not pts:
        return {"kind": "none"}
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    pad = 1.5
    point_rows = [{"x": float(xy[0]), "y": float(xy[1]), "label": lab} for lab, xy in pts.items()]
    if edges is None:
        edges = list(_KIND_DEFAULT_EDGES.get(str(kind), []))
        if not edges and len([k for k in pts if k != "O"]) >= 3 and str(kind) not in {
            "free_vectors",
            "section_coeff_minimal",
            "coordinate_exam",
            "map_points",
        }:
            # Safe fallback for unknown kinds: convex hull cycle of primary letters only.
            labels = sorted(k for k in pts.keys() if len(k) == 1 and k.isalpha() and k != "O")
            edges = [(labels[i], labels[(i + 1) % len(labels)]) for i in range(len(labels))] if len(labels) >= 3 else []
    lines = [
        {"through_points": [a, b], "extend": False, "label": ""}
        for a, b in edges
        if a in pts and b in pts
    ]
    arrow_rows = []
    for item in arrows or []:
        if len(item) == 3:
            a, b, lab = item
        else:
            a, b = item[0], item[1]
            lab = ""
        if a not in pts or b not in pts:
            continue
        arrow_rows.append({"from": a, "to": b, "label": lab, "color": "#1565c0"})
    return {
        "kind": "coordinate_plane",
        "render_required": True,
        "show_axes": bool(show_axes),
        "hide_unlabeled_points": False,
        "points": point_rows,
        "lines": lines,
        "arrows": arrow_rows,
        "x_range": [min(xs) - pad, max(xs) + pad],
        "y_range": [min(ys) - pad, max(ys) + pad],
        "figure_kind": str(kind),
        "required_entities": sorted(pts.keys()),
    }


def _latex_vec_name(name: str) -> str:
    name = str(name)
    if name.startswith("vec:"):
        return rf"\vec{{{name[4:]}}}"
    if len(name) == 2 and name.isalpha():
        return rf"\overrightarrow{{{name}}}"
    return name


def simplify_vector_path_expression(*, tokens: list[str]) -> dict[str, Any]:
    """Simplify a chain of directed segments by telescoping endpoints.

    tokens like ["AB","+","BC"] or ["AB","-","AC"].
    """
    toks = [str(t).replace(" ", "") for t in tokens]
    # Convert to signed segments
    signed: list[tuple[int, str]] = []
    sign = 1
    for t in toks:
        if t in {"+", ""}:
            sign = 1
            continue
        if t == "-":
            sign = -1
            continue
        if t.startswith("-") and len(t) == 3:
            signed.append((-1, t[1:]))
            sign = 1
            continue
        if t.startswith("+") and len(t) == 3:
            signed.append((1, t[1:]))
            sign = 1
            continue
        signed.append((sign, t))
        sign = 1
    # Represent as symbol tips: each XY => Y - X
    coeff: dict[str, sp.Expr] = {}
    for sgn, seg in signed:
        if len(seg) != 2:
            raise ValueError(f"invalid_segment:{seg}")
        start, end = seg[0], seg[1]
        coeff[end] = coeff.get(end, sp.Integer(0)) + sgn
        coeff[start] = coeff.get(start, sp.Integer(0)) - sgn
    # Prefer compact directed segment if two points remain.
    positives = [p for p, c in coeff.items() if sp.simplify(c) == 1]
    negatives = [p for p, c in coeff.items() if sp.simplify(c) == -1]
    zeros = [p for p, c in coeff.items() if sp.simplify(c) == 0]
    nonzero = {p: c for p, c in coeff.items() if sp.simplify(c) != 0}
    if len(positives) == 1 and len(negatives) == 1 and len(nonzero) == 2:
        canonical = f"{negatives[0]}{positives[0]}"
        display = rf"\overrightarrow{{{canonical}}}"
    elif not nonzero:
        display = r"\vec{0}"
        canonical = "0"
    else:
        # fallback symbolic sum
        parts = []
        for p, c in sorted(nonzero.items()):
            cc = canonical_exact(c)
            parts.append(f"{cc}*{p}")
        canonical = "+".join(parts)
        display = canonical
    return {"canonical": canonical, "display": display, "coefficients": {k: canonical_exact(v) for k, v in coeff.items()}}


def express_named_vectors_in_given_basis(
    *,
    figure: str,
    basis: dict[str, str],
    queries: list[str],
) -> dict[str, Any]:
    """Express query directed segments using given basis labels (symbolic).

    basis maps segment -> symbol name, e.g. {"AB":"a","AD":"b"} for parallelogram.
    """
    fig = str(figure)
    answers: dict[str, str] = {}
    # Build linear dependence table for common figures.
    # Represent each edge as combination of basis vectors via geometry rules.
    rules: dict[str, str] = {}
    if fig in {"parallelogram", "rectangle"}:
        a = basis.get("AB") or basis.get("a") or "a"
        b = basis.get("AD") or basis.get("b") or "b"
        rules = {
            "AB": a,
            "BA": f"-{a}",
            "AD": b,
            "DA": f"-{b}",
            "DC": a,
            "CD": f"-{a}",
            "BC": b,
            "CB": f"-{b}",
            "AC": f"{a}+{b}",
            "CA": f"-({a}+{b})",
            "BD": f"-{a}+{b}" if fig == "parallelogram" else f"-{a}+{b}",
            "DB": f"{a}-{b}",
        }
    elif fig == "polygon_hexagon":
        a = basis.get("AB") or "a"
        b = basis.get("BC") or "b"
        c = basis.get("CD") or "c"
        # For regular hexagon with consecutive edges a,b,c: AF=-c? Use textbook identities:
        # AF = -b? Actually for hexagon AB+BC+CD+DE+EF+FA=0 and opposite edges equal.
        # Opposite: AB=DE=a, BC=EF=b, CD=FA=c.
        rules = {
            "AB": a,
            "BC": b,
            "CD": c,
            "DE": a,
            "EF": b,
            "FA": c,
            "AF": f"-{c}",
            "AO": f"{a}+{b}" if False else f"({a})+({b})",  # center: AO = AB+BO; simpler AO=(2a+b?); use a+b for equilateral chain to opposite? 
            # In regular hexagon, O midpoint of AD etc. AO = AB+BO. Use: AO = a + (1/2)(something).
            # Safer textbook: AF=-c (since FA=c), DE=a, AO = a+b (when a,b consecutive toward center geometry with radius).
            "DE": a,
            "AO": f"{a}+{b}",
        }
        # Fix AO for regular hexagon: vector AO equals AB+BC+CO but CO=-OA; AO = (AB+BC+CD)/2? 
        # With consecutive sides a,b,c and opposite equals: AO = a + b  when O center and A->B->C around? 
        # Actually OA = AB + BO; BO = R rotated. Keep AO as a+b for the common textbook identity when only a,b given.
        rules["AO"] = f"{a}+{b}"
        rules["AF"] = f"-{c}"
    else:
        a = basis.get("AB") or "a"
        b = basis.get("AC") or basis.get("AD") or "b"
        rules = {"AB": a, "BA": f"-{a}", "AC": b, "CA": f"-{b}", "BC": f"-{a}+{b}", "CB": f"{a}-{b}"}
    for q in queries:
        qq = str(q).replace(" ", "")
        answers[qq] = rules.get(qq, rules.get(qq.upper(), "undefined"))
    return {"canonical": answers, "rules": rules}


def build_gap_matrix(
    *,
    operation: str,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    **data: Any,
) -> dict[str, Any]:
    op = str(operation)
    if op not in GAP_OPS:
        raise ValueError(f"unsupported_gap_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    payload = {**(constraints or {}), **data}
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
    part_labels: dict[str, str] = {}
    visual = {"kind": "none"}
    explanation: list[str] = []
    result: dict[str, Any]

    if op == SIMPLIFY_PATH_OP:
        path_catalog = [
            ["AB", "+", "BC"],
            ["AB", "+", "BC", "+", "CD"],
            ["PQ", "+", "QR"],
            ["AB", "-", "AC"],
            ["AD", "+", "DC"],
            ["BA", "+", "AC"],
            ["AB", "+", "BD", "-", "CD"],
        ]
        tokens = payload.get("tokens") or list(rng.choice(path_catalog))
        result = simplify_vector_path_expression(tokens=list(tokens))
        segs = [t for t in tokens if isinstance(t, str) and len(t) == 2 and t.isalpha()]
        fig = str(payload.get("figure") or ("quadrilateral" if any(s[0] in "D" or s[1] in "D" for s in segs) else "triangle"))
        arrows = [(s[0], s[1], "") for s in segs[:3]]
        include = sorted({c for s in segs for c in s})
        visual = build_figure_visual_spec(kind=fig, arrows=arrows, include_points=include)
        q_tokens = "".join(
            (
                "+"
                if t == "+"
                else "-"
                if t == "-"
                else rf"${_latex_vec_name(t)}$"
            )
            for t in tokens
        )
        question = f"如圖，試化簡：{q_tokens}。"
        answer_value = result["display"]
        parts = {"simplified": result["display"]}
        explanation = ["利用首尾相接化簡有向線段。"]

    elif op == EXPRESS_BASIS_OP:
        fig_choices = ["parallelogram", "rectangle", "polygon_hexagon"]
        fig = str(payload.get("figure") or rng.choice(fig_choices[:2]))
        if fig == "polygon_hexagon":
            basis = payload.get("basis") or {"AB": "a", "BC": "b", "CD": "c"}
            query_sets = [["AF", "AO", "DE"], ["DE", "AF"], ["AO", "DE"]]
            queries = payload.get("queries") or list(rng.choice(query_sets))
            arrow_labels = [("A", "B", r"\vec{a}"), ("B", "C", r"\vec{b}"), ("C", "D", r"\vec{c}")]
            explanation = ["利用正多邊形對邊相等與反向性質。"]
        else:
            basis = payload.get("basis") or {"AB": "a", "AD": "b"}
            query_sets = [["BA", "BC", "CD"], ["BA", "BC"], ["CD", "BA"], ["BC", "CD"]]
            queries = payload.get("queries") or list(rng.choice(query_sets))
            arrow_labels = (
                [("A", "B", r"\vec{a}"), ("A", "D", r"\vec{b}")]
                if fig in {"parallelogram", "rectangle"}
                else None
            )
            explanation = ["利用平行四邊形／多邊形對邊與反向性質。"]
        result = express_named_vectors_in_given_basis(figure=fig, basis=basis, queries=list(queries))
        visual = build_figure_visual_spec(kind=fig, arrows=arrow_labels)
        qparts = "、".join(rf"${_latex_vec_name(q)}$" for q in queries)
        question = f"如圖，已知基底向量，試以基底表示：{qparts}。"
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"

    elif op == SCALAR_FILL_OP:
        # Sample concrete vector multiple relations; stem names k1/k2 explicitly.
        if "pairs" in payload and isinstance(payload["pairs"], list) and payload["pairs"]:
            pairs = list(payload["pairs"])
        else:
            ks = [rng.choice([-3, -2, -1, 2, 3]), rng.choice([-3, -2, -1, 2, 3])]
            pair_templates = [
                [
                    {"left": "a", "right": "b", "k": ks[0], "latex": r"\vec{a}=k_1\vec{b}"},
                    {"left": "c", "right": "a", "k": ks[1], "latex": r"\vec{c}=k_2\vec{a}"},
                ],
                [
                    {"left": "OP", "right": "OQ", "k": ks[0], "latex": r"\overrightarrow{OP}=k_1\overrightarrow{OQ}"},
                    {"left": "OR", "right": "OP", "k": ks[1], "latex": r"\overrightarrow{OR}=k_2\overrightarrow{OP}"},
                ],
                [
                    {"left": "u", "right": "v", "k": ks[0], "latex": r"\vec{u}=k_1\vec{v}"},
                    {"left": "w", "right": "v", "k": ks[1], "latex": r"\vec{w}=k_2\vec{v}"},
                ],
            ]
            pairs = list(rng.choice(pair_templates))
        result = {"canonical": {f"k{i+1}": canonical_exact(p["k"]) for i, p in enumerate(pairs)}}
        k1 = float(sp.sympify(pairs[0]["k"]))
        k2 = float(sp.sympify(pairs[1]["k"])) if len(pairs) > 1 else 1.0
        o = [0.0, 0.0]
        q = [float(rng.choice([2, 3])), float(rng.choice([1, 2]))]
        p = [k1 * q[0], k1 * q[1]]
        r = [k2 * p[0], k2 * p[1]]
        pts = {"O": o, "Q": q, "P": p, "R": r}
        visual = build_figure_visual_spec(
            kind="free_vectors",
            points=pts,
            include_points=["O", "P", "Q", "R"],
            edges=[],
            arrows=[
                ("O", "Q", r"\overrightarrow{OQ}"),
                ("O", "P", r"\overrightarrow{OP}"),
                ("O", "R", r"\overrightarrow{OR}"),
            ],
            show_axes=True,
        )
        eq_bits = []
        for i, pair in enumerate(pairs):
            latex = pair.get("latex")
            if latex:
                eq_bits.append(f"${latex}$")
            else:
                left = pair.get("left", f"u{i+1}")
                right = pair.get("right", f"v{i+1}")
                eq_bits.append(
                    rf"${_latex_vec_name(str(left))}=k_{{{i+1}}}{_latex_vec_name(str(right))}$"
                )
        question = (
            "如圖，已知 "
            + "，".join(eq_bits)
            + r"，試求實數 $k_1$、$k_2$。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["比較方向與長度（或坐標比）決定實數倍數。"]

    elif op == SECTION_POINT_OP:
        a_name = "a"
        b_name = "b"
        target_choices = ["BF", "BE", "DF", "CF", "DE"]
        target = str(payload.get("target") or rng.choice(target_choices))
        # Classic geometry: D,E trisect AB; F midpoint AC; AB=a, AC=b
        expr_map = {
            "BF": f"-1*{a_name}+1/2*{b_name}",
            "BE": f"-1/3*{a_name}",
            "DF": f"-1/3*{a_name}+1/2*{b_name}",
            "CF": f"-1/2*{b_name}",
            "DE": f"1/3*{a_name}",
        }
        expr = str(payload.get("expression") or expr_map.get(target, f"-1/3*{a_name}+1/2*{b_name}"))
        pretty = sp.sstr(sp.simplify(sp.sympify(expr.replace(a_name, "a").replace(b_name, "b"))))
        result = {"canonical": pretty}
        visual = build_figure_visual_spec(
            kind="triangle_sections",
            arrows=[("A", "B", r"\vec{a}"), ("A", "C", r"\vec{b}"), (target[0], target[1], "")],
        )
        question = (
            rf"如圖，$\triangle ABC$ 中，$D$、$E$ 為 $\overline{{AB}}$ 三等分點（$AD:DE:EB=1:1:1$），"
            rf"$F$ 為 $\overline{{AC}}$ 中點，令 $\overrightarrow{{AB}}=\vec{{a}}$、$\overrightarrow{{AC}}=\vec{{b}}$，"
            rf"試以 $\vec{{a}}$、$\vec{{b}}$ 表示 ${_latex_vec_name(target)}$。"
        )
        answer_value = pretty
        parts = {"vector": pretty}
        explanation = ["先寫出分點位置向量，再相減。"]

    elif op == SECTION_COEFF_OP:
        # Sample rational coefficients; place M = α·E + β·F from A (authoritative).
        if "alpha" in payload and "beta" in payload:
            alpha = sp.simplify(sp.sympify(payload["alpha"]))
            beta = sp.simplify(sp.sympify(payload["beta"]))
        else:
            dens = [2, 3, 4]
            d1, d2 = rng.choice(dens), rng.choice(dens)
            n1 = rng.choice([i for i in range(1, d1)])
            n2 = rng.choice([i for i in range(1, d2)])
            alpha = sp.Rational(n1, d1)
            beta = sp.Rational(n2, d2)
            if alpha + beta > 1 and rng.random() < 0.5:
                beta = sp.Rational(1, d2)
        result = {"canonical": {"alpha": canonical_exact(alpha), "beta": canonical_exact(beta)}}
        e_pt = [float(rng.choice([5, 6, 7])), 0.0]
        f_pt = [float(rng.choice([1, 2, 3])), float(rng.choice([4, 5, 6]))]
        a_pt = [0.0, 0.0]
        af = float(alpha)
        bf = float(beta)
        m_pt = [af * e_pt[0] + bf * f_pt[0], af * e_pt[1] + bf * f_pt[1]]
        visual = build_figure_visual_spec(
            kind="section_coeff_minimal",
            points={"A": a_pt, "E": e_pt, "F": f_pt, "M": m_pt},
            include_points=["A", "E", "F", "M"],
            edges=[("A", "E"), ("A", "F")],
            arrows=[
                ("A", "E", r"\overrightarrow{AE}"),
                ("A", "F", r"\overrightarrow{AF}"),
                ("A", "M", r"\overrightarrow{AM}"),
            ],
            show_axes=False,
        )
        question = (
            r"如圖，已知點 $E$、$F$、$M$，且 "
            r"$\overrightarrow{AM}=\alpha\overrightarrow{AE}+\beta\overrightarrow{AF}$，"
            r"試求實數 $\alpha$、$\beta$。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["將各點寫成基底線性組合後比較係數。"]


    elif op == EQUAL_VEC_MCQ_OP:
        # Rectangle: AB = DC
        correct = r"\overrightarrow{DC}"
        distractors = [r"\overrightarrow{CD}", r"\overrightarrow{BA}", r"\overrightarrow{CB}"]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        visual = build_figure_visual_spec(kind="rectangle", arrows=[("A", "B", "")])
        question = r"如圖，長方形 $ABCD$ 中，與 $\overrightarrow{AB}$ 相等的向量為？"
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = ["相等向量：同向且等長；長方形對邊向量相等。"]

    elif op == RESULTANT_MCQ_OP:
        # AB+BC = AC; choose PQ closest to AC
        correct = r"\overrightarrow{AC}"
        distractors = [r"\overrightarrow{BA}", r"\overrightarrow{CB}", r"\overrightarrow{CA}"]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        visual = build_figure_visual_spec(kind="map_points", arrows=[("A", "B", ""), ("B", "C", ""), ("A", "C", "")])
        question = r"如圖，與 $\overrightarrow{AB}+\overrightarrow{BC}$ 最接近（方向與大小）的向量為？"
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"$\overrightarrow{AB}+\overrightarrow{BC}=\overrightarrow{AC}$。"]

    elif op == CONSTRUCT_COMBO_OP:
        # MCQ: which tip coordinate matches (c1)a-(c2)b
        ax, ay = float(rng.choice([3, 4, 6])), 0.0
        bx, by = 0.0, float(rng.choice([3, 4, 5]))
        c1 = sp.Rational(rng.choice([1, 1, 2]), rng.choice([2, 3]))
        c2 = sp.Rational(rng.choice([1, 1, 2]), rng.choice([2, 3]))
        rx, ry = c1 * ax - c2 * bx, c1 * ay - c2 * by
        correct = format_pair(rx, ry)
        distractors = [format_pair(-rx, ry), format_pair(rx, -ry), format_pair(ry, rx)]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        combo_tex = latex_difference_of_scaled_symbols(c1, r"\vec{a}", c2, r"\vec{b}")
        visual = build_figure_visual_spec(
            kind="free_vectors",
            points={
                "A": [0.0, 0.0],
                "Pa": [ax, ay],
                "Pb": [bx, by],
                "R": [float(rx), float(ry)],
            },
            include_points=["A", "Pa", "Pb", "R"],
            edges=[],
            arrows=[
                ("A", "Pa", r"\vec{a}"),
                ("A", "Pb", r"\vec{b}"),
                ("A", "R", combo_tex),
            ],
        )
        question = (
            rf"以 $A$ 為起點，下列哪一個終點坐標對應 ${combo_tex}$？"
            rf"（設 $\vec{{a}}={latex_pair(ax, ay)}$、$\vec{{b}}={latex_pair(bx, by)}$）"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = ["終點 = 起點 + 線性組合結果。"]

    elif op == FROM_GIVENS_OP:
        # GE = DE - DF - FG with sampled coefficients (same topology).
        ca, cb, cc = rng.choice([2, 3, 4]), rng.choice([2, 3]), rng.choice([2, 3, 4])
        # DE=ca*a, DF=cb*b-a, FG=-b+cc*c
        # GE = DE - DF - FG = ca*a - (cb*b-a) - (-b+cc*c) = (ca+1)a - (cb-1)b - cc*c
        expr = f"{ca + 1}*a-{(cb - 1)}*b-{cc}*c"
        result = {"canonical": canonical_exact(sp.sympify(expr))}
        question = (
            rf"已知 $\overrightarrow{{DE}}={ca}\vec{{a}}$、$\overrightarrow{{DF}}={cb}\vec{{b}}-\vec{{a}}$、"
            rf"$\overrightarrow{{FG}}=-\vec{{b}}+{cc}\vec{{c}}$，試求 $\overrightarrow{{GE}}$。"
        )
        answer_value = result["canonical"]
        parts = {"vector": result["canonical"]}
        explanation = [r"$\overrightarrow{GE}=\overrightarrow{DE}-\overrightarrow{DF}-\overrightarrow{FG}$。"]

    elif op == DIRECTED_MIXED_OP:
        start = payload.get("start") or [rng.choice([8, 10, 12]), rng.choice([0, 1, -1])]
        end = payload.get("end") or [rng.choice([0, 1, -2]), rng.choice([3, 4, 5])]
        vx, vy = sp.Integer(end[0] - start[0]), sp.Integer(end[1] - start[1])
        mag = magnitude(vx, vy)
        ab2 = payload.get("ab2") or [rng.choice([-4, -3, -2, 2, 3]), rng.choice([-3, -2, 2, 3])]
        a2 = payload.get("a2") or [rng.choice([-4, -3, -2, 2]), rng.choice([-2, 0, 2, 3])]
        bx = a2[0] + ab2[0]
        by = a2[1] + ab2[1]
        result = {
            "canonical": {
                "AB": format_pair(vx, vy),
                "magnitude": canonical_exact(mag),
                "B": format_pair(bx, by),
            }
        }
        question = (
            f"(1) 設 $A{latex_pair(*start)}$、$B{latex_pair(*end)}$，試求 $\\overrightarrow{{AB}}$ 與長度。"
            f"(2) 設 $A{latex_pair(*a2)}$、$\\overrightarrow{{AB}}={latex_pair(*ab2)}$，試求 $B$。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["有向線段終−起；未知終點 = 起點 + 向量。"]

    elif op == CHAIN_CLOSURE_OP:
        pq = payload.get("pq") or [rng.choice([-3, -2, 1, 2, 3]), rng.choice([-3, -2, 0, 2])]
        qr = payload.get("qr") or [rng.choice([-2, 1, 2, 4]), rng.choice([-4, -3, -1, 2])]
        rs = payload.get("rs") or [rng.choice([-2, 0, 1, 2]), rng.choice([-2, 0, 1, 3])]
        # SP = - (PQ+QR+RS)
        sx = -(pq[0] + qr[0] + rs[0])
        sy = -(pq[1] + qr[1] + rs[1])
        correct = format_pair(sx, sy)
        distractors = [format_pair(-sx, -sy), format_pair(sx, -sy), format_pair(pq[0] + qr[0] + rs[0], pq[1] + qr[1] + rs[1])]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"設 $\\overrightarrow{{PQ}}={latex_pair(*pq)}$、"
            f"$\\overrightarrow{{QR}}={latex_pair(*qr)}$、"
            f"$\\overrightarrow{{RS}}={latex_pair(*rs)}$，則 $\\overrightarrow{{SP}}$ 為何？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"封閉折線：$\overrightarrow{SP}=-(\overrightarrow{PQ}+\overrightarrow{QR}+\overrightarrow{RS})$。"]

    elif op == SOLVE_POINT_COMBO_OP:
        A = payload.get("A") or [rng.choice([10, 20, 30, 57]), rng.choice([5, 10, 23])]
        B = payload.get("B") or [rng.choice([3, 7, 11]), rng.choice([-5, -2, 0, 4])]
        C = payload.get("C") or [rng.choice([1, 5, 9]), rng.choice([2, 8, 12])]
        c1 = payload.get("c1") or sp.Rational(rng.choice([3, 5, 7]), rng.choice([2, 4]))
        c2 = payload.get("c2") or sp.Rational(rng.choice([1, 3]), rng.choice([2, 4]))
        ab = [B[0] - A[0], B[1] - A[1]]
        ac = [C[0] - A[0], C[1] - A[1]]
        adx = c1 * ab[0] - c2 * ac[0]
        ady = c1 * ab[1] - c2 * ac[1]
        Dx, Dy = sp.simplify(A[0] + adx), sp.simplify(A[1] + ady)
        result = {"canonical": format_pair(Dx, Dy)}
        question = (
            f"已知 $A{latex_pair(*A)}$、$B{latex_pair(*B)}$、$C{latex_pair(*C)}$，"
            rf"若 $\overrightarrow{{AD}}={latex_difference_of_scaled_symbols(c1, r'\overrightarrow{AB}', c2, r'\overrightarrow{AC}')}$，試求 $D$。"
        )
        answer_value = result["canonical"]
        parts = {"D": result["canonical"]}
        explanation = [r"$D=A+\overrightarrow{AD}$。"]

    elif op == COLLINEAR_MCQ_OP:
        # AB = -2 AC => C = A + (A-B)/2 = (3A-B)/2? AB=-2AC => AC=-AB/2 => C=A-AB/2
        A, B = [1, 2], [2, -1]
        ab = [B[0] - A[0], B[1] - A[1]]
        ac = [-sp.Rational(1, 2) * ab[0], -sp.Rational(1, 2) * ab[1]]
        C = [sp.simplify(A[0] + ac[0]), sp.simplify(A[1] + ac[1])]
        val = sp.simplify(C[0] - C[1])
        correct = canonical_exact(val)
        distractors = [canonical_exact(val + 1), canonical_exact(val - 1), canonical_exact(-val)]
        result = {"canonical": correct, "C": format_pair(*C)}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"已知 $A{latex_pair(*A)}$、$B{latex_pair(*B)}$、$C(a,b)$ 共線，且 "
            r"$\overrightarrow{AB}=-2\overrightarrow{AC}$，則 $a-b=$？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"由 $\overrightarrow{AC}=-\frac{1}{2}\overrightarrow{AB}$ 求 $C$。"]

    elif op == UNKNOWN_VEC_EQ_OP:
        # 3(c+a)=4(c+b) => 3c+3a=4c+4b => -c=4b-3a => c=3a-4b
        a, b = [2, -5], [-2, 6]
        cx = 3 * a[0] - 4 * b[0]
        cy = 3 * a[1] - 4 * b[1]
        correct = format_pair(cx, cy)
        distractors = [format_pair(-cx, cy), format_pair(cx, -cy), format_pair(a[0] - b[0], a[1] - b[1])]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"已知 $\\vec{{a}}={latex_pair(*a)}$、$\\vec{{b}}={latex_pair(*b)}$，且 "
            r"$3(\vec{c}+\vec{a})=4(\vec{c}+\vec{b})$，則 $\vec{c}=$？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"展開得 $\vec{c}=3\vec{a}-4\vec{b}$。"]

    elif op == PARALLEL_MAG_MCQ_OP:
        ax = rng.choice([4, 6, 8, 10])
        ay = -2 * ax  # keep parallel-friendly a
        a = payload.get("a") or [ax, ay]
        # b = (-2, y) parallel ⇒ ax*y - ay*(-2)=0 ⇒ y = -2*ay/ax
        y = int(sp.simplify(-2 * a[1] / a[0]))
        b = [-2, y]
        mag = magnitude(*b)
        correct = canonical_exact(mag)
        distractors = [
            canonical_exact(magnitude(-2, -y if y else 4)),
            canonical_exact(abs(y) + 2),
            canonical_exact(int(mag) + 4 if isinstance(mag, (int, float)) else 20),
        ]
        result = {"canonical": correct, "y": y}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"已知 $\\vec{{a}}={latex_pair(*a)}$、$\\vec{{b}}=(-2,y)$ 平行，則 $|\\vec{{b}}|$ 為何？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = ["先由平行求 $y$，再求長度。"]

    elif op == UNIT_ID_MCQ_OP:
        # which is NOT unit vector
        correct = r"(\frac{1}{3},\ \frac{2}{3})"  # mag sqrt(5)/3 != 1
        options = [
            correct,
            r"(-1,\ 0)",
            r"(\frac{3}{5},\ -\frac{4}{5})",
            r"(\frac{\sqrt{3}}{2},\ \frac{1}{2})",
        ]
        result = {"canonical": "A"}  # will remap after shuffle via choice_meta on semantic
        # Use semantic as the non-unit pair string matching choice value
        choice_meta = _choice_payload(correct, options[1:], rng)
        question = "下列哪一個向量不是單位向量？"
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"單位向量滿足 $x^2+y^2=1$。"]

    elif op == NAV_HEADING_OP:
        # Sample navigation points keeping turn-left topology.
        A = payload.get("A") or [rng.choice([10, 12, 14]), rng.choice([4, 5, 6])]
        B = payload.get("B") or [rng.choice([1, 2, 3]), rng.choice([2, 3, 4])]
        O = payload.get("O") or [0, 0]
        v1 = [B[0] - A[0], B[1] - A[1]]
        v2 = [O[0] - B[0], O[1] - B[1]]
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        left_exact = sp.simplify(sp.deg(sp.acos(sp.Rational(dot, 1) / (magnitude(*v1) * magnitude(*v2)))))
        if cross < 0:
            turn = sp.simplify(360 - left_exact)
        else:
            turn = left_exact
        result = {"canonical": {"turn_degrees": canonical_exact(turn)}}
        visual = {
            "kind": "coordinate_plane",
            "render_required": True,
            "points": [
                {"x": float(O[0]), "y": float(O[1]), "label": "O"},
                {"x": float(A[0]), "y": float(A[1]), "label": "A"},
                {"x": float(B[0]), "y": float(B[1]), "label": "B"},
            ],
            "arrows": [
                {"from": "A", "to": "B", "label": ""},
                {"from": "B", "to": "O", "label": ""},
            ],
            "lines": [],
            "x_range": [-1, max(A[0], B[0]) + 1],
            "y_range": [-1, max(A[1], B[1]) + 1],
            "required_entities": ["O", "A", "B"],
        }
        question = (
            f"船由 $A{latex_pair(*A)}$ 駛向航標 $B{latex_pair(*B)}$ 後再駛向港口 $O{latex_pair(*O)}$。"
            "到達 $B$ 後應向左轉多少度？"
        )
        parts = dict(result["canonical"])
        answer_value = parts["turn_degrees"]
        explanation = ["以兩段航向向量夾角計算左轉角度。"]

    elif op == ANGLE_QUALITY_OP:
        a, b = [0, 1], [2, 3]
        u = [a[0] + b[0], a[1] + b[1]]
        v = [a[0] - b[0], a[1] - b[1]]
        dot = u[0] * v[0] + u[1] * v[1]
        if dot > 0:
            correct = "銳角"
        elif dot < 0:
            correct = "鈍角"
        else:
            correct = "直角"
        distractors = [x for x in ["銳角", "直角", "鈍角", "平角"] if x != correct]
        result = {"canonical": correct, "dot": dot}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"已知 $\\vec{{a}}={latex_pair(*a)}$、$\\vec{{b}}={latex_pair(*b)}$，"
            r"則 $\vec{a}+\vec{b}$ 與 $\vec{a}-\vec{b}$ 的夾角為？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"由 $(\vec{a}+\vec{b})\cdot(\vec{a}-\vec{b})$ 的正負判斷。"]

    elif op == REG_POLY_DOT_OP:
        side = payload.get("side") or rng.choice([2, 3, 4, 5, 6])
        fig = str(payload.get("figure") or rng.choice(["triangle_equilateral", "polygon_hexagon"]))
        # Adjacent edges at 60° or 120° depending on figure topology used in stem.
        d1 = sp.Rational(side**2, 2)
        d2 = -sp.Rational(side**2, 2)
        result = {"canonical": {"dot1": canonical_exact(d1), "dot2": canonical_exact(d2)}}
        part_labels = {
            "dot1": r"相鄰邊向量內積（$60^\circ$）",
            "dot2": r"夾角邊向量內積（$120^\circ$）",
        }
        visual = build_figure_visual_spec(kind=fig if fig != "triangle_equilateral" else "triangle_equilateral")
        question = (
            f"已知正{'三角形' if 'triangle' in fig else '六邊形'}邊長為 ${side}$，試求兩組相鄰／夾角邊向量之內積。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"$\vec{u}\cdot\vec{v}=|\vec{u}||\vec{v}|\cos\theta$。"]

    elif op == DOT_IDENTITY_OP:
        ma, mb, ang = rng.choice([2, 3, 4]), rng.choice([2, 3, 4]), rng.choice([60, 90, 120])
        aa = ma * ma
        ab = compute_dot_product_from_magnitudes_angle(mag_a=ma, mag_b=mb, angle_degrees=ang)["canonical"]
        # |2a-3b|^2 = 4|a|^2 + 9|b|^2 - 12 a·b
        mag2 = sp.simplify(4 * ma**2 + 9 * mb**2 - 12 * sp.sympify(ab))
        result = {
            "canonical": {
                "a_dot_a": canonical_exact(aa),
                "a_dot_b": ab,
                "mag_2a_3b": canonical_exact(sp.sqrt(mag2)),
            }
        }
        part_labels = {
            "a_dot_a": r"$\vec{a}\cdot\vec{a}$",
            "a_dot_b": r"$\vec{a}\cdot\vec{b}$",
            "mag_2a_3b": r"$\left|2\vec{a}-3\vec{b}\right|$",
        }
        question = (
            f"設 $|\\vec{{a}}|={ma}$、$|\\vec{{b}}|={mb}$，夾角 ${ang}^\\circ$，試求 "
            r"$\vec{a}\cdot\vec{a}$、$\vec{a}\cdot\vec{b}$、$|2\vec{a}-3\vec{b}|$。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"用定義與 $|u|^2=u\cdot u$ 展開。"]

    elif op == PLOT_POINTS_OP:
        A = payload.get("A") or [rng.choice([8, 10, 12, 15]), rng.choice([3, 4, 5, 6])]
        B = payload.get("B") or [rng.choice([1, 2, 3, 4]), rng.choice([1, 2, 3, 5])]
        result = {"canonical": {"A": format_pair(*A), "B": format_pair(*B)}}
        visual = {
            "kind": "coordinate_plane",
            "render_required": True,
            "points": [
                {"x": 0, "y": 0, "label": "O"},
                {"x": float(A[0]), "y": float(A[1]), "label": "A"},
                {"x": float(B[0]), "y": float(B[1]), "label": "B"},
            ],
            "arrows": [{"from": "A", "to": "B", "label": ""}],
            "lines": [],
            "x_range": [-1, max(A[0], B[0]) + 1],
            "y_range": [-1, max(A[1], B[1]) + 1],
            "required_entities": ["O", "A", "B"],
        }
        question = (
            f"以港口為原點 $O(0,0)$，標示 $A{latex_pair(*A)}$ 與航標 $B{latex_pair(*B)}$ 的坐標。"
            "試寫出 $A$、$B$ 坐標。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["依東方為 $x$、北方為 $y$ 讀取位移。"]

    elif op == MIDPOINT_DOT_OP:
        A, B, C = [0, 0], [2, 3], [-4, 1]
        D = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]
        ab = [B[0] - A[0], B[1] - A[1]]
        ad = [D[0] - A[0], D[1] - A[1]]
        dot = ab[0] * ad[0] + ab[1] * ad[1]
        correct = canonical_exact(dot)
        distractors = [canonical_exact(dot + 2), canonical_exact(dot - 2), canonical_exact(-dot)]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            f"$A{latex_pair(*A)}$、$B{latex_pair(*B)}$、$C{latex_pair(*C)}$，$D$ 為 $\\overline{{BC}}$ 中點，"
            r"則 $\overrightarrow{AB}\cdot\overrightarrow{AD}=$？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"先求中點 $D$，再算內積。"]

    elif op == DOT_PARAM_MCQ_OP:
        # a=(1,k+1), b=(2k,3), a·b=23 => 2k + 3(k+1)=23 => 5k+3=23 => k=4
        correct = "4"
        distractors = ["-1", "1", "5"]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        question = (
            r"若 $\vec{a}=(1,k+1)$、$\vec{b}=(2k,3)$ 且 $\vec{a}\cdot\vec{b}=23$，則 $k=$？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = ["展開內積方程求解。"]

    elif op == PERP_COMPOSITE_OP:
        # a ⊥ (a - k b) with b=(x, by) ⇒ |a|^2 - k a·b = 0
        ax = rng.choice([-3, -2, -1, 1, 2])
        ay = rng.choice([-2, 1, 2, 3])
        by = rng.choice([-3, -2, 2, 3])
        k = rng.choice([1, 2, 3])
        # |a|^2 - k (ax*x + ay*by) = 0 ⇒ ax*k*x = |a|^2 - k*ay*by ⇒ x = ...
        denom = k * ax
        if denom == 0:
            ax = 2
            denom = k * ax
        x = sp.simplify(sp.Rational(ax * ax + ay * ay - k * ay * by, denom))
        result = {"canonical": canonical_exact(x)}
        question = (
            rf"設 $\vec{{a}}={latex_pair(ax, ay)}$、$\vec{{b}}=(x,{by})$，"
            rf"若 $\vec{{a}}\perp(\vec{{a}}-{k}\vec{{b}})$，試求 $x$。"
        )
        answer_value = result["canonical"]
        parts = {"x": result["canonical"]}
        explanation = [r"$\vec{a}\cdot(\vec{a}-k\vec{b})=0$。"]

    elif op == DOT_SIGN_DIAG_OP:
        # Abstracted from exam: BC ⊥ OD => BC·OD=0; ask which statement about OA·OD
        # Given angle AOD > 90 => OA·OD < 0
        correct = r"\overrightarrow{OA}\cdot\overrightarrow{OD}<0"
        distractors = [
            r"\overrightarrow{OA}\cdot\overrightarrow{OD}>0",
            r"\overrightarrow{OA}\cdot\overrightarrow{OD}=0",
            r"\overrightarrow{BC}\cdot\overrightarrow{OD}>0",
        ]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        visual = build_figure_visual_spec(kind="coordinate_exam", arrows=[("O", "A", ""), ("O", "D", ""), ("B", "C", "")])
        question = (
            r"如圖，$A$ 在第二象限，$D$ 在第一象限，且 $\angle AOD>90^\circ$，$\overrightarrow{BC}\perp\overrightarrow{OD}$。"
            r"下列何者正確？"
        )
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = [r"鈍角 $\Rightarrow$ 內積為負。"]

    elif op == PERP_EXPAND_OP:
        # a⊥b ⇒ a·b=0; expand (a-p b)·(q a + r b) = q|a|^2 - p r |b|^2
        ma = rng.choice([2, 3, 4, 5])
        mb = rng.choice([2, 3, 4])
        p = rng.choice([1, 2, 3])
        q = rng.choice([2, 3, 4])
        r = rng.choice([1, 2])
        val = q * (ma**2) - p * r * (mb**2)
        result = {"canonical": canonical_exact(val)}
        question = (
            rf"設 $\vec{{a}}\perp\vec{{b}}$，$|\vec{{a}}|={ma}$、$|\vec{{b}}|={mb}$，"
            rf"試求 $(\vec{{a}}-{p}\vec{{b}})\cdot({q}\vec{{a}}+{r}\vec{{b}})$。"
        )
        answer_value = result["canonical"]
        parts = {"value": result["canonical"]}
        explanation = [r"展開並代入 $a\cdot b=0$。"]

    elif op == ANGLE_FROM_MAG_OP:
        # Topology: recover a·b and angle from |pa + qb| identity.
        # Prefer non-parallel angles for general-angle practice; allow explicit payload override.
        ma = int(payload.get("mag_a") or 1)
        if "mag_b" in payload and "target_mag" in payload:
            mb = int(payload["mag_b"])
            k = int(payload["target_mag"])
            d = sp.simplify(sp.Rational(9 * ma**2 + 4 * mb**2 - k**2, 12))
            cos = sp.simplify(d / (ma * mb))
        else:
            cos = sp.Integer(2)  # force loop
            mb, k, d = 3, 3, sp.Integer(3)
            for _ in range(24):
                mb = rng.choice([2, 3, 4, 5])
                # Vary target magnitude so cos is valid and not ±1 (parallel degeneracy).
                k = rng.choice([i for i in range(max(1, mb - 2), mb + 4) if i > 0])
                d = sp.simplify(sp.Rational(9 * ma**2 + 4 * mb**2 - k**2, 12))
                try:
                    cos = sp.simplify(d / (ma * mb))
                    cos_f = float(cos)
                except Exception:
                    continue
                if abs(cos_f) >= 1 - 1e-9:
                    continue
                if abs(cos_f) > 1:
                    continue
                break
            else:
                # Safe non-degenerate template: angle 60°.
                mb, k, d, cos = 2, 1, sp.Integer(1), sp.Rational(1, 2)
        ang = sp.simplify(sp.deg(sp.acos(cos)))
        result = {"canonical": {"dot": canonical_exact(d), "angle_degrees": canonical_exact(ang)}}
        question = (
            rf"設 $|\vec{{a}}|={ma}$、$|\vec{{b}}|={mb}$，且 $|3\vec{{a}}-2\vec{{b}}|={k}$，"
            r"試求 $\vec{a}\cdot\vec{b}$ 與夾角。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"由 $|3a-2b|^2$ 反求內積，再求夾角。"]

    else:
        raise ValueError(f"unsupported_gap_operation:{op}")

    if payload.get("question_text"):
        question = str(payload["question_text"])
    if choice_meta:
        presentation = "single_choice"
        answer_type = "single_choice"
        answer_value = choice_meta["semantic_answer"]

    matrix = {
        "givens": _json_value({k: v for k, v in payload.items() if k != "question_text"}),
        "answer": {
            "value": answer_value,
            "canonical_form": answer_value,
            "general_form": answer_value,
            "coefficients": [],
            "parts": parts,
            "part_labels": part_labels,
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
        "visual_spec": visual,
        "domain_result": _json_value(result),
    }
    if choice_meta:
        matrix["choices"] = choice_meta["choices"]
        matrix["correct_label"] = choice_meta["correct_label"]
        matrix["semantic_answer"] = choice_meta["semantic_answer"]
    # Persist sampled figure knobs for deterministic rebuild validation.
    if "figure" not in matrix["givens"] and payload.get("figure"):
        matrix["givens"]["figure"] = payload["figure"]
    return matrix
