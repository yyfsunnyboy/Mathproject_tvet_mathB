# -*- coding: utf-8 -*-
"""B3 Chapter 4 logarithm families (sections 4-3, 4-4 and 4-5).

Builders sample slots, fix a clean answer first, then render the stem.
Logarithm bases stay explicit (``\\log_{b}``) except in the common-log
section, where ``\\log x`` means base 10 and the matrix marks
``log_notation = common``. Approximate answers use only the approximations
printed in the stem.
"""

from __future__ import annotations

import itertools
import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import Any

import sympy as sp

from core.domain.exponential_logarithmic_exp_builders import order_choice
from core.domain.exponential_logarithmic_math import (
    GIVEN_LOG10,
    approx_log10,
    as_fraction,
    decimal_plain,
    factor_int,
    floor_decimal,
    fraction_as_terminating_decimal,
    fraction_plain,
    log_exact,
    rational_power,
    robust_floor,
    table_log,
    true_log10,
)
from core.domain.exponential_logarithmic_render import (
    m,
    make_choices,
    num_choice,
    pack,
    same_expression,
    same_number,
    tex_exp,
    tex_log,
    tex_num,
    tex_prime_power,
)

F = Fraction
TIMES = r"\times "
LOG = r"\log "
APPROX = r"\approx "
NE = r"\ne "
ALPHA = r"\alpha"


def _items(texts: list[str]) -> list[dict[str, str]]:
    return [{"group_label": f"({i})", "text": text} for i, text in enumerate(texts, 1)]


def _parts(values: list[object]) -> dict[str, str]:
    return {f"({i})": (v if isinstance(v, str) else fraction_plain(v)) for i, v in enumerate(values, 1)}


def _lg(base: object, arg: str) -> str:
    """Explicit-base log TeX; ``base`` may be a TeX string or a number."""
    base_tex = base if isinstance(base, str) else tex_num(base, small=True)
    return tex_log(base_tex, arg)


def _paren_arg(tex: str) -> str:
    return r"\left(" + tex + r"\right)"


def _lin(p: int, q: int, var: str = "x") -> str:
    head = var if p == 1 else f"{p}{var}"
    if q == 0:
        return head
    return f"{head}+{q}" if q > 0 else f"{head}-{-q}"


def _coef_term(c: int, body: str, first: bool) -> str:
    sign = "-" if c < 0 else ("" if first else "+")
    mag = abs(c)
    return sign + ("" if mag == 1 else str(mag)) + body


def _given_tex(pairs: list[tuple[str, Decimal]], *, common: bool) -> str:
    rows = []
    for arg, value in pairs:
        head = (r"\log " + arg) if common else (r"\log_{10} " + arg)
        rows.append(m(head + r"\approx " + format(value, "f")))
    return "、".join(rows)


def _given_dict(pairs: list[tuple[str, Decimal]]) -> dict[str, str]:
    return {f"log {arg}": format(value, "f") for arg, value in pairs}


def _prime_givens(value: object) -> list[tuple[str, Decimal]]:
    """Given approximations needed for log10(value) over primes 2, 3, 7.

    Prime 5 is covered by ``log 5 = 1 - log 2`` so it contributes log 2.
    """
    v = as_fraction(value)
    primes = set(factor_int(v.numerator)) | set(factor_int(v.denominator))
    need = set()
    for p in primes:
        if p == 5:
            need.add(2)
        elif p in (2, 3, 7):
            need.add(p)
        else:
            raise ValueError(f"no_given_log_for_prime:{p}")
    return [(str(p), GIVEN_LOG10[p]) for p in sorted(need)]


# ============================================================ 4-3 builders

_DEF_BASES = [2, 3, 4, 5, 6, 7]


def build_log_definition_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    rows = []
    b1 = rng.choice(_DEF_BASES)
    k1 = rng.choice([k for k in (2, 3, 4, 5) if b1**k <= 1024])
    rows.append((_lg(b1, str(b1**k1)), F(k1)))
    b2 = rng.choice([b for b in _DEF_BASES if b != b1])
    k2 = rng.choice([k for k in (1, 2, 3) if b2**k <= 343])
    rows.append((_lg(b2, rf"\dfrac{{1}}{{{b2 ** k2}}}"), F(-k2)))
    return pack(
        spec["op"], prompt="試求下列對數之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [fraction_plain(v) for _, v in rows]},
        explanation="由定義 \\(a^{y}=x\\Leftrightarrow y=\\log_{a} x\\)，把真數寫成底數的次方。",
    )


def _domain_item(rng: random.Random, kind: str) -> tuple[str, str, bool]:
    b = rng.choice([2, 3, 5, 7, 10])
    if kind == "neg_base":
        k = rng.randint(2, 5)
        return _lg(_paren_arg(f"-{k}"), str(rng.choice([k, k * k, 3, 8]))), f"log_(-{k})", False
    if kind == "base_one":
        a = rng.randint(2, 9)
        return _lg("1", str(a)), f"log_1({a})", False
    if kind == "base_zero":
        a = rng.randint(2, 9)
        return _lg("0", str(a)), f"log_0({a})", False
    if kind == "neg_arg":
        k = rng.randint(1, 9)
        return _lg(b, _paren_arg(f"-{k}")), f"log_{b}(-{k})", False
    if kind == "zero_arg":
        return _lg(b, "0"), f"log_{b}(0)", False
    if kind == "valid_power":
        k = rng.randint(1, 3)
        return _lg(b, str(b**k)), f"log_{b}({b ** k})", True
    if kind == "valid_one":
        return _lg(b, "1"), f"log_{b}(1)", True
    base, shown = rng.choice([(F(1, 10), "0.1"), (F(1, 2), r"\frac{1}{2}"), (F(1, 5), "0.2"), (F(1, 3), r"\frac{1}{3}")])
    a = rng.randint(2, 9)
    return _lg(shown, str(a)), f"log_({fraction_plain(base)})({a})", True


_INVALID_KINDS = ["neg_base", "base_one", "base_zero", "neg_arg", "zero_arg"]
_VALID_KINDS = ["valid_power", "valid_one", "valid_frac"]


def build_log_domain_validity_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    explanation = "對數 \\(\\log_{a} x\\) 有意義的條件：底數 \\(a>0\\) 且 \\(a\\ne 1\\)，真數 \\(x>0\\)。"
    if spec.get("presentation") == "single_choice":
        good = _domain_item(rng, rng.choice(_VALID_KINDS))
        bad = [_domain_item(rng, k) for k in rng.sample(_INVALID_KINDS, 4)]
        choices, label = make_choices(rng, (good[1], m(good[0])), [(v, m(t)) for t, v, _ in bad])
        return pack(
            spec["op"], question="下列何者有意義？", answer=good[1], presentation="single_choice",
            choices=choices, correct_label=label, params={"valid": good[1]}, explanation=explanation,
        )
    kinds = rng.sample(_INVALID_KINDS, 4) + rng.sample(_VALID_KINDS, 2)
    rng.shuffle(kinds)
    rows = [_domain_item(rng, k) for k in kinds]
    answers = ["有意義" if ok else "無意義" for _, _, ok in rows]
    return pack(
        spec["op"], prompt="判斷下列各式是否有意義（填「有意義」或「無意義」）：",
        items=_items([m(t) for t, _, _ in rows]), answer=_parts(answers),
        part_checkers={f"({i})": "text_checker" for i in range(1, len(rows) + 1)},
        params={"kinds": kinds}, explanation=explanation,
    )


def _bp_log_one(rng: random.Random) -> tuple[str, str]:
    return _lg(rng.randint(2, 9), "1"), "0"


def _bp_log_self(rng: random.Random) -> tuple[str, str]:
    if rng.random() < 0.5:
        b = rng.randint(2, 9)
        return _lg(b, str(b)), "1"
    k = rng.choice([2, 3, 5, 6, 7])
    r = rf"\sqrt{{{k}}}"
    return _lg(r, r), "1"


def _bp_log_power(rng: random.Random) -> tuple[str, str]:
    b = rng.randint(2, 9)
    style = rng.choice(["int", "frac", "sqrt"])
    if style == "int":
        e = rng.randint(2, 9)
        return _lg(b, f"{b}^{{{e}}}"), str(e)
    if style == "frac":
        e = F(rng.randint(1, 7), rng.choice([2, 3, 5, 7]))
        if e.denominator == 1:
            e += F(1, 2)
        return _lg(b, f"{b}^{{{tex_exp(e)}}}"), fraction_plain(e)
    k = rng.choice([2, 3, 5, 6, 7])
    return _lg(b, f"{b}^{{\\sqrt{{{k}}}}}"), f"sqrt({k})"


def _bp_exp_log(rng: random.Random) -> tuple[str, str]:
    c = rng.choice([2, 3, 5, 7, 10])
    v = rng.choice([x for x in range(2, 20) if x != c])
    return f"{c}^{{{_lg(c, str(v))}}}", str(v)


def build_log_basic_property_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {"log_one": _bp_log_one, "log_self": _bp_log_self, "log_power": _bp_log_power, "exp_log": _bp_exp_log}
    rows = [makers[k](rng) for k in spec["kinds"]]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [v for _, v in rows]},
        explanation="\\(\\log_{a} 1=0\\)、\\(\\log_{a} a=1\\)、\\(\\log_{a} a^{r}=r\\)、\\(a^{\\log_{a} x}=x\\)。",
    )


def _rv_item(rng: random.Random, kind: str) -> tuple[str, Fraction]:
    for _ in range(300):
        p = rng.choice([2, 3, 5])
        if kind == "int":
            be = F(rng.choice([1, 1, 2]))
            ae = be * rng.choice([-2, -1, 2, 3, 4])
        elif kind == "radical_arg":
            be = F(rng.choice([2, 3]))
            ae = F(rng.choice([1, 3, 5]), 2) * rng.choice([1, -1])
        elif kind == "radical_base":
            be = F(rng.choice([1, 3, 5]), 2)
            ae = F(rng.choice([-2, -1, 1, 2, 3]))
        else:
            be = F(rng.choice([-1, 2, -2, 3]))
            ae = F(rng.choice([1, 3, 5]), 2)
        if be == 0 or ae == 0:
            continue
        if p ** abs(be.numerator) > 243 or p ** abs(ae.numerator) > 243:
            continue
        value = log_exact(p, p, base_exp=be, arg_exp=ae)
        if value.denominator <= 6:
            break
    base_tex = tex_prime_power(p, be, small=True)
    arg_tex = tex_prime_power(p, ae)
    return _lg(base_tex, arg_tex), value


def build_log_rational_value_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    explanation = "底數與真數都化成同一質數的次方：\\(\\log_{a^{m}} a^{n}=\\dfrac{n}{m}\\)。"
    if spec.get("presentation") == "single_choice":
        (t1, v1), (t2, v2) = _rv_item(rng, "mixed"), _rv_item(rng, "radical_arg")
        value = v1 - v2
        pool = [v1 + v2, -value, v2 - v1 + 1, value + F(1, 2), 2 * value, v1 * v2]
        choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=f"{m(t1 + '-' + t2 + '=')}", answer=fraction_plain(value),
            presentation="single_choice", choices=choices, correct_label=label,
            params={"value": fraction_plain(value)}, explanation=explanation,
        )
    rows = [_rv_item(rng, k) for k in spec["kinds"]]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [fraction_plain(v) for _, v in rows]},
        explanation=explanation,
    )


def _is_power_of(n: int, b: int) -> bool:
    try:
        return log_exact(b, n).denominator == 1
    except ValueError:
        return False


def build_log_product_quotient_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(300):
        b = rng.choice([2, 3, 4, 5, 6, 9, 10, 12])
        k = rng.choice([kk for kk in (1, 2, 3) if b**kk <= 1000])
        target = b**k
        divisors = [
            d for d in range(2, target)
            if target % d == 0 and d * d != target and not _is_power_of(d, b)
        ]
        if divisors:
            break
    m1 = rng.choice(divisors)
    n1 = target // m1
    for _ in range(300):
        b2 = rng.choice([2, 3, 5, 6, 10])
        k2 = rng.choice([1, 2, 3])
        n2 = rng.randint(2, 9)
        if not _is_power_of(n2, b2) and n2 * b2**k2 <= 1000:
            break
    m2 = n2 * b2**k2
    rows = [(_lg(b, str(m1)) + "+" + _lg(b, str(n1)), F(k)), (_lg(b2, str(m2)) + "-" + _lg(b2, str(n2)), F(k2))]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [k, k2]},
        explanation="\\(\\log_{a} M+\\log_{a} N=\\log_{a} MN\\)，\\(\\log_{a} M-\\log_{a} N=\\log_{a} \\dfrac{M}{N}\\)。",
    )


_LC_ARGS = [2, 3, 4, 5, 6, 8, 9, 12, 15, 16, 18, 20, 24, 25, 27, 30, 36, 40, 45, 50, 54, 60]


def _lc_combo(rng: random.Random, terms: int) -> tuple[str, Fraction, int]:
    for _ in range(2000):
        b = rng.choice([10, 10, 3, 2, 5, 6])
        v = rng.choice([0, 1, 2, 3])
        coefs = [rng.choice([1, 1, 2, 3])] + [rng.choice([1, 2, 3, -1, -1, -2]) for _ in range(terms - 2)]
        args = rng.sample(_LC_ARGS, terms - 1)
        residual = F(b) ** v
        for c, a in zip(coefs, args):
            residual /= F(a) ** c
        last_c = rng.choice([1, -1, 2, -2])
        try:
            last = rational_power(residual, F(1, last_c))
        except ValueError:
            continue
        if last.denominator != 1 or not 2 <= last <= 200 or int(last) in args:
            continue
        coefs.append(last_c)
        args.append(int(last))
        if all(c > 0 for c in coefs) or all(_is_power_of(a, b) for a in args):
            continue
        tex = "".join(_coef_term(c, _lg(b, str(a)), i == 0) for i, (c, a) in enumerate(zip(coefs, args)))
        return tex, F(v), b
    raise ValueError("log_combo_search_failed")


def _lc_surd(rng: random.Random) -> tuple[str, Fraction, int]:
    for _ in range(2000):
        b = rng.choice([2, 3, 5, 7])
        v = rng.choice([0, 0, 1])
        d = rng.choice([2, 3, 5, 6, 7])
        n = rng.randint(1, 4)
        mm2 = b**v + n * n * d
        mm = math.isqrt(mm2)
        if mm * mm == mm2 and mm > 1:
            inner = ("" if n == 1 else str(n)) + rf"\sqrt{{{d}}}"
            tex = _lg(b, _paren_arg(f"{mm}+{inner}")) + "+" + _lg(b, _paren_arg(f"{mm}-{inner}"))
            return tex, F(v), b
    raise ValueError("log_surd_search_failed")


def _lc_half(rng: random.Random) -> tuple[str, Fraction, int]:
    for _ in range(2000):
        a1 = rng.choice([2, 3, 4, 5, 6, 8])
        a2 = rng.choice([x for x in range(2, 40) if math.isqrt(x) ** 2 != x])
        a3 = F(a1 * a1 * a2, 100)
        dec = fraction_as_terminating_decimal(a3)
        if dec is None or a3 == 1 or len(dec.split(".")[-1]) > 2 or a3 > 20:
            continue
        tex = _lg(10, str(a1)) + "+" + _lg(10, rf"\sqrt{{{a2}}}") + r"-\dfrac{1}{2}" + _lg(10, dec)
        return tex, F(1), 10
    raise ValueError("log_half_search_failed")


def build_log_linear_combination_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    makers = {"combo3": lambda r: _lc_combo(r, 3), "combo4": lambda r: _lc_combo(r, 4), "surd": _lc_surd, "half": _lc_half}
    explanation = "係數先移到真數成為次方，再用對數的加減合併成單一對數。"
    if spec.get("presentation") == "single_choice":
        tex, value, _b = _lc_combo(rng, 4)
        pool = [value + 1, value - 1, value + 2, 2 * value + 1, value + 3, F(0) if value else F(4)]
        choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=m(tex + "="), answer=fraction_plain(value), presentation="single_choice",
            choices=choices, correct_label=label, params={"value": fraction_plain(value)}, explanation=explanation,
        )
    rows = [makers[k](rng) for k in spec["kinds"]]
    if len(rows) == 1:
        return pack(
            spec["op"], question=f"試求 {m(rows[0][0])} 之值。", answer=fraction_plain(rows[0][1]),
            params={"value": fraction_plain(rows[0][1])}, explanation=explanation,
        )
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _, _ in rows]),
        answer=_parts([v for _, v, _ in rows]), params={"values": [fraction_plain(v) for _, v, _ in rows]},
        explanation=explanation,
    )


_CHAIN_POOL = [3, 5, 6, 7, 10, 11, 12, 13, 15, 20]


def _cb_reciprocal(rng: random.Random) -> tuple[str, Fraction]:
    a, b = rng.sample([2, 3, 5, 7], 2)
    i, j = (1, 1) if rng.random() < 0.5 else (rng.choice([1, 2]), rng.choice([2, 3]))
    if b**i > 125 or a**j > 125:
        i, j = 1, 1
    return _lg(a, str(b**i)) + TIMES + _lg(b, str(a**j)), F(i * j)


def _cb_chain(rng: random.Random) -> tuple[str, Fraction]:
    for _ in range(200):
        s = rng.choice([2, 3, 5])
        k = rng.choice([kk for kk in (2, 3) if s**kk <= 125])
        end = s**k
        mids = rng.sample([x for x in _CHAIN_POOL if x not in (s, end)], rng.choice([1, 2, 3]))
        break
    chain = [s, *mids, end]
    tex = TIMES.join(_lg(chain[i], str(chain[i + 1])) for i in range(len(chain) - 1))
    return tex, F(k)


def _cb_exp_ratio(rng: random.Random) -> tuple[str, Fraction]:
    a, b = rng.sample([2, 3, 5, 7], 2)
    c = rng.choice([x for x in (10, 10, 6, 11) if x not in (a, b)])
    frac = r"\frac{" + _lg(c, str(b)) + "}{" + _lg(c, str(a)) + "}"
    return f"{a}^{{{frac}}}", F(b)


def build_log_change_base_chain_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    explanation = "換底公式：\\(\\log_{a} b\\times \\log_{b} c=\\log_{a} c\\)，\\(\\log_{a} b=\\dfrac{\\log_{c} b}{\\log_{c} a}\\)。"
    if spec.get("presentation") == "single_choice":
        a, p = rng.sample([2, 3, 5], 2)
        i, j = rng.choice([1, 2, 3]), rng.choice([2, 3])
        mids = rng.sample([x for x in (7, 11, 13, 6, 10) if x not in (a, p)], 2)
        tex = TIMES.join([
            _lg(a, str(mids[0])), _lg(mids[0], str(p**i)), _lg(p, str(mids[1])), _lg(mids[1], str(a**j)),
        ])
        value = F(i * j)
        pool = [F(i + j), value + 1, value - 1, value + 2, 2 * value]
        choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool if v > 0], same=same_number)
        return pack(
            spec["op"], question=m(tex + "="), answer=fraction_plain(value), presentation="single_choice",
            choices=choices, correct_label=label, params={"value": fraction_plain(value)}, explanation=explanation,
        )
    makers = {"reciprocal": _cb_reciprocal, "chain": _cb_chain, "exp_ratio": _cb_exp_ratio}
    rows = [makers[k](rng) for k in spec["kinds"]]
    return pack(
        spec["op"], prompt="試求下列各式之值：", items=_items([m(t) for t, _ in rows]),
        answer=_parts([v for _, v in rows]), params={"values": [fraction_plain(v) for _, v in rows]},
        explanation=explanation,
    )


def _cp_terms(rng: random.Random, p: int, q: int, count: int) -> tuple[list[tuple[int, int, int]], Fraction]:
    """Terms (sign, i, j) meaning sign*log_{p^i} q^j = sign*(j/i)*log_p q."""
    for _ in range(300):
        rows = []
        for idx in range(count):
            i = rng.choice([k for k in (1, 2, 3, 4) if p**k <= 81])
            j = rng.choice([k for k in (1, 2, 3, 4) if q**k <= 81])
            sign = 1 if idx == 0 else rng.choice([1, 1, -1])
            rows.append((sign, i, j))
        total = sum(F(s * j, i) for s, i, j in rows)
        if total != 0 and len({(i, j) for _, i, j in rows}) == count:
            return rows, total
    raise ValueError("change_base_terms_failed")


def _cp_tex(rows: list[tuple[int, int, int]], p: int, q: int) -> str:
    out = ""
    for idx, (s, i, j) in enumerate(rows):
        out += ("-" if s < 0 else ("" if idx == 0 else "+")) + _lg(p**i, str(q**j))
    return out


def build_log_change_base_product_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    explanation = "\\(\\log_{a^{m}} b^{n}=\\dfrac{n}{m}\\log_{a} b\\)，且 \\(\\log_{a} b\\times \\log_{b} a=1\\)。"
    for _ in range(300):
        p, q = rng.sample([2, 3, 5], 2)
        if spec.get("presentation") == "single_choice":
            top, s1 = _cp_terms(rng, p, q, 2)
            bottom, s2 = _cp_terms(rng, p, q, 2)
            value = s1 / s2
            if value in (1, -1) or value.denominator > 9 or s2 < 0:
                continue
            tex = r"\dfrac{" + _cp_tex(top, p, q) + "}{" + _cp_tex(bottom, p, q) + "}"
            pool = [1 / value, value + 1, s1 * s2, value * 2, -value]
            choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool], same=same_number)
            return pack(
                spec["op"], question=m(tex + "="), answer=fraction_plain(value), presentation="single_choice",
                choices=choices, correct_label=label, params={"value": fraction_plain(value)}, explanation=explanation,
            )
        first, s1 = _cp_terms(rng, p, q, 2)
        second, s2 = _cp_terms(rng, q, p, 2)
        value = s1 * s2
        if value.denominator <= 4 and abs(value) <= 12:
            break
    tex = _paren_arg(_cp_tex(first, p, q)) + _paren_arg(_cp_tex(second, q, p))
    return pack(
        spec["op"], question=f"試求 {m(tex)} 之值。", answer=fraction_plain(value),
        params={"value": fraction_plain(value)}, explanation=explanation,
    )


_AB = sp.symbols("a b")
_SETTINGS = {
    # setting: (log base shown, a definition, b definition, prime logs as sympy)
    "base3": ("3", (3, 2), (3, 5)),
    "base10": ("10", (10, 2), (10, 3)),
    "mixed": ("10", (10, 2), (2, 3)),
}


def _prime_log_expr(setting: str, p: int):
    a, b = _AB
    one = sp.Integer(1)
    if setting == "base3":
        return {2: a, 3: one, 5: b}[p]
    if setting == "base10":
        return {2: a, 3: b, 5: one - a}[p]
    return {2: a, 3: a * b, 5: one - a}[p]


def _log_expr(setting: str, n: object):
    v = as_fraction(n)
    total = sp.Integer(0)
    for p, k in factor_int(v.numerator).items():
        total += k * _prime_log_expr(setting, p)
    for p, k in factor_int(v.denominator).items():
        total -= k * _prime_log_expr(setting, p)
    return sp.expand(total)


def _expr_plain(expr) -> str:
    return str(sp.together(sp.expand(expr))).replace("**", "^").replace(" ", "")


def _expr_tex(expr) -> str:
    return sp.latex(sp.together(sp.expand(expr)))


_AB_NUMBERS = [4, 6, 8, 12, 15, 18, 20, 24, 30, 36, 40, 45, 48, 50, 60, 72, 75, 90, 100, 120, 150, 180]
_AB_BASES = [2, 3, 4, 5, 6, 9, 12, 15, 20, 40]


def build_log_express_in_ab(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    setting = spec.get("setting", "base10")
    base_tex, (ab, aa), (bb, ba) = _SETTINGS[setting]
    a, b = _AB
    cond = m(r"\log_{" + str(ab) + "} " + str(aa) + "=a") + "，" + m(r"\log_{" + str(bb) + "} " + str(ba) + "=b")
    if spec.get("presentation") == "single_choice":
        for _ in range(300):
            n = rng.choice(_AB_NUMBERS[:12])
            expr = _log_expr(setting, n)
            if len(sp.Add.make_args(expr)) >= 2:
                break
        ca, cb = expr.coeff(a), expr.coeff(b)
        c1 = expr.subs({a: 0, b: 0})
        pool = [
            ca * a + cb * b + c1 + 1, -ca * a + cb * b + c1, ca * a - cb * b + c1,
            ca * a + cb * b - c1, (ca + 1) * a + cb * b + c1, ca * a + (cb + 1) * b + c1, ca * b + cb * a + c1,
        ]
        correct = (_expr_plain(expr), m(_expr_tex(expr)))
        choices, label = make_choices(
            rng, correct, [(_expr_plain(e), m(_expr_tex(e))) for e in pool], same=same_expression,
        )
        return pack(
            spec["op"], question=f"若 {cond}，則 {m(_lg(base_tex, str(n)))} 等於下列何者？", answer=correct[0],
            presentation="single_choice", choices=choices, correct_label=label, params={"n": n, "setting": setting},
            explanation="把真數做質因數分解，用 \\(\\log 5=1-\\log 2\\) 等關係以 \\(a\\)、\\(b\\) 表示。",
        )
    texts, answers = [], []
    for kind in spec["parts"]:
        for _ in range(300):
            if kind == "log":
                n = rng.choice(_AB_NUMBERS)
                expr = _log_expr(setting, n)
                tex = _lg(base_tex, str(n))
            else:
                n = rng.choice(_AB_NUMBERS)
                mm = rng.choice([x for x in _AB_BASES if x != n and x != int(base_tex)])
                den = _log_expr(setting, mm)
                if den == 0:
                    continue
                expr = sp.cancel(_log_expr(setting, n) / den)
                tex = _lg(mm, str(n))
            plain = _expr_plain(expr)
            if len(sp.Add.make_args(sp.expand(expr))) >= 2 or (kind == "ratio" and sp.denom(sp.together(expr)) != 1):
                if plain not in answers and not expr.is_number:
                    break
        texts.append(m(tex))
        answers.append(plain)
    return pack(
        spec["op"], prompt=f"設 {cond}，試以 {m('a')}、{m('b')} 表示：", items=_items(texts),
        answer=_parts(answers), params={"setting": setting, "answers": answers},
        explanation="先換成同一底數的對數，再把真數做質因數分解後以 \\(a\\)、\\(b\\) 表示。",
    )


def _application_fact_pool(coef: int) -> list[tuple[int, int]]:
    rows = []
    for x in (2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 80, 100):
        approx = coef * approx_log10(x)
        exact = coef * true_log10(x)
        if approx == approx.to_integral_value() and abs(exact - approx) < Decimal("1e-20"):
            rows.append((x, int(approx)))
            continue
        if robust_floor(approx, exact, margin=Decimal("0.03")):
            rows.append((x, floor_decimal(approx)))
    return rows


def build_log_application_statement_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    coef = 50
    facts = _application_fact_pool(coef)
    fact_map = dict(facts)
    minimum = rng.choice([x for x in (2, 4, 5, 8) if x in fact_map])
    mode = spec.get("mode") or rng.choice(["wrong", "right"])
    statements: list[tuple[str, bool]] = []
    for x, s in facts:
        if x < minimum:
            continue
        if x == 100:
            statements.append(("考 100 分的同學調整前後的分數不變", True))
            continue
        statements.append((f"原始成績 {x} 分的同學，調整後的成績為 {s} 分", True))
        statements.append((f"原始成績 {x} 分的同學，調整後的成績為 {s + 1} 分", False))
        cap = (s // 10 + 1) * 10
        statements.append((f"原始成績 {x} 分的同學，調整後的分數不到 {cap} 分", True))
        statements.append((f"原始成績 {x} 分的同學，調整後的分數達到 {cap} 分以上", False))
    low = fact_map[minimum]
    statements.append((f"調整後全班的最低分是 {low} 分", True))
    statements.append((f"調整後全班的最低分是 {low + 1} 分", False))
    want = mode == "right"
    good = [row for row in statements if row[1] is want]
    bad = [row for row in statements if row[1] is not want]
    pick = rng.choice(good)
    rng.shuffle(bad)
    choices, label = make_choices(rng, (pick[0], pick[0]), [(t, t) for t, _ in bad])
    head = "下列敘述何者正確？" if want else "下列敘述何者錯誤？"
    question = (
        f"某次考試滿分為 100 分，老師進行全班成績調整：若原始成績為 {m('x')} 分，則調整後成績為 "
        f"{m(str(coef) + TIMES + _lg(10, 'x'))} 的整數部分。已知這次考試沒有人缺考且最低分數為 {minimum} 分，"
        f"{head}（{_given_tex([('2', GIVEN_LOG10[2])], common=False)}）"
    )
    return pack(
        spec["op"], question=question, answer=pick[0], presentation="single_choice", choices=choices,
        correct_label=label, params={"coef": coef, "minimum": minimum, "mode": mode},
        given_approximations=_given_dict([("2", GIVEN_LOG10[2])]),
        explanation="把各原始成績寫成 2 與 10 的乘除，代入 \\(\\log_{10} 2\\approx 0.3010\\) 計算後取整數部分。",
    )


def build_log_reciprocal_sum_param(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(200):
        p, q = rng.sample([2, 3, 5, 7, 11], 2)
        c = rng.choice([x for x in (2, 3, 5, 6, 10) if x not in (p, q)])
        variant = rng.choice(["sum", "sum", "diff", "weighted"])
        if variant == "sum":
            expr, value = r"\dfrac{1}{x}+\dfrac{1}{y}", F(p * q)
        elif variant == "diff":
            expr, value = r"\dfrac{1}{x}-\dfrac{1}{y}", F(p, q)
        else:
            expr, value = r"\dfrac{2}{x}+\dfrac{1}{y}", F(p * p * q)
        if value.numerator <= 300:
            break
    question = (
        f"設 {m(f'{p}^{{x}}={q}^{{y}}={c}')}，則 {m(expr + '=' + _lg(c, 'A'))}，"
        f"已知 {m('A>0')}，試求 {m('A')} 之值。"
    )
    return pack(
        spec["op"], question=question, answer=fraction_plain(value), params={"p": p, "q": q, "c": c, "variant": variant},
        explanation="由 \\(a^{x}=c\\) 得 \\(x=\\log_{a} c\\)，\\(\\dfrac{1}{x}=\\log_{c} a\\)，再合併對數。",
    )


def build_log_definition_inverse_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(300):
        s = rng.choice([2, 3, 5])
        power = rng.choice([2, 3])
        r = rng.choice([F(1, power), F(2, power), F(3, 2)])
        base = s**power
        try:
            a_val = rational_power(base, r)
        except ValueError:
            continue
        if a_val.denominator != 1 or a_val > 250:
            continue
        a_int = int(a_val)
        c = rng.choice([2, 3, 5])
        op = rng.choice(["div", "mul"])
        d = rng.choice([2, 3, 4, 5, 6, 8, 9])
        target = F(a_int, d) if op == "div" else F(a_int * d)
        try:
            value = log_exact(c, target)
        except ValueError:
            continue
        if value.denominator == 1 and abs(value) <= 6:
            break
    arg = (r"\dfrac{a}{" + str(d) + "}") if op == "div" else f"{d}a"
    question = f"若 {m(_lg(base, 'a') + '=' + tex_num(r))}，則 {m(_lg(c, _paren_arg(arg)) + '=')}"
    pool = [value + 1, value - 1, value + 2, -value, F(a_int)]
    choices, label = make_choices(rng, num_choice(value), [num_choice(v) for v in pool], same=same_number)
    return pack(
        spec["op"], question=question, answer=fraction_plain(value), presentation="single_choice",
        choices=choices, correct_label=label, params={"a": a_int, "value": fraction_plain(value)},
        explanation="由定義 \\(\\log_{b} a=r\\Leftrightarrow a=b^{r}\\) 先求 \\(a\\)，再計算所求對數。",
    )


# ============================================================ 4-4 builders

COMPARE_PROMPT = "試比較下列各數之大小（由小到大，以 " + m(r"a\lt b\lt c") + " 的形式作答）："


def _order(values: list[float], names: list[str]) -> str:
    idx = sorted(range(len(values)), key=lambda i: values[i])
    return "<".join(names[i] for i in idx)



_UP_BASES = [(2, "2"), (3, "3"), (5, "5")]
_DOWN_BASES = [(1 / 2, r"\frac{1}{2}"), (1 / 3, r"\frac{1}{3}"), (0.5, "0.5"), (0.3, "0.3"), (0.2, "0.2")]


def _cmp_group(rng: random.Random, kind: str) -> tuple[list[str], list[float]]:
    if kind in ("up", "down"):
        base, bt = rng.choice(_UP_BASES if kind == "up" else _DOWN_BASES)
        start = rng.randint(2, 8)
        args = rng.sample(range(start, start + 6), 3)
        return [_lg(bt, str(x)) for x in args], [math.log(x, base) for x in args]
    if kind == "sqrt_up":
        base, bt = rng.choice(_UP_BASES[:2])
        args = rng.sample([2, 3, 5, 6, 7, 10, 11], 3)
        return [_lg(bt, rf"\sqrt{{{x}}}") for x in args], [math.log(math.sqrt(x), base) for x in args]
    if kind == "pi":
        base, bt = rng.choice(_UP_BASES[:2] + _DOWN_BASES[:2])
        args = [(math.pi, r"\pi"), *rng.sample([(3, "3"), (4, "4"), (2, "2")], 2)]
        return [_lg(bt, t) for _, t in args], [math.log(v, base) for v, _ in args]
    if kind == "down_frac":
        base, bt = rng.choice([(0.3, "0.3"), (0.5, "0.5"), (0.2, "0.2")])
        fr = rng.sample([F(3, 4), F(4, 5), F(5, 6), F(2, 3), F(6, 7)], 3)
        return [_lg(bt, tex_num(f)) for f in fr], [math.log(float(f), base) for f in fr]
    base_int = rng.choice([2, 3])
    bt = rf"\frac{{1}}{{{base_int}}}"
    ks = rng.sample([2, 3, 4, 5], 3)
    return [_lg(bt, rf"\frac{{1}}{{{k}}}") for k in ks], [math.log(1 / k, 1 / base_int) for k in ks]


def _cmp_convert(rng: random.Random) -> tuple[list[str], list[float]]:
    for _ in range(300):
        b = rng.choice([2, 3])
        c1, m1 = rng.choice([2, 3]), rng.choice([x for x in (3, 5, 7, 2) if x != b])
        c2, m2 = rng.choice([2, 3, 4]), rng.choice([x for x in (3, 5, 7, 2) if x != b])
        k = rng.choice([2, 3, 4])
        texts = [f"{c1}" + _lg(b, str(m1)), f"{c2}" + _lg(b * b, str(m2)), str(k)]
        values = [c1 * math.log(m1, b), c2 * math.log(m2, b * b), float(k)]
        gaps = sorted(values)
        if min(gaps[1] - gaps[0], gaps[2] - gaps[1]) > 0.08:
            return texts, values
    raise ValueError("compare_convert_failed")


def build_log_compare_values(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    names = ["a", "b", "c"]
    explanation = "化成同底數後比較真數：底數大於 1 時真數愈大值愈大；底數介於 0 與 1 之間時真數愈大值愈小。"
    if spec.get("presentation") == "single_choice":
        for _ in range(300):
            b = rng.choice([4, 8, 9, 25])
            p = rng.choice([q for q in (2, 3, 5, 7) if b % q])
            i, j = rng.sample([e for e in (2, 3, 4, 5) if p**e <= 700], 2)
            m1, m2 = p**i, p**j
            k = rng.choice([1, 2, 3])
            texts = [str(k), _lg(b, str(m1)), _lg(b, str(m2))]
            values = [float(k), math.log(m1, b), math.log(m2, b)]
            gaps = sorted(values)
            if min(gaps[1] - gaps[0], gaps[2] - gaps[1]) > 0.1:
                break
        correct = _order(values, names)
        perms = ["<".join(p) for p in itertools.permutations(names)]
        rng.shuffle(perms)
        choices, label = make_choices(rng, order_choice(correct), [order_choice(p) for p in perms])
        shown = "、".join(m(f"{n}={t}") for n, t in zip(names, texts))
        return pack(
            spec["op"], question=f"若 {shown}，則下列何者正確？", answer=order_choice(correct)[0], presentation="single_choice",
            choices=choices, correct_label=label, params={"order": correct}, explanation=explanation,
        )
    texts, answers = [], []
    for kind in spec["parts"]:
        for _ in range(100):
            group, values = _cmp_convert(rng) if kind == "convert" else _cmp_group(rng, kind)
            if len({round(v, 9) for v in values}) == 3:
                break
        texts.append("，".join(m(f"{n}={t}") for n, t in zip(names, group)))
        answers.append(_order(values, names))
    return pack(
        spec["op"], prompt=COMPARE_PROMPT, items=_items(texts), answer=_parts(answers),
        part_checkers={f"({i})": "ordered_inequality_checker" for i in range(1, len(texts) + 1)},
        params={"orders": answers}, explanation=explanation,
    )


_SOUNDS = ["甲聲音", "乙聲音", "某設備發出的聲音", "某環境中的聲音", "某喇叭發出的聲音"]


def build_log_decibel_application(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    formula = (
        "已知聲音分貝數公式 " + m(r"d\left(I\right)=10" + TIMES + _lg(10, r"\dfrac{I}{I_{0}}"))
        + "，其中 " + m(r"I_{0}=10^{-12}") + "（W/m²）"
    )
    k1 = rng.randint(2, 9)
    d1 = 10 * (12 - k1)
    sound1 = rng.choice(_SOUNDS)
    forward = f"若{sound1}的強度 {m('I')} 為 {m(f'10^{{-{k1}}}')}（W/m²），則其產生的聲音是多少分貝"
    if spec.get("mode") == "forward":
        return pack(
            spec["op"], question=f"{formula}。{forward}？", answer=str(d1), params={"k": k1},
            explanation="代入公式：\\(10\\times \\log_{10} \\dfrac{I}{10^{-12}}\\)，化成 10 的次方後計算。",
        )
    for _ in range(50):
        k2 = rng.randint(2, 10)
        if k2 != k1:
            break
    d2 = 10 * (12 - k2)
    sound2 = rng.choice([s for s in _SOUNDS if s != sound1])
    inverse = f"若測得{sound2}為 {d2} 分貝，則其聲音強度 {m('I')} 為多少 W/m²"
    return pack(
        spec["op"], prompt=f"{formula}，試回答：", items=_items([forward, inverse]),
        answer=_parts([str(d1), f"10^(-{k2})"]), params={"k1": k1, "k2": k2},
        explanation="正向代入公式求分貝；反向由 \\(\\log_{10} \\dfrac{I}{I_{0}}=\\dfrac{d}{10}\\) 解出 \\(I\\)。",
    )


def build_log_equation_linear_arg(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(400):
        b = rng.choice([2, 3, 4, 5, 10])
        k = rng.choice([kk for kk in (1, 2, 3, 4) if b**kk <= 125])
        p, q = rng.choice([1, 1, 1, 2, 3]), rng.randint(-6, 12)
        x = F(b**k - q, p)
        if q != 0 and x != 0 and x.denominator <= 3:
            break
    eq = _lg(b, _paren_arg(_lin(p, q))) + f"={k}"
    explanation = "由對數定義得 \\(px+q=b^{k}\\)，解出 \\(x\\) 後檢查真數大於 0。"
    if spec.get("presentation") == "single_choice":
        pool = [x + b, x - b, F(b * k - q, p), F(k * k - q, p), -x]
        choices, label = make_choices(
            rng, (fraction_plain(x), m("x=" + tex_num(x))),
            [(fraction_plain(v), m("x=" + tex_num(v))) for v in pool], same=same_number,
        )
        return pack(
            spec["op"], question=f"方程式 {m(eq)} 之解為", answer=fraction_plain(x), presentation="single_choice",
            choices=choices, correct_label=label, params={"root": fraction_plain(x)}, explanation=explanation,
        )
    return pack(
        spec["op"], question=f"試求方程式 {m(eq)} 之解。", answer=fraction_plain(x),
        params={"root": fraction_plain(x)}, explanation=explanation,
    )


def build_log_equation_product_quadratic(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "const")
    for _ in range(400):
        b = rng.choice([2, 3, 5, 6, 8])
        if variant == "log_rhs":
            n = rng.randint(6, 60)
            rhs = _lg(b, str(n))
        else:
            k = rng.choice([kk for kk in (1, 2, 3) if b**kk <= 64])
            n = b**k
            rhs = str(k)
        pairs = [(u, n // u) for u in range(1, n + 1) if n % u == 0 and u != n // u]
        if not pairs:
            continue
        u, v = rng.choice(pairs)
        p = rng.randint(-6, 6)
        q = p + (v - u)
        if p == 0 or q == 0 or p == q:
            continue
        x = u - p
        bad = -v - p
        if x != 0 and abs(q) <= 12:
            break
    eq = _lg(b, _paren_arg(_lin(1, p))) + "+" + _lg(b, _paren_arg(_lin(1, q))) + "=" + rhs
    explanation = f"合併得 \\((x{p:+d})(x{q:+d})={n}\\)，解二次方程式後，真數必須大於 0，捨去 \\(x={bad}\\)。"
    if spec.get("presentation") == "single_choice":
        pool = [bad, x + 1, x - 2, -x, u + v]
        choices, label = make_choices(rng, num_choice(x), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=f"對數方程式 {m(eq)}，則 {m('x=')}", answer=str(x), presentation="single_choice",
            choices=choices, correct_label=label, params={"root": x, "rejected": bad}, explanation=explanation,
        )
    return pack(
        spec["op"], question=f"試求方程式 {m(eq)} 之解。", answer=str(x),
        params={"root": x, "rejected": bad}, explanation=explanation,
    )


def build_log_equation_quadratic_arg(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(400):
        b = rng.choice([2, 3, 5])
        k = rng.choice([kk for kk in (2, 3, 4, 5) if b**kk <= 81])
        n = b**k
        r2 = rng.choice([d for d in range(1, n + 1) if n % d == 0])
        r1 = -(n // r2)
        p = -(r1 + r2)
        if p != 0 and abs(p) <= 30:
            break
    inner = "x^{2}" + (f"+{p}x" if p > 0 else f"-{-p}x")
    rhs = _lg(b, str(n)) if rng.random() < 0.6 else str(k)
    eq = _lg(b, _paren_arg(inner)) + "=" + rhs
    return pack(
        spec["op"], question=f"解方程式 {m(eq)}（由小到大寫出所有解）。", answer={"(1)": str(r1), "(2)": str(r2)},
        part_labels={"(1)": "較小的解", "(2)": "較大的解"}, params={"roots": [r1, r2], "n": n},
        explanation=f"由 \\(x^{{2}}{p:+d}x={n}\\) 解二次方程式，兩根代回真數皆為 {n}>0，都合。",
    )


def build_log_equation_solve_base(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(300):
        c = rng.choice([2, 3, 5])
        s = rng.choice([1, 2])
        k = rng.choice([2, 3, 4])
        total = s * k
        op = rng.choice(["+", "+", "-"])
        if op == "+":
            i = rng.randint(1, total - 1)
            j = total - i
        else:
            j = rng.randint(1, 3)
            i = total + j
        if c**i <= 729 and c**j <= 729 and i != j:
            break
    eq = _lg("a", str(c**i)) + op + _lg("a", str(c**j)) + f"={k}"
    return pack(
        spec["op"], question=f"設 {m('a>0')} 且 {m('a' + NE + '1')}，若 {m(eq)}，試求 {m('a')} 之值。",
        answer=str(c**s), params={"a": c**s},
        explanation="合併成 \\(\\log_{a} N=k\\)，由定義得 \\(a^{k}=N\\)，再取正的 \\(a\\)。",
    )


def build_log_curve_through_points(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(300):
        a = rng.choice([2, 3, 4, 5])
        h = rng.choice([-3, -2, -1, 1, 2, 3])
        y1, y2 = rng.sample([1, 2, 3], 2)
        x1, x2 = a**y1 + h, a**y2 + h
        if x2 <= 130 and x1 <= 130:
            break
    ask = rng.choice(["a+b", "b-a", "a+b"])
    value = a + x2 if ask == "a+b" else x2 - a
    inner = _lin(1, -h)
    question = (
        f"若曲線 {m('y=' + _lg('a', _paren_arg(inner)))} 通過 {m('A' + _paren_arg(f'{x1},{y1}'))}、"
        f"{m('B' + _paren_arg(f'b,{y2}'))} 兩點，試求 {m(ask)} 之值。"
    )
    return pack(
        spec["op"], question=question, answer=str(value), params={"a": a, "b": x2, "h": h},
        explanation="把 A 點代入求底數 \\(a\\)，再把 B 點代入求 \\(b\\)。",
    )


_THRESHOLD_CANDIDATES = [6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 30]


def build_log_threshold_application_choice(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    given = [("2", GIVEN_LOG10[2]), ("3", GIVEN_LOG10[3])]
    for _ in range(500):
        c, d = rng.choice([30, 35, 37, 40]), rng.choice([20, 25, 31])
        picks = sorted(rng.sample(_THRESHOLD_CANDIDATES, 4))
        idx = rng.choice([1, 2])
        values = [c * approx_log10(x) + d for x in picks]
        exact = [c * true_log10(x) + d for x in picks]
        lo_val, hi_val = max(values[idx - 1], exact[idx - 1]), min(values[idx], exact[idx])
        t = int(hi_val - Decimal("0.3"))
        if t > lo_val + Decimal("0.3") and t < hi_val - Decimal("0.3"):
            break
    answer = picks[idx]
    choices, label = make_choices(rng, (str(answer), f"{answer} 歲"), [(str(x), f"{x} 歲") for x in picks if x != answer])
    question = (
        f"根據研究，若 {m('x')} 為犬隻年齡（單位：歲），則犬隻等同的人類年齡（單位：歲）約為 "
        f"{m(f'{c}' + TIMES + _lg(10, 'x') + f'+{d}')}。若稱「犬瑞」為犬隻年齡換算為人類年齡後達 {t} 歲以上，"
        f"則下列哪一個選項的犬隻年齡最接近且跨過「犬瑞」的門檻？（{_given_tex(given, common=False)}）"
    )
    return pack(
        spec["op"], question=question, answer=str(answer), presentation="single_choice", choices=choices,
        correct_label=label, params={"c": c, "d": d, "threshold": t, "choices": picks},
        given_approximations=_given_dict(given),
        explanation="把各選項代入公式，用給定的近似值計算，找出最小且達到門檻的年齡。",
    )


# ============================================================ 4-5 builders

def _table_value(r: int, c: int) -> int:
    """Four-digit mantissa for the table entry N=r (r/10), column c."""
    return int(table_log(F(10 * r + c, 100)) * 10000)


def _tail(r: int, d: int) -> int:
    span = Decimal(_table_value(r, 9) - _table_value(r, 0)) / 9
    return int((span * d / 10).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _array(header: list[str], rows: list[list[str]]) -> str:
    cols = "c|" + "c" * (len(header) - 1)
    body = r" \\ \hline ".join([" & ".join(header)] + [" & ".join(r) for r in rows])
    return r"\begin{array}{" + cols + "} " + body + r" \end{array}"


def build_common_log_table_lookup(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    kinds = spec["kinds"]
    items, answers, rows_needed, tail_rows = [], [], [], []
    for kind in kinds:
        for _ in range(200):
            r = rng.randint(11, 99)
            c = rng.randint(0, 9)
            if r not in rows_needed:
                break
        rows_needed.append(r)
        if kind == "3":
            num = F(10 * r + c, 100)
            shown = decimal_plain(Decimal(num.numerator) / Decimal(num.denominator))
            value = _table_value(r, c)
        else:
            d = rng.randint(1, 9)
            num = F(100 * r + 10 * c + d, 1000)
            shown = decimal_plain(Decimal(num.numerator) / Decimal(num.denominator))
            value = _table_value(r, c) + _tail(r, d)
            tail_rows.append(r)
        items.append(m(r"\log " + shown))
        answers.append(f"{Decimal(value) / 10000:.4f}")
    rows_needed.sort()
    left = _array(["N"] + [str(i) for i in range(5)], [[str(r)] + [f"{_table_value(r, i):04d}" for i in range(5)] for r in rows_needed])
    right = _array(["N"] + [str(i) for i in range(5, 10)], [[str(r)] + [f"{_table_value(r, i):04d}" for i in range(5, 10)] for r in rows_needed])
    stacked = r"\begin{array}{c} " + left + r" \\[6pt] " + right + r" \end{array}"
    prompt = (
        "下表為常用對數表的部分內容（表中數字為對數值小數點後的四位數字，N 為真數的前兩位數字）："
        + m(stacked)
    )
    if tail_rows:
        tails = _array(["N"] + [str(i) for i in range(1, 10)], [[str(r)] + [str(_tail(r, i)) for i in range(1, 10)] for r in sorted(tail_rows)])
        prompt += "；表尾差（真數第四位數字對應的增加量）：" + m(tails)
    prompt += "。試利用上表查出下列對數的近似值（四捨五入到小數點後第四位）："
    return pack(
        spec["op"], prompt=prompt, items=_items(items), answer=_parts(answers), common_log=True,
        params={"rows": rows_needed, "answers": answers}, visual_type="TEXT_RECOVERABLE",
        given_approximations={"table_rows": ",".join(str(r) for r in rows_needed)},
        explanation="先找前兩位數字所在的列，再找第三位數字的行；第四位數字查表尾差後加上去。",
    )


_GIVEN_APPROX_NUMBERS = [
    n for n in range(12, 1000)
    if set(factor_int(n)) <= {2, 3, 5} and len(factor_int(n)) >= 2 and n not in (100, 10) and n % 10 != 0
]


def build_common_log_given_approx_eval(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(200):
        n = rng.choice(_GIVEN_APPROX_NUMBERS)
        primes = sorted(factor_int(n))
        if len(primes) >= 2:
            break
    given = [(str(p), GIVEN_LOG10[p]) for p in primes]
    value = approx_log10(n, {p: GIVEN_LOG10[p] for p in primes})
    question = f"若 {_given_tex(given, common=False)}，則 {m(_lg(10, str(n)))} 之近似值為何？"
    return pack(
        spec["op"], question=question, answer=decimal_plain(value), params={"n": n},
        given_approximations=_given_dict(given),
        explanation="把真數做質因數分解，用對數的乘法與次方性質，代入給定的近似值。",
    )


def _mantissa(rng: random.Random) -> Decimal:
    return Decimal(rng.randint(1000, 9899)) / 10000


def build_log_characteristic_mantissa(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    var = rng.choice(["x", "y", "a"])
    sign = spec.get("sign", "pos")
    if spec.get("presentation") == "single_choice":
        n = rng.randint(1, 5)
        mant = _mantissa(rng)
        shown = -(n + mant) if sign != "pos" else n + mant
        char = floor_decimal(shown)
        pool = [char + 1, -char, char - 1, n, 0, 1]
        choices, label = make_choices(rng, num_choice(char), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=f"若 {m(LOG + var + '=' + format(shown, 'f'))}，則 {m(LOG + var)} 之首數為",
            answer=str(char), presentation="single_choice", choices=choices, correct_label=label, common_log=True,
            params={"shown": format(shown, "f"), "characteristic": char},
            explanation="首數為不大於對數值的最大整數，尾數 \\(=\\) 對數值 \\(-\\) 首數，且 \\(0\\le\\) 尾數 \\(<1\\)。",
        )
    n = rng.randint(1, 7)
    mant = _mantissa(rng)
    log_tex = LOG + var
    if sign == "pos":
        shown = n + mant
        char, mnt = n, mant
        second = f"{m(var)} 之整數部分為幾位數"
        answer = {"(1) 首數": str(char), "(1) 尾數": decimal_plain(mnt), "(2) 位數": str(n + 1)}
    else:
        shown = -(n + mant)
        char = -(n + 1)
        mnt = 1 - mant
        second = f"{m(var)} 自小數點後第幾位開始出現不為 0 的數字"
        answer = {"(1) 首數": str(char), "(1) 尾數": decimal_plain(mnt), "(2) 第幾位": str(n + 1)}
    prompt = f"設 {m(log_tex + APPROX + format(shown, 'f'))}，試求："
    return pack(
        spec["op"], prompt=prompt, items=_items([f"{m(log_tex)} 之首數與尾數", second]),
        answer=answer, common_log=True, params={"shown": format(shown, "f"), "characteristic": char},
        explanation="首數為不大於對數值的最大整數，尾數為對數值減去首數；首數為 \\(n\\ge 0\\) 時整數部分為 \\(n+1\\) 位數，首數為 \\(-n\\) 時小數點後第 \\(n\\) 位開始不為 0。",
    )


def build_log_characteristic_rule(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    letter = rng.choice(["n", "k", "m"])
    o1, o2 = rng.choice([0, 0, 1, -1]), rng.choice([0, 0, 1, -1])

    def shifted(o: int) -> str:
        return letter if o == 0 else (f"{letter}+{o}" if o > 0 else f"{letter}-{-o}")

    def shifted_tex(o: int) -> str:
        return letter if o == 0 else _paren_arg(shifted(o))

    char1 = shifted(o1)
    char2 = shifted(o2)
    alpha = ALPHA
    t1 = (
        f"若 {m('x>1')}，且 {m(LOG + 'x=' + char1 + '+' + alpha)}，其中 {m(char1)} 為首數，"
        f"{m(alpha)} 為尾數（{m(letter)} 為正整數），則 {m('x')} 之整數部分為幾位數？"
    )
    unit_interval = m(r"0\lt x\lt 1")
    t2 = (
        f"若 {unit_interval}，且 {m(LOG + 'x=-' + shifted_tex(o2) + '+' + alpha)}，其中 {m('-' + shifted_tex(o2))} 為首數，"
        f"{m(alpha)} 為尾數（{m(letter)} 為大於 1 的整數），則 {m('x')} 自小數點後第幾位開始出現不為 0 的數字？"
    )
    ans1 = shifted(o1 + 1)
    ans2 = char2
    return pack(
        spec["op"], prompt=f"以 {m(letter)} 表示下列答案：", items=_items([t1, t2]),
        answer={"(1)": ans1, "(2)": ans2}, common_log=True, params={"letter": letter, "offsets": [o1, o2]},
        part_checkers={"(1)": "expression_checker", "(2)": "expression_checker"},
        explanation="首數為 \\(n\\ge 0\\) 時整數部分為 \\(n+1\\) 位數；首數為 \\(-n\\) 時小數點後第 \\(n\\) 位開始出現不為 0 的數字。",
    )


def _sci_mantissa(rng: random.Random) -> tuple[Decimal, Decimal]:
    for _ in range(200):
        v = Decimal(rng.randint(101, 999)) / 100
        if v % 1 != 0:
            return v, table_log(F(str(v)))
    raise ValueError("sci_mantissa_failed")


def _dec_times_pow10(v: Decimal, k: int) -> str:
    return decimal_plain(v.scaleb(k))


def build_log_scientific_shift(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "forward_inverse")
    v, L = _sci_mantissa(rng)
    lg = LOG
    ap = APPROX
    explanation = "\\(\\log \\left(a\\times 10^{n}\\right)=n+\\log a\\)：乘以 \\(10^{n}\\) 只改變首數，尾數不變。"
    k, j = rng.sample([2, 3, 4, 5], 2)
    big = _dec_times_pow10(v, k)
    if variant == "neg_single":
        jn = rng.randint(1, 4)
        shown = L - (jn + 1)
        question = f"已知 {m(lg + big + ap + format(k + L, 'f'))}，若 {m(lg + 'N=' + format(shown, 'f'))}，試求 {m('N')} 之值。"
        return pack(
            spec["op"], question=question, answer=_dec_times_pow10(v, -(jn + 1)), common_log=True,
            params={"v": str(v), "L": str(L)}, given_approximations={f"log {big}": format(k + L, "f")},
            explanation=explanation,
        )
    if variant == "reverse":
        prompt = f"已知 {m(lg + big + ap + format(k + L, 'f'))}，試回答："
        texts = [f"試求 {m(lg + decimal_plain(v))} 之值", f"若 {m(lg + 'M' + ap + format(j + L, 'f'))}，試求 {m('M')} 之值"]
        answers = [decimal_plain(L), _dec_times_pow10(v, j)]
        given = {f"log {big}": format(k + L, "f")}
    else:
        prompt = f"已知 {m(lg + decimal_plain(v) + ap + format(L, 'f'))}，試回答："
        texts = [f"試求 {m(lg + big)} 之值", f"若 {m(lg + 'x' + ap + format(j + L, 'f'))}，試求 {m('x')} 之值"]
        answers = [decimal_plain(k + L), _dec_times_pow10(v, j)]
        given = {f"log {decimal_plain(v)}": format(L, "f")}
    return pack(
        spec["op"], prompt=prompt, items=_items(texts), answer=_parts(answers), common_log=True,
        params={"v": str(v), "L": str(L), "k": k, "j": j}, given_approximations=given, explanation=explanation,
    )


_DIGIT_BASES = [2, 3, 5, 6, 7, 12, 15, 18, 24, 14]


def build_log_power_digit_count(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(500):
        base = rng.choice(_DIGIT_BASES)
        n = rng.choice(list(range(10, 101, 5)))
        given = _prime_givens(base)
        approx = n * approx_log10(base)
        exact = n * true_log10(base)
        if robust_floor(approx, exact, margin=Decimal("0.02")):
            break
    digits = floor_decimal(approx) + 1
    lg = LOG
    head = f"已知 {_given_tex(given, common=True)}，則 {m(f'{base}^{{{n}}}')} 為幾位數？"
    explanation = f"\\({lg}{base}^{{{n}}}={n}{lg}{base}\\)，首數加 1 即為位數。"
    if spec.get("presentation") == "single_choice":
        pool = [digits - 1, digits + 1, digits + 2, digits - 2]
        choices, label = make_choices(rng, num_choice(digits), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=head, answer=str(digits), presentation="single_choice", choices=choices,
            correct_label=label, common_log=True, params={"base": base, "n": n}, given_approximations=_given_dict(given),
            explanation=explanation,
        )
    return pack(
        spec["op"], question=head, answer=str(digits), common_log=True, params={"base": base, "n": n},
        given_approximations=_given_dict(given), explanation=explanation,
    )


_FIRST_NONZERO_BASES = [(1, 2), (1, 3), (2, 3), (3, 4), (1, 6), (2, 9), (3, 8), (4, 9), (1, 7), (2, 7)]


def build_log_power_first_nonzero(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    for _ in range(500):
        p, q = rng.choice(_FIRST_NONZERO_BASES)
        n = rng.choice(list(range(10, 101, 5)))
        base = F(p, q)
        given = _prime_givens(base)
        approx = n * approx_log10(base)
        exact = n * true_log10(base)
        if robust_floor(approx, exact, margin=Decimal("0.02")):
            break
    place = -floor_decimal(approx)
    power = m(_paren_arg(tex_num(base)) + "^{" + str(n) + "}")
    question = (
        f"已知 {_given_tex(given, common=True)}，若將 {power} 化為小數，"
        f"則在小數點後面第幾位開始出現不為 0 的數字？"
    )
    return pack(
        spec["op"], question=question, answer=str(place), common_log=True, params={"p": p, "q": q, "n": n},
        given_approximations=_given_dict(given),
        explanation="計算對數值並寫成「負首數 + 尾數」，首數為 \\(-n\\) 時小數點後第 \\(n\\) 位開始出現不為 0 的數字。",
    )


_DEP_RATES = [5, 10, 15, 20, 25]
_GROW_RATES = [2, 5, 8, 10, 20]
_DEP_RATIOS = [F(1, 2), F(3, 8), F(1, 3), F(1, 4), F(3, 4), F(2, 3), F(3, 16)]
_GROW_RATIOS = [F(2), F(3), F(3, 2), F(4), F(9, 4), F(8, 3)]
_DEP_CONTEXTS = [("一輛汽車", "年"), ("一台機器設備", "年"), ("一支智慧型手機", "個月")]
_GROW_CONTEXTS = [("存款的本利和", "年"), ("某公司的營業額", "年"), ("某城市的人口", "年")]


def _growth_setup(rng: random.Random, grow: bool, margin: Decimal) -> dict[str, Any]:
    for _ in range(800):
        rate = rng.choice(_GROW_RATES if grow else _DEP_RATES)
        factor = F(100 + rate, 100) if grow else F(100 - rate, 100)
        ratio = rng.choice(_GROW_RATIOS if grow else _DEP_RATIOS)
        scale = rng.choice([1, 2, 5, 10])
        start = ratio.denominator * scale
        target = ratio.numerator * scale
        if not grow and start < 4:
            continue
        log_f = table_log(factor)
        approx_n = approx_log10(ratio, {2: GIVEN_LOG10[2], 3: GIVEN_LOG10[3]}) / log_f
        exact_n = true_log10(ratio) / true_log10(factor)
        if approx_n <= 1 or approx_n > 60:
            continue
        if not robust_floor(approx_n, exact_n, margin=margin):
            continue
        return {
            "rate": rate, "factor": factor, "ratio": ratio, "start": start, "target": target,
            "log_f": log_f, "approx_n": approx_n, "exact_n": exact_n,
        }
    raise ValueError("growth_setup_failed")


def build_log_growth_years(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    variant = spec.get("variant", "dep")
    grow = variant in ("grow", "closest")
    margin = Decimal("0.2") if variant == "closest" else Decimal("0.05")
    for _ in range(50):
        s = _growth_setup(rng, grow, margin)
        frac = s["approx_n"] - floor_decimal(s["approx_n"])
        if variant != "closest" or abs(frac - Decimal("0.5")) >= Decimal("0.2"):
            break
    factor_dec = fraction_as_terminating_decimal(s["factor"])
    ratio = s["ratio"]
    primes = sorted(set(factor_int(ratio.numerator)) | set(factor_int(ratio.denominator)))
    given = [(factor_dec, s["log_f"])] + [(str(p), GIVEN_LOG10[p]) for p in primes]
    given_text = _given_tex(given, common=True)
    unit = "萬元"
    if grow:
        thing, period = rng.choice(_GROW_CONTEXTS)
        amount_unit = "萬人" if "人口" in thing else unit
        story = f"{thing}目前為 {s['start']} {amount_unit}，每{period.replace('個', '')}成長 {s['rate']}%（以複利計算）"
    else:
        thing, period = rng.choice(_DEP_CONTEXTS)
        amount_unit = unit
        story = f"{thing}目前價值 {s['start']} {unit}，每{period.replace('個', '')}折舊 {s['rate']}%（即每{period.replace('個', '')}價值變為前一期的 {factor_dec} 倍）"
    if variant == "closest":
        answer = int(s["approx_n"].to_integral_value(rounding=ROUND_HALF_UP))
        question = f"{story}，試問幾{period}後最接近 {s['target']} {amount_unit}？（{given_text}）"
        pool = [answer - 2, answer + 2, answer - 4, answer + 4, answer - 6]
    else:
        answer = floor_decimal(s["approx_n"]) + 1
        verb = f"會超過 {s['target']} {amount_unit}" if grow else f"會低於 {s['target']} {amount_unit}"
        question = f"{story}，試問最少幾{period}之後{verb}？（{given_text}）"
        pool = [answer - 1, answer + 1, answer + 2, answer - 2]
    explanation = (
        f"列式 \\({s['start']}\\times {factor_dec}^{{n}}\\) 與 {s['target']} 比較，兩邊取對數得 "
        f"\\(n\\log {factor_dec}\\) 與 \\(\\log \\dfrac{{{ratio.numerator}}}{{{ratio.denominator}}}\\) 的關係，再用給定近似值求 \\(n\\)。"
    )
    params = {"rate": s["rate"], "start": s["start"], "target": s["target"], "n_star": format(s["approx_n"], "f")}
    if spec.get("presentation") == "single_choice":
        pool = [v for v in pool if v > 0]
        choices, label = make_choices(rng, num_choice(answer), [num_choice(v) for v in pool], same=same_number)
        return pack(
            spec["op"], question=question, answer=str(answer), presentation="single_choice", choices=choices,
            correct_label=label, common_log=True, params=params, given_approximations=_given_dict(given),
            explanation=explanation,
        )
    return pack(
        spec["op"], question=question, answer=str(answer), common_log=True, params=params,
        given_approximations=_given_dict(given), explanation=explanation,
    )
