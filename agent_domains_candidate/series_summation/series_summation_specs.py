"""Per-component *inputs* for 普高數學2 Unit 2 級數 — skills ``gh_Series`` and ``gh_CommonSeriesSummationFormulas`` (textbook ids 12707-12743).

Each entry gives the source-faithful stated data (variant 0) and a sampler for further variants of the same shape.  Samplers only choose
the numbers a stem prints; the domain computes every answer and refuses degenerate inputs, which the sandbox then skips.  Nothing here is an answer.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

SKILLS = {"series": "gh_Series", "common": "gh_CommonSeriesSummationFormulas"}

_PROOF = "整題是數學歸納法證明：目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代（與 gh_MathematicalInduction 同一原則）"
_FIGURE = "題幹沒有描述圖形的幾何構造（只有「右圖中…」與等腰直角三角形的個數），答案只能由圖形判讀，教材又沒有詳解可作 Source Oracle，不憑圖形推定答案"
DEFERRED: dict[int, str] = {
    12719: _FIGURE + "：隨堂練習6 正方形 ABCD 內 5 個黑色等腰直角三角形",
    12727: _FIGURE + "：習題基礎題6 以 AB=1 起算的 T1～T5 等腰直角三角形",
    12731: _PROOF + "：例題8 平方和公式",
    12735: _PROOF + "：隨堂練習8 立方和公式",
}

OP = {name: name for name in ("arithmetic_series_items", "arithmetic_series_relation", "geometric_series_items", "geometric_series_relation",
                              "partial_sum_terms", "power_sums", "series_statements", "fish_rows")}
SKILL_OPERATIONS = {
    "series": ["arithmetic_series_items", "arithmetic_series_relation", "geometric_series_items", "geometric_series_relation",
               "partial_sum_terms", "series_statements", "fish_rows"],
    "common": ["power_sums", "series_statements"],
}


def pick(rng: random.Random, values: list) -> Any:
    return values[rng.randrange(len(values))]


def _g(**kw: Any) -> dict[str, Any]:
    return kw


def _s(v: Any) -> str:
    return str(Fraction(v)) if not isinstance(v, str) else v


# --- arithmetic series ---------------------------------------------------------------------------------------------------

def _arith_items(show: int):
    def sampler(rng: random.Random) -> dict[str, Any]:
        a1, d, n = rng.randint(-12, 40), pick(rng, [-5, -4, -3, -2, 2, 3, 4, 5, 6]), rng.randint(5, 12)
        total = n * (2 * a1 + (n - 1) * d) // 2 if n * (2 * a1 + (n - 1) * d) % 2 == 0 else None
        if total is None:
            raise ValueError("odd_total")
        first, step, m = rng.randint(-8, 12), pick(rng, [2, 3, 4, 5, -3, -4]), rng.randint(6, 14)
        return {"items": [{"kind": "d_from_sum", "a1": a1, "n": n, "S": total},
                          {"kind": "sum_terms", "first": first, "d": step, "last": first + (m - 1) * step, "show": show}]}
    return sampler


def _mid_term(rng: random.Random) -> dict[str, Any]:
    return {"kind": "mid_term", "m": rng.randint(5, 16), "value": rng.randint(-15, 60)}


def _pair_from_sum(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [10, 12, 16, 20, 24, 30])
    i = rng.randint(2, 4)
    return {"kind": "pair_from_sum", "n": n, "S": n // 2 * rng.randint(-6, 15), "pairs": [[1, n], [i, n + 1 - i]]}


def _mid_total(rng: random.Random) -> dict[str, Any]:
    return {"kind": "mid_total", "n": pick(rng, [11, 13, 15, 17, 19, 21, 25]), "step": rng.randint(1, 5), "mid": rng.randint(12, 60)}


def _front_back(rng: random.Random) -> dict[str, Any]:
    n = pick(rng, [6, 8, 10, 12, 14, 16, 20])
    f = rng.randint(5, 30)
    l = rng.randint(f + 20, f + 120)
    if n * (f + l) % 4:
        raise ValueError("fractional_total")
    return {"kind": "front_back", "n": n, "first2": f, "last2": l}


def _threshold(rng: random.Random) -> dict[str, Any]:
    first = pick(rng, [5, 8, 10, 12, 15, 20])
    return {"kind": "threshold_count", "first": first, "last": first + pick(rng, [30, 40, 50, 60, 70, 80]), "threshold": pick(rng, [200, 300, 400, 450, 500, 600, 800])}


def _two_walls(rng: random.Random) -> dict[str, Any]:
    return {"kind": "two_walls", "thick": rng.randint(40, 140), "big1": rng.randint(1, 3), "bigd": rng.randint(1, 3), "small1": rng.randint(1, 2), "smalld": rng.randint(1, 2)}


def _fish(rng: random.Random) -> dict[str, Any]:
    return {"k": rng.randint(6, 20)}


# --- geometric series -----------------------------------------------------------------------------------------------------

def _geo_items(rng: random.Random) -> dict[str, Any]:
    a1, r, n = rng.randint(1, 9), pick(rng, [2, 3, -2, -3, "1/2", "sqrt(2)", "sqrt(3)"]), rng.randint(4, 7)
    first, ratio, m = pick(rng, [1, 2, 3, 4, 5, 6, 8, -2, -1]), pick(rng, [2, 3, -2, -3, "1/2", "1/3"]), rng.randint(5, 9)
    from fractions import Fraction as F

    terms = [F(first) * F(str(ratio)) ** i for i in range(m)]
    if any(t.denominator != 1 for t in terms):
        first = first * F(str(ratio)).denominator ** (m - 1)
        terms = [F(first) * F(str(ratio)) ** i for i in range(m)]
    return {"items": [{"kind": "ratio_sum", "a1": a1, "r": r, "n": n},
                      {"kind": "list_sum", "terms": [str(int(t)) for t in terms[:3]], "last": str(int(terms[-1]))}]}


def _two_terms(rng: random.Random) -> dict[str, Any]:
    r, a1 = pick(rng, [2, 3, 4, -2, -3, -4]), pick(rng, [1, 2, 3, -1, -2])
    p, gap = rng.randint(1, 3), pick(rng, [2, 2, 2, 4])
    q = p + gap
    return {"kind": "two_terms", "p": p, "q": q, "A": a1 * r ** (p - 1), "B": a1 * r ** (q - 1), "n": rng.randint(4, 7)}


def _consecutive(rng: random.Random) -> dict[str, Any]:
    r, a1 = pick(rng, [-2, -3, 2, 3, 4, -4]), rng.randint(1, 4)
    total = a1 * (1 + r + r * r)
    return {"kind": "consecutive_triples", "A": total, "B": total * r, "n": rng.randint(5, 9)}


def _first_last(rng: random.Random) -> dict[str, Any]:
    a1, r, n = rng.randint(1, 5), pick(rng, [2, 3, 4, -2, -3]), rng.randint(4, 8)
    terms = [a1 * r ** i for i in range(n)]
    return {"kind": "first_last_sum", "a1": a1, "last": terms[-1], "S": sum(terms)}


def _layers(rng: random.Random) -> dict[str, Any]:
    return {"kind": "layers", "W": pick(rng, [32, 48, 64, 80, 96, 120, 144, 160]), "frac": pick(rng, ["1/8", "1/6", "1/5", "1/10", "1/4"]), "kids": 2, "layers": rng.randint(4, 6)}


def _squares(rng: random.Random) -> dict[str, Any]:
    return {"kind": "square_areas", "k": rng.randint(3, 14)}


def _blue(rng: random.Random) -> dict[str, Any]:
    return {"kind": "blue_squares", "side": pick(rng, [16, 24, 32, 48, 64]), "n": rng.randint(5, 10)}


# --- S_n -> a_n ---------------------------------------------------------------------------------------------------------

def _psum_exp(rng: random.Random) -> dict[str, Any]:
    return {"form": {"kind": "exp", "c": pick(rng, [1, 1, 2, 3]), "base": pick(rng, [2, 3, 4, 5])},
            "asks": [["a", 1], ["a", rng.randint(2, 5)], ["general"]], "style": "前n項和"}


def _psum_quad(asks_kind: int):
    def sampler(rng: random.Random) -> dict[str, Any]:
        form = {"kind": "quad", "a": pick(rng, [-3, -2, -1, 1, 2, 3]), "b": rng.randint(-5, 8)}
        asks = [["a", 1], ["a", rng.randint(2, 6)], ["general"]] if asks_kind == 3 else [["a", 1], ["general"]]
        return {"form": form, "asks": asks, "style": "前n項和" if asks_kind == 3 else "之前n項和"}
    return sampler


# --- statements ----------------------------------------------------------------------------------------------------------

def _ap_center(rng: random.Random) -> dict[str, Any]:
    k = pick(rng, [3, 5, 5, 7])
    c = (k + 1) // 2 if rng.random() < 0.5 else pick(rng, [c for c in range(1, k + 1) if c != (k + 1) // 2])
    return {"statement": {"kind": "ap_center", "k": k, "c": c}}


def _gp_formula(rng: random.Random) -> dict[str, Any]:
    m = rng.randint(5, 12)
    return {"statement": {"kind": "gp_formula", "r": rng.randint(2, 5), "m": m, "e": m + 1 if rng.random() < 0.5 else pick(rng, [m, m + 2])}}


def _cube_claim(rng: random.Random) -> dict[str, Any]:
    return {"statement": {"kind": "cube_sum", "claim": pick(rng, ["square_of_sum", "quarter_form", "half_form", "squares_form"])}}


# --- sums of powers ---------------------------------------------------------------------------------------------------------

def _range_pair(p: int):
    def sampler(rng: random.Random) -> dict[str, Any]:
        top, start = rng.randint(12, 30), rng.randint(5, 14)
        return {"kind": "sum_ranges", "layout": "intro_items", "items": [{"p": p, "first": 1, "step": 1, "last": top}, {"p": p, "first": start, "step": 1, "last": top}]}
    return sampler


def _even_odd(rng: random.Random) -> dict[str, Any]:
    e = pick(rng, [10, 12, 14, 16, 18, 20, 24, 26, 30, 36, 40])
    return {"kind": "sum_ranges", "layout": "named_items", "items": [{"p": 2, "first": 2, "step": 2, "last": e}, {"p": 2, "first": 1, "step": 2, "last": e - 1}]}


def _multiples(rng: random.Random) -> dict[str, Any]:
    k = pick(rng, [3, 4, 5, 6])
    return {"kind": "sum_ranges", "layout": "single", "items": [{"p": 3, "first": k, "step": k, "last": k * rng.randint(5, 9)}]}


def _mixed(rng: random.Random) -> dict[str, Any]:
    a = rng.randint(2, 9)
    return {"kind": "sum_ranges", "layout": "intro_named", "items": [{"p": 2, "first": a, "step": 1, "last": a + rng.randint(6, 12)},
                                                                        {"p": 3, "first": 2, "step": 2, "last": 2 * rng.randint(6, 12)}]}


def _layer_split(rng: random.Random) -> dict[str, Any]:
    layers = rng.randint(10, 20)
    return {"kind": "layer_split", "layers": layers, "top": rng.randint(layers // 2 + 1, layers - 3)}


def _cube_inverse(rng: random.Random) -> dict[str, Any]:
    return {"kind": "cube_total_inverse", "n": rng.randint(5, 24)}


def _tower(rng: random.Random) -> dict[str, Any]:
    order = [0, 1, 2, 3]
    rng.shuffle(order)
    return {"kind": "tower", "layers": rng.randint(6, 15), "order": order}



# component id -> (skill key, operation, source-faithful stated data, sampler)
COMPONENTS: dict[int, tuple[str, str, dict[str, Any], Any]] = {
    12707: ("series", "arithmetic_series_items", _g(items=[{"kind": "d_from_sum", "a1": 24, "n": 7, "S": 105}, {"kind": "sum_terms", "first": 3, "d": 4, "last": 47, "show": 2}]), _arith_items(2)),
    12714: ("series", "arithmetic_series_items", _g(items=[{"kind": "d_from_sum", "a1": 6, "n": 8, "S": 132}, {"kind": "sum_terms", "first": 9, "d": -4, "last": -15, "show": 3}]), _arith_items(3)),
    12722: ("series", "arithmetic_series_items", _g(items=[{"kind": "d_from_sum", "a1": 36, "n": 9, "S": 144}, {"kind": "sum_terms", "first": -3, "d": 2, "last": 23, "show": 3}]), _arith_items(3)),
    12708: ("series", "arithmetic_series_relation", _g(kind="mid_term", m=13, value=11), _mid_term),
    12715: ("series", "arithmetic_series_relation", _g(kind="pair_from_sum", n=20, S=10, pairs=[[1, 20], [2, 19]]), _pair_from_sum),
    12723: ("series", "arithmetic_series_relation", _g(kind="mid_total", n=19, step=2, mid=24), _mid_total),
    12729: ("series", "arithmetic_series_relation", _g(kind="front_back", n=12, first2=15, last2=75), _front_back),
    12716: ("series", "arithmetic_series_relation", _g(kind="threshold_count", first=10, last=70, threshold=500), _threshold),
    12724: ("series", "arithmetic_series_relation", _g(kind="two_walls", thick=63, big1=2, bigd=2, small1=1, smalld=1), _two_walls),
    12709: ("series", "fish_rows", _g(k=10), _fish),
    12710: ("series", "geometric_series_items", _g(items=[{"kind": "ratio_sum", "a1": 3, "r": "sqrt(2)", "n": 6}, {"kind": "list_sum", "terms": ["3", "6", "12"], "last": "384"}]), _geo_items),
    12717: ("series", "geometric_series_items", _g(items=[{"kind": "ratio_sum", "a1": 3, "r": -2, "n": 5}, {"kind": "list_sum", "terms": ["729", "243", "81"], "last": "9"}]), _geo_items),
    12725: ("series", "geometric_series_items", _g(items=[{"kind": "ratio_sum", "a1": 96, "r": "1/2", "n": 6},
                                                          {"kind": "list_sum", "terms": ["-2", "6", "-18"], "last": "39366", "last_tex": "(-2)\\times (-3)^{9}"}]), _geo_items),
    12711: ("series", "geometric_series_relation", _g(kind="two_terms", p=2, q=4, A=6, B=54, n=5), _two_terms),
    12718: ("series", "geometric_series_relation", _g(kind="consecutive_triples", A=3, B=-6, n=8), _consecutive),
    12726: ("series", "geometric_series_relation", _g(kind="first_last_sum", a1=2, last=512, S=682), _first_last),
    12730: ("series", "geometric_series_relation", _g(kind="layers", W=96, frac="1/8", kids=2, layers=5), _layers),
    12712: ("series", "geometric_series_relation", _g(kind="square_areas", k=6), _squares),
    12743: ("series", "geometric_series_relation", _g(kind="blue_squares", side=32, n=9), _blue),
    12713: ("series", "partial_sum_terms", _g(form={"kind": "exp", "c": 1, "base": 3}, asks=[["a", 1], ["a", 3], ["general"]], style="前n項和"), _psum_exp),
    12720: ("series", "partial_sum_terms", _g(form={"kind": "quad", "a": -1, "b": 6}, asks=[["a", 1], ["a", 4], ["general"]], style="前n項和"), _psum_quad(3)),
    12728: ("series", "partial_sum_terms", _g(form={"kind": "quad", "a": -2, "b": 1}, asks=[["a", 1], ["general"]], style="之前n項和"), _psum_quad(2)),
    12721: ("series", "series_statements", {"statement": {"kind": "ap_center", "k": 5, "c": 3}}, _ap_center),
    12739: ("series", "series_statements", {"statement": {"kind": "gp_formula", "r": 3, "m": 10, "e": 10}}, _gp_formula),
    12740: ("common", "series_statements", {"statement": {"kind": "cube_sum", "claim": "square_of_sum"}}, _cube_claim),
    12732: ("common", "power_sums", _g(kind="sum_ranges", layout="intro_items", items=[{"p": 2, "first": 1, "step": 1, "last": 20}, {"p": 2, "first": 11, "step": 1, "last": 20}]), _range_pair(2)),
    12736: ("common", "power_sums", _g(kind="sum_ranges", layout="intro_items", items=[{"p": 3, "first": 1, "step": 1, "last": 20}, {"p": 3, "first": 11, "step": 1, "last": 20}]), _range_pair(3)),
    12733: ("common", "power_sums", _g(kind="sum_ranges", layout="named_items", items=[{"p": 2, "first": 2, "step": 2, "last": 20}, {"p": 2, "first": 1, "step": 2, "last": 19}]), _even_odd),
    12737: ("common", "power_sums", _g(kind="sum_ranges", layout="single", items=[{"p": 3, "first": 3, "step": 3, "last": 21}]), _multiples),
    12741: ("common", "power_sums", _g(kind="sum_ranges", layout="intro_named", items=[{"p": 2, "first": 6, "step": 1, "last": 15}, {"p": 3, "first": 2, "step": 2, "last": 20}]), _mixed),
    12738: ("common", "power_sums", _g(kind="layer_split", layers=15, top=10), _layer_split),
    12742: ("common", "power_sums", _g(kind="cube_total_inverse", n=14), _cube_inverse),
    12734: ("common", "power_sums", _g(kind="tower", layers=12, order=[0, 1, 2, 3]), _tower),
}
