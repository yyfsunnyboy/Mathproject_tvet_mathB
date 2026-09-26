# -*- coding: utf-8 -*-
"""Sequence & series domain for vocational B3 Chapter 1 (exact arithmetic).

Owns mathematical truth for arithmetic / geometric sequences and partial sums.
Generators call these primitives; they must not re-implement the formulas.

No Chinese stems, no RNG, no DB, no Flask in the pure API surface.
Randomized sampling lives only in ``build_sequence_series_matrix``.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import Any

import sympy as sp

from core.gencode.multipart_stem_contract import (
    build_stem_structure,
    stem_structure_to_question_text,
)

# ── operation keys (problem families) ─────────────────────────────────────────

EXPAND_GENERAL_TERM_FIRST_N = "expand_general_term_first_n"
ARITHMETIC_NTH_FROM_A1_D = "arithmetic_nth_from_a1_d"
ARITHMETIC_D_FROM_A1_AN = "arithmetic_d_from_a1_an"
ARITHMETIC_FROM_TWO_TERMS = "arithmetic_from_two_terms"
ARITHMETIC_INSERT_TERMS = "arithmetic_insert_terms"
ARITHMETIC_MEAN_SOLVE = "arithmetic_mean_solve"
ARITHMETIC_RECURRENCE_GENERAL = "arithmetic_recurrence_general"
ARITHMETIC_SERIES_SUM_GIVEN = "arithmetic_series_sum_given"
ARITHMETIC_SERIES_RECOVER_PARAM = "arithmetic_series_recover_param"
ARITHMETIC_SERIES_FROM_TWO_TERMS = "arithmetic_series_from_two_terms"
ARITHMETIC_SUM_MULTIPLES_RANGE = "arithmetic_sum_multiples_range"
ARITHMETIC_ODD_COUNT_MID_TOTAL = "arithmetic_odd_count_mid_total"
GEOMETRIC_NTH_FROM_A1_R = "geometric_nth_from_a1_r"
GEOMETRIC_R_FROM_A1_AN = "geometric_r_from_a1_an"
GEOMETRIC_FROM_TWO_TERMS = "geometric_from_two_terms"
GEOMETRIC_INSERT_TERMS = "geometric_insert_terms"
GEOMETRIC_MEAN_VALUE = "geometric_mean_value"
GEOMETRIC_MEAN_SOLVE_X = "geometric_mean_solve_x"
GEOMETRIC_RECURRENCE_GENERAL = "geometric_recurrence_general"
GEOMETRIC_SERIES_SUM_GIVEN = "geometric_series_sum_given"
GEOMETRIC_SERIES_RECOVER_PARAM = "geometric_series_recover_param"
GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS = "geometric_ratio_from_shifted_pair_sums"
GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT = "geometric_ratio_from_product_quotient"
ARITHMETIC_INDEX_AND_TOTAL_SUM = "arithmetic_index_and_total_sum"
ARITHMETIC_FIRST_THRESHOLD_CROSSING = "arithmetic_first_threshold_crossing"
GEOMETRIC_FIRST_THRESHOLD_CROSSING = "geometric_first_threshold_crossing"
AP_GP_MIXED_MEAN_MIDDLE = "ap_gp_mixed_mean_middle"
GEOMETRIC_GROWTH_TABLE_CELLS = "geometric_growth_table_cells"

OPS = frozenset(
    {
        EXPAND_GENERAL_TERM_FIRST_N,
        ARITHMETIC_NTH_FROM_A1_D,
        ARITHMETIC_D_FROM_A1_AN,
        ARITHMETIC_FROM_TWO_TERMS,
        ARITHMETIC_INSERT_TERMS,
        ARITHMETIC_MEAN_SOLVE,
        ARITHMETIC_RECURRENCE_GENERAL,
        ARITHMETIC_SERIES_SUM_GIVEN,
        ARITHMETIC_SERIES_RECOVER_PARAM,
        ARITHMETIC_SERIES_FROM_TWO_TERMS,
        ARITHMETIC_SUM_MULTIPLES_RANGE,
        ARITHMETIC_ODD_COUNT_MID_TOTAL,
        GEOMETRIC_NTH_FROM_A1_R,
        GEOMETRIC_R_FROM_A1_AN,
        GEOMETRIC_FROM_TWO_TERMS,
        GEOMETRIC_INSERT_TERMS,
        GEOMETRIC_MEAN_VALUE,
        GEOMETRIC_MEAN_SOLVE_X,
        GEOMETRIC_RECURRENCE_GENERAL,
        GEOMETRIC_SERIES_SUM_GIVEN,
        GEOMETRIC_SERIES_RECOVER_PARAM,
        GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS,
        GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT,
        ARITHMETIC_INDEX_AND_TOTAL_SUM,
        ARITHMETIC_FIRST_THRESHOLD_CROSSING,
        GEOMETRIC_FIRST_THRESHOLD_CROSSING,
        AP_GP_MIXED_MEAN_MIDDLE,
        GEOMETRIC_GROWTH_TABLE_CELLS,
    }
)


# ── exact helpers ─────────────────────────────────────────────────────────────

def to_rational(value: Any) -> Fraction:
    """Convert int/Fraction/str/sympy to exact Fraction when possible."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValueError("invalid_rational:bool")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(sp.nsimplify(value)).limit_denominator()
    expr = sp.simplify(sp.sympify(value))
    if expr.free_symbols:
        raise ValueError(f"non_rational_symbolic:{expr}")
    rat = sp.Rational(expr)
    return Fraction(int(rat.p), int(rat.q))


def canonical_exact(value: Any) -> str:
    from core.gencode.resources.rational_display import (
        compact_float_noise_token,
        fraction_to_plain,
        sanitize_float_noise_in_text,
    )

    if isinstance(value, Fraction):
        return fraction_to_plain(value)
    if isinstance(value, float):
        if abs(value) < 1e-15:
            return "0"
        try:
            return fraction_to_plain(value)
        except Exception:
            return compact_float_noise_token(str(value))
    expr = sp.simplify(sp.sympify(value))
    if isinstance(expr, sp.Float) or getattr(expr, "is_Float", False):
        try:
            expr = sp.nsimplify(expr, rational=True)
        except Exception:
            pass
    if expr == 0:
        return "0"
    return sanitize_float_noise_in_text(sp.sstr(expr, order="lex"))


def _require_index(n: int, *, name: str = "n") -> int:
    n_i = int(n)
    if n_i < 1:
        raise ValueError(f"{name}_must_be_positive_integer")
    return n_i


def _require_distinct_indices(i: int, j: int) -> tuple[int, int]:
    ii, jj = _require_index(i, name="i"), _require_index(j, name="j")
    if ii == jj:
        raise ValueError("indices_must_differ")
    return ii, jj


# ── general term ──────────────────────────────────────────────────────────────

def eval_term_expression(expr: Any, n: int) -> sp.Expr:
    """Evaluate closed-form a(n) exactly (symbol ``n``)."""
    n_i = _require_index(n)
    body = sp.sympify(expr)
    # SymPy may create distinct Symbol('n') instances; replace by name.
    subs_map = {s: n_i for s in body.free_symbols if str(s) == "n"}
    if not subs_map and body.free_symbols:
        # Fallback: single free symbol treated as index.
        if len(body.free_symbols) == 1:
            subs_map = {next(iter(body.free_symbols)): n_i}
    return sp.simplify(body.xreplace(subs_map) if subs_map else body.subs(sp.Symbol("n"), n_i))


def expand_first_terms(expr: Any, n: int) -> list[sp.Expr]:
    n_i = _require_index(n)
    return [eval_term_expression(expr, k) for k in range(1, n_i + 1)]


# ── arithmetic sequence ───────────────────────────────────────────────────────

def arithmetic_nth(a1: Any, d: Any, n: int) -> Fraction:
    """a_n = a1 + (n-1)d."""
    n_i = _require_index(n)
    return to_rational(a1) + (n_i - 1) * to_rational(d)


def arithmetic_diff_from_two(ai: Any, i: int, aj: Any, j: int) -> Fraction:
    """d = (a_j - a_i) / (j - i)."""
    ii, jj = _require_distinct_indices(i, j)
    return (to_rational(aj) - to_rational(ai)) / (jj - ii)


def arithmetic_term_from_two(ai: Any, i: int, aj: Any, j: int, k: int) -> Fraction:
    d = arithmetic_diff_from_two(ai, i, aj, j)
    kk = _require_index(k, name="k")
    return to_rational(ai) + (kk - _require_index(i, name="i")) * d


def arithmetic_insert_diff(A: Any, B: Any, inserted: int) -> Fraction:
    """Insert ``inserted`` numbers between A and B → common difference."""
    k = int(inserted)
    if k < 1:
        raise ValueError("inserted_count_must_be_positive")
    # total terms = inserted + 2; steps between A and B = inserted + 1
    return (to_rational(B) - to_rational(A)) / (k + 1)


def arithmetic_inserted_term(A: Any, B: Any, inserted: int, which: int) -> Fraction:
    """which in 1..inserted: the which-th inserted term."""
    k = int(inserted)
    w = int(which)
    if w < 1 or w > k:
        raise ValueError("which_out_of_inserted_range")
    d = arithmetic_insert_diff(A, B, k)
    return to_rational(A) + w * d


def arithmetic_inserted_sum(A: Any, B: Any, inserted: int) -> Fraction:
    """Sum of the inserted terms only (exclude endpoints)."""
    k = int(inserted)
    if k < 1:
        raise ValueError("inserted_count_must_be_positive")
    # Inserted terms form AP: A+d, ..., A+k*d with d=(B-A)/(k+1)
    # Sum = k*A + d*(1+...+k) = k*A + d*k*(k+1)/2 = k*A + k*(B-A)/2
    aa, bb = to_rational(A), to_rational(B)
    return k * aa + k * (bb - aa) / 2


def arithmetic_mean(a: Any, b: Any) -> Fraction:
    return (to_rational(a) + to_rational(b)) / 2


def solve_linear_arithmetic_mean(
    p_coeff: Any,
    p_const: Any,
    q_coeff: Any,
    q_const: Any,
    mean: Any,
) -> Fraction:
    """Solve ((p_c*x+p0) + (q_c*x+q0)) / 2 = mean for x."""
    pc, p0 = to_rational(p_coeff), to_rational(p_const)
    qc, q0 = to_rational(q_coeff), to_rational(q_const)
    m = to_rational(mean)
    # (pc+qc)x + (p0+q0) = 2m
    left = pc + qc
    if left == 0:
        raise ValueError("arithmetic_mean_equation_degenerate")
    return (2 * m - (p0 + q0)) / left


def arithmetic_partial_sum(a1: Any, d: Any, n: int) -> Fraction:
    """S_n = n/2 * (2*a1 + (n-1)*d)."""
    n_i = _require_index(n)
    a, dd = to_rational(a1), to_rational(d)
    return n_i * (2 * a + (n_i - 1) * dd) / 2


def arithmetic_recover_a1_from_sum(Sn: Any, d: Any, n: int) -> Fraction:
    n_i = _require_index(n)
    # Sn = n/2 * (2 a1 + (n-1)d) → 2 Sn / n = 2 a1 + (n-1)d
    return (2 * to_rational(Sn) / n_i - (n_i - 1) * to_rational(d)) / 2


def arithmetic_recover_d_from_sum(Sn: Any, a1: Any, n: int) -> Fraction:
    n_i = _require_index(n)
    if n_i == 1:
        raise ValueError("cannot_recover_d_from_single_term_sum")
    # 2 Sn / n = 2 a1 + (n-1)d
    return (2 * to_rational(Sn) / n_i - 2 * to_rational(a1)) / (n_i - 1)


def sum_multiples_in_range(lo: int, hi: int, step: int) -> Fraction:
    """Sum of multiples of ``step`` in [lo, hi] inclusive (step > 0)."""
    s = int(step)
    if s <= 0:
        raise ValueError("step_must_be_positive")
    a = int(lo)
    b = int(hi)
    if b < a:
        raise ValueError("range_hi_lt_lo")
    # first multiple >= a, last <= b
    first = a if a % s == 0 else a + (s - a % s)
    last = b - (b % s)
    if first > last:
        return Fraction(0)
    count = (last - first) // s + 1
    return arithmetic_partial_sum(first, s, count)


def arithmetic_total_from_odd_mid(mid: Any, count: int) -> Fraction:
    """Odd-length AP: total sum = mid * count."""
    c = int(count)
    if c < 1 or c % 2 == 0:
        raise ValueError("count_must_be_odd_positive")
    return to_rational(mid) * c


# ── geometric sequence ────────────────────────────────────────────────────────

def geometric_nth(a1: Any, r: Any, n: int) -> sp.Expr:
    """a_n = a1 * r^(n-1) (exact sympy)."""
    n_i = _require_index(n)
    return sp.simplify(sp.sympify(a1) * sp.sympify(r) ** (n_i - 1))


def geometric_ratio_from_two(ai: Any, i: int, aj: Any, j: int) -> sp.Expr:
    """r = (a_j / a_i) ^ (1/(j-i)). Prefer exact rational real root."""
    ii, jj = _require_distinct_indices(i, j)
    ai_v, aj_v = sp.simplify(sp.sympify(ai)), sp.simplify(sp.sympify(aj))
    if ai_v == 0:
        raise ValueError("geometric_zero_term")
    ratio = sp.simplify(aj_v / ai_v)
    exp = jj - ii
    if ratio.is_negative and exp % 2 == 0:
        raise ValueError("geometric_ratio_not_real")

    # Exact rational root via integer_nthroot when ratio is rational.
    try:
        rat = sp.Rational(ratio)
    except Exception:
        rat = None
    if rat is not None:
        sign = -1 if rat < 0 else 1
        abs_rat = abs(rat)
        ok_p, root_p = sp.integer_nthroot(int(abs_rat.p), exp)
        ok_q, root_q = sp.integer_nthroot(int(abs_rat.q), exp)
        if ok_p and ok_q:
            cand = sp.Rational(sign * root_p, root_q)
            if sp.simplify(cand**exp - rat) == 0:
                return sp.simplify(cand)
        # Odd roots of negatives: real_root
        cand = sp.simplify(sign * sp.real_root(abs_rat, exp))
        if sp.simplify(cand**exp - rat) == 0:
            return cand

    # Generic real root fallback
    cand = sp.simplify(sp.real_root(ratio, exp))
    if sp.simplify(cand**exp - ratio) == 0:
        return cand
    # Try negative when odd exponent
    if exp % 2 == 1:
        cand_neg = sp.simplify(-sp.real_root(sp.Abs(ratio), exp))
        if sp.simplify(cand_neg**exp - ratio) == 0:
            return cand_neg
    raise ValueError("geometric_ratio_not_exact")


def geometric_term_from_two(ai: Any, i: int, aj: Any, j: int, k: int) -> sp.Expr:
    r = geometric_ratio_from_two(ai, i, aj, j)
    kk = _require_index(k, name="k")
    ii = _require_index(i, name="i")
    return sp.simplify(sp.sympify(ai) * r ** (kk - ii))


def geometric_insert_ratio(A: Any, B: Any, inserted: int) -> sp.Expr:
    k = int(inserted)
    if k < 1:
        raise ValueError("inserted_count_must_be_positive")
    aa, bb = sp.simplify(sp.sympify(A)), sp.simplify(sp.sympify(B))
    if aa == 0:
        raise ValueError("geometric_zero_endpoint")
    return geometric_ratio_from_two(aa, 1, bb, k + 2)


def geometric_inserted_term(A: Any, B: Any, inserted: int, which: int) -> sp.Expr:
    k = int(inserted)
    w = int(which)
    if w < 1 or w > k:
        raise ValueError("which_out_of_inserted_range")
    r = geometric_insert_ratio(A, B, k)
    return sp.simplify(sp.sympify(A) * r**w)


def geometric_means(a: Any, b: Any) -> tuple[sp.Expr, sp.Expr]:
    """Return (±√(ab)) when real; both signs."""
    prod = sp.simplify(sp.sympify(a) * sp.sympify(b))
    if prod.is_negative:
        raise ValueError("geometric_mean_not_real")
    root = sp.simplify(sp.sqrt(prod))
    return sp.simplify(root), sp.simplify(-root)


def geometric_mean_solve_other(a: Any, mean: Any) -> sp.Expr:
    """If mean is geometric mean of a and x, then x = mean^2 / a."""
    aa = sp.simplify(sp.sympify(a))
    if aa == 0:
        raise ValueError("geometric_zero_endpoint")
    m = sp.simplify(sp.sympify(mean))
    return sp.simplify(m**2 / aa)


def geometric_partial_sum(a1: Any, r: Any, n: int) -> sp.Expr:
    """S_n = n*a1 if r==1 else a1*(1-r^n)/(1-r)."""
    n_i = _require_index(n)
    a, rr = sp.simplify(sp.sympify(a1)), sp.simplify(sp.sympify(r))
    if rr == 1:
        return sp.simplify(n_i * a)
    return sp.simplify(a * (1 - rr**n_i) / (1 - rr))


def geometric_recover_a1_from_sum(Sn: Any, r: Any, n: int) -> sp.Expr:
    n_i = _require_index(n)
    rr = sp.simplify(sp.sympify(r))
    sn = sp.simplify(sp.sympify(Sn))
    if rr == 1:
        return sp.simplify(sn / n_i)
    denom = sp.simplify((1 - rr**n_i) / (1 - rr))
    if denom == 0:
        raise ValueError("geometric_sum_factor_zero")
    return sp.simplify(sn / denom)


def geometric_recover_n_from_sum(Sn: Any, a1: Any, r: Any) -> int:
    """Solve S_n = Sn for positive integer n (exact when unique in reasonable bound)."""
    a, rr, sn = sp.simplify(sp.sympify(a1)), sp.simplify(sp.sympify(r)), sp.simplify(sp.sympify(Sn))
    if a == 0:
        raise ValueError("geometric_zero_first_term")
    if rr == 1:
        n_val = sp.simplify(sn / a)
        if not n_val.is_integer or int(n_val) < 1:
            raise ValueError("geometric_n_not_positive_integer")
        return int(n_val)
    # a (1-r^n)/(1-r) = Sn → 1-r^n = Sn(1-r)/a → r^n = 1 - Sn(1-r)/a
    target = sp.simplify(1 - sn * (1 - rr) / a)
    if target == 0:
        raise ValueError("geometric_n_unsolvable")
    # r^n = target → n = log(target)/log(r)
    for n_try in range(1, 64):
        if sp.simplify(rr**n_try - target) == 0:
            return n_try
    raise ValueError("geometric_n_not_found_in_bound")


# ── display / matrix helpers ──────────────────────────────────────────────────

def _json_value(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _json_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_value(v) for v in obj]
    if isinstance(obj, Fraction):
        return canonical_exact(obj)
    if isinstance(obj, sp.Basic):
        return canonical_exact(obj)
    if isinstance(obj, float):
        return canonical_exact(sp.nsimplify(obj))
    return obj


def _fmt_math(value: Any) -> str:
    return f"\\({canonical_exact(value)}\\)"


def _sample_int(rng: random.Random, lo: int, hi: int, *, nonzero: bool = False) -> int:
    choices = list(range(lo, hi + 1))
    if nonzero:
        choices = [c for c in choices if c != 0]
    return rng.choice(choices)


def _sample_frac(rng: random.Random) -> Fraction:
    return Fraction(_sample_int(rng, -6, 6, nonzero=True), rng.choice([1, 2, 3, 4]))


# ── matrix builders (per operation) ───────────────────────────────────────────

def _matrix_base(
    op: str,
    *,
    question_text: str,
    answer: Any,
    explanation: list[str],
    presentation: str = "short_answer",
    answer_type: str = "expression",
    stem_structure: dict[str, Any] | None = None,
    choices: list[dict[str, Any]] | None = None,
    correct_label: str | None = None,
    validation_facts: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    distractors: list[Any] | None = None,
) -> dict[str, Any]:
    answer_json = _json_value(answer)
    parts: dict[str, Any] = {}
    if isinstance(answer_json, dict) and isinstance(answer_json.get("parts"), dict):
        parts = dict(answer_json["parts"])
        answer_value: Any = {"parts": parts}
    else:
        answer_value = answer_json

    answer_block: dict[str, Any] = {
        "value": answer_value if not isinstance(answer_value, dict) else "",
        "canonical_form": answer_value if not isinstance(answer_value, dict) else "",
        "general_form": answer_value if not isinstance(answer_value, dict) else "",
        "coefficients": [],
        "parts": parts,
        "part_labels": list(parts.keys()) if parts else [],
    }
    if isinstance(answer_value, dict):
        answer_block["canonical_form"] = answer_value
        answer_block["general_form"] = answer_value
        answer_block["value"] = answer_value

    matrix: dict[str, Any] = {
        "domain_key": "sequence.series",
        "domain_operation": op,
        "operation": op,
        "question": question_text,
        "question_text": question_text,
        "answer": answer_block,
        "explanation": explanation,
        "explanation_steps": explanation,
        "distractors": list(distractors or []),
        "givens": _json_value(params or {}),
        "presentation_mode": presentation,
        "answer_type": answer_type,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "answer_type": answer_type,
            "presentation_mode": presentation,
            **(validation_facts or {}),
        },
        "visual_spec": {"kind": "none"},
        "params": _json_value(params or {}),
    }
    if stem_structure:
        matrix["stem_structure"] = stem_structure
    if choices is not None:
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = answer_value
    return matrix


def _build_expand_first_n(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    formulas = payload.get("formulas")
    n = int(payload.get("n") or rng.choice([3, 4]))
    if not formulas:
        catalog = [
            "2*n+1",
            "3*n-1",
            "n**2+1",
            "1/(2*n)",
            "(-1)**n+1",
            "2**n+3",
            "1/(n*(n+1))",
        ]
        k = int(payload.get("count") or rng.choice([2, 3]))
        formulas = rng.sample(catalog, k=min(k, len(catalog)))
    terms_lists = [expand_first_terms(f, n) for f in formulas]
    parts = {f"({i})": ", ".join(canonical_exact(t) for t in terms) for i, terms in enumerate(terms_lists, 1)}
    stem_items = []
    for i, f in enumerate(formulas, 1):
        latex = sp.latex(sp.sympify(f))
        stem_items.append(
            {
                "group_label": f"({i})",
                "text": f"\\(\\langle a_n \\rangle = \\langle {latex} \\rangle\\)",
            }
        )
    stem = build_stem_structure(f"試寫出下列各數列的前{n}項：", stem_items)
    return _matrix_base(
        EXPAND_GENERAL_TERM_FIRST_N,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[f"將 n=1..{n} 代入通項。"],
        answer_type="multi_part",
        stem_structure=stem,
        params={"formulas": formulas, "n": n},
        validation_facts={"multipart_count": len(parts)},
    )


def _build_arith_nth(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -12, 12))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -6, 6, nonzero=True))
    n = int(payload.get("n") or rng.randint(5, 15))
    an = arithmetic_nth(a1, d, n)
    q = (
        f"設一等差數列的首項為{_fmt_math(a1)}，公差為{_fmt_math(d)}，"
        f"試求第{n}項。"
    )
    return _matrix_base(
        ARITHMETIC_NTH_FROM_A1_D,
        question_text=q,
        answer=an,
        explanation=[f"a_n = a_1+(n-1)d = {canonical_exact(an)}"],
        params={"a1": a1, "d": d, "n": n},
    )


def _build_arith_d_from_a1_an(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -10, 10))
    n = int(payload.get("n") or rng.randint(5, 12))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    an = arithmetic_nth(a1, d, n)
    recovered = arithmetic_diff_from_two(a1, 1, an, n)
    q = (
        f"設一等差數列首項為{_fmt_math(a1)}，第{n}項為{_fmt_math(an)}，"
        f"試求其公差。"
    )
    return _matrix_base(
        ARITHMETIC_D_FROM_A1_AN,
        question_text=q,
        answer=recovered,
        explanation=[f"d=(a_n-a_1)/(n-1)={canonical_exact(recovered)}"],
        params={"a1": a1, "an": an, "n": n, "d": recovered},
    )


def _build_arith_from_two(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    locked = str(payload.get("locked_stem") or "").strip()
    if locked == "pitcher_training_days":
        # Recovered 11901: positive increasing daily pitches; (1) d (2) a_k.
        # Prefer clean positive integers; avoid textbook (i=5,j=13,ai=41,aj=73,k=10).
        i = int(payload.get("i") or rng.choice([3, 4, 5, 6, 7]))
        j = int(payload.get("j") or (i + rng.choice([5, 6, 7, 8, 9])))
        k = int(payload.get("k") or rng.choice([8, 9, 10, 12, 15]))
        if k == i or k == j:
            k = j + 2
        d = to_rational(payload["d"]) if "d" in payload else Fraction(rng.choice([3, 4, 5, 6, 8]))
        ai = to_rational(payload["ai"]) if "ai" in payload else Fraction(rng.randint(18, 48))
        aj = ai + (j - i) * d
        if (i, j, int(ai), int(aj), k) == (5, 13, 41, 73, 10) and "ai" not in payload:
            ai = ai + 3
            aj = ai + (j - i) * d
        ak = arithmetic_term_from_two(ai, i, aj, j, k)
        d_out = arithmetic_diff_from_two(ai, i, aj, j)
        parts = {"(1)": canonical_exact(d_out), "(2)": canonical_exact(ak)}
        stem = build_stem_structure(
            (
                f"棒球投手桃太郎從4月1日開始自主訓練，每日投球數呈等差數列形式，且為逐漸增多。"
                f"若4月{i}日投球數為{_fmt_math(ai)}個，4月{j}日投球數為{_fmt_math(aj)}個，請問："
            ),
            [
                {"group_label": "(1)", "text": "他每天增加幾個投球數？"},
                {"group_label": "(2)", "text": f"第{k}天他投了幾個球？"},
            ],
        )
        return _matrix_base(
            ARITHMETIC_FROM_TWO_TERMS,
            question_text=stem_structure_to_question_text(stem),
            answer={"parts": parts},
            explanation=[
                f"d=({canonical_exact(aj)}-{canonical_exact(ai)})/({j}-{i})={canonical_exact(d_out)}",
                f"a_{k}={canonical_exact(ak)}",
            ],
            answer_type="multi_part",
            stem_structure=stem,
            params={"ai": ai, "i": i, "aj": aj, "j": j, "k": k, "d": d_out, "locked_stem": locked},
            validation_facts={
                "multipart_count": 2,
                "locked_stem": locked,
                "source_rescue": "SOURCE_RESCUED_FROM_SCREENSHOT",
            },
        )

    i = int(payload.get("i") or rng.randint(2, 5))
    j = int(payload.get("j") or (i + rng.randint(3, 6)))
    k = int(payload.get("k") or (j + rng.randint(3, 8)))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    ai = to_rational(payload["ai"]) if "ai" in payload else Fraction(_sample_int(rng, -10, 10))
    aj = ai + (j - i) * d
    ak = arithmetic_term_from_two(ai, i, aj, j, k)
    d_out = arithmetic_diff_from_two(ai, i, aj, j)
    parts = {"(1)": canonical_exact(d_out), "(2)": canonical_exact(ak)}
    stem = build_stem_structure(
        f"已知一等差數列 \\(\\langle a_n \\rangle\\) 中，"
        f"\\(a_{{{i}}}={canonical_exact(ai)}\\)，"
        f"\\(a_{{{j}}}={canonical_exact(aj)}\\)，試求：",
        [
            {"group_label": "(1)", "text": "公差 d"},
            {"group_label": "(2)", "text": f"\\(a_{{{k}}}\\) 之值"},
        ],
    )
    return _matrix_base(
        ARITHMETIC_FROM_TWO_TERMS,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[
            f"d=({canonical_exact(aj)}-{canonical_exact(ai)})/({j}-{i})={canonical_exact(d_out)}",
            f"a_{k}={canonical_exact(ak)}",
        ],
        answer_type="multi_part",
        stem_structure=stem,
        params={"ai": ai, "i": i, "aj": aj, "j": j, "k": k, "d": d_out},
        validation_facts={"multipart_count": 2},
    )


def _build_arith_insert(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    A = to_rational(payload["A"]) if "A" in payload else Fraction(_sample_int(rng, -20, 20))
    inserted = int(payload.get("inserted") or rng.choice([4, 5, 9]))
    which = int(payload.get("which") or max(1, inserted // 2))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, 2, 8))
    B = A + (inserted + 1) * d
    mode = str(payload.get("mode") or "term")  # term | sum
    if mode == "sum":
        ans = arithmetic_inserted_sum(A, B, inserted)
        q = (
            f"在{_fmt_math(A)}與{_fmt_math(B)}之間插入{inserted}個數，"
            f"使所成數列成一等差數列，試求所插入各數之和。"
        )
    else:
        ans = arithmetic_inserted_term(A, B, inserted, which)
        total = inserted + 2
        q = (
            f"在{_fmt_math(A)}與{_fmt_math(B)}之間插入{inserted}個數，"
            f"使所成的{total}個數成一等差數列，試求插入的第{which}個數。"
        )
    return _matrix_base(
        ARITHMETIC_INSERT_TERMS,
        question_text=q,
        answer=ans,
        explanation=[f"d={canonical_exact(arithmetic_insert_diff(A, B, inserted))}"],
        params={"A": A, "B": B, "inserted": inserted, "which": which, "mode": mode},
    )


def _build_arith_mean_solve(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    if all(k in payload for k in ("p_coeff", "p_const", "q_coeff", "q_const")):
        pc = to_rational(payload["p_coeff"])
        p0 = to_rational(payload["p_const"])
        qc = to_rational(payload["q_coeff"])
        q0 = to_rational(payload["q_const"])
    else:
        # Guarantee non-degenerate (pc+qc != 0)
        for _ in range(32):
            pc = Fraction(_sample_int(rng, -3, 3, nonzero=True))
            p0 = Fraction(_sample_int(rng, -5, 5))
            qc = Fraction(_sample_int(rng, -3, 3, nonzero=True))
            q0 = Fraction(_sample_int(rng, -5, 5))
            if pc + qc != 0:
                break
        else:
            pc, p0, qc, q0 = Fraction(1), Fraction(2), Fraction(-2), Fraction(5)
    # pick x then mean so equation is consistent
    if "mean" in payload:
        mean = to_rational(payload["mean"])
        x_true = solve_linear_arithmetic_mean(pc, p0, qc, q0, mean)
    else:
        x_seed = to_rational(payload["x"]) if "x" in payload else Fraction(_sample_int(rng, -6, 6))
        mean = arithmetic_mean(pc * x_seed + p0, qc * x_seed + q0)
        x_true = solve_linear_arithmetic_mean(pc, p0, qc, q0, mean)
    left = f"{canonical_exact(pc)}x" if pc != 1 else "x"
    if pc == -1:
        left = "-x"
    elif pc != 1 and pc != -1:
        left = f"{canonical_exact(pc)}x"
    # simpler classroom forms
    p_expr = sp.simplify(pc * sp.symbols("x") + p0)
    q_expr = sp.simplify(qc * sp.symbols("x") + q0)
    q = (
        f"設\\({sp.latex(p_expr)}\\)與\\({sp.latex(q_expr)}\\)的等差中項為"
        f"{_fmt_math(mean)}，試求\\(x\\)的值。"
    )
    return _matrix_base(
        ARITHMETIC_MEAN_SOLVE,
        question_text=q,
        answer=x_true,
        explanation=[f"等差中項：({sp.latex(p_expr)}+{sp.latex(q_expr)})/2={canonical_exact(mean)}"],
        params={"p_coeff": pc, "p_const": p0, "q_coeff": qc, "q_const": q0, "mean": mean},
    )


def _build_arith_recurrence(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    locked = str(payload.get("locked_stem") or "").strip()
    if locked == "bw_tile_white_count":
        # Recovered 11922: fixed tile pattern → a_n = 5n+3 = AP(a1=8,d=5).
        # Only target index varies; text-surrogate replaces diagram.
        a1 = Fraction(8)
        d = Fraction(5)
        target_n = int(payload.get("target_n") or payload.get("k") or rng.choice([4, 6, 7, 8, 10]))
        if target_n == 5 and "target_n" not in payload and "k" not in payload:
            target_n = 6  # avoid exact textbook clone by default
        if target_n < 2:
            target_n = 4
        an = arithmetic_nth(a1, d, target_n)
        assert an == Fraction(5 * target_n + 3)
        parts = {
            "(1)": canonical_exact(a1),
            "(2)": canonical_exact(d),
            "(3)": canonical_exact(an),
        }
        stem = build_stem_structure(
            (
                "用黑、白兩種顏色的正方形地磚依照規律拼成圖形。"
                "第 n 個圖由 3 列地磚組成，中間一列有 n 塊黑色地磚，"
                "黑磚彼此間隔 1 塊白磚，左右兩端各有 1 塊白磚；"
                "上、下兩列全為白磚，每列寬度與中間列相同。"
                "設 \\(a_n\\) 為第 n 個圖中白色地磚總數。請完成："
            ),
            [
                {"group_label": "(1)", "text": "遞迴關係中的首項 \\(a_1\\)"},
                {
                    "group_label": "(2)",
                    "text": "遞迴增量：每增加一圖，白色地磚增加幾塊（即 \\(a_n=a_{n-1}+\\,?\\)）",
                },
                {
                    "group_label": "(3)",
                    "text": f"拼第{target_n}個圖需用到幾塊白色地磚",
                },
            ],
        )
        return _matrix_base(
            ARITHMETIC_RECURRENCE_GENERAL,
            question_text=stem_structure_to_question_text(stem),
            answer={"parts": parts},
            explanation=[
                "總磚數=3(2n+1)，黑磚=n ⇒ a_n=5n+3",
                f"故 a_1={canonical_exact(a1)}，a_n=a_{{n-1}}+{canonical_exact(d)}",
                f"a_{target_n}={canonical_exact(an)}",
            ],
            answer_type="multi_part",
            stem_structure=stem,
            params={
                "a1": a1,
                "d": d,
                "k": target_n,
                "target_n": target_n,
                "locked_stem": locked,
            },
            validation_facts={
                "multipart_count": 3,
                "locked_stem": locked,
                "text_surrogate": True,
                "source_rescue": "SOURCE_RESCUED_FROM_SCREENSHOT",
            },
        )

    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -4, 4, nonzero=True))
    k = int(payload.get("k") or rng.randint(5, 8))
    ak = arithmetic_nth(a1, d, k)
    # general term string
    general = sp.simplify(sp.sympify(a1) + (sp.symbols("n") - 1) * sp.sympify(d))
    parts = {"(1)": canonical_exact(general).replace("n", "n"), "(2)": canonical_exact(ak)}
    # Prefer sympy sstr for general
    parts["(1)"] = sp.sstr(general, order="lex")
    stem = build_stem_structure(
        f"數列\\(\\langle a_n \\rangle\\)之遞迴關係式為"
        f"\\(a_1={canonical_exact(a1)},\\ a_n=a_{{n-1}}+({canonical_exact(d)}),\\ n\\ge 2\\)，試求：",
        [
            {"group_label": "(1)", "text": "一般項 \\(a_n\\)"},
            {"group_label": "(2)", "text": f"\\(a_{{{k}}}\\)"},
        ],
    )
    return _matrix_base(
        ARITHMETIC_RECURRENCE_GENERAL,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[f"a_n={parts['(1)']}", f"a_{k}={canonical_exact(ak)}"],
        answer_type="multi_part",
        stem_structure=stem,
        params={"a1": a1, "d": d, "k": k},
        validation_facts={"multipart_count": 2},
    )


def _build_arith_series_sum(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    locked = str(payload.get("locked_stem") or "").strip()
    if locked == "installment_equal_step_ap":
        # Recovered 11952: monthly payments step,2*step,...,n*step; price = S_n.
        step = (
            to_rational(payload["monthly_base_step"])
            if "monthly_base_step" in payload
            else (
                to_rational(payload["a1"])
                if "a1" in payload
                else Fraction(rng.choice([500, 800, 1200, 1500, 2000, 2500]))
            )
        )
        n = int(payload.get("total_months") or payload.get("n") or rng.choice([8, 9, 10, 12]))
        # avoid exact textbook clone (step=1000, n=10 → 55000)
        if (int(step), n) == (1000, 10) and "monthly_base_step" not in payload and "a1" not in payload:
            step = Fraction(1200)
        a1 = step
        d = step
        sn = arithmetic_partial_sum(a1, d, n)
        a2 = a1 + d
        a3 = a1 + 2 * d
        q = (
            f"某人到電器行購買一個電器商品，老闆讓他無息分期付款，付款方式約定為："
            f"第一個月償還{_fmt_math(a1)}元、第二個月償還{_fmt_math(a2)}元、"
            f"第三個月償還{_fmt_math(a3)}元⋯⋯，按此等差數列付款到第{n}個月可將款項還清，"
            f"請問購買的商品為多少元？"
        )
        return _matrix_base(
            ARITHMETIC_SERIES_SUM_GIVEN,
            question_text=q,
            answer=sn,
            explanation=[
                f"a1=d={canonical_exact(step)}，S_{n}=n(n+1)·step/2={canonical_exact(sn)}"
            ],
            params={
                "a1": a1,
                "d": d,
                "n": n,
                "monthly_base_step": step,
                "total_months": n,
                "total_price": sn,
                "locked_stem": locked,
            },
            validation_facts={
                "locked_stem": locked,
                "source_rescue": "SOURCE_RESCUED_FROM_SCREENSHOT",
            },
        )

    if locked == "triangular_stacking_cups":
        # Recovered 11918: text-surrogate for triangular stack 1+2+...+n (no image).
        n = int(payload.get("n") or payload.get("layers") or rng.choice([8, 10, 12, 14, 16, 18, 20]))
        if n == 15 and "n" not in payload and "layers" not in payload:
            n = 16  # avoid exact textbook layer count when sampling freely
        a1 = Fraction(1)
        d = Fraction(1)
        sn = arithmetic_partial_sum(a1, d, n)
        q = (
            f"競技疊杯（Sport Stacking）依規律堆高成金字塔形："
            f"第1層有1個疊杯，第2層有2個疊杯，第3層有3個疊杯，以此類推。"
            f"若要疊成{n}層，則一共需要幾個疊杯？"
        )
        return _matrix_base(
            ARITHMETIC_SERIES_SUM_GIVEN,
            question_text=q,
            answer=sn,
            explanation=[f"S_n=1+2+\\cdots+{n}=n(n+1)/2={canonical_exact(sn)}"],
            params={
                "a1": a1,
                "d": d,
                "n": n,
                "layers": n,
                "locked_stem": locked,
            },
            validation_facts={
                "locked_stem": locked,
                "text_surrogate": True,
                "source_rescue": "SOURCE_RESCUED_FROM_SCREENSHOT",
            },
        )

    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -10, 15, nonzero=True))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -6, 6, nonzero=True))
    n = int(payload.get("n") or rng.randint(8, 20))
    sn = arithmetic_partial_sum(a1, d, n)
    q = (
        f"試求等差級數{_fmt_math(a1)}+{_fmt_math(a1+d)}+{_fmt_math(a1+2*d)}+\\(\\cdots\\)"
        f"到第{n}項的和。"
    )
    return _matrix_base(
        ARITHMETIC_SERIES_SUM_GIVEN,
        question_text=q,
        answer=sn,
        explanation=[f"S_n=n(2a_1+(n-1)d)/2={canonical_exact(sn)}"],
        params={"a1": a1, "d": d, "n": n},
    )


def _build_arith_series_recover(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    recover = str(payload.get("recover") or rng.choice(["a1", "d"]))
    n = int(payload.get("n") or rng.randint(8, 20))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -8, 12, nonzero=True))
    sn = arithmetic_partial_sum(a1, d, n)
    if recover == "a1":
        ans = arithmetic_recover_a1_from_sum(sn, d, n)
        q = (
            f"設一等差級數前{n}項的和為{_fmt_math(sn)}，公差為{_fmt_math(d)}，"
            f"試求此級數的首項。"
        )
    else:
        ans = arithmetic_recover_d_from_sum(sn, a1, n)
        q = (
            f"設一等差級數的首項為{_fmt_math(a1)}，前{n}項的和為{_fmt_math(sn)}，"
            f"試求此級數的公差。"
        )
    return _matrix_base(
        ARITHMETIC_SERIES_RECOVER_PARAM,
        question_text=q,
        answer=ans,
        explanation=[f"recover {recover} = {canonical_exact(ans)}"],
        params={"a1": a1, "d": d, "n": n, "Sn": sn, "recover": recover},
    )


def _build_arith_series_from_two(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    i = int(payload.get("i") or 5)
    j = int(payload.get("j") or 9)
    n = int(payload.get("n") or 12)
    ai = to_rational(payload["ai"]) if "ai" in payload else Fraction(_sample_int(rng, 5, 30))
    d = to_rational(payload["d"]) if "d" in payload else Fraction(_sample_int(rng, 2, 6))
    aj = ai + (j - i) * d
    a1 = ai - (i - 1) * d
    sn = arithmetic_partial_sum(a1, d, n)
    q = (
        f"設一等差數列的第{i}項為{_fmt_math(ai)}，第{j}項為{_fmt_math(aj)}，"
        f"試求此級數的前{n}項之和。"
    )
    return _matrix_base(
        ARITHMETIC_SERIES_FROM_TWO_TERMS,
        question_text=q,
        answer=sn,
        explanation=[f"d={canonical_exact(d)}, a1={canonical_exact(a1)}, S_{n}={canonical_exact(sn)}"],
        params={"ai": ai, "i": i, "aj": aj, "j": j, "n": n},
    )


def _build_sum_multiples(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    lo = int(payload.get("lo") or 1)
    hi = int(payload.get("hi") or rng.choice([100, 120, 153, 200]))
    step = int(payload.get("step") or rng.choice([3, 4, 5]))
    ans = sum_multiples_in_range(lo, hi, step)
    q = f"試求{lo}到{hi}之間，所有{step}的倍數總和。"
    return _matrix_base(
        ARITHMETIC_SUM_MULTIPLES_RANGE,
        question_text=q,
        answer=ans,
        explanation=[f"首項末項公差構成等差求和={canonical_exact(ans)}"],
        params={"lo": lo, "hi": hi, "step": step},
    )


def _build_odd_mid_total(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    count = int(payload.get("count") or rng.choice([7, 9, 11, 13]))
    if count % 2 == 0:
        count += 1
    mid = to_rational(payload["mid"]) if "mid" in payload else Fraction(_sample_int(rng, 20, 100))
    ans = arithmetic_total_from_odd_mid(mid, count)
    q = (
        f"已知一等差數列共有{count}項，中間一項（第{(count+1)//2}項）為{_fmt_math(mid)}，"
        f"試求此數列所有項之和。"
    )
    return _matrix_base(
        ARITHMETIC_ODD_COUNT_MID_TOTAL,
        question_text=q,
        answer=ans,
        explanation=[f"奇數項等差總和=中項×項數={canonical_exact(ans)}"],
        params={"mid": mid, "count": count},
    )


def _build_geo_nth(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    r = to_rational(payload["r"]) if "r" in payload else Fraction(_sample_int(rng, -3, 3, nonzero=True))
    n = int(payload.get("n") or rng.randint(4, 8))
    an = geometric_nth(a1, r, n)
    q = (
        f"已知一等比數列的首項為{_fmt_math(a1)}，公比為{_fmt_math(r)}，"
        f"試求其第{n}項。"
    )
    return _matrix_base(
        GEOMETRIC_NTH_FROM_A1_R,
        question_text=q,
        answer=an,
        explanation=[f"a_n=a_1 r^{{n-1}}={canonical_exact(an)}"],
        params={"a1": a1, "r": r, "n": n},
    )


def _build_geo_r_from_a1_an(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, -5, 5, nonzero=True))
    r = to_rational(payload["r"]) if "r" in payload else Fraction(_sample_int(rng, -3, 3, nonzero=True))
    n = int(payload.get("n") or rng.choice([4, 5, 6]))
    an = geometric_nth(a1, r, n)
    recovered = geometric_ratio_from_two(a1, 1, an, n)
    q = (
        f"設一等比數列首項為{_fmt_math(a1)}，第{n}項為{_fmt_math(an)}，"
        f"試求其公比。"
    )
    return _matrix_base(
        GEOMETRIC_R_FROM_A1_AN,
        question_text=q,
        answer=recovered,
        explanation=[f"r={canonical_exact(recovered)}"],
        params={"a1": a1, "an": an, "n": n},
    )


def _build_geo_from_two(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    i = int(payload.get("i") or 3)
    j = int(payload.get("j") or 6)
    k = int(payload.get("k") or 9)
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([-2, -1, Fraction(1, 2), 2, 3]))
    ai = to_rational(payload["ai"]) if "ai" in payload else Fraction(_sample_int(rng, 2, 16, nonzero=True))
    # avoid zero path
    aj = geometric_nth(ai, r, j - i + 1)  # treat ai as "first" relative
    # Better: aj = ai * r^(j-i)
    aj = sp.simplify(sp.sympify(ai) * sp.sympify(r) ** (j - i))
    ak = geometric_term_from_two(ai, i, aj, j, k)
    q = (
        f"設等比數列\\(\\langle a_n \\rangle\\)的第{i}項為{_fmt_math(ai)}，"
        f"第{j}項為{_fmt_math(aj)}，試求第{k}項。"
    )
    return _matrix_base(
        GEOMETRIC_FROM_TWO_TERMS,
        question_text=q,
        answer=ak,
        explanation=[f"a_{k}={canonical_exact(ak)}"],
        params={"ai": ai, "i": i, "aj": aj, "j": j, "k": k},
    )


def _build_geo_insert(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    A = to_rational(payload["A"]) if "A" in payload else Fraction(rng.choice([Fraction(3, 8), 2, Fraction(1, 2)]))
    inserted = int(payload.get("inserted") or 4)
    which = int(payload.get("which") or 2)
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([-2, 2, -3, 3]))
    B = sp.simplify(sp.sympify(A) * sp.sympify(r) ** (inserted + 1))
    ans = geometric_inserted_term(A, B, inserted, which)
    q = (
        f"在{_fmt_math(A)}與{_fmt_math(B)}之間插入{inserted}個數，"
        f"使其成一等比數列，試求插入的第{which}個數。"
    )
    return _matrix_base(
        GEOMETRIC_INSERT_TERMS,
        question_text=q,
        answer=ans,
        explanation=[f"r={canonical_exact(geometric_insert_ratio(A, B, inserted))}"],
        params={"A": A, "B": B, "inserted": inserted, "which": which},
    )


def _build_geo_mean(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a = to_rational(payload["a"]) if "a" in payload else Fraction(_sample_int(rng, 1, 16))
    b = to_rational(payload["b"]) if "b" in payload else Fraction(_sample_int(rng, 1, 25))
    pos, neg = geometric_means(a, b)
    # Return both as multipart or joined
    parts = {"(1)": canonical_exact(pos), "(2)": canonical_exact(neg)}
    stem = build_stem_structure(
        f"試求{_fmt_math(a)}與{_fmt_math(b)}的等比中項。",
        [
            {"group_label": "(1)", "text": "正值"},
            {"group_label": "(2)", "text": "負值"},
        ],
    )
    return _matrix_base(
        GEOMETRIC_MEAN_VALUE,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[f"±√(ab)=±{canonical_exact(pos)}"],
        answer_type="multi_part",
        stem_structure=stem,
        params={"a": a, "b": b},
        validation_facts={"multipart_count": 2},
    )


def _build_geo_mean_solve(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a = to_rational(payload["a"]) if "a" in payload else Fraction(_sample_int(rng, 2, 12, nonzero=True))
    x = to_rational(payload["x"]) if "x" in payload else Fraction(_sample_int(rng, 2, 20, nonzero=True))
    # mean^2 = a*x; use positive mean
    mean = sp.simplify(sp.sqrt(sp.sympify(a) * sp.sympify(x)))
    # If mean not nice, force perfect square
    if "mean" in payload:
        mean = sp.simplify(sp.sympify(payload["mean"]))
        x = geometric_mean_solve_other(a, mean)
    else:
        # rebuild with perfect square mean
        m_rat = Fraction(_sample_int(rng, 2, 8))
        mean = sp.sympify(m_rat)
        x = geometric_mean_solve_other(a, mean)
    q = f"已知{_fmt_math(a)}與\\(x\\)的等比中項為\\(\\pm {_fmt_math(mean)}\\)，試求\\(x\\)值。"
    return _matrix_base(
        GEOMETRIC_MEAN_SOLVE_X,
        question_text=q,
        answer=x,
        explanation=[f"x=mean^2/a={canonical_exact(x)}"],
        params={"a": a, "mean": mean, "x": x},
    )


def _build_geo_recurrence(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, 2, 6, nonzero=True))
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([-3, -2, 2, 3, Fraction(-1, 2)]))
    k = int(payload.get("k") or rng.randint(4, 7))
    ak = geometric_nth(a1, r, k)
    general = sp.simplify(sp.sympify(a1) * sp.sympify(r) ** (sp.symbols("n") - 1))
    parts = {"(1)": sp.sstr(general, order="lex"), "(2)": canonical_exact(ak)}
    stem = build_stem_structure(
        f"設數列\\(\\langle a_n \\rangle\\)滿足"
        f"\\(a_1={canonical_exact(a1)},\\ a_n=({canonical_exact(r)})a_{{n-1}},\\ n\\ge 2\\)，試求：",
        [
            {"group_label": "(1)", "text": "一般項 \\(a_n\\)"},
            {"group_label": "(2)", "text": f"\\(a_{{{k}}}\\)"},
        ],
    )
    return _matrix_base(
        GEOMETRIC_RECURRENCE_GENERAL,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=[f"a_n={parts['(1)']}", f"a_{k}={canonical_exact(ak)}"],
        answer_type="multi_part",
        stem_structure=stem,
        params={"a1": a1, "r": r, "k": k},
        validation_facts={"multipart_count": 2},
    )


def _build_geo_series_sum(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(rng.choice([-2, 1, 2, Fraction(1, 2), 3]))
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([-2, Fraction(-1, 2), Fraction(1, 2), 2, -1]))
    n = int(payload.get("n") or rng.randint(6, 12))
    sn = geometric_partial_sum(a1, r, n)
    q = (
        f"試求等比級數{_fmt_math(a1)}+{_fmt_math(a1*r)}+\\(\\cdots\\)"
        f"至第{n}項的和。"
    )
    return _matrix_base(
        GEOMETRIC_SERIES_SUM_GIVEN,
        question_text=q,
        answer=sn,
        explanation=[f"S_n={canonical_exact(sn)}"],
        params={"a1": a1, "r": r, "n": n},
    )


def _build_geo_series_recover(rng: random.Random, payload: dict[str, Any]) -> dict[str, Any]:
    recover = str(payload.get("recover") or rng.choice(["a1", "n"]))
    a1 = to_rational(payload["a1"]) if "a1" in payload else Fraction(_sample_int(rng, 2, 5, nonzero=True))
    r = to_rational(payload["r"]) if "r" in payload else Fraction(rng.choice([2, 3, 5, Fraction(1, 2)]))
    n = int(payload.get("n") or rng.randint(4, 8))
    sn = geometric_partial_sum(a1, r, n)
    if recover == "n":
        ans = geometric_recover_n_from_sum(sn, a1, r)
        q = (
            f"設一等比級數首項為{_fmt_math(a1)}，公比為{_fmt_math(r)}，"
            f"和為{_fmt_math(sn)}，試求其項數。"
        )
    else:
        ans = geometric_recover_a1_from_sum(sn, r, n)
        q = (
            f"設一等比級數公比為{_fmt_math(r)}，前{n}項和為{_fmt_math(sn)}，"
            f"試求其首項。"
        )
    return _matrix_base(
        GEOMETRIC_SERIES_RECOVER_PARAM,
        question_text=q,
        answer=ans,
        explanation=[f"recover {recover} = {canonical_exact(ans)}"],
        params={"a1": a1, "r": r, "n": n, "Sn": sn, "recover": recover},
    )


_BUILDERS = {
    EXPAND_GENERAL_TERM_FIRST_N: _build_expand_first_n,
    ARITHMETIC_NTH_FROM_A1_D: _build_arith_nth,
    ARITHMETIC_D_FROM_A1_AN: _build_arith_d_from_a1_an,
    ARITHMETIC_FROM_TWO_TERMS: _build_arith_from_two,
    ARITHMETIC_INSERT_TERMS: _build_arith_insert,
    ARITHMETIC_MEAN_SOLVE: _build_arith_mean_solve,
    ARITHMETIC_RECURRENCE_GENERAL: _build_arith_recurrence,
    ARITHMETIC_SERIES_SUM_GIVEN: _build_arith_series_sum,
    ARITHMETIC_SERIES_RECOVER_PARAM: _build_arith_series_recover,
    ARITHMETIC_SERIES_FROM_TWO_TERMS: _build_arith_series_from_two,
    ARITHMETIC_SUM_MULTIPLES_RANGE: _build_sum_multiples,
    ARITHMETIC_ODD_COUNT_MID_TOTAL: _build_odd_mid_total,
    GEOMETRIC_NTH_FROM_A1_R: _build_geo_nth,
    GEOMETRIC_R_FROM_A1_AN: _build_geo_r_from_a1_an,
    GEOMETRIC_FROM_TWO_TERMS: _build_geo_from_two,
    GEOMETRIC_INSERT_TERMS: _build_geo_insert,
    GEOMETRIC_MEAN_VALUE: _build_geo_mean,
    GEOMETRIC_MEAN_SOLVE_X: _build_geo_mean_solve,
    GEOMETRIC_RECURRENCE_GENERAL: _build_geo_recurrence,
    GEOMETRIC_SERIES_SUM_GIVEN: _build_geo_series_sum,
    GEOMETRIC_SERIES_RECOVER_PARAM: _build_geo_series_recover,
}


def _mcq_pack_scalar(correct: Any, rng: random.Random) -> tuple[list[dict[str, Any]], str, list[str]]:
    """Build exactly-4 vocational MCQ from a scalar exact answer + derived distractors."""
    correct_s = canonical_exact(correct)
    candidates: list[str] = []
    try:
        base = to_rational(correct)
        for delta in (1, -1, 2, -2, 3, -3, 5, -5, 10, Fraction(1, 2), Fraction(-1, 2)):
            cand = canonical_exact(base + delta)
            if cand != correct_s and cand not in candidates:
                candidates.append(cand)
    except Exception:
        pass
    try:
        expr = sp.simplify(sp.sympify(correct))
        for factor in (2, -1, Fraction(1, 2), 3):
            cand = canonical_exact(sp.simplify(expr * factor))
            if cand != correct_s and cand not in candidates:
                candidates.append(cand)
    except Exception:
        pass
    # pad unique distractors
    pad = 1
    while len(candidates) < 3:
        cand = canonical_exact(pad * 17 + rng.randint(1, 9))
        if cand != correct_s and cand not in candidates:
            candidates.append(cand)
        pad += 1
        if pad > 40:
            break
    distractors = candidates[:3]
    labels = ["A", "B", "C", "D"]
    values = [correct_s] + distractors
    rng.shuffle(values)
    choices = []
    correct_label = "A"
    for lab, val in zip(labels, values):
        choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
        if val == correct_s:
            correct_label = lab
    return choices, correct_label, distractors


def _apply_mcq_if_requested(
    matrix: dict[str, Any],
    *,
    rng: random.Random,
    want_mcq: bool,
) -> dict[str, Any]:
    if not want_mcq:
        return matrix
    if matrix.get("answer_type") == "multi_part":
        return matrix
    ans = matrix.get("answer") or {}
    if not isinstance(ans, dict):
        return matrix
    if ans.get("parts"):
        return matrix
    correct = ans.get("canonical_form")
    if correct in (None, "", {}, []):
        correct = ans.get("value")
    if correct in (None, "", {}, []):
        return matrix
    choices, correct_label, distractors = _mcq_pack_scalar(correct, rng)
    matrix["choices"] = choices
    matrix["correct_label"] = correct_label
    matrix["correct_answer"] = correct_label
    matrix["semantic_answer"] = canonical_exact(correct)
    matrix["presentation_mode"] = "single_choice"
    matrix["answer_type"] = "single_choice"
    matrix["distractors"] = distractors
    facts = dict(matrix.get("validation_facts") or {})
    facts["presentation_mode"] = "single_choice"
    facts["answer_type"] = "single_choice"
    matrix["validation_facts"] = facts
    # Keep semantic value in answer block; label is student-facing correct_answer.
    return matrix


def build_sequence_series_matrix(
    *,
    operation: str | None = None,
    domain_operation: str | None = None,
    constraints: dict[str, Any] | None = None,
    seed: int | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    **data: Any,
) -> dict[str, Any]:
    op = str(operation or domain_operation or "").strip()
    if op not in OPS:
        raise ValueError(f"unsupported_sequence_series_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    raw_constraints = dict(constraints or {})
    want_mcq = str(raw_constraints.get("presentation_mode") or data.get("presentation_mode") or "").strip() in {
        "single_choice",
        "multiple_choice",
    } or str(raw_constraints.get("answer_type") or data.get("answer_type") or "").strip() in {
        "single_choice",
        "choice",
        "choice_label",
    }
    payload = {**raw_constraints, **data}
    for bookkeeping in (
        "skill_id",
        "phase1_classification",
        "v3_induced_spec",
        "classification_status",
        "source_hash",
        "required_capabilities",
        "answer_contract",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "textbook_example_id",
        "source_example_id",
        "classification_source",
        "domain_resolution",
        "exact_task_operation",
    ):
        payload.pop(bookkeeping, None)
    # Allow nested params
    if isinstance(payload.get("params"), dict):
        nested = dict(payload.pop("params"))
        nested.update(payload)
        payload = nested
    builder = _BUILDERS.get(op)
    if builder is None:
        from core.domain.sequence_series_extended import EXTENDED_OPS, build_extended_matrix

        if op in EXTENDED_OPS:
            matrix = build_extended_matrix(op, rng, payload)
        else:
            raise ValueError(f"unsupported_sequence_series_operation:{op}")
    else:
        matrix = builder(rng, payload)
    matrix = _apply_mcq_if_requested(matrix, rng=rng, want_mcq=want_mcq)
    matrix["curriculum_profile"] = curriculum_profile
    matrix["difficulty_profile"] = difficulty_profile
    matrix["seed"] = 0 if seed is None else int(seed)
    return matrix


def validate_sequence_series_matrix(matrix: dict[str, Any]) -> bool:
    if not isinstance(matrix, dict):
        return False
    if matrix.get("domain_key") != "sequence.series":
        return False
    op = str(matrix.get("domain_operation") or matrix.get("operation") or "")
    if op not in OPS:
        return False
    q = str(matrix.get("question_text") or matrix.get("question") or "").strip()
    if not q:
        return False
    for key in ("distractors", "givens", "explanation_steps", "visual_spec", "validation_facts"):
        if key not in matrix:
            return False
    ans = matrix.get("answer")
    if not isinstance(ans, dict) or "canonical_form" not in ans:
        return False
    if not isinstance(matrix.get("validation_facts"), dict):
        return False
    if matrix.get("answer_type") == "single_choice" or (
        isinstance(matrix.get("validation_facts"), dict)
        and matrix["validation_facts"].get("answer_type") == "single_choice"
    ):
        choices = matrix.get("choices")
        if not isinstance(choices, list) or len(choices) != 4:
            return False
        if not matrix.get("correct_label"):
            return False
    return True
