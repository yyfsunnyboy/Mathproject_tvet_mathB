"""Exact domain operations for general-high Mathematics 2, Unit 2 級數 (arithmetic / geometric series, S_n -> a_n, sums of powers).

Domain key ``sequence.series_sums``.  Components pass the *stated data of the problem*; every answer is derived here with exact
arithmetic (sympy Rationals / radicals).  Each operation owns a validator that re-derives the answer a different way (term by term
enumeration, day-by-day or layer-by-layer simulation, coordinate geometry, substitute-and-check) and never calls the construction
a second time.  Numbers cross the JSON boundary as ints or strings (``"1/2"``, ``"-3"``, ``"sqrt(2)"``).
"""

from __future__ import annotations

from typing import Any, Callable

import sympy as sp

DOMAIN_KEY = "sequence.series_sums"
N = sp.Symbol("n", integer=True, positive=True)


def num(v: Any) -> sp.Expr:
    if isinstance(v, bool):
        raise ValueError("bool_is_not_a_number")
    if isinstance(v, sp.Basic):
        return sp.nsimplify(v)
    return sp.sympify(str(v).strip(), rational=True)


def text(v: Any) -> str:
    e = sp.radsimp(sp.expand(num(v)))
    return str(e) if e.is_Rational else sp.sstr(e).replace(" ", "")


def tex(v: Any) -> str:
    return sp.latex(sp.radsimp(sp.expand(num(v))))


def is_rational(v: Any) -> bool:
    return bool(sp.radsimp(sp.expand(num(v))).is_Rational)


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _int(v: Any, name: str, low: int | None = None) -> int:
    e = num(v)
    if not e.is_Integer or (low is not None and e < low):
        raise ValueError(f"not_an_integer:{name}")
    return int(e)


def _same(a: Any, b: Any) -> bool:
    return sp.simplify(num(a) - num(b)) == 0


# --- 1. arithmetic series items --------------------------------------------------------------------------------------------

def _ap_count(first: sp.Expr, d: sp.Expr, last: sp.Expr) -> int:
    if d == 0:
        raise ValueError("zero_common_difference")
    n = (last - first) / d + 1
    if not n.is_Integer or n < 2:
        raise ValueError("last_term_not_in_progression")
    return int(n)


def arithmetic_series_items(items: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    out = []
    for item in items:
        kind = item["kind"]
        if kind == "d_from_sum":
            a1, n, s = num(item["a1"]), _int(item["n"], "n", 2), num(item["S"])
            d = (2 * s / n - 2 * a1) / (n - 1)
            out.append({"kind": kind, "value": text(d)})
        elif kind == "sum_terms":
            first, d, last = num(item["first"]), num(item["d"]), num(item["last"])
            n = _ap_count(first, d, last)
            out.append({"kind": kind, "value": text(n * (first + last) / 2), "n": n})
        else:
            raise ValueError(f"unsupported_item:{kind}")
    return {"items": out}


def _check_arithmetic_series_items(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for item, got in zip(givens["items"], answer["items"]):
        if item["kind"] == "d_from_sum":
            a1, n, s, d = num(item["a1"]), int(item["n"]), num(item["S"]), num(got["value"])
            if sum(a1 + k * d for k in range(n)) != s:
                return False
        else:
            first, d, last = num(item["first"]), num(item["d"]), num(item["last"])
            terms, t = [], first
            while (t <= last) if d > 0 else (t >= last):
                terms.append(t)
                t += d
            if terms[-1] != last or len(terms) != got["n"] or sum(terms) != num(got["value"]):
                return False
    return len(givens["items"]) == len(answer["items"])


# --- 2. arithmetic series relations ------------------------------------------------------------------------------------------

def arithmetic_series_relation(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "mid_term":  # a_m given -> a_1 + a_(2m-1) and S_(2m-1)
        m, v = _int(g["m"], "m", 2), num(g["value"])
        n = 2 * m - 1
        return {"kind": kind, "n": n, "pair_sum": text(2 * v), "total": text(n * v)}
    if kind == "pair_from_sum":  # S_n given -> a_i + a_j for pairs with i + j = n + 1
        n, s = _int(g["n"], "n", 2), num(g["S"])
        pairs = [[_int(i, "i", 1), _int(j, "j", 1)] for i, j in g["pairs"]]
        if any(i + j != n + 1 for i, j in pairs):
            raise ValueError("pair_not_symmetric")
        return {"kind": kind, "values": [text(2 * s / n) for _ in pairs]}
    if kind == "mid_total":  # n rows, the middle one has v seats
        n, v = _int(g["n"], "n", 3), num(g["mid"])
        if n % 2 == 0:
            raise ValueError("needs_a_middle_row")
        return {"kind": kind, "total": text(n * v)}
    if kind == "front_back":  # first two terms and last two terms
        n, f, l = _int(g["n"], "n", 4), num(g["first2"]), num(g["last2"])
        return {"kind": kind, "total": text(n * (f + l) / 4)}
    if kind == "threshold_count":  # progression from `first` to `last`, total must exceed `threshold`
        first, last, th = num(g["first"]), num(g["last"]), num(g["threshold"])
        n = sp.floor(2 * th / (first + last)) + 1
        n = max(int(n), 2)
        return {"kind": kind, "count": n}
    if kind == "two_walls":  # two diggers, first-day amounts and daily increments
        thick = num(g["thick"])
        b1, bd, s1, sd = num(g["big1"]), num(g["bigd"]), num(g["small1"]), num(g["smalld"])
        # closed form: n(2b1+(n-1)bd)/2 + n(2s1+(n-1)sd)/2 >= thick
        n = sp.Symbol("n", positive=True)
        expr = n * (2 * b1 + (n - 1) * bd) / 2 + n * (2 * s1 + (n - 1) * sd) / 2 - thick
        root = max(sp.solve(sp.Eq(expr, 0), n), key=lambda r: float(r))
        days = int(sp.ceiling(root))
        return {"kind": kind, "days": days}
    raise ValueError(f"unsupported_kind:{kind}")


def _check_arithmetic_series_relation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = givens["kind"]
    if kind == "mid_term":
        m, v = int(givens["m"]), num(givens["value"])
        # an AP with a_m = v: take any difference, rebuild the terms
        for d in (1, -3, sp.Rational(1, 2)):
            terms = [v + (k - m) * d for k in range(1, 2 * m)]
            if terms[0] + terms[-1] != num(answer["pair_sum"]) or sum(terms) != num(answer["total"]):
                return False
        return answer["n"] == 2 * m - 1
    if kind == "pair_from_sum":
        n, s = int(givens["n"]), num(givens["S"])
        for d in (1, 5, -2):
            a1 = (2 * s / n - (n - 1) * d) / 2
            terms = [a1 + k * d for k in range(n)]
            if sum(terms) != s:
                return False
            for (i, j), got in zip(givens["pairs"], answer["values"]):
                if terms[i - 1] + terms[j - 1] != num(got):
                    return False
        return len(givens["pairs"]) == len(answer["values"])
    if kind == "mid_total":
        n, v = int(givens["n"]), num(givens["mid"])
        for d in (2, 3, 0):
            if sum(v + (k - (n + 1) // 2) * d for k in range(1, n + 1)) != num(answer["total"]):
                return False
        return True
    if kind == "front_back":
        n, f, l = int(givens["n"]), num(givens["first2"]), num(givens["last2"])
        a1, d = sp.symbols("a1 d")
        sol = sp.solve([sp.Eq(2 * a1 + d, f), sp.Eq(2 * a1 + (2 * n - 3) * d, l)], [a1, d], dict=True)[0]
        return sum(sol[a1] + k * sol[d] for k in range(n)) == num(answer["total"])
    if kind == "threshold_count":
        first, last, th = num(givens["first"]), num(givens["last"]), num(givens["threshold"])
        n = 2
        while n * (first + last) / 2 <= th:
            n += 1
        return n == answer["count"] and (n == 2 or (n - 1) * (first + last) / 2 <= th)
    if kind == "two_walls":
        thick = num(givens["thick"])
        total_b = total_s = day = 0
        while total_b + total_s < thick:
            day += 1
            total_b += num(givens["big1"]) + (day - 1) * num(givens["bigd"])
            total_s += num(givens["small1"]) + (day - 1) * num(givens["smalld"])
        return day == answer["days"]
    return False


# --- 3. geometric series items ----------------------------------------------------------------------------------------------

def _gp_sum(a1: sp.Expr, r: sp.Expr, n: int) -> sp.Expr:
    if r == 1:
        return a1 * n
    return sp.radsimp(sp.expand(a1 * (1 - r ** n) / (1 - r)))


def geometric_series_items(items: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    out = []
    for item in items:
        kind = item["kind"]
        if kind == "ratio_sum":
            a1, r, n = num(item["a1"]), num(item["r"]), _int(item["n"], "n", 2)
            if r in (0, 1):
                raise ValueError("degenerate_ratio")
            out.append({"kind": kind, "value": text(_gp_sum(a1, r, n)), "n": n})
        elif kind == "list_sum":
            terms, last = [num(t) for t in item["terms"]], num(item["last"])
            r = terms[1] / terms[0]
            if r in (0, 1) or terms[2] / terms[1] != r:
                raise ValueError("not_geometric")
            n, t = 1, terms[0]
            while t != last and n < 60:
                t, n = t * r, n + 1
            if t != last:
                raise ValueError("last_term_not_in_progression")
            out.append({"kind": kind, "value": text(_gp_sum(terms[0], r, n)), "n": n, "ratio": text(r)})
        else:
            raise ValueError(f"unsupported_item:{kind}")
    return {"items": out}


def _check_geometric_series_items(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for item, got in zip(givens["items"], answer["items"]):
        if item["kind"] == "ratio_sum":
            a1, r, n = num(item["a1"]), num(item["r"]), int(item["n"])
            if not _same(sum(a1 * r ** k for k in range(n)), got["value"]):
                return False
        else:
            terms = [num(t) for t in item["terms"]]
            r, t, total, count = terms[1] / terms[0], terms[0], 0, 0
            while True:
                total += t
                count += 1
                if t == num(item["last"]):
                    break
                t = t * r
                if count > 60:
                    return False
            if count != got["n"] or not _same(total, got["value"]):
                return False
    return len(givens["items"]) == len(answer["items"])


# --- 4. geometric series relations -------------------------------------------------------------------------------------------

def geometric_series_relation(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "two_terms":  # a_p = A, a_q = B -> every possible S_n
        p, q, a_, b_, n = _int(g["p"], "p", 1), _int(g["q"], "q", 2), num(g["A"]), num(g["B"]), _int(g["n"], "n", 2)
        ratio_pow = b_ / a_
        r = sp.Symbol("r")
        sols = [s for s in sp.solve(r ** (q - p) - ratio_pow, r) if s.is_real and s.is_Rational]
        if not sols or any(s in (0, 1) for s in sols):
            raise ValueError("no_rational_ratio")
        sums = sorted({sp.radsimp(_gp_sum(a_ / s ** (p - 1), s, n)) for s in sols})
        return {"kind": kind, "ratios": [text(s) for s in sorted(sols)], "sums": [text(x) for x in sums]}
    if kind == "consecutive_triples":  # a1+a2+a3 = A, a2+a3+a4 = B
        a_, b_, n = num(g["A"]), num(g["B"]), _int(g["n"], "n", 2)
        r = b_ / a_
        if r in (0, 1) or 1 + r + r ** 2 == 0:
            raise ValueError("degenerate_ratio")
        a1 = a_ / (1 + r + r ** 2)
        return {"kind": kind, "ratio": text(r), "a1": text(a1), "sum": text(_gp_sum(a1, r, n))}
    if kind == "first_last_sum":  # a1, last term, S given -> ratio and number of terms
        a1, last, s = num(g["a1"]), num(g["last"]), num(g["S"])
        r = (s - a1) / (s - last)
        if r in (0, 1):
            raise ValueError("degenerate_ratio")
        n, t = 1, a1
        while t != last and n < 60:
            t, n = t * r, n + 1
        if t != last:
            raise ValueError("last_term_not_in_progression")
        return {"kind": kind, "ratio": text(r), "n": n}
    if kind == "layers":  # each item carries `kids` smaller ones weighing `frac` of it
        w, frac, kids, layers = num(g["W"]), num(g["frac"]), _int(g["kids"], "kids", 1), _int(g["layers"], "layers", 2)
        return {"kind": kind, "total": text(_gp_sum(w, kids * frac, layers)), "ratio": text(kids * frac)}
    if kind == "square_areas":  # angle A = 45 degrees, AB = 1: squares standing on the line, the first corner on the slanted side
        k = _int(g["k"], "k", 2)
        return {"kind": kind, "total": text(_gp_sum(sp.Integer(1), sp.Integer(4), k)), "ratio": "4"}
    if kind == "blue_squares":  # side L; figure n has all blue squares of stages 1..n
        side, n = _int(g["side"], "side", 2), _int(g["n"], "n", 2)
        count = 2 ** (n + 1) - 2
        area = sp.Integer(side) ** 2 * (1 - sp.Rational(1, 2 ** n))
        return {"kind": kind, "count": count, "area": text(area)}
    raise ValueError(f"unsupported_kind:{kind}")


def _check_geometric_series_relation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = givens["kind"]
    if kind == "two_terms":
        p, q, a_, b_, n = int(givens["p"]), int(givens["q"]), num(givens["A"]), num(givens["B"]), int(givens["n"])
        sums = set()
        for rs in answer["ratios"]:
            r = num(rs)
            a1 = a_ / r ** (p - 1)
            if a1 * r ** (q - 1) != b_:
                return False
            sums.add(sp.radsimp(sum(a1 * r ** k for k in range(n))))
        return sorted(sums) == sorted(sp.radsimp(num(x)) for x in answer["sums"])
    if kind == "consecutive_triples":
        a1, r = num(answer["a1"]), num(answer["ratio"])
        return (a1 + a1 * r + a1 * r ** 2 == num(givens["A"]) and a1 * r + a1 * r ** 2 + a1 * r ** 3 == num(givens["B"])
                and sum(a1 * r ** k for k in range(int(givens["n"]))) == num(answer["sum"]))
    if kind == "first_last_sum":
        r, n = num(answer["ratio"]), int(answer["n"])
        a1 = num(givens["a1"])
        terms = [a1 * r ** k for k in range(n)]
        return terms[-1] == num(givens["last"]) and sum(terms) == num(givens["S"])
    if kind == "layers":
        w, frac, kids, layers = num(givens["W"]), num(givens["frac"]), int(givens["kids"]), int(givens["layers"])
        total, weight, count = sp.Integer(0), w, 1
        for _ in range(layers):
            total += count * weight
            count, weight = count * kids, weight * frac
        return total == num(answer["total"])
    if kind == "square_areas":
        k = int(givens["k"])
        x, area = sp.Integer(1), sp.Integer(0)  # square i starts at x_i and its top-left corner lies on y = x, so its side is x_i
        for _ in range(k):
            side = x
            area += side ** 2
            x += side
        return area == num(answer["total"])
    if kind == "blue_squares":
        side, n = int(givens["side"]), int(givens["n"])
        whites, blue, area = [sp.Integer(side)], 0, sp.Integer(0)
        for _ in range(n):
            nxt = []
            for w in whites:
                half = w / 2
                blue += 2
                area += 2 * half ** 2
                nxt += [half, half]
            whites = nxt
        return blue == answer["count"] and area == num(answer["area"])
    return False


# --- 5. S_n -> terms --------------------------------------------------------------------------------------------------------

def _partial_sum_expr(form: dict[str, Any]) -> sp.Expr:
    kind = form["kind"]
    if kind == "exp":  # S_n = c * b**n - c  (so a_1 = S_1 fits the general term)
        c, b = num(form["c"]), num(form["base"])
        return c * b ** N - c
    if kind == "quad":  # S_n = a n^2 + b n
        return num(form["a"]) * N ** 2 + num(form["b"]) * N
    raise ValueError(f"unsupported_form:{kind}")


def _general_term(form: dict[str, Any]) -> sp.Expr:
    if form["kind"] == "exp":
        c, b = num(form["c"]), num(form["base"])
        return c * (b - 1) * b ** (N - 1)
    a, b = num(form["a"]), num(form["b"])
    return sp.expand(a * (2 * N - 1) + b)


def partial_sum_terms(form: dict[str, Any], asks: list[list[Any]], **_: Any) -> dict[str, Any]:
    s = _partial_sum_expr(form)
    general = _general_term(form)
    if sp.simplify(general.subs(N, 1) - s.subs(N, 1)) != 0:
        raise ValueError("first_term_does_not_fit")
    values = []
    for ask in asks:
        if ask[0] == "a":
            k = _int(ask[1], "k", 1)
            values.append({"ask": ["a", k], "value": text(s.subs(N, k) - (s.subs(N, k - 1) if k > 1 else 0))})
        elif ask[0] == "general":
            values.append({"ask": ["general"], "value": sp.sstr(general).replace(" ", "")})
        else:
            raise ValueError("unsupported_ask")
    return {"values": values}


def _check_partial_sum_terms(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    s = _partial_sum_expr(givens["form"])
    terms = {k: s.subs(N, k) - (s.subs(N, k - 1) if k > 1 else 0) for k in range(1, 10)}
    for got in answer["values"]:
        if got["ask"][0] == "a":
            if terms[got["ask"][1]] != num(got["value"]):
                return False
        else:
            g = sp.sympify(got["value"], locals={"n": N})
            if any(sp.simplify(g.subs(N, k) - terms[k]) != 0 for k in terms):
                return False
            if sum(g.subs(N, k) for k in range(1, 8)) != s.subs(N, 7):
                return False
    return len(answer["values"]) == len(givens["asks"])


# --- 6. sums of powers ------------------------------------------------------------------------------------------------------

def _power_sum(item: dict[str, Any]) -> sp.Expr:
    p, first, step, last = _int(item["p"], "p", 2), _int(item["first"], "first", 1), _int(item["step"], "step", 1), _int(item["last"], "last", 1)
    if (last - first) % step or last < first + 2 * step:
        raise ValueError("last_term_not_in_progression")
    j, m = sp.Symbol("j", integer=True), (last - first) // step
    return sp.summation((first + step * j) ** p, (j, 0, m))


def power_sums(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "sum_ranges":
        return {"kind": kind, "values": [text(_power_sum(it)) for it in g["items"]]}
    if kind == "layer_split":  # layers 1^2 ... L^2: the top `top` layers vs the bottom ones
        layers, top = _int(g["layers"], "layers", 3), _int(g["top"], "top", 1)
        if top >= layers:
            raise ValueError("top_must_be_smaller")
        k = sp.Symbol("k", integer=True)
        upper = sp.summation(k ** 2, (k, 1, top))
        lower = sp.summation(k ** 2, (k, top + 1, layers))
        return {"kind": kind, "top": text(upper), "bottom": text(lower), "difference": text(lower - upper)}
    if kind == "cube_total_inverse":  # sum of the first n cubes is T: find n
        n = _int(g["n"], "n", 2)
        t = (n * (n + 1) // 2) ** 2
        return {"kind": kind, "total": t, "n": n}
    if kind == "tower":  # layer i is an i x i square of cups
        layers = _int(g["layers"], "layers", 3)
        order = [_int(x, "order") for x in g["order"]]
        if sorted(order) != [0, 1, 2, 3]:
            raise ValueError("order_invalid")
        # candidate 1 (index 1) is "L^2"; the others are the textbook distractors
        correct = "ABCD"[order.index(1)]
        k = sp.Symbol("k", integer=True)
        return {"kind": kind, "layers": layers, "correct_option": correct, "layer_count": layers ** 2,
                "total": text(sp.summation(k ** 2, (k, 1, layers)))}
    raise ValueError(f"unsupported_kind:{kind}")


def _check_power_sums(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = givens["kind"]
    if kind == "sum_ranges":
        for it, got in zip(givens["items"], answer["values"]):
            if sum(t ** int(it["p"]) for t in range(int(it["first"]), int(it["last"]) + 1, int(it["step"]))) != num(got):
                return False
        return len(givens["items"]) == len(answer["values"])
    if kind == "layer_split":
        layers, top = int(givens["layers"]), int(givens["top"])
        up = sum(i * i for i in range(1, top + 1))
        low = sum(i * i for i in range(top + 1, layers + 1))
        return (up, low, low - up) == (num(answer["top"]), num(answer["bottom"]), num(answer["difference"]))
    if kind == "cube_total_inverse":
        total, n = 0, 0
        while total < answer["total"]:
            n += 1
            total += n ** 3
        return total == answer["total"] and n == answer["n"] == int(givens["n"])
    if kind == "tower":
        layers = int(givens["layers"])
        cups = [i * i for i in range(1, layers + 1)]  # layer i is an i-by-i square
        return cups[-1] == answer["layer_count"] and sum(cups) == num(answer["total"]) and "ABCD"[list(givens["order"]).index(1)] == answer["correct_option"]
    return False


# --- 7. ○× statements about series ----------------------------------------------------------------------------------------------

_CUBE_CLAIMS = {"square_of_sum": True, "quarter_form": True, "half_form": False, "squares_form": False}


def _cube_claim_value(claim: str, n: int) -> sp.Expr:
    return {"square_of_sum": (n * (n + 1) // 2) ** 2, "quarter_form": sp.Rational(n ** 2 * (n + 1) ** 2, 4),
            "half_form": sp.Rational(n ** 2 * (n + 1) ** 2, 2), "squares_form": sp.Rational(n * (n + 1) * (2 * n + 1), 6)}[claim]


def series_statements(statement: dict[str, Any], **_: Any) -> dict[str, Any]:
    kind = statement["kind"]
    if kind == "ap_center":  # a_1 + ... + a_k = k * a_c
        k, c = _int(statement["k"], "k", 3), _int(statement["c"], "c", 1)
        return {"kind": kind, "truth": bool(k % 2 == 1 and c == (k + 1) // 2)}
    if kind == "gp_formula":  # 1 + r + ... + r^m = (r^e - 1) / (r - 1)
        r, m, e = _int(statement["r"], "r", 2), _int(statement["m"], "m", 2), _int(statement["e"], "e", 2)
        return {"kind": kind, "truth": bool(e == m + 1)}
    if kind == "cube_sum":
        claim = statement["claim"]
        if claim not in _CUBE_CLAIMS:
            raise ValueError("unsupported_claim")
        return {"kind": kind, "truth": _CUBE_CLAIMS[claim]}
    raise ValueError(f"unsupported_statement:{kind}")


def _check_series_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    st = givens["statement"]
    if st["kind"] == "ap_center":
        k, c = int(st["k"]), int(st["c"])
        ok = all(sum(a1 + i * d for i in range(k)) == k * (a1 + (c - 1) * d) for a1, d in ((1, 1), (2, 5), (-3, 2), (0, 7)))
        return ok == answer["truth"]
    if st["kind"] == "gp_formula":
        r, m, e = int(st["r"]), int(st["m"]), int(st["e"])
        return (sum(r ** i for i in range(m + 1)) == sp.Rational(r ** e - 1, r - 1)) == answer["truth"]
    ok = all(sum(i ** 3 for i in range(1, n + 1)) == _cube_claim_value(st["claim"], n) for n in range(1, 9))
    return ok == answer["truth"]


# --- 8. rows of 1, 3, 5, ... ------------------------------------------------------------------------------------------------------

def fish_rows(k: int, **_: Any) -> dict[str, Any]:
    k = _int(k, "k", 3)
    return {"first_k": text(k * k), "general": "n**2", "k": k}


def _check_fish_rows(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    k = int(givens["k"])
    rows = [2 * i - 1 for i in range(1, k + 1)]
    return sum(rows) == num(answer["first_k"]) and all(sum(2 * i - 1 for i in range(1, n + 1)) == n * n for n in range(1, 12)) and answer["general"] == "n**2"


# --- registry / entrypoint ------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "arithmetic_series_items": (arithmetic_series_items, _check_arithmetic_series_items, ("items",)),
    "arithmetic_series_relation": (arithmetic_series_relation, _check_arithmetic_series_relation, ("kind",)),
    "geometric_series_items": (geometric_series_items, _check_geometric_series_items, ("items",)),
    "geometric_series_relation": (geometric_series_relation, _check_geometric_series_relation, ("kind",)),
    "partial_sum_terms": (partial_sum_terms, _check_partial_sum_terms, ("form", "asks")),
    "power_sums": (power_sums, _check_power_sums, ("kind",)),
    "series_statements": (series_statements, _check_series_statements, ("statement",)),
    "fish_rows": (fish_rows, _check_fish_rows, ("k",)),
}
OPERATIONS = tuple(_OPERATIONS)


def build_series_summation_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_series_summation_operation:{operation}")
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


def _make_validator(operation: str) -> Callable[[Any], bool]:
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if matrix.get("domain") != DOMAIN_KEY or matrix.get("domain_operation") != operation or facts.get("domain_operation") != operation:
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
