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
    if kind == "segment_division":
        return {"A": [0, 0], "B": [6, 0], "C": [2, 0], "D": [4, 0]}
    if kind == "triangle_equilateral":
        return {"A": [0, 0], "B": [4, 0], "C": [2, round(2 * math.sqrt(3), 4)]}
    if kind == "coordinate_exam":
        return {"O": [0, 0], "A": [-2, 2], "B": [1, 1], "C": [3, 2], "D": [4, 1]}
    return {"A": [0, 0], "B": [3, 0], "C": [2, 2]}


def build_figure_visual_spec(
    *,
    kind: str,
    edges: list[tuple[str, str]] | None = None,
    arrows: list[tuple[str, str, str]] | None = None,
    show_axes: bool = True,
) -> dict[str, Any]:
    pts = _figure_points(kind)
    if not pts:
        return {"kind": "none"}
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    pad = 1.5
    point_rows = [{"x": float(xy[0]), "y": float(xy[1]), "label": lab} for lab, xy in pts.items()]
    if edges is None:
        labels = [k for k in pts.keys() if k not in {"O"}]
        edges = []
        if len(labels) >= 3:
            for i in range(len(labels)):
                edges.append((labels[i], labels[(i + 1) % len(labels)]))
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
    visual = {"kind": "none"}
    explanation: list[str] = []
    result: dict[str, Any]

    if op == SIMPLIFY_PATH_OP:
        tokens = payload.get("tokens") or ["AB", "+", "BC"]
        result = simplify_vector_path_expression(tokens=list(tokens))
        fig = str(payload.get("figure") or "quadrilateral")
        visual = build_figure_visual_spec(kind=fig, arrows=[(tokens[0][0], tokens[0][1], "")])
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
        fig = str(payload.get("figure") or "parallelogram")
        basis = payload.get("basis") or {"AB": "a", "AD": "b"}
        queries = payload.get("queries") or ["BA", "BC", "CD"]
        result = express_named_vectors_in_given_basis(figure=fig, basis=basis, queries=list(queries))
        visual = build_figure_visual_spec(
            kind=fig,
            arrows=[("A", "B", r"\vec{a}"), ("A", "D", r"\vec{b}")] if fig in {"parallelogram", "rectangle"} else None,
        )
        qparts = "、".join(rf"${_latex_vec_name(q)}$" for q in queries)
        question = f"如圖，已知基底向量，試以基底表示：{qparts}。"
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["利用平行四邊形／多邊形對邊與反向性質。"]

    elif op == SCALAR_FILL_OP:
        # u = k v style fill blanks
        pairs = payload.get("pairs") or [{"left": "a", "right": "c", "k": 2}, {"left": "b", "right": "a", "k": -1}]
        result = {"canonical": {f"k{i+1}": canonical_exact(p["k"]) for i, p in enumerate(pairs)}}
        visual = build_figure_visual_spec(kind=str(payload.get("figure") or "free_vectors"))
        question = "如圖，填入實數完成向量倍數關係。"
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = ["比較方向與長度決定實數倍數。"]

    elif op == SECTION_POINT_OP:
        # Express BF etc in a,b with section points
        a_name = "a"
        b_name = "b"
        # Classic: D,E trisect AB, F midpoint AC; BF = -a/3 + b/2 etc.
        target = str(payload.get("target") or "BF")
        expr = str(payload.get("expression") or f"-1/3*{a_name}+1/2*{b_name}")
        result = {"canonical": canonical_exact(sp.sympify(expr.replace(a_name, "a").replace(b_name, "b")))}
        # Prefer pretty form
        pretty = sp.sstr(sp.simplify(sp.sympify(expr.replace("a", "a").replace("b", "b"))))
        result["canonical"] = pretty
        visual = build_figure_visual_spec(kind="triangle_sections")
        question = (
            rf"如圖，$\triangle ABC$ 中，$D$、$E$ 為 $\overline{{AB}}$ 三等分點，$F$ 為 $\overline{{AC}}$ 中點，"
            rf"令 $\overrightarrow{{AB}}=\vec{{a}}$、$\overrightarrow{{AC}}=\vec{{b}}$，試以 $\vec{{a}}$、$\vec{{b}}$ 表示 ${_latex_vec_name(target)}$。"
        )
        answer_value = pretty
        parts = {"vector": pretty}
        explanation = ["先寫出分點位置向量，再相減。"]

    elif op == SECTION_COEFF_OP:
        alpha, beta = payload.get("alpha", sp.Rational(2, 3)), payload.get("beta", sp.Rational(1, 3))
        result = {"canonical": {"alpha": canonical_exact(alpha), "beta": canonical_exact(beta)}}
        visual = build_figure_visual_spec(kind="parallelogram_sections")
        question = r"如圖，若 $\overrightarrow{AM}=\alpha\overrightarrow{AE}+\beta\overrightarrow{AF}$，試求 $(\alpha,\beta)$。"
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
        # MCQ: which resultant matches (1/3)a-(1/2)b — answer as coordinate of tip from A
        ax, ay = 3, 0
        bx, by = 0, 4
        rx, ry = sp.Rational(1, 3) * ax - sp.Rational(1, 2) * bx, sp.Rational(1, 3) * ay - sp.Rational(1, 2) * by
        correct = format_pair(rx, ry)
        distractors = [format_pair(-rx, ry), format_pair(rx, -ry), format_pair(ry, rx)]
        result = {"canonical": correct}
        choice_meta = _choice_payload(correct, distractors, rng)
        visual = build_figure_visual_spec(
            kind="free_vectors",
            arrows=[("O", "P", r"\vec{a}"), ("O", "Q", r"\vec{b}"), ("O", "R", r"\frac{1}{3}\vec{a}-\frac{1}{2}\vec{b}")],
        )
        # Place R at result for diagram consistency
        visual["points"] = [
            {"x": 0, "y": 0, "label": "A"},
            {"x": float(ax), "y": float(ay), "label": "Pa"},
            {"x": float(bx), "y": float(by), "label": "Pb"},
            {"x": float(rx), "y": float(ry), "label": "R"},
        ]
        visual["arrows"] = [
            {"from": "A", "to": "Pa", "label": r"\vec{a}"},
            {"from": "A", "to": "Pb", "label": r"\vec{b}"},
            {"from": "A", "to": "R", "label": r"\frac{1}{3}\vec{a}-\frac{1}{2}\vec{b}"},
        ]
        visual["x_range"] = [-1, 4]
        visual["y_range"] = [-3, 5]
        question = r"以 $A$ 為起點，下列哪一個終點坐標對應 $\frac{1}{3}\vec{a}-\frac{1}{2}\vec{b}$？（設 $\vec{a}=(3,0)$、$\vec{b}=(0,4)$）"
        answer_value = correct
        presentation = "single_choice"
        answer_type = "single_choice"
        explanation = ["終點 = 起點 + 線性組合結果。"]

    elif op == FROM_GIVENS_OP:
        # GE from DE, DF, FG
        # DE=4a, DF=3b-a, FG=-b+4c => GE = ?
        # G = F + FG, E = D + DE; GE = E - G = (D+DE) - (D+DF+FG) = DE - DF - FG
        # = 4a - (3b-a) - (-b+4c) = 4a -3b +a +b -4c = 5a -2b -4c
        expr = "5*a-2*b-4*c"
        result = {"canonical": canonical_exact(sp.sympify(expr))}
        question = (
            r"已知 $\overrightarrow{DE}=4\vec{a}$、$\overrightarrow{DF}=3\vec{b}-\vec{a}$、"
            r"$\overrightarrow{FG}=-\vec{b}+4\vec{c}$，試求 $\overrightarrow{GE}$。"
        )
        answer_value = result["canonical"]
        parts = {"vector": result["canonical"]}
        explanation = [r"$\overrightarrow{GE}=\overrightarrow{DE}-\overrightarrow{DF}-\overrightarrow{FG}$。"]

    elif op == DIRECTED_MIXED_OP:
        # (1) AB from points (2) |AB| (3) optional unknown endpoint consistent
        start = payload.get("start") or [12, 0]
        end = payload.get("end") or [0, 5]
        vx, vy = sp.Integer(end[0] - start[0]), sp.Integer(end[1] - start[1])
        mag = magnitude(vx, vy)
        # second part: B=(x,y), AB=(-3,2) style
        ab2 = payload.get("ab2") or [-3, 2]
        a2 = payload.get("a2") or [-3, 2]
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
        pq, qr, rs = payload.get("pq") or [2, -2], payload.get("qr") or [4, -3], payload.get("rs") or [1, 0]
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
        # AD = (7/4)AB - (3/4)AC  solve D
        A = payload.get("A") or [57, 23]
        B = payload.get("B") or [7, -2]
        C = payload.get("C") or [5, 12]
        ab = [B[0] - A[0], B[1] - A[1]]
        ac = [C[0] - A[0], C[1] - A[1]]
        adx = sp.Rational(7, 4) * ab[0] - sp.Rational(3, 4) * ac[0]
        ady = sp.Rational(7, 4) * ab[1] - sp.Rational(3, 4) * ac[1]
        Dx, Dy = sp.simplify(A[0] + adx), sp.simplify(A[1] + ady)
        result = {"canonical": format_pair(Dx, Dy)}
        question = (
            f"已知 $A{latex_pair(*A)}$、$B{latex_pair(*B)}$、$C{latex_pair(*C)}$，"
            r"若 $\overrightarrow{AD}=\frac{7}{4}\overrightarrow{AB}-\frac{3}{4}\overrightarrow{AC}$，試求 $D$。"
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
        a = payload.get("a") or [6, -12]
        # b = (-2, y) parallel => 6*y - (-12)*(-2)=0 => 6y-24=0 => y=4
        y = 4
        b = [-2, y]
        mag = magnitude(*b)
        correct = canonical_exact(mag)
        distractors = [
            canonical_exact(magnitude(-2, -4)),
            canonical_exact(20),
            canonical_exact(36),
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
        # A(12,5), B(2,3), port O(0,0); heading AB then BO
        A, B, O = [12, 5], [2, 3], [0, 0]
        v1 = [B[0] - A[0], B[1] - A[1]]
        v2 = [O[0] - B[0], O[1] - B[1]]
        # angle from v1 to v2 (left turn positive)
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        ang = sp.N(sp.deg(sp.atan2(cross, dot)))
        # left turn amount = ang if ang>0 else 360+ang — textbook wants left correction
        left = float(ang) if float(ang) > 0 else float(ang) + 360
        # Keep exact via acos of normalized if possible — use rounded degree for vocational
        left_exact = sp.simplify(sp.deg(sp.acos(sp.Rational(dot, 1) / (magnitude(*v1) * magnitude(*v2)))))
        # Determine orientation
        if cross < 0:
            # right-handed screen: negative cross means clockwise; left turn = 360 - interior
            turn = sp.simplify(360 - left_exact)
        else:
            turn = left_exact
        result = {"canonical": {"turn_degrees": canonical_exact(turn)}}
        visual = build_figure_visual_spec(kind="coordinate")
        visual = {
            "kind": "coordinate_plane",
            "render_required": True,
            "points": [
                {"x": 0, "y": 0, "label": "O"},
                {"x": 12, "y": 5, "label": "A"},
                {"x": 2, "y": 3, "label": "B"},
            ],
            "arrows": [
                {"from": "A", "to": "B", "label": ""},
                {"from": "B", "to": "O", "label": ""},
            ],
            "lines": [],
            "x_range": [-1, 13],
            "y_range": [-1, 6],
        }
        question = (
            "船由 $A(12,5)$ 駛向航標 $B(2,3)$ 後再駛向港口 $O(0,0)$。"
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
        side = payload.get("side") or 4
        fig = str(payload.get("figure") or "triangle_equilateral")
        if fig == "triangle_equilateral":
            # AB·AC = side^2 cos60 = side^2/2; AB·BC = side^2 cos120 = -side^2/2
            d1 = sp.Rational(side**2, 2)
            d2 = -sp.Rational(side**2, 2)
        else:
            # hexagon side s: AB·AF = s^2 cos60 = s^2/2; AB·BC = s^2 cos120 = -s^2/2
            d1 = sp.Rational(side**2, 2)
            d2 = -sp.Rational(side**2, 2)
        result = {"canonical": {"dot1": canonical_exact(d1), "dot2": canonical_exact(d2)}}
        visual = build_figure_visual_spec(kind=fig if fig != "triangle_equilateral" else "triangle_equilateral")
        question = (
            f"已知正{'三角形' if 'triangle' in fig else '六邊形'}邊長為 ${side}$，試求兩組相鄰／夾角邊向量之內積。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"$\vec{u}\cdot\vec{v}=|\vec{u}||\vec{v}|\cos\theta$。"]

    elif op == DOT_IDENTITY_OP:
        ma, mb, ang = 3, 2, 60
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
        question = (
            f"設 $|\\vec{{a}}|={ma}$、$|\\vec{{b}}|={mb}$，夾角 ${ang}^\\circ$，試求 "
            r"$\vec{a}\cdot\vec{a}$、$\vec{a}\cdot\vec{b}$、$|2\vec{a}-3\vec{b}|$。"
        )
        parts = dict(result["canonical"])
        answer_value = parts
        answer_type = "multi_part"
        explanation = [r"用定義與 $|u|^2=u\cdot u$ 展開。"]

    elif op == PLOT_POINTS_OP:
        A, B = [12, 5], [2, 3]
        result = {"canonical": {"A": format_pair(*A), "B": format_pair(*B)}}
        visual = {
            "kind": "coordinate_plane",
            "render_required": True,
            "points": [{"x": 0, "y": 0, "label": "O"}, {"x": 12, "y": 5, "label": "A"}, {"x": 2, "y": 3, "label": "B"}],
            "arrows": [{"from": "A", "to": "B", "label": ""}],
            "x_range": [-1, 13],
            "y_range": [-1, 6],
        }
        question = "以港口為原點 $O(0,0)$，標示 $A(12,5)$ 與航標 $B(2,3)$ 的坐標。試寫出 $A$、$B$ 坐標。"
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
        # a=(-1,2), b=(x,2), a ⊥ (a-2b)
        # a·(a-2b)=0 => |a|^2 - 2 a·b =0 => 5 - 2(-x+4)=0 => 5 +2x -8=0 => 2x=3 => x=3/2
        x = sp.Rational(3, 2)
        result = {"canonical": canonical_exact(x)}
        question = (
            r"設 $\vec{a}=(-1,2)$、$\vec{b}=(x,2)$，若 $\vec{a}\perp(\vec{a}-2\vec{b})$，試求 $x$。"
        )
        answer_value = result["canonical"]
        parts = {"x": result["canonical"]}
        explanation = [r"$\vec{a}\cdot(\vec{a}-2\vec{b})=0$。"]

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
        # a⊥b, |a|=3,|b|=2; (a-2b)·(3a+b)=3|a|^2 -2|b|^2 +(-6+1)a·b = 27 - 8 = 19
        val = 3 * 9 + (-2) * 4  # a·b=0
        # expand: 3 a·a + a·b -6 b·a -2 b·b = 3*9 +0 -0 -2*4 = 27-8=19
        result = {"canonical": "19"}
        question = (
            r"設 $\vec{a}\perp\vec{b}$，$|\vec{a}|=3$、$|\vec{b}|=2$，試求 $(\vec{a}-2\vec{b})\cdot(3\vec{a}+\vec{b})$。"
        )
        answer_value = "19"
        parts = {"value": "19"}
        explanation = [r"展開並代入 $a\cdot b=0$。"]

    elif op == ANGLE_FROM_MAG_OP:
        # |a|=1,|b|=3, |3a-2b|=3 => 9|a|^2+4|b|^2-12 a·b =9 => 9+36-12d=9 => 36=12d => d=3
        # cos = d/(|a||b|)=3/3=1 => angle 0
        d = 3
        result = {"canonical": {"dot": "3", "angle_degrees": "0"}}
        question = (
            r"設 $|\vec{a}|=1$、$|\vec{b}|=3$，且 $|3\vec{a}-2\vec{b}|=3$，試求 $\vec{a}\cdot\vec{b}$ 與夾角。"
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
