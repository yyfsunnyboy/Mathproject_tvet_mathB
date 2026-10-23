"""Per-component *inputs* for 普高數學1 Unit 7 (圓與直線的關係).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the
same shape.  Samplers only choose inputs (they may construct inputs that make exact answers
possible, e.g. lattice tangency); the domain computes every answer and rejects degenerate inputs.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import isqrt
from typing import Any

SKILLS = {
    "judge": "gh_JudgingTheRelationshipOfCircleAndLine",
    "tangent": "gh_TangentLinesOfACircle",
}

# 教材題目中無法落入正式作答契約的題目（記錄原因，不進 wrapper）
DEFERRED: dict[int, str] = {}

OP = {name: name for name in (
    "classify_circle_line_relations", "solve_circle_line_parameter", "write_circle_tangent_lines",
    "solve_chord_and_distance", "solve_circle_from_tangent_point", "evaluate_circle_line_statement_truth",
    "solve_circle_tangent_scenarios",
)}

SKILL_OPERATIONS = {
    "judge": ["classify_circle_line_relations", "solve_circle_line_parameter", "write_circle_tangent_lines",
              "solve_chord_and_distance", "evaluate_circle_line_statement_truth"],
    "tangent": ["write_circle_tangent_lines", "solve_circle_from_tangent_point", "evaluate_circle_line_statement_truth",
                "solve_circle_line_parameter", "solve_circle_tangent_scenarios"],
}

# Single-surface components (the source statement has no numeric givens to vary).
STATIC_COMPONENTS = {12491: "concept statement without numeric givens"}


# --- helpers -----------------------------------------------------------------------------------------

def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def is_square(n: int) -> bool:
    return n >= 0 and isqrt(n) ** 2 == n


def lattice_offsets(r2: int) -> list[tuple[int, int]]:
    r = isqrt(r2) + 1
    return [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy == r2]


def std(h: int, k: int, r2: int) -> dict[str, Any]:
    return {"center": [h, k], "r2": r2}


def general(h: int, k: int, r2: int) -> dict[str, Any]:
    return {"d": -2 * h, "e": -2 * k, "f": h * h + k * k - r2}


def norm_ints(a: int, b: int, c: int) -> list[int]:
    from math import gcd
    g = gcd(gcd(abs(a), abs(b)), abs(c)) or 1
    a, b, c = a // g, b // g, c // g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return [a, b, c]


def line_through(p: tuple[int, int], q: tuple[int, int]) -> list[int]:
    (x1, y1), (x2, y2) = p, q
    return norm_ints(y2 - y1, x1 - x2, x2 * y1 - x1 * y2)


PYTH_NORMALS = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (6, 8, 10), (8, 6, 10)]
LATTICE_R2 = [5, 10, 13, 17, 20, 25, 26, 29, 34, 50]
RELATION_WEIGHTS = ["secant"] * 7 + ["tangent"] * 2 + ["disjoint"]


def signed_normal(rng: random.Random) -> tuple[int, int, int]:
    a, b, n = pick(rng, PYTH_NORMALS)
    return a, pick(rng, [b, -b]), n


def line_at_distance(rng: random.Random, h: int, k: int, dist: int) -> list[int]:
    """Integer line with a Pythagorean normal whose distance to (h, k) is exactly ``dist``."""
    a, b, n = signed_normal(rng)
    c = -(a * h + b * k) + pick(rng, [1, -1]) * dist * n
    return norm_ints(a, b, c)


def relation_line(rng: random.Random, h: int, k: int, r2: int, kind: str) -> list[int] | None:
    """A line of the requested relation whose common points (if any) are lattice points."""
    offs = [o for o in lattice_offsets(r2)]
    if kind == "secant":
        p, q = rng.sample(offs, 2)
        if p[0] == q[0]:
            return None
        return line_through((h + p[0], k + p[1]), (h + q[0], k + q[1]))
    if kind == "tangent":
        u, v = pick(rng, offs)
        x0, y0 = h + u, k + v
        return norm_ints(u, v, -(u * x0 + v * y0))
    a, b = nz(rng, -4, 4), nz(rng, -4, 4)
    sigma_min = isqrt(r2 * (a * a + b * b)) + 1
    sigma = pick(rng, [1, -1]) * (sigma_min + rng.randint(0, 6))
    return norm_ints(a, b, sigma - a * h - b * k)


# --- 1. classify_circle_line_relations -----------------------------------------------------------------

v12481 = {"circle": std(0, 0, 5), "lines": [[1, -1, 1]], "ask_points": True, "style": "given_pair"}


def s12481(rng):
    r2 = pick(rng, LATTICE_R2)
    line = relation_line(rng, 0, 0, r2, pick(rng, RELATION_WEIGHTS))
    if line is None:
        raise ValueError("retry")
    return {"circle": std(0, 0, r2), "lines": [line], "ask_points": True, "style": "given_pair"}


v12483 = {"circle": std(1, -2, 9), "lines": [[12, 5, 11], [4, -3, 5]]}


def s12483(rng):
    h, k, r = rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(2, 6)
    kinds = rng.sample(["secant", "tangent", "disjoint"], 2)
    dists = {"secant": rng.randint(0, r - 1), "tangent": r, "disjoint": r + rng.randint(1, 3)}
    return {"circle": std(h, k, r * r), "lines": [line_at_distance(rng, h, k, dists[kd]) for kd in kinds]}


v12486 = {"circle": std(0, 1, 8), "lines": [[1, 1, -5], [1, 1, -6]], "ask_points": True}


def s12486(rng):
    """Two parallel lines with normal (1, +-1): r2 = 2 t^2 keeps tangency / chord points rational."""
    h, k, t = rng.randint(-3, 3), rng.randint(-3, 3), pick(rng, [1, 2, 3, 5])
    a, b = 1, pick(rng, [1, -1])
    n = 2
    kinds = rng.sample(["secant", "tangent", "disjoint"], 2)
    sign = pick(rng, [1, -1])
    sigmas = []
    for kd in kinds:
        if kd == "tangent":
            sigmas.append(sign * n * t)
        elif kd == "disjoint":
            sigmas.append(sign * (n * t + rng.randint(1, 3)))
        else:
            sigmas.append(sign * n * pick(rng, [0, 3, 4] if t == 5 else [0]))
    if sigmas[0] == sigmas[1]:
        raise ValueError("retry")
    lines = [norm_ints(a, b, s - a * h - b * k) for s in sigmas]
    return {"circle": std(h, k, n * t * t), "lines": lines, "ask_points": True}


v12488 = {"circle": std(2, 3, 16), "lines": [[3, 4, 7]], "show_r": True}


def s12488(rng):
    h, k, r = rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(2, 7)
    kind = pick(rng, ["secant", "tangent", "disjoint"])
    dist = {"secant": rng.randint(0, r - 1), "tangent": r, "disjoint": r + rng.randint(1, 3)}[kind]
    return {"circle": std(h, k, r * r), "lines": [line_at_distance(rng, h, k, dist)], "show_r": True}


v12495 = {"circle": std(-1, 0, 20), "lines": [[3, 1, -7]], "ask_points": True, "line_form": "rhs"}


def s12495(rng):
    h, k, r2 = rng.randint(-3, 3), rng.randint(-3, 3), pick(rng, LATTICE_R2)
    line = relation_line(rng, h, k, r2, pick(rng, RELATION_WEIGHTS))
    if line is None:
        raise ValueError("retry")
    return {"circle": std(h, k, r2), "lines": [line], "ask_points": True, "line_form": "rhs"}


v12497 = {"circle": std(1, -2, 13), "lines": [[2, 3, -10]], "style": "three_cases"}


def s12497(rng):
    h, k = rng.randint(-4, 4), rng.randint(-4, 4)
    a, b = nz(rng, -4, 4), nz(rng, -4, 4)
    n = a * a + b * b
    kind = pick(rng, ["secant", "tangent", "disjoint"])
    if kind == "tangent":
        j = rng.randint(1, 3)
        sigma, r2 = pick(rng, [1, -1]) * n * j, n * j * j
    else:
        sigma = nz(rng, -15, 15)
        exact = Fraction(sigma * sigma, n)
        r2 = int(exact) + rng.randint(1, 8) if kind == "secant" else int(exact) - rng.randint(0, 6)
        if r2 <= 0 or r2 == exact:
            raise ValueError("retry")
    return {"circle": std(h, k, r2), "lines": [norm_ints(a, b, sigma - a * h - b * k)], "style": "three_cases"}


# --- 2. solve_circle_line_parameter --------------------------------------------------------------------

v12482 = {"circle": {"d": 1, "e": [0, 1], "f": 2}, "line": {"a": 1, "b": -1, "c": 0},
          "asks": [{"condition": "tangent", "output": "set"}], "line_form": "rhs"}


def s12482(rng):
    """Like the source, both tangency roots must give a real circle.

    Tangency of x^2+y^2+dx+ky+f=0 and ax+by=0 means (ak-bd)^2 = 4f(a^2+b^2); a root is degenerate (r^2=0)
    exactly when the centre lies on the line, i.e. ad+bk=0.
    """
    a, b = pick(rng, [(1, -1), (1, 1), (1, -2), (2, -1), (1, 2), (2, 1), (1, -3), (3, -1)])
    d, f = rng.randint(-4, 4), nz(rng, -6, 6)
    s2 = f * (a * a + b * b)
    if s2 <= 0 or isqrt(s2) ** 2 != s2:
        raise ValueError("retry")
    roots = [Fraction(b * d + sign * 2 * isqrt(s2), a) for sign in (1, -1)]
    if any(a * d + b * k == 0 for k in roots):
        raise ValueError("retry")
    return {"circle": {"d": d, "e": [0, 1], "f": f}, "line": {"a": a, "b": b, "c": 0},
            "asks": [{"condition": "tangent", "output": "set"}], "line_form": "rhs"}


v12485 = {"circle": std(1, 2, 9), "line": {"a": 3, "b": 4, "c": [0, 1]},
          "asks": [{"condition": "tangent", "output": "set"}, {"condition": "tangent", "output": "lines"},
                   {"condition": "secant", "output": "region"}], "two_solution_hint": True}


def s12485(rng):
    a, b, _n = signed_normal(rng)
    return {"circle": std(rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(2, 6) ** 2), "line": {"a": a, "b": b, "c": [0, 1]},
            "asks": v12485["asks"], "two_solution_hint": True}


v12487 = {"circle": {"d": 2, "e": 0, "f": [0, 1]}, "line": {"a": 1, "b": 1, "c": 0},
          "asks": [{"condition": "disjoint", "output": "region"}], "line_form": "rhs"}


def s12487(rng):
    a, b = pick(rng, [(1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (3, 1), (1, 3)])
    return {"circle": {"d": 2 * rng.randint(-3, 3), "e": 2 * rng.randint(-3, 3), "f": [0, 1]},
            "line": {"a": a, "b": b, "c": rng.randint(-3, 3)},
            "asks": [{"condition": "disjoint", "output": "region"}], "line_form": "rhs"}


v12496 = {"circle": {"d": 0, "e": -4, "f": [0, 1]}, "line": {"a": 1, "b": -2, "c": 0},
          "asks": [{"condition": "intersect", "output": "region"}], "line_form": "rhs"}


def s12496(rng):
    a, b = pick(rng, [(1, -2), (2, -1), (1, 2), (2, 1), (1, -1), (1, 1), (1, -3)])
    return {"circle": {"d": 2 * rng.randint(-3, 3), "e": 2 * rng.randint(-3, 3), "f": [0, 1]},
            "line": {"a": a, "b": b, "c": rng.randint(-3, 3)},
            "asks": [{"condition": "intersect", "output": "region"}], "line_form": "rhs"}


v12489 = {"circle": std(-1, 2, 169), "line": {"a": 3, "b": 4, "c": [0, 1]},
          "asks": [{"condition": "chord", "chord": 24, "output": "set"}], "show_r": True}

PYTH_TRIPLES = [(5, 4, 3), (5, 3, 4), (13, 12, 5), (13, 5, 12), (10, 8, 6), (10, 6, 8), (17, 15, 8), (17, 8, 15)]


def s12489(rng):
    r, half, _d = pick(rng, PYTH_TRIPLES)
    a, b, _n = signed_normal(rng)
    return {"circle": std(rng.randint(-4, 4), rng.randint(-4, 4), r * r), "line": {"a": a, "b": b, "c": [0, 1]},
            "asks": [{"condition": "chord", "chord": 2 * half, "output": "set"}], "show_r": True}


v12498 = {"circle": {"d": 2, "e": 0, "f": [0, 1]}, "line": {"a": 15, "b": -8, "c": -2},
          "asks": [{"condition": "chord", "chord": 4, "output": "set"}]}


def s12498(rng):
    h, k = rng.randint(-3, 3), rng.randint(-3, 3)
    a, b, n = signed_normal(rng)
    dist = rng.randint(1, 3)
    c = -(a * h + b * k) + pick(rng, [1, -1]) * dist * n
    return {"circle": {"d": -2 * h, "e": -2 * k, "f": [0, 1]}, "line": {"a": a, "b": b, "c": c},
            "asks": [{"condition": "chord", "chord": 2 * rng.randint(1, 4), "output": "set"}]}


v12512 = {"circle": std(-1, 0, 2), "line": {"a": [0, 1], "b": -1, "c": -3},
          "asks": [{"condition": "tangent", "output": "set"}], "param": "m", "line_form": "slope"}


def s12512(rng):
    h, k, r2, q = rng.randint(-3, 3), rng.randint(-3, 3), rng.randint(1, 10), nz(rng, -5, 5)
    # (m h - k + q)^2 = r2 (m^2 + 1): rational slopes need a square discriminant
    qa, qb, qc = h * h - r2, 2 * h * (q - k), (q - k) ** 2 - r2
    if qa == 0 or not is_square(qb * qb - 4 * qa * qc) or qb * qb - 4 * qa * qc == 0:
        raise ValueError("retry")
    return {"circle": std(h, k, r2), "line": {"a": [0, 1], "b": -1, "c": q},
            "asks": [{"condition": "tangent", "output": "set"}], "param": "m", "line_form": "slope"}


v12513 = {"circle": std(0, 2, 4), "line": {"a": 1, "b": -1, "c": [0, 1]},
          "asks": [{"condition": "quarter_arcs", "output": "ordered"}], "param": "m", "line_form": "slope", "names": ["m", "n"]}


def s12513(rng):
    a = pick(rng, [1, -1])
    return {"circle": std(rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(1, 5) ** 2), "line": {"a": a, "b": -1, "c": [0, 1]},
            "asks": v12513["asks"], "param": "m", "line_form": "slope", "names": ["m", "n"]}


# --- 3. write_circle_tangent_lines ---------------------------------------------------------------------

v12490 = {"circle": std(3, -4, 10), "kind": "with_slope", "slope": 3}


def s12490(rng):
    m = pick(rng, [1, -1, 2, -2, 3, -3, 4, -4])
    q = pick(rng, [1, 1, 2])
    return {"circle": std(rng.randint(-4, 4), rng.randint(-4, 4), (m * m + 1) * q * q), "kind": "with_slope", "slope": m}


v12509 = {"circle": {"d": 0, "e": 2, "f": -12}, "kind": "parallel_to", "parallel_to": [2, 3, 0]}


def s12509(rng):
    a, b = pick(rng, [(2, 3), (3, 2), (1, 2), (2, 1), (2, -3), (3, -2), (1, -2), (1, 3), (3, -1)])
    h, k, q = rng.randint(-3, 3), rng.randint(-3, 3), 1
    return {"circle": general(h, k, (a * a + b * b) * q * q), "kind": "parallel_to", "parallel_to": [a, b, rng.randint(-4, 4)]}


v12500 = {"circle": std(-1, 2, 25), "kind": "through_point", "point": [3, 5]}


def _on_circle(rng, wording: str | None):
    h, k, r2 = rng.randint(-4, 4), rng.randint(-4, 4), pick(rng, LATTICE_R2)
    u, v = pick(rng, [o for o in lattice_offsets(r2) if o[0] and o[1]])
    out = {"circle": std(h, k, r2), "kind": "through_point", "point": [h + u, k + v]}
    if wording:
        out["wording"] = wording
    return out


def s12500(rng):
    return _on_circle(rng, None)


v12510 = {"circle": std(2, -1, 10), "kind": "through_point", "point": [3, -4], "wording": "plain"}


def s12510(rng):
    return _on_circle(rng, "plain")


def _outside_offsets() -> list[tuple[int, int, int]]:
    """(dx, dy, r2): P - M = (dx, dy) with two rational, non-axis tangents: r2 (|MP|^2 - r2) is a square."""
    out = []
    for dx in range(-7, 8):
        for dy in range(-7, 8):
            d2 = dx * dx + dy * dy
            for r2 in range(1, d2):
                if dx * dx != r2 and dy * dy != r2 and is_square(r2 * (d2 - r2)) and r2 <= 30:
                    out.append((dx, dy, r2))
    return out


OUTSIDE = _outside_offsets()

v12501 = {"circle": std(1, 2, 8), "kind": "through_point", "point": [5, 2]}


def s12501(rng):
    h, k = rng.randint(-3, 3), rng.randint(-3, 3)
    dx, dy, r2 = pick(rng, OUTSIDE)
    return {"circle": std(h, k, r2), "kind": "through_point", "point": [h + dx, k + dy]}


v12505 = {"circle": {"d": 6, "e": 0, "f": 4}, "kind": "through_point", "point": [2, 0]}


def s12505(rng):
    h, k = rng.randint(-3, 3), rng.randint(-3, 3)
    dx, dy, r2 = pick(rng, OUTSIDE)
    return {"circle": general(h, k, r2), "kind": "through_point", "point": [h + dx, k + dy]}


def _axis_tangent(rng, axis: str, wording: str | None, origin: bool = False):
    """P lies on a vertical (or horizontal) tangent, so the other tangent slope is rational too."""
    h, k = (0, 0) if origin else (rng.randint(-3, 3), rng.randint(-3, 3))
    r = rng.randint(1, 4)
    along = nz(rng, -6, 6)
    if abs(along) <= r and abs(along) != 0:
        along += r if along > 0 else -r
    side = pick(rng, [r, -r])
    p = [h + side, k + along] if axis == "vertical" else [h + along, k + side]
    out = {"circle": std(h, k, r * r), "kind": "through_point", "point": p}
    if wording:
        out["wording"] = wording
    return out


v12502 = {"circle": std(0, 0, 4), "kind": "through_point", "point": [2, 6]}


def s12502(rng):
    return _axis_tangent(rng, "vertical", None, origin=True)


v12506 = {"circle": std(-1, 0, 1), "kind": "through_point", "point": [0, 2]}


def s12506(rng):
    return _axis_tangent(rng, "vertical", None)


v12511 = {"circle": std(1, 2, 1), "kind": "through_point", "point": [6, 3], "wording": "neutral"}


def s12511(rng):
    return _axis_tangent(rng, "horizontal", "neutral")


# --- 4. solve_chord_and_distance -----------------------------------------------------------------------

v12484 = {"circle": std(2, 3, 25), "line": [3, -4, 21], "asks": ["chord"]}


def s12484(rng):
    h, k = rng.randint(-4, 4), rng.randint(-4, 4)
    dist = rng.randint(1, 5)
    r2 = dist * dist + rng.randint(2, 30)
    return {"circle": std(h, k, r2), "line": line_at_distance(rng, h, k, dist), "asks": ["chord"]}


v12499 = {"circle": std(0, 3, 5), "line": [5, -12, -3], "asks": ["max_distance", "min_distance"]}


def s12499(rng):
    h, k = rng.randint(-4, 4), rng.randint(-4, 4)
    dist = rng.randint(2, 6)
    r2 = rng.randint(1, dist * dist - 1)
    if is_square(r2):
        raise ValueError("retry")
    return {"circle": std(h, k, r2), "line": line_at_distance(rng, h, k, dist), "asks": ["max_distance", "min_distance"]}


v12515 = {"circle": std(1, 2, 9), "point": [2, 4], "asks": ["shortest_chord", "shortest_chord_line"]}


def s12515(rng):
    h, k = rng.randint(-4, 4), rng.randint(-4, 4)
    u, v = rng.randint(-3, 3), rng.randint(-3, 3)
    if u == 0 and v == 0:
        raise ValueError("retry")
    r2 = u * u + v * v + rng.randint(1, 16)
    return {"circle": std(h, k, r2), "point": [h + u, k + v], "asks": ["shortest_chord", "shortest_chord_line"]}


# --- 5. solve_circle_from_tangent_point ----------------------------------------------------------------

v12504 = {"d": -4, "point": [-1, 3], "tangent": [3, -4, 15], "names": ["m", "n"]}


def s12504(rng):
    h, k = nz(rng, -4, 4), nz(rng, -4, 4)
    u, v = nz(rng, -4, 4), nz(rng, -4, 4)
    px, py = h + u, k + v
    return {"d": -2 * h, "point": [px, py], "tangent": norm_ints(u, v, -(u * px + v * py)), "names": ["m", "n"]}


# --- 6. evaluate_circle_line_statement_truth -----------------------------------------------------------

v12491 = {"statement": {"kind": "line_through_point_on_circle_is_tangent"}}


def s12491(rng):
    return dict(v12491)


v12492 = {"statement": {"kind": "disjoint_distance_bound", "r2": 25, "bound": 5}}


def s12492(rng):
    r = rng.randint(2, 12)
    return {"statement": {"kind": "disjoint_distance_bound", "r2": r * r, "bound": max(1, r + pick(rng, [0, 0, -1, -2, 1, 2]))}}


v12493 = {"statement": {"kind": "tangent_to_both_axes", "center": [2, -2], "r2": 4}}


def s12493(rng):
    r = rng.randint(1, 6)
    h, k = pick(rng, [r, -r]), pick(rng, [r, -r])
    mode = pick(rng, ["both", "both", "x_only", "y_only"])
    if mode == "x_only":
        h = pick(rng, [1, -1]) * (r + rng.randint(1, 3))
    elif mode == "y_only":
        k = pick(rng, [1, -1]) * (r + rng.randint(1, 3))
    return {"statement": {"kind": "tangent_to_both_axes", "center": [h, k], "r2": r * r}}


v12494 = {"statement": {"kind": "tangent_slope_exists", "slope": 100}}


def s12494(rng):
    return {"statement": {"kind": "tangent_slope_exists", "slope": pick(rng, [1, 2, 3, 5, 10, 50, 100, 200, 1000, -1, -2, -5, -10, -100])
                          if rng.random() < 0.8 else f"{nz(rng, -9, 9)}/{rng.randint(2, 7)}"}}


v12508 = {"statement": {"kind": "two_tangents_through_point", "center": [0, 0], "r2": 1, "point": [1, 3]}}


def s12508(rng):
    h, k = pick(rng, [(0, 0), (0, 0), (rng.randint(-3, 3), rng.randint(-3, 3))])
    r2 = pick(rng, [1, 4, 5, 9, 10, 13, 25])
    mode = pick(rng, ["outside", "outside", "on", "inside"])
    if mode == "on":
        u, v = pick(rng, lattice_offsets(r2))
    elif mode == "inside":
        u, v = rng.randint(-1, 1), rng.randint(-1, 1)
        if u * u + v * v >= r2:
            raise ValueError("retry")
    else:
        u, v = rng.randint(-6, 6), rng.randint(-6, 6)
        if u * u + v * v <= r2:
            raise ValueError("retry")
    return {"statement": {"kind": "two_tangents_through_point", "center": [h, k], "r2": r2, "point": [h + u, k + v]}}


# --- 7. solve_circle_tangent_scenarios -----------------------------------------------------------------

def _building_inputs() -> list[tuple[int, int, int]]:
    """(k, px, dy): P = (px, k + dy); the base half-length sqrt(px^2 + dy^2 - k^2) is an integer."""
    out = []
    for k in range(2, 9):
        for px in range(1, 11):
            for dy in range(1, 9):
                r2 = px * px + dy * dy
                if r2 > k * k and is_square(r2 - k * k):
                    out.append((k, px, dy))
    return out


BUILDINGS = _building_inputs()

v12503 = {"scenario": "building_view", "center_y": 6, "point": [6, 10]}


def s12503(rng):
    k, px, dy = pick(rng, BUILDINGS)
    return {"scenario": "building_view", "center_y": k, "point": [px, k + dy]}


v12507 = {"scenario": "building_dimensions", "center_y": 6, "point": [6, 10]}


def s12507(rng):
    k, px, dy = pick(rng, BUILDINGS)
    return {"scenario": "building_dimensions", "center_y": k, "point": [px, k + dy]}


def _light_inputs() -> list[tuple[int, int, int, int, int]]:
    """(h, k, r2, dx, dy): light at (h + dx, k + dy) above the circle, both tangent slopes rational."""
    out = []
    for k in range(2, 7):
        for r2 in range(1, k * k):
            for dx in range(-3, 4):
                for dy in range(1, 7):
                    d2 = dx * dx + dy * dy
                    if dy * dy > r2 and is_square(r2 * (d2 - r2)) and dx * dx != r2:
                        # tangent slopes from the light: (dx^2 - r2) m^2 - 2 dx dy m + (dy^2 - r2) = 0
                        root = isqrt(4 * r2 * (d2 - r2))
                        slopes = [Fraction(2 * dx * dy + s * root, 2 * (dx * dx - r2)) for s in (1, -1)]
                        feet = [dx - Fraction(k + dy) / m for m in slopes]
                        # no near-horizontal grazing shadow; shadow ends keep classroom-size fractions
                        if all(abs(m) >= Fraction(1, 2) for m in slopes) and all(f.denominator <= 3 for f in feet):
                            out.append((0, k, r2, dx, dy))
    return out


LIGHTS = _light_inputs()

v12514 = {"scenario": "light_shadow", "circle": std(0, 3, 5), "light": [1, 6]}


def s12514(rng):
    _h, k, r2, dx, dy = pick(rng, LIGHTS)
    h = rng.randint(-2, 2)
    return {"scenario": "light_shadow", "circle": std(h, k, r2), "light": [h + dx, k + dy]}


v12516 = {"scenario": "badge", "width": 4, "r2": 2, "center_height": 3, "od": 1}


def _badge_inputs() -> list[tuple[int, int, int, int]]:
    """(width, r2, centre height, OD) with rational tangents from D, one to each side, and a badge at most 3 widths tall."""
    out = []
    for w in (4, 6, 8, 10, 12):
        for r2 in range(1, (w // 2) ** 2):
            for cy in range(2, 13):
                for od in range(1, w):
                    dx, dy = Fraction(w, 2) - od, cy
                    disc = 4 * r2 * (dx * dx + dy * dy - r2)
                    qa = dx * dx - r2
                    if qa == 0 or cy * cy <= r2 or not is_square(int(disc)):
                        continue
                    slopes = sorted(Fraction(2 * dx * dy + s * isqrt(int(disc)), 2 * qa) for s in (1, -1))
                    if not slopes[0] < 0 < slopes[1]:
                        continue
                    top, e_y = -slopes[0] * od, slopes[1] * (w - od)
                    if 0 < e_y < top <= 3 * w and (cy + isqrt(r2) + 1) ** 2 <= top * top:
                        out.append((w, r2, cy, od))
    return out


BADGES = _badge_inputs()


def s12516(rng):
    w, r2, cy, od = pick(rng, BADGES)
    return {"scenario": "badge", "width": w, "r2": r2, "center_height": cy, "od": od}


# --- component table --------------------------------------------------------------------------------------------------------

COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12481: ("judge", "classify_circle_line_relations", v12481, s12481),
    12482: ("judge", "solve_circle_line_parameter", v12482, s12482),
    12483: ("judge", "classify_circle_line_relations", v12483, s12483),
    12484: ("judge", "solve_chord_and_distance", v12484, s12484),
    12485: ("judge", "solve_circle_line_parameter", v12485, s12485),
    12486: ("judge", "classify_circle_line_relations", v12486, s12486),
    12487: ("judge", "solve_circle_line_parameter", v12487, s12487),
    12488: ("judge", "classify_circle_line_relations", v12488, s12488),
    12489: ("judge", "solve_circle_line_parameter", v12489, s12489),
    12490: ("judge", "write_circle_tangent_lines", v12490, s12490),
    12491: ("judge", "evaluate_circle_line_statement_truth", v12491, s12491),
    12492: ("judge", "evaluate_circle_line_statement_truth", v12492, s12492),
    12493: ("judge", "evaluate_circle_line_statement_truth", v12493, s12493),
    12494: ("judge", "evaluate_circle_line_statement_truth", v12494, s12494),
    12495: ("judge", "classify_circle_line_relations", v12495, s12495),
    12496: ("judge", "solve_circle_line_parameter", v12496, s12496),
    12497: ("judge", "classify_circle_line_relations", v12497, s12497),
    12498: ("judge", "solve_circle_line_parameter", v12498, s12498),
    12499: ("judge", "solve_chord_and_distance", v12499, s12499),
    12500: ("tangent", "write_circle_tangent_lines", v12500, s12500),
    12501: ("tangent", "write_circle_tangent_lines", v12501, s12501),
    12502: ("tangent", "write_circle_tangent_lines", v12502, s12502),
    12503: ("tangent", "solve_circle_tangent_scenarios", v12503, s12503),
    12504: ("tangent", "solve_circle_from_tangent_point", v12504, s12504),
    12505: ("tangent", "write_circle_tangent_lines", v12505, s12505),
    12506: ("tangent", "write_circle_tangent_lines", v12506, s12506),
    12507: ("tangent", "solve_circle_tangent_scenarios", v12507, s12507),
    12508: ("tangent", "evaluate_circle_line_statement_truth", v12508, s12508),
    12509: ("tangent", "write_circle_tangent_lines", v12509, s12509),
    12510: ("tangent", "write_circle_tangent_lines", v12510, s12510),
    12511: ("tangent", "write_circle_tangent_lines", v12511, s12511),
    12512: ("tangent", "solve_circle_line_parameter", v12512, s12512),
    12513: ("judge", "solve_circle_line_parameter", v12513, s12513),
    12514: ("tangent", "solve_circle_tangent_scenarios", v12514, s12514),
    12515: ("judge", "solve_chord_and_distance", v12515, s12515),
    12516: ("tangent", "solve_circle_tangent_scenarios", v12516, s12516),
}
