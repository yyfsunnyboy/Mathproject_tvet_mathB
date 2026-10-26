"""Per-component *inputs* for 普高數學2 Unit 1 (數列) — skill ``gh_Sequence`` (textbook ids 12667-12685).

Each entry gives the source-faithful stated data (variant 0) and a sampler for further variants of the same shape.
Samplers only choose the numbers a stem prints; the domain computes every answer and refuses degenerate inputs, which the
sandbox then skips.  Nothing here is an answer.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

import sympy as sp

SKILLS = {"seq": "gh_Sequence", "rr": "gh_RecursiveRelation", "mi": "gh_MathematicalInduction"}

_FIGURE = "題幹依賴教材圖形（含圖形選項），目前沒有已驗證的圖形渲染與判圖契約，不可只靠文字出題"
_PROOF = "含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代"
_PATTERN = "圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律"
DEFERRED: dict[int, str] = {
    12686: _PATTERN + "：例題6 的正六邊形地磚排列",
    12694: _PATTERN + "：基礎題5 的正方形地磚排列",
    12698: _PATTERN + "：進階題9 的艾薛爾飛魚圖案",
    12696: "第 (3) 小題要求使用數學歸納法驗證：" + _PROOF,
    12700: "第 (3) 小題要求使用數學歸納法驗證：" + _PROOF,
    12701: "整題是數學歸納法證明：" + _PROOF,
    12702: _PATTERN + "，並含圖形選項（單選）：例題11 的艾薛爾蜥蜴圖案",
    12703: "第 (3) 小題要求使用數學歸納法驗證：" + _PROOF,
    12704: "整題是數學歸納法證明：" + _PROOF,
    12705: _PATTERN + "：隨堂練習11 的艾薛爾蝴蝶圖案",
    12706: "整題是數學歸納法證明：" + _PROOF,
}

OP = {name: name for name in ("sequence_terms_from_formula", "geometric_from_terms", "geometric_from_relations",
                              "progression_three_numbers", "arithmetic_from_terms", "sequence_statements", "recurrence_from_process",
                              "figure_path_pattern", "finger_counting_cycle")}
# gh_MathematicalInduction has no buildable component in this revision (every row is a proof or a figure pattern): no binding.
SKILL_OPERATIONS = {"seq": [o for o in OP if o != "recurrence_from_process"],
                    "rr": ["recurrence_from_process", "progression_three_numbers", "sequence_statements"]}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _s(v: Any) -> str:
    """JSON-safe number text for the domain (``1/2``, ``-3``, ``2*sqrt(2)``)."""
    e = sp.radsimp(sp.sympify(v, rational=True))
    return str(e) if e.is_Rational else sp.sstr(e).replace(" ", "")


def _int_or_none(v: Any) -> int | None:
    e = sp.sympify(v, rational=True)
    return int(e) if e.is_Integer else None


# --- 1. general terms ---------------------------------------------------------------------------------------

def _terms_a(rng: random.Random) -> dict[str, Any]:
    return {"items": [{"kind": "linear", "a": pick(rng, [1, 2, 3, 4, 5, -1, -2]), "b": pick(rng, [-5, -3, -2, -1, 1, 2, 3, 4])},
                      {"kind": "frac", "p": pick(rng, [1, 2, 3]), "q": pick(rng, [0, 0, 1, -1]), "r": pick(rng, [2, 3, 4, 5]), "s": pick(rng, [1, 1, 2, -1])}]}


def _terms_b(rng: random.Random) -> dict[str, Any]:
    return {"items": [{"kind": "quad", "a": pick(rng, [-1, -2, 1, 2, 3]), "b": pick(rng, [0, 0, 1, -1]), "c": pick(rng, [1, 2, 3, 4, 5, -2]), "ascending": True},
                      {"kind": "signed_frac", "p": pick(rng, [1, 1, 2, 3]), "r": pick(rng, [1, 2, 3, 4]), "s": pick(rng, [0, 0, 1, 2])}]}


# --- 2. geometric progression read off its terms ----------------------------------------------------------------

def _shown(a1: sp.Expr, r: sp.Expr, count: int = 3) -> list[str]:
    return [_s(a1 * r ** i) for i in range(count)]


def _aperture(rng: random.Random) -> dict[str, Any]:
    a1 = pick(rng, [1, 2, 3, 4, 5])
    r = pick(rng, [sp.sqrt(2), sp.sqrt(3), 2, 3, sp.Rational(3, 2)])
    n = pick(rng, [5, 6, 7, 8, 9, 10])
    return {"style": "aperture", "terms": _shown(a1, r), "ask_k": pick(rng, [4, 5, 6, 7]), "target": _s(a1 * r ** (n - 1))}


def _list_style(rng: random.Random) -> dict[str, Any]:
    a1 = pick(rng, [1, 2, 3, 4, 5, -2, -3])
    r = pick(rng, [-2, 2, 3, -3, 4, -4, sp.Rational(-1, 2)])
    n = pick(rng, [5, 6, 7, 8])
    if r == sp.Rational(-1, 2):
        a1 = 2 ** (n + 1) * pick(rng, [1, 3])
    return {"style": "list", "terms": _shown(a1, r), "ask_k": pick(rng, [4, 5, 6]), "target": _s(a1 * r ** (n - 1))}


# --- 3. geometric progression from relations --------------------------------------------------------------------------

def _sum_pairs(rng: random.Random) -> dict[str, Any]:
    r = pick(rng, [2, -2, 3, -3, sp.Rational(1, 2), sp.Rational(-1, 2), sp.Rational(1, 3), sp.Rational(-1, 3)])
    a1 = pick(rng, [1, 2, 3, 4, 8, 9, 16, 18, 27, 32])
    s13, s24 = a1 * (1 + r ** 2), a1 * r * (1 + r ** 2)
    if _int_or_none(s13) is None or _int_or_none(s24) is None:
        raise ValueError("integer_relations_only")
    return {"kind": "sum_pairs", "S13": int(s13), "S24": int(s24), "ask_k": pick(rng, [5, 6])}


def _product_positive(rng: random.Random) -> dict[str, Any]:
    a2, r = pick(rng, [1, 2, 3, 4, 5, 6, 8]), pick(rng, [2, 3, 4, 5])
    return {"kind": "product_positive", "P13": a2 ** 2, "a4": a2 * r ** 2}


def _two_terms(rng: random.Random) -> dict[str, Any]:
    a1 = pick(rng, [-1, 1, 2, -2, 3, -3, 4, sp.Rational(1, 2)])
    r = pick(rng, [sp.sqrt(3), -sp.sqrt(3), sp.sqrt(2), -sp.sqrt(2), 2, -2, 3, sp.sqrt(5)])
    m = pick(rng, [1, 2, 3])
    n = m + pick(rng, [1, 3])
    return {"kind": "two_terms", "m": m, "A": _s(a1 * r ** (m - 1)), "n": n, "B": _s(a1 * r ** (n - 1))}


def _diff_sum(rng: random.Random) -> dict[str, Any]:
    u = pick(rng, [1, 2, 3, 4, sp.Rational(1, 2), -1, -2, sp.Rational(1, 3)])
    r1, r2 = 1 + u, 1 + 2 / u  # (r1-1)(r2-1) = 2 gives two geometric progressions meeting both relations
    if r1 in (0, 1) or r2 in (0, 1) or r1 == r2:
        raise ValueError("degenerate_ratios")
    D = rng.randint(1, 12)
    S = D * (r1 + r2)
    if _int_or_none(S) is None:
        raise ValueError("integer_relations_only")
    return {"kind": "diff_sum", "D": D, "S": int(S), "ask_k": pick(rng, [4, 5, 6])}


# --- 4. three numbers -----------------------------------------------------------------------------------------------------------

def _geo_then_arith(rng: random.Random) -> dict[str, Any]:
    m = pick(rng, [2, 3, 4, 5, 6, 7, 8, 9, 10])
    divisors = [d for d in range(1, m * m) if (m * m) % d == 0 and d < m * m // d]
    d1 = pick(rng, divisors)
    r1, r2 = d1, m * m // d1
    if rng.random() < 0.3:
        r1, r2 = -r1, -r2
    c = 2 * m - (r1 + r2)
    if c == 0:
        raise ValueError("degenerate_shift")
    return {"kind": "geo_then_arith", "m": m, "c": c}


def _arith_geo_chain(rng: random.Random) -> dict[str, Any]:
    p, q = pick(rng, [-6, -5, -4, -3, -2, -1, 1, 2, 3, 4]), rng.randint(-40, 40)
    if q == 0:
        raise ValueError("degenerate_end")
    return {"kind": "arith_geo_chain", "p": p, "q": q}


def _arith_positions(rng: random.Random) -> dict[str, Any]:
    i = pick(rng, [2, 3, 4])
    j = rng.randint(i + 1, 9)
    if Fraction(j - i, i - 1) == 1:
        raise ValueError("coincident_solutions")
    return {"kind": "arith_positions", "A": pick(rng, [1, 1, 2, 3, -1, -2, 4]), "i": i, "j": j}


def _arith_geo_shift(rng: random.Random) -> dict[str, Any]:
    x = rng.randint(6, 24)
    d = rng.randint(1, x - 2)
    g, q = pick(rng, [1, 2, 3, 4, 5, 6, 8, 9]), pick(rng, [2, 3, 4])
    geo = [g * 2, g * 2 * q, g * 2 * q * q]
    shifts = [geo[0] - (x - d), geo[1] - x, geo[2] - (x + d)]
    if any(s <= 0 for s in shifts):
        raise ValueError("positive_shifts_only")
    return {"kind": "arith_geo_shift", "S": 3 * x, "shifts": shifts}


# --- 5. arithmetic progression -------------------------------------------------------------------------------------------------

def _arithmetic(rng: random.Random) -> dict[str, Any]:
    d = pick(rng, [-1, -2, -3, -4, -5, sp.Rational(-1, 2), sp.Rational(-3, 2)])
    a1 = rng.randint(8, 70)
    m = pick(rng, [3, 5, 8, 10, 12])
    n = m + pick(rng, [4, 5, 6, 10])
    return {"m": m, "A": _s(a1 + (m - 1) * d), "n": n, "B": _s(a1 + (n - 1) * d)}


# --- 6. statements ----------------------------------------------------------------------------------------------------------------

def _term_claim(rng: random.Random) -> dict[str, Any]:
    p2, p0, r, s, k = pick(rng, [1, 1, 2, 3]), pick(rng, [-3, -2, 1, 2, 3, 4]), pick(rng, [1, 2, 3]), pick(rng, [-3, -2, -1, 1, 2]), rng.randint(2, 7)
    actual = Fraction(p2 * k * k + p0, r * k + s)
    value = actual if rng.random() < 0.5 else actual + pick(rng, [1, -1, Fraction(1, 2), 2])
    return {"statement": {"kind": "term_claim", "p2": p2, "p1": 0, "p0": p0, "r": r, "s": s, "k": k, "value": str(value)}}


def _progression_claim(rng: random.Random) -> dict[str, Any]:
    start, kind = pick(rng, [1, 2, 3, 4, 5, -2]), rng.randrange(3)
    if kind == 0:
        step = pick(rng, [2, 3, 5, -2])
        terms = [start + i * step for i in range(3)]
    elif kind == 1:
        ratio = pick(rng, [2, 3, -2, Fraction(3, 2)])
        terms = [Fraction(start) * Fraction(ratio) ** i for i in range(3)]
    else:
        terms = [start, start + pick(rng, [1, 2, 3]), start + pick(rng, [5, 6, 7, 9])]
    return {"statement": {"kind": "progression_claim", "terms": [str(t) for t in terms], "claim": pick(rng, ["arithmetic", "geometric"])}}


def _both_claim(rng: random.Random) -> dict[str, Any]:
    """Half true (a non-zero constant list), half false: the zero list, an almost-constant list, or a genuine arithmetic / geometric list."""
    size = pick(rng, [3, 4, 5])
    if rng.random() < 0.5:
        terms = [pick(rng, [5, 3, -2, 7, 9, -4, 1, 6, 8, -6])] * size
    else:
        kind = rng.randrange(4)
        c = pick(rng, [2, 3, 4, 5, -3])
        if kind == 0:
            terms = [0] * size
        elif kind == 1:
            terms = [c] * (size - 1) + [c + pick(rng, [1, 2, -1])]
        elif kind == 2:
            terms = [c + i * pick(rng, [1, 2, 3]) for i in range(size)]
        else:
            terms = [c * pick(rng, [2, 3]) ** i for i in range(size)]
    return {"statement": {"kind": "both_claim", "terms": [str(t) for t in terms]}}


def _recurrence_claim(rng: random.Random) -> dict[str, Any]:
    tp = pick(rng, ["arithmetic", "geometric"])
    a1 = pick(rng, [5, 3, 2, 4, -1, 6])
    c = pick(rng, [-3, 2, 4, -2, 5]) if tp == "arithmetic" else pick(rng, [2, 3, -2, 4])
    shown = (tp, a1, c)
    flaw = 0 if rng.random() < 0.5 else rng.randint(1, 3)  # half of the shown recurrences are the correct one
    if flaw == 1:
        shown = (tp, a1, -c)
    elif flaw == 2:
        shown = (tp, a1 + pick(rng, [1, 2]), c)
    elif flaw == 3:
        other = "geometric" if tp == "arithmetic" else "arithmetic"
        shown = (other, a1, c)
    return {"statement": {"kind": "recurrence_claim", "type": tp, "a1": a1, "c": c, "shown_type": shown[0], "shown_a1": shown[1], "shown_c": shown[2]}}



# --- recurrence processes (gh_RecursiveRelation) ------------------------------------------------------------------------

def _subdivision_sampler(shape: str, parts_choices: list[int], ask: str):
    def sample(rng: random.Random) -> dict[str, Any]:
        parts = pick(rng, parts_choices)
        removed = rng.randint(1, parts - 2)
        g: dict[str, Any] = {"kind": "subdivision", "shape": shape, "parts": parts, "removed": removed, "ask": ask}
        if removed == 1 and (shape == "triangle" and parts == 4 or shape == "segment" and parts % 2 == 1):
            g["where"] = "中間"
        elif removed == 1 and shape == "square":
            g["where"] = "左上角"
        if ask == "value":
            g["k"] = rng.randint(4, 9)
        else:
            g["limit"] = pick(rng, [100, 500, 1000, 3000, 5000])
        return g
    return sample


def _row_sums(rng: random.Random) -> dict[str, Any]:
    return {"kind": "row_sums", "first": pick(rng, [1, 1, 2, 3]), "step": pick(rng, [1, 2, 3, 4]), "k": rng.randint(5, 9)}


def _tearing(rng: random.Random) -> dict[str, Any]:
    start, pieces = pick(rng, [1, 2, 3, 4, 5]), pick(rng, [3, 4, 5, 6])
    return {"kind": "tearing", "start": start, "pieces": pieces, "k": pick(rng, [2, 3, 4]), "target": start + (pieces - 1) * rng.randint(12, 60)}


def _array_row_end(rng: random.Random) -> dict[str, Any]:
    return {"kind": "array_row_end", "start": pick(rng, [1, 1, 1, 2, 5]), "first_row": pick(rng, [1, 2, 3]), "k": rng.randint(5, 9)}


def _nested(rng: random.Random) -> dict[str, Any]:
    return {"kind": "nested_polygon", "shape": pick(rng, ["square", "triangle"]), "P": pick(rng, [8, 12, 16, 24, 32, 48]), "k": rng.randint(5, 11)}


def _geo_sum(rng: random.Random) -> dict[str, Any]:
    return {"kind": "geo_sum_relation", "c": pick(rng, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, "1/2", "3/4", "5/4", "15/4", "2/3", "7/4"])}


def _recurrence_claim_term(rng: random.Random) -> dict[str, Any]:
    tp = pick(rng, ["geometric", "arithmetic"])
    a1 = pick(rng, [1, 2, 3, 4, 5, -1])
    c = pick(rng, [2, 3, -2, 4]) if tp == "geometric" else pick(rng, [2, 3, -3, 5, -2])
    k = pick(rng, [3, 4, 5])
    actual = Fraction(a1) * Fraction(c) ** (k - 1) if tp == "geometric" else Fraction(a1) + c * (k - 1)
    value = actual if rng.random() < 0.5 else actual + pick(rng, [-2, -1, 1, 2]) if tp == "arithmetic" else (actual if rng.random() < 0.5 else actual / 2 if actual % 2 == 0 else actual + 1)
    return {"statement": {"kind": "recurrence_term_claim", "type": tp, "a1": a1, "c": c, "k": k, "value": str(value)}}

def _figure_path(rng: random.Random) -> dict[str, Any]:
    order = list(range(4))
    rng.shuffle(order)
    t = rng.randint(6, 400)
    return {"start": 1, "t": t, "T": pick(rng, [t + 1, rng.randint(12, 500)]), "order": order}


def _finger(rng: random.Random) -> dict[str, Any]:
    first = rng.randint(1, 6)
    ks = pick(rng, [[1, 2, 3, 4], [first, first + 1, first + 2, first + 3], sorted(rng.sample(range(1, 13), 4))])
    return {"ks": ks, "N": 8 * rng.randint(3, 250) + pick(rng, [1, 2, 3, 4, 5, 6, 7, 8])}  # every residue (finger) comes up


def _g(**kw: Any) -> dict[str, Any]:
    return kw


# component id -> (skill key, operation, source-faithful stated data, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12667: ("seq", "sequence_terms_from_formula", {"items": [{"kind": "linear", "a": 2, "b": -1}, {"kind": "frac", "p": 1, "q": 0, "r": 3, "s": 1}]}, _terms_a),
    12668: ("seq", "figure_path_pattern", _g(start=1, t=106, T=107, order=[2, 3, 0, 1]), _figure_path),
    12669: ("seq", "geometric_from_terms", _g(style="aperture", terms=["2", "2*sqrt(2)", "4"], ask_k=6, target=32), _aperture),
    12670: ("seq", "geometric_from_relations", _g(kind="sum_pairs", S13=20, S24=-10, ask_k=5), _sum_pairs),
    12671: ("seq", "progression_three_numbers", _g(kind="geo_then_arith", m=2, c=-1), _geo_then_arith),
    12672: ("seq", "sequence_terms_from_formula", {"items": [{"kind": "quad", "a": -1, "b": 0, "c": 1, "ascending": True}, {"kind": "signed_frac", "p": 1, "r": 2, "s": 0}]}, _terms_b),
    12673: ("seq", "finger_counting_cycle", _g(ks=[1, 2, 3, 4], N=999), _finger),
    12674: ("seq", "geometric_from_terms", _g(style="list", terms=["3", "-6", "12"], ask_k=5, target=-384), _list_style),
    12675: ("seq", "geometric_from_relations", _g(kind="product_positive", P13=1, a4=4), _product_positive),
    12676: ("seq", "progression_three_numbers", _g(kind="arith_positions", A=1, i=2, j=5), _arith_positions),
    12677: ("seq", "sequence_statements", {"statement": {"kind": "term_claim", "p2": 1, "p1": 0, "p0": 2, "r": 2, "s": -1, "k": 5, "value": "3"}}, _term_claim),
    12678: ("seq", "sequence_statements", {"statement": {"kind": "progression_claim", "terms": ["4", "6", "9"], "claim": "geometric"}}, _progression_claim),
    12679: ("seq", "sequence_statements", {"statement": {"kind": "both_claim", "terms": ["5", "5", "5"]}}, _both_claim),
    12680: ("seq", "sequence_statements", {"statement": {"kind": "recurrence_claim", "type": "arithmetic", "a1": 5, "c": -3,
                                                          "shown_type": "arithmetic", "shown_a1": 5, "shown_c": -3}}, _recurrence_claim),
    12681: ("seq", "arithmetic_from_terms", _g(m=10, A=20, n=20, B=10), _arithmetic),
    12682: ("seq", "geometric_from_relations", _g(kind="two_terms", m=3, A=-3, n=6, B="9*sqrt(3)"), _two_terms),
    12683: ("seq", "geometric_from_relations", _g(kind="diff_sum", D=2, S=10, ask_k=4), _diff_sum),
    12684: ("seq", "progression_three_numbers", _g(kind="arith_geo_chain", p=-2, q=18), _arith_geo_chain),
    12685: ("seq", "progression_three_numbers", _g(kind="arith_geo_shift", S=30, shifts=[1, 6, 47]), _arith_geo_shift),
    12687: ("rr", "recurrence_from_process", _g(kind="subdivision", shape="triangle", parts=4, removed=1, where="中間", ask="value", k=6), _subdivision_sampler("triangle", [4, 9, 16], "value")),
    12688: ("rr", "recurrence_from_process", _g(kind="row_sums", first=1, step=2, k=6), _row_sums),
    12689: ("rr", "recurrence_from_process", _g(kind="tearing", start=2, pieces=4, k=2, target=101), _tearing),
    12690: ("rr", "recurrence_from_process", _g(kind="subdivision", shape="segment", parts=3, removed=1, where="中間", ask="value", k=9), _subdivision_sampler("segment", [3, 4, 5, 6], "value")),
    12692: ("rr", "recurrence_from_process", _g(kind="array_row_end", start=1, first_row=1, k=6), _array_row_end),
    12693: ("rr", "sequence_statements", {"statement": {"kind": "recurrence_term_claim", "type": "geometric", "a1": 2, "c": 2, "k": 4, "value": "8"}}, _recurrence_claim_term),
    12695: ("rr", "recurrence_from_process", _g(kind="subdivision", shape="square", parts=9, removed=1, where="左上角", ask="threshold", limit=1000), _subdivision_sampler("square", [4, 9, 16], "threshold")),
    12697: ("rr", "progression_three_numbers", _g(kind="geo_sum_relation", c=1), _geo_sum),
    12699: ("rr", "recurrence_from_process", _g(kind="nested_polygon", shape="square", P=16, k=10), _nested),
}
