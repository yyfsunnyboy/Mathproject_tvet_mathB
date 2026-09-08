# -*- coding: utf-8 -*-
"""Generic source-text routing for B1 §3-3 factoring / rational ops.

No per-example_id branches. Callers inject source_problem_text via constraints.
"""
from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

from core.domain import polynomial_domain as pd


def _src(rng: random.Random) -> str:
    return pd._constraint_source_text(rng)


def _compact(src: str) -> str:
    return pd._compact_src(src)


def _part_count(src: str) -> int:
    compact = _compact(src).replace("（", "(").replace("）", ")")
    n = 0
    for i in range(1, 6):
        if f"({i})" in compact:
            n = i
    return n


def _wants_choice(src: str, rng: random.Random) -> bool:
    compact = _compact(src).replace("（", "(").replace("）", ")")
    return "(A)" in compact or bool(getattr(rng, "_prefer_choice", False))


def _is_prime(n: int) -> bool:
    n = abs(int(n))
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _lin(a: int, b: int) -> dict[int, Fraction]:
    return pd._trim({1: Fraction(a), 0: Fraction(b)})


def _lin_tex(a: int, b: int) -> str:
    return pd.poly_plain(_lin(a, b))


def _pm_root_tex(neg_b: int, disc: int, den: int) -> str:
    return rf"x=\frac{{{neg_b}\pm \sqrt{{{disc}}}}}{{{den}}}"


def _distinct_ints(rng: random.Random, n: int, pool: list[int]) -> list[int]:
    out: list[int] = []
    choices = list(pool)
    rng.shuffle(choices)
    for v in choices:
        if v not in out:
            out.append(v)
        if len(out) >= n:
            break
    while len(out) < n:
        v = int(rng.choice(pool))
        if v not in out:
            out.append(v)
    return out[:n]


# ---------------------------------------------------------------------------
# Factoring
# ---------------------------------------------------------------------------

def _factoring_mode(src: str) -> str:
    if not str(src or "").strip():
        return "default"
    compact = _compact(src)
    if "質數" in src:
        return "prime_value"
    if "長方體" in src and "體積" in src:
        return "cuboid_volume"
    if "長方形" in src and ("y" in compact or "{{y}" in src) and ("周長" in src or "面積" in src):
        return "rect_diff_squares_perim"
    if ("正方形" in src or "長方形" in src) and ("周長" in src or "面積" in src):
        return "area_side_perimeter"
    if "十字" in src or ("a+b+c" in compact and "因式" in src):
        return "cross_param_sum"
    if "何者" in src and "因式" in src:
        return "which_factor"
    n = _part_count(src)
    if n >= 2:
        if "乘法公式" in src:
            if any(tok in compact for tok in ("x^3", "a^3", "x^{3", "a^{3", "x^4")):
                return "formula_cubes_multi"
            if n == 2 and "x^2-" in compact and (
                ")^2-" in compact or "(a+" in compact or "a+b" in compact
            ):
                return "diff_squares_two"
            return "formula_squares_multi"
        return "group_multi"
    if "乘法公式" in src:
        return "formula_single"
    return "single_factor"


def _bundle_parts(
    question: str,
    parts: dict[str, str],
    *,
    extra: dict[str, Any] | None = None,
    distractors: list[str] | None = None,
    explanation: list[str] | None = None,
) -> dict[str, Any]:
    canonical = parts["part_1"] if len(parts) == 1 else "；".join(parts.values())
    value: Any = parts["part_1"] if len(parts) == 1 else parts
    return {
        "givens": {"question_text": question, **(extra or {})},
        "answer": pd._answer_bundle(canonical, parts=parts, value=value),
        "distractors": list(distractors or []),
        "explanation_steps": explanation or ["依因式分解或分式運算化簡。"],
    }


def _build_single_factor(rng: random.Random) -> dict[str, Any]:
    roots = _distinct_ints(rng, rng.choice([2, 2, 3]), [-4, -3, -2, -1, 1, 2, 3, 4])
    lead = int(rng.choice([1, 1, 1, 2, -1]))
    f: dict[int, Fraction] = {0: Fraction(1)}
    for r in roots:
        f = pd._poly_mul(f, {1: Fraction(1), 0: Fraction(-r)})
    f = pd._poly_scalar_mul(f, Fraction(lead))
    factored = pd._factorization_plain(lead, roots)
    question = f"試將多項式${pd.poly_latex(f, name=None)}$因式分解。"
    return _bundle_parts(
        question,
        {"part_1": factored},
        extra={"f": {str(k): pd._frac_plain(v) for k, v in f.items()}, "roots": roots, "lead": lead},
        explanation=["展開因式分解後必須回到原多項式。"],
    )


def _build_group_multi(rng: random.Random, n_parts: int) -> dict[str, Any]:
    n_parts = max(2, min(n_parts, 3))
    p = int(rng.choice([1, 2, 3]))
    # (x+p)(x^2+1)
    f1 = pd._poly_mul(_lin(1, p), {2: Fraction(1), 0: Fraction(1)})
    a1 = f"({pd._linear_factor_plain(-p)})(x^2+1)" if p != 0 else "x(x^2+1)"
    a1 = f"(x+{p})(x^2+1)"
    m = int(rng.choice([2, 3]))
    n = int(rng.choice([1, 1, 2]))
    f2 = pd._poly_mul(_lin(m, -n), {2: Fraction(m * m), 0: Fraction(n * n)})
    a2 = f"({_lin_tex(m, -n)})({_lin_tex(m * m, 0).replace('x', 'x^2')}+{n * n})".replace("x^2^2", "x^2")
    a2 = f"({m}x-{n})({m * m}x^2+{n * n})"
    u = int(rng.choice([-2, -1, 1, 2]))
    k = int(rng.choice([2, 3, 4]))
    # (x-u)^2 - k(x-u) = (x-u)(x-u-k)
    t = pd._linear_factor_plain(u)
    a3 = f"({t})({pd._linear_factor_plain(u + k)})"
    f3_lead = {1: Fraction(1), 0: Fraction(-u)}
    f3 = pd._poly_mul(f3_lead, {1: Fraction(1), 0: Fraction(-(u + k))})
    items = [
        (pd.poly_latex(f1, name=None), a1),
        (pd.poly_latex(f2, name=None), a2),
        (f"{t}^2-{k}({t})", a3),
    ]
    used = items[:n_parts]
    bits = [f"({i + 1})${poly}$" for i, (poly, _) in enumerate(used)]
    parts = {f"part_{i + 1}": ans for i, (_, ans) in enumerate(used)}
    question = "因式分解下列多項式：" + "".join(bits)
    return _bundle_parts(question, parts, extra={"n_parts": n_parts})


def _build_diff_squares_two(rng: random.Random, src: str) -> dict[str, Any]:
    """Two independent difference-of-squares items: x^2-k^2 and (linear)^2-m^2."""
    compact = _compact(src)
    k, m = _distinct_ints(rng, 2, [2, 3, 4, 5, 6])
    inner = "a+b" if "a+b" in compact else f"a+{int(rng.choice([1, 2, 3]))}"
    p1_exp = pd.poly_latex({2: Fraction(1), 0: Fraction(-(k * k))}, name=None)
    p1_ans = f"(x-{k})(x+{k})"
    p2_exp = rf"{{\left( {inner} \right)}}^{{2}}-{m * m}"
    p2_ans = f"({inner}-{m})({inner}+{m})"
    question = (
        "利用乘法公式因式分解下列各式："
        f"(1)${p1_exp}$ (2)${p2_exp}$"
    )
    return _bundle_parts(
        question,
        {"part_1": p1_ans, "part_2": p2_ans},
        extra={"k": k, "m": m, "inner": inner, "n_parts": 2},
        explanation=[
            "平方差：u^2-k^2=(u-k)(u+k)。",
            "兩小題各自因式分解，答案由常數 k、m 推導。",
        ],
    )


def _build_formula_squares_multi(rng: random.Random, n_parts: int) -> dict[str, Any]:
    n_parts = max(2, min(n_parts, 3))
    a = int(rng.choice([1, 2, 3, 4]))
    p1_exp = pd.poly_latex({2: Fraction(1), 1: Fraction(-2 * a), 0: Fraction(a * a)}, name=None)
    p1_ans = f"({pd._linear_factor_plain(a)})^2"
    p, q = int(rng.choice([2, 3, 4])), int(rng.choice([1, 2, 3]))
    p2_exp = f"{p * p}a^2+{2 * p * q}ab+{q * q}b^2"
    p2_ans = f"({p}a+{q}b)^2"
    k = int(rng.choice([3, 4, 5]))
    r = int(rng.choice([2, 3, 4]))
    p3_exp = pd.poly_latex({2: Fraction(k), 0: Fraction(-k * r * r)}, name=None)
    p3_ans = f"{k}(x-{r})(x+{r})"
    s = int(rng.choice([2, 3]))
    p2b_exp = f"(a+{s})^2-9"
    p2b_ans = f"(a+{s}-3)(a+{s}+3)"
    items = [(p1_exp, p1_ans), (p2_exp if n_parts == 3 else p2b_exp, p2_ans if n_parts == 3 else p2b_ans), (p3_exp, p3_ans)]
    used = items[:n_parts]
    bits = [f"({i + 1})${poly}$" for i, (poly, _) in enumerate(used)]
    parts = {f"part_{i + 1}": ans for i, (_, ans) in enumerate(used)}
    question = "利用乘法公式因式分解下列各式：" + "".join(bits)
    return _bundle_parts(question, parts)


def _cube_sum(u: str, v: str) -> str:
    return f"({u}+{v})({u}^2-{u}{v}+{v}^2)"


def _cube_diff(u: str, v: str) -> str:
    return f"({u}-{v})({u}^2+{u}{v}+{v}^2)"


def _build_formula_cubes_multi(rng: random.Random, n_parts: int) -> dict[str, Any]:
    n_parts = max(2, min(n_parts, 3))
    a = int(rng.choice([1, 2, 3]))
    p1 = (pd.poly_latex({3: Fraction(1), 0: Fraction(-(a ** 3))}, name=None), _cube_diff("x", str(a)))
    b = int(rng.choice([2, 3, 4, 5]))
    p2 = (pd.poly_latex({3: Fraction(8), 0: Fraction(b ** 3)}, name=None) if False else (f"{(2)**3}x^3+{b ** 3}", _cube_sum("2x", str(b))))
    c = int(rng.choice([2, 4]))
    # x^4 - c^4
    p3 = (pd.poly_latex({4: Fraction(1), 0: Fraction(-(c ** 4))}, name=None), f"(x-{c})(x+{c})(x^2+{c * c})")
    d = int(rng.choice([2, 3]))
    p2b = (pd.poly_latex({3: Fraction(1), 0: Fraction(d ** 3)}, name=None), _cube_sum("x", str(d)))
    items = [p1, p2 if n_parts >= 3 else p2b, p3]
    used = items[:n_parts]
    bits = [f"({i + 1})${poly}$" for i, (poly, _) in enumerate(used)]
    parts = {f"part_{i + 1}": ans for i, (_, ans) in enumerate(used)}
    question = "利用乘法公式因式分解下列各式：" + "".join(bits)
    return _bundle_parts(question, parts)


def _build_cross_param_sum(rng: random.Random) -> dict[str, Any]:
    a = int(rng.choice([2, 3, 4]))
    r = int(rng.choice([-3, -2, -1, 1, 2, 3]))
    s = int(rng.choice([-3, -2, -1, 1, 2, 3]))
    while s == 0:
        s = int(rng.choice([-3, -2, -1, 1, 2, 3]))
    # (a x + r)(x + s) = a x^2 + (a s + r) x + r s
    poly = pd._poly_mul(_lin(a, r), _lin(1, s))
    total = a + r + s
    question = (
        f"利用十字交乘法因式分解${pd.poly_latex(poly, name=None)}$，"
        f"得其因式分解為$(ax+b)(x+c)$，試求$a+b+c$之值。"
    )
    return pd._scalar_bundle(
        question,
        str(total),
        extra_givens={"a": a, "b": r, "c": s, "sum": total},
        explanation=["由十字交乘法讀出一次因式係數後相加。"],
    )


def _build_prime_value(rng: random.Random, src: str) -> dict[str, Any]:
    k = int(rng.choice([2, 3, 4, 5]))
    x_true = k + 1
    lead = int(rng.choice([2, 3, 4, 8]))
    const = int(rng.choice([-1, 1, 3, 5, 7, 11, 13, 17, 19]))
    p_val = lead * x_true + const
    tries = 0
    while (not _is_prime(p_val)) or p_val <= 1:
        const = int(rng.choice([1, 3, 5, 7, 11, 13, 17, 19, 23]))
        p_val = lead * x_true + const
        tries += 1
        if tries > 20:
            const = 1
            p_val = lead * x_true + const
            if not _is_prime(p_val):
                x_true = 2
                k = 1
                p_val = 5
                lead = 2
                const = 1
            break
    poly = pd._poly_mul(_lin(lead, const), _lin(1, -k))
    question = (
        f"已知$P={pd.poly_plain(poly)}$是質數，x為正整數，"
    )
    if _part_count(src) >= 2:
        question += "試求：(1) x之值。(2) 此質數P。"
        parts = {"part_1": str(x_true), "part_2": str(p_val)}
        return _bundle_parts(question, parts, extra={"x": x_true, "P": p_val, "excluded_composite": True})
    question = f"若x為正整數，且$P={pd.poly_plain(poly)}$是質數，試求此質數。"
    return pd._scalar_bundle(question, str(p_val), extra_givens={"x": x_true, "P": p_val})


def _is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    root = int(n ** 0.5)
    return root * root == n


def _expr_ax_plus_b(a: int, b: int) -> str:
    return pd.poly_plain({1: Fraction(a), 0: Fraction(b)})


def _build_rect_diff_squares_perim(rng: random.Random) -> dict[str, Any]:
    """Rectangle area (kx+m)^2-y^2 → sides kx+m±y → perimeter 4kx+4m."""
    k = int(rng.choice([2, 3, 4]))
    m = int(rng.choice([-2, -1, 1, 2, 3]))
    peri = _expr_ax_plus_b(4 * k, 4 * m)
    area_x = {2: Fraction(k * k), 1: Fraction(2 * k * m), 0: Fraction(m * m)}
    area_tex = pd.poly_plain(area_x) + "-y^{2}"
    length = f"({_expr_ax_plus_b(k, m)}-y)"
    width = f"({_expr_ax_plus_b(k, m)}+y)"
    candidates = [
        _expr_ax_plus_b(2 * k, 2 * m),
        _expr_ax_plus_b(4 * k, -4 * m),
        _expr_ax_plus_b(2 * k, 4 * m),
        _expr_ax_plus_b(4 * k, 2 * m),
        _expr_ax_plus_b(6, 4),
        _expr_ax_plus_b(12, -4),
    ]
    distractors: list[str] = []
    for item in candidates:
        if item == peri or item in distractors:
            continue
        distractors.append(item)
        if len(distractors) >= 3:
            break
    extra_n = 1
    while len(distractors) < 3:
        cand = _expr_ax_plus_b(4 * k + extra_n, 4 * m)
        if cand != peri and cand not in distractors:
            distractors.append(cand)
        extra_n += 1
    question = (
        f"已知一長方形的面積為${area_tex}$平方單位，"
        f"若其長、寬均為$x$、$y$的一次式且$x$、$y$項的係數均為整數，"
        f"則此長方形的周長為？"
    )
    return pd._scalar_bundle(
        question,
        peri,
        distractors=distractors,
        extra_givens={
            "k": k,
            "m": m,
            "length": length,
            "width": width,
            "perimeter": peri,
            "area": area_tex,
        },
        explanation=[
            "先寫成完全平方減 y^2，再用平方差得兩邊長。",
            "周長=2(長+寬)，由係數 k、m 推導，不得寫死常數。",
        ],
    )


def _build_area_side_perimeter(rng: random.Random) -> dict[str, Any]:
    p = int(rng.choice([2, 3, 4]))
    q = int(rng.choice([-5, -3, -2, 1, 2]))
    r = int(rng.choice([2, 3]))
    s = int(rng.choice([-5, -4, -1, 1]))
    area = pd._poly_mul(_lin(p, q), _lin(r, s))
    side = f"({_lin_tex(p, q)})" if abs(p) >= abs(r) else f"({_lin_tex(r, s)})"
    peri = f"4{side}"
    question = (
        f"已知一正方形的邊長為正整數，其面積為${pd.poly_latex(area, name=None)}$平方公分，"
        f"且邊長可寫成x的一次式，試求此正方形的周長。"
    )
    return pd._scalar_bundle(question, peri, extra_givens={"side": side, "perimeter": peri})


def _build_cuboid_volume(rng: random.Random) -> dict[str, Any]:
    e1, e2, e3 = _distinct_ints(rng, 3, [-4, -3, -2, 2, 3, 4, 5])
    a = _lin(1, -e1)
    b = _lin(1, -e2)
    c = _lin(2, e3) if abs(e3) <= 5 else _lin(1, -e3)
    face_ab = pd._poly_mul(a, b)
    face_bc = pd._poly_mul(b, c)
    face_ca = pd._poly_mul(c, a)
    vol = f"({pd.poly_plain(a)})({pd.poly_plain(b)})({pd.poly_plain(c)})"
    question = (
        f"長方體相鄰三面面積分別為${pd.poly_latex(face_ab, name=None)}$、"
        f"${pd.poly_latex(face_bc, name=None)}$、${pd.poly_latex(face_ca, name=None)}$"
        f"平方單位，則此長方體體積為多少立方單位？"
    )
    return pd._scalar_bundle(
        question,
        vol,
        extra_givens={"volume": vol},
        explanation=["相鄰三面分別為兩邊長之積，體積為三邊長之積。"],
    )


def _build_which_factor(rng: random.Random) -> dict[str, Any]:
    """Substitution factoring: [u(x)]^2-(p+q)u(x)+pq, then pick one linear factor of u-p."""
    r = int(rng.choice([-4, -3, -2, 2, 3, 4]))
    s = int(rng.choice([-5, -4, -1, 1, 5, 6]))
    while s in {r, -r}:
        s = int(rng.choice([-6, -5, -1, 1, 5, 6]))
    a = r + s
    p = -r * s
    q = int(rng.choice([2, 5, 7, 11, 13, 15]))
    for step in range(80):
        if q not in {p, -p} and not _is_perfect_square(a * a + 4 * q):
            break
        q = abs(q) + step + 1
    coef = p + q
    const = p * q
    u_plain = pd.poly_plain({2: Fraction(1), 1: Fraction(-a), 0: Fraction(0)})
    u_tex = rf"\left( {u_plain} \right)"
    sign_mid = "-" if coef >= 0 else "+"
    const_sign = "+" if const >= 0 else "-"
    question = (
        f"下列何者為多項式${u_tex}^{{2}}{sign_mid}{abs(coef)}{u_tex}"
        f"{const_sign}{abs(const)}$之因式？"
    )
    true = pd._linear_factor_plain(r)
    also_factor = pd._linear_factor_plain(s)
    forbidden = {true, also_factor}
    pool = [
        pd._linear_factor_plain(-r),
        pd._linear_factor_plain(-s),
        pd._linear_factor_plain(r + 1 if r + 1 not in {r, s} else r + 2),
        pd._linear_factor_plain(r - 1 if r - 1 not in {r, s} else r - 2),
        pd._linear_factor_plain(s + 2 if s + 2 not in {r, s} else s - 2),
        "x",
    ]
    distractors: list[str] = []
    for item in pool:
        if item in forbidden or item in distractors:
            continue
        distractors.append(item)
        if len(distractors) >= 3:
            break
    delta = 3
    while len(distractors) < 3:
        cand = pd._linear_factor_plain(r + delta)
        if cand not in forbidden and cand not in distractors:
            distractors.append(cand)
        delta = -delta if delta > 0 else -delta + 1
    return pd._scalar_bundle(
        question,
        true,
        distractors=distractors[:3],
        extra_givens={
            "u": u_plain,
            "u_shift": a,
            "p": p,
            "q": q,
            "correct_root": r,
            "pair_root": s,
            "also_factor": also_factor,
        },
        explanation=[
            "先令 u 為內層二次式，分解 u^2-(p+q)u+pq。",
            "代回後再分解其中一個二次因式，得到真正的一次因式。",
        ],
    )


def _ensure_choice_distractors(built: dict[str, Any], rng: random.Random, src: str) -> dict[str, Any]:
    if not _wants_choice(src, rng):
        return built
    ans = str((built.get("answer") or {}).get("value") or "").strip()
    uniq: list[str] = []
    for item in list(built.get("distractors") or []):
        text = str(item).strip()
        if text and text != ans and text not in uniq:
            uniq.append(text)
    extras = [
        "x",
        "x-1",
        "x+1",
        "x-2",
        "x+2",
        "2x+1",
        "x^2-1",
        f"{ans}+1" if ans else "x+3",
    ]
    for item in extras:
        if item == ans or item in uniq or not item:
            continue
        uniq.append(item)
        if len(uniq) >= 3:
            break
    n = 3
    while len(uniq) < 3:
        cand = f"x-{n}"
        if cand != ans and cand not in uniq:
            uniq.append(cand)
        n += 1
    built["distractors"] = uniq[:3]
    return built


def build_polynomial_factoring_from_source(rng: random.Random) -> dict[str, Any]:
    src = _src(rng)
    mode = _factoring_mode(src)
    n = _part_count(src)
    if mode == "prime_value":
        built = _build_prime_value(rng, src)
    elif mode == "cuboid_volume":
        built = _build_cuboid_volume(rng)
    elif mode == "rect_diff_squares_perim":
        built = _build_rect_diff_squares_perim(rng)
    elif mode == "area_side_perimeter":
        built = _build_area_side_perimeter(rng)
    elif mode == "cross_param_sum":
        built = _build_cross_param_sum(rng)
        if _wants_choice(src, rng):
            ans = str(built["answer"]["value"])
            built["distractors"] = pd._numeric_distractors(rng, ans)
    elif mode == "which_factor":
        built = _build_which_factor(rng)
    elif mode == "diff_squares_two":
        built = _build_diff_squares_two(rng, src)
    elif mode == "formula_cubes_multi":
        built = _build_formula_cubes_multi(rng, n or 2)
    elif mode == "formula_squares_multi":
        built = _build_formula_squares_multi(rng, n or 2)
    elif mode == "group_multi":
        built = _build_group_multi(rng, n or 2)
    else:
        built = _build_single_factor(rng)
    return _ensure_choice_distractors(built, rng, src)


# ---------------------------------------------------------------------------
# Rational expressions
# ---------------------------------------------------------------------------

def _arith_mode(src: str) -> str:
    if not str(src or "").strip():
        return "default"
    n = _part_count(src)
    if n >= 2:
        return "multi_arith"
    if "\\times" in src or r"\times" in src:
        return "multiply"
    if "\\div" in src or r"\div" in src:
        return "divide"
    return "addsub"


def _frac_tex(num: dict[int, Fraction], den: dict[int, Fraction]) -> str:
    return rf"\dfrac{{{pd.poly_plain(num)}}}{{{pd.poly_plain(den)}}}"


def _build_multiply_rational(rng: random.Random) -> tuple[str, str, dict[str, Any]]:
    a, b, c, d = _distinct_ints(rng, 4, [-4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
    n1 = pd._poly_mul(_lin(1, -a), _lin(1, -b))
    d1 = pd._poly_mul(_lin(1, -c), _lin(1, -d))
    n2 = _lin(1, -d)
    d2 = _lin(1, -a)
    ans = pd._rational_plain(_lin(1, -b), _lin(1, -c))
    tex = rf"{_frac_tex(n1, d1)}\times{_frac_tex(n2, d2)}"
    return tex, ans, {"excluded": [a, c, d]}


def _build_divide_rational(rng: random.Random) -> tuple[str, str, dict[str, Any]]:
    a, b, c, d, e = _distinct_ints(rng, 5, [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
    n1 = pd._poly_mul(_lin(1, -a), _lin(1, -b))
    d1 = pd._poly_mul(_lin(1, -c), _lin(1, -d))
    n2 = _lin(1, -a)
    d2 = _lin(1, -e)
    ans = pd._rational_plain(
        pd._poly_mul(_lin(1, -b), d2),
        pd._poly_mul(_lin(1, -c), _lin(1, -d)),
    )
    tex = rf"{_frac_tex(n1, d1)}\div{_frac_tex(n2, d2)}"
    return tex, ans, {"excluded": sorted({a, c, d, e})}


def _build_addsub_same(rng: random.Random) -> tuple[str, str, dict[str, Any]]:
    p = int(rng.choice([-3, -2, -1, 1, 2, 3]))
    r = int(rng.choice([-4, -2, 1, 3, 5]))
    s = int(rng.choice([-5, -3, 2, 4, 6]))
    while s == r:
        s = int(rng.choice([-5, -3, 2, 4, 6]))
    num = _lin(1, r - s)
    den = _lin(1, -p)
    ans = pd._rational_plain(num, den)
    tex = rf"{_frac_tex(_lin(1, r), den)}-{_frac_tex(_lin(0, s) if False else {0: Fraction(s)}, den)}"
    tex = rf"\dfrac{{{pd._linear_factor_plain(-r) if False else pd.poly_plain(_lin(1, r))}}}{{{pd.poly_plain(den)}}}-\dfrac{{{s}}}{{{pd.poly_plain(den)}}}"
    return tex, ans, {"excluded": [p]}


def _build_addsub_diff(rng: random.Random) -> tuple[str, str, dict[str, Any]]:
    p, q = _distinct_ints(rng, 2, [-4, -3, -2, 1, 2, 3, 4])
    n1, n2 = _lin(1, 1), {0: Fraction(2)}
    den1, den2 = _lin(1, -p), _lin(1, -q)
    num = pd._poly_add(pd._poly_mul(n1, den2), pd._poly_mul(n2, den1))
    den = pd._poly_mul(den1, den2)
    ans = pd._rational_plain(num, den)
    tex = rf"{_frac_tex(n1, den1)}+{_frac_tex(n2, den2)}"
    return tex, ans, {"excluded": [p, q]}


def build_rational_expression_from_source(rng: random.Random) -> dict[str, Any]:
    src = _src(rng)
    mode = _arith_mode(src)
    n = _part_count(src)
    if mode == "multi_arith":
        t1, a1, g1 = _build_multiply_rational(rng) if "\\times" in src else _build_addsub_same(rng)
        t2, a2, g2 = _build_addsub_diff(rng) if n >= 2 else _build_divide_rational(rng)
        if "\\div" in src:
            t1, a1, g1 = _build_divide_rational(rng)
            t2, a2, g2 = _build_addsub_diff(rng)
        elif "\\times" in src:
            t1, a1, g1 = _build_multiply_rational(rng)
            t2, a2, g2 = _build_divide_rational(rng)
        else:
            t1, a1, g1 = _build_addsub_same(rng)
            t2, a2, g2 = _build_addsub_diff(rng)
        question = f"化簡下列各式：(1)${t1}$ (2)${t2}$"
        return _bundle_parts(question, {"part_1": a1, "part_2": a2}, extra={"excluded": g1.get("excluded")})
    if mode == "multiply":
        tex, ans, extra = _build_multiply_rational(rng)
        return pd._scalar_bundle(f"化簡${tex}$。", ans, extra_givens=extra)
    if mode == "divide":
        tex, ans, extra = _build_divide_rational(rng)
        return pd._scalar_bundle(f"化簡${tex}$。", ans, extra_givens=extra)
    tex, ans, extra = _build_addsub_diff(rng)
    return pd._scalar_bundle(f"化簡${tex}$。", ans, extra_givens=extra)


# ---------------------------------------------------------------------------
# Rational equations
# ---------------------------------------------------------------------------

def _eq_mode(src: str) -> str:
    if not str(src or "").strip():
        return "simple"
    compact = _compact(src)
    if "Q(x)" in compact or "Q\\left" in src:
        return "exam_identity_abc"
    if ("a、b" in src or "a,b" in compact or "試求a" in compact) and ("ax+b" in compact or "a x+b" in src):
        return "identity_ab"
    if "(A)" in compact.replace("（", "(") and ("pm" in compact or "\\pm" in src or "sqrt" in compact):
        return "choice_quadratic"
    if "(A)" in compact.replace("（", "("):
        return "choice_linear"
    if _part_count(src) >= 2:
        return "multi_solve"
    if compact.count("frac") >= 2 and src.count("=") >= 1:
        left_plus = src.split("=")[0].count("+") + src.split("=")[0].count("-")
        if left_plus == 0:
            return "proportion"
        return "clear_denoms"
    return "simple"


def _simple_prop_eq(rng: random.Random) -> dict[str, Any]:
    b = int(rng.choice([-3, -2, -1, 1, 2, 3]))
    k = int(rng.choice([2, 3, -2]))
    s = int(rng.choice([-4, -3, -1, 1, 3, 4]))
    while s == b:
        s = int(rng.choice([-4, -3, -1, 1, 3, 4]))
    a = k * (s - b) + s
    question = (
        f"解分式方程式$\\dfrac{{{pd.poly_plain(_lin(1, -a))}}}{{{pd.poly_plain(_lin(1, -b))}}}={k}$。"
    )
    return pd._scalar_bundle(
        question,
        str(s),
        extra_givens={"solution": s, "excluded": [b]},
        explanation=[f"定義域 x≠{b}；去分母後回代，增根須排除。"],
    )


def _proportion_common_num(rng: random.Random) -> dict[str, Any]:
    r = int(rng.choice([-5, -3, -2, 2, 3, 5]))
    p = int(rng.choice([1, 2, 3]))
    q = int(rng.choice([-3, -1, 1, 4]))
    s = q + int(rng.choice([-2, -1, 1, 2]))
    while s == q:
        s += 1
    # (x-r)/(p x+q) = (x-r)/(p x+s) → x=r if r not a pole
    while p * r + q == 0 or p * r + s == 0:
        r += 1
    question = (
        f"解分式方程式$\\dfrac{{{pd.poly_plain(_lin(1, -r))}}}{{{pd.poly_plain(_lin(p, q))}}}"
        f"=\\dfrac{{{pd.poly_plain(_lin(1, -r))}}}{{{pd.poly_plain(_lin(p, s))}}}$。"
    )
    return pd._scalar_bundle(
        question,
        str(r),
        extra_givens={"solution": r, "excluded": []},
        explanation=["若分子相同且分母不同，則分子為 0 的根在定義域內即為解。"],
    )


def _clear_denoms_eq(rng: random.Random) -> dict[str, Any]:
    p, q, c = _distinct_ints(rng, 3, [-4, -3, -2, 1, 2, 3, 4, 5])
    k = p - c - q
    den = q - p
    if den == 0:
        q = p + 3
        den = q - p
        k = p - c - q
    num = c * q - 3 + k * p
    if num % den != 0:
        c = q + 4
        while c == p:
            c += 1
        k = p - c - q
        num = c * q - 3 + k * p
        if num % den != 0:
            # fallback simple: 1/(x-p)+1/(x-q)=something with unique root
            return _simple_prop_eq(rng)
    s_coef = num // den
    r_coef = s_coef + k
    lhs = (
        rf"\dfrac{{3}}{{({pd._linear_factor_plain(p)})({pd._linear_factor_plain(q)})}}"
        rf"+\dfrac{{{pd.poly_plain(_lin(1, r_coef))}}}{{{pd.poly_plain(_lin(1, -q))}}}"
    )
    rhs = rf"\dfrac{{{s_coef}}}{{{pd.poly_plain(_lin(1, -p))}}}"
    question = f"解分式方程式${lhs}={rhs}$。"
    return pd._scalar_bundle(
        question,
        str(c),
        extra_givens={"solution": c, "excluded": [p, q], "extraneous": q},
        explanation=[f"定義域 x≠{p},{q}。去分母後 {q} 為增根，必須排除。"],
    )


def _choice_linear_eq(rng: random.Random) -> dict[str, Any]:
    built = _clear_denoms_eq(rng)
    sol = str((built.get("givens") or {}).get("solution") or built["answer"]["value"])
    excluded = list((built.get("givens") or {}).get("excluded") or [])
    extra_wrong = [str(v) for v in excluded[:2]]
    pool = [str(int(sol) + d) for d in (-3, -2, -1, 1, 2, 3, 4) if str(int(sol) + d) != sol]
    distractors: list[str] = []
    for item in extra_wrong + pool:
        label = f"x={item}"
        if label == f"x={sol}" or label in distractors:
            continue
        distractors.append(label)
        if len(distractors) >= 3:
            break
    while len(distractors) < 3:
        distractors.append(f"x={int(sol) + 10 + len(distractors)}")
    built["answer"] = pd._answer_bundle(f"x={sol}", parts={"part_1": f"x={sol}"}, value=f"x={sol}")
    built["distractors"] = distractors
    built["givens"]["question_text"] = str(built["givens"].get("question_text") or "").replace("解分式方程式", "試求方程式").rstrip("。") + "之解為？"
    return built


def _choice_quadratic_eq(rng: random.Random) -> dict[str, Any]:
    p = int(rng.choice([1, 2, 3, 5]))
    # x/(p-x)=1/x → x^2 + x - p = 0, disc=1+4p
    disc = 1 + 4 * p
    ans = _pm_root_tex(-1, disc, 2)
    d2 = disc + 4 if disc + 4 != disc else disc + 8
    d3 = 1 + 4 * (p + 1)
    if d3 == disc:
        d3 = disc + 12
    distractors = [
        _pm_root_tex(-2, disc, 2),
        _pm_root_tex(-1, d3 if d3 != disc else 3, 2),
        _pm_root_tex(-2, 3 if disc != 3 else 5, 2),
    ]
    seen = {ans}
    uniq = []
    for item in distractors:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    while len(uniq) < 3:
        extra = _pm_root_tex(-1, disc + 8 + len(uniq), 2)
        if extra not in seen:
            seen.add(extra)
            uniq.append(extra)
    question = rf"試求方程式$\dfrac{{x}}{{{p}-x}}=\dfrac{{1}}{{x}}$之解為？"
    # both roots: x≠0, x≠p. For p=1, roots of x^2+x-1: neither 0 nor 1.
    return pd._scalar_bundle(
        question,
        ans,
        distractors=uniq[:3],
        extra_givens={"p": p, "disc": disc, "excluded": [0, p], "both_roots_valid": True},
        explanation=["去分母得二次方程，兩根均須回代確認不使分母為 0。"],
    )


def _exam_identity_abc(rng: random.Random) -> dict[str, Any]:
    """Q=ax+b, f=g determines a,b; rational eq in Q and (x-p); ask a^2+b^2+c^2."""
    a = 1
    b = int(rng.choice([-3, -2, -1, 1, 2]))
    p = int(rng.choice([-3, -2, 2, 3, 4]))
    c = int(rng.choice([-5, -4, -3, 3, 4, 5]))
    r_q = -b  # since a=1
    while c in {p, r_q} or p == r_q:
        c = int(rng.choice([-6, -5, -4, 3, 4, 5, 6]))
        p = int(rng.choice([-4, -3, 2, 3, 5]))
        if p == r_q:
            p = r_q + 3
    k = b - c + p
    m = b * (k + c)
    lead_g = 2 * a - b
    const = -1
    total = a * a + b * b + c * c
    g_tex = pd.poly_plain({2: Fraction(lead_g), 1: Fraction(a), 0: Fraction(const)})
    const_tex = pd._term_latex(Fraction(const), 0, first=False)
    question = (
        r"已知多項式$Q\left( x \right)=ax+b$，"
        r"$f\left( x \right)=\left( 2a-b \right)x^{2}+ax"
        + const_tex
        + r"$，$g\left( x \right)="
        + g_tex
        + r"$，且$f\left( x \right)=g\left( x \right)$。"
        r"若分式方程式$\dfrac{x}{Q\left( x \right)}+\dfrac{"
        + str(k)
        + r"}{x-"
        + str(p)
        + r"}=\dfrac{"
        + str(m)
        + r"}{\left( x-"
        + str(p)
        + r" \right)Q\left( x \right)}$的解為$x=c$，則$a^{2}+b^{2}+c^{2}=$？"
    )
    near = [total + d for d in (-14, -8, -6, 4, 8, 9, 14, 16) if total + d > 0 and total + d != total]
    distractors = [str(v) for v in near[:3]]
    while len(distractors) < 3:
        distractors.append(str(total + 10 + len(distractors)))
    return pd._scalar_bundle(
        question,
        str(total),
        distractors=distractors,
        extra_givens={
            "a": a,
            "b": b,
            "c": c,
            "p": p,
            "excluded": [r_q, p],
            "extraneous": r_q,
            "value": total,
        },
        explanation=[
            "由 f=g 比較係數得 a,b，故 Q 確定。",
            "去分母後回代，使 Q=0 的根必須排除。",
            "最後以合法解 c 計算 a^2+b^2+c^2，不得寫死常數。",
        ],
    )


def _identity_ab(rng: random.Random) -> dict[str, Any]:
    p, q = _distinct_ints(rng, 2, [2, 3, 4, -2, -3])
    r, s = _distinct_ints(rng, 2, [-4, -1, 1, 4, 5])
    A, B = int(rng.choice([1, 2, 3])), int(rng.choice([1, 2, 3]))
    # A/(p x+r) - B/(q x+s) = (ax+b)/((p x+r)(q x+s))
    # num = A(qx+s)-B(px+r) = (Aq-Bp)x + (As-Br)
    a_coef = A * q - B * p
    b_coef = A * s - B * r
    lhs = (
        rf"\dfrac{{{A}}}{{{pd.poly_plain(_lin(p, r))}}}-\dfrac{{{B}}}{{{pd.poly_plain(_lin(q, s))}}}"
    )
    den = pd._poly_mul(_lin(p, r), _lin(q, s))
    question = (
        f"已知${lhs}=\\dfrac{{ax+b}}{{{pd.poly_plain(den)}}}$，試求a、b之值。"
    )
    return _bundle_parts(
        question,
        {"part_1": str(a_coef), "part_2": str(b_coef)},
        extra={"a": a_coef, "b": b_coef},
        explanation=["通分後比較分子係數。"],
    )


def _multi_solve(rng: random.Random) -> dict[str, Any]:
    b1 = _simple_prop_eq(rng)
    b2 = _proportion_common_num(rng)
    s1 = str((b1.get("givens") or {}).get("solution"))
    s2 = str((b2.get("givens") or {}).get("solution"))
    q1 = str(b1["givens"]["question_text"]).replace("解分式方程式", "").strip("。")
    q2 = str(b2["givens"]["question_text"]).replace("解分式方程式", "").strip("。")
    question = f"解下列分式方程式：(1)${q1.strip('$')}$ (2)${q2.strip('$')}$"
    # recover tex only — keep simple
    question = (
        f"解下列分式方程式：(1)${b1['givens']['question_text'].split('$')[1]}$ "
        f"(2)${b2['givens']['question_text'].split('$')[1]}$"
    )
    return _bundle_parts(
        question,
        {"part_1": s1, "part_2": s2},
        extra={"excluded_1": (b1.get("givens") or {}).get("excluded"), "excluded_2": (b2.get("givens") or {}).get("excluded")},
    )


def build_rational_equation_from_source(rng: random.Random) -> dict[str, Any]:
    src = _src(rng)
    mode = _eq_mode(src)
    if mode == "exam_identity_abc":
        return _exam_identity_abc(rng)
    if mode == "identity_ab":
        return _identity_ab(rng)
    if mode == "choice_quadratic":
        return _choice_quadratic_eq(rng)
    if mode == "choice_linear":
        return _choice_linear_eq(rng)
    if mode == "multi_solve":
        return _multi_solve(rng)
    if mode == "proportion":
        return _proportion_common_num(rng)
    if mode == "clear_denoms":
        return _clear_denoms_eq(rng)
    return _simple_prop_eq(rng)
