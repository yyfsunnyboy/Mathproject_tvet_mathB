"""Exact domain operations for general-high Mathematics 2, Unit 5 組合 (combinations and the binomial theorem).

Domain key ``discrete.combinations``.  Components pass the *stated data of the problem*; every answer is derived here with exact integer /
rational arithmetic (binomial coefficients, products of binomials, inclusion-exclusion, the binomial theorem).  Each operation owns a validator
that re-derives the answer a different way and never calls the construction a second time: enumeration of the labelled objects
(``itertools.combinations`` / ``permutations`` / ``product``), bit-mask subset counts, Pascal's triangle built by additions, repeated
polynomial / Laurent / Z[sqrt p] multiplication.  Polynomial expansions reuse the promoted ``algebra.multiplication_formulas`` polynomial core.
Numbers cross the JSON boundary as ints (rationals as ``p/q`` strings).
"""

from __future__ import annotations

import itertools
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_domain import (
    parse_polynomial,
    poly_mul,
    polynomial_plain,
    serialize_polynomial,
)

DOMAIN_KEY = "discrete.combinations"
_BRUTE = 300_000  # largest enumeration a validator runs
_VARS = "abcdefghijklmnopqrstuvwxyz"


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _int(v: Any, name: str, low: int | None = None, high: int | None = None) -> int:
    if isinstance(v, bool):
        raise ValueError(f"not_an_integer:{name}")
    try:
        f = Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_an_integer:{name}") from None
    if f.denominator != 1:
        raise ValueError(f"not_an_integer:{name}")
    n = int(f)
    if (low is not None and n < low) or (high is not None and n > high):
        raise ValueError(f"out_of_range:{name}")
    return n


def _int_list(values: Any, name: str, min_len: int, max_len: int, low: int, high: int, distinct: bool = False) -> list[int]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"not_a_list:{name}")
    out = [_int(v, name, low, high) for v in values]
    if not (min_len <= len(out) <= max_len) or (distinct and len(set(out)) != len(out)):
        raise ValueError(f"bad_list:{name}")
    return out


def _asks(asks: Any, allowed: tuple[str, ...], max_len: int = 3) -> list[str]:
    if not isinstance(asks, (list, tuple)) or not 1 <= len(asks) <= max_len or len(set(asks)) != len(asks) or any(a not in allowed for a in asks):
        raise ValueError("bad_asks")
    return list(asks)


def _positive(count: int) -> int:
    if count <= 0:
        raise ValueError("empty_result")
    return count


def _sequential(sizes: list[int]) -> int:
    left, out = sum(sizes), 1
    for s in sizes:
        out *= math.comb(left, s)
        left -= s
    return out


@lru_cache(maxsize=None)
def _pascal_row(n: int) -> tuple[int, ...]:
    """Row n of Pascal's triangle, built by additions only (independent of ``math.comb``)."""
    row: tuple[int, ...] = (1,)
    for _ in range(n):
        row = tuple(a + b for a, b in zip((0,) + row, row + (0,)))
    return row


def _pascal(n: int, k: int) -> int:
    return _pascal_row(n)[k] if 0 <= k <= n else 0


def _count_subsets(n: int, k: int, test: Callable[[tuple[int, ...]], bool]) -> int:
    if _pascal(n, k) > _BRUTE:
        raise ValueError("too_large_to_enumerate")
    return sum(1 for s in itertools.combinations(range(n), k) if test(s))


# --- 1. evaluate C(n,k) and P(n,k)/C(n,k) -----------------------------------------------------------------------------------------------

EVAL_KINDS = ("comb", "perm_over_comb")


def combination_evaluate(items: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    if not isinstance(items, (list, tuple)) or not 1 <= len(items) <= 4:
        raise ValueError("bad_items")
    out = []
    for it in items:
        kind = it.get("kind")
        n = _int(it.get("n"), "n", 1, 30)
        k = _int(it.get("k"), "k", 0, n)
        if kind == "comb":
            value = math.comb(n, k)
        elif kind == "perm_over_comb":
            if not 1 <= k <= 8:
                raise ValueError("bad_k")
            value = math.perm(n, k) // math.comb(n, k)
        else:
            raise ValueError(f"bad_kind:{kind}")
        out.append({"kind": kind, "n": n, "k": k, "value": value})
    return {"items": out}


def _check_combination_evaluate(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    items = answer["items"]
    if len(items) != len(givens["items"]):
        return False
    for g, it in zip(givens["items"], items):
        n, k = int(g["n"]), int(g["k"])
        if (it["kind"], it["n"], it["k"]) != (g["kind"], n, k):
            return False
        if g["kind"] == "comb":
            want = _pascal(n, k)
        else:
            orders = sum(1 for _ in itertools.permutations(range(k)))  # orderings of one chosen k-set
            if math.prod(range(n - k + 1, n + 1)) != _pascal(n, k) * orders:
                return False
            want = orders
        if it["value"] != want:
            return False
    return True


# --- 2. choose k of n with conditions on two named members ------------------------------------------------------------------------------

MEMBER_ASKS = ("total", "exactly_one", "both", "neither", "at_least_one")


def select_with_members(n: int, k: int, asks: list[str], **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 4, 16)
    k_ = _int(k, "k", 2, n_ - 1)
    rest = n_ - 2
    values = {"total": math.comb(n_, k_), "exactly_one": 2 * math.comb(rest, k_ - 1), "both": math.comb(rest, k_ - 2),
              "neither": math.comb(rest, k_), "at_least_one": math.comb(n_, k_) - math.comb(rest, k_)}
    return {"n": n_, "k": k_, "items": [{"ask": a, "count": _positive(values[a])} for a in _asks(asks, MEMBER_ASKS)]}


def _check_select_with_members(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, k = int(givens["n"]), int(givens["k"])
    tests = {"total": lambda c: True, "exactly_one": lambda c: c == 1, "both": lambda c: c == 2, "neither": lambda c: c == 0, "at_least_one": lambda c: c >= 1}
    if [it["ask"] for it in answer["items"]] != list(givens["asks"]):
        return False
    return all(_count_subsets(n, k, lambda s, t=tests[it["ask"]]: t(sum(1 for v in s if v < 2))) == it["count"] for it in answer["items"])


# --- 3. choose from several groups, every required group present, then line up (roles / ranks) -----------------------------------------

def mixed_group_ordered(groups: list[int], pick: int, require: list[int], **_: Any) -> dict[str, Any]:
    sizes = _int_list(groups, "groups", 2, 3, 1, 6)
    p = _int(pick, "pick", 2, min(4, sum(sizes)))
    req = sorted(_int_list(require, "require", 1, len(sizes), 0, len(sizes) - 1, distinct=True))
    if len(req) > p:
        raise ValueError("too_many_required_groups")
    cases = []
    for counts in itertools.product(*(range(min(s, p) + 1) for s in sizes)):
        if sum(counts) != p or any(counts[i] == 0 for i in req):
            continue
        selections = math.prod(math.comb(s, c) for s, c in zip(sizes, counts))
        cases.append({"counts": list(counts), "selections": selections, "ways": selections * math.factorial(p)})
    selections = _positive(sum(c["selections"] for c in cases))
    return {"groups": sizes, "pick": p, "require": req, "cases": cases, "selections": selections, "count": selections * math.factorial(p)}


def _check_mixed_group_ordered(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    sizes, p, req = [int(s) for s in givens["groups"]], int(givens["pick"]), [int(r) for r in givens["require"]]
    owner = [g for g, s in enumerate(sizes) for _ in range(s)]
    if math.perm(len(owner), p) > _BRUTE:
        return False
    brute = sum(1 for t in itertools.permutations(range(len(owner)), p) if all(any(owner[v] == r for v in t) for r in req))
    return brute == answer["count"] and sum(c["ways"] for c in answer["cases"]) == brute


# --- 4. split n distinct objects into groups of given sizes (labelled or identical groups) ----------------------------------------------

def group_partition(n: int, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 2, 10)
    if not isinstance(asks, (list, tuple)) or not 1 <= len(asks) <= 3:
        raise ValueError("bad_asks")
    items = []
    for ask in asks:
        sizes = _int_list(ask.get("sizes"), "sizes", 2, 4, 1, n_)
        labeled = ask.get("labeled")
        if sum(sizes) != n_ or not isinstance(labeled, bool):
            raise ValueError("bad_partition")
        if len(sizes) ** n_ > _BRUTE:
            raise ValueError("too_large_to_enumerate")
        ordered = _sequential(sizes)
        repeat = 1 if labeled else math.prod(math.factorial(c) for c in Counter(sizes).values())
        items.append({"sizes": sizes, "labeled": labeled, "ordered_count": ordered, "repeat_factor": repeat, "count": ordered // repeat})
    return {"n": n_, "items": items}


def _check_group_partition(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n = int(givens["n"])
    if len(answer["items"]) != len(givens["asks"]):
        return False
    for ask, item in zip(givens["asks"], answer["items"]):
        sizes = [int(s) for s in ask["sizes"]]
        g = len(sizes)
        if g ** n > _BRUTE or item["sizes"] != sizes or item["labeled"] != ask["labeled"]:
            return False
        fits = [t for t in itertools.product(range(g), repeat=n) if all(t.count(j) == sizes[j] for j in range(g))]
        if ask["labeled"]:
            brute = len(fits)
        else:
            brute = len({frozenset(frozenset(i for i in range(n) if t[i] == j) for j in range(g)) for t in fits})
        if brute != item["count"]:
            return False
    return True


# --- 5. which combination identities are correct (multi-select) -------------------------------------------------------------------------

IDENTITY_FORMS = ("symmetry", "pascal", "pascal_diff", "pascal_chain", "hockey_stick")


def identity_lhs(form: str, n: int, a: int) -> tuple[list[list[int]], tuple[int, int]]:
    """Signed terms [sign, n, k] of the left side and the single C(N, K) it reduces to by the identity of its form."""
    if form == "symmetry":
        return [[1, n, a]], (n, n - a)
    if form == "pascal":
        return [[1, n, a], [1, n, a - 1]], (n + 1, a)
    if form == "pascal_diff":
        return [[1, n + 1, a], [-1, n, a]], (n, a - 1)
    if form == "pascal_chain":
        return [[1, n, a], [1, n, a + 1], [1, n + 1, a + 2]], (n + 2, a + 2)
    if form == "hockey_stick":
        return [[1, n + i, i] for i in range(a + 1)], (n + a + 1, a)
    raise ValueError(f"bad_form:{form}")


def combination_identity_select(statements: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    if not isinstance(statements, (list, tuple)) or not 3 <= len(statements) <= 5:
        raise ValueError("bad_statements")
    out = []
    for st in statements:
        form = st.get("form")
        n = _int(st.get("n"), "n", 4, 150)
        a = _int(st.get("a"), "a", 1, n)
        lhs, (big_n, big_k) = identity_lhs(form, n, a)
        if form == "hockey_stick" and a > 6:
            raise ValueError("hockey_stick_too_long")
        if any(not 0 <= k <= m for _s, m, k in lhs) or not 0 < big_k < big_n:
            raise ValueError("index_out_of_range")
        value = sum(s * math.comb(m, k) for s, m, k in lhs)
        if value != math.comb(big_n, big_k):
            raise ValueError("identity_does_not_hold")
        rhs = _int_list(st.get("rhs"), "rhs", 2, 2, 0, 160)
        if not 0 <= rhs[1] <= rhs[0]:
            raise ValueError("rhs_out_of_range")
        out.append({"form": form, "lhs": lhs, "rhs": rhs, "identity": [big_n, big_k], "truth": value == math.comb(rhs[0], rhs[1])})
    selected = [i for i, st in enumerate(out, 1) if st["truth"]]
    if not selected:
        raise ValueError("selection_needs_at_least_one_correct_option")
    return {"statements": out, "selected": selected}


def _check_combination_identity_select(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    sts = answer["statements"]
    if len(sts) != len(givens["statements"]):
        return False
    selected = []
    for i, (g, st) in enumerate(zip(givens["statements"], sts), 1):
        if st["rhs"] != [int(v) for v in g["rhs"]]:
            return False
        left = sum(s * _pascal(m, k) for s, m, k in st["lhs"])
        truth = left == _pascal(*st["rhs"])
        if truth != st["truth"] or left != _pascal(*st["identity"]):
            return False
        if truth:
            selected.append(i)
    return selected == answer["selected"]


# --- 6. true / false statements about combinations -------------------------------------------------------------------------------------

def _coefficient_list(n: int) -> list[int]:
    """Coefficients of (1+t)^n by repeated multiplication by (1+t)."""
    coeffs = [1]
    for _ in range(n):
        coeffs = [a + b for a, b in zip(coeffs + [0], [0] + coeffs)]
    return coeffs


def combination_claim(setting: dict[str, Any], claim: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    kind = setting.get("kind")
    if kind == "choose":
        n = _int(setting.get("n"), "n", 2, 30)
        k = _int(setting.get("k"), "k", 1, n - 1)
        form = (claim or {}).get("form")
        cn, ck = _int((claim or {}).get("n"), "claim_n", 1, 30), _int((claim or {}).get("k"), "claim_k", 0, 30)
        if ck > cn or form not in ("comb", "perm"):
            raise ValueError("bad_claim")
        left, right = math.comb(n, k), (math.comb(cn, ck) if form == "comb" else math.perm(cn, ck))
    elif kind == "comb_times_factorial":
        n = _int(setting.get("n"), "n", 3, 20)
        k = _int(setting.get("k"), "k", 2, n - 1)
        m = _int(setting.get("m"), "m", 2, 10)
        left, right = math.comb(n, k) * math.factorial(m), math.perm(n, k)
    elif kind == "comb_equal":
        n = _int(setting.get("n"), "n", 4, 150)
        a, b = _int(setting.get("a"), "a", 1, n - 1), _int(setting.get("b"), "b", 1, n - 1)
        if a == b:
            raise ValueError("trivial_claim")
        left, right = math.comb(n, a), math.comb(n, b)
    elif kind == "binomial_coefficients":
        n = _int(setting.get("n"), "n", 3, 20)
        a, c = _int(setting.get("a"), "a", 1, n - 1), _int(setting.get("c"), "c", 1, n - 1)
        if a == c:
            raise ValueError("trivial_claim")
        left, right = math.comb(n, n - a), math.comb(n, n - c)  # coefficient of x^a y^(n-a) is C(n, n-a)
    else:
        raise ValueError(f"bad_setting:{kind}")
    return {"kind": kind, "left": left, "right": right, "truth": left == right}


def _check_combination_claim(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    s, c = givens["setting"], givens.get("claim") or {}
    kind = s["kind"]
    if kind == "choose":
        n, k = int(s["n"]), int(s["k"])
        left = _count_subsets(n, k, lambda _t: True) if _pascal(n, k) <= _BRUTE else _pascal(n, k)
        cn, ck = int(c["n"]), int(c["k"])
        right = _pascal(cn, ck) if c["form"] == "comb" else math.prod(range(cn - ck + 1, cn + 1))
    elif kind == "comb_times_factorial":
        n, k, m = int(s["n"]), int(s["k"]), int(s["m"])
        left = _pascal(n, k) * math.prod(range(1, m + 1))
        right = sum(1 for _ in itertools.permutations(range(n), k)) if math.perm(n, k) <= _BRUTE else math.prod(range(n - k + 1, n + 1))
    elif kind == "comb_equal":
        n = int(s["n"])
        left, right = _pascal(n, int(s["a"])), _pascal(n, int(s["b"]))
    else:
        n = int(s["n"])
        coeffs = _coefficient_list(n)  # index = power of y in (x+y)^n
        left, right = coeffs[n - int(s["a"])], coeffs[n - int(s["c"])]
    return (left, right, left == right) == (answer["left"], answer["right"], answer["truth"]) and answer["kind"] == kind


# --- 7. pairs among n (count C(n,2), or recover n from the number of pairs) -------------------------------------------------------------

def pair_count(mode: str, n: Any = None, total: Any = None, **_: Any) -> dict[str, Any]:
    if mode == "count":
        n_ = _int(n, "n", 3, 200)
        return {"mode": mode, "n": n_, "count": math.comb(n_, 2)}
    if mode == "solve_n":
        t = _int(total, "total", 3, 20000)
        n_ = (1 + math.isqrt(1 + 8 * t)) // 2
        if n_ * (n_ - 1) // 2 != t:
            raise ValueError("no_integer_solution")
        return {"mode": mode, "total": t, "n": n_}
    raise ValueError(f"bad_mode:{mode}")


def _check_pair_count(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    if givens["mode"] == "count":
        n = int(givens["n"])
        return sum(range(n)) == answer["count"] and sum(1 for _ in itertools.combinations(range(n), 2)) == answer["count"]
    t, size, pairs = int(givens["total"]), 1, 0
    while pairs < t:
        pairs += size  # the next player meets every earlier one
        size += 1
    return pairs == t and size == answer["n"]


# --- 8. choose k1 for one task, then k2 (k3) for the next from the rest -----------------------------------------------------------------

def sequential_selection(n: int, ks: list[int], **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 3, 10)
    ks_ = _int_list(ks, "ks", 2, 3, 1, n_)
    if sum(ks_) > n_ or (len(ks_) + 1) ** n_ > _BRUTE:
        raise ValueError("bad_selection")
    steps, left = [], n_
    for k in ks_:
        steps.append({"from": left, "k": k, "ways": math.comb(left, k)})
        left -= k
    return {"n": n_, "ks": ks_, "steps": steps, "count": math.prod(s["ways"] for s in steps)}


def _check_sequential_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, ks = int(givens["n"]), [int(k) for k in givens["ks"]]
    tasks = len(ks)
    brute = sum(1 for t in itertools.product(range(tasks + 1), repeat=n) if all(t.count(j + 1) == ks[j] for j in range(tasks)))
    return brute == answer["count"]


# --- 9. committee of boys and girls ----------------------------------------------------------------------------------------------------

def gender_committee(boys: int, girls: int, pick: int, asks: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    b, g = _int(boys, "boys", 1, 10), _int(girls, "girls", 1, 10)
    p = _int(pick, "pick", 2, min(6, b + g - 1))
    if not isinstance(asks, (list, tuple)) or not 1 <= len(asks) <= 3:
        raise ValueError("bad_asks")
    total = math.comb(b + g, p)
    items = []
    for ask in asks:
        kind = ask.get("kind")
        if kind == "exact":
            i = _int(ask.get("boys"), "exact_boys", 0, p)
            items.append({"kind": kind, "boys": i, "girls": p - i, "count": _positive(math.comb(b, i) * math.comb(g, p - i))})
        elif kind == "at_least_one_girl":
            items.append({"kind": kind, "total": total, "none": math.comb(b, p), "count": _positive(total - math.comb(b, p))})
        elif kind == "at_least_one_boy":
            items.append({"kind": kind, "total": total, "none": math.comb(g, p), "count": _positive(total - math.comb(g, p))})
        elif kind == "both":
            items.append({"kind": kind, "total": total, "only_boys": math.comb(b, p), "only_girls": math.comb(g, p),
                          "count": _positive(total - math.comb(b, p) - math.comb(g, p))})
        else:
            raise ValueError(f"bad_ask:{kind}")
    return {"boys": b, "girls": g, "pick": p, "items": items}


def _check_gender_committee(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    b, g, p = int(givens["boys"]), int(givens["girls"]), int(givens["pick"])
    tests = {"exact": lambda nb, ask: nb == int(ask["boys"]), "at_least_one_girl": lambda nb, ask: nb < p,
             "at_least_one_boy": lambda nb, ask: nb > 0, "both": lambda nb, ask: 0 < nb < p}
    for ask, item in zip(givens["asks"], answer["items"]):
        if item["kind"] != ask["kind"]:
            return False
        if _count_subsets(b + g, p, lambda s, a=ask: tests[a["kind"]](sum(1 for v in s if v < b), a)) != item["count"]:
            return False
    return len(givens["asks"]) == len(answer["items"])


# --- 10. groups of 1 teacher + m students sent to labelled sites ------------------------------------------------------------------------

def paired_group_assignment(teachers: int, students: int, **_: Any) -> dict[str, Any]:
    t = _int(teachers, "teachers", 2, 4)
    s = _int(students, "students", t, 4 * t)
    if s % t or t ** s > _BRUTE:
        raise ValueError("students_not_divisible")
    per = s // t
    sites, left_t, left_s = [], t, s
    for _site in range(t):
        sites.append({"teachers": left_t, "students_from": left_s, "student_ways": math.comb(left_s, per), "ways": left_t * math.comb(left_s, per)})
        left_t, left_s = left_t - 1, left_s - per
    return {"teachers": t, "students": s, "per_group": per, "sites": sites, "count": math.prod(x["ways"] for x in sites)}


def _check_paired_group_assignment(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    t, s = int(givens["teachers"]), int(givens["students"])
    per = s // t
    if t ** s > _BRUTE:
        return False
    student_ways = sum(1 for a in itertools.product(range(t), repeat=s) if all(a.count(j) == per for j in range(t)))
    teacher_ways = sum(1 for _ in itertools.permutations(range(t)))
    return student_ways * teacher_ways == answer["count"]


# --- 11. distinct people onto distinct places, every place used --------------------------------------------------------------------------

def surjective_distribution(people: int, places: int, **_: Any) -> dict[str, Any]:
    m = _int(places, "places", 2, 5)
    n = _int(people, "people", m, 8)
    if m ** n > _BRUTE:
        raise ValueError("too_large_to_enumerate")
    terms = [{"j": j, "sign": (-1) ** j, "choose": math.comb(m, j), "power": (m - j) ** n} for j in range(m + 1)]
    count = sum(x["sign"] * x["choose"] * x["power"] for x in terms)
    method = "bijection" if n == m else ("pair" if n == m + 1 else "inclusion_exclusion")
    return {"people": n, "places": m, "terms": terms, "method": method, "count": _positive(count)}


def _check_surjective_distribution(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, m = int(givens["people"]), int(givens["places"])
    return sum(1 for a in itertools.product(range(m), repeat=n) if len(set(a)) == m) == answer["count"]


# --- 12. pick numbers from 1..N with an even / odd sum -----------------------------------------------------------------------------------

def parity_sum_selection(top: int, pick: int, parity: str, **_: Any) -> dict[str, Any]:
    t = _int(top, "top", 5, 12)
    p = _int(pick, "pick", 2, min(5, t - 1))
    if parity not in ("even", "odd"):
        raise ValueError("bad_parity")
    odd, even = (t + 1) // 2, t // 2
    want = 0 if parity == "even" else 1
    cases = [{"odd": j, "even": p - j, "ways": math.comb(odd, j) * math.comb(even, p - j)}
             for j in range(p + 1) if j % 2 == want and j <= odd and p - j <= even]
    return {"top": t, "pick": p, "parity": parity, "odd_count": odd, "even_count": even, "cases": cases,
            "count": _positive(sum(c["ways"] for c in cases))}


def _check_parity_sum_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    t, p = int(givens["top"]), int(givens["pick"])
    want = 0 if givens["parity"] == "even" else 1
    return sum(1 for c in itertools.combinations(range(1, t + 1), p) if sum(c) % 2 == want) == answer["count"]


# --- 13. choose r letters of a word with repeated letters and line them up --------------------------------------------------------------

def multiset_select_arrange(word: str, pick: int, **_: Any) -> dict[str, Any]:
    w = str(word)
    if not 4 <= len(w) <= 8 or any(ch not in _VARS for ch in w):
        raise ValueError("bad_word")
    counts = Counter(w)
    if max(counts.values()) < 2:
        raise ValueError("word_needs_a_repeated_letter")
    r = _int(pick, "pick", 2, min(4, len(w) - 1))
    letters = sorted(counts, key=w.index)
    by_pattern: dict[tuple[int, ...], dict[str, int]] = {}
    for vec in itertools.product(*(range(min(counts[ch], r) + 1) for ch in letters)):
        if sum(vec) != r:
            continue
        pattern = tuple(sorted((c for c in vec if c), reverse=True))
        each = math.factorial(r) // math.prod(math.factorial(c) for c in vec)
        slot = by_pattern.setdefault(pattern, {"selections": 0, "arrangements_each": each})
        slot["selections"] += 1
    cases = [{"pattern": list(p), "selections": v["selections"], "arrangements_each": v["arrangements_each"],
              "ways": v["selections"] * v["arrangements_each"]} for p, v in sorted(by_pattern.items(), key=lambda kv: (kv[0][0], kv[0]))]
    return {"word": w, "length": len(w), "pick": r, "letters": {ch: counts[ch] for ch in letters}, "cases": cases,
            "count": sum(c["ways"] for c in cases)}


def _check_multiset_select_arrange(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    return len(set(itertools.permutations(str(givens["word"]), int(givens["pick"])))) == answer["count"]


# --- 14. binomial expansion (aX + bY)^n ------------------------------------------------------------------------------------------------

def _variables(vars_: Any) -> tuple[str, str]:
    if not isinstance(vars_, (list, tuple)) or len(vars_) != 2 or len(set(vars_)) != 2 or any(v not in _VARS for v in vars_):
        raise ValueError("bad_variables")
    return str(vars_[0]), str(vars_[1])


def binomial_expansion(a: int, b: int, n: int, vars: list[str], **_: Any) -> dict[str, Any]:  # noqa: A002
    a_, b_ = _int(a, "a", -4, 4), _int(b, "b", -4, 4)
    n_ = _int(n, "n", 2, 6)
    if not a_ or not b_:
        raise ValueError("zero_coefficient")
    x, y = _variables(vars)
    if x > y:
        raise ValueError("variables_must_be_in_alphabetical_order")
    coefficients = [math.comb(n_, r) * a_ ** (n_ - r) * b_ ** r for r in range(n_ + 1)]
    poly = parse_polynomial([[c, {x: n_ - r, y: r}] for r, c in enumerate(coefficients)])
    return {"a": a_, "b": b_, "n": n_, "vars": [x, y], "coefficients": coefficients, "terms": serialize_polynomial(poly), "plain": polynomial_plain(poly)}


def _check_binomial_expansion(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    x, y = givens["vars"]
    base = parse_polynomial([[int(givens["a"]), {x: 1}], [int(givens["b"]), {y: 1}]])
    product = {(): Fraction(1)}
    for _ in range(int(givens["n"])):
        product = poly_mul(product, base)
    return parse_polynomial(answer["terms"]) == product and answer["plain"] == polynomial_plain(product)


# --- 15. (sqrt p + c)^n = A + B sqrt p ------------------------------------------------------------------------------------------------

SQUAREFREE = (2, 3, 5, 6, 7, 10)


def radical_binomial_power(radicand: int, constant: int, n: int, **_: Any) -> dict[str, Any]:
    p = _int(radicand, "radicand", 2, 10)
    c = _int(constant, "constant", -3, 3)
    n_ = _int(n, "n", 2, 6)
    if p not in SQUAREFREE or not c:
        raise ValueError("bad_radical_binomial")
    terms = []
    for r in range(n_ + 1):
        e = n_ - r  # power of sqrt p
        terms.append({"r": r, "root_power": e, "value": math.comb(n_, r) * p ** (e // 2) * c ** r, "radical": e % 2 == 1})
    a = sum(t["value"] for t in terms if not t["radical"])
    b = sum(t["value"] for t in terms if t["radical"])
    return {"radicand": p, "constant": c, "n": n_, "terms": terms, "a": a, "b": b}


def _check_radical_binomial_power(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    p, c, n = int(givens["radicand"]), int(givens["constant"]), int(givens["n"])
    x, y = 1, 0  # x + y sqrt p
    for _ in range(n):
        x, y = x * c + y * p, x + y * c
    numeric = (math.sqrt(p) + c) ** n
    return (x, y) == (answer["a"], answer["b"]) and abs(x + y * math.sqrt(p) - numeric) < 1e-6 * max(1.0, abs(numeric))


# --- 16. a coefficient (or the constant term) of (c1 x^p1 + c2 x^p2)^n -------------------------------------------------------------------

def general_term_coefficient(c1: int, p1: int, c2: int, p2: int, n: int, target: int, **_: Any) -> dict[str, Any]:
    c1_, c2_ = _int(c1, "c1", -3, 3), _int(c2, "c2", -5, 5)
    p1_, p2_ = _int(p1, "p1", 1, 3), _int(p2, "p2", -3, -1)
    n_ = _int(n, "n", 3, 9)
    t = _int(target, "target", -30, 30)
    if not c1_ or not c2_:
        raise ValueError("zero_coefficient")
    step = p1_ - p2_
    if (p1_ * n_ - t) % step:
        raise ValueError("no_such_term")
    r = (p1_ * n_ - t) // step
    if not 0 <= r <= n_:
        raise ValueError("no_such_term")
    coefficient = math.comb(n_, r) * c1_ ** (n_ - r) * c2_ ** r
    return {"r": r, "n": n_, "target": t, "general_exponent": [p1_ * n_, step], "coefficient": coefficient}


def _check_general_term_coefficient(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    c1, p1, c2, p2, n, t = (int(givens[k]) for k in ("c1", "p1", "c2", "p2", "n", "target"))
    laurent = {0: 1}
    for _ in range(n):
        nxt: dict[int, int] = {}
        for e, v in laurent.items():
            nxt[e + p1] = nxt.get(e + p1, 0) + v * c1
            nxt[e + p2] = nxt.get(e + p2, 0) + v * c2
        laurent = nxt
    return laurent.get(t, 0) == answer["coefficient"] and answer["coefficient"] != 0


# --- 17. send at least k of n people -----------------------------------------------------------------------------------------------------

def at_least_k_selection(n: int, k: int, **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 4, 14)
    k_ = _int(k, "k", 1, n_)
    count = sum(math.comb(n_, j) for j in range(k_, n_ + 1))
    if n_ % 2 == 1 and k_ == (n_ + 1) // 2:
        method = "half"
    elif n_ % 2 == 0 and k_ == n_ // 2 + 1:
        method = "half_even"
    else:
        method = "complement"
    return {"n": n_, "k": k_, "method": method, "excluded": [math.comb(n_, j) for j in range(k_)], "count": _positive(count)}


def _check_at_least_k_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, k = int(givens["n"]), int(givens["k"])
    return sum(1 for mask in range(1 << n) if bin(mask).count("1") >= k) == answer["count"]


# --- 18. low < C(n,s) + ... + C(n,n) < high, find n --------------------------------------------------------------------------------------

def binomial_sum_bound(low: int, high: int, start: int, **_: Any) -> dict[str, Any]:
    lo, hi = _int(low, "low", 1, 10 ** 7), _int(high, "high", 2, 10 ** 7)
    s = _int(start, "start", 0, 1)
    found = [n for n in range(1, 41) if lo < 2 ** n - s < hi]
    if len(found) != 1:
        raise ValueError("solution_not_unique")
    n = found[0]
    return {"low": lo, "high": hi, "start": s, "n": n, "value": 2 ** n - s}


def _check_binomial_sum_bound(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    lo, hi, s = int(givens["low"]), int(givens["high"]), int(givens["start"])
    found = [n for n in range(1, 41) if lo < sum(_pascal_row(n)[s:]) < hi]
    return found == [answer["n"]] and sum(_pascal_row(answer["n"])[s:]) == answer["value"]


# --- 19. (1 + a x)(1 + x)^n has x^m coefficient c, find a -----------------------------------------------------------------------------

def coefficient_solve_parameter(n: int, m: int, value: int, **_: Any) -> dict[str, Any]:
    n_ = _int(n, "n", 2, 9)
    m_ = _int(m, "m", 1, n_)
    v = _int(value, "value", -500, 500)
    base, slope = math.comb(n_, m_), math.comb(n_, m_ - 1)
    a = Fraction(v - base, slope)
    if a == 0:
        raise ValueError("parameter_must_be_nonzero")
    text = str(a.numerator) if a.denominator == 1 else f"{a.numerator}/{a.denominator}"
    return {"n": n_, "m": m_, "value": v, "base": base, "slope": slope, "a": text}


def _check_coefficient_solve_parameter(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, m, v = int(givens["n"]), int(givens["m"]), int(givens["value"])
    a = Fraction(answer["a"])
    coeffs = [Fraction(1)]
    for factor in [[Fraction(1), a]] + [[Fraction(1), Fraction(1)]] * n:
        coeffs = [sum(coeffs[i - j] * factor[j] for j in range(2) if 0 <= i - j < len(coeffs)) for i in range(len(coeffs) + 1)]
    return coeffs[m] == v


# --- registry / entrypoint --------------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "combination_evaluate": (combination_evaluate, _check_combination_evaluate, ("items",)),
    "select_with_members": (select_with_members, _check_select_with_members, ("n", "k", "asks")),
    "mixed_group_ordered": (mixed_group_ordered, _check_mixed_group_ordered, ("groups", "pick", "require")),
    "group_partition": (group_partition, _check_group_partition, ("n", "asks")),
    "combination_identity_select": (combination_identity_select, _check_combination_identity_select, ("statements",)),
    "combination_claim": (combination_claim, _check_combination_claim, ("setting",)),
    "pair_count": (pair_count, _check_pair_count, ("mode",)),
    "sequential_selection": (sequential_selection, _check_sequential_selection, ("n", "ks")),
    "gender_committee": (gender_committee, _check_gender_committee, ("boys", "girls", "pick", "asks")),
    "paired_group_assignment": (paired_group_assignment, _check_paired_group_assignment, ("teachers", "students")),
    "surjective_distribution": (surjective_distribution, _check_surjective_distribution, ("people", "places")),
    "parity_sum_selection": (parity_sum_selection, _check_parity_sum_selection, ("top", "pick", "parity")),
    "multiset_select_arrange": (multiset_select_arrange, _check_multiset_select_arrange, ("word", "pick")),
    "binomial_expansion": (binomial_expansion, _check_binomial_expansion, ("a", "b", "n", "vars")),
    "radical_binomial_power": (radical_binomial_power, _check_radical_binomial_power, ("radicand", "constant", "n")),
    "general_term_coefficient": (general_term_coefficient, _check_general_term_coefficient, ("c1", "p1", "c2", "p2", "n", "target")),
    "at_least_k_selection": (at_least_k_selection, _check_at_least_k_selection, ("n", "k")),
    "binomial_sum_bound": (binomial_sum_bound, _check_binomial_sum_bound, ("low", "high", "start")),
    "coefficient_solve_parameter": (coefficient_solve_parameter, _check_coefficient_solve_parameter, ("n", "m", "value")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_combinations_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_combinations_operation:{operation}")
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
