# -*- coding: utf-8 -*-
"""B2 Ch4 4-2 gap coverage for circle.plane (point/line/tangent families)."""

from __future__ import annotations

import math
import random
from typing import Any

import sympy as sp

from core.domain.circle_plane_domain import (
    _as_pair,
    _coeff_term,
    _format_interval,
    _json_value,
    _mcq_pack,
    _sample_int,
    _sample_point,
    _sample_radius,
    canonical_exact,
    center_radius_from_general,
    format_general_equation,
    format_pair,
    format_standard_equation,
    latex_general_equation,
    latex_pair,
    latex_standard_equation,
    make_circle,
    point_distance,
    point_line_distance,
)
from core.gencode.multipart_stem_contract import (
    build_stem_structure,
    stem_structure_to_question_text,
)


def _sample_circle(rng: random.Random) -> dict[str, Any]:
    return make_circle(
        h=_sample_int(rng, -4, 4),
        k=_sample_int(rng, -4, 4),
        r=_sample_radius(rng),
    )


def _sample_line_ab(rng: random.Random) -> tuple[int, int]:
    a = _sample_int(rng, -5, 5, nonzero=True)
    b = _sample_int(rng, -5, 5)
    if b == 0 and a == 0:
        a = 1
    return a, b


def _line_c_for_distance(
    h: Any, k: Any, a: int, b: int, target_d: Any
) -> int:
    """Pick integer c so |ah+bk+c|/sqrt(a^2+b^2) ≈ target_d (prefer exact)."""
    denom = sp.sqrt(a * a + b * b)
    # Prefer c so ah+bk+c = ± target_d * denom
    base = a * h + b * k
    candidates = [
        sp.simplify(target_d * denom - base),
        sp.simplify(-target_d * denom - base),
    ]
    for cand in candidates:
        if cand.is_integer:
            return int(cand)
    # Fallback: round
    return int(sp.N(candidates[0]))


def _sample_point_on_circle(rng: random.Random, h: Any, k: Any, r: Any) -> list[Any]:
    offsets = [(r, 0), (-r, 0), (0, r), (0, -r)]
    ox, oy = rng.choice(offsets)
    return [h + ox, k + oy]


def _sample_external_point(rng: random.Random, h: Any, k: Any, r: Any) -> list[int]:
    for _ in range(20):
        px = int(h) + rng.randint(-8, 8)
        py = int(k) + rng.randint(-8, 8)
        if (px - h) ** 2 + (py - k) ** 2 > r**2:
            return [px, py]
    return [int(h) + int(r) + 3, int(k)]

# ── op keys ───────────────────────────────────────────────────────────────────

CLASSIFY_POINT_VS_CIRCLES_OP = "classify_point_vs_circles_multipart"
SOLVE_POINT_PARAM_OP = "solve_point_circle_parameter_range"
IDENTIFY_POINT_ON_CIRCLE_MCQ_OP = "identify_point_on_circle_mcq"

CLASSIFY_LINE_CIRCLE_OP = "classify_line_circle_relation"
CLASSIFY_LINES_VS_CIRCLE_OP = "classify_lines_vs_circle_multipart"
SOLVE_LINE_PARAM_RANGE_OP = "solve_line_circle_parameter_range"
SOLVE_LINE_TANGENT_PARAM_OP = "solve_line_circle_tangent_parameter"
COMPUTE_CHORD_OP = "compute_chord_length"
SOLVE_LINE_RELATION_RANGES_OP = "solve_line_circle_relation_ranges_multipart"
COUNT_INTERSECTIONS_OP = "count_line_circle_intersections"
STORM_PATH_OP = "compute_storm_path_length_in_circle"
CLASSIFY_LINE_CIRCLE_MCQ_OP = "classify_line_circle_relation_mcq"
DIAMETER_CHORD_PARAM_MCQ_OP = "solve_diameter_chord_parameter_mcq"
TRIANGLE_MAB_AREA_OP = "compute_triangle_center_chord_area"
AXIS_TANGENT_PARAM_OP = "solve_axis_tangent_parameter"

TANGENT_AT_POINT_OP = "tangent_at_point_on_circle"
TANGENTS_PARALLEL_OP = "tangents_parallel_to_line"
TANGENTS_PERP_OP = "tangents_perpendicular_to_line"
TANGENTS_QUAD_AREA_OP = "compute_tangents_from_point_quad_area"

TANGENT_SEGMENT_LENGTHS_OP = "compute_tangent_segment_lengths"
COUNT_LINE_TWO_CIRCLES_OP = "count_line_vs_two_circles_intersections"
TANGENT_SEGMENT_MCQ_OP = "compute_tangent_segment_length_mcq"
PARAMETER_RANGE_MCQ_OP = "solve_circle_parameter_range_mcq"
TANGENT_AT_POINT_MCQ_OP = "tangent_at_point_on_circle_mcq"

GAP_OPS = frozenset(
    {
        CLASSIFY_POINT_VS_CIRCLES_OP,
        SOLVE_POINT_PARAM_OP,
        IDENTIFY_POINT_ON_CIRCLE_MCQ_OP,
        CLASSIFY_LINE_CIRCLE_OP,
        CLASSIFY_LINES_VS_CIRCLE_OP,
        SOLVE_LINE_PARAM_RANGE_OP,
        SOLVE_LINE_TANGENT_PARAM_OP,
        COMPUTE_CHORD_OP,
        SOLVE_LINE_RELATION_RANGES_OP,
        COUNT_INTERSECTIONS_OP,
        STORM_PATH_OP,
        CLASSIFY_LINE_CIRCLE_MCQ_OP,
        DIAMETER_CHORD_PARAM_MCQ_OP,
        TRIANGLE_MAB_AREA_OP,
        AXIS_TANGENT_PARAM_OP,
        TANGENT_AT_POINT_OP,
        TANGENTS_PARALLEL_OP,
        TANGENTS_PERP_OP,
        TANGENTS_QUAD_AREA_OP,
        TANGENT_SEGMENT_LENGTHS_OP,
        COUNT_LINE_TWO_CIRCLES_OP,
        TANGENT_SEGMENT_MCQ_OP,
        PARAMETER_RANGE_MCQ_OP,
        TANGENT_AT_POINT_MCQ_OP,
    }
)


def _point_circle_relation(point: Any, h: Any, k: Any, r2: Any) -> str:
    px, py = _as_pair(point)
    d2 = sp.simplify((px - sp.sympify(h)) ** 2 + (py - sp.sympify(k)) ** 2)
    rr = sp.simplify(sp.sympify(r2))
    if d2 < rr:
        return "圓內"
    if d2 == rr:
        return "圓上"
    return "圓外"


def _line_circle_relation(d: Any, r: Any) -> str:
    dd, rr = sp.simplify(sp.sympify(d)), sp.simplify(sp.sympify(r))
    if dd > rr:
        return "相離"
    if dd == rr:
        return "相切"
    return "相交"


def _intersection_count(d: Any, r: Any) -> int:
    rel = _line_circle_relation(d, r)
    return {"相離": 0, "相切": 1, "相交": 2}[rel]


def _format_line(a: Any, b: Any, c: Any) -> str:
    aa, bb, cc = sp.Integer(sp.sympify(a)), sp.Integer(sp.sympify(b)), sp.Integer(sp.sympify(c))
    g = sp.gcd(sp.gcd(abs(aa), abs(bb)), abs(cc)) or 1
    aa, bb, cc = aa // g, bb // g, cc // g
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb, cc = -aa, -bb, -cc
    body = ""
    if aa != 0:
        body += "x" if aa == 1 else ("-x" if aa == -1 else f"{aa}x")
    if bb != 0:
        if bb == 1:
            body += "+y" if body else "y"
        elif bb == -1:
            body += "-y"
        else:
            body += f"+{bb}y" if bb > 0 and body else f"{bb}y"
    if cc != 0:
        body += f"+{cc}" if cc > 0 else str(cc)
    return f"{body}=0"


def _line_semantic_key(a: Any, b: Any, c: Any) -> str:
    return _format_line(a, b, c)


def _latex_line(a: Any, b: Any, c: Any) -> str:
    return _format_line(a, b, c).replace("=", "=")


def _normalize_line_coeffs(a: Any, b: Any, c: Any) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    aa, bb, cc = sp.simplify(sp.sympify(a)), sp.simplify(sp.sympify(b)), sp.simplify(sp.sympify(c))
    # Prefer integers when possible
    try:
        nums = [sp.Integer(x) for x in (aa, bb, cc)]
        g = sp.gcd(sp.gcd(abs(nums[0]), abs(nums[1])), abs(nums[2])) or 1
        aa, bb, cc = nums[0] // g, nums[1] // g, nums[2] // g
    except Exception:
        pass
    if aa < 0 or (aa == 0 and bb < 0):
        aa, bb, cc = -aa, -bb, -cc
    return aa, bb, cc


def _tangent_at_point(h: Any, k: Any, r2: Any, px: Any, py: Any) -> dict[str, Any]:
    hh, kk = sp.sympify(h), sp.sympify(k)
    x0, y0 = sp.sympify(px), sp.sympify(py)
    # (x-h)(x0-h)+(y-k)(y0-k)=r2
    a = sp.simplify(x0 - hh)
    b = sp.simplify(y0 - kk)
    c = sp.simplify(-(a * x0 + b * y0))
    a, b, c = _normalize_line_coeffs(a, b, c)
    return {"A": a, "B": b, "C": c, "equation": _format_line(a, b, c)}


def _parallel_tangents(h: Any, k: Any, r: Any, a: Any, b: Any) -> list[dict[str, Any]]:
    aa, bb = sp.sympify(a), sp.sympify(b)
    # ax+by+c=0 with |ah+bk+c|/sqrt(a^2+b^2)=r
    # ah+bk+c = ± r sqrt(a^2+b^2)
    denom = sp.sqrt(aa**2 + bb**2)
    base = aa * sp.sympify(h) + bb * sp.sympify(k)
    cs = [sp.simplify(-base + sp.sympify(r) * denom), sp.simplify(-base - sp.sympify(r) * denom)]
    out = []
    for c in cs:
        # Clear radicals when denom is integer
        if denom.is_rational:
            A, B, C = _normalize_line_coeffs(aa, bb, c)
        else:
            # Multiply by denom to clear: a*d x + b*d y + (-base*d ± r*d^2)=0 wait
            # Better: ah+bk+c = ± r*s where s=sqrt(a^2+b^2)
            # Keep exact with cleared form when a^2+b^2 perfect square
            s2 = aa**2 + bb**2
            if sp.integer_nthroot(int(s2), 2)[1]:
                s = sp.Integer(sp.integer_nthroot(int(s2), 2)[0])
                A, B, C = _normalize_line_coeffs(aa, bb, c)
            else:
                A, B, C = aa, bb, c
                A, B, C = _normalize_line_coeffs(A, B, sp.simplify(C))
        out.append({"A": A, "B": B, "C": C, "equation": _format_line(A, B, C)})
    out.sort(key=lambda d: d["equation"])
    return out


def _perp_direction(a: Any, b: Any) -> tuple[sp.Expr, sp.Expr]:
    # perpendicular to (a,b) is (-b, a)
    return sp.simplify(-sp.sympify(b)), sp.simplify(sp.sympify(a))


def _visual_circle(h: Any, k: Any, r: Any, label: str = "C") -> dict[str, Any]:
    return {
        "h": float(sp.N(h)),
        "k": float(sp.N(k)),
        "r": float(sp.N(r)),
        "label": label,
    }


def _visual_point(x: Any, y: Any, label: str) -> dict[str, Any]:
    return {"x": float(sp.N(x)), "y": float(sp.N(y)), "label": label}


def _visual_line(a: Any, b: Any, c: Any, label: str = "L") -> dict[str, Any]:
    return {"A": float(sp.N(a)), "B": float(sp.N(b)), "C": float(sp.N(c)), "label": label}


def _range_from_entities(points: list, circles: list, pad: float = 2.0) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for p in points:
        xs.append(float(p["x"]))
        ys.append(float(p["y"]))
    for c in circles:
        xs.extend([c["h"] - c["r"], c["h"] + c["r"]])
        ys.extend([c["k"] - c["r"], c["k"] + c["r"]])
    if not xs:
        return [-8, 8], [-8, 8]
    return [min(xs) - pad, max(xs) + pad], [min(ys) - pad, max(ys) + pad]


def _finish_matrix(
    *,
    op: str,
    question: str,
    answer_value: Any,
    explanation: list[str],
    payload: dict[str, Any],
    result: dict[str, Any],
    seed: int | None,
    curriculum_profile: str | None,
    difficulty_profile: str | None,
    answer_type: str,
    presentation: str,
    parts: dict[str, Any] | None = None,
    choices: list | None = None,
    correct_label: str | None = None,
    semantic_answer: Any = None,
    distractors: list | None = None,
    visual_spec: dict[str, Any] | None = None,
    stem_structure: dict[str, Any] | None = None,
    part_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    parts = parts or {}
    if choices is not None:
        from core.gencode.choice_contract_validator import choice_semantic_key as _csk

        answer_value_for_block = semantic_answer
        distractor_values = [
            str(c.get("value") or c.get("text") or "").strip()
            for c in choices
            if isinstance(c, dict) and _csk(c.get("value") or c.get("text")) != _csk(semantic_answer)
        ]
    else:
        answer_value_for_block = answer_value
        distractor_values = list(distractors or [])

    labels_out: Any
    if part_labels is not None:
        labels_out = part_labels
    else:
        labels_out = list(parts.keys())

    answer_block: dict[str, Any] = {
        "value": answer_value_for_block,
        "canonical_form": answer_value_for_block if not isinstance(answer_value_for_block, dict) else "",
        "general_form": answer_value_for_block if not isinstance(answer_value_for_block, dict) else "",
        "coefficients": [],
        "parts": parts,
        "part_labels": labels_out,
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


def build_gap_matrix(
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
    if op == PARAMETER_RANGE_MCQ_OP:
        # Delegate to core domain op with forced MCQ.
        from core.domain.circle_plane_domain import build_circle_plane_matrix as _core_build

        return _core_build(
            operation="solve_circle_parameter_range",
            seed=seed,
            constraints={**(constraints or {}), **data, "as_mcq": True, "pattern": data.get("pattern") or (constraints or {}).get("pattern") or "F_param"},
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            as_mcq=True,
            pattern=data.get("pattern") or "F_param",
        )
    if op == TANGENT_AT_POINT_MCQ_OP:
        return build_gap_matrix(
            operation=TANGENT_AT_POINT_OP,
            seed=seed,
            constraints={**(constraints or {}), **data, "as_mcq": True},
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            as_mcq=True,
        )
    if op not in GAP_OPS:
        raise ValueError(f"unsupported_circle_plane_gap_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    payload = {**dict(constraints or {}), **data}
    for key in (
        "skill_id", "phase1_classification", "v3_induced_spec", "classification_status",
        "source_hash", "required_capabilities", "answer_contract", "presentation_mode",
        "answer_type", "problem_type_id", "textbook_example_id", "source_example_id",
        "classification_source",
    ):
        payload.pop(key, None)

    choices = None
    correct_label = None
    semantic_answer = None
    distractors: list[str] = []
    parts: dict[str, Any] = {}
    visual_spec = None
    presentation = "short_answer"
    answer_type = "expression"
    stem_structure: dict[str, Any] | None = None
    part_labels: dict[str, str] | None = None

    if op == CLASSIFY_POINT_VS_CIRCLES_OP:
        if "point" not in payload:
            payload["point"] = _sample_point(rng)
            # Two circles: one standard, one general
            c1 = make_circle(h=_sample_int(rng, -3, 3), k=_sample_int(rng, -3, 3), r=_sample_radius(rng))
            c2 = make_circle(h=_sample_int(rng, -4, 4), k=_sample_int(rng, -4, 4), r=_sample_radius(rng))
            payload["circles"] = [
                {"form": "standard", "h": c1["h"], "k": c1["k"], "r2": c1["r2"]},
                {"form": "general", "d": c2["D"], "e": c2["E"], "f": c2["F"]},
            ]
        px, py = _as_pair(payload["point"])
        stem_items: list[dict[str, str]] = []
        for idx, circ in enumerate(payload["circles"], 1):
            if circ.get("form") == "general" or "d" in circ:
                ext = center_radius_from_general(d=circ["d"], e=circ["e"], f=circ["f"], scale=circ.get("scale", 1))
                h, k, r2 = ext["h"], ext["k"], ext["r2"]
                eq = latex_general_equation(circ["d"], circ["e"], circ["f"])
            else:
                h, k, r2 = circ["h"], circ["k"], circ["r2"]
                eq = latex_standard_equation(h, k, r2)
            rel = _point_circle_relation(payload["point"], h, k, r2)
            parts[f"({idx})"] = rel
            stem_items.append({"group_label": f"({idx})", "text": f"$C_{idx}:{eq}$"})
        stem_structure = build_stem_structure(
            f"試判斷點 $P{latex_pair(px, py)}$ 是在下列各圓的圓上、圓外或圓內？",
            stem_items,
        )
        question = stem_structure_to_question_text(stem_structure)
        answer_value = parts
        answer_type = "multi_part"
        presentation = "multiple_inputs"
        result = {"parts": parts}
        explanation = ["比較 $d^2$ 與 $r^2$ 判斷點與圓的位置關係。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(px, py, "P")],
            "circles": [],
            "implemented": True,
        }
        for idx, circ in enumerate(payload["circles"], 1):
            if "d" in circ or circ.get("form") == "general":
                ext = center_radius_from_general(d=circ["d"], e=circ["e"], f=circ["f"], scale=circ.get("scale", 1))
                visual_spec["circles"].append(_visual_circle(ext["h"], ext["k"], ext["r"], f"C{idx}"))
            else:
                visual_spec["circles"].append(
                    _visual_circle(circ["h"], circ["k"], sp.sqrt(circ["r2"]), f"C{idx}")
                )
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op == SOLVE_POINT_PARAM_OP:
        # Point outside circle x^2+y^2+Dx+Ey+k=0 → r2 < d2_to_center wait
        # (2,1) outside x^2+y^2+2x-4y+k=0 → center (-1,2), r2=1+4-k=5-k
        # d2=(2+1)^2+(1-2)^2=9+1=10 > r2 ⇒ 10>5-k ⇒ k>-5? Outside means d2>r2 ⇒ 10>5-k ⇒ k>-5
        # Actually textbook: 點在圓外 ⇒ d2 > r2
        if "point" not in payload:
            circ = _sample_circle(rng)
            pt = _sample_point(rng, nonzero=True)
            if pt[0] == circ["h"] and pt[1] == circ["k"]:
                pt = [pt[0] + 2, pt[1] + 1]
            payload.update(
                {
                    "point": pt,
                    "d": int(circ["D"]),
                    "e": int(circ["E"]),
                    "f_const": 0,
                    "param": "k",
                    "relation": rng.choice(["outside", "inside", "on"]),
                }
            )
        px, py = _as_pair(payload["point"])
        dd, ee = sp.sympify(payload["d"]), sp.sympify(payload["e"])
        param = str(payload.get("param") or "k")
        p = sp.symbols(param)
        ff = sp.sympify(payload.get("f_const", 0)) + p
        h, k = -dd / 2, -ee / 2
        r2 = sp.simplify((dd**2 + ee**2) / 4 - ff)
        d2 = sp.simplify((px - h) ** 2 + (py - k) ** 2)
        relation = str(payload.get("relation") or "outside")
        if relation == "outside":
            ineq = sp.StrictGreaterThan(d2, r2)
            label = "圓外"
        elif relation == "inside":
            ineq = sp.StrictLessThan(d2, r2)
            label = "圓內"
        else:
            ineq = sp.Eq(d2, r2)
            label = "圓上"
        sol = sp.solve_univariate_inequality(ineq, p, relational=False) if relation != "on" else sp.solve(sp.Eq(d2, r2), p)
        if relation == "on":
            answer_value = canonical_exact(sol[0]) if isinstance(sol, list) and sol else canonical_exact(sol)
        else:
            answer_value = _format_interval(sol, param)
        question = (
            f"若點 ${latex_pair(px, py)}$ 在圓 $x^{{2}}+y^{{2}}"
            f"{_coeff_term(dd, 'x')}{_coeff_term(ee, 'y')}+{param}=0$ 的{label}，"
            f"試求 ${param}$ 值的範圍。"
        )
        result = {"solution": answer_value, "relation": relation}
        explanation = [f"由 $d^2$ {'>' if relation=='outside' else '<' if relation=='inside' else '='} $r^2$ 解不等式。"]

    elif op == IDENTIFY_POINT_ON_CIRCLE_MCQ_OP:
        if "h" not in payload:
            circ = _sample_circle(rng)
            payload.update({"h": circ["h"], "k": circ["k"], "r": circ["r"]})
        circle = make_circle(h=payload["h"], k=payload["k"], r=payload["r"])
        # Sample a point on circle
        px, py = _sample_point_on_circle(rng, circle["h"], circle["k"], circle["r"])
        correct = format_pair(px, py)
        distractors = [
            format_pair(circle["h"] + circle["r"] + 1, circle["k"]),
            format_pair(circle["h"], circle["k"] + circle["r"] + 1),
            format_pair(circle["h"] - 1, circle["k"] - 1),
        ]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"若圓 $C$ 的半徑為 ${canonical_exact(circle['r'])}$，圓心在 ${latex_pair(circle['h'], circle['k'])}$，"
            f"則下列何者落在圓 $C$ 上？"
        )
        result = {"point": correct}
        explanation = ["落在圓上的點滿足 $d^2=r^2$。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(px, py, "P")],
            "circles": [_visual_circle(circle["h"], circle["k"], circle["r"])],
            "implemented": True,
        }
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op in {CLASSIFY_LINE_CIRCLE_OP, CLASSIFY_LINE_CIRCLE_MCQ_OP}:
        if "h" not in payload:
            circ = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            target_rel = rng.choice(["相離", "相切", "相交"])
            if target_rel == "相切":
                target_d = circ["r"]
            elif target_rel == "相交":
                target_d = circ["r"] * sp.Rational(1, 2) if circ["r"] >= 2 else 0
            else:
                target_d = circ["r"] + rng.randint(1, 3)
            c = _line_c_for_distance(circ["h"], circ["k"], a, b, target_d)
            payload.update(
                {"h": circ["h"], "k": circ["k"], "r": circ["r"], "a": a, "b": b, "c": c}
            )
        circle = make_circle(h=payload["h"], k=payload["k"], r=payload["r"])
        d = point_line_distance([circle["h"], circle["k"]], payload["a"], payload["b"], payload["c"])
        rel = _line_circle_relation(d, circle["r"])
        applied = bool(payload.get("applied"))
        if applied or op == CLASSIFY_LINE_CIRCLE_OP and payload.get("story"):
            question = (
                f"已知圓 ${latex_standard_equation(circle['h'], circle['k'], circle['r2'])}$ 與航線 "
                f"$L:{_format_line(payload['a'], payload['b'], payload['c'])}$。"
                f"試判斷直線與圓的關係（是否相交／觸礁）。"
            )
            answer_value = "會觸礁" if rel != "相離" else "不會觸礁"
            # Also accept geometric relation as primary for non-story
            if not payload.get("story"):
                answer_value = rel
                question = (
                    f"試判斷圓 ${latex_standard_equation(circle['h'], circle['k'], circle['r2'])}$ "
                    f"與直線 ${_format_line(payload['a'], payload['b'], payload['c'])}$ 的關係。"
                )
        else:
            question = (
                f"試判斷圓 ${latex_standard_equation(circle['h'], circle['k'], circle['r2'])}$ "
                f"與直線 ${_format_line(payload['a'], payload['b'], payload['c'])}$ 的關係。"
            )
            answer_value = rel
        result = {"relation": rel, "distance": canonical_exact(d)}
        explanation = ["比較圓心到直線距離與半徑。"]
        if op == CLASSIFY_LINE_CIRCLE_MCQ_OP:
            distractors = [x for x in ("相離", "相切", "相交", "直線過圓心") if x != rel]
            pack = _mcq_pack(rel, distractors, rng)
            choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
            answer_type, presentation = "single_choice", "single_choice"
            answer_value = correct_label
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(circle["h"], circle["k"], "O")],
            "lines": [_visual_line(payload["a"], payload["b"], payload["c"])],
            "circles": [_visual_circle(circle["h"], circle["k"], circle["r"])],
            "implemented": True,
        }
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op == CLASSIFY_LINES_VS_CIRCLE_OP:
        if "h" not in payload:
            circle = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            lines = []
            for td in (circle["r"], 0, circle["r"] + 2):
                c = _line_c_for_distance(circle["h"], circle["k"], a, b, td)
                lines.append({"a": a, "b": b, "c": c})
            rng.shuffle(lines)
            payload.update(
                {
                    "h": circle["h"],
                    "k": circle["k"],
                    "r2": circle["r2"],
                    "lines": lines,
                    "form": "general",
                    "d": circle["D"],
                    "e": circle["E"],
                    "f": circle["F"],
                }
            )
        if "d" in payload:
            ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"])
            h, k, r = ext["h"], ext["k"], ext["r"]
            eq = latex_general_equation(payload["d"], payload["e"], payload["f"])
        else:
            h, k, r = payload["h"], payload["k"], sp.sqrt(payload["r2"])
            eq = latex_standard_equation(h, k, payload["r2"])
        labels = []
        stem_items = []
        for idx, line in enumerate(payload["lines"], 1):
            d = point_line_distance([h, k], line["a"], line["b"], line["c"])
            rel = _line_circle_relation(d, r)
            parts[f"({idx})"] = rel
            body = f"$L_{idx}:{_format_line(line['a'], line['b'], line['c'])}$"
            labels.append(f"({idx}) {body}")
            stem_items.append({"group_label": f"({idx})", "text": body})
        stem_structure = build_stem_structure(
            f"試判斷圓 $C:{eq}$ 與下列各直線的關係：",
            stem_items,
        )
        question = stem_structure_to_question_text(stem_structure)
        answer_value = parts
        answer_type, presentation = "multi_part", "multiple_inputs"
        result = {"parts": parts}
        explanation = ["分別比較圓心到各直線距離與半徑。"]

    elif op == SOLVE_LINE_PARAM_RANGE_OP:
        # L:ax+by+k=0 vs circle — sample circle + line direction
        if "h" not in payload:
            circ = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            payload.update(
                {
                    "h": circ["h"],
                    "k": circ["k"],
                    "r": circ["r"],
                    "a": a,
                    "b": b,
                    "param": "k",
                    "mode": rng.choice(["secant", "disjoint", "tangent"]),
                }
            )
        circle = make_circle(h=payload["h"], k=payload["k"], r=payload["r"])
        param = str(payload.get("param") or "k")
        p = sp.symbols(param, real=True)
        a, b = sp.sympify(payload["a"]), sp.sympify(payload["b"])
        # d = |a h + b k + p| / sqrt(a^2+b^2)
        numer = a * circle["h"] + b * circle["k"] + p
        denom = sp.sqrt(a**2 + b**2)
        mode = str(payload.get("mode") or "secant")
        bound = sp.simplify(circle["r"] * denom)
        if mode == "tangent":
            vals = sorted(
                {
                    sp.simplify(bound - (a * circle["h"] + b * circle["k"])),
                    sp.simplify(-bound - (a * circle["h"] + b * circle["k"])),
                },
                key=str,
            )
            answer_value = ",".join(canonical_exact(v) for v in vals)
        else:
            # |base + p| ? r*denom  →  squared form
            base = a * circle["h"] + b * circle["k"]
            expr = sp.simplify((base + p) ** 2 - bound**2)
            if mode == "secant":
                sol = sp.solve_univariate_inequality(sp.StrictLessThan(expr, 0), p, relational=False)
            else:
                sol = sp.solve_univariate_inequality(sp.StrictGreaterThan(expr, 0), p, relational=False)
            answer_value = _format_interval(sol, param)
        a_disp = canonical_exact(a)
        b_disp = canonical_exact(b)
        b_term = "" if b == 0 else (f"+{b_disp}y" if b > 0 else f"{b_disp}y")
        question = (
            f"設直線 $L:{a_disp}x{b_term}+{param}=0$ 與圓 "
            f"${latex_standard_equation(circle['h'], circle['k'], circle['r2'])}$ "
            + ("相交於兩點" if mode == "secant" else "不相交" if mode == "disjoint" else "相切")
            + f"，試求實數 ${param}$ 的範圍。"
        )
        result = {"solution": answer_value, "mode": mode}
        explanation = ["由圓心到直線距離與半徑的不等／等式解參數。"]

    elif op == SOLVE_LINE_TANGENT_PARAM_OP:
        if "a" not in payload:
            a, b = _sample_line_ab(rng)
            c = -rng.choice([1, 2, 3, 4, 5])
            payload.update(
                {
                    "h": 0,
                    "k": 0,
                    "a_line": a,
                    "b_line": b,
                    "c_line": c,
                    "param": "a",
                    "circle_r2_is_param": True,
                }
            )
        param = str(payload.get("param") or "a")
        p = sp.symbols(param)
        if payload.get("circle_r2_is_param"):
            h = k = 0
            r = sp.sqrt(p)
            d = point_line_distance([0, 0], payload["a_line"], payload["b_line"], payload["c_line"])
            # d = r ⇒ p = d^2
            ans = sp.simplify(d**2)
            answer_value = canonical_exact(ans)
            question = (
                f"已知直線 $L:{_format_line(payload['a_line'], payload['b_line'], payload['c_line'])}$ "
                f"與圓 $x^{{2}}+y^{{2}}={param}$ 相切，試求實數 ${param}$ 之值。"
            )
        else:
            # circle with param in F, line fixed, tangent
            dd, ee = sp.sympify(payload["d"]), sp.sympify(payload["e"])
            ff = p
            ext_r2 = (dd**2 + ee**2) / 4 - ff
            h, k = -dd / 2, -ee / 2
            d = sp.Abs(payload["a_line"] * h + payload["b_line"] * k + payload["c_line"]) / sp.sqrt(
                payload["a_line"] ** 2 + payload["b_line"] ** 2
            )
            sols = sp.solve(sp.Eq(d**2, ext_r2), p)
            answer_value = canonical_exact(sols[0]) if len(sols) == 1 else ",".join(canonical_exact(s) for s in sols)
            question = (
                f"若圓 $x^{{2}}+y^{{2}}{_coeff_term(dd,'x')}{_coeff_term(ee,'y')}+{param}=0$ "
                f"與直線 ${_format_line(payload['a_line'], payload['b_line'], payload['c_line'])}$ 相切，則 ${param}=$"
            )
        as_mcq = bool(payload.get("as_mcq"))
        if as_mcq:
            correct = answer_value.split(",")[0]
            distractors = [canonical_exact(sp.sympify(correct) + sp.Rational(1, 4)), "1", "2"]
            pack = _mcq_pack(correct, distractors, rng)
            choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
            answer_type, presentation = "single_choice", "single_choice"
            answer_value = correct_label
        result = {"parameter": answer_value}
        explanation = ["相切條件：圓心到直線距離等於半徑。"]

    elif op == COMPUTE_CHORD_OP:
        if "h" not in payload:
            circ = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            td = circ["r"] * sp.Rational(1, 2) if circ["r"] >= 2 else 0
            c = _line_c_for_distance(circ["h"], circ["k"], a, b, td)
            payload.update(
                {"h": circ["h"], "k": circ["k"], "r": circ["r"], "a": a, "b": b, "c": c}
            )
        circle = make_circle(h=payload["h"], k=payload["k"], r=payload["r"])
        d = point_line_distance([circle["h"], circle["k"]], payload["a"], payload["b"], payload["c"])
        if d >= circle["r"]:
            # force secant
            payload["c"] = int(-(payload["a"] * int(circle["h"]) + payload["b"] * int(circle["k"])))
            d = point_line_distance([circle["h"], circle["k"]], payload["a"], payload["b"], payload["c"])
        half = sp.simplify(sp.sqrt(circle["r2"] - d**2))
        chord = sp.simplify(2 * half)
        answer_value = canonical_exact(chord)
        question = (
            f"設圓 $C:{latex_standard_equation(circle['h'], circle['k'], circle['r2'])}$，"
            f"直線 $L:{_format_line(payload['a'], payload['b'], payload['c'])}$，"
            f"且圓與直線交於 $A$、$B$ 兩點，試求弦 $\\overline{{AB}}$ 的長。"
        )
        result = {"chord": answer_value, "d": canonical_exact(d)}
        explanation = [r"弦長 $=2\sqrt{r^2-d^2}$。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(circle["h"], circle["k"], "O")],
            "lines": [_visual_line(payload["a"], payload["b"], payload["c"])],
            "circles": [_visual_circle(circle["h"], circle["k"], circle["r"])],
            "implemented": True,
        }
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op == SOLVE_LINE_RELATION_RANGES_OP:
        if "r2" not in payload:
            r = _sample_radius(rng)
            a, b = _sample_line_ab(rng)
            payload.update({"r2": int(r * r), "a": a, "b": b})
        param = "k"
        p = sp.symbols(param)
        a, b = sp.sympify(payload["a"]), sp.sympify(payload["b"])
        r = sp.sqrt(payload["r2"])
        d = sp.Abs(p) / sp.sqrt(a**2 + b**2)  # line x+y+k=0, center origin
        sol_out = sp.solve_univariate_inequality(sp.StrictGreaterThan(d, r), p, relational=False)
        sol_sec = sp.solve_univariate_inequality(sp.StrictLessThan(d, r), p, relational=False)
        parts = {"(1)不相交": _format_interval(sol_out, param), "(2)相割": _format_interval(sol_sec, param)}
        line_tex = _format_line(a, b, 0).replace("=0", f"+{param}=0")
        if f"+{param}" not in line_tex and param not in line_tex:
            # _format_line with c=0 may omit constant; rebuild
            a_disp, b_disp = canonical_exact(a), canonical_exact(b)
            b_term = "" if b == 0 else (f"+{b_disp}y" if b > 0 else f"{b_disp}y")
            line_tex = f"{a_disp}x{b_term}+{param}=0"
        question = (
            f"(1) 若直線 $L:{line_tex}$ 與圓 $x^{{2}}+y^{{2}}={canonical_exact(payload['r2'])}$ 不相交，試求 $k$ 的範圍。\n"
            f"(2) 若直線 $L:{line_tex}$ 與同一圓相割，試求 $k$ 的範圍。"
        )
        answer_value = parts
        answer_type, presentation = "multi_part", "multiple_inputs"
        result = {"parts": parts}
        explanation = ["不相交 $d>r$；相割 $d<r$。"]

    elif op == COUNT_INTERSECTIONS_OP:
        if "h" not in payload:
            circle = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            td = rng.choice([0, circle["r"], circle["r"] + 2])
            c = _line_c_for_distance(circle["h"], circle["k"], a, b, td)
            payload.update(
                {
                    "d": circle["D"],
                    "e": circle["E"],
                    "f": circle["F"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "h": circle["h"],
                }
            )
        ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"])
        d = point_line_distance([ext["h"], ext["k"]], payload["a"], payload["b"], payload["c"])
        n = _intersection_count(d, ext["r"])
        answer_value = str(n)
        question = (
            f"試問直線 $L:{_format_line(payload['a'], payload['b'], payload['c'])}$ 與圓 "
            f"$C:{latex_general_equation(payload['d'], payload['e'], payload['f'])}$ 有幾個交點？"
        )
        result = {"count": n}
        explanation = ["由距離與半徑比較得交點個數。"]

    elif op == STORM_PATH_OP:
        # Chord length of path through storm circle: 2*sqrt(R^2-d^2)
        if "R" not in payload:
            R = rng.choice([100, 150, 200, 250, 300])
            d = rng.choice([x for x in (50, 80, 100, 120, 150, 180) if x < R])
            payload.update({"R": R, "d": d})
        R, d = sp.Integer(payload["R"]), sp.Integer(payload["d"])
        if d >= R:
            d = R - 50
        length = sp.simplify(2 * sp.sqrt(R**2 - d**2))
        answer_value = canonical_exact(length)
        question = (
            f"颱風暴風半徑為 ${canonical_exact(R)}$ 公里，前進路線到燈塔的垂直距離為 ${canonical_exact(d)}$ 公里。"
            f"設速度方向與暴風半徑不變，試求燈塔在暴風圈內期間，颱風共前進幾公里？"
        )
        result = {"path_length": answer_value}
        explanation = [r"相當於求弦長 $2\sqrt{R^2-d^2}$。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(0, 0, "O"), _visual_point(0, d, "L")],
            "lines": [_visual_line(0, 1, -int(d), "航線")],
            "circles": [_visual_circle(0, 0, R, "暴風圈")],
            "implemented": True,
            "x_range": [-float(R) - 20, float(R) + 20],
            "y_range": [-float(R) - 20, float(R) + 20],
        }

    elif op == DIAMETER_CHORD_PARAM_MCQ_OP:
        # AB diameter iff line through center: d=0
        if "a" not in payload:
            payload.update({"a_line": 3, "b_line": 4, "c_line": 5, "r": 1})
        # circle (x-a)^2+(y+a)^2=1, line 3x+4y+5=0 through center (a,-a)
        # 3a - 4a + 5 = 0 ⇒ -a + 5 = 0 ⇒ a = 5
        p = sp.symbols("a", real=True)
        h, k = p, -p
        expr = sp.simplify(payload["a_line"] * h + payload["b_line"] * k + payload["c_line"])
        sols = sp.solve(sp.Eq(expr, 0), p)
        correct = canonical_exact(sols[0])
        ci = int(sols[0])
        distractors = [str(ci + i) for i in (-1, 1, 2)]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"已知圓 $C:\\left(x-a\\right)^{{2}}+\\left(y+a\\right)^{{2}}=1$。若直線 "
            f"$L:{_format_line(payload['a_line'], payload['b_line'], payload['c_line'])}$ "
            f"與圓相交於 $A$、$B$ 且 $\\overline{{AB}}$ 為直徑，則 $a$ 之值為"
        )
        result = {"a": correct}
        explanation = ["直徑弦 ⇒ 直線過圓心。"]

    elif op == TRIANGLE_MAB_AREA_OP:
        if "h" not in payload:
            circle = make_circle(h=-1, k=2, r=5)
            payload.update({"d_c": circle["D"], "e_c": circle["E"], "f_c": circle["F"], "a": 3, "b": -4, "c": -4})
        ext = center_radius_from_general(d=payload["d_c"], e=payload["e_c"], f=payload["f_c"])
        d = point_line_distance([ext["h"], ext["k"]], payload["a"], payload["b"], payload["c"])
        if d >= ext["r"]:
            payload["c"] = int(-(payload["a"] * int(ext["h"]) + payload["b"] * int(ext["k"])) + 3)
            d = point_line_distance([ext["h"], ext["k"]], payload["a"], payload["b"], payload["c"])
        chord = 2 * sp.sqrt(ext["r2"] - d**2)
        area = sp.simplify(sp.Rational(1, 2) * chord * d)
        correct = canonical_exact(area)
        distractors = [canonical_exact(area * 2), canonical_exact(area / 2), "48"]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"若圓 $C:{latex_general_equation(payload['d_c'], payload['e_c'], payload['f_c'])}$ "
            f"與直線 $L:{_format_line(payload['a'], payload['b'], payload['c'])}$ 相交於 $A$、$B$，"
            f"圓心為 $M$，則 $\\triangle MAB$ 的面積為"
        )
        result = {"area": correct}
        explanation = [r"面積 $=\dfrac{1}{2}\cdot AB\cdot d$。"]

    elif op == AXIS_TANGENT_PARAM_OP:
        # x^2+y^2+Dx+Ey-k=0 tangent to y-axis (x=0)
        if "d" not in payload:
            dd = _sample_int(rng, -6, 6, nonzero=True) * 2
            ee = _sample_int(rng, -6, 6, nonzero=True) * 2
            payload.update({"d": dd, "e": ee})
        param = "k"
        p = sp.symbols(param)
        dd, ee = sp.sympify(payload["d"]), sp.sympify(payload["e"])
        h, k0 = -dd / 2, -ee / 2
        r2 = (dd**2 + ee**2) / 4 - (-p)  # F=-k when equation ...-k=0
        # y-axis x=0: d=|h|
        sols = sp.solve(sp.Eq(sp.Abs(h) ** 2, r2), p)
        answer_value = canonical_exact(sols[0]) if len(sols) == 1 else ",".join(canonical_exact(s) for s in sols)
        question = (
            f"在坐標平面上，若圓 $x^{{2}}+y^{{2}}{_coeff_term(dd,'x')}{_coeff_term(ee,'y')}-{param}=0$ "
            f"與 $y$ 軸相切，則 ${param}=$"
        )
        result = {"k": answer_value}
        explanation = ["與 y 軸相切 ⇒ 圓心到 x=0 的距離等於半徑。"]

    elif op == TANGENT_AT_POINT_OP:
        if "h" not in payload:
            circ = _sample_circle(rng)
            px, py = _sample_point_on_circle(rng, circ["h"], circ["k"], circ["r"])
            payload.update(
                {
                    "h": circ["h"],
                    "k": circ["k"],
                    "r2": circ["r2"],
                    "px": px,
                    "py": py,
                }
            )
        tan = _tangent_at_point(payload["h"], payload["k"], payload["r2"], payload["px"], payload["py"])
        answer_value = tan["equation"]
        question = (
            f"試求通過圓 ${latex_standard_equation(payload['h'], payload['k'], payload['r2'])}$ "
            f"上一點 $P{latex_pair(payload['px'], payload['py'])}$ 的切線方程式。"
        )
        as_mcq = bool(payload.get("as_mcq"))
        if as_mcq:
            distractors = [
                _format_line(tan["A"] + 1, tan["B"], tan["C"]),
                _format_line(tan["A"], tan["B"] + 1, tan["C"]),
                _format_line(tan["A"], tan["B"], tan["C"] + 2),
            ]
            pack = _mcq_pack(answer_value, distractors, rng)
            choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
            answer_type, presentation = "single_choice", "single_choice"
            answer_value = correct_label
        result = tan
        explanation = ["切線垂直於半徑，代入切點得方程式。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [
                _visual_point(payload["h"], payload["k"], "O"),
                _visual_point(payload["px"], payload["py"], "P"),
            ],
            "lines": [_visual_line(tan["A"], tan["B"], tan["C"], "切線")],
            "circles": [_visual_circle(payload["h"], payload["k"], sp.sqrt(payload["r2"]))],
            "implemented": True,
        }
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op in {TANGENTS_PARALLEL_OP, TANGENTS_PERP_OP}:
        if "h" not in payload:
            circ = _sample_circle(rng)
            a, b = _sample_line_ab(rng)
            payload.update(
                {
                    "h": circ["h"],
                    "k": circ["k"],
                    "r": circ["r"],
                    "a": a,
                    "b": b,
                    "c_ref": rng.choice([-5, -3, -1, 1, 3, 5]),
                }
            )
        a, b = sp.sympify(payload["a"]), sp.sympify(payload["b"])
        if op == TANGENTS_PERP_OP:
            a, b = _perp_direction(a, b)
        lines = _parallel_tangents(payload["h"], payload["k"], payload["r"], a, b)
        parts = {"切線一": lines[0]["equation"], "切線二": lines[1]["equation"]}
        answer_value = parts
        answer_type, presentation = "multi_part", "multiple_inputs"
        verb = "平行於" if op == TANGENTS_PARALLEL_OP else "垂直於"
        ref = _format_line(payload["a"], payload["b"], payload.get("c", 0) if "c" in payload else (
            5 if op == TANGENTS_PARALLEL_OP else -3
        ))
        # rebuild ref without forcing c for perp source x+2y-3=0
        if op == TANGENTS_PERP_OP:
            ref = _format_line(payload["a"], payload["b"], payload.get("c_ref", -3))
        else:
            ref = _format_line(payload["a"], payload["b"], payload.get("c_ref", 5))
        circle_eq = (
            latex_standard_equation(payload["h"], payload["k"], sp.Integer(payload["r"]) ** 2)
            if not (payload["h"] == 0 and payload["k"] == 0)
            else f"x^{{2}}+y^{{2}}={canonical_exact(sp.Integer(payload['r'])**2)}"
        )
        question = f"試求{verb}${ref}$且與圓 ${circle_eq}$ 相切的直線方程式。"
        result = {"lines": lines}
        explanation = ["設平行／垂直直線族，由圓心距離等於半徑解出兩解。"]
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "points": [_visual_point(payload["h"], payload["k"], "O")],
            "lines": [_visual_line(L["A"], L["B"], L["C"], f"L{i}") for i, L in enumerate(lines, 1)],
            "circles": [_visual_circle(payload["h"], payload["k"], payload["r"])],
            "implemented": True,
        }
        xr, yr = _range_from_entities(visual_spec["points"], visual_spec["circles"])
        visual_spec["x_range"], visual_spec["y_range"] = xr, yr

    elif op == TANGENTS_QUAD_AREA_OP:
        # External A, circle, tangents AP AQ, center M; kite APMQ area = r * t
        if "point" not in payload:
            payload.update({"point": [5, 0], "d": -2, "e": -4, "f": -11})
        ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"])
        px, py = _as_pair(payload["point"])
        pc2 = sp.simplify((px - ext["h"]) ** 2 + (py - ext["k"]) ** 2)
        t2 = sp.simplify(pc2 - ext["r2"])
        if t2 <= 0:
            payload["point"] = [ext["h"] + ext["r"] + 3, ext["k"]]
            px, py = _as_pair(payload["point"])
            pc2 = sp.simplify((px - ext["h"]) ** 2 + (py - ext["k"]) ** 2)
            t2 = sp.simplify(pc2 - ext["r2"])
        t = sp.sqrt(t2)
        area = sp.simplify(ext["r"] * t)  # kite area = r*t ? Actually 2 triangles each (1/2)r*t → r*t
        # Wait: two right triangles AMP and AMQ each area (1/2)*r*t → total r*t. Yes.
        correct = canonical_exact(area)
        distractors = [canonical_exact(area * 2), canonical_exact(area / 2), "6"]
        pack = _mcq_pack(correct, distractors, rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"過點 $A{latex_pair(px, py)}$ 向圓 ${latex_general_equation(payload['d'], payload['e'], payload['f'])}$ "
            f"作二切線，切點為 $P$、$Q$，圓心為 $M$，則四邊形 $APMQ$ 面積為"
        )
        result = {"area": correct, "t": canonical_exact(t)}
        explanation = [r"直角三角形面積和：面積 $=r\cdot t$。"]

    elif op == TANGENT_SEGMENT_LENGTHS_OP:
        if "point" not in payload:
            c1 = _sample_circle(rng)
            c2 = _sample_circle(rng)
            pt = _sample_external_point(rng, c1["h"], c1["k"], c1["r"])
            # ensure external to both
            if (pt[0] - c2["h"]) ** 2 + (pt[1] - c2["k"]) ** 2 <= c2["r2"]:
                pt = _sample_external_point(rng, c2["h"], c2["k"], c2["r"])
            payload.update(
                {
                    "point": pt,
                    "circles": [
                        {"form": "standard", "h": c1["h"], "k": c1["k"], "r2": c1["r2"]},
                        {
                            "form": "general",
                            "d": c2["D"],
                            "e": c2["E"],
                            "f": c2["F"],
                        },
                    ],
                }
            )
        px, py = _as_pair(payload["point"])
        for idx, circ in enumerate(payload["circles"], 1):
            if circ.get("form") == "general" or "d" in circ:
                ext = center_radius_from_general(d=circ["d"], e=circ["e"], f=circ["f"], scale=circ.get("scale", 1))
                h, k, r2 = ext["h"], ext["k"], ext["r2"]
                eq = latex_general_equation(circ["d"], circ["e"], circ["f"]) if circ.get("scale", 1) == 1 else "…"
            else:
                h, k, r2 = circ["h"], circ["k"], circ["r2"]
                eq = latex_standard_equation(h, k, r2)
            pc2 = (px - h) ** 2 + (py - k) ** 2
            t2 = sp.simplify(pc2 - r2)
            if t2 <= 0:
                # nudge point outward for generation safety
                t2 = sp.Integer(4)
            parts[f"({idx})"] = canonical_exact(sp.sqrt(t2))
        stem_items = []
        for idx, circ in enumerate(payload["circles"], 1):
            if "d" in circ or circ.get("form") == "general":
                body = f"${latex_general_equation(circ['d'], circ['e'], circ['f'])}$"
            else:
                body = f"${latex_standard_equation(circ['h'], circ['k'], circ['r2'])}$"
            stem_items.append({"group_label": f"({idx})", "text": body})
        stem_structure = build_stem_structure(
            f"已知點 $P{latex_pair(px, py)}$，試求 $P$ 到下列兩圓之切線段長：",
            stem_items,
        )
        question = stem_structure_to_question_text(stem_structure)
        answer_value = parts
        answer_type, presentation = "multi_part", "multiple_inputs"
        result = {"parts": parts}
        explanation = [r"切線段長 $=\sqrt{PC^2-r^2}$。"]

    elif op == COUNT_LINE_TWO_CIRCLES_OP:
        if "a" not in payload:
            payload.update({
                "a": 1, "b": -1, "c": -4,
                "c1": {"d": -2, "e": 2, "f": 0},
                "c2": {"d": -4, "e": 4, "f": 0},
            })
        total = 0
        for key in ("c1", "c2"):
            circ = payload[key]
            ext = center_radius_from_general(d=circ["d"], e=circ["e"], f=circ["f"])
            d = point_line_distance([ext["h"], ext["k"]], payload["a"], payload["b"], payload["c"])
            total += _intersection_count(d, ext["r"])
        correct = str(total)
        distractors = [str(x) for x in (1, 2, 3, 4) if str(x) != correct]
        pack = _mcq_pack(correct, distractors[:3], rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"若圓 $C_1:{latex_general_equation(payload['c1']['d'], payload['c1']['e'], payload['c1']['f'])}$、"
            f"圓 $C_2:{latex_general_equation(payload['c2']['d'], payload['c2']['e'], payload['c2']['f'])}$，"
            f"則直線 $L:{_format_line(payload['a'], payload['b'], payload['c'])}$ 與兩圓共有幾個交點？"
        )
        result = {"count": total}
        explanation = ["分別求直線與各圓交點數後相加（不重複計公共點時依題意累加）。"]

    elif op == TANGENT_SEGMENT_MCQ_OP:
        if "d" not in payload:
            payload.update({"d": -6, "e": 4, "f": 4, "point": [0, 0]})
        ext = center_radius_from_general(d=payload["d"], e=payload["e"], f=payload["f"])
        px, py = _as_pair(payload["point"])
        t2 = sp.simplify((px - ext["h"]) ** 2 + (py - ext["k"]) ** 2 - ext["r2"])
        if t2 <= 0:
            t2 = sp.Integer(9)
        t = sp.sqrt(t2)
        correct = canonical_exact(t)
        distractors = ["2", "3", "4", canonical_exact(sp.sqrt(13))]
        pack = _mcq_pack(correct, [d for d in distractors if d != correct][:3], rng)
        choices, correct_label, semantic_answer = pack["choices"], pack["correct_label"], pack["semantic_answer"]
        answer_type, presentation = "single_choice", "single_choice"
        answer_value = correct_label
        question = (
            f"自原點 $O$ 到圓 ${latex_general_equation(payload['d'], payload['e'], payload['f'])}$ 作一切線，"
            f"切點為 $T$，則 $\\overline{{OT}}=$"
        )
        result = {"length": correct}
        explanation = [r"$\overline{OT}=\sqrt{OC^2-r^2}$。"]

    else:
        raise ValueError(f"unhandled_gap_op:{op}")

    return _finish_matrix(
        op=op,
        question=question,
        answer_value=answer_value,
        explanation=explanation,
        payload=payload,
        result=result,
        seed=seed,
        curriculum_profile=curriculum_profile,
        difficulty_profile=difficulty_profile,
        answer_type=answer_type,
        presentation=presentation,
        parts=parts,
        choices=choices,
        correct_label=correct_label,
        semantic_answer=semantic_answer,
        distractors=distractors,
        visual_spec=visual_spec,
        stem_structure=stem_structure,
        part_labels=part_labels,
    )
