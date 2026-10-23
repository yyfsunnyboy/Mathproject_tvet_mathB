"""Exact domain operations for general-high Mathematics 1, Unit 5 (直線方程式).

Domain key ``analytic_geometry.line_equations``.  Every operation is one shared, source-agnostic
implementation: components pass *inputs only* (``constraints``); this module computes the
canonical answer with exact ``Fraction`` arithmetic and a validator re-derives / re-checks it by an
independent method (sympy substitution and defining-property checks), never by calling the same
construction code again.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import isqrt
from typing import Any, Callable

import sympy as sp

from . import line_geometry as G
from .line_geometry import Radical, fr, frac_text, pt

DOMAIN_KEY = "analytic_geometry.line_equations"


def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _sr(value: Any) -> sp.Rational:
    value = fr(value)
    return sp.Rational(value.numerator, value.denominator)


def _sp_point(p: Any) -> tuple[sp.Rational, sp.Rational]:
    return (_sr(p[0]), _sr(p[1]))


def _line_rec(line: G.Line) -> dict[str, Any]:
    return {"kind": "line", "line": list(line), "text": G.line_text(line)}


def _point_rec(p: G.Point) -> dict[str, Any]:
    return {"kind": "point", "point": [frac_text(p[0]), frac_text(p[1])], "text": G.point_text(p)}


def _rational_rec(value: Fraction) -> dict[str, Any]:
    return {"kind": "rational", "canonical": frac_text(value)}


def _radical_rec(value: Radical) -> dict[str, Any]:
    return {
        "kind": "rational" if value.is_rational() else "radical",
        "canonical": value.canonical(),
        "latex": value.latex(),
        "coef": frac_text(value.coef),
        "radicand": value.radicand,
    }


def _sp_line_holds(line: list[int], p: Any) -> bool:
    x, y = _sp_point(p)
    return sp.Rational(line[0]) * x + sp.Rational(line[1]) * y + sp.Rational(line[2]) == 0


def _sp_parallel(l1: list[int], l2: list[int]) -> bool:
    return sp.Rational(l1[0]) * l2[1] - sp.Rational(l2[0]) * l1[1] == 0


def _sp_perpendicular(l1: list[int], l2: list[int]) -> bool:
    return sp.Rational(l1[0]) * l2[0] + sp.Rational(l1[1]) * l2[1] == 0


def _sp_intersection(l1: list[int], l2: list[int]) -> tuple[sp.Rational, sp.Rational] | None:
    x, y = sp.symbols("x y")
    sol = sp.linsolve([l1[0] * x + l1[1] * y + l1[2], l2[0] * x + l2[1] * y + l2[2]], x, y)
    if not sol:
        return None
    (sx, sy), = list(sol)
    if not (sx.is_Rational and sy.is_Rational):
        return None
    return (sx, sy)


# --- 1. rank_line_slopes ---------------------------------------------------------------

def rank_line_slopes(lines: list[dict[str, Any]], ask: str = "slopes_and_order", **text: Any) -> dict[str, Any]:
    records = []
    for item in lines:
        p, q = pt(item["p"]), pt(item["q"])
        if p[0] == q[0]:
            raise ValueError("vertical_line_has_no_slope")
        records.append({"index": int(item["index"]), "slope": frac_text((q[1] - p[1]) / (q[0] - p[0]))})
    values = [fr(r["slope"]) for r in records]
    if len(set(values)) != len(values):
        raise ValueError("slopes_must_be_distinct")
    order = [r["index"] for r in sorted(records, key=lambda r: fr(r["slope"]), reverse=True)]
    return {"slopes": records, "order": order, "order_text": ">".join(f"m{i}" for i in order), "ask": ask}


def _check_rank_line_slopes(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    sympy_slopes: dict[int, sp.Rational] = {}
    for item in givens["lines"]:
        (x1, y1), (x2, y2) = _sp_point(item["p"]), _sp_point(item["q"])
        sympy_slopes[int(item["index"])] = sp.Rational((y2 - y1) / (x2 - x1))
    for record in answer["slopes"]:
        if sp.Rational(record["slope"]) != sympy_slopes[record["index"]]:
            return False
    expected = [i for i, _ in sorted(sympy_slopes.items(), key=lambda kv: kv[1], reverse=True)]
    return answer["order"] == expected and len(set(sympy_slopes.values())) == len(sympy_slopes)


# --- 2. evaluate_slope_sign_statements -------------------------------------------------------

def _segment_slopes(points: dict[str, Any], segments: list[list[str]]) -> list[Fraction]:
    out = []
    for a, b in segments:
        p, q = pt(points[a]), pt(points[b])
        if p[0] == q[0]:
            raise ValueError("vertical_segment_has_no_slope")
        out.append((q[1] - p[1]) / (q[0] - p[0]))
    return out


def _meaningful_selection(selected: list[int], total: int) -> list[int]:
    """A "select all correct options" item needs at least one right and one wrong option."""
    if not 1 <= len(selected) < total:
        raise ValueError("selection_must_have_a_true_and_a_false_option")
    return selected


def _cmp(value: Fraction, op: str) -> bool:
    return value > 0 if op == ">" else value < 0


def evaluate_slope_sign_statements(points: dict[str, Any], segments: list[list[str]], statements: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    slopes = _segment_slopes(points, segments)
    truth = []
    for s in statements:
        kind = s["kind"]
        if kind == "sign":
            truth.append(_cmp(slopes[int(s["index"]) - 1], s["op"]))
        elif kind == "product":
            value = Fraction(1)
            for m in slopes:
                value *= m
            truth.append(_cmp(value, s["op"]))
        elif kind == "sum":
            truth.append(_cmp(sum(slopes, Fraction(0)), s["op"]))
        elif kind == "chain":
            chain = [slopes[i - 1] for i in s["order"]]
            truth.append(all(chain[i] > chain[i + 1] for i in range(len(chain) - 1)))
        else:
            raise ValueError(f"unknown_statement_kind:{kind}")
    return {
        "slopes": [frac_text(m) for m in slopes],
        "truth": truth,
        "selected": _meaningful_selection([i for i, t in enumerate(truth, start=1) if t], len(truth)),
    }


def _check_evaluate_slope_sign_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    slopes = []
    for a, b in givens["segments"]:
        (x1, y1), (x2, y2) = _sp_point(givens["points"][a]), _sp_point(givens["points"][b])
        slopes.append(sp.Rational((y2 - y1) / (x2 - x1)))
    if [sp.Rational(s) for s in answer["slopes"]] != slopes:
        return False
    for statement, truth in zip(givens["statements"], answer["truth"]):
        kind = statement["kind"]
        if kind == "sign":
            m = slopes[int(statement["index"]) - 1]
            independent = bool(m > 0) if statement["op"] == ">" else bool(m < 0)
        elif kind == "product":
            value = sp.Mul(*slopes)
            independent = bool(value > 0) if statement["op"] == ">" else bool(value < 0)
        elif kind == "sum":
            value = sp.Add(*slopes)
            independent = bool(value > 0) if statement["op"] == ">" else bool(value < 0)
        else:
            chain = [slopes[i - 1] for i in statement["order"]]
            independent = all(bool(a > b) for a, b in zip(chain, chain[1:]))
        if independent != truth:
            return False
    return len(answer["truth"]) == len(givens["statements"]) and answer["selected"] == [i for i, t in enumerate(answer["truth"], 1) if t]


# --- 3. solve_line_equations -----------------------------------------------------------------

def _item_line(item: dict[str, Any]) -> G.Line:
    kind = item["kind"]
    if kind == "point_slope":
        return G.line_from_point_slope(pt(item["p"]), fr(item["m"]))
    if kind == "two_points":
        return G.line_through(pt(item["p"]), pt(item["q"]))
    if kind == "slope_y_intercept":
        return G.line_from_point_slope((Fraction(0), fr(item["b"])), fr(item["m"]))
    if kind == "intercepts":
        return G.line_from_intercepts(fr(item["a"]), fr(item["b"]))
    if kind == "vertical_through":
        return G.vertical_line(pt(item["p"])[0])
    if kind == "horizontal_through":
        return G.horizontal_line(pt(item["p"])[1])
    if kind == "parallel_through":
        return G.parallel_through(pt(item["p"]), G.norm_line(*item["line"]))
    if kind == "perpendicular_through":
        return G.perpendicular_through(pt(item["p"]), G.norm_line(*item["line"]))
    if kind == "parallel_through_intersection":
        cross = G.intersect(G.norm_line(*item["l1"]), G.norm_line(*item["l2"]))
        if cross is None:
            raise ValueError("lines_do_not_intersect")
        return G.parallel_through(cross, G.norm_line(*item["line"]))
    if kind == "perpendicular_through_intersection":
        cross = G.intersect(G.norm_line(*item["l1"]), G.norm_line(*item["l2"]))
        if cross is None:
            raise ValueError("lines_do_not_intersect")
        return G.perpendicular_through(cross, G.norm_line(*item["line"]))
    raise ValueError(f"unknown_line_item_kind:{kind}")


def solve_line_equations(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    return {"values": [_line_rec(_item_line(item)) for item in items]}


def _check_line_item(item: dict[str, Any], line: list[int]) -> bool:
    kind = item["kind"]
    if line[0] == 0 and line[1] == 0:
        return False
    if kind == "point_slope":
        if not _sp_line_holds(line, item["p"]) or line[1] == 0:
            return False
        return sp.Rational(-line[0], line[1]) == _sr(item["m"])
    if kind == "two_points":
        return _sp_line_holds(line, item["p"]) and _sp_line_holds(line, item["q"])
    if kind == "slope_y_intercept":
        if line[1] == 0:
            return False
        return _sp_line_holds(line, (0, item["b"])) and sp.Rational(-line[0], line[1]) == _sr(item["m"])
    if kind == "intercepts":
        return _sp_line_holds(line, (item["a"], 0)) and _sp_line_holds(line, (0, item["b"]))
    if kind == "vertical_through":
        return line[1] == 0 and _sp_line_holds(line, item["p"])
    if kind == "horizontal_through":
        return line[0] == 0 and _sp_line_holds(line, item["p"])
    if kind == "parallel_through":
        return _sp_line_holds(line, item["p"]) and _sp_parallel(line, list(item["line"]))
    if kind == "perpendicular_through":
        return _sp_line_holds(line, item["p"]) and _sp_perpendicular(line, list(item["line"]))
    if kind in {"parallel_through_intersection", "perpendicular_through_intersection"}:
        cross = _sp_intersection(list(G.norm_line(*item["l1"])), list(G.norm_line(*item["l2"])))
        if cross is None or not _sp_line_holds(line, cross):
            return False
        return _sp_parallel(line, list(item["line"])) if kind.startswith("parallel") else _sp_perpendicular(line, list(item["line"]))
    return False


def _check_solve_line_equations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    values = answer["values"]
    if len(values) != len(givens["items"]):
        return False
    for item, record in zip(givens["items"], values):
        line = [int(v) for v in record["line"]]
        if G.line_text(tuple(line)) != record["text"] or not _check_line_item(item, line):
            return False
    return True


# --- 4. slope_of_line_from_equation ------------------------------------------------------------

def slope_of_line_from_equation(line: list[Any], **text: Any) -> dict[str, Any]:
    a, b, c = (fr(v) for v in line)
    if b == 0:
        raise ValueError("vertical_line_has_no_slope")
    return {"values": [_rational_rec(-a / b)]}


def _check_slope_of_line_from_equation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    x, y = sp.symbols("x y")
    a, b, c = (_sr(v) for v in givens["line"])
    solved = sp.solve(sp.Eq(a * x + b * y + c, 0), y)
    if len(solved) != 1:
        return False
    slope = sp.diff(solved[0], x)
    return sp.Rational(answer["values"][0]["canonical"]) == slope


# --- 5. fill_line_property_table ---------------------------------------------------------------

def _row_full(row: dict[str, Any]) -> dict[str, Any]:
    given = row["given"]
    if given == "equation":
        line = G.norm_line(*row["line"])
    elif given == "slope_y_intercept":
        line = G.line_from_point_slope((Fraction(0), fr(row["b"])), fr(row["m"]))
    elif given == "slope_x_intercept":
        m, a = fr(row["m"]), fr(row["a"])
        line = G.line_from_point_slope((a, Fraction(0)), m)
    else:
        raise ValueError(f"unknown_row_given:{given}")
    a_, b_, c_ = line
    if a_ == 0 or b_ == 0 or c_ == 0:
        raise ValueError("table_row_needs_oblique_line_with_nonzero_intercepts")
    return {
        "equation": G.line_text(line),
        "line": list(line),
        "slope": frac_text(Fraction(-a_, b_)),
        "x_intercept": frac_text(Fraction(-c_, a_)),
        "y_intercept": frac_text(Fraction(-c_, b_)),
    }


def fill_line_property_table(rows: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    return {"rows": [_row_full(row) for row in rows]}


def _check_fill_line_property_table(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    x, y = sp.symbols("x y")
    if len(answer["rows"]) != len(givens["rows"]):
        return False
    for row, record in zip(givens["rows"], answer["rows"]):
        a, b, c = (sp.Integer(v) for v in record["line"])
        m, xi, yi = (sp.Rational(record[k]) for k in ("slope", "x_intercept", "y_intercept"))
        if not (a * xi + c == 0 and b * yi + c == 0 and m * b == -a):
            return False
        given = row["given"]
        if given == "equation":
            if not _sp_parallel(record["line"], list(row["line"])) or sp.Rational(row["line"][2]) * a != c * sp.Rational(row["line"][0]):
                return False
        elif given == "slope_y_intercept":
            if m != _sr(row["m"]) or yi != _sr(row["b"]):
                return False
        elif given == "slope_x_intercept":
            if m != _sr(row["m"]) or xi != _sr(row["a"]):
                return False
        else:
            return False
    return True


# --- 6. translate_line_equation ----------------------------------------------------------------

def translate_line_equation(line: list[Any], dx: Any, dy: Any, direction: str = "forward", **text: Any) -> dict[str, Any]:
    base = G.norm_line(*line)
    dx, dy = fr(dx), fr(dy)
    if direction == "forward":
        result = G.translate_line(base, dx, dy)
    elif direction == "inverse":
        result = G.translate_line(base, -dx, -dy)
    else:
        raise ValueError(f"unknown_translation_direction:{direction}")
    return {"values": [_line_rec(result)], "direction": direction}


def _check_translate_line_equation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    shown = [int(v) for v in G.norm_line(*givens["line"])]
    result = [int(v) for v in answer["values"][0]["line"]]
    dx, dy = _sr(givens["dx"]), _sr(givens["dy"])
    # Independent: move one concrete point of the *original* line and re-test membership.
    if givens.get("direction", "forward") == "forward":
        original, moved = shown, result
    else:
        original, moved = result, shown
    x0 = sp.Integer(0)
    a, b, c = (sp.Integer(v) for v in original)
    if b != 0:
        sample = (x0, -c / b)
    else:
        sample = (-c / a, sp.Integer(0))
    shifted = (sample[0] + dx, sample[1] + dy)
    if not _sp_line_holds(moved, shifted):
        return False
    return _sp_parallel(original, moved) and (original == moved) == (dx == 0 and dy == 0 or (a * dx + b * dy == 0))


# --- 7. solve_translation_parameter ------------------------------------------------------------

def solve_translation_parameter(line: list[Any], result_line: list[Any], axis: str = "right", **text: Any) -> dict[str, Any]:
    (a, b, c), (a2, b2, c2) = G.norm_line(*line), G.norm_line(*result_line)
    if (a, b) != (a2, b2):
        raise ValueError("translated_line_must_share_normal")
    if axis == "right":
        if a == 0:
            raise ValueError("horizontal_line_cannot_shift_right")
        h = Fraction(c - c2, a)
    elif axis == "up":
        if b == 0:
            raise ValueError("vertical_line_cannot_shift_up")
        h = Fraction(c - c2, b)
    else:
        raise ValueError(f"unknown_translation_axis:{axis}")
    return {"values": [_rational_rec(h)], "axis": axis}


def _check_solve_translation_parameter(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    h = sp.Rational(answer["values"][0]["canonical"])
    x, y = sp.symbols("x y")
    a, b, c = (sp.Integer(v) for v in G.norm_line(*givens["line"]))
    a2, b2, c2 = (sp.Integer(v) for v in G.norm_line(*givens["result_line"]))
    shifted = a * (x - h) + b * y + c if givens.get("axis", "right") == "right" else a * x + b * (y - h) + c
    return sp.expand(shifted - c2 - (a * x + b * y)) == 0


# --- 8. solve_line_constructions ---------------------------------------------------------------

def _construct(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    raw: list[Any] = []
    for item in items:
        kind = item["kind"]
        if kind == "line_through":
            value: Any = G.line_through(pt(item["p"]), pt(item["q"]))
        elif kind == "perp_bisector":
            value = G.perp_bisector(pt(item["p"]), pt(item["q"]))
        elif kind == "circumcenter":
            a, b, c = (pt(v) for v in item["pts"])
            value = G.circumcenter(a, b, c)
        elif kind == "orthocenter":
            a, b, c = (pt(v) for v in item["pts"])
            value = G.orthocenter(a, b, c)
        elif kind == "reflect_point":
            value = G.reflect_point(pt(item["p"]), G.norm_line(*item["line"]))
        elif kind == "intersect_items":
            first, second = raw[int(item["a"])], raw[int(item["b"])]
            if not (isinstance(first, tuple) and len(first) == 3 and isinstance(second, tuple) and len(second) == 3):
                raise ValueError("intersect_items_needs_two_lines")
            value = G.intersect(first, second)
            if value is None:
                raise ValueError("lines_do_not_intersect")
        elif kind == "shortest_path_point_on_axis":
            a, b = pt(item["a"]), pt(item["b"])
            if a[1] * b[1] <= 0:
                raise ValueError("points_must_be_on_the_same_side_of_the_axis")
            mirror = (a[0], -a[1])
            value = G.intersect(G.line_through(mirror, b), (0, 1, 0))
        elif kind == "shortest_path_length":
            a, b = pt(item["a"]), pt(item["b"])
            if a[1] * b[1] <= 0:
                raise ValueError("points_must_be_on_the_same_side_of_the_axis")
            dx, dy = b[0] - a[0], b[1] + a[1]
            squared = dx * dx + dy * dy
            if squared.denominator != 1:
                raise ValueError("integer_squared_distance_required")
            value = G.sqrt_radical(int(squared))
        else:
            raise ValueError(f"unknown_construction_kind:{kind}")
        raw.append(value)
        if isinstance(value, Radical):
            out.append(_radical_rec(value))
        elif len(value) == 3 and all(isinstance(v, int) for v in value):
            out.append(_line_rec(value))
        else:
            out.append(_point_rec(value))
    return out


def solve_line_constructions(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    return {"values": _construct(items)}


def _sp_dist(p: Any, q: Any) -> sp.Expr:
    return sp.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def _check_solve_line_constructions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    items, values = givens["items"], answer["values"]
    if len(values) != len(items):
        return False
    resolved: list[Any] = []
    for item, record in zip(items, values):
        kind = item["kind"]
        if kind in {"line_through", "perp_bisector"} and record["kind"] != "line":
            return False
        if record["kind"] == "line":
            line = [int(v) for v in record["line"]]
            if kind == "line_through":
                ok = _sp_line_holds(line, item["p"]) and _sp_line_holds(line, item["q"])
            else:  # perp_bisector: passes through the midpoint and its normal is parallel to PQ
                p, q = _sp_point(item["p"]), _sp_point(item["q"])
                mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                ok = _sp_line_holds(line, mid) and sp.Rational(line[0]) * (q[1] - p[1]) - sp.Rational(line[1]) * (q[0] - p[0]) == 0
            if not ok:
                return False
            resolved.append(line)
        elif record["kind"] == "point":
            point = (sp.Rational(record["point"][0]), sp.Rational(record["point"][1]))
            if kind == "circumcenter":
                a, b, c = (_sp_point(v) for v in item["pts"])
                if not (sp.simplify(_sp_dist(point, a) - _sp_dist(point, b)) == 0 and sp.simplify(_sp_dist(point, b) - _sp_dist(point, c)) == 0):
                    return False
            elif kind == "orthocenter":
                a, b, c = (_sp_point(v) for v in item["pts"])
                def dot(u, v):  # noqa: E306
                    return u[0] * v[0] + u[1] * v[1]
                if not (dot((point[0] - a[0], point[1] - a[1]), (b[0] - c[0], b[1] - c[1])) == 0
                        and dot((point[0] - b[0], point[1] - b[1]), (a[0] - c[0], a[1] - c[1])) == 0):
                    return False
            elif kind == "reflect_point":
                p = _sp_point(item["p"])
                line = [int(v) for v in G.norm_line(*item["line"])]
                midpoint = ((p[0] + point[0]) / 2, (p[1] + point[1]) / 2)
                direction = (point[0] - p[0], point[1] - p[1])
                if not (_sp_line_holds(line, midpoint) and direction[0] * line[1] - direction[1] * line[0] == 0):
                    return False
            elif kind == "intersect_items":
                for ref in (int(item["a"]), int(item["b"])):
                    if not _sp_line_holds(resolved[ref], point):
                        return False
            elif kind == "shortest_path_point_on_axis":
                a, b = _sp_point(item["a"]), _sp_point(item["b"])
                if point[1] != 0:
                    return False
                best = _sp_dist(a, point) + _sp_dist(point, b)
                mirror = (a[0], -a[1])
                if sp.simplify(best - _sp_dist(mirror, b)) != 0:
                    return False
                for delta in (sp.Rational(-1, 2), sp.Rational(1, 2)):
                    other = (point[0] + delta, sp.Integer(0))
                    if not bool(_sp_dist(a, other) + _sp_dist(other, b) > best):
                        return False
            else:
                return False
            resolved.append(point)
        else:  # radical / rational length
            if kind != "shortest_path_length":
                return False
            a, b = _sp_point(item["a"]), _sp_point(item["b"])
            length = _sp_dist((a[0], -a[1]), b)
            claimed = sp.Rational(record["coef"]) * sp.sqrt(record["radicand"])
            if sp.simplify(length - claimed) != 0:
                return False
            resolved.append(claimed)
    return True


# --- 9. solve_line_parameters ----------------------------------------------------------------------

def _parse_coefficients(spec: dict[str, Any], symbols: dict[str, sp.Symbol]) -> list[sp.Expr]:
    return [sp.sympify(str(c), locals=symbols) for c in spec]


def _condition_equations(givens: dict[str, Any], symbols: dict[str, sp.Symbol]) -> list[sp.Expr]:
    lines = {name: _parse_coefficients(coef, symbols) for name, coef in givens["lines"].items()}
    equations: list[sp.Expr] = []
    for cond in givens["conditions"]:
        kind = cond["kind"]
        if kind == "on_line":
            a, b, c = lines[cond["line"]]
            x, y = _sp_point(cond["point"])
            equations.append(a * x + b * y + c)
        elif kind == "perpendicular":
            a1, b1, _ = lines[cond["l1"]]
            a2, b2, _ = lines[cond["l2"]]
            equations.append(a1 * a2 + b1 * b2)
        elif kind == "parallel":
            a1, b1, _ = lines[cond["l1"]]
            a2, b2, _ = lines[cond["l2"]]
            equations.append(a1 * b2 - a2 * b1)
        elif kind == "perpendicular_to_segment":
            a, b, _ = lines[cond["line"]]
            (x1, y1), (x2, y2) = _sp_point(cond["p"]), _sp_point(cond["q"])
            equations.append(a * (y2 - y1) - b * (x2 - x1))
        elif kind == "point_line_distance":
            a, b, c = lines[cond["line"]]
            x, y = _sp_point(cond["point"])
            d = sp.sympify(str(cond["distance"]))
            equations.append((a * x + b * y + c) ** 2 - d ** 2 * (a ** 2 + b ** 2))
        else:
            raise ValueError(f"unknown_parameter_condition:{kind}")
    return equations


def solve_line_parameters(unknowns: list[str], lines: dict[str, Any], conditions: list[dict[str, Any]], targets: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    symbols = {name: sp.Symbol(name, real=True) for name in unknowns}
    givens = {"lines": lines, "conditions": conditions}
    equations = _condition_equations(givens, symbols)
    solutions = sp.solve(equations, [symbols[n] for n in unknowns], dict=True)
    valid = []
    for sol in solutions:
        if not all(name in {str(k) for k in sol} for name in unknowns):
            raise ValueError("unknowns_not_determined")
        # reject degenerate lines (both normal coefficients zero)
        resolved = {name: _parse_coefficients(coef, symbols) for name, coef in lines.items()}
        if any(sp.simplify(c[0].subs(sol)) == 0 and sp.simplify(c[1].subs(sol)) == 0 for c in resolved.values()):
            continue
        valid.append(sol)
    if not valid:
        raise ValueError("no_valid_parameter_solution")
    rows = []
    for target in targets:
        expr = sp.sympify(target["expr"], locals=symbols)
        values = sorted({sp.nsimplify(expr.subs(sol)) for sol in valid}, key=lambda v: float(v))
        if not all(v.is_Rational for v in values):
            raise ValueError("irrational_parameter_value")
        rows.append({"name": target["name"], "values": [frac_text(Fraction(int(v.p), int(v.q))) for v in values]})
    return {"targets": rows, "solution_count": len(valid)}


def _check_solve_line_parameters(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    symbols = {name: sp.Symbol(name, real=True) for name in givens["unknowns"]}
    equations = _condition_equations(givens, symbols)
    names = givens["unknowns"]
    # Independent: brute-force every rational candidate the answer implies, substitute, and require zero residual.
    per_target = {row["name"]: [sp.Rational(v) for v in row["values"]] for row in answer["targets"]}
    unknown_targets = [t for t in givens["targets"] if t["expr"] in names]
    if len(unknown_targets) != len(names):
        # composite targets (e.g. a+b+c): rebuild each solution from the solver's own count, then verify by substitution
        resolved = sp.solve(equations, [symbols[n] for n in names], dict=True)
    else:
        grids = [per_target[t["name"]] for t in unknown_targets]
        resolved = []
        for combo in product(*grids):
            candidate = {symbols[t["expr"]]: v for t, v in zip(unknown_targets, combo)}
            if all(sp.simplify(eq.subs(candidate)) == 0 for eq in equations):
                resolved.append(candidate)
        if not resolved:
            return False
        if len(resolved) != answer["solution_count"]:
            return False
    if not resolved:
        return False
    for sol in resolved:
        if not all(sp.simplify(eq.subs(sol)) == 0 for eq in equations):
            return False
    for target in givens["targets"]:
        expr = sp.sympify(target["expr"], locals=symbols)
        independent = sorted({sp.nsimplify(expr.subs(sol)) for sol in resolved}, key=lambda v: float(v))
        if [sp.Rational(v) for v in per_target[target["name"]]] != [sp.Rational(v) for v in independent]:
            return False
    return True


# --- 10. compute_line_distances --------------------------------------------------------------------

def compute_line_distances(items: list[dict[str, Any]], **text: Any) -> dict[str, Any]:
    values = []
    for item in items:
        if item["kind"] == "point_to_line":
            values.append(_radical_rec(G.distance_point_line(pt(item["p"]), G.norm_line(*item["line"]))))
        elif item["kind"] == "parallel_lines":
            values.append(_radical_rec(G.distance_parallel_lines(G.norm_line(*item["l1"]), G.norm_line(*item["l2"]))))
        else:
            raise ValueError(f"unknown_distance_kind:{item['kind']}")
    return {"values": values}


def _check_compute_line_distances(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    if len(answer["values"]) != len(givens["items"]):
        return False
    for item, record in zip(givens["items"], answer["values"]):
        claimed = sp.Rational(record["coef"]) * sp.sqrt(record["radicand"])
        if item["kind"] == "point_to_line":
            line = [sp.Rational(str(v)) for v in item["line"]]
            p = _sp_point(item["p"])
            # Independent: foot of the perpendicular found with linsolve, then the Euclidean distance.
            t = sp.symbols("t", real=True)
            foot = (p[0] + t * line[0], p[1] + t * line[1])
            t_sol = sp.solve(line[0] * foot[0] + line[1] * foot[1] + line[2], t)[0]
            foot = (foot[0].subs(t, t_sol), foot[1].subs(t, t_sol))
            truth = _sp_dist(p, foot)
        else:
            l1 = [sp.Rational(str(v)) for v in item["l1"]]
            l2 = [sp.Rational(str(v)) for v in item["l2"]]
            if l1[0] * l2[1] - l2[0] * l1[1] != 0:
                return False
            # pick a concrete point on l1, measure to l2 through its perpendicular foot
            if l1[1] != 0:
                p = (sp.Integer(0), -l1[2] / l1[1])
            else:
                p = (-l1[2] / l1[0], sp.Integer(0))
            t = sp.symbols("t", real=True)
            foot = (p[0] + t * l2[0], p[1] + t * l2[1])
            t_sol = sp.solve(l2[0] * foot[0] + l2[1] * foot[1] + l2[2], t)[0]
            foot = (foot[0].subs(t, t_sol), foot[1].subs(t, t_sol))
            truth = _sp_dist(p, foot)
        if sp.simplify(truth - claimed) != 0:
            return False
    return True


# --- 11. solve_window_decorative_lines -----------------------------------------------------------------

def _window_lines(width: Fraction, height: Fraction, edge: G.Point, delta_c: Fraction) -> tuple[G.Line, G.Line]:
    center = (width / 2, height / 2)
    l1 = G.line_through(center, edge)
    if l1[0] != l1[1] or l1[0] <= 0:
        raise ValueError("decorative_lines_must_have_slope_minus_one")
    # toward the origin the constant term grows by delta_c (a x + b y + c = 0 with a=b=1)
    l2 = G.norm_line(l1[0], l1[1], Fraction(l1[2]) + delta_c)
    return l1, l2


def solve_window_decorative_lines(width: Any, height: Any, edge_point: list[Any], delta_c: Any, asks: list[str], **text: Any) -> dict[str, Any]:
    w, h, dc = fr(width), fr(height), fr(delta_c)
    l1, l2 = _window_lines(w, h, pt(edge_point), dc)
    spacing = G.radical_of_ratio(dc, 2)  # distance between x+y+c=0 and x+y+c+dc=0
    answer: dict[str, Any] = {"spacing": _radical_rec(spacing), "values": []}
    for ask in asks:
        if ask == "l1_equation":
            answer["values"].append(_line_rec(l1))
        elif ask == "l2_equation":
            answer["values"].append(_line_rec(l2))
        elif ask == "distance_origin_l1":
            answer["values"].append(_radical_rec(G.distance_point_line((Fraction(0), Fraction(0)), l1)))
        elif ask == "line_count":
            lo, hi = Fraction(0), w + h  # x + y over the window runs from 0 to w + h
            c1 = Fraction(l1[2])
            span = int(w + h) * 4
            count = sum(1 for t in range(-span, span + 1) if lo < -(c1 + dc * t) < hi)
            answer["values"].append(_rational_rec(Fraction(count)))
        else:
            raise ValueError(f"unknown_window_ask:{ask}")
    answer["asks"] = list(asks)
    return answer


def _check_solve_window_decorative_lines(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    w, h = _sr(givens["width"]), _sr(givens["height"])
    dc = _sr(givens["delta_c"])
    ex, ey = _sp_point(givens["edge_point"])
    cx, cy = w / 2, h / 2
    slope = (ey - cy) / (ex - cx)
    if slope != -1:
        return False
    c1 = -(cx + cy)  # x + y + c1 = 0 passes through the centre
    for ask, record in zip(answer["asks"], answer["values"]):
        if ask == "l1_equation":
            if not (_sp_line_holds(record["line"], (cx, cy)) and _sp_line_holds(record["line"], (ex, ey))):
                return False
        elif ask == "l2_equation":
            line = record["line"]
            if not _sp_parallel(line, [1, 1, 0]):
                return False
            # the neighbour line lies delta_c/sqrt(2) from L1 on the origin side
            if sp.simplify(sp.Abs(sp.Rational(line[2]) - c1) / sp.sqrt(2) - dc / sp.sqrt(2)) != 0 or not bool(line[2] > c1):
                return False
        elif ask == "distance_origin_l1":
            claimed = sp.Rational(record["coef"]) * sp.sqrt(record["radicand"])
            if sp.simplify(sp.Abs(c1) / sp.sqrt(2) - claimed) != 0:
                return False
        elif ask == "line_count":
            levels = [-(c1 + dc * t) for t in range(-300, 301)]
            independent = sum(1 for level in levels if 0 < level < w + h)
            # also count by testing real intersection with the open rectangle through its four corners
            corners = [x + y for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
            independent_corners = sum(1 for level in levels if min(corners) < level < max(corners))
            if independent != independent_corners or int(record["canonical"]) != independent:
                return False
        else:
            return False
    return True


# --- 12. solve_triangle_region_system ---------------------------------------------------------------------

def _closed_inequality(line: G.Line, inside: G.Point, strict: bool = False) -> dict[str, Any]:
    value = G.side_value(line, inside)
    if value == 0:
        raise ValueError("interior_point_on_boundary")
    sign = 1 if value > 0 else -1
    a, b, c = (sign * v for v in line)  # a x + b y + c >= 0 holds at ``inside``
    return {"line": [a, b, c], "op": ">" if strict else ">="}


def inequality_text(rel: dict[str, Any], prefer_le: bool = True) -> str:
    """Render ``ax+by+c (op) 0``; textbook style turns ≥ into ≤ when the leading coefficient is negative."""
    a, b, c = rel["line"]
    op = rel["op"]
    if prefer_le and (a < 0 or (a == 0 and b < 0)):
        a, b, c = -a, -b, -c
        op = {">=": "<=", ">": "<"}[op]
    body = G.line_text((a, b, c))[:-2]
    symbol = {">=": "≥", ">": ">", "<=": "≤", "<": "<"}[op]
    return f"{body}{symbol}0"


def solve_triangle_region_system(vertices: dict[str, Any], choice_points: list[dict[str, Any]], family_point: list[Any], **text: Any) -> dict[str, Any]:
    names = list(vertices)
    a, b, c = (pt(vertices[n]) for n in names)
    area2 = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
    if area2 == 0:
        raise ValueError("degenerate_triangle")
    centroid = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3)
    pairs = [(a, b), (b, c), (c, a)]
    relations = [_closed_inequality(G.line_through(p, q), centroid) for p, q in pairs]
    # family y = m x + 1 passes through (0, 1) = family_point; it bisects the triangle iff it hits the midpoint of the opposite side
    pivot = pt(family_point)
    if pivot not in (a, b, c):
        raise ValueError("family_point_must_be_a_vertex")
    others = [v for v in (a, b, c) if v != pivot]
    mid = G.midpoint(others[0], others[1])
    if mid[0] == pivot[0]:
        raise ValueError("bisecting_line_would_be_vertical")
    m = (mid[1] - pivot[1]) / (mid[0] - pivot[0])
    always_on = [i for i, p in enumerate(choice_points) if pt(p["point"]) == pivot]
    if len(always_on) != 1:
        raise ValueError("exactly_one_choice_must_be_the_fixed_point")
    return {
        "relations": relations,
        "inequality_texts": [inequality_text(r) for r in relations],
        "fixed_point_choice": always_on[0],
        "m": _rational_rec(m),
        "bisect_point": [frac_text(mid[0]), frac_text(mid[1])],
        "centroid": [frac_text(centroid[0]), frac_text(centroid[1])],
    }


def _sp_area(p: Any, q: Any, r: Any) -> sp.Expr:
    return sp.Abs((q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1])) / 2


def _check_solve_triangle_region_system(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    pts_ = [_sp_point(v) for v in givens["vertices"].values()]
    centroid = tuple(sum(p[i] for p in pts_) / 3 for i in range(2))
    for rel in answer["relations"]:
        a, b, c = (sp.Rational(v) for v in rel["line"])
        if rel["op"] != ">=" or not bool(a * centroid[0] + b * centroid[1] + c > 0):
            return False
        if sum(1 for p in pts_ if a * p[0] + b * p[1] + c == 0) != 2:
            return False
        if not all(bool(a * p[0] + b * p[1] + c >= 0) for p in pts_):
            return False
    if len(answer["relations"]) != 3 or len({tuple(r["line"]) for r in answer["relations"]}) != 3:
        return False
    pivot = _sp_point(givens["family_point"])
    m = sp.Rational(answer["m"]["canonical"])
    x, y = sp.symbols("x y")
    others = [p for p in pts_ if p != pivot]
    # the line through the pivot with slope m splits the triangle into two equal-area pieces
    cut = sp.solve(sp.Eq((others[1][1] - others[0][1]) * (x - others[0][0]) - (others[1][0] - others[0][0]) * (y - others[0][1]), 0).subs(y, pivot[1] + m * (x - pivot[0])), x)
    if len(cut) != 1:
        return False
    cut_pt = (cut[0], pivot[1] + m * (cut[0] - pivot[0]))
    if sp.simplify(_sp_area(pivot, others[0], cut_pt) * 2 - _sp_area(pivot, others[0], others[1])) != 0:
        return False
    ok_choice = [i for i, p in enumerate(givens["choice_points"]) if _sp_point(p["point"]) == pivot]
    return ok_choice == [answer["fixed_point_choice"]]


# --- 13. read_region_signs_from_figure ----------------------------------------------------------------------

def _find_interior_point(relations: list[tuple[int, int, int]]) -> G.Point | None:
    for denominator in (1, 2, 4):
        for ix in range(-40, 41):
            for iy in range(-40, 41):
                p = (Fraction(ix, denominator), Fraction(iy, denominator))
                if all(G.side_value(r, p) > 0 for r in relations):
                    return p
    return None


def read_region_signs_from_figure(lines: list[dict[str, Any]], statements: list[dict[str, Any]], view: list[Any], **text: Any) -> dict[str, Any]:
    relations = [tuple(int(v) for v in ln["line"]) for ln in lines]
    for rel in relations:
        if rel[0] == 0 and rel[1] == 0:
            raise ValueError("degenerate_boundary")
    corner = G.intersect(relations[0], relations[1])
    if corner is None:
        raise ValueError("boundaries_must_intersect")
    lo_x, hi_x, lo_y, hi_y = (fr(v) for v in view)
    if not (lo_x < corner[0] < hi_x and lo_y < corner[1] < hi_y):
        raise ValueError("corner_outside_view")
    probe = _find_interior_point(relations)
    if probe is None:
        raise ValueError("empty_region")
    # a region point inside the view is needed for the figure
    if not (lo_x < probe[0] < hi_x and lo_y < probe[1] < hi_y):
        raise ValueError("region_probe_outside_view")
    coefficient = {"a": relations[0][0], "b": relations[0][1], "c": relations[0][2], "d": relations[1][2]}
    truth = []
    for s in statements:
        value = coefficient[s["coef"]]
        truth.append(value > 0 if s["op"] == ">" else value < 0)
    return {
        "coefficients": coefficient,
        "truth": truth,
        "selected": _meaningful_selection([i for i, t in enumerate(truth, start=1) if t], len(truth)),
        "probe": [frac_text(probe[0]), frac_text(probe[1])],
        "corner": [frac_text(corner[0]), frac_text(corner[1])],
    }


def _check_read_region_signs_from_figure(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    # Independent: read each sign off the *picture* (region side), not off the coefficient list.
    relations = [[int(v) for v in ln["line"]] for ln in givens["lines"]]
    probe = _sp_point(answer["probe"])
    for rel in relations:
        if not bool(sp.Rational(rel[0]) * probe[0] + sp.Rational(rel[1]) * probe[1] + rel[2] > 0):
            return False
    first, second = relations
    def f(rel, p):  # noqa: E306
        return sp.Rational(rel[0]) * p[0] + sp.Rational(rel[1]) * p[1] + rel[2]
    signs = {
        "a": bool(f(first, (probe[0] + 1, probe[1])) > f(first, probe)) - bool(f(first, (probe[0] + 1, probe[1])) < f(first, probe)),
        "b": bool(f(first, (probe[0], probe[1] + 1)) > f(first, probe)) - bool(f(first, (probe[0], probe[1] + 1)) < f(first, probe)),
        "c": bool(f(first, (0, 0)) > 0) - bool(f(first, (0, 0)) < 0),
        "d": bool(f(second, (0, 0)) > 0) - bool(f(second, (0, 0)) < 0),
    }
    for statement, truth in zip(givens["statements"], answer["truth"]):
        sign = signs[statement["coef"]]
        independent = sign > 0 if statement["op"] == ">" else sign < 0
        if independent != truth:
            return False
    return answer["selected"] == [i for i, t in enumerate(answer["truth"], start=1) if t]


# --- 14. solve_region_coefficients_from_figure -----------------------------------------------------------------

def solve_region_coefficients_from_figure(a_point: list[Any], b_point: list[Any], bound: Any = 5, **text: Any) -> dict[str, Any]:
    (px, py), (rx, ry) = pt(a_point), pt(b_point)
    k = fr(bound)
    if ry != 0 or py <= 0 or rx <= 0 or k == 0:
        raise ValueError("region_needs_apex_above_axis_and_base_on_positive_x_axis")
    a_coef = -px / py
    b_coef = k / rx
    c_coef = (k - b_coef * px) / py
    return {"values": [_rational_rec(a_coef), _rational_rec(b_coef), _rational_rec(c_coef)], "bound": frac_text(k)}


def _check_solve_region_coefficients_from_figure(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    x, y = sp.symbols("x y")
    a, b, c = (sp.Rational(v["canonical"]) for v in answer["values"])
    k = sp.Rational(answer["bound"])
    ap, bp = _sp_point(givens["a_point"]), _sp_point(givens["b_point"])
    on_oa = ap[0] + a * ap[1] == 0 and 0 + a * 0 == 0
    on_ab = b * ap[0] + c * ap[1] == k and b * bp[0] + c * bp[1] == k
    # the region x + a y >= 0, b x + c y <= k, y >= 0 must be the triangle O, A, B
    centroid = ((ap[0] + bp[0]) / 3, (ap[1] + bp[1]) / 3)
    inside = bool(centroid[0] + a * centroid[1] > 0 and b * centroid[0] + c * centroid[1] < k and centroid[1] > 0)
    base_ok = bool(bp[0] + a * bp[1] >= 0 and b * 0 + c * 0 <= k)
    return bool(on_oa and on_ab and inside and base_ok)


# --- 15. evaluate_line_statement_truth ---------------------------------------------------------------------------

_SHAPES = ("rectangle", "parallelogram", "rhombus", "trapezoid", "kite")


def _shape_instances(shape: str) -> list[list[G.Point]]:
    """Concrete polygons (axis-aligned and tilted, vertical sides included) for universal claims."""
    out: list[list[G.Point]] = []
    F = Fraction
    if shape == "rectangle":
        out += [[(F(0), F(0)), (F(4), F(0)), (F(4), F(3)), (F(0), F(3))],
                [(F(0), F(0)), (F(3), F(4)), (F(-1), F(7)), (F(-4), F(3))],
                [(F(0), F(0)), (F(0), F(5)), (F(2), F(5)), (F(2), F(0))]]
    elif shape == "parallelogram":
        out += [[(F(0), F(0)), (F(4), F(0)), (F(5), F(3)), (F(1), F(3))],
                [(F(0), F(0)), (F(0), F(4)), (F(3), F(5)), (F(3), F(1))],
                [(F(0), F(0)), (F(3), F(1)), (F(5), F(4)), (F(2), F(3))]]
    elif shape == "rhombus":
        out += [[(F(0), F(0)), (F(3), F(4)), (F(8), F(4)), (F(5), F(0))],
                [(F(0), F(0)), (F(0), F(5)), (F(4), F(8)), (F(4), F(3))]]
    elif shape == "trapezoid":
        out += [[(F(0), F(0)), (F(0), F(6)), (F(3), F(5)), (F(3), F(1))],
                [(F(0), F(0)), (F(5), F(0)), (F(4), F(3)), (F(1), F(3))]]
    elif shape == "kite":
        out += [[(F(0), F(0)), (F(2), F(1)), (F(0), F(4)), (F(-2), F(1))]]
    else:
        raise ValueError(f"unknown_shape:{shape}")
    return out


def _side_slopes(polygon: list[G.Point]) -> list[Fraction | None]:
    out: list[Fraction | None] = []
    for i in range(len(polygon)):
        p, q = polygon[i], polygon[(i + 1) % len(polygon)]
        out.append(None if p[0] == q[0] else (q[1] - p[1]) / (q[0] - p[0]))
    return out


def _has_two_equal_slopes(polygon: list[G.Point]) -> bool:
    slopes = [s for s in _side_slopes(polygon) if s is not None]
    return len(slopes) != len(set(slopes))


def evaluate_line_statement_truth(statement: dict[str, Any], **text: Any) -> dict[str, Any]:
    kind = statement["kind"]
    if kind == "shape_equal_slopes":
        negated = bool(statement.get("negated", False))
        holds = [(not _has_two_equal_slopes(poly)) if negated else _has_two_equal_slopes(poly) for poly in _shape_instances(statement["shape"])]
        witness = next((poly for poly, ok in zip(_shape_instances(statement["shape"]), holds) if not ok), None)
        return {"truth": all(holds), "witness": [[frac_text(x), frac_text(y)] for x, y in witness] if witness else None}
    if kind == "y_intercept_of_line_through_point":
        k, claimed, slope_exists = fr(statement["through_y"]), fr(statement["claimed"]), bool(statement.get("slope_exists", False))
        # y-intercept is the y-coordinate where the line meets the y-axis; a vertical line through (0,k) has none
        truth = slope_exists and claimed == k
        return {"truth": truth}
    if kind == "perpendicular_by_coefficients":
        (a1, b1, _), (a2, b2, _) = (tuple(fr(v) for v in statement["l1"]), tuple(fr(v) for v in statement["l2"]))
        return {"truth": a1 * a2 + b1 * b2 == 0}
    if kind == "parallel_at_distance_count":
        d, count = fr(statement["distance"]), int(statement["claimed_count"])
        actual = 1 if d == 0 else 2
        return {"truth": count == actual, "actual_count": actual}
    if kind == "opposite_sides":
        line = G.norm_line(*statement["line"])
        va, vb = G.side_value(line, pt(statement["a"])), G.side_value(line, pt(statement["b"]))
        if va == 0 or vb == 0:
            raise ValueError("point_on_boundary_is_neither_side")
        return {"truth": (va > 0) != (vb > 0)}
    raise ValueError(f"unknown_statement_truth_kind:{kind}")


def _check_evaluate_line_statement_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    statement, truth = givens["statement"], answer["truth"]
    kind = statement["kind"]
    if kind == "shape_equal_slopes":
        # independent: direction vectors, treating vertical as slope-less
        def dirs(poly):  # noqa: E306
            out = []
            for i in range(len(poly)):
                p, q = _sp_point(poly[i]), _sp_point(poly[(i + 1) % len(poly)])
                out.append((q[0] - p[0], q[1] - p[1]))
            return out
        def equal_pair(poly):  # noqa: E306
            d = [v for v in dirs(poly) if v[0] != 0]
            return any(d[i][1] / d[i][0] == d[j][1] / d[j][0] for i in range(len(d)) for j in range(i + 1, len(d)))
        negated = bool(statement.get("negated", False))
        independent = all((not equal_pair(poly)) if negated else equal_pair(poly) for poly in _shape_instances(statement["shape"]))
        return independent == truth
    if kind == "y_intercept_of_line_through_point":
        k, claimed = _sr(statement["through_y"]), _sr(statement["claimed"])
        independent = bool(statement.get("slope_exists", False)) and sp.simplify(claimed - k) == 0
        return independent == truth
    if kind == "perpendicular_by_coefficients":
        x, y = sp.symbols("x y")
        l1, l2 = statement["l1"], statement["l2"]
        if l1[1] == 0 or l2[1] == 0:
            independent = bool(sp.Rational(l1[0]) * l2[0] + sp.Rational(l1[1]) * l2[1] == 0)
        else:
            independent = bool(sp.simplify((-_sr(l1[0]) / _sr(l1[1])) * (-_sr(l2[0]) / _sr(l2[1])) + 1) == 0)
        return independent == truth
    if kind == "parallel_at_distance_count":
        d, claimed = _sr(statement["distance"]), int(statement["claimed_count"])
        # lines ax+by+c' with |c'-c| = d*sqrt(a^2+b^2): one equation |t| = r has 2 solutions iff r > 0
        independent_count = len(sp.solve(sp.Abs(sp.Symbol("t", real=True)) - d, sp.Symbol("t", real=True)))
        return (claimed == independent_count) == truth and (answer.get("actual_count") in (None, independent_count))
    if kind == "opposite_sides":
        line = [sp.Integer(v) for v in G.norm_line(*statement["line"])]
        values = []
        for key in ("a", "b"):
            p = _sp_point(statement[key])
            values.append(line[0] * p[0] + line[1] * p[1] + line[2])
        # opposite sides iff the segment AB crosses the line at an interior parameter
        t = sp.Symbol("t", real=True)
        a_p, b_p = _sp_point(statement["a"]), _sp_point(statement["b"])
        cross = sp.solve(line[0] * (a_p[0] + t * (b_p[0] - a_p[0])) + line[1] * (a_p[1] + t * (b_p[1] - a_p[1])) + line[2], t)
        independent = bool(cross) and 0 < cross[0] < 1
        return independent == truth
    return False


# --- 16. select_points_same_side ----------------------------------------------------------------------------------

def select_points_same_side(line: list[Any], reference: list[Any], points: list[list[Any]], **text: Any) -> dict[str, Any]:
    ln = G.norm_line(*line)
    ref = G.side_value(ln, pt(reference))
    if ref == 0:
        raise ValueError("reference_point_on_line")
    selected, sides = [], []
    for index, p in enumerate(points, start=1):
        v = G.side_value(ln, pt(p))
        sides.append(0 if v == 0 else (1 if (v > 0) == (ref > 0) else -1))
        if sides[-1] == 1:
            selected.append(index)
    return {"selected": _meaningful_selection(selected, len(points)), "sides": sides}


def _check_select_points_same_side(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, b, c = (sp.Integer(v) for v in G.norm_line(*givens["line"]))
    ref = _sp_point(givens["reference"])
    t = sp.Symbol("t", real=True)
    selected = []
    for index, raw in enumerate(givens["points"], start=1):
        p = _sp_point(raw)
        if a * p[0] + b * p[1] + c == 0:
            continue
        # same half-plane iff the segment to the reference point never meets the line
        cross = sp.solve(a * (ref[0] + t * (p[0] - ref[0])) + b * (ref[1] + t * (p[1] - ref[1])) + c, t)
        if not cross or not (0 <= cross[0] <= 1):
            selected.append(index)
    return selected == answer["selected"]


# --- 17. graph_inequality_system ---------------------------------------------------------------------------------------

def _clip_region(relations: list[dict[str, Any]], view: tuple[Fraction, Fraction, Fraction, Fraction]) -> list[G.Point]:
    lo_x, hi_x, lo_y, hi_y = view
    polygon: list[G.Point] = [(lo_x, lo_y), (hi_x, lo_y), (hi_x, hi_y), (lo_x, hi_y)]
    for rel in relations:
        a, b, c = rel["line"]
        clipped: list[G.Point] = []
        for i in range(len(polygon)):
            cur, prev = polygon[i], polygon[i - 1]
            vc, vp = a * cur[0] + b * cur[1] + c, a * prev[0] + b * prev[1] + c
            if vc >= 0:
                if vp < 0:
                    t = vp / (vp - vc)
                    clipped.append((prev[0] + (cur[0] - prev[0]) * t, prev[1] + (cur[1] - prev[1]) * t))
                clipped.append(cur)
            elif vp >= 0:
                t = vp / (vp - vc)
                clipped.append((prev[0] + (cur[0] - prev[0]) * t, prev[1] + (cur[1] - prev[1]) * t))
        polygon = clipped
        if not polygon:
            break
    return polygon


def _has_drawable_core(rels: list[dict[str, Any]], view: tuple[Fraction, Fraction, Fraction, Fraction]) -> bool:
    """A student must be able to shade it: some half-unit grid point lies >= 0.75 inside every boundary."""
    lo_x, hi_x, lo_y, hi_y = view
    margin = Fraction(3, 4)
    for ix in range(int(lo_x * 2) + 1, int(hi_x * 2)):
        for iy in range(int(lo_y * 2) + 1, int(hi_y * 2)):
            x, y = Fraction(ix, 2), Fraction(iy, 2)
            if all(rel["line"][0] * x + rel["line"][1] * y + rel["line"][2] >= margin * G.sqrt_radical(rel["line"][0] ** 2 + rel["line"][1] ** 2).value() for rel in rels):
                return True
    return False


def graph_inequality_system(relations: list[dict[str, Any]], view: list[Any], **text: Any) -> dict[str, Any]:
    view_t = tuple(fr(v) for v in view)
    rels = []
    for rel in relations:
        a, b, c = (fr(v) for v in rel["coefficients"])
        norm = G.norm_line(a, b, c)
        sign = 1
        # keep the half-plane the same after normalising the line to canonical sign
        scale = fr(norm[0]) / a if a != 0 else fr(norm[1]) / b
        sign = 1 if scale > 0 else -1
        # original: a x + b y + c  (op) 0 ; normalised = scale * original
        op = rel["op"]
        if sign < 0:
            op = {">=": "<=", ">": "<", "<=": ">=", "<": ">"}[op]
        if op in {"<=", "<"}:
            norm = tuple(-v for v in norm)
            op = {"<=": ">=", "<": ">"}[op]
        rels.append({"line": list(norm), "op": op, "boundary": "solid" if op == ">=" else "dashed"})
    polygon = _clip_region(rels, view_t)
    if len(polygon) < 3:
        raise ValueError("empty_region_in_view")
    if not _has_drawable_core(rels, view_t):
        raise ValueError("region_too_thin_to_draw")
    probe = (sum(p[0] for p in polygon) / len(polygon), sum(p[1] for p in polygon) / len(polygon))
    corner = None
    if len(rels) >= 2:
        corner = G.intersect(tuple(rels[0]["line"]), tuple(rels[1]["line"]))
    strict_all = [r for r in rels if r["boundary"] == "dashed"]
    return {
        "relations": rels,
        "region_polygon": [[frac_text(x), frac_text(y)] for x, y in polygon],
        "probe": [frac_text(probe[0]), frac_text(probe[1])],
        "corner": None if corner is None else [frac_text(corner[0]), frac_text(corner[1])],
        "corner_excluded": bool(strict_all),
        "view": [frac_text(v) for v in view_t],
    }


def _check_graph_inequality_system(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    view = [sp.Rational(v) for v in answer["view"]]
    originals = []
    for rel in givens["relations"]:
        a, b, c = (_sr(v) for v in rel["coefficients"])
        originals.append((a, b, c, rel["op"]))

    def satisfies(x, y) -> bool:  # noqa: E306
        for a, b, c, op in originals:
            v = a * x + b * y + c
            if op == ">=" and not v >= 0 or op == ">" and not v > 0 or op == "<=" and not v <= 0 or op == "<" and not v < 0:
                return False
        return True

    polygon = [(sp.Rational(x), sp.Rational(y)) for x, y in answer["region_polygon"]]
    # Independent: dense grid membership must match the clipped polygon's interior (strict interior points only).
    steps = 12
    for i in range(steps + 1):
        for j in range(steps + 1):
            x = view[0] + (view[1] - view[0]) * i / steps
            y = view[2] + (view[3] - view[2]) * j / steps
            inside = _point_in_polygon_strict((x, y), polygon)
            on_boundary = any(a * x + b * y + c == 0 for a, b, c, _ in originals)
            if on_boundary:
                continue
            if inside != satisfies(x, y) and not _on_polygon_edge((x, y), polygon):
                return False
    probe = (sp.Rational(answer["probe"][0]), sp.Rational(answer["probe"][1]))
    if not satisfies(*probe):
        return False
    for rel, record in zip(originals, answer["relations"]):
        if (record["boundary"] == "solid") != (rel[3] in (">=", "<=")):
            return False
    return True


def _point_in_polygon_strict(p: Any, polygon: list[Any]) -> bool:
    x, y = p
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            cross = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if cross > x:
                inside = not inside
    return bool(inside)


def _on_polygon_edge(p: Any, polygon: list[Any]) -> bool:
    x, y = p
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) == 0 and min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return True
    return False


# --- 18. solve_rectangle_perpendicular_diagonals ----------------------------------------------------------------------------

def solve_rectangle_perpendicular_diagonals(ab: Any, bf: Any, **text: Any) -> dict[str, Any]:
    h, w = fr(ab), fr(bf)
    if h <= 0 or w <= 0:
        raise ValueError("positive_lengths_required")
    # B=(0,0), D=(w+a,h), C=(w+a,0), E=(w,h): BD ⟂ CE  <=>  a^2 + w a - h^2 = 0
    disc = w * w + 4 * h * h
    if disc.denominator != 1:
        raise ValueError("integer_discriminant_required")
    root = G.sqrt_radical(int(disc))
    # a = (-w + sqrt(disc)) / 2 = (-w)/2 + (coef/2) sqrt(t)
    rational_part = -w / 2
    radical_coef = root.coef / 2
    if root.radicand == 1:
        value = Radical(rational_part + radical_coef, 1)
        canonical, latex = value.canonical(), value.latex()
    else:
        canonical = f"{frac_text(rational_part)}+{Radical(radical_coef, root.radicand).canonical()}" if rational_part else Radical(radical_coef, root.radicand).canonical()
        rad_latex = Radical(radical_coef, root.radicand).latex()
        latex = (f"{frac_text(rational_part)}+{rad_latex}" if rational_part else rad_latex).replace("+-", "-")
        canonical = canonical.replace("+-", "-")
    return {
        "values": [{"kind": "radical" if root.radicand != 1 else "rational", "canonical": canonical, "latex": latex,
                    "rational_part": frac_text(rational_part), "coef": frac_text(radical_coef), "radicand": root.radicand}],
    }


def _check_solve_rectangle_perpendicular_diagonals(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    h, w = _sr(givens["ab"]), _sr(givens["bf"])
    record = answer["values"][0]
    a = sp.Rational(record["rational_part"]) + sp.Rational(record["coef"]) * sp.sqrt(record["radicand"])
    # vectors BD and CE must be perpendicular for CF = a, and a must be positive
    bd = (w + a, h)
    ce = (w - (w + a), h)
    return bool(a > 0) and sp.simplify(bd[0] * ce[0] + bd[1] * ce[1]) == 0


# --- 19. solve_axis_triangle_area_line ----------------------------------------------------------------------------------------

def solve_axis_triangle_area_line(point: list[Any], area: Any, **text: Any) -> dict[str, Any]:
    px, py = pt(point)
    s = fr(area)
    if px == 0 or py == 0 or s <= 0:
        raise ValueError("point_off_axes_and_positive_area_required")
    lines: set[G.Line] = set()
    # x/a + y/b = 1 through P, |a b| = 2S.   Substitute b = ±2S/a: px/a + py/b = 1.
    for sign in (1, -1):
        # a*b = sign*2S  ->  b = sign*2S/a;  px/a + py*a/(sign*2S) = 1  ->  (py/(sign 2S)) a^2 - a + px = 0
        qa, qb, qc = py / (sign * 2 * s), Fraction(-1), px
        disc = qb * qb - 4 * qa * qc
        if disc < 0:
            continue
        num, den = disc.numerator, disc.denominator
        rn, rd = isqrt(num), isqrt(den)
        if rn * rn != num or rd * rd != den:
            raise ValueError("irrational_intercepts")
        root = Fraction(rn, rd)
        for a in {(-qb + root) / (2 * qa), (-qb - root) / (2 * qa)}:
            if a == 0:
                continue
            b = sign * 2 * s / a
            if b == 0:
                continue
            lines.add(G.line_from_intercepts(a, b))
    ordered = sorted(lines)
    if not ordered:
        raise ValueError("no_such_line")
    return {"values": [_line_rec(line) for line in ordered], "count": len(ordered)}


def _check_solve_axis_triangle_area_line(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    px, py = _sp_point(givens["point"])
    s = _sr(givens["area"])
    seen = set()
    for record in answer["values"]:
        a_, b_, c_ = (sp.Integer(v) for v in record["line"])
        if a_ == 0 or b_ == 0 or c_ == 0:
            return False
        if a_ * px + b_ * py + c_ != 0:
            return False
        x_int, y_int = -c_ / a_, -c_ / b_
        if sp.simplify(sp.Abs(x_int * y_int) / 2 - s) != 0:
            return False
        seen.add(tuple(record["line"]))
    # exhaustive independent search over rational intercept pairs with small denominators
    found = set()
    for a_num, a_den in product(range(-60, 61), (1, 2, 4)):
        if a_num == 0:
            continue
        a = sp.Rational(a_num, a_den)
        for sign in (1, -1):
            b = sign * 2 * s / a
            if px / a + py / b == 1:
                found.add(tuple(G.line_from_intercepts(fr(str(a)), fr(str(b)))))
    return found <= seen and len(seen) == len(answer["values"]) == answer["count"]


# --- 20. solve_parallel_line_family -------------------------------------------------------------------------------------------

def solve_parallel_line_family(a_point: list[Any], b_point: list[Any], p_point: list[Any], spacing: Any, **text: Any) -> dict[str, Any]:
    base = G.line_through(pt(a_point), pt(b_point))
    p = pt(p_point)
    d = G.distance_point_line(p, base)
    sp_ = fr(spacing)
    if not d.is_rational():
        raise ValueError("rational_distance_required")
    distance = d.coef
    index = int(distance // sp_) + 1  # P strictly between L_{n-1} and L_n
    if distance % sp_ == 0:
        raise ValueError("point_must_not_lie_on_a_family_line")
    norm = Fraction(base[0] ** 2 + base[1] ** 2)
    root = G.sqrt_radical(int(norm))
    if not root.is_rational():
        raise ValueError("rational_normal_length_required")
    sign = 1 if G.side_value(base, p) > 0 else -1
    shift = sign * index * sp_ * root.coef
    line_n = G.norm_line(base[0], base[1], Fraction(base[2]) - shift)
    return {"values": [_rational_rec(distance), _rational_rec(Fraction(index)), _line_rec(line_n)]}


def _check_solve_parallel_line_family(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ap, bp, pp = (_sp_point(givens[k]) for k in ("a_point", "b_point", "p_point"))
    s = _sr(givens["spacing"])
    distance = sp.Rational(answer["values"][0]["canonical"])
    n = int(answer["values"][1]["canonical"])
    line = [sp.Integer(v) for v in answer["values"][2]["line"]]
    # distance via the area of triangle ABP: dist = 2*area/|AB|
    ab = sp.sqrt((bp[0] - ap[0]) ** 2 + (bp[1] - ap[1]) ** 2)
    if sp.simplify(2 * _sp_area(ap, bp, pp) / ab - distance) != 0:
        return False
    if not (s * (n - 1) < distance < s * n):
        return False
    # L_n is parallel to AB, lies s*n from AB, and P is strictly between L_{n-1} and L_n  (P is on the AB side of L_n)
    base_dir = (bp[0] - ap[0], bp[1] - ap[1])
    if sp.simplify(line[0] * base_dir[0] + line[1] * base_dir[1]) != 0:
        return False
    sample = ap
    dist_to_ln = sp.Abs(line[0] * sample[0] + line[1] * sample[1] + line[2]) / sp.sqrt(line[0] ** 2 + line[1] ** 2)
    if sp.simplify(dist_to_ln - s * n) != 0:
        return False
    side_p = line[0] * pp[0] + line[1] * pp[1] + line[2]
    side_ab = line[0] * ap[0] + line[1] * ap[1] + line[2]
    return bool(side_p * side_ab > 0)


# --- operation table ---------------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "rank_line_slopes": (rank_line_slopes, _check_rank_line_slopes, ("lines",)),
    "evaluate_slope_sign_statements": (evaluate_slope_sign_statements, _check_evaluate_slope_sign_statements, ("points", "segments", "statements")),
    "solve_line_equations": (solve_line_equations, _check_solve_line_equations, ("items",)),
    "slope_of_line_from_equation": (slope_of_line_from_equation, _check_slope_of_line_from_equation, ("line",)),
    "fill_line_property_table": (fill_line_property_table, _check_fill_line_property_table, ("rows",)),
    "translate_line_equation": (translate_line_equation, _check_translate_line_equation, ("line", "dx", "dy")),
    "solve_translation_parameter": (solve_translation_parameter, _check_solve_translation_parameter, ("line", "result_line")),
    "solve_line_constructions": (solve_line_constructions, _check_solve_line_constructions, ("items",)),
    "solve_line_parameters": (solve_line_parameters, _check_solve_line_parameters, ("unknowns", "lines", "conditions", "targets")),
    "compute_line_distances": (compute_line_distances, _check_compute_line_distances, ("items",)),
    "solve_window_decorative_lines": (solve_window_decorative_lines, _check_solve_window_decorative_lines, ("width", "height", "edge_point", "delta_c", "asks")),
    "solve_triangle_region_system": (solve_triangle_region_system, _check_solve_triangle_region_system, ("vertices", "choice_points", "family_point")),
    "read_region_signs_from_figure": (read_region_signs_from_figure, _check_read_region_signs_from_figure, ("lines", "statements", "view")),
    "solve_region_coefficients_from_figure": (solve_region_coefficients_from_figure, _check_solve_region_coefficients_from_figure, ("a_point", "b_point")),
    "evaluate_line_statement_truth": (evaluate_line_statement_truth, _check_evaluate_line_statement_truth, ("statement",)),
    "select_points_same_side": (select_points_same_side, _check_select_points_same_side, ("line", "reference", "points")),
    "graph_inequality_system": (graph_inequality_system, _check_graph_inequality_system, ("relations", "view")),
    "solve_rectangle_perpendicular_diagonals": (solve_rectangle_perpendicular_diagonals, _check_solve_rectangle_perpendicular_diagonals, ("ab", "bf")),
    "solve_axis_triangle_area_line": (solve_axis_triangle_area_line, _check_solve_axis_triangle_area_line, ("point", "area")),
    "solve_parallel_line_family": (solve_parallel_line_family, _check_solve_parallel_line_family, ("a_point", "b_point", "p_point", "spacing")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_line_equations_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_line_equations_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k not in ("skill_id",)}
    _require(givens, *required)
    answer = solve(**givens)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": answer,
        "validation_facts": {"domain_operation": operation, "seed": 0 if seed is None else int(seed)},
    }


# --- validators (never raise) -------------------------------------------------------------------------------------------------------

def _make_validator(operation: str) -> Callable[[Any], bool]:
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if (
                matrix.get("domain") != DOMAIN_KEY
                or matrix.get("domain_operation") != operation
                or facts.get("domain_operation") != operation
            ):
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
