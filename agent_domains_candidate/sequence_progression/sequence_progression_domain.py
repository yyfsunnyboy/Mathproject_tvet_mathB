"""Exact domain operations for general-high Mathematics 2, Unit 1 數列 (general terms, arithmetic / geometric progressions).

Domain key ``sequence.progression``.  Components pass the *stated data of the problem* (the numbers a textbook stem
prints); every answer is derived here with exact arithmetic (sympy Rationals / radicals).  Each operation owns a
validator that re-derives the answer a different way (substitute-and-check against the stated relations, enumeration
of the terms, or a second algebraic route) and never calls the construction a second time.

Numbers cross the JSON boundary as ints or strings (``"1/2"``, ``"-3"``, ``"9*sqrt(3)"``).  Canonical answers are
the strings the shared checkers parse (``"-3/2"`` for rationals, ``"-sqrt(3)"`` for radicals).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

import sympy as sp

DOMAIN_KEY = "sequence.progression"
N = sp.Symbol("n", integer=True, positive=True)


# --- numbers ---------------------------------------------------------------------------------------------

def num(v: Any) -> sp.Expr:
    if isinstance(v, bool):
        raise ValueError("bool_is_not_a_number")
    if isinstance(v, sp.Basic):
        return sp.nsimplify(v)
    return sp.sympify(str(v).strip(), rational=True)


def text(v: Any) -> str:
    """Canonical checker text: ``p/q`` for rationals, ``sqrt(3)`` style for radicals."""
    e = sp.radsimp(num(v))
    if e.is_Rational:
        return str(e)
    return sp.sstr(e).replace(" ", "")


def tex(v: Any) -> str:
    return sp.latex(sp.radsimp(num(v)))


def is_rational(v: Any) -> bool:
    return bool(num(v).is_Rational)


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _geom_term(a1: sp.Expr, r: sp.Expr, k: int) -> sp.Expr:
    return sp.radsimp(sp.expand(a1 * r ** (k - 1)))


# --- 1. general-term formulas -> first terms ----------------------------------------------------------------

def formula_expr(item: dict[str, Any]) -> sp.Expr:
    kind = item["kind"]
    if kind == "linear":
        return num(item["a"]) * N + num(item["b"])
    if kind == "quad":
        return num(item["a"]) * N ** 2 + num(item["b"]) * N + num(item["c"])
    if kind == "frac":
        return (num(item["p"]) * N + num(item["q"])) / (num(item["r"]) * N + num(item["s"]))
    if kind == "signed_frac":
        return (-1) ** N * num(item.get("p", 1)) / (num(item["r"]) * N + num(item["s"]))
    raise ValueError(f"unsupported_formula_kind:{kind}")


def sequence_terms_from_formula(items: list[dict[str, Any]], count: int = 5, **_: Any) -> dict[str, Any]:
    out = []
    for item in items:
        expr = formula_expr(item)
        terms = []
        for n in range(1, int(count) + 1):
            value = sp.simplify(expr.subs(N, n))
            if value.is_Rational is not True:
                raise ValueError("term_not_rational")
            terms.append(str(value))
        out.append({"terms": terms})
    return {"items": out}


def _fraction_term(item: dict[str, Any], n: int) -> Fraction:
    f = lambda v: Fraction(str(v))  # noqa: E731
    kind = item["kind"]
    if kind == "linear":
        return f(item["a"]) * n + f(item["b"])
    if kind == "quad":
        return f(item["a"]) * n * n + f(item["b"]) * n + f(item["c"])
    if kind == "frac":
        return (f(item["p"]) * n + f(item["q"])) / (f(item["r"]) * n + f(item["s"]))
    return Fraction((-1) ** n) * f(item.get("p", 1)) / (f(item["r"]) * n + f(item["s"]))


def _check_sequence_terms_from_formula(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for item, rec in zip(givens["items"], answer["items"]):  # plain Fraction arithmetic, independent of sympy
        if [Fraction(t) for t in rec["terms"]] != [_fraction_term(item, n) for n in range(1, int(givens.get("count", 5)) + 1)]:
            return False
    return len(givens["items"]) == len(answer["items"])


# --- 2. geometric progression read off its listed terms ---------------------------------------------------------

def geometric_from_terms(terms: list[Any], ask_k: int, target: Any, **_: Any) -> dict[str, Any]:
    t = [num(v) for v in terms]
    if len(t) < 3 or t[0] == 0:
        raise ValueError("need_three_terms_with_nonzero_first")
    r = sp.radsimp(t[1] / t[0])
    if sp.simplify(t[2] / t[1] - r) != 0 or r in (0, 1):
        raise ValueError("terms_are_not_geometric")
    target_value = num(target)
    index = None
    for n in range(1, 60):
        if sp.simplify(_geom_term(t[0], r, n) - target_value) == 0:
            index = n
            break
    if index is None:
        raise ValueError("target_not_in_sequence")
    return {"a1": text(t[0]), "r": text(r), "a_k": text(_geom_term(t[0], r, int(ask_k))), "k": int(ask_k), "target_index": index}


def _check_geometric_from_terms(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    terms = [num(v) for v in givens["terms"]]
    cur, seen = terms[0], []
    for _n in range(1, 60):  # enumerate by repeated multiplication of the stated ratio
        seen.append(sp.radsimp(sp.expand(cur)))
        cur = cur * num(answer["r"])
    if any(sp.simplify(a - b) != 0 for a, b in zip(seen, terms)):
        return False
    return (sp.simplify(seen[answer["k"] - 1] - num(answer["a_k"])) == 0
            and sp.simplify(seen[answer["target_index"] - 1] - num(givens["target"])) == 0
            and all(sp.simplify(s - num(givens["target"])) != 0 for s in seen[:answer["target_index"] - 1])
            and sp.simplify(num(answer["a1"]) - terms[0]) == 0)


# --- 3. geometric progression from stated relations -------------------------------------------------------------

_A1, _R = sp.symbols("a1 r")


def _real_solutions(eqs: list[sp.Expr]) -> list[tuple[sp.Expr, sp.Expr]]:
    sols = sp.solve(eqs, [_A1, _R], dict=True)
    out = []
    for s in sols:
        a1, r = sp.simplify(s[_A1]), sp.simplify(s[_R])
        if a1.is_real is True and r.is_real is True and a1 != 0 and r != 0:
            out.append((a1, r))
    return out


def geometric_from_relations(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "sum_pairs":  # a1+a3=S13, a2+a4=S24 -> a_k
        sols = _real_solutions([_A1 * (1 + _R ** 2) - num(g["S13"]), _A1 * _R * (1 + _R ** 2) - num(g["S24"])])
        if len(sols) != 1:
            raise ValueError("unique_progression_required")
        (a1, r), k = sols[0], int(g["ask_k"])
        return {"kind": kind, "members": [text(_geom_term(a1, r, k))], "a1": text(a1), "r": text(r), "k": k}
    if kind == "product_positive":  # positive terms, a1*a3=P13, a4=Q -> a1
        P, Q = num(g["P13"]), num(g["a4"])
        if P <= 0 or Q <= 0:
            raise ValueError("positive_terms_required")
        sols = [(a, r) for a, r in _real_solutions([_A1 ** 2 * _R ** 2 - P, _A1 * _R ** 3 - Q]) if a > 0 and r > 0]
        if len(sols) != 1:
            raise ValueError("unique_progression_required")
        a1, r = sols[0]
        return {"kind": kind, "a1": text(a1), "r": text(r)}
    if kind == "two_terms":  # a_m=A, a_n=B (n-m odd) -> a1, r
        m, n, A, B = int(g["m"]), int(g["n"]), num(g["A"]), num(g["B"])
        if (n - m) % 2 == 0 or m >= n or A == 0:
            raise ValueError("odd_gap_and_nonzero_first_term_required")
        sols = _real_solutions([_A1 * _R ** (m - 1) - A, _A1 * _R ** (n - 1) - B])
        sols = [(a, r) for a, r in sols if sp.im(r) == 0]
        if len(sols) != 1:
            raise ValueError("unique_progression_required")
        a1, r = sols[0]
        return {"kind": kind, "a1": text(a1), "r": text(r)}
    if kind == "diff_sum":  # a2-a1=D, a1+a3=S -> {a_k}
        D, S, k = num(g["D"]), num(g["S"]), int(g["ask_k"])
        sols = _real_solutions([_A1 * (_R - 1) - D, _A1 * (1 + _R ** 2) - S])
        values = sorted({sp.radsimp(_geom_term(a, r, k)) for a, r in sols}, key=lambda v: float(v))
        if len(values) < 1 or any(not v.is_Rational for v in values):
            raise ValueError("rational_values_required")
        return {"kind": kind, "members": [text(v) for v in values], "k": k}
    raise ValueError(f"unsupported_geometric_relation:{kind}")


def _term(a1: sp.Expr, r: sp.Expr, k: int) -> sp.Expr:
    return sp.radsimp(sp.expand(a1 * r ** (k - 1)))


def _check_geometric_from_relations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = answer["kind"]
    if kind in ("sum_pairs", "product_positive", "two_terms"):
        a1, r = num(answer["a1"]), num(answer["r"])
        terms = {k: _term(a1, r, k) for k in range(1, 8)}  # substitute back into every stated relation
        if kind == "sum_pairs":
            return (sp.simplify(terms[1] + terms[3] - num(givens["S13"])) == 0 and sp.simplify(terms[2] + terms[4] - num(givens["S24"])) == 0
                    and len(answer["members"]) == 1 and sp.simplify(terms[int(givens["ask_k"])] - num(answer["members"][0])) == 0)
        if kind == "product_positive":
            return (a1 > 0 and r > 0 and sp.simplify(terms[1] * terms[3] - num(givens["P13"])) == 0 and sp.simplify(terms[4] - num(givens["a4"])) == 0)
        m, n = int(givens["m"]), int(givens["n"])
        return sp.simplify(terms[m] - num(givens["A"])) == 0 and sp.simplify(terms[n] - num(givens["B"])) == 0
    # diff_sum: every listed value must come from a progression meeting both relations, and r satisfies the quadratic
    D, S, k = num(givens["D"]), num(givens["S"]), int(givens["ask_k"])
    r = sp.Symbol("r")
    roots = [x for x in sp.Poly(D * r ** 2 - S * r + S + D, r).nroots(n=30) if abs(sp.im(x)) < 1e-20]
    values = set()
    for root in roots:
        rr = sp.nsimplify(sp.re(root), rational=True, tolerance=1e-12)
        if rr == 1 or rr == 0:
            continue
        a1 = D / (rr - 1)
        if sp.simplify(a1 * (1 + rr ** 2) - S) == 0:
            values.add(sp.nsimplify(a1 * rr ** (k - 1), rational=True))
    return sorted(str(v) for v in values) == sorted(answer["members"]) and len(values) == len(answer["members"])


# --- 4. three numbers constrained by arithmetic / geometric conditions -------------------------------------------

_A, _B, _DD = sp.symbols("a b d")


def progression_three_numbers(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "geo_sum_relation":
        from .sequence_progression_recurrence import geo_sum_relation

        return geo_sum_relation(**g)
    if kind == "geo_then_arith":  # a, m, b geometric and a, m, b+c arithmetic -> {a}
        m, c = num(g["m"]), num(g["c"])
        sols = sp.solve([_A * _B - m ** 2, _A + (_B + c) - 2 * m], [_A, _B], dict=True)
        values = sorted({s[_A] for s in sols if s[_A].is_real is True and s[_B].is_real is True and s[_A] != 0 and s[_B] != 0}, key=float)
        if len(values) < 2 or any(not v.is_Rational for v in values):
            raise ValueError("two_rational_solutions_required")
        return {"kind": kind, "members": [text(v) for v in values]}
    if kind == "arith_geo_chain":  # p, a, b, q : (p,a,b) arithmetic, (a,b,q) geometric -> {a}
        p, q = num(g["p"]), num(g["q"])
        sols = sp.solve([2 * _A - p - _B, _B ** 2 - _A * q], [_A, _B], dict=True)
        values = sorted({s[_A] for s in sols if s[_A].is_real is True and s[_B].is_real is True and s[_A] != 0 and s[_B] != 0}, key=float)
        if len(values) < 2 or any(not v.is_Rational for v in values):
            raise ValueError("two_rational_solutions_required")
        return {"kind": kind, "members": [text(v) for v in values]}
    if kind == "arith_positions":  # A, A r, A r^2 are terms 1, i, j of an arithmetic progression -> {r}
        A, i, j = num(g["A"]), int(g["i"]), int(g["j"])
        r, d = sp.symbols("r d")
        if A == 0 or not 1 < i < j:
            raise ValueError("nonzero_first_term_and_positions_required")
        sols = sp.solve([A * r - A - (i - 1) * d, A * r ** 2 - A - (j - 1) * d], [r, d], dict=True)
        values = sorted({s[r] for s in sols if s[r].is_real is True}, key=float)
        if len(values) != 2:
            raise ValueError("two_solutions_required")
        return {"kind": kind, "members": [text(v) for v in values]}
    if kind == "arith_geo_shift":  # x-d, x, x+d positive with sum S; adding (u, v, w) gives a geometric triple -> smallest
        S, (u, v, w) = num(g["S"]), [num(t) for t in g["shifts"]]
        x = S / 3
        cands = []
        for dd in sp.solve((x - _DD + u) * (x + _DD + w) - (x + v) ** 2, _DD):
            if dd.is_real is not True:
                continue
            triple = [x - dd, x, x + dd]
            if all(t > 0 for t in triple) and all(t + s != 0 for t, s in zip(triple, (u, v, w))):
                cands.append((dd, triple))
        if len(cands) != 1:
            raise ValueError("unique_positive_triple_required")
        triple = sorted(cands[0][1])
        return {"kind": kind, "triple": [text(t) for t in cands[0][1]], "smallest": text(triple[0])}
    raise ValueError(f"unsupported_three_number_kind:{kind}")


def _check_progression_three_numbers(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = answer["kind"]
    if kind == "geo_sum_relation":
        from .sequence_progression_recurrence import check_geo_sum_relation

        return check_geo_sum_relation(givens, answer)
    if kind == "geo_then_arith":
        m, c = num(givens["m"]), num(givens["c"])
        found = set()
        for a in answer["members"]:  # every answer must produce a b meeting both stated conditions, and no other a may
            a = num(a)
            b = sp.simplify(m ** 2 / a)
            if sp.simplify(a + b + c - 2 * m) != 0:
                return False
            found.add(a)
        # completeness: the quadratic a^2 - (2m - c) a + m^2 = 0 has no further real root
        disc = (2 * m - c) ** 2 - 4 * m ** 2
        return len(found) == (2 if disc > 0 else 1 if disc == 0 else 0)
    if kind == "arith_geo_chain":
        p, q = num(givens["p"]), num(givens["q"])
        found = set()
        for a in answer["members"]:
            a = num(a)
            b = 2 * a - p
            if b == 0 or sp.simplify(b * b - a * q) != 0:
                return False
            found.add(a)
        disc = (4 * p + q) ** 2 - 16 * p * p  # 4a^2 - (4p + q) a + p^2 = 0
        return len(found) == (2 if disc > 0 else 1)
    if kind == "arith_positions":
        A, i, j = num(givens["A"]), int(givens["i"]), int(givens["j"])
        for r in answer["members"]:
            r = num(r)
            if sp.simplify((A * r ** 2 - A) * (i - 1) - (A * r - A) * (j - 1)) != 0:  # common difference consistent
                return False
        return sorted(float(num(r)) for r in answer["members"]) == sorted({1.0, float(Fraction(j - i, i - 1))})
    S = num(givens["S"])
    x = S / 3
    shifts = [num(t) for t in givens["shifts"]]
    triple = [num(t) for t in answer["triple"]]
    if sp.simplify(sum(triple) - S) != 0 or sp.simplify(triple[1] - x) != 0 or any(t <= 0 for t in triple):
        return False
    shifted = [t + s for t, s in zip(triple, shifts)]
    return sp.simplify(shifted[1] ** 2 - shifted[0] * shifted[2]) == 0 and min(triple) == num(answer["smallest"])


# --- 5. arithmetic progression from two terms ----------------------------------------------------------------------

def arithmetic_from_terms(m: int, A: Any, n: int, B: Any, **_: Any) -> dict[str, Any]:
    m, n, A, B = int(m), int(n), num(A), num(B)
    if m == n:
        raise ValueError("two_distinct_positions_required")
    d = (B - A) / (n - m)
    a1 = A - (m - 1) * d
    if d >= 0 or a1 <= 0:
        raise ValueError("decreasing_positive_start_required")
    first_negative = int(sp.floor(a1 / (-d))) + 2  # a1 + (k-1) d < 0  <=>  k-1 > a1/(-d)
    return {"a1": text(a1), "d": text(d), "first_negative": first_negative}


def _check_arithmetic_from_terms(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    a1, d = Fraction(answer["a1"]), Fraction(answer["d"])
    term = lambda k: a1 + (k - 1) * d  # noqa: E731
    if term(int(givens["m"])) != Fraction(str(givens["A"])) or term(int(givens["n"])) != Fraction(str(givens["B"])):
        return False
    k = 1
    while term(k) >= 0:  # walk the sequence until it first goes negative
        k += 1
    return k == answer["first_negative"] and term(k - 1) >= 0 and term(k) < 0


# --- 6. true / false statements -----------------------------------------------------------------------------------------

def _is_arithmetic(t: list[sp.Expr]) -> bool:
    return len(t) >= 3 and all(sp.simplify((t[i + 1] - t[i]) - (t[1] - t[0])) == 0 for i in range(len(t) - 1))


def _is_geometric(t: list[sp.Expr]) -> bool:
    return len(t) >= 3 and all(x != 0 for x in t) and all(sp.simplify(t[i + 1] * t[0] - t[i] * t[1]) == 0 for i in range(len(t) - 1))


def _recurrence_terms(kind: str, a1: sp.Expr, c: sp.Expr, count: int = 6) -> list[sp.Expr]:
    out = [a1]
    for _ in range(count - 1):
        out.append(out[-1] + c if kind == "arithmetic" else out[-1] * c)
    return out


def sequence_statements(statement: dict[str, Any], **_: Any) -> dict[str, Any]:
    kind = statement["kind"]
    if kind == "term_claim":  # "the k-th term of <formula> is V"
        expr = (num(statement["p2"]) * N ** 2 + num(statement["p1"]) * N + num(statement["p0"])) / (num(statement["r"]) * N + num(statement["s"]))
        actual = sp.simplify(expr.subs(N, int(statement["k"])))
        truth = sp.simplify(actual - num(statement["value"])) == 0
        return {"truth": bool(truth), "actual": text(actual)}
    if kind == "progression_claim":  # "the listed numbers form an arithmetic / geometric progression"
        t = [num(v) for v in statement["terms"]]
        truth = _is_arithmetic(t) if statement["claim"] == "arithmetic" else _is_geometric(t)
        return {"truth": bool(truth), "arithmetic": _is_arithmetic(t), "geometric": _is_geometric(t)}
    if kind == "both_claim":  # "the listed numbers are both arithmetic and geometric"
        t = [num(v) for v in statement["terms"]]
        return {"truth": bool(_is_arithmetic(t) and _is_geometric(t)), "arithmetic": _is_arithmetic(t), "geometric": _is_geometric(t)}
    if kind == "recurrence_term_claim":  # "this recurrence gives a_k = V"
        from .sequence_progression_recurrence import recurrence_term_claim

        return recurrence_term_claim(statement)
    if kind == "recurrence_claim":  # "a progression with these data has this recurrence"
        real = _recurrence_terms(statement["type"], num(statement["a1"]), num(statement["c"]))
        shown = _recurrence_terms(statement["shown_type"], num(statement["shown_a1"]), num(statement["shown_c"]))
        return {"truth": all(sp.simplify(x - y) == 0 for x, y in zip(real, shown)), "real": [text(x) for x in real[:4]]}
    raise ValueError(f"unsupported_statement_kind:{kind}")


def _check_sequence_statements(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    st = givens["statement"]
    f = lambda v: Fraction(str(v))  # noqa: E731
    kind = st["kind"]
    if kind == "recurrence_term_claim":
        from .sequence_progression_recurrence import check_recurrence_term_claim

        return check_recurrence_term_claim(st, answer)
    if kind == "term_claim":
        k = int(st["k"])
        actual = (f(st["p2"]) * k * k + f(st["p1"]) * k + f(st["p0"])) / (f(st["r"]) * k + f(st["s"]))
        return answer["truth"] == (actual == f(st["value"])) and Fraction(answer["actual"]) == actual
    if kind in ("progression_claim", "both_claim"):
        t = [f(v) for v in st["terms"]]
        diffs = {t[i + 1] - t[i] for i in range(len(t) - 1)}
        ratios = {t[i + 1] / t[i] for i in range(len(t) - 1)} if all(x != 0 for x in t) else None
        arith, geom = len(diffs) == 1, ratios is not None and len(ratios) == 1
        want = (arith and geom) if kind == "both_claim" else (arith if st["claim"] == "arithmetic" else geom)
        return answer["truth"] == want
    real, shown = [f(st["a1"])], [f(st["shown_a1"])]
    for _ in range(5):
        real.append(real[-1] + f(st["c"]) if st["type"] == "arithmetic" else real[-1] * f(st["c"]))
        shown.append(shown[-1] + f(st["shown_c"]) if st["shown_type"] == "arithmetic" else shown[-1] * f(st["shown_c"]))
    return answer["truth"] == (real == shown)


# --- registry / entrypoint ---------------------------------------------------------------------------------------------

def _solve_geometric_relations(**g: Any) -> dict[str, Any]:
    return geometric_from_relations(**g)


def _solve_three_numbers(**g: Any) -> dict[str, Any]:
    return progression_three_numbers(**g)


def _patterns_entry(name: str):
    from . import sequence_progression_patterns as P

    keys = {"figure_path_pattern": ("start", "t", "T", "order"), "finger_counting_cycle": ("ks", "N")}[name]
    return (getattr(P, name), getattr(P, f"_check_{name}"), keys)


def _recurrence_entry() -> tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]:
    from .sequence_progression_recurrence import check_recurrence_from_process, recurrence_from_process

    return (recurrence_from_process, check_recurrence_from_process, ("kind",))


_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "sequence_terms_from_formula": (sequence_terms_from_formula, _check_sequence_terms_from_formula, ("items",)),
    "geometric_from_terms": (geometric_from_terms, _check_geometric_from_terms, ("terms", "ask_k", "target")),
    "geometric_from_relations": (_solve_geometric_relations, _check_geometric_from_relations, ("kind",)),
    "progression_three_numbers": (_solve_three_numbers, _check_progression_three_numbers, ("kind",)),
    "arithmetic_from_terms": (arithmetic_from_terms, _check_arithmetic_from_terms, ("m", "A", "n", "B")),
    "sequence_statements": (sequence_statements, _check_sequence_statements, ("statement",)),
    "recurrence_from_process": _recurrence_entry(),
    "figure_path_pattern": _patterns_entry("figure_path_pattern"),
    "finger_counting_cycle": _patterns_entry("finger_counting_cycle"),
}
OPERATIONS = tuple(_OPERATIONS)


def build_sequence_progression_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_sequence_progression_operation:{operation}")
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
