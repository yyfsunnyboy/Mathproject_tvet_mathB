# -*- coding: utf-8 -*-
"""Extended B3 Ch1 families: locked-stem isomorphic generation (exact).

Generic capabilities for MANUAL_REVIEW resolution — not situation-specific APIs.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any, Literal

import sympy as sp

from core.domain.sequence_series_domain import (
    _fmt_math,
    _matrix_base,
    arithmetic_nth,
    arithmetic_partial_sum,
    canonical_exact,
    geometric_nth,
    to_rational,
)
from core.gencode.multipart_stem_contract import (
    build_stem_structure,
    stem_structure_to_question_text,
)

# ── operation keys ────────────────────────────────────────────────────────────

GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS = "geometric_ratio_from_shifted_pair_sums"
GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT = "geometric_ratio_from_product_quotient"
ARITHMETIC_INDEX_AND_TOTAL_SUM = "arithmetic_index_and_total_sum"
ARITHMETIC_FIRST_THRESHOLD_CROSSING = "arithmetic_first_threshold_crossing"
GEOMETRIC_FIRST_THRESHOLD_CROSSING = "geometric_first_threshold_crossing"
AP_GP_MIXED_MEAN_MIDDLE = "ap_gp_mixed_mean_middle"
GEOMETRIC_GROWTH_TABLE_CELLS = "geometric_growth_table_cells"

EXTENDED_OPS = frozenset(
    {
        GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS,
        GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT,
        ARITHMETIC_INDEX_AND_TOTAL_SUM,
        ARITHMETIC_FIRST_THRESHOLD_CROSSING,
        GEOMETRIC_FIRST_THRESHOLD_CROSSING,
        AP_GP_MIXED_MEAN_MIDDLE,
        GEOMETRIC_GROWTH_TABLE_CELLS,
    }
)

EXTENDED_MULTIPART = frozenset({ARITHMETIC_INDEX_AND_TOTAL_SUM, GEOMETRIC_GROWTH_TABLE_CELLS})

CompareMode = Literal["lt", "le", "gt", "ge"]


# ── pure primitives ───────────────────────────────────────────────────────────

def geometric_ratio_from_shifted_pair_sums(
    first_pair_sum: Any,
    second_pair_sum: Any,
    index_shift: int,
) -> Fraction:
    """For GP, (a_{i+s}+a_{i+1+s}) / (a_i+a_{i+1}) = r^s with s=index_shift>0."""
    s = int(index_shift)
    if s < 1:
        raise ValueError("index_shift_must_be_positive")
    x = to_rational(first_pair_sum)
    y = to_rational(second_pair_sum)
    if x <= 0 or y <= 0:
        raise ValueError("pair_sums_must_be_positive")
    ratio = y / x
    root = sp.simplify(sp.real_root(sp.Rational(ratio), s))
    r = to_rational(root)
    if r <= 0:
        raise ValueError("common_ratio_must_be_positive")
    powered = Fraction(r.numerator**s, r.denominator**s)
    if powered != ratio:
        raise ValueError("ratio_power_mismatch")
    return r


def geometric_ratio_from_product_quotient(
    product_quotient: Any,
    *,
    exponent: int = 4,
) -> Fraction:
    """cd/ab = r^exponent for positive 4-term GP (default exponent=4)."""
    exp = int(exponent)
    if exp < 1:
        raise ValueError("exponent_must_be_positive")
    k = to_rational(product_quotient)
    if k <= 0:
        raise ValueError("product_quotient_must_be_positive")
    root = sp.simplify(sp.real_root(sp.Rational(k), exp))
    r = to_rational(root)
    if r <= 0:
        raise ValueError("common_ratio_must_be_positive")
    powered = Fraction(r.numerator**exp, r.denominator**exp)
    if powered != k:
        raise ValueError("product_quotient_power_mismatch")
    return r


def arithmetic_index_from_a1_d_an(a1: Any, d: Any, an: Any) -> int:
    """Solve a_n = a1+(n-1)d for n >= 1."""
    dd = to_rational(d)
    if dd == 0:
        raise ValueError("common_difference_zero")
    n_frac = (to_rational(an) - to_rational(a1)) / dd + 1
    if n_frac.denominator != 1 or int(n_frac) < 1:
        raise ValueError("index_not_positive_integer")
    return int(n_frac)


def first_arithmetic_index_crossing_threshold(
    start: Any,
    step: Any,
    threshold: Any,
    *,
    compare: CompareMode = "lt",
    max_index: int = 10_000,
) -> int:
    """Smallest k>=1 such that start + k*step ≷ threshold (after k steps from start).

    Model: balance_k = start + k*step. Returns first k where compare holds.
    Requires that k-1 does NOT satisfy (or k==1).
    """
    s0 = to_rational(start)
    d = to_rational(step)
    thr = to_rational(threshold)
    if d == 0:
        raise ValueError("step_zero")

    def holds(val: Fraction) -> bool:
        if compare == "lt":
            return val < thr
        if compare == "le":
            return val <= thr
        if compare == "gt":
            return val > thr
        if compare == "ge":
            return val >= thr
        raise ValueError(f"bad_compare:{compare}")

    # If already true at k=0, invalid for "first after steps"
    if holds(s0):
        raise ValueError("threshold_already_met_at_start")

    for k in range(1, int(max_index) + 1):
        if holds(s0 + k * d):
            return k
    raise ValueError("threshold_not_crossed_in_bound")


def first_geometric_index_crossing_threshold(
    a1: Any,
    r: Any,
    threshold: Any,
    *,
    compare: CompareMode = "ge",
    power_of_index: bool = True,
    max_index: int = 64,
) -> int:
    """First k>=1 with value_k ≷ threshold.

    If power_of_index: value_k = a1 * r^k  (rounds/growth after k steps).
    Else: value_k = a1 * r^(k-1) (standard a_k).
    """
    a = sp.simplify(sp.sympify(a1))
    rr = sp.simplify(sp.sympify(r))
    thr = sp.simplify(sp.sympify(threshold))
    if rr == 0:
        raise ValueError("ratio_zero")

    def value(k: int) -> sp.Expr:
        if power_of_index:
            return sp.simplify(a * rr**k)
        return sp.simplify(a * rr ** (k - 1))

    def holds(val: sp.Expr) -> bool:
        diff = to_rational(sp.simplify(val - thr))
        if compare == "lt":
            return diff < 0
        if compare == "le":
            return diff <= 0
        if compare == "gt":
            return diff > 0
        if compare == "ge":
            return diff >= 0
        raise ValueError(f"bad_compare:{compare}")

    for k in range(1, int(max_index) + 1):
        if holds(value(k)):
            return k
    raise ValueError("threshold_not_crossed_in_bound")


def ap_gp_mixed_mean_middle_from_x3(x3: Any) -> dict[str, Fraction]:
    """x1..x4 AP, d>0, x2 = GM(x1,x4), x3 known → unique positive solution.

    Yields x1=d=x3/3, x2=2*x3/3, x4=4*x3/3.
    """
    m = to_rational(x3)
    x1 = m / 3
    d = x1
    if d <= 0:
        raise ValueError("common_difference_must_be_positive")
    x2 = x1 + d
    x4 = x1 + 3 * d
    if x2 * x2 != x1 * x4:
        raise ValueError("gp_mean_constraint_failed")
    return {"x1": x1, "x2": x2, "x3": m, "x4": x4, "d": d}


# ── locked-stem builders (backward generation) ────────────────────────────────

def _build_geo_shifted_pair_sums(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    shift = int(payload.get("index_shift") or 2)
    if "r" in payload:
        r = to_rational(payload["r"])
    else:
        r = Fraction(rng.choice([2, 3] if shift >= 5 else [2, 3, 4]))
    a = to_rational(payload["a"]) if "a" in payload else Fraction(rng.randint(1, 4 if shift >= 5 else 6))
    # Avoid textbook clones: (8,72,r=3) and (6,24,r=2)
    x = a * (1 + r)
    y = a * (r**shift) * (1 + r)
    # fingerprint guard vs common textbook
    if (int(x), int(y)) in {(8, 72), (6, 24)} and "r" not in payload:
        a = a + 1
        x = a * (1 + r)
        y = a * (r**shift) * (1 + r)
    recovered = geometric_ratio_from_shifted_pair_sums(x, y, shift)
    template = str(
        payload.get("stem_template")
        or (
            "設a, b, c, d四正數成等比數列，若\\(a+b={X}\\)，\\(c+d={Y}\\)，試求公比r之值。"
            if shift == 2
            else "數列\\(a_1\\),\\(a_2\\),\\(\\ldots\\),\\(a_{{{last}}}\\)成等比數列，設公比為r，"
            "且\\(a_1+a_2={X}\\)、\\(a_{{{p}}} +a_{{{q}}}={Y}\\)，試求\\(r\\)。"
        )
    )
    last = shift + 2
    p, q = shift + 1, shift + 2
    q_text = (
        template.replace("{X}", canonical_exact(x))
        .replace("{Y}", canonical_exact(y))
        .replace("{last}", str(last))
        .replace("{p}", str(p))
        .replace("{q}", str(q))
    )
    # 11957-style uses a1..a7 with shift 5: p=6,q=7
    if shift == 5 and "stem_template" not in payload:
        q_text = (
            f"數列\\(a_1\\),\\(a_2\\),\\(a_3\\),\\(a_4\\),\\(a_5\\),\\(a_6\\),\\(a_7\\)成等比數列，"
            f"設公比為r，且\\(a_1+a_2={canonical_exact(x)}\\)、"
            f"\\(a_6+a_7={canonical_exact(y)}\\)，試求\\(r\\)。"
        )
    return _matrix_base(
        GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS,
        question_text=q_text,
        answer=recovered,
        explanation=[f"Y/X=r^{shift} ⇒ r={canonical_exact(recovered)}"],
        params={"X": x, "Y": y, "index_shift": shift, "r": recovered, "a": a},
    )


def _build_geo_product_quotient(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    exp = int(payload.get("exponent") or 4)
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([2, 3, 4, 5]))
    k = Fraction(r.numerator**exp, r.denominator**exp)
    # avoid textbook K=81 (r=3)
    if k == 81 and "r" not in payload:
        r = Fraction(2)
        k = Fraction(16)
    recovered = geometric_ratio_from_product_quotient(k, exponent=exp)
    q = (
        f"設正數a, b, c, d成等比數列，若\\(\\dfrac{{cd}}{{ab}}={canonical_exact(k)}\\)，"
        f"試求此數列的公比。"
    )
    return _matrix_base(
        GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT,
        question_text=q,
        answer=recovered,
        explanation=[f"cd/ab=r^{exp} ⇒ r={canonical_exact(recovered)}"],
        params={"K": k, "exponent": exp, "r": recovered},
    )


def _build_arith_index_and_total(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    # seats: N rows, a1, d, target row seats an → index k and S_N
    n_total = int(payload.get("n_total") or rng.choice([40, 45, 48, 50, 55]))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(rng.choice([2, 3, 4]))
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(rng.randint(20, 45))
    # pick k in 2..n_total-1
    k = int(payload.get("k") or rng.randint(max(2, n_total // 5), max(3, (3 * n_total) // 4)))
    if k >= n_total:
        k = n_total - 1
    an = arithmetic_nth(a1, d, k)
    # avoid exact textbook (50,40,2,88)
    if (n_total, int(a1), int(d), int(an)) == (50, 40, 2, 88) and "a1" not in payload:
        a1 = a1 + 2
        an = arithmetic_nth(a1, d, k)
    total = arithmetic_partial_sum(a1, d, n_total)
    idx = arithmetic_index_from_a1_d_an(a1, d, an)
    parts = {"(1)": canonical_exact(idx), "(2)": canonical_exact(total)}
    stem = build_stem_structure(
        (
            f"某棒球場A區共有{n_total}排座位，此區每一排都比前一排多{_fmt_math(d)}個座位，"
            f"已知第一排有{_fmt_math(a1)}個座位，且阿民所坐的那一排有{_fmt_math(an)}個座位，請問："
        ),
        [
            {"group_label": "(1)", "text": "阿民坐在第幾排"},
            {"group_label": "(2)", "text": "A區共有幾個座位"},
        ],
    )
    return _matrix_base(
        ARITHMETIC_INDEX_AND_TOTAL_SUM,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[
            f"a_k=a1+(k-1)d ⇒ k={idx}",
            f"S_{n_total}={canonical_exact(total)}",
        ],
        answer_type="multi_part",
        stem_structure=stem,
        params={"n_total": n_total, "a1": a1, "d": d, "an": an, "k": idx, "Sn": total},
        validation_facts={"multipart_count": 2, "locked_stem": "stadium_seats"},
    )


def _build_arith_threshold(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    # backward: choose k, cost>0, start in (cost*(k-1), cost*k)
    k = int(payload.get("k") or rng.randint(20, 60))
    cost = to_rational(payload["cost"]) if "cost" in payload else Fraction(rng.choice([10, 15, 20, 25, 30]))
    # start = cost*(k-1) + rem, 0 < rem < cost → after k-1 still >0 (or >= if rem), after k <0
    rem = to_rational(payload["remainder"]) if "remainder" in payload else cost / 2
    if rem <= 0 or rem >= cost:
        rem = cost / 2
    start = cost * (k - 1) + rem
    step = -cost
    thr = to_rational(payload.get("threshold", 0))
    # narrative slots: shown debt negative, topup = start - shown
    shown = to_rational(payload.get("shown_balance", -10))
    if shown >= 0:
        shown = Fraction(-10)
    topup = start - shown
    if topup <= 0:
        shown = Fraction(-rng.choice([5, 10, 15, 20]))
        topup = start - shown
    ans = first_arithmetic_index_crossing_threshold(start, step, thr, compare="lt")
    assert ans == k
    q = (
        f"小喬每天使用悠遊卡坐捷運上下課，有一天他下課後坐捷運刷卡出站時，"
        f"刷卡機畫面顯示餘額為{_fmt_math(shown)}元，因此當天他將悠遊卡加值{_fmt_math(topup)}元。"
        f"若他每天坐捷運上下學，每次均花費{_fmt_math(cost)}元，"
        f"問第幾次出站刷卡時，刷卡機畫面會出現餘額為負的？"
    )
    return _matrix_base(
        ARITHMETIC_FIRST_THRESHOLD_CROSSING,
        question_text=q,
        answer=ans,
        explanation=[
            f"加值後餘額={canonical_exact(start)}，每次{canonical_exact(step)}，"
            f"求最小k使 start+k·step < 0 ⇒ k={ans}"
        ],
        params={
            "start": start,
            "step": step,
            "threshold": thr,
            "compare": "lt",
            "k": ans,
            "shown_balance": shown,
            "topup": topup,
            "cost": cost,
        },
        validation_facts={"locked_stem": "easycard_threshold"},
    )


def _build_geo_threshold(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    # infection-like: after round k, infected = base^k (a1=1,r=base), find min k: base^k >= T
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([2, 3, 4, 5]))
    k = int(payload.get("k") or rng.randint(6, 12))
    a1 = to_rational(payload.get("a1", 1))
    # value after k rounds: a1 * r^k
    val_km1 = a1 * (r ** (k - 1))
    val_k = a1 * (r**k)
    # threshold strictly between val_{k-1} and val_k, prefer near val_k for "達到"
    # textbook: >= 1000000 with 4^10
    if "threshold" in payload:
        thr = to_rational(payload["threshold"])
    else:
        # pick T with val_{k-1} < T <= val_k for compare ge on power_of_index
        thr = val_km1 + 1 if val_km1 + 1 <= val_k else val_k
        if thr <= val_km1:
            thr = val_k
    ans = first_geometric_index_crossing_threshold(
        a1, r, thr, compare="ge", power_of_index=True
    )
    # avoid exact textbook 4^k / 1000000 clone if default
    infect_extra = int(r - 1)  # "最多傳染 r-1 人" if r=4 → 3
    if infect_extra < 1:
        infect_extra = 1
        r = Fraction(2)
    q = (
        f"已知某種傳染病的特性是感染者經由接觸其他未感染者後，最多傳染{infect_extra}人，"
        f"也就是一個感染者經由第一輪接觸他人後，連同自己最多{_fmt_math(r)}人感染，"
        f"這些感染者經由第二輪接觸他人後，最多共有{_fmt_math(a1 * r * r)}位感染者，以此類推；"
        f"則從第一個感染者開始，最快經由幾輪傳播後，感染者會達到{_fmt_math(thr)}人？"
    )
    return _matrix_base(
        GEOMETRIC_FIRST_THRESHOLD_CROSSING,
        question_text=q,
        answer=ans,
        explanation=[f"人數=\\({canonical_exact(a1)}\\cdot{canonical_exact(r)}^k\\ge{canonical_exact(thr)}\\Rightarrow k={ans}"],
        params={
            "a1": a1,
            "r": r,
            "threshold": thr,
            "compare": "ge",
            "power_of_index": True,
            "k": ans,
            "infect_extra": infect_extra,
        },
        validation_facts={"locked_stem": "infection_rounds"},
    )


def _build_ap_gp_mixed(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    # backward: pick positive x1 (=d), x3=3*x1
    x1 = to_rational(payload["x1"]) if "x1" in payload else Fraction(rng.choice([4, 5, 6, 8, 9, 10, 12]))
    x3 = 3 * x1
    # avoid textbook x3=27 (x2=18)
    if x3 == 27 and "x1" not in payload:
        x1 = Fraction(8)
        x3 = Fraction(24)
    sol = ap_gp_mixed_mean_middle_from_x3(x3)
    q = (
        f"設\\(x_1\\),\\(x_2\\),\\(x_3\\),\\(x_4\\)為等差數列，其公差為d，\\(d>0\\)。"
        f"若\\(x_2\\)為\\(x_1\\)與\\(x_4\\)的等比中項，且\\(x_3={canonical_exact(x3)}\\)，"
        f"則\\(x_2=\\)？"
    )
    return _matrix_base(
        AP_GP_MIXED_MEAN_MIDDLE,
        question_text=q,
        answer=sol["x2"],
        explanation=[
            f"由 GM 與 AP 得 d=x1，且 x1+2d=x3 ⇒ x2={canonical_exact(sol['x2'])}"
        ],
        params=sol,
        validation_facts={"locked_stem": "ap_gp_mixed_mean"},
    )


def _decimal_plain(q: Fraction) -> str:
    """Exact terminating/repeating-safe plain decimal for growth factors."""
    from decimal import Decimal, localcontext

    with localcontext() as ctx:
        ctx.prec = 40
        d = Decimal(q.numerator) / Decimal(q.denominator)
        s = format(d, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s or "0"


def format_geometric_power_expr(principal: Any, growth_factor: Any, exponent: int) -> str:
    """Checker-friendly exact power cell using rational growth factor."""
    p = to_rational(principal)
    q = to_rational(growth_factor)
    e = int(exponent)
    if e < 0:
        raise ValueError("exponent_must_be_nonnegative")
    p_s = canonical_exact(p)
    if q.denominator == 1:
        q_s = str(int(q.numerator))
    else:
        q_s = f"({int(q.numerator)}/{int(q.denominator)})"
    if e == 0:
        return p_s
    if e == 1:
        return f"{p_s}*{q_s}"
    return f"{p_s}*{q_s}**{e}"


def format_geometric_power_latex(principal: Any, growth_factor: Any, exponent: int) -> str:
    p = to_rational(principal)
    q = to_rational(growth_factor)
    e = int(exponent)
    p_s = canonical_exact(p)
    q_s = _decimal_plain(q)
    if e == 0:
        return p_s
    if e == 1:
        return f"{p_s} \\times {q_s}"
    return f"{p_s} \\times {q_s}^{{{e}}}"


def geometric_year_start_expr(principal: Any, growth_factor: Any, year: int) -> str:
    """year_start(k) = P * q^(k-1)."""
    return format_geometric_power_expr(principal, growth_factor, int(year) - 1)


def geometric_year_end_expr(principal: Any, growth_factor: Any, year: int) -> str:
    """year_end(k) = P * q^k."""
    return format_geometric_power_expr(principal, growth_factor, int(year))


def _growth_cell_exponent(year: int, position: str) -> int:
    pos = str(position).strip().lower()
    y = int(year)
    if y < 1:
        raise ValueError("year_must_be_positive")
    if pos in {"start", "year_start", "beginning"}:
        return y - 1
    if pos in {"end", "year_end", "ending"}:
        return y
    raise ValueError(f"unsupported_cell_position:{position}")


def _build_geo_growth_table(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    """Locked-stem isomorphic compound-growth table fill via geometric powers."""
    principals = [5000, 8000, 12000, 15000, 20000]
    rate_choices = [
        Fraction(1, 100),
        Fraction(3, 200),  # 1.5%
        Fraction(1, 50),  # 2%
        Fraction(1, 40),  # 2.5%
        Fraction(3, 100),  # 3%
    ]
    principal = (
        to_rational(payload["principal"])
        if "principal" in payload
        else Fraction(rng.choice(principals))
    )
    rate = to_rational(payload["annual_rate"]) if "annual_rate" in payload else rng.choice(rate_choices)
    years = int(payload.get("years") or rng.choice([4, 5, 6]))
    if years < 4:
        years = 4
    # avoid exact textbook fingerprint (10000, 1.5%, 5)
    if (
        int(principal) == 10000
        and rate == Fraction(3, 200)
        and years == 5
        and "principal" not in payload
    ):
        principal = Fraction(12000)
        rate = Fraction(1, 50)
        years = 4
    q = 1 + rate
    # isomorphic blank layout (from screenshot topology):
    # ① year_end(2), ② year_start(4), ③ year_end(years)
    cells = payload.get("cells")
    if not isinstance(cells, list) or not cells:
        cells = [
            {"label": "①", "year": 2, "position": "end"},
            {"label": "②", "year": 4, "position": "start"},
            {"label": "③", "year": years, "position": "end"},
        ]
    parts: dict[str, str] = {}
    part_meta: list[dict[str, Any]] = []
    group_specs = []
    for cell in cells:
        label = str(cell.get("label") or cell.get("group_label") or "")
        year = int(cell["year"])
        position = str(cell["position"])
        exp = _growth_cell_exponent(year, position)
        expr = format_geometric_power_expr(principal, q, exp)
        # verify against geometric_nth
        term = geometric_nth(principal, q, exp + 1)
        if sp.simplify(sp.sympify(expr) - term) != 0:
            raise ValueError(f"growth_cell_mismatch:{expr}")
        parts[label] = expr
        part_meta.append(
            {
                "label": label,
                "year": year,
                "position": position,
                "exponent": exp,
                "expression": expr,
            }
        )
        pos_zh = "年初本金" if position.lower().startswith("start") or position == "start" else "年底本利和"
        group_specs.append(
            {
                "group_label": label,
                "text": f"第{year}年{pos_zh}",
            }
        )

    p_s = canonical_exact(principal)
    q_s = _decimal_plain(q)
    rate_pct = _decimal_plain(rate * 100)
    # Build filled table narrative with blanks labeled.
    lines = [
        f"日常生活中的存款或貸款利息，一般都採用複利計息。"
        f"例如現在存入銀行{_fmt_math(principal)}元，年利率{rate_pct}%，"
        f"按照複利計算，{years}年內各年年初本金與年底本利和如下，試完成表格。"
    ]
    for y in range(1, years + 1):
        start_expr = format_geometric_power_latex(principal, q, y - 1)
        end_expr = format_geometric_power_latex(principal, q, y)
        start_show = start_expr
        end_show = end_expr
        for meta in part_meta:
            if int(meta["year"]) != y:
                continue
            if meta["position"] == "start":
                start_show = str(meta["label"])
            else:
                end_show = str(meta["label"])
        lines.append(f"第{y}年　年初：\\({start_show}\\)　年底：\\({end_show}\\)")

    stem = build_stem_structure("".join(lines[:1]) + " " + "；".join(lines[1:]), group_specs)
    return _matrix_base(
        GEOMETRIC_GROWTH_TABLE_CELLS,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[
            f"成長因子 q=1+r={q_s}",
            "年初(k)=P·q^(k-1)，年底(k)=P·q^k",
            *[f"{m['label']}={m['expression']}" for m in part_meta],
        ],
        answer_type="multi_part",
        stem_structure=stem,
        params={
            "principal": principal,
            "annual_rate": rate,
            "growth_factor": q,
            "years": years,
            "cells": part_meta,
            "locked_stem": "compound_growth_table",
        },
        validation_facts={
            "multipart_count": len(parts),
            "locked_stem": "compound_growth_table",
            "source_rescue": "SOURCE_RESCUED_FROM_SCREENSHOT",
        },
    )


EXTENDED_BUILDERS = {
    GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS: _build_geo_shifted_pair_sums,
    GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT: _build_geo_product_quotient,
    ARITHMETIC_INDEX_AND_TOTAL_SUM: _build_arith_index_and_total,
    ARITHMETIC_FIRST_THRESHOLD_CROSSING: _build_arith_threshold,
    GEOMETRIC_FIRST_THRESHOLD_CROSSING: _build_geo_threshold,
    AP_GP_MIXED_MEAN_MIDDLE: _build_ap_gp_mixed,
    GEOMETRIC_GROWTH_TABLE_CELLS: _build_geo_growth_table,
}


def build_extended_matrix(op: str, rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    if op not in EXTENDED_BUILDERS:
        raise ValueError(f"unsupported_extended_sequence_op:{op}")
    return EXTENDED_BUILDERS[op](rng, payload)
