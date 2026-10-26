"""Recurrence-relation operations of ``sequence.progression`` (普高數學2 Unit 1, 遞迴關係式).

Part of the same reviewed package as ``sequence_progression_domain``.  Components pass the stated data of a stem; every
answer is derived here, and each operation has an independent validator that rebuilds the situation explicitly
(counting pieces step by step, tearing sheets one at a time, writing the rows of a number array, constructing the
midpoint polygons with exact coordinates) instead of reusing the closed form that produced the answer.

The recurrence itself is answered as the missing pieces of a template (a first term and one increment / ratio), because
no shared checker can grade a free-form recurrence equation soundly.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import sympy as sp

from .sequence_progression_domain import num, text

_N = sp.Symbol("n")


def _expr_text(e: sp.Expr) -> str:
    return sp.sstr(sp.expand(e)).replace(" ", "")


# --- process families --------------------------------------------------------------------------------------------

def recurrence_from_process(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "subdivision":  # every white piece splits into ``parts`` pieces of which ``removed`` are blackened / deleted
        parts, removed, a1 = int(g["parts"]), int(g["removed"]), int(g.get("a1", 1))
        ratio = parts - removed
        if not (parts > removed >= 1 and ratio >= 2 and a1 >= 1):
            raise ValueError("subdivision_needs_growth")
        out: dict[str, Any] = {"kind": kind, "a1": str(a1), "ratio": str(ratio), "ask": g["ask"]}
        if g["ask"] == "value":
            k = int(g["k"])
            out.update(k=k, a_k=str(a1 * ratio ** (k - 1)))
        elif g["ask"] == "threshold":
            limit = int(g["limit"])
            n = next(i for i in range(1, 80) if a1 * ratio ** (i - 1) > limit)
            out.update(limit=limit, first_n=n)
        else:
            raise ValueError("unsupported_subdivision_question")
        return out
    if kind == "tearing":  # ``start`` sheets, each operation turns one sheet into ``pieces`` sheets
        start, pieces, k, target = int(g["start"]), int(g["pieces"]), int(g["k"]), int(g["target"])
        d = pieces - 1
        if d < 1 or (target - start) % d or target <= start:
            raise ValueError("target_must_be_reachable")
        return {"kind": kind, "start": str(start), "d": str(d), "k": k, "a_k": str(start + k * d), "target": target, "n": (target - start) // d}
    if kind == "row_sums":  # rows hold first, first+step, first+2*step, ... people; a_n = people in the first n rows
        first, step, k = int(g["first"]), int(g["step"]), int(g["k"])
        if first < 1 or step < 1:
            raise ValueError("positive_rows_required")
        totals = [sum(first + i * step for i in range(n)) for n in range(1, max(k, 4) + 1)]
        return {"kind": kind, "first_terms": [str(t) for t in totals[:4]], "increment": _expr_text(step * _N + (first - step)),
                "k": k, "a_k": str(totals[k - 1])}
    if kind == "array_row_end":  # consecutive integers from ``start`` fill rows of length first_row, first_row+1, ...
        start, first_row, k = int(g["start"]), int(g["first_row"]), int(g["k"])
        if first_row < 1 or start < 1 or k < 4:
            raise ValueError("array_parameters_invalid")
        ends, last = [], start - 1
        for n in range(1, k + 1):
            last += first_row + n - 1
            ends.append(last)
        return {"kind": kind, "shown_terms": [str(v) for v in ends[:3]], "increment": _expr_text(_N + (first_row - 1)),
                "k": k, "a_k": str(ends[k - 1])}
    if kind == "nested_polygon":  # midpoints of a regular polygon's sides span the next one; a_n = perimeter of T_n
        shape, P, k = g["shape"], num(g["P"]), int(g["k"])
        if shape not in ("square", "triangle") or P <= 0 or k < 3:
            raise ValueError("nested_polygon_parameters_invalid")
        ratio = sp.sqrt(2) / 2 if shape == "square" else sp.Rational(1, 2)
        return {"kind": kind, "ratio": text(ratio), "k": k, "a_k": text(P * ratio ** (k - 1))}
    raise ValueError(f"unsupported_recurrence_process:{kind}")


def _perimeter(points: list[tuple[sp.Expr, sp.Expr]]) -> sp.Expr:
    total = sp.Integer(0)
    for i, (x0, y0) in enumerate(points):
        x1, y1 = points[(i + 1) % len(points)]
        total += sp.sqrt(sp.simplify((x1 - x0) ** 2 + (y1 - y0) ** 2))
    return sp.radsimp(sp.simplify(total))


def check_recurrence_from_process(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = answer["kind"]
    if kind == "subdivision":
        parts, removed = int(givens["parts"]), int(givens["removed"])
        white, history = int(givens.get("a1", 1)), []
        for _ in range(40):  # split every white piece into ``parts`` pieces, then blacken ``removed`` per old piece, recount
            history.append(white)
            white = white * parts - white * removed
        if str(history[0]) != answer["a1"] or history[1] != history[0] * int(answer["ratio"]) or history[2] != history[1] * int(answer["ratio"]):
            return False
        if answer["ask"] == "value":
            return history[answer["k"] - 1] == int(answer["a_k"])
        first = next(i + 1 for i, v in enumerate(history) if v > int(givens["limit"]))
        return first == answer["first_n"] and (first == 1 or history[first - 2] <= int(givens["limit"]))
    if kind == "tearing":
        sheets, counts = int(givens["start"]), [int(givens["start"])]
        for _ in range(int(answer["n"]) + 5):  # tear one sheet at a time
            sheets = sheets - 1 + int(givens["pieces"])
            counts.append(sheets)
        return (str(counts[0]) == answer["start"] and counts[answer["k"]] == int(answer["a_k"]) and counts[answer["n"]] == int(givens["target"])
                and int(givens["target"]) not in counts[:answer["n"]] and counts[1] - counts[0] == int(answer["d"]))
    if kind == "row_sums":
        rows = [[1] * (int(givens["first"]) + i * int(givens["step"])) for i in range(max(int(answer["k"]), 4))]  # one entry per person
        running = [sum(len(r) for r in rows[: n + 1]) for n in range(len(rows))]
        inc = sp.sympify(answer["increment"])
        return ([str(v) for v in running[:4]] == answer["first_terms"] and str(running[answer["k"] - 1]) == answer["a_k"]
                and all(len(rows[n - 1]) == inc.subs(sp.Symbol("n"), n) for n in range(1, len(rows) + 1)))
    if kind == "array_row_end":
        start, first_row = int(givens["start"]), int(givens["first_row"])
        numbers = iter(range(start, start + 10_000))
        rows = [[next(numbers) for _ in range(first_row + i)] for i in range(int(answer["k"]))]  # write the array out
        inc = sp.sympify(answer["increment"])
        ends = [r[-1] for r in rows]
        return ([str(v) for v in ends[:3]] == answer["shown_terms"] and str(ends[-1]) == answer["a_k"]
                and all(ends[n - 1] - ends[n - 2] == inc.subs(sp.Symbol("n"), n) for n in range(2, len(ends) + 1)))
    P, k = num(givens["P"]), int(answer["k"])
    if givens["shape"] == "square":  # exact coordinates, repeated midpoint construction
        s = P / 4
        pts = [(sp.Integer(0), sp.Integer(0)), (s, sp.Integer(0)), (s, s), (sp.Integer(0), s)]
    else:
        s = P / 3
        pts = [(sp.Integer(0), sp.Integer(0)), (s, sp.Integer(0)), (s / 2, s * sp.sqrt(3) / 2)]
    perimeters = []
    for _ in range(k):
        perimeters.append(_perimeter(pts))
        pts = [((pts[i][0] + pts[(i + 1) % len(pts)][0]) / 2, (pts[i][1] + pts[(i + 1) % len(pts)][1]) / 2) for i in range(len(pts))]
    return (sp.simplify(perimeters[-1] - num(answer["a_k"])) == 0
            and sp.simplify(perimeters[1] - num(answer["ratio"]) * perimeters[0]) == 0 and sp.simplify(perimeters[0] - P) == 0)


# --- geometric numbers with a sum relation (the 'perfect thumb' problem) ---------------------------------------------

def geo_sum_relation(c: Any, **_: Any) -> dict[str, Any]:
    """Positive geometric a1, a2, a3 with a3 = a2 + c*a1: the positive root of r^2 - r - c = 0."""
    c = num(c)
    if c <= 0:
        raise ValueError("positive_coefficient_required")
    r = sp.Symbol("r", positive=True)
    roots = [x for x in sp.solve(r ** 2 - r - c, r) if x.is_real and x > 0]
    if len(roots) != 1:
        raise ValueError("unique_positive_ratio_required")
    return {"kind": "geo_sum_relation", "ratio": text(roots[0])}


def check_geo_sum_relation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    c, r = num(givens["c"]), num(answer["ratio"])
    a1, a2, a3 = sp.Integer(1), r, r * r  # the ratio does not depend on the scale of a1
    return bool(r > 0 and sp.simplify(a3 - (a2 + c * a1)) == 0 and sp.simplify(a2 * a2 - a1 * a3) == 0
                and sp.simplify((1 - sp.sqrt(1 + 4 * c)) / 2) <= 0)  # the other root is not positive


# --- ○× on a stated recurrence ----------------------------------------------------------------------------------------

def recurrence_term_claim(st: dict[str, Any]) -> dict[str, Any]:
    """The statement 'recurrence a1=A, a_n = r a_{n-1} (or a_{n-1}+d) gives a_k = V'."""
    value = num(st["a1"])
    for _ in range(int(st["k"]) - 1):
        value = value * num(st["c"]) if st["type"] == "geometric" else value + num(st["c"])
    return {"truth": bool(sp.simplify(value - num(st["value"])) == 0), "actual": text(value)}


def check_recurrence_term_claim(st: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, c, steps = Fraction(str(st["a1"])), Fraction(str(st["c"])), int(st["k"]) - 1
    actual = a * c ** steps if st["type"] == "geometric" else a + c * steps
    return Fraction(answer["actual"]) == actual and answer["truth"] == (actual == Fraction(str(st["value"])))
