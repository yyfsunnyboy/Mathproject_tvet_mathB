"""Per-component *inputs* for 普高數學1 Unit 6 (圓方程式).

Each entry gives the source-faithful givens (variant 0) and a sampler for further variants of the
same shape.  Samplers only choose inputs; the domain computes every answer.  Display strings
(``stem``) are descriptive text only and never carry an answer.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from agent_domains_candidate.analytic_geometry_circles.circle_geometry import (
    fr, frac_latex, frac_text, general_latex, general_text, std_latex, std_text,
)

SKILLS = {
    "std": "gh_StandardFormOfACircle",
    "gen": "gh_GeneralFormOfACircle",
    "pc": "gh_PointAndCircleRelationship",
}

# 教材題目中無法落入 Spec §5 正式作答契約的題目（記錄原因，不進 wrapper）
DEFERRED: dict[int, str] = {}

OP = {name: name for name in (
    "write_circle_equations", "analyze_general_circle", "solve_distance_ratio_locus", "classify_points_against_circle",
    "solve_circle_point_distances", "solve_point_position_parameter_range", "evaluate_circle_statement_truth",
    "solve_mohr_circles", "solve_storm_entry_time", "solve_circular_arch_height",
)}


# --- helpers -----------------------------------------------------------------------------------------

def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


def pt2(rng: random.Random, span: int = 5) -> list[int]:
    return [rng.randint(-span, span), rng.randint(-span, span)]


def distinct_pts(rng: random.Random, n: int = 2, span: int = 5) -> list[list[int]]:
    while True:
        pts = [pt2(rng, span) for _ in range(n)]
        if len({tuple(p) for p in pts}) == n:
            return pts


def lattice_offsets(r2: int) -> list[tuple[int, int]]:
    out = []
    r = int(r2 ** 0.5) + 1
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy == r2:
                out.append((dx, dy))
    return out


INT_DIST = [5, 10, 13, 15, 17]  # centre distances that have lattice offsets
OFFSETS = {r: lattice_offsets(r * r) for r in (5, 10, 13, 15, 17, 25)}
OFFSETS.update({r: lattice_offsets(r * r) for r in (3, 4, 6, 7, 8)})
OFFSETS = {r: [o for o in offs if o[0] != 0 and o[1] != 0] or offs for r, offs in OFFSETS.items()}


def general(center: list[Any], r2: Any, a: int = 1) -> dict[str, Any]:
    h, k, r2 = fr(center[0]), fr(center[1]), fr(r2)
    return {"a": a, "d": frac_text(-2 * a * h), "e": frac_text(-2 * a * k), "f": frac_text(a * (h * h + k * k - r2))} if a != 1 else {
        "d": frac_text(-2 * h), "e": frac_text(-2 * k), "f": frac_text(h * h + k * k - r2)}


def standard(center: list[Any], r2: Any) -> dict[str, Any]:
    return {"center": [frac_text(fr(center[0])), frac_text(fr(center[1]))], "r2": frac_text(fr(r2))}


def option(spec_kind: str, **kw: Any) -> dict[str, Any]:
    """A Mohr-option: general or standard form with its display strings (display only; the domain reads d/e/f)."""
    if spec_kind == "general":
        d, e, f = kw["d"], kw["e"], kw["f"]
        return {"d": d, "e": e, "f": f, "latex": general_latex(d, e, f), "text": general_text(d, e, f)}
    h, k, r2 = kw["h"], kw["k"], kw["r2"]
    d, e, f = -2 * h, -2 * k, h * h + k * k - r2
    return {"d": d, "e": e, "f": f, "latex": std_latex(h, k, r2), "text": std_text(h, k, r2)}


# --- write_circle_equations -----------------------------------------------------------------------------------

def _item_center_radius(center, r2):
    return {"kind": "center_radius", "center": center, "r2": r2}


def _item_center_point(center, point, names=None):
    item = {"kind": "center_point", "center": center, "point": point}
    if names:
        item["names"] = names
    return item


v12449 = {"stem": "求下列各圓的方程式：", "items": [_item_center_radius([2, -3], 16), _item_center_point([2, -3], [5, 1], {"center": "M", "point": "A"})]}


def s12449(rng):
    c = pt2(rng, 4)
    c2 = pt2(rng, 4)
    p = [c2[0] + nz(rng, -6, 6), c2[1] + rng.randint(-6, 6)]
    return {"stem": "求下列各圓的方程式：", "items": [_item_center_radius(c, rng.randint(2, 7) ** 2), _item_center_point(c2, p, {"center": "M", "point": "A"})]}


v12450 = {"items": [{"kind": "diameter", "a": [-2, 3], "b": [6, -3]}]}


def s12450(rng):
    a, b = distinct_pts(rng, 2, 7)
    return {"items": [{"kind": "diameter", "a": a, "b": b}]}


v12451 = {"items": [_item_center_radius([-1, 0], 5), {"kind": "origin_circle_k", "x_sqrt": 3, "point": [0, -1], "names": {"point": "A"}}]}


def s12451(rng):
    return {"items": [_item_center_radius(pt2(rng, 4), pick(rng, [2, 3, 5, 6, 7, 8, 10, 11])),
                      {"kind": "origin_circle_k", "x_sqrt": pick(rng, [2, 3, 5, 6, 7]), "point": [0, nz(rng, -4, 4)], "names": {"point": "A"}}]}


v12452 = {"items": [{"kind": "diameter_param_k", "center": [4, 1], "a": [2, 3]}]}


def s12452(rng):
    c = pt2(rng, 4)
    a = [c[0] + nz(rng, -4, 4), c[1] + rng.randint(-4, 4)]
    return {"items": [{"kind": "diameter_param_k", "center": c, "a": a}]}


# 12469: radius r, passes through (px, py): centre (px +- sqrt(r^2-py^2), 0)
_ARCH_LEGS = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 6, 10), (8, 15, 17), (7, 24, 25)]

v12469 = {"items": [{"kind": "axis_center_through_point_radius", "point": [7, 3], "r": 5}]}


def s12469(rng):
    py, leg, r = pick(rng, _ARCH_LEGS)
    return {"items": [{"kind": "axis_center_through_point_radius", "point": [rng.randint(-8, 10), pick(rng, [py, -py])], "r": r}]}


v12476 = {"stem": "求符合下列條件的圓方程式：", "items": [
    {"kind": "diameter", "a": [2, -3], "b": [-4, 1], "names": {"a": "A", "b": "B"}},
    {"kind": "concentric_through", "ref": {"d": 2, "e": -4, "f": -1}, "point": [3, 5]},
    {"kind": "axis_center_through_points", "points": [[1, 4], [0, 3]]},
]}


def s12476(rng):
    a, b = distinct_pts(rng, 2, 6)
    centre = pt2(rng, 3)
    ref = general(centre, rng.randint(1, 6))
    point = [centre[0] + nz(rng, -5, 5), centre[1] + rng.randint(-5, 5)]
    while True:
        p, q = distinct_pts(rng, 2, 5)
        if p[0] != q[0]:
            break
    return {"stem": "求符合下列條件的圓方程式：", "items": [
        {"kind": "diameter", "a": a, "b": b, "names": {"a": "A", "b": "B"}},
        {"kind": "concentric_through", "ref": {k: ref[k] for k in ("d", "e", "f")}, "point": point},
        {"kind": "axis_center_through_points", "points": [p, q]}]}


def _circumcircle(rng):
    r = pick(rng, [5, 10, 13, 15, 17, 25])
    offsets = lattice_offsets(r * r)
    chosen = rng.sample(offsets, 3)
    centre = pt2(rng, 4)
    return [[centre[0] + dx, centre[1] + dy] for dx, dy in chosen]


def _perp_bisector_items(a, b, c):
    return [{"kind": "perp_bisector", "p": a, "q": b, "names": {"p": "A", "q": "B"}},
            {"kind": "perp_bisector", "p": b, "q": c, "names": {"p": "B", "q": "C"}},
            {"kind": "circumcircle", "a": a, "b": b, "c": c, "names": {"a": "A", "b": "B", "c": "C"}}]


def _stem_points(a, b, c):
    from agent_domains_candidate.analytic_geometry_circles.circle_geometry import G, pt

    return "已知 " + "、".join(f"${G.point_latex(pt(p), n)}$" for p, n in zip((a, b, c), "ABC")) + "，"


v12479 = {"stem": _stem_points([5, 10], [6, 9], [-2, 3]), "items": _perp_bisector_items([5, 10], [6, 9], [-2, 3])}


def s12479(rng):
    a, b, c = _circumcircle(rng)
    return {"stem": _stem_points(a, b, c), "items": _perp_bisector_items(a, b, c)}


# --- analyze_general_circle -----------------------------------------------------------------------------------

def _g(center, r2, a=1):
    spec = general(center, r2, a)
    return {k: spec[k] for k in spec}


v12453 = {"items": [{"kind": "center_radius", **_g([1, -3], 4)}]}


def s12453(rng):
    return {"items": [{"kind": "center_radius", **_g(pt2(rng, 5), rng.randint(1, 30))}]}


def _cls(center, r2):
    return {"kind": "standard_and_classify", **_g(center, r2)}


v12454 = {"stem": "將下列方程式化成 $\\left(x-h\\right)^{2}+\\left(y-k\\right)^{2}=\\ell$ 的形式，並說明它所表示的圖形。",
          "items": [_cls([-1, 2], 0), _cls([-1, 2], -5)]}


def s12454(rng):
    c = pt2(rng, 5)
    return {"stem": v12454["stem"], "items": [_cls(c, 0), _cls(c, -rng.randint(1, 9))]}


v12455 = {"items": [{"kind": "param_range", "d": -4, "e": 2, "f1": 1}]}


def s12455(rng):
    return {"items": [{"kind": "param_range", "d": 2 * nz(rng, -5, 5), "e": 2 * rng.randint(-5, 5), "f0": rng.randint(-3, 3), "f1": pick(rng, [1, -1, 2, -2])}]}


v12458 = {"items": [{"kind": "param_from_radius", "d": -4, "e": 2, "f1": 1, "r2": 9}]}


def s12458(rng):
    return {"items": [{"kind": "param_from_radius", "d": 2 * nz(rng, -5, 5), "e": 2 * rng.randint(-5, 5), "f1": pick(rng, [1, -1, 2]), "r2": rng.randint(2, 8) ** 2}]}


def _three_kinds(c, m1, m2):
    return [{"kind": "classify", **_g(c, m1)}, {"kind": "classify", **_g(c, 0)}, {"kind": "classify", **_g(c, -m2)}]


v12459 = {"stem": "試判斷下列方程式所代表的圖形：", "items": _three_kinds([2, -3], 25, 4)}


def s12459(rng):
    items = _three_kinds(pt2(rng, 5), rng.randint(1, 8) ** 2, rng.randint(1, 9))
    rng.shuffle(items)
    return {"stem": v12459["stem"], "items": items}


v12460 = {"items": [{"kind": "param_radius_center", "d": 2, "e1": -2, "f1": 2, "r2": 9}]}


def s12460(rng):
    while True:
        a, k1, k2 = nz(rng, -3, 3), rng.randint(-5, 6), rng.randint(-5, 6)
        r2 = a * a - k1 * k2
        if k1 != k2 and r2 > 0:
            break
    return {"items": [{"kind": "param_radius_center", "d": 2 * a, "e1": pick(rng, [-2, 2]), "f1": k1 + k2, "r2": r2}]}


v12462 = {"items": [{"kind": "coefficients_from_center", "h": 1, "k": -3, "f": -6}]}


def s12462(rng):
    while True:
        h, k, f = rng.randint(-4, 4), nz(rng, -4, 4), rng.randint(-9, 4)
        if h * h + k * k - f > 0:
            return {"items": [{"kind": "coefficients_from_center", "h": h, "k": k, "f": f}]}


v12463 = {"items": [{"kind": "param_range", "d": 2, "e": 2, "f0": 7, "f1": -1}]}


def s12463(rng):
    return {"items": [{"kind": "param_range", "d": 2 * nz(rng, -4, 4), "e": 2 * rng.randint(-4, 4), "f0": rng.randint(2, 12), "f1": pick(rng, [-1, -2, -3])}]}


def _root(h, k, rhs):
    return {"kind": "center_radius", "form": "root", "h": h, "k": k, "rhs": rhs}


v12475 = {"stem": "求下列各圓的圓心和半徑：", "items": [
    _root(1, 0, 2), {"kind": "center_radius", **_g([0, 2], 1)}, {"kind": "center_radius", **_g(["1/3", 0], 4, a=9)}]}


def s12475(rng):
    a = pick(rng, [4, 9])
    s = 2 if a == 4 else 3
    centre = [Fraction(nz(rng, -5, 5), s), Fraction(rng.randint(-2, 2), s)]
    return {"stem": v12475["stem"], "items": [
        _root(rng.randint(-4, 4), rng.randint(-3, 3), rng.randint(1, 6)),
        {"kind": "center_radius", **_g([0, nz(rng, -5, 5)], rng.randint(1, 8))},
        {"kind": "center_radius", **_g([frac_text(centre[0]), frac_text(centre[1])], rng.randint(1, 5), a=a)}]}


# --- solve_distance_ratio_locus ----------------------------------------------------------------------------------

v12456 = {"a": [0, 0], "b": [6, 0], "ratio": [2, 1], "asks": ["equation"]}


def s12456(rng):
    p, q = pick(rng, [(2, 1), (3, 1), (3, 2), (4, 1), (4, 3), (5, 2), (5, 3), (5, 4)])
    return {"a": [0, 0], "b": [rng.randint(3, 12), 0], "ratio": [p, q], "asks": ["equation"]}


v12461 = {"a": [0, 0], "b": [6, 0], "ratio": [1, 2], "asks": ["equation"]}


def s12461(rng):
    p, q = pick(rng, [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5), (3, 5), (4, 5)])
    return {"a": [0, 0], "b": [rng.randint(3, 12), 0], "ratio": [p, q], "asks": ["equation"]}


v12457 = {"scenario": "garbage", "a": [0, 0], "b": [16, 0], "weights": [3, 5], "half": "upper",
          "asks": ["ratio_p", "ratio_q", "shape", "center", "radius"],
          "figure": {"points": [{"p": [0, 0], "label": "A"}, {"p": [16, 0], "label": "B"}], "segments": [[0, 1]], "pad": 2, "extent": [[8, 8]]}}


def s12457(rng):
    wa, wb = rng.sample([2, 3, 4, 5, 6, 7, 8], 2)
    d = rng.randint(6, 24)
    return {"scenario": "garbage", "a": [0, 0], "b": [d, 0], "weights": [wa, wb], "half": "upper",
            "asks": ["ratio_p", "ratio_q", "shape", "center", "radius"],
            "figure": {"points": [{"p": [0, 0], "label": "A"}, {"p": [d, 0], "label": "B"}], "segments": [[0, 1]], "pad": 2, "extent": [[d // 2, d // 2]]}}


# --- point / circle relations --------------------------------------------------------------------------------------

v12464 = {"circle": standard([2, -3], 25), "points": [[6, 0], [-2, -1], [0, 2]], "names": ["P", "Q", "R"]}


def s12464(rng):
    r = pick(rng, [3, 4, 5, 6, 7])
    c = pt2(rng, 4)
    on = pick(rng, OFFSETS[r] if r in OFFSETS else lattice_offsets(r * r))
    inside = pick(rng, [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if 0 < dx * dx + dy * dy < r * r])
    outside = pick(rng, [(dx, dy) for dx in range(-r - 3, r + 4) for dy in range(-r - 3, r + 4) if dx * dx + dy * dy > r * r])
    pts = [[c[0] + dx, c[1] + dy] for dx, dy in (on, inside, outside)]
    rng.shuffle(pts)
    return {"circle": standard(c, r * r), "points": pts, "names": ["P", "Q", "R"]}


def _lattice_point_at(rng, centre, dist):
    dx, dy = pick(rng, OFFSETS[dist])
    return [centre[0] + dx, centre[1] + dy]


v12465 = {"circle": general([-2, 1], 1), "point": [2, 4], "asks": ["max", "min"], "point_name": "P"}


def s12465(rng):
    c = pt2(rng, 4)
    r = rng.randint(1, 4)
    dist = pick(rng, [d for d in (5, 10, 13, 15, 17) if d > r])
    return {"circle": general(c, r * r), "point": _lattice_point_at(rng, c, dist), "asks": ["max", "min"], "point_name": "P"}


v12468 = {"circle": general([3, 4], 36), "point": [0, 0], "asks": ["max", "min"], "point_name": "原點"}


def s12468(rng):
    dist = pick(rng, [5, 10, 13, 15, 17])
    dx, dy = pick(rng, OFFSETS[dist])
    r = pick(rng, [x for x in range(1, dist + 8) if x != dist])
    return {"circle": general([dx, dy], r * r), "point": [0, 0], "asks": ["max", "min"], "point_name": "原點"}


v12477 = {"circle": standard([0, 2], 9), "point": [3, -2], "asks": ["relation", "min"], "point_name": "A"}


def s12477(rng):
    c = pt2(rng, 3)
    dist = pick(rng, [5, 10, 13])
    r = pick(rng, [x for x in range(2, dist + 5) if x != dist])
    return {"circle": standard(c, r * r), "point": _lattice_point_at(rng, c, dist), "asks": ["relation", "min"], "point_name": "A"}


v12467 = {"inside": [[1, -2]], "outside": [[-3, 3]], "names": {"inside": ["P"], "outside": ["Q"]}}


def s12467(rng):
    while True:
        p, q = pt2(rng, 4), pt2(rng, 5)
        if p != [0, 0] and p[0] ** 2 + p[1] ** 2 < q[0] ** 2 + q[1] ** 2:
            return {"inside": [p], "outside": [q], "names": {"inside": ["P"], "outside": ["Q"]}}


# --- statements (觀念澄清) --------------------------------------------------------------------------------------------

v12470 = {"statement": {"kind": "center_quadrant", "center": [2, -3], "r2": 2, "claimed": 2}}


def s12470(rng):
    return {"statement": {"kind": "center_quadrant", "center": [nz(rng, -5, 5), nz(rng, -5, 5)], "r2": rng.randint(1, 12), "claimed": rng.randint(1, 4)}}


v12471 = {"statement": {"kind": "is_circle", "d": 0, "e": 0, "f": 5}}


def s12471(rng):
    return {"statement": {"kind": "is_circle", "d": 2 * rng.randint(-3, 3), "e": 2 * rng.randint(-3, 3), "f": rng.randint(-8, 8)}}


v12472 = {"statement": {"kind": "may_be_point", "d": -2, "e": 4, "f1": 1}}


def s12472(rng):
    return {"statement": {"kind": "may_be_point", "d": 2 * nz(rng, -3, 3), "e": 2 * nz(rng, -3, 3), "f0": rng.randint(-3, 3), "f1": pick(rng, [1, -1, 2])}}


v12473 = {"statement": {"kind": "origin_inside", "center": [1, 2], "r2": 2}}


def s12473(rng):
    while True:
        c = [rng.randint(-4, 4), rng.randint(-4, 4)]
        r2 = rng.randint(1, 20)
        if c[0] ** 2 + c[1] ** 2 not in (0, r2) and r2 > 0:
            return {"statement": {"kind": "origin_inside", "center": c, "r2": r2}}


v12474 = {"statement": {"kind": "area_equals", "r2": 2, "claimed_coef": 2, "with_pi": True}}


def s12474(rng):
    r2 = rng.randint(1, 12)
    return {"statement": {"kind": "area_equals", "r2": r2, "claimed_coef": pick(rng, [r2, r2, r2 + 1, 2 * r2, r2 * r2]), "with_pi": pick(rng, [True, True, False])}}


# --- Mohr circles ---------------------------------------------------------------------------------------------------------

def _mohr(a, b, options, nested):
    return {"options": options, "diameter": {"a": a, "b": b}, "nested": nested}


v12466 = _mohr(
    [1, 2], [5, -2],
    [{"d": 0, "e": -6, "f": -16, "latex": "x^{2}+\\left(y-3\\right)^{2}=5^{2}", "text": "x^2+(y-3)^2=5^2"},
     {"d": 2, "e": -6, "f": -15, "latex": "\\left(x+1\\right)^{2}+\\left(y-3\\right)^{2}=5^{2}", "text": "(x+1)^2+(y-3)^2=5^2"},
     {"d": 2, "e": 0, "f": -5, "latex": "x^{2}+y^{2}+2x-5=0", "text": "x^2+y^2+2x-5=0"},
     {"d": -2, "e": 0, "f": 5, "latex": "x^{2}+y^{2}-2x+5=0", "text": "x^2+y^2-2x+5=0"}],
    [{"d": -12, "e": 0, "f": 11}, {"d": -6, "e": 0, "f": 5}, {"d": -16, "e": 0, "f": 55}])


def s12466(rng):
    h = rng.randint(-4, 4)
    r2 = rng.randint(2, 20)
    good = option("general", d=-2 * h, e=0, f=h * h - r2)
    off_axis = option("standard", h=rng.randint(-3, 3), k=nz(rng, -4, 4), r2=rng.randint(4, 30))
    off_axis2 = option("general", d=rng.randint(-4, 4), e=nz(rng, -3, 3) * 2, f=-rng.randint(1, 10))
    hh = rng.randint(-3, 3)
    empty = option("general", d=-2 * hh, e=0, f=hh * hh + rng.randint(1, 9))
    opts = [good, off_axis, off_axis2, empty]
    rng.shuffle(opts)
    m, s, t = rng.randint(-4, 5), rng.randint(1, 4), nz(rng, -4, 4)
    r1, r2_ = rng.sample(range(1, 6), 2)
    big = r1 + r2_
    c0 = rng.randint(-3, 6)
    nested = [{"d": -2 * c0, "e": 0, "f": c0 * c0 - big * big},
              {"d": -2 * (c0 - big + r1), "e": 0, "f": (c0 - big + r1) ** 2 - r1 * r1},
              {"d": -2 * (c0 + big - r2_), "e": 0, "f": (c0 + big - r2_) ** 2 - r2_ * r2_}]
    rng.shuffle(nested)
    return _mohr([m - s, t], [m + s, -t], opts, nested)


# --- storm / arch -------------------------------------------------------------------------------------------------------

v12478 = {"start_hour": 15, "distance": 460, "radius": 80, "speed": 25, "options": [18, 23, 30, 35]}


def s12478(rng):
    while True:
        start = pick(rng, [13, 14, 15, 16, 17, 18, 19, 20])
        speed = pick(rng, [20, 25, 30, 40])
        radius = pick(rng, [60, 80, 100, 120])
        whole = rng.randint(6, 18)
        frac_steps = rng.randint(0, 4)  # extra 0.0 .. 0.4 hour, in units of speed/10
        distance = radius + speed * whole + (speed * frac_steps) // 10
        entry = Fraction(start) + Fraction(distance - radius, speed)
        centre = round(entry)
        offsets = rng.sample([-14, -12, -9, -7, -5, -4, -3, 3, 4, 5, 6, 8, 10], 3)
        options = sorted({centre} | {centre + o for o in offsets})
        if len(options) != 4 or min(options) < 1 or max(options) > 47 or any(o % 12 == 0 for o in options):
            continue
        return {"start_hour": start, "distance": distance, "radius": radius, "speed": speed, "options": options}


def _arch(w, h):
    return {"width": w, "height": h, "post_offset": str(Fraction(w) / 2)}


v12480 = _arch(3, "9/2")


def s12480(rng):
    """PR = H - m^2/H where m = w/2; choose q = m^2/H < m so that the post height is a clean rational."""
    m = pick(rng, [Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2), Fraction(4), Fraction(5), Fraction(6)])
    q = pick(rng, [Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3)])
    while q >= m:
        q = pick(rng, [Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3)])
    return _arch(frac_text(2 * m), frac_text(m * m / q))


# --- component table --------------------------------------------------------------------------------------------------------

COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12449: ("std", "write_circle_equations", v12449, s12449),
    12450: ("std", "write_circle_equations", v12450, s12450),
    12451: ("std", "write_circle_equations", v12451, s12451),
    12452: ("std", "write_circle_equations", v12452, s12452),
    12453: ("gen", "analyze_general_circle", v12453, s12453),
    12454: ("gen", "analyze_general_circle", v12454, s12454),
    12455: ("gen", "analyze_general_circle", v12455, s12455),
    12456: ("gen", "solve_distance_ratio_locus", v12456, s12456),
    12457: ("gen", "solve_distance_ratio_locus", v12457, s12457),
    12458: ("gen", "analyze_general_circle", v12458, s12458),
    12459: ("gen", "analyze_general_circle", v12459, s12459),
    12460: ("gen", "analyze_general_circle", v12460, s12460),
    12461: ("gen", "solve_distance_ratio_locus", v12461, s12461),
    12462: ("gen", "analyze_general_circle", v12462, s12462),
    12463: ("gen", "analyze_general_circle", v12463, s12463),
    12464: ("pc", "classify_points_against_circle", v12464, s12464),
    12465: ("pc", "solve_circle_point_distances", v12465, s12465),
    12466: ("pc", "solve_mohr_circles", v12466, s12466),
    12467: ("pc", "solve_point_position_parameter_range", v12467, s12467),
    12468: ("pc", "solve_circle_point_distances", v12468, s12468),
    12469: ("pc", "write_circle_equations", v12469, s12469),
    12470: ("std", "evaluate_circle_statement_truth", v12470, s12470),
    12471: ("gen", "evaluate_circle_statement_truth", v12471, s12471),
    12472: ("gen", "evaluate_circle_statement_truth", v12472, s12472),
    12473: ("pc", "evaluate_circle_statement_truth", v12473, s12473),
    12474: ("std", "evaluate_circle_statement_truth", v12474, s12474),
    12475: ("gen", "analyze_general_circle", v12475, s12475),
    12476: ("std", "write_circle_equations", v12476, s12476),
    12477: ("pc", "solve_circle_point_distances", v12477, s12477),
    12478: ("pc", "solve_storm_entry_time", v12478, s12478),
    12479: ("std", "write_circle_equations", v12479, s12479),
    12480: ("std", "solve_circular_arch_height", v12480, s12480),
}
