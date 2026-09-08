# -*- coding: utf-8 -*-
"""Polynomial algebra domain operators for vocational Math B1 chapter 3."""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

_SUPPORTED_OPS = frozenset(
    {
        # 3-1 PolynomialBasicConcepts
        "polynomial_descending_power_properties",
        "polynomial_param_degree_constraint",
        "polynomial_descending_power_table",
        "zero_polynomial_find_coeffs",
        "polynomial_degree_product_sum",
        # 3-1 PolynomialArithmeticOperations
        "polynomial_add_sub",
        "polynomial_multiply",
        "polynomial_product_term_coefficient",
        "polynomial_long_division",
        "polynomial_synthetic_division",
        "polynomial_remainder_param_solve",
        "polynomial_shifted_basis_eval",
        # reserved for later chapter-3 expansion
        "polynomial_equality_identity",
        "remainder_theorem_evaluate",
        "factor_theorem_root_factor",
        "polynomial_factoring",
        "rational_expression_arithmetic",
        "rational_equation_solve",
    }
)


def _trim(coeffs: dict[int, Fraction]) -> dict[int, Fraction]:
    return {int(k): Fraction(v) for k, v in coeffs.items() if Fraction(v) != 0}


def _degree(coeffs: dict[int, Fraction]) -> int:
    cleaned = _trim(coeffs)
    return max(cleaned.keys()) if cleaned else -1


def _leading(coeffs: dict[int, Fraction]) -> Fraction:
    cleaned = _trim(coeffs)
    if not cleaned:
        return Fraction(0)
    return cleaned[max(cleaned.keys())]


def _eval(coeffs: dict[int, Fraction], x: int | Fraction) -> Fraction:
    xx = Fraction(x)
    total = Fraction(0)
    for exp, coeff in coeffs.items():
        total += Fraction(coeff) * (xx ** int(exp))
    return total


def _frac_plain(val: Fraction) -> str:
    val = Fraction(val)
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"


def _term_latex(coeff: Fraction, exp: int, *, first: bool) -> str:
    c = Fraction(coeff)
    if c == 0:
        return ""
    abs_c = abs(c)
    sign = ""
    if first:
        sign = "-" if c < 0 else ""
    else:
        sign = " - " if c < 0 else " + "

    if exp == 0:
        body = _frac_plain(abs_c)
    elif exp == 1:
        if abs_c == 1:
            body = "x"
        else:
            body = f"{_frac_plain(abs_c)}x"
    else:
        if abs_c == 1:
            body = f"x^{{{exp}}}"
        else:
            body = f"{_frac_plain(abs_c)}x^{{{exp}}}"
    return f"{sign}{body}"


def poly_latex(coeffs: dict[int, Fraction], *, name: str | None = "f") -> str:
    cleaned = _trim(coeffs)
    if not cleaned:
        body = "0"
    else:
        degrees = sorted(cleaned.keys(), reverse=True)
        parts: list[str] = []
        for idx, exp in enumerate(degrees):
            parts.append(_term_latex(cleaned[exp], exp, first=(idx == 0)))
        body = "".join(parts)
    if name:
        return f"{name}(x)={body}"
    return body


def poly_plain(coeffs: dict[int, Fraction]) -> str:
    cleaned = _trim(coeffs)
    if not cleaned:
        return "0"
    degrees = sorted(cleaned.keys(), reverse=True)
    parts: list[str] = []
    for idx, exp in enumerate(degrees):
        c = cleaned[exp]
        abs_c = abs(c)
        sign = "-" if c < 0 else ("+" if idx else "")
        if exp == 0:
            term = _frac_plain(abs_c)
        elif exp == 1:
            term = "x" if abs_c == 1 else f"{_frac_plain(abs_c)}x"
        else:
            term = f"x^{exp}" if abs_c == 1 else f"{_frac_plain(abs_c)}x^{exp}"
        if idx == 0 and c >= 0:
            parts.append(term)
        elif idx == 0 and c < 0:
            parts.append(f"-{term}")
        else:
            parts.append(f"{sign}{term}")
    return "".join(parts)


def _answer_bundle(canonical: str, *, parts: dict[str, str] | None = None, value: Any = None) -> dict[str, Any]:
    payload_value = value if value is not None else (parts if parts is not None else canonical)
    return {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": [],
        "parts": parts or {},
        "value": payload_value,
    }


def _numeric_distractors(rng: random.Random, correct: int | str, *, count: int = 3) -> list[str]:
    """Build distinct integer-like distractors around a scalar correct answer."""
    try:
        base = int(str(correct).strip())
    except (TypeError, ValueError):
        base = None
    out: list[str] = []
    seen = {str(correct).strip()}
    if base is not None:
        deltas = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, -6, -7, 8, -8, 9, -9, 10]
        rng.shuffle(deltas)
        for d in deltas:
            cand = str(base + d)
            if cand in seen:
                continue
            seen.add(cand)
            out.append(cand)
            if len(out) >= count:
                return out
    # fallback strings
    for i in range(1, 20):
        cand = f"d{i}"
        if cand in seen:
            continue
        seen.add(cand)
        out.append(cand)
        if len(out) >= count:
            break
    return out[:count]


def _rand_nonzero(rng: random.Random, lo: int = -5, hi: int = 5) -> int:
    values = [v for v in range(lo, hi + 1) if v != 0]
    return int(rng.choice(values))


def _poly_add(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) + Fraction(coeff)
    return _trim(out)


def _poly_sub(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out = dict(a)
    for exp, coeff in b.items():
        out[exp] = out.get(exp, Fraction(0)) - Fraction(coeff)
    return _trim(out)


def _poly_mul(a: dict[int, Fraction], b: dict[int, Fraction]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            out[e1 + e2] = out.get(e1 + e2, Fraction(0)) + Fraction(c1) * Fraction(c2)
    return _trim(out)


def _poly_scalar_mul(a: dict[int, Fraction], k: Fraction) -> dict[int, Fraction]:
    return _trim({exp: Fraction(coeff) * Fraction(k) for exp, coeff in a.items()})


def _poly_long_division(
    dividend: dict[int, Fraction],
    divisor: dict[int, Fraction],
) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
    divisor = _trim(divisor)
    if not divisor:
        raise ValueError("division by zero polynomial")
    remainder = dict(dividend)
    quotient: dict[int, Fraction] = {}
    div_deg = _degree(divisor)
    div_lead = divisor[div_deg]
    while remainder and _degree(remainder) >= div_deg:
        rem_deg = _degree(remainder)
        rem_lead = remainder[rem_deg]
        q_exp = rem_deg - div_deg
        q_coeff = Fraction(rem_lead, div_lead)
        quotient[q_exp] = quotient.get(q_exp, Fraction(0)) + q_coeff
        subtract_poly = _poly_scalar_mul(
            {exp + q_exp: coeff for exp, coeff in divisor.items()},
            q_coeff,
        )
        remainder = _poly_sub(remainder, subtract_poly)
    return _trim(quotient), _trim(remainder)


def _rand_poly(
    rng: random.Random,
    *,
    deg: int | None = None,
    deg_lo: int = 1,
    deg_hi: int = 3,
    coeff_lo: int = -5,
    coeff_hi: int = 5,
    allow_zero_lower: bool = True,
) -> dict[int, Fraction]:
    d = int(deg if deg is not None else rng.randint(deg_lo, deg_hi))
    coeffs: dict[int, Fraction] = {d: Fraction(_rand_nonzero(rng, coeff_lo, coeff_hi))}
    for e in range(d):
        if allow_zero_lower and rng.random() < 0.25:
            continue
        coeffs[e] = Fraction(_rand_nonzero(rng, coeff_lo, coeff_hi))
    return _trim(coeffs)


def _build_descending_power_properties(rng: random.Random) -> dict[str, Any]:
    degree = rng.randint(2, 4)
    coeffs = {d: Fraction(_rand_nonzero(rng)) for d in range(degree + 1)}
    # scramble display order
    display_order = list(range(degree + 1))
    rng.shuffle(display_order)
    display_coeffs = {d: coeffs[d] for d in display_order}
    x0 = rng.choice([-2, -1, 1, 2])
    value = _eval(coeffs, x0)
    descending = poly_plain(coeffs)
    question = (
        f"設${poly_latex(display_coeffs)}$，試求："
        f"(1) $f(x)$依降冪排列 "
        f"(2) $\\deg f(x)$ "
        f"(3) $f(x)$的首項係數 "
        f"(4) $f(x)$在$x={x0}$時之值"
    )
    parts = {
        "part_1": descending,
        "part_2": str(_degree(coeffs)),
        "part_3": _frac_plain(_leading(coeffs)),
        "part_4": _frac_plain(value),
    }
    return {
        "givens": {
            "question_text": question,
            "coeffs": {str(k): _frac_plain(v) for k, v in coeffs.items()},
            "evaluate_at": x0,
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "先依次數由高到低排列各項。",
            "次數為最高次項的指數；首項係數為該項係數。",
            "代入指定 x 值求函數值。",
        ],
    }


def _build_param_degree_constraint(rng: random.Random) -> dict[str, Any]:
    target_deg = rng.choice([1, 2])
    high = target_deg + 2
    # Build parametric coeffs so deg == target_deg forces higher coeffs to 0
    # f(x) = (a-p)x^high + (b-q)x^(high-1) + ... + lower terms with numbers
    p = rng.randint(-3, 3)
    q = rng.randint(-3, 3)
    a_true = p  # so a-p = 0
    b_true = q  # so b-q = 0
    lower: dict[int, Fraction] = {}
    for d in range(0, target_deg + 1):
        lower[d] = Fraction(_rand_nonzero(rng, -4, 4))
    # Ensure exact degree target_deg
    if target_deg not in lower or lower[target_deg] == 0:
        lower[target_deg] = Fraction(_rand_nonzero(rng))

    poly_terms = []
    poly_terms.append(f"\\left(a{-p:+d}\\right)x^{{{high}}}" if p else f"(a)x^{{{high}}}")
    # cleaner latex
    a_shift = -p
    b_shift = -q
    a_factor = f"(a{a_shift:+d})" if a_shift else "a"
    b_factor = f"(b{b_shift:+d})" if b_shift else "b"
    mid_deg = high - 1
    body = f"{a_factor}x^{{{high}}}+{b_factor}x^{{{mid_deg}}}"
    for d in sorted(lower.keys(), reverse=True):
        body += _term_latex(lower[d], d, first=False)

    result_poly = poly_plain(lower)
    question = (
        f"多項式$f(x)={body}$，若$\\deg f(x)={target_deg}$，試求："
        f"(1) $a$、$b$之值 (2) $f(x)$"
    )
    parts = {
        "part_1": f"a={a_true},b={b_true}",
        "part_2": result_poly,
    }
    return {
        "givens": {
            "question_text": question,
            "target_degree": target_deg,
            "a": a_true,
            "b": b_true,
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            f"要使次數為 {target_deg}，高於該次的係數必須為 0。",
            "解出 a、b 後，寫出剩餘多項式。",
        ],
    }


def _build_descending_power_table(rng: random.Random) -> dict[str, Any]:
    deg_f = rng.randint(2, 3)
    deg_g = rng.randint(2, 4)
    f = {d: Fraction(_rand_nonzero(rng, -5, 5)) for d in range(deg_f + 1)}
    g = {d: Fraction(_rand_nonzero(rng, -5, 5)) for d in range(deg_g + 1)}
    # scrambled presentation
    f_order = list(f.keys())
    g_order = list(g.keys())
    rng.shuffle(f_order)
    rng.shuffle(g_order)
    f_display = {d: f[d] for d in f_order}
    g_display = {d: g[d] for d in g_order}
    question = (
        f"已知${poly_latex(f_display)}$，${poly_latex(g_display, name='g')}$，"
        f"試按降冪排列完成下表："
    )
    parts = {
        "part_1": poly_plain(f),
        "part_2": poly_plain(g),
        "part_3": str(_degree(f)),
        "part_4": str(_degree(g)),
        "part_5": _frac_plain(_leading(f)),
        "part_6": _frac_plain(_leading(g)),
    }
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
            "g": {str(k): _frac_plain(v) for k, v in g.items()},
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "將 f、g 各自依降冪排列。",
            "讀取次數與首項係數填入表格。",
        ],
    }


def _build_zero_polynomial(rng: random.Random) -> dict[str, Any]:
    # (a-p)x^2 + (b-q)x + (c-r) = 0 for all x => a=p,b=q,c=r
    p = rng.randint(-3, 3)
    q = rng.randint(-3, 3)
    r = rng.randint(-4, 4)
    # avoid trivial all-zero offsets looking odd; keep variety
    a_shift = -p
    b_shift = -q
    # constant term as 2c - 2r style sometimes; keep simple c-r
    a_factor = f"(a{a_shift:+d})" if a_shift else "a"
    b_factor = f"(b{b_shift:+d})" if b_shift else "b"
    if r == 0:
        c_term = "c"
    elif abs(r) == 1:
        c_term = f"c{'+' if r < 0 else '-'}1"
    else:
        c_term = f"c{-r:+d}"
    question = (
        f"設$g(x)={a_factor}x^{{2}}+{b_factor}x+{c_term}$為一零多項式，試求$a$、$b$、$c$之值。"
    )
    parts = {
        "part_1": str(p),
        "part_2": str(q),
        "part_3": str(r),
    }
    return {
        "givens": {
            "question_text": question,
            "a": p,
            "b": q,
            "c": r,
        },
        "answer": _answer_bundle(f"a={p},b={q},c={r}", parts=parts),
        "distractors": [],
        "explanation_steps": [
            "零多項式各次係數皆為 0。",
            "分別令二次、一次、常數項係數為 0 解出參數。",
        ],
    }


def _build_degree_product_sum(rng: random.Random) -> dict[str, Any]:
    deg_f = rng.randint(2, 4)
    deg_g = rng.randint(2, 5)
    # product degree always deg_f + deg_g
    # sum degree is max unless cancellation; assume no cancellation of leading terms
    deg_h = deg_f + deg_g
    deg_k = max(deg_f, deg_g)
    # ask a+b / a-b / a,b depending on seed
    prefer_choice = bool(getattr(rng, "_prefer_choice", False))
    if prefer_choice:
        mode = rng.choice(["diff", "diff", "sum", "product_only"])
    else:
        mode = rng.choice(["sum", "pair", "product_only"])
    if mode == "sum":
        question = (
            f"設$f(x)$為{deg_f}次多項式，$g(x)$為{deg_g}次多項式，"
            f"$h(x)=f(x)\\times g(x)$，$k(x)=f(x)+g(x)$，"
            f"且$h(x)$為$a$次多項式，$k(x)$為$b$次多項式。若首項不互相消去，求$a+b$之值。"
        )
        ans = str(deg_h + deg_k)
        parts = {"part_1": ans}
        canonical = ans
        distractors = _numeric_distractors(rng, ans)
    elif mode == "diff":
        question = (
            f"設$f(x)$為{deg_f}次多項式，$g(x)$為{deg_g}次多項式，"
            f"$h(x)=f(x)\\times g(x)$，$k(x)=f(x)+g(x)$，"
            f"且$h(x)$為$a$次多項式，$k(x)$為$b$次多項式，則$a-b=$？"
        )
        ans = str(deg_h - deg_k)
        parts = {"part_1": ans}
        canonical = ans
        distractors = _numeric_distractors(rng, ans)
        for extra in (str(deg_h), str(deg_h + deg_k), str(abs(deg_f - deg_g))):
            if extra != ans and extra not in distractors:
                distractors.append(extra)
        distractors = distractors[:3]
    elif mode == "product_only":
        question = (
            f"設$f(x)$為{deg_f}次多項式，$g(x)$為{deg_g}次多項式，"
            f"則$f(x)\\times g(x)$的次數為？"
        )
        ans = str(deg_h)
        parts = {"part_1": ans}
        canonical = ans
        distractors = _numeric_distractors(rng, ans)
    else:
        question = (
            f"設$f(x)$為{deg_f}次多項式，$g(x)$為{deg_g}次多項式，"
            f"$h(x)=f(x)\\times g(x)$，$k(x)=f(x)+g(x)$，"
            f"且首項不互相消去。若$h(x)$為$a$次、$k(x)$為$b$次，求$a$、$b$。"
        )
        parts = {"part_1": str(deg_h), "part_2": str(deg_k)}
        canonical = f"a={deg_h},b={deg_k}"
        distractors = [str(deg_h), str(deg_k), str(abs(deg_f - deg_g))]
    return {
        "givens": {
            "question_text": question,
            "deg_f": deg_f,
            "deg_g": deg_g,
        },
        "answer": _answer_bundle(
            canonical,
            parts=parts,
            value=parts if len(parts) > 1 else parts["part_1"],
        ),
        "distractors": distractors,
        "explanation_steps": [
            "乘積次數為兩式次數相加。",
            "和的次數為較高次數（首項不消去時）。",
        ],
    }


def _build_add_sub(rng: random.Random) -> dict[str, Any]:
    f = _rand_poly(rng, deg_lo=2, deg_hi=3)
    g = _rand_poly(rng, deg_lo=1, deg_hi=3)
    s = _poly_add(f, g)
    d = _poly_sub(f, g)
    mode = rng.choice(["add_sub", "add_sub", "add_sub_mul"])
    question = (
        f"已知${poly_latex(f)}$，${poly_latex(g, name='g')}$，試求："
        f"(1) $f(x)+g(x)$ (2) $f(x)-g(x)$"
    )
    parts = {"part_1": poly_plain(s), "part_2": poly_plain(d)}
    if mode == "add_sub_mul":
        p = _poly_mul(f, g)
        question += " (3) $f(x)\\times g(x)$"
        parts["part_3"] = poly_plain(p)
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
            "g": {str(k): _frac_plain(v) for k, v in g.items()},
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "同類項係數相加得和；相減得差。",
            "若求乘積，將各項逐一相乘後合併同類項。",
        ],
    }


def _build_multiply(rng: random.Random) -> dict[str, Any]:
    f = _rand_poly(rng, deg_lo=1, deg_hi=3)
    g = _rand_poly(rng, deg_lo=1, deg_hi=2)
    product = _poly_mul(f, g)
    deg = _degree(product)
    parts = {"part_1": poly_plain(product), "part_2": str(deg)}
    question = (
        f"試求多項式${poly_latex(f)}$與${poly_latex(g, name='g')}$的乘積及其次數。"
    )
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
            "g": {str(k): _frac_plain(v) for k, v in g.items()},
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "將兩多項式各項相乘後合併同類項得乘積。",
            "乘積次數為兩式次數之和（首項不為零時）。",
        ],
    }


def _build_product_term_coefficient(rng: random.Random) -> dict[str, Any]:
    f = _rand_poly(rng, deg_lo=2, deg_hi=4, allow_zero_lower=True)
    g = _rand_poly(rng, deg_lo=1, deg_hi=2, allow_zero_lower=True)
    product = _poly_mul(f, g)
    max_k = _degree(product)
    # prefer a middle power that appears in textbook-style x^3 / x^4 targets
    candidates = [k for k in range(1, max_k) if k in product] or list(range(0, max_k + 1))
    k = int(rng.choice(candidates))
    coeff = product.get(k, Fraction(0))
    ans = _frac_plain(coeff)
    parts = {"part_1": ans}
    question = (
        f"已知多項式${poly_latex(f)}$，${poly_latex(g, name='g')}$，"
        f"試求$f(x)\\times g(x)$的$x^{{{k}}}$項係數。"
    )
    return {
        "givens": {
            "question_text": question,
            "target_power": k,
            "f": {str(k0): _frac_plain(v) for k0, v in f.items()},
            "g": {str(k0): _frac_plain(v) for k0, v in g.items()},
        },
        "answer": _answer_bundle(ans, parts=parts, value=ans),
        "distractors": _numeric_distractors(rng, ans),
        "explanation_steps": [
            f"只收集乘積中次數為 {k} 的各項係數並相加。",
            "不必展開全部乘積。",
        ],
    }


def _build_long_division(rng: random.Random) -> dict[str, Any]:
    # monic quadratic divisor keeps quotient/remainder integer-friendly
    divisor = {
        2: Fraction(1),
        1: Fraction(rng.randint(-3, 3)),
        0: Fraction(_rand_nonzero(rng, -3, 3)),
    }
    quotient = _rand_poly(rng, deg=1, coeff_lo=-4, coeff_hi=4, allow_zero_lower=False)
    remainder = {
        1: Fraction(_rand_nonzero(rng, -8, 8)),
        0: Fraction(rng.randint(-8, 8)),
    }
    if _degree(remainder) >= _degree(divisor):
        remainder = {0: Fraction(_rand_nonzero(rng))}
    dividend = _poly_add(_poly_mul(divisor, quotient), remainder)
    q, r = _poly_long_division(dividend, divisor)
    mode = (
        rng.choice(["remainder_ab_sum", "recover_quotient", "remainder_ab_sum"])
        if bool(getattr(rng, "_prefer_choice", False))
        else "quotient_remainder"
    )
    if mode == "remainder_ab_sum" and 1 in r:
        a = int(r.get(1, Fraction(0)))
        b = int(r.get(0, Fraction(0)))
        ans = str(a + b)
        parts = {"part_1": ans}
        question = (
            f"多項式${poly_plain(dividend)}$除以${poly_plain(divisor)}$，"
            f"餘式為$ax+b$，則$a+b=$？"
        )
        return {
            "givens": {
                "question_text": question,
                "dividend": {str(k): _frac_plain(v) for k, v in dividend.items()},
                "divisor": {str(k): _frac_plain(v) for k, v in divisor.items()},
            },
            "answer": _answer_bundle(ans, parts=parts, value=ans),
            "distractors": _numeric_distractors(rng, ans),
            "explanation_steps": [
                "以長除法求出一次餘式 ax+b。",
                "再計算 a+b。",
            ],
        }
    if mode == "recover_quotient":
        # Style: dividend = f(x)*divisor + known linear remainder → ask f(x)
        rem_display = poly_plain(remainder)
        # rearrange: dividend = f*divisor - (-remainder) presentation like textbook
        # textbook: LHS = f*divisor - 4x - 2  ⇒ remainder contribution is -(-4x-2)
        neg_rem = {e: -c for e, c in remainder.items()}
        lhs = _poly_add(_poly_mul(divisor, quotient), remainder)
        question = (
            f"設$f(x)$為多項式，且${poly_plain(lhs)}=f(x)\\left({poly_plain(divisor)}\\right)"
            f"{_signed_poly_suffix(neg_rem)}$，則$f(x)=$？"
        )
        ans = poly_plain(quotient)
        # distractors: nearby linear polys
        dist = []
        for _ in range(8):
            dq = dict(quotient)
            e = rng.choice(list(dq.keys()) or [0])
            dq[e] = dq.get(e, Fraction(0)) + Fraction(_rand_nonzero(rng, -2, 2))
            text = poly_plain(_trim(dq))
            if text != ans and text not in dist:
                dist.append(text)
            if len(dist) >= 3:
                break
        while len(dist) < 3:
            dist.append(poly_plain({1: Fraction(_rand_nonzero(rng)), 0: Fraction(rng.randint(-3, 3))}))
        return {
            "givens": {
                "question_text": question,
                "divisor": {str(k): _frac_plain(v) for k, v in divisor.items()},
                "remainder": {str(k): _frac_plain(v) for k, v in remainder.items()},
            },
            "answer": _answer_bundle(ans, parts={"part_1": ans}, value=ans),
            "distractors": dist[:3],
            "explanation_steps": [
                "移項得 f(x)×除式 = 左式 − 餘式項。",
                "長除或比較係數求出一次式 f(x)。",
            ],
        }
    parts = {"part_1": poly_plain(q), "part_2": poly_plain(r)}
    question = (
        f"試求$\\left({poly_plain(dividend)}\\right)\\div\\left({poly_plain(divisor)}\\right)$的商式和餘式。"
    )
    return {
        "givens": {
            "question_text": question,
            "dividend": {str(k): _frac_plain(v) for k, v in dividend.items()},
            "divisor": {str(k): _frac_plain(v) for k, v in divisor.items()},
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "用長除法：每次以首項相除得商項，乘回後從被除式減去。",
            "餘式次數須小於除式次數。",
        ],
    }


def _signed_poly_suffix(poly: dict[int, Fraction]) -> str:
    """Render a signed poly suffix like '+3x-2' or '-4x-2' for equation stems."""
    body = poly_plain(poly)
    if not body or body == "0":
        return ""
    if body.startswith("-"):
        return body
    return f"+{body}"


def _build_synthetic_division(rng: random.Random) -> dict[str, Any]:
    f = _rand_poly(rng, deg=rng.choice([2, 3]), coeff_lo=-5, coeff_hi=5, allow_zero_lower=True)
    # ensure dense descending for synthetic division display
    for e in range(_degree(f) + 1):
        f.setdefault(e, Fraction(0))
    n_cases = rng.choice([1, 2, 2])
    cs = []
    while len(cs) < n_cases:
        c = rng.choice([-3, -2, -1, 1, 2, 3])
        if c not in cs:
            cs.append(c)
    parts: dict[str, str] = {}
    case_texts: list[str] = []
    for i, c in enumerate(cs):
        divisor = {1: Fraction(1), 0: Fraction(-c)}  # x - c
        q, r = _poly_long_division(f, divisor)
        # pair each case: quotient then remainder
        parts[f"part_{2 * i + 1}"] = poly_plain(q)
        parts[f"part_{2 * i + 2}"] = poly_plain(r)
        if c >= 0:
            g_tex = f"x-{c}" if c else "x"
        else:
            g_tex = f"x+{-c}"
        case_texts.append(f"({i + 1}) $g(x)={g_tex}$")
    question = (
        f"試利用綜合除法，求多項式${poly_latex(f)}$除以$g(x)$的商式及餘式："
        + " ".join(case_texts)
    )
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in _trim(f).items()},
            "roots": cs,
        },
        "answer": _answer_bundle("；".join(parts.values()), parts=parts),
        "distractors": [],
        "explanation_steps": [
            "對一次因式 x−c 可用綜合除法。",
            "最後一列得商式係數，最右為餘式（常數）。",
        ],
    }


def _constraint_example_ids(rng: random.Random) -> set[int]:
    constraints = getattr(rng, "_constraints", None) or {}
    if not isinstance(constraints, dict):
        return set()
    ids: set[int] = set()
    blobs: list[Any] = [constraints]
    for key in ("v3_induced_spec", "phase1_classification"):
        nested = constraints.get(key)
        if isinstance(nested, dict):
            blobs.append(nested)
    for blob in blobs:
        for key in ("source_example_id", "textbook_example_id"):
            raw = blob.get(key)
            try:
                eid = int(raw)
            except (TypeError, ValueError):
                continue
            if eid > 0:
                ids.add(eid)
    return ids


def _constraint_source_text(rng: random.Random) -> str:
    constraints = getattr(rng, "_constraints", None) or {}
    if not isinstance(constraints, dict):
        return ""
    parts = [
        str(constraints.get("source_question_text") or ""),
        str(constraints.get("source_problem_text") or ""),
    ]
    for key in ("v3_induced_spec", "phase1_classification"):
        nested = constraints.get(key)
        if isinstance(nested, dict):
            parts.append(str(nested.get("source_question_text") or ""))
            parts.append(str(nested.get("source_problem_text") or ""))
    return "\n".join(parts)


def _looks_like_square_remainder_divisibility(rng: random.Random) -> bool:
    """Detect 4628-style: remainder of f/(x-p)^2 is divisible by (x-q)."""
    if 4628 in _constraint_example_ids(rng):
        return True
    text = _constraint_source_text(rng)
    if "餘式被" in text and "整除" in text:
        return True
    return False


def _square_factor_tex(root: int) -> str:
    inner = _linear_factor_tex(root)
    return r"{{\left(" + inner + r"\right)}^{2}}"


def _solve_quadratic_square_remainder(p: int, q: int) -> tuple[int, int]:
    """Unique (b, c) for f(x)=x^2+bx+c under the 4628 remainder conditions."""
    if p == q:
        raise ValueError("square_remainder_roots_must_differ")
    b = -(p + q)
    c = p * p + q * q - p * q
    return b, c


def _build_quadratic_square_remainder_divisibility(rng: random.Random) -> dict[str, Any]:
    # Topology (教材 4628 / 110統測B):
    # f(x)=x^2+bx+c
    # rem(f, (x-p)^2) divisible by (x-q)
    # rem(f, (x-q)^2) divisible by (x-p)
    # ask c. Safe pairs keep a unique integer solution.
    safe_pairs = ((-1, 1), (1, -1), (-2, 1), (1, -2), (-1, 2), (2, -1))
    p, q = rng.choice(safe_pairs)
    b_true, c_true = _solve_quadratic_square_remainder(p, q)
    # Independent remainder check (never hard-code c).
    rem1_at_q = (b_true + 2 * p) * q + (c_true - p * p)
    rem2_at_p = (b_true + 2 * q) * p + (c_true - q * q)
    if rem1_at_q != 0 or rem2_at_p != 0:
        raise ValueError("square_remainder_conditions_inconsistent")
    ans = str(c_true)
    p_tex = _linear_factor_tex(p)
    q_tex = _linear_factor_tex(q)
    question = (
        rf"已知$f\left( x \right)={{{{x}}^{{2}}}}+bx+c$為二次多項式。"
        rf"若$f\left( x \right)$被${_square_factor_tex(p)}$除的餘式被${q_tex}$整除，"
        rf"且$f\left( x \right)$被${_square_factor_tex(q)}$除的餘式被${p_tex}$整除，"
        rf"則$c=$？"
    )
    textbook_choices = ["-3", "-1", "1", "3"]
    if ans in textbook_choices:
        distractors = [item for item in textbook_choices if item != ans]
    else:
        distractors = _numeric_distractors(rng, ans)
        for extra in ("-3", "-1", "1", "3", str(-c_true), str(p * p + q * q)):
            if extra != ans and extra not in distractors:
                distractors.append(extra)
        distractors = distractors[:3]
    return {
        "givens": {
            "question_text": question,
            "p": p,
            "q": q,
            "b": b_true,
            "c": c_true,
            "divisor_root_1": p,
            "divisor_root_2": q,
        },
        "answer": _answer_bundle(ans, parts={"part_1": ans}, value=ans),
        "distractors": distractors,
        "explanation_steps": [
            f"f(x) 與 ({_linear_factor_plain(p)})^2 均為二次且首項係數 1，"
            f"餘式 r1(x)=(b+{2 * p})x+(c-{p * p})。",
            f"r1 被 {_linear_factor_plain(q)} 整除 ⇒ r1({q})=0。",
            f"同理 r2({p})=0。聯立得唯一解 c={c_true}。",
        ],
    }


def _build_remainder_param_solve(rng: random.Random) -> dict[str, Any]:
    # Style 4628: quadratic remainder-of-square divisible by the other linear factor
    if _looks_like_square_remainder_divisibility(rng):
        return _build_quadratic_square_remainder_divisibility(rng)
    # Style 4627: divisor known, dividend has a,b unknown, remainder given → solve a,b
    # Also isomorphic to self-assessment: divisible case asking a+b
    mode = (
        "divisible_a_plus_b"
        if bool(getattr(rng, "_prefer_choice", False))
        else "solve_ab"
    )
    if mode == "divisible_a_plus_b":
        divisor = {
            2: Fraction(1),
            1: Fraction(rng.randint(-2, 2)),
            0: Fraction(_rand_nonzero(rng, -3, 3)),
        }
        quotient = _rand_poly(rng, deg=1, coeff_lo=-3, coeff_hi=3, allow_zero_lower=False)
        remainder = {0: Fraction(0)}
        dividend = _poly_mul(divisor, quotient)  # exact division
        # present as x^3 + a x^2 + b x + const with const known
        const = int(dividend.get(0, Fraction(0)))
        a_true = int(dividend.get(2, Fraction(0)))
        b_true = int(dividend.get(1, Fraction(0)))
        # force cubic leading 1
        if _degree(dividend) != 3:
            # rebuild with deg-1 quotient ensuring cubic
            quotient = {
                1: Fraction(_rand_nonzero(rng, -3, 3)),
                0: Fraction(rng.randint(-3, 3)),
            }
            dividend = _poly_mul(divisor, quotient)
            const = int(dividend.get(0, Fraction(0)))
            a_true = int(dividend.get(2, Fraction(0)))
            b_true = int(dividend.get(1, Fraction(0)))
        lead = int(dividend.get(3, Fraction(1)))
        # simpler display matching textbook: x^3 + a x^2 + b x + const
        const_term = _term_latex(Fraction(const), 0, first=False)
        if lead == 1:
            display = f"x^{{3}}+ax^{{2}}+bx{const_term}"
        else:
            display = f"{lead}x^{{3}}+ax^{{2}}+bx{const_term}"
        ans = str(a_true + b_true)
        question = (
            f"已知$a$、$b$為實數，若${display}$可被${poly_plain(divisor)}$整除，則$a+b=$？"
        )
        return {
            "givens": {
                "question_text": question,
                "a": a_true,
                "b": b_true,
                "divisor": {str(k): _frac_plain(v) for k, v in divisor.items()},
            },
            "answer": _answer_bundle(ans, parts={"part_1": ans}, value=ans),
            "distractors": _numeric_distractors(rng, ans),
            "explanation_steps": [
                "可整除表示餘式為 0。",
                "比較係數或做長除法解出 a、b 後求 a+b。",
            ],
        }

    divisor = {2: Fraction(1), 1: Fraction(1), 0: Fraction(1)}  # x^2+x+1 common
    if rng.random() < 0.4:
        divisor = {
            2: Fraction(1),
            1: Fraction(rng.randint(-2, 3)),
            0: Fraction(_rand_nonzero(rng, -2, 3)),
        }
    quotient = _rand_poly(rng, deg=1, coeff_lo=-3, coeff_hi=3, allow_zero_lower=False)
    remainder = {
        1: Fraction(_rand_nonzero(rng, -8, 8)),
        0: Fraction(rng.randint(-8, 8)),
    }
    dividend = _poly_add(_poly_mul(divisor, quotient), remainder)
    a_true = dividend.get(1, Fraction(0))
    b_true = dividend.get(0, Fraction(0))
    # present higher terms known + ax + b
    high = {e: c for e, c in dividend.items() if e >= 2}
    high_body = poly_plain(high) if high else "0"
    if high_body == "0":
        display = "ax+b"
    else:
        display = f"{high_body}+ax+b"
    rem_plain = poly_plain(remainder)
    question = (
        f"設${poly_plain(divisor)}$除${display}$的餘式為${rem_plain}$，試求實數$a$、$b$之值。"
    )
    parts = {"part_1": _frac_plain(a_true), "part_2": _frac_plain(b_true)}
    return {
        "givens": {
            "question_text": question,
            "a": _frac_plain(a_true),
            "b": _frac_plain(b_true),
            "divisor": {str(k): _frac_plain(v) for k, v in divisor.items()},
            "remainder": {str(k): _frac_plain(v) for k, v in remainder.items()},
        },
        "answer": _answer_bundle(f"a={_frac_plain(a_true)},b={_frac_plain(b_true)}", parts=parts),
        "distractors": [],
        "explanation_steps": [
            "被除式 = 商式×除式 + 餘式；比較同類項係數。",
            "或令被除式減去已知餘式後可被除式整除，解出 a、b。",
        ],
    }


def _build_shifted_basis_eval(rng: random.Random) -> dict[str, Any]:
    # Style 4617: f(x)=a(x-s)^3+b(x-s)^2+c(x-s)+d；a+b+c+d = f(s+1)
    s = rng.choice([1, 1, 2, -1])
    f = _rand_poly(rng, deg=3, coeff_lo=-5, coeff_hi=5, allow_zero_lower=False)
    ans_val = _eval(f, s + 1)
    ans = _frac_plain(ans_val)
    parts = {"part_1": ans}
    shift_tex = f"x-{s}" if s >= 0 else f"x+{-s}"
    question = (
        f"設多項式${poly_latex(f)}="
        f"a\\left({shift_tex}\\right)^{{3}}+b\\left({shift_tex}\\right)^{{2}}"
        f"+c\\left({shift_tex}\\right)+d$，試求$a+b+c+d$之值。"
        f"（提示：令${shift_tex}=1$）"
    )
    return {
        "givens": {
            "question_text": question,
            "shift": s,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
        },
        "answer": _answer_bundle(ans, parts=parts, value=ans),
        "distractors": [],
        "explanation_steps": [
            f"令 {shift_tex}=1，即 x={s + 1}。",
            "此時右邊恰為 a+b+c+d，等於左邊代入該 x 值。",
        ],
    }


def _linear_factor_plain(c: int) -> str:
    """Monic linear factor (x - c) in plain text."""
    if c == 0:
        return "x"
    if c > 0:
        return f"x-{c}"
    return f"x+{-c}"


def _linear_factor_tex(c: int) -> str:
    if c == 0:
        return "x"
    if c > 0:
        return f"x-{c}"
    return f"x+{-c}"


def _factorization_plain(lead: int, roots: list[int]) -> str:
    body = "".join(f"({_linear_factor_plain(r)})" for r in roots)
    if lead == 1:
        return body
    if lead == -1:
        return f"-{body}"
    return f"{lead}{body}"


def _build_equality_identity(rng: random.Random) -> dict[str, Any]:
    # Identity: equate coefficients → solve a, b (, c)
    # Also cube-expansion isomorphic mode: (ax^2+bx+c)^3 = expanded, ask a+b+c
    mode = (
        "cube_sum"
        if bool(getattr(rng, "_prefer_choice", False))
        else rng.choice(["ab", "abc", "ab"])
    )
    if mode == "cube_sum":
        a = rng.choice([1, 1, 1, -1])
        b = rng.randint(-3, 3)
        c = rng.choice([-3, -2, -1, 1, 2, 3])
        inner = {2: Fraction(a), 1: Fraction(b), 0: Fraction(c)}
        expanded = _poly_mul(_poly_mul(inner, inner), inner)
        ans = str(a + b + c)
        question = (
            "設$"
            + poly_plain(expanded)
            + r"={{\left(a{{x}^{2}}+bx+c\right)}^{3}}$，則$a+b+c=$？"
        )
        return {
            "givens": {
                "question_text": question,
                "a": a,
                "b": b,
                "c": c,
                "expanded": {str(k): _frac_plain(v) for k, v in expanded.items()},
            },
            "answer": _answer_bundle(ans, parts={"part_1": ans}, value=ans),
            "distractors": _numeric_distractors(rng, ans),
            "explanation_steps": [
                "由最高次項得 a；由展開交叉項比較得 b、c。",
                "最後求 a+b+c。",
            ],
        }

    # Right-hand side known poly
    rhs = {
        2: Fraction(_rand_nonzero(rng, -4, 4)),
        1: Fraction(rng.randint(-5, 5)),
        0: Fraction(rng.randint(-5, 5)),
    }
    a_true = int(rhs[2])
    b_true = int(rhs[1])
    # left: (a+p)x^2 + (b+q)x + ... so a_true = rhs[2]-p etc.
    p = rng.randint(-3, 3)
    q = rng.randint(-3, 3)
    a_ans = a_true - p
    b_ans = b_true - q
    a_factor = f"(a{p:+d})" if p else "a"
    b_factor = f"(b{q:+d})" if q else "b"
    if mode == "abc":
        c_true = int(rhs[0])
        r = rng.randint(-3, 3)
        c_ans = c_true - r
        c_factor = f"(c{r:+d})" if r else "c"
        left = f"{a_factor}x^{{2}}+{b_factor}x+{c_factor}"
        parts = {
            "part_1": str(a_ans),
            "part_2": str(b_ans),
            "part_3": str(c_ans),
        }
        canonical = f"a={a_ans},b={b_ans},c={c_ans}"
        givens_extra = {"a": a_ans, "b": b_ans, "c": c_ans}
    else:
        # constant known on left
        const = int(rhs[0])
        left = f"{a_factor}x^{{2}}+{b_factor}x{_term_latex(Fraction(const), 0, first=False)}"
        parts = {"part_1": str(a_ans), "part_2": str(b_ans)}
        canonical = f"a={a_ans},b={b_ans}"
        givens_extra = {"a": a_ans, "b": b_ans}
    rhs_body = poly_plain(rhs)
    question = (
        f"若對所有實數$x$皆有${left}={rhs_body}$，試求實數參數之值。"
    )
    return {
        "givens": {
            "question_text": question,
            "rhs": {str(k): _frac_plain(v) for k, v in rhs.items()},
            **givens_extra,
        },
        "answer": _answer_bundle(canonical, parts=parts),
        "distractors": [],
        "explanation_steps": [
            "恆等式兩邊同次項係數必須相等。",
            "分別比較二次、一次、常數項係數解出參數。",
        ],
    }


def _build_remainder_theorem(rng: random.Random) -> dict[str, Any]:
    f = _rand_poly(rng, deg=rng.choice([2, 3]), coeff_lo=-5, coeff_hi=5, allow_zero_lower=True)
    mode = rng.choice(["remainder", "evaluate", "both", "multi_c"])
    if mode == "multi_c":
        cs = []
        while len(cs) < 2:
            c = rng.choice([-3, -2, -1, 1, 2, 3])
            if c not in cs:
                cs.append(c)
        parts = {}
        case_bits = []
        for i, c in enumerate(cs):
            rem = _eval(f, c)
            parts[f"part_{i + 1}"] = _frac_plain(rem)
            case_bits.append(f"({i + 1}) 除以${_linear_factor_tex(c)}$的餘式")
        question = (
            f"設${poly_latex(f)}$，利用餘式定理求：" + " ".join(case_bits)
        )
        return {
            "givens": {
                "question_text": question,
                "f": {str(k): _frac_plain(v) for k, v in f.items()},
                "roots": cs,
            },
            "answer": _answer_bundle("；".join(parts.values()), parts=parts),
            "distractors": [],
            "explanation_steps": [
                "除以 (x−c) 的餘式等於 f(c)。",
                "分別代入各 c 值求函數值即得餘式。",
            ],
        }

    c = rng.choice([-3, -2, -1, 1, 2, 3, 4])
    rem = _eval(f, c)
    rem_s = _frac_plain(rem)
    divisor = _linear_factor_tex(c)
    if mode == "remainder":
        question = (
            f"設${poly_latex(f)}$，試求$f(x)$除以${divisor}$的餘式。"
        )
        parts = {"part_1": rem_s}
        canonical = rem_s
    elif mode == "evaluate":
        question = f"設${poly_latex(f)}$，試求$f({c})$之值。"
        parts = {"part_1": rem_s}
        canonical = rem_s
    else:
        question = (
            f"設${poly_latex(f)}$，試求："
            f"(1) $f({c})$ (2) $f(x)$除以${divisor}$的餘式"
        )
        parts = {"part_1": rem_s, "part_2": rem_s}
        canonical = f"{rem_s}；{rem_s}"
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
            "c": c,
            "remainder": rem_s,
        },
        "answer": _answer_bundle(
            canonical,
            parts=parts,
            value=parts if len(parts) > 1 else rem_s,
        ),
        "distractors": [],
        "explanation_steps": [
            "餘式定理：f(x) 除以 (x−c) 的餘式等於 f(c)。",
            "將 x=c 代入多項式即可。",
        ],
    }


def _build_factor_theorem(rng: random.Random) -> dict[str, Any]:
    mode = rng.choice(["root_to_factor", "factor_to_root", "param_root", "verify_and_factor"])
    if mode == "root_to_factor":
        c = rng.choice([-3, -2, -1, 1, 2, 3])
        other = rng.choice([-3, -2, -1, 1, 2, 3])
        while other == c:
            other = rng.choice([-3, -2, -1, 1, 2, 3])
        lead = rng.choice([1, 1, 2, -1])
        f = _poly_scalar_mul(
            _poly_mul({1: Fraction(1), 0: Fraction(-c)}, {1: Fraction(1), 0: Fraction(-other)}),
            Fraction(lead),
        )
        # maybe inflate to cubic with another root
        if rng.random() < 0.45:
            third = rng.choice([-2, -1, 1, 2, 3])
            f = _poly_mul(f, {1: Fraction(1), 0: Fraction(-third)})
        question = (
            f"設${poly_latex(f)}$，已知$x={c}$為一根，試求對應一次因式，"
            f"並寫出$f(x)$可被該因式整除。"
        )
        factor = _linear_factor_plain(c)
        parts = {"part_1": factor, "part_2": f"({factor})"}
        return {
            "givens": {
                "question_text": question,
                "root": c,
                "f": {str(k): _frac_plain(v) for k, v in f.items()},
            },
            "answer": _answer_bundle(f"{factor}；可整除", parts=parts),
            "distractors": [],
            "explanation_steps": [
                "因式定理：若 f(c)=0，則 (x−c) 為 f(x) 的因式。",
                "由已知根直接寫出一次因式。",
            ],
        }

    if mode == "factor_to_root":
        c = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        other = _rand_nonzero(rng, -3, 3)
        while other == c:
            other = _rand_nonzero(rng, -3, 3)
        f = _poly_mul(
            {1: Fraction(1), 0: Fraction(-c)},
            {1: Fraction(1), 0: Fraction(-other)},
        )
        if rng.random() < 0.5:
            f = _poly_mul(f, {1: Fraction(1), 0: Fraction(-rng.choice([-2, -1, 1, 2]))})
        factor = _linear_factor_tex(c)
        question = (
            f"設${poly_latex(f)}$，已知${factor}$為$f(x)$的因式，試求對應的根。"
        )
        parts = {"part_1": str(c)}
        return {
            "givens": {
                "question_text": question,
                "factor": _linear_factor_plain(c),
                "f": {str(k): _frac_plain(v) for k, v in f.items()},
            },
            "answer": _answer_bundle(str(c), parts=parts, value=str(c)),
            "distractors": [],
            "explanation_steps": [
                "若 (x−c) 為因式，則 x=c 為一根。",
                "由因式直接讀出根。",
            ],
        }

    if mode == "param_root":
        # f(x)=(x-c)(x-r)+k style with parameter a so f(c)=0 forces a
        c = rng.choice([-2, -1, 1, 2, 3])
        a_true = rng.randint(-4, 4)
        # f(x)=x^2 + (a-p)x + (q) with f(c)=0 => a known
        # Build: f(x)=x^2 + m x + n, force f(c)=0 by choosing n from m,c then encode m via a
        m = a_true  # coefficient of x is a
        n = -c * c - m * c  # so c^2 + m c + n = 0
        # present as x^2 + a x + n (n fixed)
        f_display = f"x^{{2}}+ax{_term_latex(Fraction(n), 0, first=False)}"
        question = (
            f"設$f(x)={f_display}$，若$x={c}$為$f(x)$的一根，試求$a$之值，"
            f"並寫出對應因式。"
        )
        factor = _linear_factor_plain(c)
        parts = {"part_1": str(a_true), "part_2": factor}
        return {
            "givens": {
                "question_text": question,
                "root": c,
                "a": a_true,
            },
            "answer": _answer_bundle(f"a={a_true}；{factor}", parts=parts),
            "distractors": [],
            "explanation_steps": [
                "代入 f(c)=0 解出參數 a。",
                "由因式定理得一次因式 (x−c)。",
            ],
        }

    # verify_and_factor: check f(c)=0 then factor completely (quadratic)
    c = rng.choice([-3, -2, -1, 1, 2, 3])
    other = rng.choice([-3, -2, -1, 1, 2, 3])
    while other == c:
        other = rng.choice([-3, -2, -1, 1, 2, 3])
    lead = rng.choice([1, 1, 2])
    f = _poly_scalar_mul(
        _poly_mul({1: Fraction(1), 0: Fraction(-c)}, {1: Fraction(1), 0: Fraction(-other)}),
        Fraction(lead),
    )
    factored = _factorization_plain(lead, [c, other])
    question = (
        f"設${poly_latex(f)}$。(1) 驗證$x={c}$為一根 "
        f"(2) 將$f(x)$因式分解"
    )
    parts = {"part_1": "0", "part_2": factored}
    return {
        "givens": {
            "question_text": question,
            "root": c,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
        },
        "answer": _answer_bundle(f"f({c})=0；{factored}", parts=parts),
        "distractors": [],
        "explanation_steps": [
            "先算 f(c)，若為 0 則 (x−c) 為因式。",
            "再用短除或觀察得另一因式，完成分解。",
        ],
    }


def _build_polynomial_factoring(rng: random.Random) -> dict[str, Any]:
    deg = rng.choice([2, 2, 3])
    roots: list[int] = []
    pool = [-3, -2, -1, 1, 2, 3, 4]
    while len(roots) < deg:
        r = int(rng.choice(pool))
        # allow at most one repeated root
        if roots.count(r) >= 1 and rng.random() < 0.7:
            continue
        roots.append(r)
    lead = int(rng.choice([1, 1, 1, 2, -1]))
    f: dict[int, Fraction] = {0: Fraction(1)}
    for r in roots:
        f = _poly_mul(f, {1: Fraction(1), 0: Fraction(-r)})
    f = _poly_scalar_mul(f, Fraction(lead))
    factored = _factorization_plain(lead, roots)
    mode = rng.choice(["expression", "expression", "multi_part"])
    if mode == "multi_part":
        question = (
            f"試將多項式${poly_latex(f, name=None)}$因式分解為一次因式的乘積，"
            f"並寫出所有整數根。"
        )
        roots_sorted = sorted(set(roots))
        parts = {
            "part_1": factored,
            "part_2": ",".join(str(r) for r in roots_sorted),
        }
        canonical = "；".join(parts.values())
    else:
        question = f"試將多項式${poly_latex(f, name=None)}$因式分解。"
        parts = {"part_1": factored}
        canonical = factored
    return {
        "givens": {
            "question_text": question,
            "f": {str(k): _frac_plain(v) for k, v in f.items()},
            "roots": roots,
            "lead": lead,
        },
        "answer": _answer_bundle(
            canonical,
            parts=parts,
            value=parts if len(parts) > 1 else factored,
        ),
        "distractors": [],
        "explanation_steps": [
            "先試可能的整數根（常數項因數）。",
            "用因式定理逐次提出一次因式，直到完全分解。",
        ],
    }


def _rational_plain(num: dict[int, Fraction], den: dict[int, Fraction]) -> str:
    return f"({poly_plain(num)})/({poly_plain(den)})"


def _build_rational_expression_arithmetic(rng: random.Random) -> dict[str, Any]:
    mode = rng.choice(["simplify", "multiply", "add", "simplify"])
    if mode == "simplify":
        # cancel common linear factor
        common = rng.choice([-2, -1, 1, 2, 3])
        other_n = rng.choice([-3, -2, -1, 1, 2, 3])
        while other_n == common:
            other_n = rng.choice([-3, -2, -1, 1, 2, 3])
        other_d = rng.choice([-3, -2, -1, 1, 2, 3])
        while other_d in (common, other_n):
            other_d = rng.choice([-3, -2, -1, 1, 2, 3])
        num = _poly_mul(
            {1: Fraction(1), 0: Fraction(-common)},
            {1: Fraction(1), 0: Fraction(-other_n)},
        )
        den = _poly_mul(
            {1: Fraction(1), 0: Fraction(-common)},
            {1: Fraction(1), 0: Fraction(-other_d)},
        )
        simplified = _rational_plain(
            {1: Fraction(1), 0: Fraction(-other_n)},
            {1: Fraction(1), 0: Fraction(-other_d)},
        )
        question = (
            f"試化簡有理式$\\dfrac{{{poly_plain(num)}}}{{{poly_plain(den)}}}$（可約分）。"
        )
        parts = {"part_1": simplified}
        return {
            "givens": {
                "question_text": question,
                "numerator": {str(k): _frac_plain(v) for k, v in num.items()},
                "denominator": {str(k): _frac_plain(v) for k, v in den.items()},
            },
            "answer": _answer_bundle(simplified, parts=parts, value=simplified),
            "distractors": [],
            "explanation_steps": [
                "分子分母因式分解後約去公因式。",
                "注意定義域須扣除使原分母為零的值。",
            ],
        }

    if mode == "multiply":
        a = rng.choice([-2, -1, 1, 2])
        b = rng.choice([-3, -2, 1, 2, 3])
        while b == a:
            b = rng.choice([-3, -2, 1, 2, 3])
        c = rng.choice([-2, -1, 1, 2, 3])
        while c in (a, b):
            c = rng.choice([-2, -1, 1, 2, 3])
        # (x-a)/(x-b) * (x-b)/(x-c) = (x-a)/(x-c)
        n1 = {1: Fraction(1), 0: Fraction(-a)}
        d1 = {1: Fraction(1), 0: Fraction(-b)}
        n2 = {1: Fraction(1), 0: Fraction(-b)}
        d2 = {1: Fraction(1), 0: Fraction(-c)}
        product = _rational_plain(n1, d2)
        question = (
            f"試求$\\dfrac{{{poly_plain(n1)}}}{{{poly_plain(d1)}}}"
            f"\\times\\dfrac{{{poly_plain(n2)}}}{{{poly_plain(d2)}}}$"
            f"（化簡後）。"
        )
        parts = {"part_1": product}
        return {
            "givens": {"question_text": question},
            "answer": _answer_bundle(product, parts=parts, value=product),
            "distractors": [],
            "explanation_steps": [
                "有理式相乘：分子相乘、分母相乘。",
                "約去公因式後得最簡形式。",
            ],
        }

    # add: 1/(x-a) + 1/(x-b) = (2x-(a+b))/((x-a)(x-b))
    a = rng.choice([-2, -1, 1, 2])
    b = rng.choice([-3, -2, 1, 2, 3])
    while b == a:
        b = rng.choice([-3, -2, 1, 2, 3])
    num = {1: Fraction(2), 0: Fraction(-(a + b))}
    den = _poly_mul(
        {1: Fraction(1), 0: Fraction(-a)},
        {1: Fraction(1), 0: Fraction(-b)},
    )
    result = _rational_plain(num, den)
    question = (
        f"試求$\\dfrac{{1}}{{{_linear_factor_tex(a)}}}"
        f"+\\dfrac{{1}}{{{_linear_factor_tex(b)}}}$（化成單一分式）。"
    )
    parts = {"part_1": result}
    return {
        "givens": {"question_text": question, "a": a, "b": b},
        "answer": _answer_bundle(result, parts=parts, value=result),
        "distractors": [],
        "explanation_steps": [
            "通分：分母為兩一次因式之積。",
            "分子為各分子乘上互補因式後相加。",
        ],
    }


def _build_rational_equation_solve(rng: random.Random) -> dict[str, Any]:
    # Solve A/(x-p) + B/(x-q) = C  with small integers; state excluded values
    mode = rng.choice(["two_denom", "two_denom", "simple_prop"])
    if mode == "simple_prop":
        # (x-a)/(x-b) = k  → x-a = k(x-b), excluded x=b
        a = rng.choice([-3, -2, -1, 1, 2, 3])
        b = rng.choice([-3, -2, -1, 1, 2, 3])
        while b == a:
            b = rng.choice([-3, -2, -1, 1, 2, 3])
        k = rng.choice([2, 3, -1, -2])
        # x - a = k(x - b) => x - a = k x - k b => x - k x = a - k b => x(1-k)=a-kb
        # x = (a - k b)/(1 - k)
        num = a - k * b
        den = 1 - k
        if den == 0 or num % den != 0:
            # force integer: choose a so that solution is integer s ≠ b
            s = rng.choice([-2, -1, 1, 2, 3, 4])
            while s == b:
                s = rng.choice([-2, -1, 1, 2, 3, 4])
            a = k * (s - b) + s  # from s-a = k(s-b)
            sol = s
        else:
            sol = num // den
            if sol == b:
                sol = b + 1
                a = k * (sol - b) + sol
        excluded = b
        question = (
            f"解方程式$\\dfrac{{{_linear_factor_tex(a)}}}{{{_linear_factor_tex(b)}}}={k}$，"
            f"並寫出不屬於定義域的值。"
        )
        parts = {
            "part_1": str(sol),
            "part_2": str(excluded),
        }
        canonical = f"x={sol}；x≠{excluded}"
        return {
            "givens": {
                "question_text": question,
                "solution": sol,
                "excluded": [excluded],
            },
            "answer": _answer_bundle(canonical, parts=parts),
            "distractors": [],
            "explanation_steps": [
                f"定義域：分母≠0，故 x≠{excluded}。",
                "兩邊同乘分母得一次方程，解出後檢驗是否在定義域內。",
            ],
        }

    # A/(x-p) = B/(x-q) → linear after clearing; unique solution
    p = rng.choice([-3, -2, -1, 1, 2])
    q = rng.choice([-3, -2, 1, 2, 3])
    while q == p:
        q = rng.choice([-3, -2, 1, 2, 3])
    A = int(rng.choice([1, 2, 3]))
    B = int(rng.choice([1, 2, 3]))
    # A(x-q)=B(x-p) => A x - A q = B x - B p => (A-B)x = A q - B p
    if A == B:
        B = A + 1
    # Force integer solution s ≠ p,q
    s = rng.choice([-4, -3, -1, 1, 3, 4])
    while s in (p, q):
        s = rng.choice([-4, -3, -1, 1, 3, 4])
    # Choose A,B so s satisfies A/(s-p)=B/(s-q): take A=s-q, B=s-p (nonzero)
    A = s - q
    B = s - p
    if A == 0 or B == 0:
        s = max(p, q) + 2
        A = s - q
        B = s - p
    eq_tex = (
        f"\\dfrac{{{A}}}{{{_linear_factor_tex(p)}}}"
        f"=\\dfrac{{{B}}}{{{_linear_factor_tex(q)}}}"
    )
    excluded = sorted({p, q})
    question = (
        f"解有理方程式${eq_tex}$，並寫出解集合與定義域排除值。"
    )
    excl_str = ",".join(str(v) for v in excluded)
    parts = {
        "part_1": str(s),
        "part_2": excl_str,
    }
    canonical = f"{{{s}}}；x≠{excl_str}"
    return {
        "givens": {
            "question_text": question,
            "solution": s,
            "excluded": excluded,
        },
        "answer": _answer_bundle(canonical, parts=parts),
        "distractors": [],
        "explanation_steps": [
            f"先排除使分母為零的值：x≠{excl_str}。",
            "兩邊同乘兩分母得一次方程，解出後確認屬於定義域。",
        ],
    }


def build_polynomial_matrix(
    *,
    seed: int | None,
    line_type: str | None = None,
    domain_operation: str | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a Full Matrix Dictionary for a polynomial algebra scenario."""
    op = str(domain_operation or line_type or "").strip()
    if op not in _SUPPORTED_OPS:
        raise ValueError(f"Unsupported polynomial operation: {op!r}")

    rng = random.Random(0 if seed is None else seed)
    constraints = constraints or {}
    prefer_choice = str((constraints or {}).get("presentation_mode") or "").strip() == "single_choice"
    setattr(rng, "_prefer_choice", prefer_choice)
    setattr(rng, "_constraints", constraints)
    builders = {
        "polynomial_descending_power_properties": _build_descending_power_properties,
        "polynomial_param_degree_constraint": _build_param_degree_constraint,
        "polynomial_descending_power_table": _build_descending_power_table,
        "zero_polynomial_find_coeffs": _build_zero_polynomial,
        "polynomial_degree_product_sum": _build_degree_product_sum,
        "polynomial_add_sub": _build_add_sub,
        "polynomial_multiply": _build_multiply,
        "polynomial_product_term_coefficient": _build_product_term_coefficient,
        "polynomial_long_division": _build_long_division,
        "polynomial_synthetic_division": _build_synthetic_division,
        "polynomial_remainder_param_solve": _build_remainder_param_solve,
        "polynomial_shifted_basis_eval": _build_shifted_basis_eval,
        "polynomial_equality_identity": _build_equality_identity,
        "remainder_theorem_evaluate": _build_remainder_theorem,
        "factor_theorem_root_factor": _build_factor_theorem,
        "polynomial_factoring": _build_polynomial_factoring,
        "rational_expression_arithmetic": _build_rational_expression_arithmetic,
        "rational_equation_solve": _build_rational_equation_solve,
    }
    if op not in builders:
        raise ValueError(
            f"Polynomial operation {op!r} is registered but not implemented yet."
        )

    built = builders[op](rng)
    if prefer_choice:
        for _ in range(12):
            distractors = built.get("distractors") or []
            parts = (built.get("answer") or {}).get("parts") or {}
            if distractors and len(parts) <= 1:
                break
            built = builders[op](rng)
    return {
        "givens": built["givens"],
        "answer": built["answer"],
        "distractors": built.get("distractors") or [],
        "explanation_steps": built.get("explanation_steps") or [],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
        },
        "visual_spec": {
            "kind": "none",
            "points": [],
            "lines": [],
        },
        "question_text": built["givens"].get("question_text"),
        "question": built["givens"].get("question_text"),
    }
