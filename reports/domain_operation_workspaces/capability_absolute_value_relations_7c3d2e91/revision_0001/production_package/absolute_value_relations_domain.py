"""Exact, seed-deterministic operations for the algebra.absolute_value_relations domain.

Number-line distance and division points, and equations / inequalities / systems
built from absolute values of linear forms.  Every relation is solved exactly by
splitting the line at the zeros of its absolute-value arguments and solving the
linear relation on each piece.  Source items supply their inputs through
``constraints``; seeded generation produces inputs of the same shape.  Rendering
and answer topology belong to the adapter module.

Structured inputs
-----------------
linear form  ``[[coefficient, degree], ...]`` in written order, degree 0 or 1
             (``[[2, 0], [-1, 1]]`` is 2-x)
side         ``[{"abs": form, "coef": k?} | {"poly": form}, ...]`` meaning Σ k·|form| + Σ form
relation     ``{"lhs": side, "op": "=" | "<" | "<=" | ">" | ">=", "rhs": side}``
interval     ``[low, high, low_closed, high_closed]`` with ``"-oo"`` / ``"oo"`` for unbounded ends
weighted point ``[p, q]`` meaning (p·a + q·b)/(p + q) for a < b
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import combinations, product
from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_domain import (
    canonical_rational,
    parse_exact_rational,
)

DOMAIN_KEY = "algebra.absolute_value_relations"

NEG_INF = float("-inf")
POS_INF = float("inf")
RELATION_OPS = ("=", "<", "<=", ">", ">=")
INEQUALITY_OPS = ("<", "<=", ">", ">=")
_MAX_PARTS = 4
_MAX_TERMS = 6
_MAX_RELATIONS = 3
_MAX_OPTIONS = 4

Interval = tuple[Any, Any, bool, bool]
_WHOLE_LINE: Interval = (NEG_INF, POS_INF, False, False)


# --- linear forms, sides, relations ----------------------------------------------

def _form(raw: Any) -> list[list[Any]]:
    if not isinstance(raw, list) or not raw or len(raw) > _MAX_TERMS:
        raise ValueError("linear form must be a non-empty list")
    out = []
    for item in raw:
        coefficient, degree = item
        if degree not in (0, 1):
            raise ValueError("linear form degree must be 0 or 1")
        value = parse_exact_rational(coefficient)
        if value == 0:
            raise ValueError("linear form coefficients must be non-zero")
        out.append([canonical_rational(value), int(degree)])
    return out


def form_coefficients(form: list[list[Any]]) -> tuple[Fraction, Fraction]:
    """Return (slope, constant) of a linear form."""
    slope = sum((parse_exact_rational(c) for c, d in form if d == 1), Fraction(0))
    constant = sum((parse_exact_rational(c) for c, d in form if d == 0), Fraction(0))
    return slope, constant


def _side(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw or len(raw) > _MAX_TERMS:
        raise ValueError("relation side must be a non-empty list of terms")
    out: list[dict[str, Any]] = []
    for term in raw:
        if not isinstance(term, dict):
            raise ValueError("relation term must be a mapping")
        if "abs" in term:
            form = _form(term["abs"])
            if form_coefficients(form)[0] == 0:
                raise ValueError("absolute-value argument must depend on x")
            k = parse_exact_rational(term.get("coef", 1))
            if k == 0:
                raise ValueError("absolute-value coefficient must be non-zero")
            out.append({"abs": form, "coef": canonical_rational(k)})
        elif "poly" in term:
            out.append({"poly": _form(term["poly"])})
        else:
            raise ValueError("relation term must be 'abs' or 'poly'")
    return out


def _relation(raw: Any, *, ops: tuple[str, ...] = RELATION_OPS) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("op") not in ops:
        raise ValueError(f"relation op must be one of {ops}")
    return {"lhs": _side(raw["lhs"]), "op": raw["op"], "rhs": _side(raw["rhs"])}


def side_value(side: list[dict[str, Any]], x: Fraction) -> Fraction:
    total = Fraction(0)
    for term in side:
        if "abs" in term:
            a, b = form_coefficients(term["abs"])
            total += parse_exact_rational(term["coef"]) * abs(a * x + b)
        else:
            a, b = form_coefficients(term["poly"])
            total += a * x + b
    return total


def _holds(op: str, difference: Fraction) -> bool:
    if op == "=":
        return difference == 0
    if op == "<":
        return difference < 0
    if op == "<=":
        return difference <= 0
    if op == ">":
        return difference > 0
    return difference >= 0


def relation_holds(relation: dict[str, Any], x: Fraction) -> bool:
    return _holds(relation["op"], side_value(relation["lhs"], x) - side_value(relation["rhs"], x))


def breakpoints(relations: list[dict[str, Any]]) -> list[Fraction]:
    points: set[Fraction] = set()
    for relation in relations:
        for side in (relation["lhs"], relation["rhs"]):
            for term in side:
                if "abs" in term:
                    a, b = form_coefficients(term["abs"])
                    points.add(-b / a)
    return sorted(points)


# --- exact interval sets ---------------------------------------------------------

def _intersect_one(u: Interval, v: Interval) -> Interval | None:
    if u[0] > v[0]:
        lo, lc = u[0], u[2]
    elif v[0] > u[0]:
        lo, lc = v[0], v[2]
    else:
        lo, lc = u[0], u[2] and v[2]
    if u[1] < v[1]:
        hi, hc = u[1], u[3]
    elif v[1] < u[1]:
        hi, hc = v[1], v[3]
    else:
        hi, hc = u[1], u[3] and v[3]
    if lo < hi or (lo == hi and lc and hc):
        return (lo, hi, lc and lo != NEG_INF, hc and hi != POS_INF)
    return None


def merge_intervals(items: list[Interval]) -> list[Interval]:
    out: list[Interval] = []
    for lo, hi, lc, hc in sorted(items, key=lambda i: (i[0], not i[2])):
        if out:
            plo, phi, plc, phc = out[-1]
            if lo < phi or (lo == phi and (phc or lc)):
                if hi > phi:
                    out[-1] = (plo, hi, plc, hc)
                elif hi == phi:
                    out[-1] = (plo, phi, plc, phc or hc)
                continue
        out.append((lo, hi, lc, hc))
    return out


def intersect_intervals(a: list[Interval], b: list[Interval]) -> list[Interval]:
    return merge_intervals([w for u in a for v in b if (w := _intersect_one(u, v)) is not None])


def _test_point(left: Any, right: Any) -> Fraction:
    if left == NEG_INF and right == POS_INF:
        return Fraction(0)
    if left == NEG_INF:
        return right - 1
    if right == POS_INF:
        return left + 1
    return (left + right) / 2


def _linear_piece(relation: dict[str, Any], t: Fraction) -> tuple[Fraction, Fraction]:
    """Slope and constant of lhs - rhs on the piece containing ``t`` (no argument vanishes at t)."""
    slope = constant = Fraction(0)
    for sign, side in ((1, relation["lhs"]), (-1, relation["rhs"])):
        for term in side:
            if "abs" in term:
                a, b = form_coefficients(term["abs"])
                k = parse_exact_rational(term["coef"]) * (1 if a * t + b > 0 else -1)
            else:
                a, b = form_coefficients(term["poly"])
                k = Fraction(1)
            slope += sign * k * a
            constant += sign * k * b
    return slope, constant


def _linear_solution(slope: Fraction, constant: Fraction, op: str) -> list[Interval]:
    if slope == 0:
        return [_WHOLE_LINE] if _holds(op, constant) else []
    root = -constant / slope
    if op == "=":
        return [(root, root, True, True)]
    closed = op in ("<=", ">=")
    if (op in ("<", "<=")) == (slope > 0):
        return [(NEG_INF, root, False, closed)]
    return [(root, POS_INF, closed, False)]


def solve_relation(relation: dict[str, Any]) -> list[Interval]:
    points = breakpoints([relation])
    cuts = [NEG_INF, *points, POS_INF]
    pieces: list[Interval] = []
    for left, right in zip(cuts, cuts[1:]):
        slope, constant = _linear_piece(relation, _test_point(left, right))
        for half in _linear_solution(slope, constant, relation["op"]):
            hit = _intersect_one(half, (left, right, False, False))
            if hit is not None:
                pieces.append(hit)
    pieces.extend((p, p, True, True) for p in points if relation_holds(relation, p))
    return merge_intervals(pieces)


def solve_system(relations: list[dict[str, Any]]) -> list[Interval]:
    result: list[Interval] = [_WHOLE_LINE]
    for relation in relations:
        result = intersect_intervals(result, solve_relation(relation))
    return result


def _bound_text(value: Any) -> str:
    if value == NEG_INF:
        return "-oo"
    if value == POS_INF:
        return "oo"
    return canonical_rational(value)


def serialize_intervals(items: list[Interval]) -> list[list[Any]]:
    return [[_bound_text(lo), _bound_text(hi), bool(lc), bool(hc)] for lo, hi, lc, hc in items]


def parse_bound(value: Any) -> Any:
    if value == "-oo":
        return NEG_INF
    if value == "oo":
        return POS_INF
    return parse_exact_rational(value)


def parse_intervals(raw: Any) -> list[Interval]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("interval set must be a non-empty list")
    items = []
    for item in raw:
        lo, hi, lc, hc = item
        lo, hi = parse_bound(lo), parse_bound(hi)
        if not (lo < hi or (lo == hi and lc and hc)) or (lc and lo == NEG_INF) or (hc and hi == POS_INF):
            raise ValueError("malformed interval")
        items.append((lo, hi, bool(lc), bool(hc)))
    if merge_intervals(items) != sorted(items, key=lambda i: (i[0], not i[2])):
        raise ValueError("interval set must be disjoint and non-adjacent")
    return merge_intervals(items)


def interval_sample_points(items: list[Interval]) -> list[tuple[Fraction, bool]]:
    """(x, expected membership) probes: interiors, endpoints and every gap."""
    probes: list[tuple[Fraction, bool]] = []
    edges: list[Any] = [NEG_INF]
    for lo, hi, lc, hc in items:
        if lo == hi:
            probes.append((lo, True))
        else:
            probes.append((_test_point(lo, hi), True))
            if lo != NEG_INF:
                probes.append((lo, lc))
            if hi != POS_INF:
                probes.append((hi, hc))
        edges.extend([lo, hi])
    edges.append(POS_INF)
    for left, right in zip(edges[::2], edges[1::2]):
        if left < right:
            probes.append((_test_point(left, right), False))
    return probes


# --- number-line distance and division points ------------------------------------

def evaluate_number_line_division_points(points: dict[str, Any], parts: list[dict[str, Any]]) -> dict[str, Any]:
    a, b = parse_exact_rational(points["A"]), parse_exact_rational(points["B"])
    out = []
    for part in parts:
        find = part["find"]
        if find == "distance":
            value = abs(a - b)
        else:
            m, n = (parse_exact_rational(r) for r in part["ratio"])
            value = (n * a + m * b) / (m + n) if find == "internal" else (m * b - n * a) / (m - n)
        out.append({"find": find, "value": canonical_rational(value)})
    return {"parts": out}


# --- equations and inequalities --------------------------------------------------

def solve_absolute_value_equations(equations: list[dict[str, Any]]) -> dict[str, Any]:
    parts = []
    for equation in equations:
        solution = solve_relation(equation)
        if any(lo != hi for lo, hi, _, _ in solution):
            raise ValueError("equation_solution_not_discrete")
        parts.append({
            "solutions": [canonical_rational(lo) for lo, _, _, _ in solution],
            "breakpoints": [canonical_rational(p) for p in breakpoints([equation])],
        })
    return {"parts": parts}


def solve_absolute_value_inequalities(systems: list[dict[str, Any]]) -> dict[str, Any]:
    parts = []
    for system in systems:
        relations = system["relations"]
        parts.append({
            "intervals": serialize_intervals(solve_system(relations)),
            "relation_solutions": [serialize_intervals(solve_relation(r)) for r in relations],
        })
    return {"parts": parts}


# --- parameter recovery for |kx+m| op r ------------------------------------------

def _template(relation: dict[str, Any]) -> dict[str, Any]:
    slope, known, shift = Fraction(0), Fraction(0), None
    for coefficient, degree in relation["inner"]:
        if isinstance(coefficient, dict):
            shift = (coefficient["param"], int(coefficient["sign"]))
        elif degree == 1:
            slope += parse_exact_rational(coefficient)
        else:
            known += parse_exact_rational(coefficient)
    bound = relation["bound"]
    return {
        "k": slope, "m_known": known, "shift": shift, "op": relation["op"],
        "bound_param": bound["param"] if isinstance(bound, dict) else None,
        "r_known": None if isinstance(bound, dict) else parse_exact_rational(bound),
    }


def _instantiate(tpl: dict[str, Any], values: dict[str, Fraction]) -> dict[str, Any]:
    m = tpl["m_known"] + (tpl["shift"][1] * values[tpl["shift"][0]] if tpl["shift"] else 0)
    r = values[tpl["bound_param"]] if tpl["bound_param"] else tpl["r_known"]
    inner = [[canonical_rational(tpl["k"]), 1], [canonical_rational(m), 0]]
    return {"lhs": [{"abs": inner, "coef": "1"}], "op": tpl["op"], "rhs": [{"poly": [[canonical_rational(r), 0]]}]}


def _candidates(tpl: dict[str, Any], ends: list[Fraction]) -> list[dict[str, Fraction]]:
    k, known, shift, bound = tpl["k"], tpl["m_known"], tpl["shift"], tpl["bound_param"]
    out: list[dict[str, Fraction]] = []
    if shift and bound:
        for e1, e2 in combinations(ends, 2):
            m = -k * (e1 + e2) / 2
            out.append({shift[0]: (m - known) / shift[1], bound: abs(k) * (e2 - e1) / 2})
    elif shift:
        for e in ends:
            for sigma in (1, -1):
                out.append({shift[0]: (sigma * tpl["r_known"] - k * e - known) / shift[1]})
    elif bound:
        for e in ends:
            for sigma in (1, -1):
                out.append({bound: sigma * (k * e + known)})
    else:
        out.append({})
    return out


def recover_absolute_value_parameters(
    relations: list[dict[str, Any]], parameters: list[str], target: list[list[Any]]
) -> dict[str, Any]:
    """Find the unique parameter values for which the system's solution set is ``target``."""
    target_set = parse_intervals(target)
    ends = sorted({e for lo, hi, _, _ in target_set for e in (lo, hi) if e not in (NEG_INF, POS_INF)})
    templates = [_template(r) for r in relations]
    found: dict[tuple[str, ...], dict[str, Fraction]] = {}
    checked = 0
    for combo in product(*[_candidates(t, ends) for t in templates]):
        values: dict[str, Fraction] = {}
        for item in combo:
            values.update(item)
        if set(values) != set(parameters):
            continue
        checked += 1
        if solve_system([_instantiate(t, values) for t in templates]) == target_set:
            found[tuple(canonical_rational(values[p]) for p in parameters)] = values
    if len(found) != 1:
        raise ValueError(f"parameter_recovery_not_unique:{len(found)}")
    values = next(iter(found.values()))
    return {
        "values": {p: canonical_rational(values[p]) for p in parameters},
        "relations": [_instantiate(t, values) for t in templates],
        "candidates_checked": checked,
    }


# --- statements and weighted points ----------------------------------------------

def weighted_position(weights: list[Any]) -> Fraction:
    """Position t of (p·a + q·b)/(p+q) = a + t(b - a); a larger t is a larger number when a < b."""
    p, q = (parse_exact_rational(w) for w in weights)
    return q / (p + q)


def evaluate_absolute_value_statements(statements: list[dict[str, Any]]) -> dict[str, Any]:
    truths, details = [], []
    for statement in statements:
        kind = statement["kind"]
        if kind == "distance_expression":
            u, operator, v = statement["claim"]
            u, v = parse_exact_rational(u), parse_exact_rational(v)
            claimed = abs(u - v) if operator == "-" else abs(u + v)
            actual = abs(parse_exact_rational(statement["points"]["A"]) - parse_exact_rational(statement["points"]["B"]))
            truths.append(claimed == actual)
            details.append({"claimed": canonical_rational(claimed), "actual": canonical_rational(actual)})
        elif kind == "weighted_point_order":
            left, right = weighted_position(statement["left"]), weighted_position(statement["right"])
            truths.append(_holds(statement["op"], left - right))
            details.append({"left_position": canonical_rational(left), "right_position": canonical_rational(right)})
        else:
            left, right = solve_relation(statement["left"]), solve_relation(statement["right"])
            truths.append(left == right)
            details.append({"left": serialize_intervals(left), "right": serialize_intervals(right)})
    return {"truth_values": truths, "details": details}


def select_extreme_weighted_point(options: list[list[Any]], extreme: str) -> dict[str, Any]:
    positions = [weighted_position(w) for w in options]
    best = max(positions) if extreme == "max" else min(positions)
    if positions.count(best) != 1:
        raise ValueError("extreme_weighted_point_not_unique")
    return {"choice": positions.index(best) + 1, "positions": [canonical_rational(t) for t in positions]}


# --- givens (constraints or seeded defaults) -------------------------------------

def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _division_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    points, parts = constraints.get("points"), constraints.get("parts")
    if points is None:
        a, b = rng.sample(range(-15, 16), 2)
        m, n = rng.sample(range(1, 6), 2)
        points = {"A": a, "B": b}
        parts = [{"find": "internal", "label": "P", "variable": "x", "ratio": [m, n]},
                 {"find": "external", "label": "Q", "variable": "y", "ratio": [m, n]}]
    a, b = parse_exact_rational(points["A"]), parse_exact_rational(points["B"])
    if a == b:
        raise ValueError("A and B must be distinct")
    if not isinstance(parts, list) or not 1 <= len(parts) <= _MAX_PARTS:
        raise ValueError("parts must be a list of 1..4 items")
    out_parts = []
    for part in parts:
        find = part.get("find")
        item: dict[str, Any] = {"find": find}
        if find in ("internal", "external"):
            m, n = (_positive_int(r, "ratio") for r in part["ratio"])
            if find == "external" and m == n:
                raise ValueError("external division needs unequal ratio terms")
            item.update(label=str(part.get("label", "P")), ratio=[m, n])
            if part.get("variable"):
                item["variable"] = str(part["variable"])
            style = part.get("ratio_style", "colon")
            if style not in ("colon", "multiple") or (style == "multiple" and n != 1):
                raise ValueError("ratio_style must be colon, or multiple with n = 1")
            item["ratio_style"] = style
            if find == "internal":
                position = part.get("position", "on_segment")
                if position not in ("on_segment", "between"):
                    raise ValueError("position must be on_segment or between")
                item["position"] = position
            else:
                order = part.get("segment_order", "BQ")
                if order not in ("BQ", "QB"):
                    raise ValueError("segment_order must be BQ or QB")
                item["segment_order"] = order
        elif find != "distance":
            raise ValueError("find must be distance, internal or external")
        out_parts.append(item)
    intro = constraints.get("intro", "points_first")
    if intro not in ("points_first", "line_first"):
        raise ValueError("intro must be points_first or line_first")
    return {"points": {"A": canonical_rational(a), "B": canonical_rational(b)}, "parts": out_parts, "intro": intro}


def _abs_side(a: int, b: int) -> list[dict[str, Any]]:
    return [{"abs": [[a, 1], [b, 0]] if b else [[a, 1]]}]


def _const_side(c: Any) -> list[dict[str, Any]]:
    return [{"poly": [[c, 0]]}]


def _equation_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    equations = constraints.get("equations")
    if equations is None:
        a, b, c = rng.randint(1, 4), rng.choice([-5, -3, -2, -1, 1, 2, 4]), rng.randint(1, 9)
        equations = [{"lhs": _abs_side(a, b), "op": "=", "rhs": _const_side(c)}]
    if not isinstance(equations, list) or not 1 <= len(equations) <= _MAX_PARTS:
        raise ValueError("equations must be a list of 1..4 relations")
    prompt = constraints.get("prompt", "solve")
    if prompt not in ("solve", "find_real_x"):
        raise ValueError("prompt must be solve or find_real_x")
    return {"equations": [_relation(e, ops=("=",)) for e in equations], "prompt": prompt,
            "state_solution_count": bool(constraints.get("state_solution_count", False))}


def _system(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("system must be a mapping")
    relations = raw.get("relations")
    if not isinstance(relations, list) or not 1 <= len(relations) <= _MAX_RELATIONS:
        raise ValueError("system needs 1..3 relations")
    relations = [_relation(r, ops=INEQUALITY_OPS) for r in relations]
    joiner = raw.get("joiner", "and")
    if joiner not in ("and", "chain"):
        raise ValueError("joiner must be and or chain")
    if joiner == "chain" and (len(relations) != 2 or relations[0]["rhs"] != relations[1]["lhs"]):
        raise ValueError("chain joiner needs two relations sharing the middle side")
    return {"relations": relations, "joiner": joiner}


def _inequality_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    systems = constraints.get("systems")
    if systems is None:
        a, b, c = rng.randint(1, 4), rng.choice([-5, -3, -2, -1, 1, 2, 4]), rng.randint(1, 9)
        systems = [{"relations": [{"lhs": _abs_side(a, b), "op": rng.choice(INEQUALITY_OPS), "rhs": _const_side(c)}]}]
    if not isinstance(systems, list) or not 1 <= len(systems) <= _MAX_PARTS:
        raise ValueError("systems must be a list of 1..4 items")
    return {"systems": [_system(s) for s in systems]}


def _parameter_inner(raw: Any, parameters: set[str]) -> list[list[Any]]:
    if not isinstance(raw, list) or not raw or len(raw) > _MAX_TERMS:
        raise ValueError("inner form must be a non-empty list")
    out, slope = [], Fraction(0)
    for coefficient, degree in raw:
        if isinstance(coefficient, dict):
            if degree != 0 or coefficient.get("param") not in parameters or coefficient.get("sign") not in (1, -1):
                raise ValueError("parameter may only appear as a signed constant term")
            out.append([{"param": coefficient["param"], "sign": coefficient["sign"]}, 0])
        else:
            out.append(_form([[coefficient, degree]])[0])
            if degree == 1:
                slope += parse_exact_rational(coefficient)
    if slope == 0:
        raise ValueError("inner form must depend on x")
    return out


def _recovery_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    relations = constraints.get("relations")
    if relations is None:
        k, lo = rng.randint(1, 3), rng.randint(-8, 4)
        hi = lo + 2 * rng.randint(1, 5)
        relations = [{"inner": [[k, 1], [{"param": "a", "sign": 1}, 0]], "op": "<=", "bound": {"param": "b"}}]
        constraints = {"parameters": ["a", "b"], "target": [[lo, hi, True, True]], "prompt": "real_parameters"}
    parameters = constraints.get("parameters")
    if not isinstance(parameters, list) or not parameters or len(set(parameters)) != len(parameters):
        raise ValueError("parameters must be a non-empty list of distinct names")
    names = set(parameters)
    if not isinstance(relations, list) or not 1 <= len(relations) <= _MAX_RELATIONS:
        raise ValueError("relations must be a list of 1..3 items")
    out, used = [], []
    for relation in relations:
        if relation.get("op") not in INEQUALITY_OPS:
            raise ValueError("relation op must be an inequality")
        inner = _parameter_inner(relation["inner"], names)
        bound = relation["bound"]
        if isinstance(bound, dict):
            if bound.get("param") not in names:
                raise ValueError("unknown bound parameter")
            bound = {"param": bound["param"]}
        else:
            bound = canonical_rational(bound)
        used += [c["param"] for c, _ in inner if isinstance(c, dict)] + ([bound["param"]] if isinstance(bound, dict) else [])
        out.append({"inner": inner, "op": relation["op"], "bound": bound})
    if sorted(used) != sorted(parameters):
        raise ValueError("every parameter must appear exactly once")
    target = serialize_intervals(parse_intervals(constraints.get("target")))
    if all(lo in ("-oo", "oo") and hi in ("-oo", "oo") for lo, hi, _, _ in target):
        raise ValueError("target needs a finite endpoint")
    prompt = constraints.get("prompt", "real_parameters")
    if prompt not in ("real_parameters", "system", "body_temperature", "pregnancy_weeks"):
        raise ValueError("unsupported prompt")
    if prompt == "body_temperature" and not (
        len(target) == 2 and target[0][0] == "-oo" and target[1][1] == "oo" and not target[0][3] and not target[1][2]
    ):
        raise ValueError("body_temperature prompt needs x < low or x > high")
    if prompt == "pregnancy_weeks" and not (len(target) == 1 and target[0][2] and target[0][3] and "oo" not in target[0][1]):
        raise ValueError("pregnancy_weeks prompt needs a closed bounded range")
    if prompt in ("real_parameters", "body_temperature", "pregnancy_weeks") and len(out) != 1:
        raise ValueError("single-relation prompt needs exactly one relation")
    return {"relations": out, "parameters": list(parameters), "target": target, "prompt": prompt}


def _relation_for_statement(raw: Any) -> dict[str, Any]:
    return _relation(raw, ops=RELATION_OPS)


def _statement(raw: Any) -> dict[str, Any]:
    kind = raw.get("kind") if isinstance(raw, dict) else None
    if kind == "distance_expression":
        u, operator, v = raw["claim"]
        if operator not in ("-", "+"):
            raise ValueError("claim operator must be - or +")
        points = {"A": canonical_rational(raw["points"]["A"]), "B": canonical_rational(raw["points"]["B"])}
        return {"kind": kind, "points": points, "claim": [canonical_rational(u), operator, canonical_rational(v)]}
    if kind == "weighted_point_order":
        if raw.get("op") not in RELATION_OPS:
            raise ValueError("unsupported comparison")
        left = [_positive_int(w, "weight") for w in raw["left"]]
        right = [_positive_int(w, "weight") for w in raw["right"]]
        return {"kind": kind, "left": left, "op": raw["op"], "right": right}
    if kind == "same_solution_set":
        return {"kind": kind, "left": _relation_for_statement(raw["left"]), "right": _relation_for_statement(raw["right"])}
    raise ValueError(f"unsupported statement kind: {kind}")


def _statement_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    statements = constraints.get("statements")
    if statements is None:
        a, b = rng.sample(range(-9, 10), 2)
        statements = [{"kind": "distance_expression", "points": {"A": a, "B": b}, "claim": [a, rng.choice("-+"), b]}]
    if not isinstance(statements, list) or not 1 <= len(statements) <= _MAX_PARTS:
        raise ValueError("statements must be a list of 1..4 items")
    labels = constraints.get("item_labels") or []
    if not isinstance(labels, list) or (labels and len(labels) != len(statements)):
        raise ValueError("item_labels must match statements")
    return {"statements": [_statement(s) for s in statements], "item_labels": [str(x) for x in labels]}


def _choice_givens(constraints: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    options = constraints.get("options")
    if options is None:
        pool = [[p, q] for p in range(1, 5) for q in range(1, 5)]
        while True:
            options = rng.sample(pool, 4)
            positions = [weighted_position(o) for o in options]
            if len(set(positions)) == 4:
                break
    if not isinstance(options, list) or not 2 <= len(options) <= _MAX_OPTIONS:
        raise ValueError("options must be a list of 2..4 weighted points")
    extreme = constraints.get("extreme", "max")
    if extreme not in ("max", "min"):
        raise ValueError("extreme must be max or min")
    return {"options": [[_positive_int(w, "weight") for w in o] for o in options], "extreme": extreme}


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "evaluate_number_line_division_points": (
        _division_givens, lambda g: evaluate_number_line_division_points(g["points"], g["parts"]),
    ),
    "solve_absolute_value_equations": (_equation_givens, lambda g: solve_absolute_value_equations(g["equations"])),
    "solve_absolute_value_inequalities": (_inequality_givens, lambda g: solve_absolute_value_inequalities(g["systems"])),
    "recover_absolute_value_parameters": (
        _recovery_givens, lambda g: recover_absolute_value_parameters(g["relations"], g["parameters"], g["target"]),
    ),
    "evaluate_absolute_value_statements": (_statement_givens, lambda g: evaluate_absolute_value_statements(g["statements"])),
    "select_extreme_weighted_point": (_choice_givens, lambda g: select_extreme_weighted_point(g["options"], g["extreme"])),
}
OPERATIONS = tuple(_OPERATIONS)


def build_absolute_value_relations_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_absolute_value_relations_operation:{operation}")
    seed_value = 0 if seed is None else int(seed)
    rng = random.Random(f"{DOMAIN_KEY}:{operation}:{seed_value}")
    make_givens, solve = _OPERATIONS[operation]
    givens = make_givens(constraints if isinstance(constraints, dict) else {}, rng)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": solve(givens),
        "validation_facts": {"domain_operation": operation, "seed": seed_value},
    }


# --- validators ------------------------------------------------------------------

def _validator(operation: str) -> Callable[[Callable[[dict[str, Any], dict[str, Any]], bool]], Callable[[Any], bool]]:
    def wrap(check: Callable[[dict[str, Any], dict[str, Any]], bool]) -> Callable[[Any], bool]:
        def validate(matrix: Any) -> bool:
            try:
                facts = matrix.get("validation_facts") or {}
                if (
                    matrix.get("domain") != DOMAIN_KEY
                    or matrix.get("domain_operation") != operation
                    or facts.get("domain_operation") != operation
                ):
                    return False
                if _OPERATIONS[operation][1](matrix["givens"]) != matrix["answer"]:
                    return False
                return bool(check(matrix["givens"], matrix["answer"]))
            except Exception:
                return False

        validate.__name__ = f"validate_{operation}_matrix"
        return validate

    return wrap


def _set_matches_relations(relations: list[dict[str, Any]], intervals: list[list[Any]]) -> bool:
    return all(
        all(relation_holds(r, x) for r in relations) == member
        for x, member in interval_sample_points(parse_intervals(intervals))
    ) if intervals else False


@_validator("evaluate_number_line_division_points")
def validate_evaluate_number_line_division_points_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, b = parse_exact_rational(givens["points"]["A"]), parse_exact_rational(givens["points"]["B"])
    for part, result in zip(givens["parts"], answer["parts"]):
        x = parse_exact_rational(result["value"])
        if part["find"] == "distance":
            if x != abs(a - b):
                return False
            continue
        m, n = part["ratio"]
        inside = min(a, b) < x < max(a, b)
        if inside != (part["find"] == "internal") or abs(x - a) * n != abs(b - x) * m:
            return False
    return len(answer["parts"]) == len(givens["parts"])


@_validator("solve_absolute_value_equations")
def validate_solve_absolute_value_equations_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for equation, part in zip(givens["equations"], answer["parts"]):
        values = [parse_exact_rational(s) for s in part["solutions"]]
        if values != sorted(set(values)) or not all(relation_holds(equation, x) for x in values):
            return False
    return len(answer["parts"]) == len(givens["equations"])


@_validator("solve_absolute_value_inequalities")
def validate_solve_absolute_value_inequalities_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for system, part in zip(givens["systems"], answer["parts"]):
        if part["intervals"] and not _set_matches_relations(system["relations"], part["intervals"]):
            return False
    return len(answer["parts"]) == len(givens["systems"])


@_validator("recover_absolute_value_parameters")
def validate_recover_absolute_value_parameters_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return set(answer["values"]) == set(givens["parameters"]) and _set_matches_relations(answer["relations"], givens["target"])


@_validator("evaluate_absolute_value_statements")
def validate_evaluate_absolute_value_statements_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for statement, truth in zip(givens["statements"], answer["truth_values"]):
        if statement["kind"] == "weighted_point_order":
            a, b = Fraction(0), Fraction(1)
            left = (statement["left"][0] * a + statement["left"][1] * b) / sum(statement["left"])
            right = (statement["right"][0] * a + statement["right"][1] * b) / sum(statement["right"])
            if _holds(statement["op"], left - right) != truth:
                return False
    return len(answer["truth_values"]) == len(givens["statements"])


@_validator("select_extreme_weighted_point")
def validate_select_extreme_weighted_point_matrix(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a, b = Fraction(-3), Fraction(5)
    values = [(p * a + q * b) / (p + q) for p, q in givens["options"]]
    best = max(values) if givens["extreme"] == "max" else min(values)
    return values.index(best) + 1 == answer["choice"] and values.count(best) == 1
