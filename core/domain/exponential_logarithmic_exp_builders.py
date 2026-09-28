# -*- coding: utf-8 -*-
"""B3 Chapter 4 exponent families (sections 4-1 and 4-2).

Builders sample slots, pick a clean answer first, then render the stem.
Every value comes from ``exponential_logarithmic_math``.
"""

from __future__ import annotations

import itertools
import math
import random
import re
from decimal import ROUND_CEILING, Decimal, localcontext
from fractions import Fraction
from typing import Any

from core.domain.exponential_logarithmic_math import (
    as_fraction,
    fraction_as_terminating_decimal,
    fraction_plain,
    mono,
    mono_mul,
    mono_plain,
    mono_pow,
    rational_power,
)
from core.domain.exponential_logarithmic_render import (
    m,
    make_choices,
    num_choice,
    pack,
    same_number,
    statement_choice,
    tex_base,
    tex_exp,
    tex_mono,
    tex_num,
    tex_power,
    tex_radical,
)

F = Fraction
TIMES = r"\times "


def _pw(var: str, e: object) -> str:
    e = as_fraction(e)
    return var if e == 1 else f"{var}^{{{tex_exp(e)}}}"


def _items(texts: list[str]) -> list[dict[str, str]]:
    return [{"group_label": f"({i})", "text": text} for i, text in enumerate(texts, 1)]


def _parts(values: list[object]) -> dict[str, str]:
    return {f"({i})": (v if isinstance(v, str) else fraction_plain(v)) for i, v in enumerate(values, 1)}


def tex_lin(p: object, q: object, var: str = "x") -> str:
    p, q = as_fraction(p), as_fraction(q)
    head = "" if p == 0 else (var if p == 1 else ("-" + var if p == -1 else f"{tex_num(p)}{var}"))
    if q == 0:
        return head or "0"
    if not head:
        return tex_num(q)
    return f"{head}+{tex_num(q)}" if q > 0 else f"{head}-{tex_num(-q)}"


def _coef(c: int) -> str:
    return "" if c == 1 else f"{c}" + TIMES


def _positive_int_or_reciprocal(b: int, k: int) -> str:
    if k >= 0:
        return str(b**k)
    return rf"\dfrac{{1}}{{{b ** (-k)}}}"


# ------------------------------------------------------------------ curves

def curve_polyline(fn, x0: float, x1: float, y0: float, y1: float, steps: int = 80) -> list[list[float]]:
    points: list[list[float]] = []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        try:
            y = fn(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
        if y0 - 0.05 <= y <= y1 + 0.05:
            points.append([round(x, 4), round(y, 4)])
    return points


def _float(v: object) -> float:
    return float(as_fraction(v)) if not isinstance(v, float) else v


# ============================================================ 4-1 builders

def _ip_same_base(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(80):
        b = rng.choice([2, 3])
        exps = [1, rng.randint(2, 4), rng.randint(2, 4)] if rng.random() < 0.5 else [rng.randint(2, 4), rng.randint(2, 3), rng.randint(1, 3)]
        if b ** sum(exps) <= 4096:
            break
    tex = r"\times ".join(str(b) if e == 1 else f"{b}^{{{e}}}" for e in exps)
    return tex, F(b ** sum(exps))


def _ip_power_of_power(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(80):
        b, p, q = rng.choice([2, 3, 4]), rng.choice([2, 3]), rng.choice([2, 3, 5])
        if b ** (p * q) <= 4096:
            break
    return rf"\left[\left(-{b}\right)^{{{p}}}\right]^{{{q}}}", F((-b) ** (p * q))


def _ip_product_power(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(80):
        p, q, n = rng.choice([2, 3, 5]), rng.choice([2, 3, 4, 5]), rng.choice([2, 3, 4])
        if q**n <= 1024 and p != q:
            break
    tex = rf"\left(\dfrac{{1}}{{{p}}}\right)^{{{n}}}\times {p * q}^{{{n}}}"
    return tex, rational_power(F(1, p), n) * rational_power(p * q, n)


def build_exp_integer_power_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    kinds = spec.get("kinds") or ["same_base", "power_of_power", "product_power"]
    makers = {"same_base": _ip_same_base, "power_of_power": _ip_power_of_power, "product_power": _ip_product_power}
    rows = [makers[k](rng) for k in kinds]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [fraction_plain(v) for _, v in rows]},
        explanation="同底數相乘指數相加；乘冪的乘冪指數相乘；指數相同時底數可先相乘。",
    )


_FACTOR_BASES = {6: {2: 1, 3: 1}, 10: {2: 1, 5: 1}, 12: {2: 2, 3: 1}, 15: {3: 1, 5: 1}, 18: {2: 1, 3: 2}, 20: {2: 2, 5: 1}, 45: {3: 2, 5: 1}}


def build_exp_prime_factor_exponent(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(200):
        bases = rng.sample(sorted(_FACTOR_BASES), 3)
        exps = [rng.choice([-4, -3, -2, 2, 3, 4, 5]) for _ in bases]
        vec = {2: 0, 3: 0, 5: 0}
        for base, e in zip(bases, exps):
            for p, k in _FACTOR_BASES[base].items():
                vec[p] += k * e
        coef = [rng.choice([1, 2, 3]), rng.choice([1, 2]), rng.choice([1, 2])]
        value = coef[0] * vec[2] + coef[1] * vec[3] + coef[2] * vec[5]
        if all(vec.values()) and abs(value) <= 40:
            break
    lhs = r"\times ".join(f"{b}^{{{e}}}" for b, e in zip(bases, exps))
    combo = "".join(
        (("" if i == 0 else "+") + ("" if c == 1 else str(c)) + v)
        for i, (c, v) in enumerate(zip(coef, "xyz"))
    )
    equation = lhs + "=2^{x}" + TIMES + "3^{y}" + TIMES + "5^{z}"
    question = (
        f"若 {m('x')}、{m('y')}、{m('z')} 為有理數，且 {m(equation)}，"
        f"試求 {m(combo)} 之值。"
    )
    return pack(
        spec["op"], question=question, answer=str(value),
        params={"x": vec[2], "y": vec[3], "z": vec[5], "coef": coef},
        explanation="把每個底數做質因數分解，再比較 2、3、5 的指數。",
    )


def build_exp_law_product_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    p, q = sorted(rng.sample([2, 3, 5], 2))
    t, k = rng.randint(6, 10), rng.choice([1, 2])
    m1 = rng.randint(2, t + k - 2)
    n1 = rng.randint(1, t - 1)
    a_exp, b_exp = (m1, n1), (t + k - m1, t - n1)
    pq = p * q

    def form(pp: int, kk: int, base: int, tt: int) -> tuple[str, str, int]:
        head = "" if kk == 0 else (f"{pp}" if kk == 1 else f"{pp}^{{{kk}}}")
        tex = (head + r"\times " if head else "") + f"{base}^{{{tt}}}"
        return f"{pp}^{kk}*{base}^{tt}", m(tex), pp**kk * base**tt

    correct = form(p, k, pq, t)
    pool = [form(p, 0, pq, t), form(p, 0, pq, t + k), form(q, k, pq, t), form(p, k, pq, t + 1), form(p, k + 1, pq, t - 1)]
    values = {row[0]: row[2] for row in [correct, *pool]}
    choices, label = make_choices(
        rng, correct[:2], [row[:2] for row in pool], same=lambda a, b: values[a] == values[b],
    )
    a_tex = f"a={p}^{{{a_exp[0]}}}" + TIMES + f"{q}^{{{a_exp[1]}}}"
    b_tex = f"b={p}^{{{b_exp[0]}}}" + TIMES + f"{q}^{{{b_exp[1]}}}"
    ab_tex = m("a" + TIMES + "b")
    question = f"若 {m(a_tex)}，{m(b_tex)}，則 {ab_tex} 的值為何？"
    return pack(
        spec["op"], question=question, answer=correct[0], presentation="single_choice",
        choices=choices, correct_label=label, params={"p": p, "q": q, "t": t, "k": k},
        explanation=f"同底數相乘指數相加，得 \\({p}^{{{t + k}}}\\times {q}^{{{t}}}\\)，再把 \\({p}^{{{t}}}\\times {q}^{{{t}}}\\) 合成 \\({pq}^{{{t}}}\\)。",
    )


def _ie_numeric(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(200):
        p = rng.choice([2, 3])
        k, j = rng.randint(2, 4), rng.randint(2, 5)
        mm, nn = rng.choice([2, 3]), rng.choice([2, 3])
        e = -k * mm + j * nn
        if p**k <= 81 and p**j <= 243 and k != j and e != 0 and -3 <= e <= 3:
            break
    tex = rf"\left(\dfrac{{1}}{{{p ** k}}}\right)^{{{mm}}}\times {p ** j}^{{{nn}}}"
    return tex, rational_power(p, e)


def _ie_monomial2(rng: random.Random) -> tuple[str, dict]:
    for _ in range(200):
        p1 = rng.choice([-3, -2, -1, 2, 3])
        q1, r1 = rng.choice([2, 3]), rng.choice([2, 3])
        s = rng.choice([-3, -2, 2])
        p2, q2 = rng.choice([-3, -2, 2, 3]), rng.choice([-4, -3, -2, 2, 3])
        t = rng.choice([-3, -2, 2, 3])
        result = mono_mul(mono_pow(mono_mul(mono(a=p1), mono_pow(mono(b=q1), r1)), s), mono_pow(mono(a=p2, b=q2), t))
        if result and max(abs(v) for v in result.values()) <= 15:
            break
    tex = (
        rf"\left[{_pw('a', p1)}\times \left({_pw('b', q1)}\right)^{{{r1}}}\right]^{{{s}}}"
        rf"\times \left({_pw('a', p2)}\times {_pw('b', q2)}\right)^{{{t}}}"
    )
    return tex, result


def _ie_monomial1(rng: random.Random) -> tuple[str, dict]:
    for _ in range(200):
        p, q, r, s = rng.choice([2, 3, 4]), rng.choice([-3, -2, 2]), rng.randint(2, 9), rng.choice([-3, -2, 2])
        result = mono_pow(mono_mul(mono_pow(mono(a=p), q), mono(a=r)), s)
        if result and max(abs(v) for v in result.values()) <= 15:
            break
    return rf"\left[\left({_pw('a', p)}\right)^{{{q}}}\times {_pw('a', r)}\right]^{{{s}}}", result


def _ie_monomial_frac(rng: random.Random) -> tuple[str, dict]:
    for _ in range(200):
        p, q, r = rng.randint(2, 5), rng.choice([-4, -3, -2, 2, 3]), rng.choice([-3, -2, 2])
        result = mono_pow(mono_mul(mono(a=-p), mono(a=q)), r)
        if result and max(abs(v) for v in result.values()) <= 16:
            break
    return rf"\left(\dfrac{{1}}{{{_pw('a', p)}}}\times {_pw('a', q)}\right)^{{{r}}}", result


def build_exp_integer_exponent_simplify(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {"numeric": _ie_numeric, "monomial2": _ie_monomial2, "monomial1": _ie_monomial1, "monomial_frac": _ie_monomial_frac}
    rows = [makers[k](rng) for k in spec["kinds"]]
    answers = [v if isinstance(v, Fraction) else mono_plain(v) for _, v in rows]
    uses_b = any(isinstance(v, dict) and "b" in t for t, v in rows)
    cond = m(r"a\ne 0") + ("、" + m(r"b\ne 0") if uses_b else "")
    return pack(
        spec["op"], prompt=f"設 {cond}，化簡下列各式：", items=_items([m(t) for t, _ in rows]),
        answer=_parts(answers), params={"answers": [str(a) if isinstance(a, str) else fraction_plain(a) for a in answers]},
        explanation="負指數表示倒數：\\(a^{-n}=\\dfrac{1}{a^{n}}\\)；再用指數律合併同底數。",
    )


def build_exp_fill_integer_exponent(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    p, k = rng.choice([2, 3, 5, 7]), rng.choice([2, 3, 4])
    q = rng.randint(2, 12)
    p3, k3 = rng.choice([(2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (5, 2)])
    u, v = rng.choice([(3, 2), (2, 3), (4, 5), (5, 4), (3, 4), (5, 3)])
    sq = rng.random() < 0.4
    left4 = rf"\dfrac{{{u ** 2}}}{{{v ** 2}}}" if sq else rf"\dfrac{{{u}}}{{{v}}}"
    texts = [
        m(rf"\dfrac{{1}}{{{p}^{{{k}}}}}={p}^{{\square}}"),
        m(rf"1={q}^{{\square}}"),
        m(rf"\dfrac{{1}}{{{p3 ** k3}}}={p3}^{{\square}}"),
        m(rf"{left4}=\left(\dfrac{{{v}}}{{{u}}}\right)^{{\square}}"),
    ]
    answers = [F(-k), F(0), F(-k3), F(-2 if sq else -1)]
    square = m(r"\square")
    return pack(
        spec["op"], prompt=f"在下列等式中的 {square} 填上整數：", items=_items(texts),
        answer=_parts(answers), params={"answers": [fraction_plain(a) for a in answers]},
        explanation="\\(a^{0}=1\\)，\\(\\dfrac{1}{a^{n}}=a^{-n}\\)；倒數的底數用負指數表示。",
    )


def build_exp_zero_negative_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    p = rng.randint(2, 9)
    u, v = rng.choice([(2, 3), (3, 4), (4, 5), (5, 2), (3, 7)])
    c = rng.choice([1, 2, 3])
    if c == 1:
        t1, v1 = rf"{p}^{{0}}+\left(\dfrac{{{u}}}{{{v}}}\right)^{{0}}", F(2)
    else:
        t1, v1 = rf"{c}\times {p}^{{0}}-\left(\dfrac{{{u}}}{{{v}}}\right)^{{0}}", F(c - 1)
    b, k = rng.choice([(2, 3), (2, 2), (3, 2), (5, 1), (2, 4)])
    r, s = rng.choice([(4, 3), (3, 2), (5, 2), (2, 5), (3, 4)])
    t2 = rf"{b}^{{-{k}}}+\left(\dfrac{{{r}}}{{{s}}}\right)^{{-2}}"
    v2 = rational_power(b, -k) + rational_power(F(r, s), -2)
    t3, v3 = _ie_numeric(rng)
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t1), m(t2), m(t3)]),
        answer=_parts([v1, v2, v3]), params={"values": [fraction_plain(x) for x in (v1, v2, v3)]},
        explanation="非零數的零次方為 1；負指數先化成倒數再計算。",
    )


# --------------------------------------------------------- rational powers

def _rp_int_neg_frac(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(200):
        r, k, mm = rng.choice([2, 3, 5]), rng.choice([2, 3]), rng.choice([1, 2, 3, 4, 5])
        if math.gcd(mm, k) == 1 and r**k <= 125 and r**mm <= 256:
            break
    e = F(-mm, k)
    return tex_power(r**k, e), rational_power(r**k, e)


def _rp_frac_root(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(300):
        p, q = rng.randint(1, 9), rng.randint(2, 9)
        k, mm = rng.choice([2, 3, 4, 5]), rng.choice([1, 2, 3])
        sign = rng.choice([1, 1, -1])
        if math.gcd(p, q) == 1 and p != q and math.gcd(mm, k) == 1 and p**k <= 1000 and q**k <= 1000 and max(p, q) ** mm <= 1000:
            break
    base = F(p**k, q**k)
    e = F(sign * mm, k)
    dec = fraction_as_terminating_decimal(e) if rng.random() < 0.45 else None
    return tex_power(base, e, exp_decimal=dec), rational_power(base, e)


_DEC_SQUARES = [(F(1, 2), "0.25"), (F(1, 5), "0.04"), (F(1, 10), "0.01"), (F(3, 10), "0.09"), (F(2, 5), "0.16"), (F(3, 5), "0.36"), (F(1, 4), "0.0625")]


def _rp_decimal_base(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(200):
        root, shown = rng.choice(_DEC_SQUARES)
        mm = rng.choice([1, 3, 5])
        sign = rng.choice([-1, -1, 1])
        value = rational_power(root, sign * mm)
        if value.numerator <= 1000 and value.denominator <= 1000:
            break
    e = F(sign * mm, 2)
    dec = fraction_as_terminating_decimal(e) if rng.random() < 0.5 else None
    return tex_power(root * root, e, base_decimal=shown, exp_decimal=dec), value


def build_exp_rational_power_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {"int_neg_frac": _rp_int_neg_frac, "frac_root": _rp_frac_root, "decimal_base": _rp_decimal_base}
    rows = [makers[k](rng) for k in spec["kinds"]]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [fraction_plain(v) for _, v in rows]},
        explanation="\\(a^{\\frac{m}{n}}=\\left(\\sqrt[n]{a}\\right)^{m}\\)；小數先化成分數，負指數取倒數。",
    )


def _re_power_product(rng: random.Random) -> tuple[str, dict]:
    for _ in range(300):
        k = rng.choice([2, 3, 4, 5])
        mm = rng.choice([1, 2, 3])
        if math.gcd(mm, k) != 1:
            continue
        inner1 = mono(a=k * rng.randint(1, 3), b=k * rng.randint(1, 3))
        r = F(mm, k)
        if rng.random() < 0.5:
            u = rng.choice([-6, -4, -3, -2])
            inner2 = mono(a=F(rng.choice([-4, -2, -1, 1, 2, 3]), abs(u)), b=F(rng.choice([-3, -1, 1, 2, 5]), abs(u)))
        else:
            d = rng.choice([2, 3, 4])
            u = F(-1, d)
            inner2 = mono(a=d * rng.choice([-2, -1, 1, 2]), b=d * rng.choice([-2, -1, 1, 2]))
        if len(inner2) < 2:
            continue
        result = mono_mul(mono_pow(inner1, r), mono_pow(inner2, u))
        if result and all(v.denominator == 1 for v in result.values()) and max(abs(v) for v in result.values()) <= 20:
            break
    tex = (
        rf"\left({tex_mono(inner1)}\right)^{{{tex_exp(r)}}}\times "
        rf"\left({tex_mono(inner2)}\right)^{{{tex_exp(u)}}}"
    )
    return tex, result


def _re_radical_quotient(rng: random.Random) -> tuple[str, dict]:
    for _ in range(300):
        mi, ni = rng.sample([2, 3, 4, 5, 6], 2)
        p, q = rng.randint(1, 7), rng.randint(1, 7)
        e = F(p, mi) - F(q, ni)
        if p % mi and q % ni and e != 0 and e.denominator <= 30:
            break
    top = tex_radical(_pw("a", p), mi)
    bottom = tex_radical(_pw("a", q), ni)
    return rf"\dfrac{{{top}}}{{{bottom}}}", mono(a=e)


def _re_radical_product(rng: random.Random) -> tuple[str, dict]:
    for _ in range(300):
        if rng.random() < 0.5:
            roots = rng.sample([2, 3, 4, 6, 12], 3)
            pows = [rng.choice([1, 1, 2, 3, 5]) for _ in roots]
            e = sum(F(pw, rt) for pw, rt in zip(pows, roots))
            if any(pw % rt == 0 for pw, rt in zip(pows, roots)) or e.denominator > 12:
                continue
            tex = r"\times ".join(tex_radical(_pw("a", pw), rt) for pw, rt in zip(pows, roots))
        else:
            r1, r2 = rng.choice([(6, 12), (4, 8), (3, 6), (2, 4), (6, 18)])
            p1, p2, p3 = rng.randint(1, 5), rng.randint(1, 7), rng.randint(2, 9)
            e = F(p1, r1) + F(p2 + p3, r2)
            if p1 % r1 == 0 or e.denominator > 12:
                continue
            inner = _pw("a", p2) + TIMES + _pw("a", p3)
            tex = tex_radical(_pw("a", p1), r1) + TIMES + tex_radical(inner, r2)
        break
    return tex, mono(a=e)


def _re_bracket_half(rng: random.Random) -> tuple[str, dict]:
    for _ in range(300):
        p1, q1 = rng.randint(1, 4), rng.randint(1, 5)
        p2, q2 = rng.choice([-3, -2, -1, 1, 2]), rng.choice([-2, 1, 2, 3, 4])
        sq = rng.random() < 0.5
        inner = mono_mul(mono(a=p1, b=q1), mono_pow(mono(a=p2, b=q2), 2)) if not sq else mono_mul(mono_pow(mono(a=p1, b=q1), 2), mono(a=p2, b=q2))
        result = mono_pow(inner, F(1, 2))
        if result and all(v.denominator == 1 for v in result.values()) and (p2 != 0 and q2 != 0):
            break
    first = rf"\left({_pw('a', p1)}{_pw('b', q1)}\right)" + ("^{2}" if sq else "")
    second = rf"\left({_pw('a', p2)}{_pw('b', q2)}\right)" + ("" if sq else "^{2}")
    return rf"\left[{first}{second}\right]^{{\frac{{1}}{{2}}}}", result


def _re_three_var(rng: random.Random) -> tuple[str, dict]:
    for _ in range(300):
        e1 = [3 * rng.choice([-3, -2, -1, 1, 2, 3]) for _ in range(3)]
        e2 = [2 * rng.choice([-3, -2, -1, 1, 2, 3]) for _ in range(3)]
        result = mono_mul(mono_pow(mono(a=e1[0], b=e1[1], c=e1[2]), F(1, 3)), mono_pow(mono(a=e2[0], b=e2[1], c=e2[2]), F(-1, 2)))
        if result and len(result) <= 2:
            break
    t1 = "".join(_pw(v, e) for v, e in zip("abc", e1))
    t2 = "".join(_pw(v, e) for v, e in zip("abc", e2))
    return rf"\left({t1}\right)^{{\frac{{1}}{{3}}}}\times \left({t2}\right)^{{-\frac{{1}}{{2}}}}", result


def build_exp_rational_exponent_simplify(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {
        "power_product": _re_power_product,
        "radical_quotient": _re_radical_quotient,
        "radical_product": _re_radical_product,
        "bracket_half": _re_bracket_half,
        "three_var": _re_three_var,
    }
    rows = [makers[k](rng) for k in spec["kinds"]]
    answers = [mono_plain(v) for _, v in rows]
    letters = sorted({ch for t, _ in rows for ch in "abc" if ch in re.sub(r"\\[A-Za-z]+", "", t)})
    cond = "，".join(m(f"{ch}>0") for ch in letters)
    explanation = "根式化為分數指數：\\(\\sqrt[n]{a^{m}}=a^{\\frac{m}{n}}\\)，再用指數律合併。"
    if len(rows) == 1:
        return pack(
            spec["op"], question=f"設 {cond}，試化簡 {m(rows[0][0])}。", answer=answers[0],
            params={"answer": answers[0]}, explanation=explanation,
        )
    return pack(
        spec["op"], prompt=f"設 {cond}，試化簡下列各式：", items=_items([m(t) for t, _ in rows]),
        answer=_parts(answers), params={"answers": answers}, explanation=explanation,
    )


def _combo_value_choices(rng: random.Random, value: Fraction, extra: list[Fraction]) -> list[tuple[str, str]]:
    pool = [*extra, value + 1, value - 1, 2 * value, value + 2]
    return [num_choice(v) for v in pool]


def build_exp_rational_power_combo(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "sum3")
    presentation = spec.get("presentation", "short_answer")
    if variant == "same_base":
        for _ in range(200):
            b, k = rng.choice([2, 3, 5]), rng.choice([2, 3])
            p, q = rng.randint(1, 8), rng.randint(1, 8)
            r = p + q - 3 * k
            if b**k <= 125 and r > 0 and p % 3 and q % 3 and r % 3:
                break
        tex = rf"\dfrac{{{b}^{{\frac{{{p}}}{{3}}}}\times {b}^{{\frac{{{q}}}{{3}}}}}}{{{b}^{{\frac{{{r}}}{{3}}}}}}"
        value = rational_power(b, k)
        extra = [F(b ** (k + 1)), F(b ** (k - 1)), F(k * b)]
        question = f"{m(tex + '=')}"
    elif variant == "sum2":
        for _ in range(200):
            r, k, mm = rng.choice([2, 3]), rng.choice([2, 3]), rng.choice([1, 2])
            p, q = rng.randint(1, 4), rng.randint(2, 4)
            n = rng.choice([3, 4, 5])
            if math.gcd(mm, k) == 1 and math.gcd(p, q) == 1 and p != q and (p**n) <= 1024 and (q**n) <= 1024:
                break
        t1 = tex_power(r**k, F(mm, k))
        t2 = tex_power(F(p**n, q**n), F(1, n))
        value = rational_power(r**k, F(mm, k)) + F(p, q)
        extra = [rational_power(r**k, F(mm, k)) + F(q, p), F(r**mm) * F(p, q)]
        question = f"{m(t1 + '+' + t2 + '=')}"
    else:
        for _ in range(300):
            p1, q1 = rng.randint(2, 10), rng.randint(2, 10)
            p2, q2 = rng.randint(2, 7), rng.randint(2, 7)
            s, t = rng.randint(4, 9), rng.randint(2, 5)
            if not (math.gcd(p1, q1) == 1 and math.gcd(p2, q2) == 1 and math.gcd(s, t) == 1 and p1 != q1 and p2 != q2
                    and p1**3 <= 1000 and q1**3 <= 1000 and p2**3 <= 400 and q2**3 <= 400 and s > t):
                continue
            b1 = F(p1**3, q1**3)
            b2 = F(p2**3, q2**3)
            b3 = F(s * s, t * t)
            value = rational_power(b1, F(-2, 3)) - rational_power(b2, F(-1, 3)) + rational_power(b3, F(1, 2))
            if value.denominator <= 36:
                break
        else:
            raise ValueError("combo_value_not_clean")
        t1 = tex_power(b1, F(-2, 3))
        t2 = tex_power(b2, F(-1, 3))
        t3 = tex_power(b3, F(1, 2), mixed=True)
        extra = [rational_power(b1, F(-2, 3)) + rational_power(b2, F(-1, 3)) + rational_power(b3, F(1, 2))]
        question = f"已知 {m('A=' + t1 + '-' + t2 + '+' + t3)}，則 {m('A')} 之值為何？"
    choices = label = None
    if presentation == "single_choice":
        choices, label = make_choices(rng, num_choice(value), _combo_value_choices(rng, value, extra), same=same_number)
        if variant != "sum3":
            question = question
    return pack(
        spec["op"], question=question, answer=fraction_plain(value), presentation=presentation,
        choices=choices, correct_label=label, params={"value": fraction_plain(value), "variant": variant},
        explanation="每一項先化成最簡分數的有理數次方，再依序計算。",
    )


_GROWTH_COMBOS = [
    (1, 365, "每天", "一年"),
    (2, 100, "每天", "一百天"),
    (5, 60, "每天", "六十天"),
    (10, 30, "每天", "三十天"),
    (1, 200, "每天", "兩百天"),
    (3, 60, "每天", "六十天"),
]


def build_exp_growth_decay_model_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    rate, n, per, span = rng.choice(_GROWTH_COMBOS)
    who = rng.choice(["功力", "實力", "能力"])
    with localcontext() as ctx:
        ctx.prec = 40
        g = (Decimal(100 + rate) / 100) ** n
        d = (Decimal(100 - rate) / 100) ** n
    k = int(g) - 1
    remain_pct = int((d * 100).to_integral_value(rounding=ROUND_CEILING))
    loss_pct = 100 - remain_pct
    up = f"{fraction_as_terminating_decimal(F(100 + rate, 100))}"
    dn = f"{fraction_as_terminating_decimal(F(100 - rate, 100))}"
    remain = fraction_as_terminating_decimal(F(remain_pct, 100))
    loss = fraction_as_terminating_decimal(F(loss_pct, 100))

    def row(a: str, b: str) -> tuple[str, str]:
        return f"{a}|{b}".replace("\\", ""), f"{m(a)} 且 {m(b)}"

    correct = row(rf"{up}^{{{n}}}\ge {k + 1}", rf"{dn}^{{{n}}}\le {remain}")
    pool = [
        row(rf"{n}^{{{up}}}\le {k + 1}", rf"{n}^{{{dn}}}\ge {remain}"),
        row(rf"{up}^{{{n}}}\ge {k}", rf"{dn}^{{{n}}}\le {loss}"),
        row(rf"{n}^{{{up}}}\le {k}", rf"{n}^{{{dn}}}\ge {loss}"),
        row(rf"{up}^{{{n}}}\ge {k + 1}", rf"{dn}^{{{n}}}\le {loss}"),
    ]
    choices, label = make_choices(rng, correct, pool)
    question = (
        f"老師勉勵學生：「若{per}增加百分之{rate}的{who}，則{span}後至少會增加 {k} 倍；"
        f"反之，{per}減少百分之{rate}的{who}，則{span}後至少流失現今{who}的 {loss_pct}%」。"
        f"這段話運用了指數成長與衰退的概念，其數學表達最貼切下列哪一個選項？"
    )
    return pack(
        spec["op"], question=question, answer=correct[0], presentation="single_choice",
        choices=choices, correct_label=label, params={"rate": rate, "n": n, "k": k, "remain_pct": remain_pct},
        explanation=f"每期乘上 \\({up}\\)，{span}後為 \\({up}^{{{n}}}\\) 倍；增加 {k} 倍即變為 {k + 1} 倍。每期乘上 \\({dn}\\)，流失 {loss_pct}% 表示剩下不超過 {remain}。",
    )


def build_exp_solve_exponent_radical(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("variant") == "nested":
        for _ in range(300):
            k1, k2 = rng.choice([2, 3]), rng.choice([3, 4, 5])
            p, q = rng.randint(1, 4), rng.randint(1, 6)
            if q % k2 and 2**p <= 16 and 2**q <= 64:
                break
        a = (F(p) + F(q, k2)) / k1
        tex = "2^{a}=" + tex_radical(str(2**p) + TIMES + tex_radical(str(2**q), k2), k1)
        question = f"若 {m(tex)}，則 {m('a=')}"
        pool = [a * k1, a / k1, 1 / a, F(p + q, k1 * k2), a + 1]
        value = a
        explanation = f"由內而外化成 2 的次方：\\(2^{{{tex_exp(F(p) + F(q, k2))}}}\\)，再開 {k1} 次方根。"
    else:
        b1, mm = rng.choice([(2, 3), (2, 5), (2, 7), (3, 3), (3, 5), (5, 3)])
        b2, nn = rng.choice([(3, 3), (3, 5), (2, 3), (2, 5), (5, 3), (2, 7)])
        a, b = F(mm, 2), F(-nn, 2)
        op = rng.choice(["a+b", "a-b", "2a+b"])
        value = {"a+b": a + b, "a-b": a - b, "2a+b": 2 * a + b}[op]
        eq1 = f"{b1}^{{a}}=" + tex_radical(str(b1**mm), 2)
        eq2 = f"{b2}^{{b}}=" + r"\dfrac{1}{" + tex_radical(str(b2**nn), 2) + "}"
        question = f"已知 {m('a')}、{m('b')} 為實數，若 {m(eq1)} 且 {m(eq2)}，則 {m(op + '=')}"
        pool = [a - b if op != "a-b" else a + b, -value, value + 1, value - 1, a * b, F(mm + nn, 2)]
        explanation = f"\\(\\sqrt{{{b1 ** mm}}}={b1}^{{\\frac{{{mm}}}{{2}}}}\\)，\\(\\dfrac{{1}}{{\\sqrt{{{b2 ** nn}}}}}={b2}^{{-\\frac{{{nn}}}{{2}}}}\\)，比較指數。"
    choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool if v != 0], same=same_number)
    return pack(
        spec["op"], question=question, answer=fraction_plain(value), presentation="single_choice",
        choices=choices, correct_label=label, params={"value": fraction_plain(value)}, explanation=explanation,
    )


# ============================================================ 4-2 builders

_EXP_BASES_UP = [F(2), F(3), F(4)]
_EXP_BASES_DOWN = [F(1, 2), F(1, 3), F(1, 4)]


def _exp_fn_tex(base: Fraction) -> str:
    return f"y={tex_base(base)}^{{x}}"


def _log_fn_tex(base: Fraction) -> str:
    return rf"y=\log_{{{tex_num(base, small=True)}}} x"


def build_graph_sketch_table(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    fn = spec.get("fn", "exp")
    mode = spec.get("mode", "single")
    if fn == "exp":
        base = rng.choice(_EXP_BASES_UP if spec.get("base") == "up" else _EXP_BASES_DOWN if spec.get("base") == "down" else _EXP_BASES_UP + _EXP_BASES_DOWN)
        if mode == "pair":
            base = rng.choice(_EXP_BASES_UP + [F(3, 2)])
            inv = 1 / base
            xs = rng.choice([(2, -2), (2, -1), (3, -2)])
            prompt = f"在同一坐標平面描繪 {m(_exp_fn_tex(base))} 與 {m(_exp_fn_tex(inv))} 的圖形時，先列表描點。試回答："
            texts = [
                f"{m(_exp_fn_tex(base))} 在 {m(f'x={xs[0]}')} 時的 {m('y')} 值",
                f"{m(_exp_fn_tex(inv))} 在 {m(f'x={xs[0]}')} 時的 {m('y')} 值",
                f"{m(_exp_fn_tex(inv))} 在 {m(f'x={xs[1]}')} 時的 {m('y')} 值",
                f"兩圖形對稱於直線 {m('x=k')}，求 {m('k')}",
            ]
            answers = [rational_power(base, xs[0]), rational_power(inv, xs[0]), rational_power(inv, xs[1]), F(0)]
            checkers = {}
        else:
            xs = rng.choice([(-1, 0, 2), (-2, 0, 1), (-1, 0, 1), (-2, 0, 2)])
            prompt = f"描繪 {m(_exp_fn_tex(base))} 的圖形時，先列表描點。試回答："
            texts = [f"{m(f'x={x}')} 時的 {m('y')} 值" for x in xs] + ["此函數為遞增函數或遞減函數？（填「遞增」或「遞減」）"]
            answers = [rational_power(base, x) for x in xs] + ["遞增" if base > 1 else "遞減"]
            checkers = {"(4)": "text_checker"}
    else:
        base = rng.choice([F(2), F(3)] if spec.get("base") == "up" else [F(1, 2), F(1, 3)] if spec.get("base") == "down" else [F(2), F(3), F(1, 2), F(1, 3)])
        if mode == "pair":
            base = rng.choice([F(2), F(3)])
            inv = 1 / base
            k = rng.choice([2, 3])
            prompt = f"在同一坐標平面描繪 {m(_log_fn_tex(base))} 與 {m(_log_fn_tex(inv))} 的圖形時，先列表描點。試回答："
            texts = [
                f"{m(_log_fn_tex(base))} 在 {m(f'x={tex_num(base ** k)}')} 時的 {m('y')} 值",
                f"{m(_log_fn_tex(inv))} 在 {m(f'x={tex_num(base ** k)}')} 時的 {m('y')} 值",
                f"{m(_log_fn_tex(inv))} 在 {m(f'x={tex_num(inv)}')} 時的 {m('y')} 值",
                f"兩圖形對稱於直線 {m('y=k')}，求 {m('k')}",
            ]
            answers = [F(k), F(-k), F(1), F(0)]
            checkers = {}
        else:
            ks = rng.choice([(-1, 0, 2), (-2, 0, 1), (-1, 0, 1), (-2, 0, 2)])
            xs_tex = [tex_num(rational_power(base, k)) for k in ks]
            prompt = f"描繪 {m(_log_fn_tex(base))} 的圖形時，先列表描點。試回答："
            texts = [f"{m(f'x={x}')} 時的 {m('y')} 值" for x in xs_tex] + ["此函數為遞增函數或遞減函數？（填「遞增」或「遞減」）"]
            answers = [F(k) for k in ks] + ["遞增" if base > 1 else "遞減"]
            checkers = {"(4)": "text_checker"}
    return pack(
        spec["op"], prompt=prompt, items=_items(texts), answer=_parts(answers),
        part_checkers=checkers, params={"fn": fn, "base": fraction_plain(base), "mode": mode},
        explanation="代入各 \\(x\\) 值求出坐標點；底數大於 1 時圖形遞增，介於 0 與 1 之間時遞減。",
    )


_CMP_UP = [(F(2), "2", None), (F(3), "3", None), (F(5), "5", None), (F(7), "7", None)]
_CMP_DOWN = [(F(1, 2), None, None), (F(2, 3), None, None), (F(1, 2), None, "0.5"), (F(9, 10), None, "0.9"), (F(1, 3), None, None)]
_CMP_EXPS = [F(-3), F(-2), F(-1), F(-1, 2), F(-1, 4), F(1, 3), F(1, 2), F(3, 5), F(3, 4), F(7, 6), F(1), F(3, 2), F(2), F(3), F(4)]


COMPARE_PROMPT = "試比較下列各數之大小（由小到大，以 " + m(r"a\lt b\lt c") + " 的形式作答）："


def order_tex(order: str) -> str:
    return order.replace("<", r"\lt ")


def order_choice(order: str) -> tuple[str, str]:
    """Choice (value, text) for an ascending ordering ``a<b<c``.

    Shown in descending ``>`` form: the choice checker compares display text via
    expression equivalence, which treats ``\\lt`` as a commuting symbol and would
    equate different orderings, while raw ``<`` is unsafe in HTML choice text."""
    names = order.split("<")
    return "order_" + "".join(names), m(">".join(reversed(names)))


def _compare_names(values: list[float], names: list[str]) -> str:
    order = sorted(range(len(values)), key=lambda i: values[i])
    return "<".join(names[i] for i in order)


def _exp_compare_part(rng: random.Random, kind: str, count: int) -> tuple[str, str]:
    names = ["a", "b", "c", "d"][:count]
    exps = rng.sample(_CMP_EXPS, count)
    if kind == "sqrt":
        p = rng.choice([2, 3, 5, 7])
        base_tex = rf"\left(\sqrt{{{p}}}\right)"
        base_val = math.sqrt(p)
        texts = [rf"\sqrt{{{p}}}" if e == 1 else f"{base_tex}^{{{tex_exp(e)}}}" for e in exps]
    else:
        pool = _CMP_UP if kind == "up" else _CMP_DOWN
        base, _shown, dec = rng.choice(pool)
        base_val = float(base)
        texts = [tex_base(base, decimal=dec) if e == 1 else tex_power(base, e, base_decimal=dec) for e in exps]
        if rng.random() < 0.35:
            zero_idx = rng.randrange(count)
            exps[zero_idx] = F(0) if F(0) not in exps else exps[zero_idx]
            if exps[zero_idx] == 0:
                texts[zero_idx] = "1"
    values = [base_val ** float(e) for e in exps]
    if len({round(v, 12) for v in values}) != count:
        raise ValueError("compare_tie")
    shown = "，".join(m(f"{n}={t}") for n, t in zip(names, texts))
    return shown, _compare_names(values, names)


def build_exp_compare_same_base(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("presentation") == "single_choice":
        p = rng.choice([2, 3, 5])
        for _ in range(200):
            (j1, k1), (j3, k3) = rng.sample([(2, 3), (4, 5), (3, 4), (5, 6), (1, 2), (3, 5)], 2)
            r = rng.choice([F(3, 4), F(2, 3), F(4, 5), F(5, 6), F(3, 5), F(1, 2)])
            exps = [F(j1, k1), r, F(j3, k3)]
            if len(set(exps)) == 3 and p ** j1 <= 625 and p ** j3 <= 625:
                break
        texts = [tex_radical(str(p**j1), k1), f"{p}^{{{tex_exp(r)}}}", tex_radical(str(p**j3), k3)]
        names = ["a", "b", "c"]
        correct = _compare_names([float(e) for e in exps], names)
        perms = ["<".join(order) for order in itertools.permutations(names)]
        rng.shuffle(perms)
        choices, label = make_choices(rng, order_choice(correct), [order_choice(pm) for pm in perms])
        question = "設 " + "、".join(m(f"{n}={t}") for n, t in zip(names, texts)) + "，則 " + m("a") + "、" + m("b") + "、" + m("c") + " 之大小關係為"
        return pack(
            spec["op"], question=question, answer=order_choice(correct)[0], presentation="single_choice",
            choices=choices, correct_label=label, params={"exps": [fraction_plain(e) for e in exps]},
            explanation=f"化成同底數 \\({p}\\) 的次方，底數大於 1，指數愈大值愈大。",
        )
    parts = spec["parts"]
    rows = []
    for kind, count in parts:
        for _ in range(50):
            try:
                rows.append(_exp_compare_part(rng, kind, count))
                break
            except ValueError:
                continue
    checkers = {f"({i})": "ordered_inequality_checker" for i in range(1, len(rows) + 1)}
    return pack(
        spec["op"], prompt=COMPARE_PROMPT,
        items=_items([t for t, _ in rows]), answer=_parts([a for _, a in rows]), part_checkers=checkers,
        params={"orders": [a for _, a in rows]},
        explanation="同底數比較：底數大於 1 時指數愈大值愈大；底數介於 0 與 1 之間時指數愈大值愈小。",
    )


def build_exp_model_from_graph(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("variant") == "decay":
        m0, base = rng.choice([(8, F(1, 2)), (4, F(1, 2)), (9, F(1, 3))])
        k = rng.choice([3, 4, 5] if base == F(1, 2) else [2, 3, 4])
        frac = rational_power(base, k)
        thing, unit = rng.choice([("某放射性物質的質量", "公克"), ("某藥物在體內的殘留量", "毫克")])
        period = "半衰期為 1 千年，即每經過 1 千年，質量會衰退成原來的一半" if base == F(1, 2) else "每經過 1 千年，質量會衰退成原來的 \\(\\dfrac{1}{3}\\)"
        if thing.startswith("某藥物"):
            period = period.replace("1 千年", "1 小時").replace("質量", "殘留量")
        time_word = "千年" if "千年" in period else "小時"
        coef_plain = f"{m0}*({fraction_plain(base)})^x"
        question = (
            f"下圖為{thing} {m('y')}（{unit}）與時間 {m('x')}（{time_word}）的關係圖，假設其關係為指數函數，且{period}。試回答："
        )
        texts = [f"試求此指數函數 {m('f(x)')}", f"經過幾{time_word}後，剩下的量只有原來的 {m(tex_num(frac))}"]
        answers = [coef_plain, F(k)]
        pts = [(0, F(m0)), (1, m0 * base), (2, m0 * base * base)]
        fn = lambda x: m0 * float(base) ** x  # noqa: E731
    else:
        c, base = rng.choice([(1, F(2)), (2, F(2)), (1, F(3))])
        n = rng.choice([4, 5, 6])
        lo, hi = c * base ** (n - 1), c * base**n
        threshold = rng.randint(int(lo) + 1, int(hi) - 1) if hi - lo > 2 else int(lo)
        thing, unit, word = rng.choice([
            ("某池塘中布袋蓮蔓延的面積", "平方公尺", "面積"),
            ("某水域藻類覆蓋的面積", "平方公尺", "面積"),
            ("某培養皿中細菌的數量", "千個", "數量"),
        ])
        coef_plain = f"{c}*{fraction_plain(base)}^x" if c != 1 else f"{fraction_plain(base)}^x"
        question = f"下圖為{thing} {m('y')}（{unit}）與時間 {m('x')}（月）的關係圖，假設其關係為指數函數。試回答："
        texts = [f"試求此指數函數 {m('f(x)')}", f"在第幾個月時，{word}就會超過 {threshold} {unit}"]
        answers = [coef_plain, F(n)]
        pts = [(0, F(c)), (1, c * base), (2, c * base * base)]
        fn = lambda x: c * float(base) ** x  # noqa: E731
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": True,
        "scale_mode": "cartesian_equal_units",
        "x_range": [-1, 4],
        "y_range": [-1, 10],
        "curves": [{"label": "y=f(x)", "points": curve_polyline(fn, -0.8, 3.8, -1, 10), "label_at": None}],
        "points": [{"x": float(x), "y": float(y), "label": f"({x}, {fraction_plain(y)})"} for x, y in pts],
        "lines": [],
        "function": {"type": "exp", "coef": fraction_plain(pts[0][1]), "base": fraction_plain(base)},
    }
    return pack(
        spec["op"], prompt=question, items=_items(texts), answer=_parts(answers), visual=visual,
        part_labels={"(1)": "(1) f(x)=", "(2)": "(2)"},
        params={"coef": fraction_plain(pts[0][1]), "base": fraction_plain(base)},
        explanation="由 \\(x=0\\) 的點得係數，再由相鄰兩點的比值得底數；最後解不等式或比較次方。",
        visual_type="DETERMINISTIC_VISUAL",
    )


def _exp_statements(base: Fraction, tex_base_text: str, *, fname: str = "y") -> list[tuple[str, bool]]:
    fn = m(f"y={tex_base_text}^{{x}}")
    up = base > 1
    inv = tex_num(1 / base) if (1 / base).denominator != 1 else str((1 / base).numerator)
    rows = [
        (f"{fn} 的圖形必通過點 {m('(0,1)')}", True),
        (f"{fn} 的圖形必通過點 {m('(1,0)')}", False),
        (f"{fn} 為遞增函數", up),
        (f"{fn} 為遞減函數", not up),
        (f"{fn} 的圖形與 {m('x')} 軸不相交", True),
        (f"{fn} 的圖形與 {m('y')} 軸不相交", False),
        (f"{fn} 的值域為所有正實數", True),
        (f"{fn} 的值域為所有實數", False),
        (f"{fn} 的圖形只分布在第一、二象限", True),
        (f"{fn} 的圖形只分布在第一、四象限", False),
        (f"{fn} 的圖形與 {m(f'y={tex_base(1 / base)}^{{x}}')} 的圖形對稱於 {m('y')} 軸", True),
        (f"{fn} 的圖形與 {m(f'y={tex_base(1 / base)}^{{x}}')} 的圖形對稱於 {m('x')} 軸", False),
    ]
    if fname == "f":
        f_m1 = rational_power(base, -1)
        rows += [
            (m(f"f(-1)={tex_num(f_m1)}"), True),
            (m(f"f(-1)={tex_num(-base)}"), False),
            (m("f(0)=0"), False),
            (m("f(-3)>f(-2)"), not up),
            (f"當 {m('x_{2}>x_{1}')} 時，{m('f(x_{2})>f(x_{1})')}", up),
        ]
        rows = [(t.replace(fn, m(f'f(x)={tex_base_text}^{{x}}')), v) for t, v in rows]
    return rows


def _log_statements(base: Fraction) -> list[tuple[str, bool]]:
    b = tex_num(base, small=True)
    fn = m(rf"y=\log_{{{b}}} x")
    up = base > 1
    inv_fn = m(rf"y=\log_{{{tex_num(1 / base, small=True)}}} x")
    exp_fn = m(f"y={tex_base(base)}^{{x}}")
    return [
        (f"{fn} 的圖形必通過點 {m('(1,0)')}", True),
        (f"{fn} 的圖形必通過點 {m('(0,1)')}", False),
        (f"{fn} 為遞增函數", up),
        (f"{fn} 為遞減函數", not up),
        (f"{fn} 的圖形與 {m('y')} 軸不相交", True),
        (f"{fn} 的圖形與 {m('x')} 軸不相交", False),
        (f"{fn} 的定義域為所有正實數", True),
        (f"{fn} 的定義域為所有實數", False),
        (f"{fn} 的圖形只分布在第一、四象限", True),
        (f"{fn} 的圖形只分布在第一、二象限", False),
        (f"{fn} 的圖形與 {exp_fn} 的圖形對稱於直線 {m('y=x')}", True),
        (f"{fn} 的圖形與 {exp_fn} 的圖形對稱於直線 {m('y=-x')}", False),
        (f"{fn} 的圖形與 {inv_fn} 的圖形對稱於 {m('x')} 軸", True),
        (f"{fn} 的圖形與 {inv_fn} 的圖形對稱於 {m('y')} 軸", False),
    ]


def _pair_statements(base: Fraction) -> list[tuple[str, bool]]:
    return [
        (f"{m('y=f(x)')} 與 {m('y=g(x)')} 的圖形對稱於 {m('y')} 軸", True),
        (f"{m('y=f(x)')} 與 {m('y=g(x)')} 的圖形對稱於 {m('x')} 軸", False),
        (f"兩圖形交於點 {m('(0,1)')}", True),
        (f"兩圖形交於點 {m('(1,0)')}", False),
        (f"{m('f(x)')} 為遞增函數，{m('g(x)')} 為遞減函數", True),
        (f"{m('f(x)')} 為遞減函數，{m('g(x)')} 為遞增函數", False),
        (f"當 {m('x>0')} 時，{m('f(x)>g(x)')}", True),
        (f"當 {m('x>0')} 時，{m('f(x)<g(x)')}", False),
        (m("f(2)=g(-2)"), True),
        (m("f(2)=g(2)"), False),
    ]


def build_graph_property_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    pool = spec.get("pool", "exp")
    mode = spec.get("mode") or rng.choice(["correct", "incorrect"])
    visual = None
    visual_type = "TEXT_ONLY"
    head = "下列敘述何者正確？" if mode == "correct" else "下列敘述何者不正確？"
    if pool == "pair":
        base = rng.choice([F(2), F(3)])
        rows = _pair_statements(base)
        inv = 1 / base
        question = (
            f"設 {m(f'f(x)={tex_base(base)}^{{x}}')}，{m(f'g(x)={tex_base(inv)}^{{x}}')}，"
            f"兩函數的圖形如下圖所示。{head}"
        )
        visual = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "scale_mode": "cartesian_equal_units",
            "x_range": [-3, 3],
            "y_range": [-1, 5],
            "curves": [
                {"label": "y=f(x)", "points": curve_polyline(lambda x: float(base) ** x, -3, 3, -1, 5), "function": {"type": "exp", "base": fraction_plain(base)}},
                {"label": "y=g(x)", "points": curve_polyline(lambda x: float(inv) ** x, -3, 3, -1, 5), "function": {"type": "exp", "base": fraction_plain(inv)}},
            ],
            "points": [{"x": 0, "y": 1, "label": "(0, 1)"}],
            "lines": [],
        }
        visual_type = "DETERMINISTIC_VISUAL"
    elif pool == "exp":
        base = rng.choice([F(2), F(3), F(1, 2), F(1, 3), F(3, 2), F(2, 3), F(5)])
        fname = spec.get("fname", "y")
        rows = _exp_statements(base, tex_base(base), fname=fname)
        question = head
        if fname == "f":
            question = f"若 {m(f'f(x)={tex_base(base)}^{{x}}')}，則下列何者正確？" if mode == "correct" else f"若 {m(f'f(x)={tex_base(base)}^{{x}}')}，則下列何者不正確？"
    elif pool == "log":
        base = rng.choice([F(2), F(3), F(1, 2), F(1, 3), F(5), F(1, 5)])
        rows = _log_statements(base)
        question = head
    else:
        bases = [rng.choice([F(2), F(3)]), rng.choice([F(1, 2), F(1, 3)])]
        rows = []
        for b in bases:
            rows += _exp_statements(b, tex_base(b))
            rows += _log_statements(b)
        question = head
    want = mode == "correct"
    good = [r for r in rows if r[1] is want]
    bad = [r for r in rows if r[1] is not want]
    pick = rng.choice(good)
    rng.shuffle(bad)
    correct = statement_choice(pick[0])
    choices, label = make_choices(rng, correct, [statement_choice(t) for t, _ in bad])
    return pack(
        spec["op"], question=question, answer=correct[0], presentation="single_choice",
        choices=choices, correct_label=label, visual=visual, visual_type=visual_type,
        params={"pool": pool, "mode": mode},
        explanation="指數函數圖形恆過 (0,1)、在 x 軸上方；對數函數圖形恆過 (1,0)、在 y 軸右方；底數大於 1 遞增、介於 0 與 1 之間遞減。",
    )


_IDENTIFY_BASES = [
    (math.pi / 4, r"\dfrac{\pi}{4}", "pi/4"),
    (2 / 3, r"\dfrac{2}{3}", "2/3"),
    (3 / 4, r"\dfrac{3}{4}", "3/4"),
    (0.8, "0.8", "0.8"),
    (1.5, r"\dfrac{3}{2}", "3/2"),
    (math.pi / 3, r"\dfrac{\pi}{3}", "pi/3"),
    (1.25, r"\dfrac{5}{4}", "5/4"),
]


def build_exp_graph_identify_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    r, r_tex, r_plain = rng.choice(_IDENTIFY_BASES)
    shapes = [
        ("target", lambda x: r**x),
        ("mirror", lambda x: (1 / r) ** x),
        ("neg", lambda x: -(r**x)),
        ("negmirror", lambda x: -((1 / r) ** x)),
    ]
    marks = ["①", "②", "③", "④"]
    rng.shuffle(shapes)
    curves = []
    target_mark = ""
    for mark, (kind, fn) in zip(marks, shapes):
        pts = curve_polyline(fn, -3.4, 3.4, -4.4, 4.4)
        anchor_x = 2.2 if (kind in {"target", "neg"}) == (r > 1) else -2.2
        curves.append({
            "label": mark,
            "points": pts,
            "label_at": [anchor_x, round(fn(anchor_x), 3)],
            "function": {"type": "exp", "base_value": round(r if kind in {"target", "neg"} else 1 / r, 6), "sign": -1 if kind.startswith("neg") else 1},
        })
        if kind == "target":
            target_mark = mark
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": True,
        "scale_mode": "cartesian_equal_units",
        "x_range": [-3.5, 3.5],
        "y_range": [-4.5, 4.5],
        "curves": curves,
        "points": [{"x": 0, "y": 1, "label": "1"}, {"x": 0, "y": -1, "label": "-1"}],
        "lines": [],
    }
    choices, label = make_choices(rng, (target_mark, f"曲線{target_mark}"), [(mk, f"曲線{mk}") for mk in marks if mk != target_mark])
    fx = "f(x)=" + r"\left(" + r_tex + r"\right)^{x}"
    question = f"若 {m(fx)}，則附圖中哪一條曲線為 {m('y=f(x)')} 的圖形？"
    return pack(
        spec["op"], question=question, answer=target_mark, presentation="single_choice",
        choices=choices, correct_label=label, visual=visual, visual_type="DETERMINISTIC_VISUAL",
        params={"base": r_plain, "increasing": r > 1},
        explanation="指數函數 \\(y=a^{x}\\) 的圖形通過 \\((0,1)\\) 且在 \\(x\\) 軸上方；\\(a>1\\) 遞增，\\(0<a<1\\) 遞減。",
    )


def _eq_linear_exp(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(300):
        b = rng.choice([2, 3, 5])
        k = rng.randint(-5, 5)
        p, q = rng.choice([1, 1, 2, 3]), rng.randint(-3, 3)
        x = F(k - q, p)
        if k != 0 and (b ** abs(k)) <= 1000 and x != 0 and x.denominator <= 3:
            break
    return f"{b}^{{{tex_lin(p, q)}}}={_positive_int_or_reciprocal(b, k)}", x


def _eq_power_base(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(300):
        b = rng.choice([2, 3, 5])
        p, q = rng.choice([1, 2]), rng.choice([-2, -1, 1, 2])
        s = rng.choice([0, 0, 1, -1])
        x = F(2 * q - s, 1 - 2 * p)
        if x != 0:
            break
    return f"{b}^{{{tex_lin(1, s)}}}={b * b}^{{{tex_lin(p, q)}}}", x


def build_exp_equation_same_base(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {"linear_exp": _eq_linear_exp, "power_base": _eq_power_base}
    rows = [makers[k](rng) for k in spec["kinds"]]
    return pack(
        spec["op"], prompt="解下列指數方程式：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([x for _, x in rows]), params={"roots": [fraction_plain(x) for _, x in rows]},
        explanation="把兩邊化成同底數，再令指數相等解一次方程式。",
    )


def build_exp_equation_convert_base(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "reciprocal")
    presentation = spec.get("presentation", "short_answer")
    for _ in range(400):
        if variant == "inverse_square":
            b = rng.choice([2, 3, 5])
            c1, a, c2 = rng.randint(-3, 3), rng.choice([1, 2]), rng.randint(-4, 4)
            x = F(-(2 * c2 + c1), 1 + 2 * a)
            tex = rf"\left(\dfrac{{1}}{{{b}}}\right)^{{{tex_lin(1, c1)}}}={b * b}^{{{tex_lin(a, c2)}}}"
        elif variant == "square_reciprocal":
            u, v = rng.choice([(13, 17), (2, 3), (3, 5), (5, 7), (7, 11), (4, 9)])
            a1, b1 = rng.choice([2, 3, 4]), rng.randint(-3, 3)
            c, d = rng.randint(-3, 3), rng.choice([-1, 1])
            den = a1 + 2 * d
            if den == 0:
                continue
            x = F(-(b1 + 2 * c), den)
            tex = rf"\left(\dfrac{{{u}}}{{{v}}}\right)^{{{tex_lin(a1, b1)}}}=\left(\dfrac{{{v * v}}}{{{u * u}}}\right)^{{{tex_lin(d, c)}}}"
        else:
            u, v = rng.choice([(3, 4), (2, 5), (4, 7), (2, 3), (5, 6)])
            a1, a2 = rng.randint(1, 4), rng.randint(1, 4)
            x = F(rng.randint(-3, 4), rng.choice([1, 1, a1 + a2]))
            b1 = rng.randint(-4, 4)
            b2 = -(a1 + a2) * x - b1
            if b2.denominator != 1 or abs(b2) > 9:
                continue
            tex = rf"\left(\dfrac{{{u}}}{{{v}}}\right)^{{{tex_lin(a1, b1)}}}=\left(\dfrac{{{v}}}{{{u}}}\right)^{{{tex_lin(a2, b2)}}}"
        if x != 0 and x.denominator <= 7:
            break
    question = f"解指數方程式 {m(tex)}。"
    choices = label = None
    if presentation == "single_choice":
        question = f"已知 {m(tex)}，則 {m('x')} 之值為"
        choices, label = make_choices(rng, num_choice(x), [num_choice(v) for v in (-x, x + 1, x - 1, 1 / x if x else F(2), 2 * x)], same=same_number)
    return pack(
        spec["op"], question=question, answer=fraction_plain(x), presentation=presentation,
        choices=choices, correct_label=label, params={"root": fraction_plain(x), "variant": variant},
        explanation="倒數底數可寫成負一次方，化成同底數後令指數相等。",
    )


def build_exp_equation_quadratic_sub(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "basic")
    presentation = spec.get("presentation", "short_answer")
    part_labels = None
    for _ in range(400):
        b = rng.choice([2, 3])
        if variant == "two_roots":
            k1, k2 = sorted(rng.sample([1, 2, 3], 2))
            t1, t2 = b**k1, b**k2
            c, const = (t1 + t2) // b, t1 * t2
            if (t1 + t2) % b or const > 800:
                continue
            tex = f"{b}^{{2x}}-" + _coef(c) + f"{b}^{{x+1}}+{const}=0"
            answer: Any = {"(1)": str(k1), "(2)": str(k2)}
            part_labels = {"(1)": "較小的解", "(2)": "較大的解"}
            break
        if variant == "divide":
            k, s = rng.choice([3, 4, 5]), rng.choice([2, 3, 4])
            num = b ** (2 * k) + b ** (k + 1)
            if num % (b**s):
                continue
            c = num // (b**s)
            if c > 99:
                continue
            tex = rf"{b}^{{2x+1}}+{b}^{{3x}}={c}\times {b}^{{x+{s}}}"
            answer = str(k)
            break
        k = rng.choice([1, 2, 3])
        t1 = b**k
        neg = rng.choice([1, 2, 3, 4])
        ssum, prod = t1 - neg, -t1 * neg
        if variant == "shifted":
            if ssum == 0 or ssum % b:
                continue
            c = -ssum // b
            mid = ("+" if c > 0 else "-") + _coef(abs(c)) + f"{b}^{{x+1}}"
            tex = f"{b}^{{2x}}{mid}-{-prod}=0"
        elif variant == "square_base":
            if ssum == 0:
                continue
            mid = ("+" if ssum < 0 else "-") + _coef(abs(ssum)) + f"{b}^{{x}}"
            tex = f"{b * b}^{{x}}{mid}-{-prod}=0"
        else:
            if ssum == 0:
                continue
            mid = ("+" if ssum < 0 else "-") + _coef(abs(ssum)) + f"{b}^{{x}}"
            tex = f"{b}^{{2x}}{mid}-{-prod}=0"
        answer = str(k)
        break
    question = f"試解方程式 {m(tex)}。"
    if variant == "two_roots":
        question = f"試解方程式 {m(tex)}（由小到大寫出所有解）。"
    choices = label = None
    if presentation == "single_choice":
        question = f"設方程式 {m(tex)}，則 {m('x=')}"
        k = int(answer)
        choices, label = make_choices(rng, num_choice(k), [num_choice(v) for v in (b**k, b ** (2 * k), 0, k + 1, -neg)], same=same_number)
    return pack(
        spec["op"], question=question, answer=answer, presentation=presentation,
        choices=choices, correct_label=label, part_labels=part_labels,
        params={"variant": variant, "base": b}, explanation="令 \\(t=a^{x}>0\\)，化成 \\(t\\) 的二次方程式，捨去不為正的根，再由 \\(a^{x}=t\\) 求 \\(x\\)。",
    )


def build_exp_equation_factor_common(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(300):
        b, mm, c, k = rng.choice([2, 3, 5]), rng.choice([1, 2]), rng.choice([1, 2, 3]), rng.choice([1, 2, 3])
        n = b**k * (b**mm + c)
        if n <= 1000:
            break
    mid = f"{b}^{{x}}" if c == 1 else f"{c}\\times {b}^{{x}}"
    return pack(
        spec["op"], question=f"解指數方程式 {m(f'{b}^{{x+{mm}}}+{mid}={n}')}。", answer=str(k),
        params={"base": b, "k": k}, explanation=f"提出公因式 \\({b}^{{x}}\\)：\\({b}^{{x}}({b ** mm}+{c})={n}\\)。",
    )


def build_exp_power_substitution_value(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    b, v, k = rng.choice([2, 3, 5]), rng.choice([2, 3, 4, 5]), rng.choice([2, 3])
    if v == b:
        v += 1
    value = F(v**k)
    choices, label = make_choices(rng, num_choice(value), [num_choice(x) for x in (v * k, v ** (k - 1), v ** (k + 1), b**k, v * v * k)], same=same_number)
    return pack(
        spec["op"], question=f"已知 {m(f'{b}^{{x}}={v}')}，則 {m(f'{b ** k}^{{x}}')} 之值為何？", answer=fraction_plain(value),
        presentation="single_choice", choices=choices, correct_label=label, params={"b": b, "v": v, "k": k},
        explanation=f"\\({b ** k}^{{x}}=\\left({b}^{{x}}\\right)^{{{k}}}={v}^{{{k}}}\\)。",
    )
