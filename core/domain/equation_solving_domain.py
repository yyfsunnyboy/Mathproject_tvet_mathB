# -*- coding: utf-8 -*-
"""Exact linear / inequality / quadratic primitives for B3 Chapter 2.

Pure math. No Flask, no DB, no randomness inside the solvers.
Generators pick intended solutions first, then render coefficients.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

import sympy as sp

from core.gencode.multipart_stem_contract import (
    build_stem_structure,
    stem_structure_to_question_text,
)

DOMAIN_KEY = "equation.solving"

LINEAR_SOLVE_ISOLATED = "linear_solve_isolated"
LINEAR_SOLVE_GENERAL = "linear_solve_general"
LINEAR_WORD_UNIT_TOTAL = "linear_word_unit_total"
LINEAR_WORD_TWO_CONDITIONS = "linear_word_two_conditions"
LINEAR_WORD_RATIO_SUM = "linear_word_ratio_sum"
LINEAR_WORD_THREE_SHARES = "linear_word_three_shares"
LINEAR_WORD_MARKUP = "linear_word_markup"
LINEAR_WORD_TWO_PLANS = "linear_word_two_plans"
LINEAR_WORD_CLASS_SHARE = "linear_word_class_share"
INEQUALITY_SOLVE = "inequality_solve"
INEQUALITY_WORD_MINIMUM = "inequality_word_minimum"
INEQUALITY_BMI_BOUND = "inequality_bmi_bound"
QUADRATIC_INTEGER_ROOTS = "quadratic_integer_roots"
QUADRATIC_FORMULA_EXACT = "quadratic_formula_exact"
QUADRATIC_PROJECTILE_TIME = "quadratic_projectile_time"
QUADRATIC_ROOT_COUNT = "quadratic_root_count"
QUADRATIC_PARAMETER_EQUAL_ROOTS = "quadratic_parameter_equal_roots"
QUADRATIC_PARAMETER_NO_REAL = "quadratic_parameter_no_real"
QUADRATIC_PARAMETER_TWO_DISTINCT = "quadratic_parameter_two_distinct"
QUADRATIC_VIETA_EXPRESSIONS = "quadratic_vieta_expressions"
QUADRATIC_VIETA_PARAMETER = "quadratic_vieta_parameter"
QUADRATIC_BUILD_FROM_SYMMETRIC = "quadratic_build_from_symmetric"
QUADRATIC_FACTOR_IDENTITY = "quadratic_factor_identity"
QUADRATIC_WORD_PYTHAGORAS = "quadratic_word_pythagoras"
QUADRATIC_WORD_PAIR_COUNT = "quadratic_word_pair_count"
QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION = "quadratic_right_triangle_side_relation"

OPS = frozenset({
    LINEAR_SOLVE_ISOLATED,
    LINEAR_SOLVE_GENERAL,
    LINEAR_WORD_UNIT_TOTAL,
    LINEAR_WORD_TWO_CONDITIONS,
    LINEAR_WORD_RATIO_SUM,
    LINEAR_WORD_THREE_SHARES,
    LINEAR_WORD_MARKUP,
    LINEAR_WORD_TWO_PLANS,
    LINEAR_WORD_CLASS_SHARE,
    INEQUALITY_SOLVE,
    INEQUALITY_WORD_MINIMUM,
    INEQUALITY_BMI_BOUND,
    QUADRATIC_INTEGER_ROOTS,
    QUADRATIC_FORMULA_EXACT,
    QUADRATIC_PROJECTILE_TIME,
    QUADRATIC_ROOT_COUNT,
    QUADRATIC_PARAMETER_EQUAL_ROOTS,
    QUADRATIC_PARAMETER_NO_REAL,
    QUADRATIC_PARAMETER_TWO_DISTINCT,
    QUADRATIC_VIETA_EXPRESSIONS,
    QUADRATIC_VIETA_PARAMETER,
    QUADRATIC_BUILD_FROM_SYMMETRIC,
    QUADRATIC_FACTOR_IDENTITY,
    QUADRATIC_WORD_PYTHAGORAS,
    QUADRATIC_WORD_PAIR_COUNT,
    QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION,
})

# textbook_example_id -> routing. 12013 is a text surrogate of the figure.
SOURCE_SPECS: dict[int, dict[str, Any]] = {
    11971: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_ISOLATED, "parts": 2, "presentation": "short_answer", "source_kind": "example"},
    11972: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_ISOLATED, "parts": 2, "fraction": True, "presentation": "short_answer", "source_kind": "quiz"},
    11973: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 2, "presentation": "short_answer", "source_kind": "example"},
    11974: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 2, "presentation": "short_answer", "source_kind": "quiz"},
    11975: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_UNIT_TOTAL, "presentation": "short_answer", "source_kind": "example", "stem": "fuel"},
    11976: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_UNIT_TOTAL, "presentation": "short_answer", "source_kind": "quiz", "stem": "cafe"},
    11977: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_TWO_CONDITIONS, "presentation": "short_answer", "source_kind": "example", "stem": "tent"},
    11978: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_TWO_CONDITIONS, "presentation": "short_answer", "source_kind": "quiz", "stem": "share"},
    11987: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_ISOLATED, "parts": 4, "presentation": "short_answer", "source_kind": "exercise"},
    11988: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 1, "presentation": "short_answer", "source_kind": "exercise"},
    11989: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 1, "fraction": True, "presentation": "short_answer", "source_kind": "exercise"},
    11990: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_RATIO_SUM, "presentation": "short_answer", "source_kind": "exercise"},
    11991: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_THREE_SHARES, "presentation": "short_answer", "source_kind": "exercise"},
    11992: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_TWO_CONDITIONS, "presentation": "short_answer", "source_kind": "exercise", "stem": "tent"},
    11995: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_MARKUP, "presentation": "short_answer", "source_kind": "exercise"},
    11996: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_TWO_PLANS, "presentation": "short_answer", "source_kind": "exercise"},
    12022: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 1, "presentation": "short_answer", "source_kind": "test"},
    12032: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_SOLVE_GENERAL, "parts": 1, "fraction": True, "presentation": "single_choice", "source_kind": "test"},
    12033: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_CLASS_SHARE, "presentation": "single_choice", "source_kind": "test"},
    12034: {"skill_id": "vh_數學B3_SubSection_2_1_1", "op": LINEAR_WORD_MARKUP, "presentation": "single_choice", "source_kind": "test"},
    11979: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 2, "presentation": "short_answer", "source_kind": "example"},
    11980: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 2, "presentation": "short_answer", "source_kind": "quiz"},
    11981: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_WORD_MINIMUM, "presentation": "short_answer", "source_kind": "example", "stem": "ticket"},
    11982: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_WORD_MINIMUM, "presentation": "short_answer", "source_kind": "quiz", "stem": "save"},
    11986: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_BMI_BOUND, "presentation": "single_choice", "source_kind": "test"},
    11993: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 2, "presentation": "short_answer", "source_kind": "exercise"},
    11994: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_WORD_MINIMUM, "presentation": "short_answer", "source_kind": "exercise", "stem": "ticket"},
    12035: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 1, "presentation": "single_choice", "source_kind": "test"},
    12036: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 1, "fraction": True, "presentation": "single_choice", "source_kind": "test"},
    12037: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_SOLVE, "parts": 1, "fraction": True, "presentation": "single_choice", "source_kind": "test"},
    12038: {"skill_id": "vh_數學B3_SubSection_2_1_2", "op": INEQUALITY_WORD_MINIMUM, "presentation": "single_choice", "source_kind": "test", "stem": "save"},
    11997: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_INTEGER_ROOTS, "parts": 1, "presentation": "short_answer", "source_kind": "example"},
    11998: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_INTEGER_ROOTS, "parts": 1, "presentation": "short_answer", "source_kind": "quiz"},
    11999: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_PROJECTILE_TIME, "presentation": "short_answer", "source_kind": "example"},
    12000: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_PROJECTILE_TIME, "presentation": "short_answer", "source_kind": "quiz"},
    12001: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_FORMULA_EXACT, "parts": 2, "presentation": "short_answer", "source_kind": "example"},
    12002: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_FORMULA_EXACT, "parts": 2, "presentation": "short_answer", "source_kind": "quiz"},
    12012: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_INTEGER_ROOTS, "parts": 2, "presentation": "short_answer", "source_kind": "exercise"},
    12013: {
        "skill_id": "vh_數學B3_SubSection_2_2_2",
        "op": QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION,
        "presentation": "short_answer",
        "source_kind": "exercise",
        "recovery": "SOURCE_RESCUED_FROM_SCREENSHOT",
        "text_surrogate": True,
    },
    12014: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_WORD_PAIR_COUNT, "presentation": "short_answer", "source_kind": "exercise"},
    12015: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_FORMULA_EXACT, "parts": 2, "presentation": "short_answer", "source_kind": "exercise"},
    12023: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_INTEGER_ROOTS, "parts": 1, "presentation": "single_choice", "source_kind": "test"},
    12025: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_WORD_PYTHAGORAS, "presentation": "single_choice", "source_kind": "test"},
    12039: {"skill_id": "vh_數學B3_SubSection_2_2_2", "op": QUADRATIC_INTEGER_ROOTS, "parts": 1, "presentation": "single_choice", "source_kind": "test"},
    12024: {"skill_id": "vh_數學B3_SubSection_2_2_1", "op": QUADRATIC_FACTOR_IDENTITY, "presentation": "single_choice", "source_kind": "test"},
    12003: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_ROOT_COUNT, "parts": 3, "presentation": "short_answer", "source_kind": "example"},
    12004: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_ROOT_COUNT, "parts": 3, "presentation": "short_answer", "source_kind": "quiz"},
    12005: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_EQUAL_ROOTS, "presentation": "short_answer", "source_kind": "example"},
    12006: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_NO_REAL, "presentation": "short_answer", "source_kind": "quiz"},
    12016: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_ROOT_COUNT, "parts": 3, "presentation": "short_answer", "source_kind": "exercise"},
    12020: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_NO_REAL, "presentation": "short_answer", "source_kind": "exercise"},
    12028: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_EQUAL_ROOTS, "presentation": "single_choice", "source_kind": "test"},
    12029: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_NO_REAL, "presentation": "short_answer", "source_kind": "test"},
    12030: {"skill_id": "vh_數學B3_SubSection_2_2_3", "op": QUADRATIC_PARAMETER_TWO_DISTINCT, "presentation": "single_choice", "source_kind": "test"},
    12007: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["sum_sq", "recip_sum"], "presentation": "short_answer", "source_kind": "example"},
    12008: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["sum_sq", "recip_sum"], "presentation": "short_answer", "source_kind": "quiz"},
    12009: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "double", "presentation": "short_answer", "source_kind": "example"},
    12010: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "diff_one", "presentation": "short_answer", "source_kind": "quiz"},
    12011: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "consecutive", "presentation": "single_choice", "source_kind": "test"},
    12017: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["sum_sq", "recip_sq_sum", "two_recip"], "presentation": "short_answer", "source_kind": "exercise"},
    12018: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "consecutive", "presentation": "short_answer", "source_kind": "exercise"},
    12019: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "diff", "presentation": "short_answer", "source_kind": "exercise"},
    12021: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_BUILD_FROM_SYMMETRIC, "presentation": "short_answer", "source_kind": "exercise"},
    12026: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["abs_diff"], "presentation": "single_choice", "source_kind": "test"},
    12027: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["ordered_diff"], "presentation": "single_choice", "source_kind": "test"},
    12031: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["sum_over_prod"], "presentation": "single_choice", "source_kind": "test"},
    12040: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_EXPRESSIONS, "exprs": ["sum_sq"], "presentation": "single_choice", "source_kind": "test"},
    12041: {"skill_id": "vh_數學B3_SubSection_2_2_4", "op": QUADRATIC_VIETA_PARAMETER, "relation": "consecutive_then_sum", "presentation": "single_choice", "source_kind": "test"},
}

VISUAL_UNSUPPORTED_IDS = frozenset()
LEG_GAP_POOL = (2, 3, 4, 5, 7, 8, 9, 10, 12)


def canonical_exact(value: Any) -> str:
    from core.gencode.resources.rational_display import fraction_to_plain

    if isinstance(value, Fraction):
        return fraction_to_plain(value)
    if isinstance(value, sp.Basic):
        return sp.sstr(sp.simplify(value))
    return sp.sstr(sp.simplify(sp.sympify(value)))


def solve_linear(left_a: Fraction, left_b: Fraction, right_a: Fraction, right_b: Fraction) -> Fraction:
    """Solve left_a*x + left_b = right_a*x + right_b. Unique root only."""
    den = left_a - right_a
    if den == 0:
        raise ValueError("linear_not_unique")
    return (right_b - left_b) / den


def solve_inequality(
    left_a: Fraction,
    left_b: Fraction,
    right_a: Fraction,
    right_b: Fraction,
    op: str,
) -> tuple[str, Fraction]:
    """Return (canonical relation, boundary). op in > >= < <=."""
    den = left_a - right_a
    if den == 0:
        raise ValueError("inequality_not_unique")
    boundary = (right_b - left_b) / den
    flip = den < 0
    table = {">": "<", "<": ">", ">=": "<=", "<=": ">="}
    shown = table[op] if flip else op
    return f"x {shown} {canonical_exact(boundary)}", boundary


def quadratic_coeffs(lead: Fraction, r1: Fraction, r2: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """lead*(x-r1)*(x-r2) = a x^2 + b x + c."""
    a = lead
    b = -lead * (r1 + r2)
    c = lead * r1 * r2
    return a, b, c


def discriminant(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    return b * b - 4 * a * c


def quadratic_real_roots(a: Fraction, b: Fraction, c: Fraction) -> tuple[Fraction, ...]:
    """Exact rational roots of a x^2 + b x + c = 0 when the discriminant is a perfect square."""
    if a == 0:
        raise ValueError("not_quadratic")
    disc = discriminant(a, b, c)
    if disc < 0:
        return ()
    if disc == 0:
        return ((-b) / (2 * a),)
    if disc.denominator != 1:
        raise ValueError("quadratic_disc_not_integer")
    radical = sp.sqrt(sp.Integer(int(disc)))
    if not radical.is_integer:
        raise ValueError("quadratic_disc_not_square")
    delta = Fraction(int(radical))
    lo = (-b - delta) / (2 * a)
    hi = (-b + delta) / (2 * a)
    return tuple(sorted((lo, hi)))


def root_count(a: Fraction, b: Fraction, c: Fraction) -> int:
    d = discriminant(a, b, c)
    if d > 0:
        return 2
    if d == 0:
        return 1
    return 0


def vieta(a: Fraction, b: Fraction, c: Fraction) -> tuple[Fraction, Fraction]:
    return -b / a, c / a


def vieta_value(kind: str, a: Fraction, b: Fraction, c: Fraction) -> sp.Expr:
    s, p = vieta(a, b, c)
    d = discriminant(a, b, c)
    if kind == "sum_sq":
        return sp.simplify(s * s - 2 * p)
    if kind == "recip_sum":
        if p == 0:
            raise ValueError("recip_undefined")
        return sp.simplify(s / p)
    if kind == "recip_sq_sum":
        if p == 0:
            raise ValueError("recip_undefined")
        return sp.simplify((s * s - 2 * p) / (p * p))
    if kind == "two_recip":
        if p == 0:
            raise ValueError("recip_undefined")
        return sp.simplify(2 * s / p)
    if kind == "abs_diff":
        return sp.simplify(sp.sqrt(d) / abs(a))
    if kind == "ordered_diff":
        return sp.simplify(sp.sqrt(d) / abs(a))
    if kind == "sum_over_prod":
        if p == 0:
            raise ValueError("prod_zero")
        return sp.simplify(s / p)
    raise ValueError(f"unknown_vieta_kind:{kind}")


def _part_label_map(*names: str) -> dict[str, str]:
    return {f"({index})": name for index, name in enumerate(names, 1)}


def _numbered_labels(count: int, pattern: str = "第{n}題") -> dict[str, str]:
    return {f"({index})": pattern.format(n=index) for index in range(1, count + 1)}


def _tex_lin(a: Fraction, b: Fraction) -> str:
    expr = sp.simplify(a * sp.symbols("x") + b)
    return sp.latex(expr)


def _tex_quad(a: Fraction, b: Fraction, c: Fraction) -> str:
    x = sp.symbols("x")
    return sp.latex(sp.expand(a * x**2 + b * x + c))


def _tex_quad_with_parameter(a: Fraction, b: Fraction, param: str = "k") -> str:
    """Canonical ``a x^2 + b x + param`` with term signs, including ``+k``."""
    x = sp.symbols("x")
    k = sp.symbols(param)
    return sp.latex(sp.expand(a * x**2 + b * x + k))


def _matrix(
    op: str,
    *,
    question_text: str,
    answer: Any,
    explanation: list[str],
    answer_type: str,
    presentation: str,
    params: dict[str, Any],
    stem_structure: dict[str, Any] | None = None,
    choices: list[dict[str, Any]] | None = None,
    correct_label: str | None = None,
    part_label_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    parts: dict[str, Any] = {}
    if isinstance(answer, dict) and isinstance(answer.get("parts"), dict):
        parts = {str(k): canonical_exact(v) if not isinstance(v, str) else v for k, v in answer["parts"].items()}
        answer_value: Any = parts
    else:
        answer_value = canonical_exact(answer) if not isinstance(answer, str) else answer
    labels = dict(part_label_map or {})
    if parts and not labels:
        labels = {key: key for key in parts}
    block = {
        "value": answer_value,
        "canonical_form": answer_value,
        "general_form": answer_value,
        "coefficients": [],
        "parts": parts,
        "part_labels": labels if parts else [],
    }
    matrix: dict[str, Any] = {
        "domain_key": DOMAIN_KEY,
        "domain_operation": op,
        "operation": op,
        "question": question_text,
        "question_text": question_text,
        "answer": block,
        "explanation": explanation,
        "explanation_steps": explanation,
        "distractors": [],
        "givens": params,
        "presentation_mode": presentation,
        "answer_type": answer_type,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "answer_type": answer_type,
            "presentation_mode": presentation,
            "multipart_count": len(parts) if parts else 1,
        },
        "visual_spec": {"kind": "none"},
        "params": params,
    }
    if stem_structure:
        matrix["stem_structure"] = stem_structure
    if choices is not None:
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = answer_value
        matrix["distractors"] = [c["value"] for c in choices if c["label"] != correct_label]
    return matrix


def _pick(rng: random.Random, lo: int, hi: int, *, nonzero: bool = False) -> int:
    vals = [n for n in range(lo, hi + 1) if not nonzero or n != 0]
    return rng.choice(vals)


def _mcq(correct: str, distractors: list[str], rng: random.Random) -> tuple[list[dict[str, Any]], str]:
    pool = []
    seen = {correct}
    for item in distractors:
        if item not in seen:
            pool.append(item)
            seen.add(item)
    pad = 1
    while len(pool) < 3:
        extra = canonical_exact(Fraction(pad))
        if extra not in seen:
            pool.append(extra)
            seen.add(extra)
        pad += 1
        if pad > 30:
            break
    values = [correct] + pool[:3]
    rng.shuffle(values)
    labels = ["A", "B", "C", "D"]
    choices = []
    correct_label = "A"
    for lab, val in zip(labels, values):
        choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
        if val == correct:
            correct_label = lab
    return choices, correct_label


def _coeff_pack(left_a: Fraction, left_b: Fraction, right_a: Fraction, right_b: Fraction) -> dict[str, str]:
    return {
        "left_a": canonical_exact(left_a),
        "left_b": canonical_exact(left_b),
        "right_a": canonical_exact(right_a),
        "right_b": canonical_exact(right_b),
    }


def _isolated_equation(rng: random.Random, *, fraction: bool) -> tuple[str, Fraction, dict[str, str]]:
    x = Fraction(_pick(rng, -8, 8))
    kind = rng.choice(["shift", "scale", "frac"]) if fraction else rng.choice(["shift", "scale"])
    if kind == "shift":
        c = Fraction(_pick(rng, -9, 9, nonzero=True))
        return (
            f"{_tex_lin(Fraction(1), c)} = {canonical_exact(x + c)}",
            x,
            _coeff_pack(Fraction(1), c, Fraction(0), x + c),
        )
    if kind == "scale":
        a = Fraction(_pick(rng, -6, 6, nonzero=True))
        return f"{canonical_exact(a)}x = {canonical_exact(a * x)}", x, _coeff_pack(a, Fraction(0), Fraction(0), a * x)
    den = Fraction(_pick(rng, 2, 7, nonzero=True))
    if rng.random() < 0.5:
        den = -den
    frac = sp.latex(sp.symbols("x") / den)
    return (
        f"{frac} = {canonical_exact(x / den)}",
        x,
        _coeff_pack(Fraction(1, den), Fraction(0), Fraction(0), x / den),
    )


def _general_equation(rng: random.Random, *, fraction: bool) -> tuple[str, Fraction, dict[str, str]]:
    x = Fraction(_pick(rng, -6, 6))
    if fraction:
        a1 = Fraction(_pick(rng, -4, 4, nonzero=True), _pick(rng, 1, 4))
        b1 = Fraction(_pick(rng, -5, 5), _pick(rng, 1, 3))
        a2 = Fraction(_pick(rng, -4, 4), _pick(rng, 1, 3))
        if a1 == a2:
            a2 = a1 + 1
    else:
        a1 = Fraction(_pick(rng, -5, 5, nonzero=True))
        b1 = Fraction(_pick(rng, -8, 8))
        a2 = Fraction(_pick(rng, -5, 5))
        if a1 == a2:
            a2 = a1 + Fraction(2)
    b2 = a1 * x + b1 - a2 * x
    got = solve_linear(a1, b1, a2, b2)
    if got != x:
        raise ValueError("linear_recompute_mismatch")
    text = f"{_tex_lin(a1, b1)} = {_tex_lin(a2, b2)}"
    return text, x, {"a1": canonical_exact(a1), "b1": canonical_exact(b1), "a2": canonical_exact(a2), "b2": canonical_exact(b2)}


def _build_isolated(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec.get("parts") or 2)
    items = []
    parts = {}
    params = []
    for i in range(1, n + 1):
        tex, root, coeffs = _isolated_equation(rng, fraction=bool(spec.get("fraction")))
        items.append({"group_label": f"({i})", "text": f"\\({tex}\\)"})
        parts[f"({i})"] = canonical_exact(root)
        params.append(coeffs)
    stem = build_stem_structure("解下列一元一次方程式：", items)
    return _matrix(
        LINEAR_SOLVE_ISOLATED,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts} if n > 1 else parts["(1)"],
        explanation=["移項後係數不為 0，得唯一解。"],
        answer_type="multi_part" if n > 1 else "expression",
        presentation=spec["presentation"] if n == 1 else "short_answer",
        params={"equations": params},
        stem_structure=stem if n > 1 else None,
        part_label_map=_numbered_labels(n) if n > 1 else None,
    )


def _build_general(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec.get("parts") or 1)
    items = []
    parts = {}
    params = []
    for i in range(1, n + 1):
        tex, root, coeffs = _general_equation(rng, fraction=bool(spec.get("fraction")) or i == n)
        items.append({"group_label": f"({i})", "text": f"\\({tex}\\)"})
        parts[f"({i})"] = canonical_exact(root)
        params.append(coeffs)
    if n == 1:
        q = f"解一元一次方程式\\({items[0]['text'][2:-2]}\\)。"
        answer: Any = parts["(1)"]
        answer_type = "expression"
        stem = None
        presentation = spec["presentation"]
    else:
        stem = build_stem_structure("解下列一元一次方程式：", items)
        q = stem_structure_to_question_text(stem)
        answer = {"parts": parts}
        answer_type = "multi_part"
        presentation = "short_answer"
    matrix = _matrix(
        LINEAR_SOLVE_GENERAL,
        question_text=q,
        answer=answer,
        explanation=["兩邊整理成 ax+b=cx+d 後，係數差不為 0。"],
        answer_type=answer_type,
        presentation=presentation,
        params={"equations": params},
        stem_structure=stem,
        part_label_map=_numbered_labels(n) if n > 1 else None,
    )
    if presentation == "single_choice" and n == 1:
        correct = parts["(1)"]
        wrong = [canonical_exact(Fraction(correct) + d) for d in (1, -1, 2) if canonical_exact(Fraction(correct) + d) != correct]
        choices, label = _mcq(f"x = {correct}" if False else correct, wrong, rng)
        # Student-facing choices show x = value, semantic value stays the number.
        shown = []
        labels = ["A", "B", "C", "D"]
        vals = [correct] + wrong[:3]
        rng.shuffle(vals)
        correct_label = "A"
        for lab, val in zip(labels, vals):
            shown.append({"label": lab, "text": f"\\(x={val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = shown
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["validation_facts"]["presentation_mode"] = "single_choice"
        _ = choices, label
    return matrix


def _build_unit_total(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    qty = _pick(rng, 4, 18)
    unit = _pick(rng, 15, 40) * 5
    fixed = _pick(rng, 2, 12) * 50
    total = unit * qty + fixed
    if spec.get("stem") == "cafe":
        q = (
            f"老師買了一個蛋糕和幾杯咖啡，咖啡每杯{unit}元，蛋糕一個{fixed}元，"
            f"結帳共付了{total}元，請問買了幾杯咖啡？"
        )
    else:
        q = (
            f"加油並洗車，汽油每公升{unit}元，洗車一次{fixed}元。"
            f"若共付了{total}元，請問加了幾公升汽油？"
        )
    answer = Fraction(qty)
    got = solve_linear(Fraction(unit), Fraction(fixed), Fraction(0), Fraction(total))
    if got != answer:
        raise ValueError("unit_total_mismatch")
    return _matrix(
        LINEAR_WORD_UNIT_TOTAL,
        question_text=q,
        answer=answer,
        explanation=[f"{unit}x+{fixed}={total}"],
        answer_type="expression",
        presentation=spec["presentation"],
        params={"unit": unit, "fixed": fixed, "total": total},
    )


def _build_two_conditions(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("stem") == "share":
        s = _pick(rng, 6, 15)
        per_a = _pick(rng, 4, 8)
        rem = _pick(rng, 1, 8)
        per_b = per_a + _pick(rng, 1, 3)
        items = per_a * s + rem
        short = per_b * s - items
        q = (
            f"將一盒物品平均分給學生。如果每人分{per_a}個，則剩{rem}個；"
            f"如果每人分{per_b}個，則不足{short}個。試問學生有幾人？物品有幾個？"
        )
        parts = {"(1)": str(s), "(2)": str(items)}
        params = {"per_a": per_a, "per_b": per_b, "rem": rem, "short": short}
        labels = _part_label_map("學生人數", "物品個數")
    else:
        per_a = _pick(rng, 3, 6)
        extra = _pick(rng, 1, 3)
        rooms = _pick(rng, 8, 16)
        per_b = per_a + 2
        people = per_b * (rooms - extra)
        leftover = people - per_a * rooms
        if leftover <= 0:
            rooms = 8
            per_a, per_b, extra = 5, 7, 2
            people = 7 * (rooms - extra)
            leftover = people - per_a * rooms
        q = (
            f"若每頂帳篷睡{per_a}人，會有{leftover}人沒有帳篷；"
            f"若每頂睡{per_b}人，就會多出{extra}頂帳篷。"
            f"試問帳篷有幾頂？學生有幾人？"
        )
        parts = {"(1)": str(rooms), "(2)": str(people)}
        params = {"per_a": per_a, "per_b": per_b, "leftover": leftover, "extra": extra}
        labels = _part_label_map("帳篷數", "學生數")
    return _matrix(
        LINEAR_WORD_TWO_CONDITIONS,
        question_text=q,
        answer={"parts": parts},
        explanation=["兩種分法寫成同一個總量。"],
        answer_type="multi_part",
        presentation="short_answer",
        params=params,
        part_label_map=labels,
    )


def _finish_scalar(op: str, q: str, answer: Fraction, explanation: list[str], spec: dict[str, Any], params: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    matrix = _matrix(
        op,
        question_text=q,
        answer=answer,
        explanation=explanation,
        answer_type="expression",
        presentation=spec.get("presentation") or "short_answer",
        params=params,
    )
    if spec.get("presentation") == "single_choice":
        correct = canonical_exact(answer)
        wrong = []
        for delta in (1, -1, 2, -2, 5):
            cand = canonical_exact(answer + delta)
            if cand != correct and cand not in wrong:
                wrong.append(cand)
        labels = ["A", "B", "C", "D"]
        vals = [correct] + wrong[:3]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["validation_facts"]["presentation_mode"] = "single_choice"
        matrix["distractors"] = [c["value"] for c in choices if c["label"] != correct_label]
    return matrix


def _build_ratio_sum(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    eng = _pick(rng, 40, 80)
    math = 2 * eng - _pick(rng, 4, 16)
    if math <= 0:
        math = eng + 10
        eng = math
    total = math + eng
    # math = 2*eng - gap, gap = 2*eng - math
    gap = 2 * eng - math
    q = f"數學成績是英文成績的兩倍少{gap}分，且兩科合計{total}分。試問數學、英文分別幾分？"
    parts = {"(1)": str(math), "(2)": str(eng)}
    return _matrix(
        LINEAR_WORD_RATIO_SUM,
        question_text=q,
        answer={"parts": parts},
        explanation=[f"m=2e-{gap}, m+e={total}"],
        answer_type="multi_part",
        presentation="short_answer",
        params={"gap": gap, "total": total},
        part_label_map=_part_label_map("數學", "英文"),
    )


def _build_three(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    sister = _pick(rng, 8, 20) * 100
    big_gap = _pick(rng, 2, 8) * 100
    little_extra = _pick(rng, 1, 6) * 100
    big = 2 * sister - big_gap
    little = sister // 2 + little_extra
    if sister % 2:
        sister += 1
        big = 2 * sister - big_gap
        little = sister // 2 + little_extra
    total = big + sister + little
    q = (
        f"三個孩子每月零用錢總和是{total}元。大哥是二姊的2倍少{big_gap}元，"
        f"小妹是二姊的一半多{little_extra}元。請問大哥、二姊、小妹各是多少？"
    )
    parts = {"(1)": str(big), "(2)": str(sister), "(3)": str(little)}
    return _matrix(
        LINEAR_WORD_THREE_SHARES,
        question_text=q,
        answer={"parts": parts},
        explanation=["以二姊為未知數。"],
        answer_type="multi_part",
        presentation="short_answer",
        params={"total": total, "big_gap": big_gap, "little_extra": little_extra},
        part_label_map=_part_label_map("大哥", "二姊", "小妹"),
    )


def _build_markup(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    cost = _pick(rng, 8, 30) * 100
    rate_num, rate_den = 3, 2  # +50%
    discount_num, discount_den = 4, 5  # 八折
    price = Fraction(cost) * Fraction(rate_num, rate_den) * Fraction(discount_num, discount_den)
    if price.denominator != 1:
        cost = cost * price.denominator
        price = Fraction(cost) * Fraction(rate_num, rate_den) * Fraction(discount_num, discount_den)
    q = (
        f"商品以進貨成本提高50%當作定價，再以定價的八折出售。"
        f"若售價為{int(price)}元，請問進貨成本是多少元？"
    )
    return _finish_scalar(
        LINEAR_WORD_MARKUP, q, Fraction(cost), ["售價 = 成本 × 1.5 × 0.8"], spec,
        {"cost_price": int(price)}, rng,
    )


def _build_plans(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    # Plan A: fee_a includes first included minutes, then rate_a
    included = _pick(rng, 40, 80)
    fee_a = _pick(rng, 4, 12) * 50
    rate_a = Fraction(_pick(rng, 2, 4))
    fee_b = _pick(rng, 2, 8) * 50
    rate_b = Fraction(rate_a.numerator - 1 if rate_a > 1 else 1, 2)
    if rate_a == rate_b:
        rate_b = rate_a - Fraction(1, 2)
    minutes = included + _pick(rng, 20, 80)
    cost_a = fee_a + rate_a * (minutes - included)
    # set fee_b so costs equal: fee_b + rate_b*minutes = cost_a
    fee_b_exact = cost_a - rate_b * minutes
    if fee_b_exact <= 0 or fee_b_exact.denominator != 1:
        rate_b = Fraction(1)
        rate_a = Fraction(2)
        fee_a = 200
        included = 100
        minutes = 180
        cost_a = fee_a + rate_a * (minutes - included)
        fee_b_exact = cost_a - rate_b * minutes
    q = (
        f"甲方案月租{int(fee_a)}元，含{included}分鐘，超過每分鐘{canonical_exact(rate_a)}元。"
        f"乙方案月租{int(fee_b_exact)}元，每分鐘{canonical_exact(rate_b)}元。"
        f"通話幾分鐘時兩家收費相同？"
    )
    got = solve_linear(rate_a, Fraction(fee_a) - rate_a * included, rate_b, Fraction(fee_b_exact))
    if got != Fraction(minutes):
        # equation only valid when minutes > included; recompute display from solver
        minutes = int(got)
    return _finish_scalar(
        LINEAR_WORD_TWO_PLANS, q, Fraction(minutes), ["令兩方案費用相等"], spec,
        {
            "included": included,
            "fee_a": int(fee_a),
            "rate_a": canonical_exact(rate_a),
            "fee_b": canonical_exact(Fraction(fee_b_exact)),
            "rate_b": canonical_exact(rate_b),
        }, rng,
    )


def _build_class(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    # fail = n/3, mid = n/2 + extra, high = h, sum = n
    extra = _pick(rng, 1, 4)
    high = _pick(rng, 3, 8)
    # n/3 + n/2 + extra + high = n => n/6 = extra+high => n = 6*(extra+high)
    n = 6 * (extra + high)
    fail = n // 3
    q = (
        f"不及格人數占全班的\\(\\frac{{1}}{{3}}\\)，及格但不到80分的人數占全班的一半又多{extra}人，"
        f"80分以上有{high}人。請問不及格人數有幾人？"
    )
    return _finish_scalar(
        LINEAR_WORD_CLASS_SHARE, q, Fraction(fail), ["n/3+n/2+extra+high=n"], spec,
        {"extra": extra, "high": high}, rng,
    )


def _one_inequality(rng: random.Random, *, fraction: bool) -> tuple[str, str, dict[str, Any]]:
    x_bound = Fraction(_pick(rng, -6, 8), _pick(rng, 1, 3) if fraction else 1)
    a1 = Fraction(_pick(rng, -5, 5, nonzero=True), 2 if fraction and rng.random() < 0.5 else 1)
    b1 = Fraction(_pick(rng, -6, 6), 1)
    a2 = Fraction(_pick(rng, -4, 4), 1)
    if a1 == a2:
        a2 = a1 + 1
    op = rng.choice([">", ">=", "<", "<="])
    # left(boundary) ? right(boundary) is the boundary equality; relation uses op on the solution side
    b2 = a1 * x_bound + b1 - a2 * x_bound
    shown, boundary = solve_inequality(a1, b1, a2, b2, op)
    if boundary != x_bound:
        raise ValueError("inequality_boundary_mismatch")
    tex = f"{_tex_lin(a1, b1)} {op} {_tex_lin(a2, b2)}"
    return tex, shown, {
        "left_a": canonical_exact(a1),
        "left_b": canonical_exact(b1),
        "right_a": canonical_exact(a2),
        "right_b": canonical_exact(b2),
        "op": op,
    }


def _build_inequality(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec.get("parts") or 1)
    items = []
    parts = {}
    params = []
    for i in range(1, n + 1):
        tex, shown, meta = _one_inequality(rng, fraction=bool(spec.get("fraction")) or i > 1)
        items.append({"group_label": f"({i})", "text": f"\\({tex}\\)"})
        parts[f"({i})"] = shown
        params.append(meta)
    if n == 1:
        q = f"解不等式\\({items[0]['text'][2:-2]}\\)，其解的範圍為"
        answer: Any = parts["(1)"]
        answer_type = "expression"
        stem = None
    else:
        stem = build_stem_structure("解下列不等式：", items)
        q = stem_structure_to_question_text(stem)
        answer = {"parts": parts}
        answer_type = "multi_part"
    matrix = _matrix(
        INEQUALITY_SOLVE,
        question_text=q,
        answer=answer,
        explanation=["移項時若係數為負，不等號方向改變。"],
        answer_type=answer_type,
        presentation="short_answer" if n > 1 else spec["presentation"],
        params={"relations": params},
        stem_structure=stem,
        part_label_map=_numbered_labels(n) if n > 1 else None,
    )
    if spec["presentation"] == "single_choice" and n == 1:
        correct = parts["(1)"]
        flipped = correct.replace(">", "<").replace("<", ">") if ">=" not in correct and "<=" not in correct else (
            correct.replace(">=", "<=").replace("<=", ">=") if ">=" in correct else correct.replace("<=", ">=")
        )
        # The replace above is not reliable for both symbols. Build explicit opposite.
        if ">=" in correct:
            opposite = correct.replace(">=", "<=")
        elif "<=" in correct:
            opposite = correct.replace("<=", ">=")
        elif ">" in correct:
            opposite = correct.replace(">", "<")
        else:
            opposite = correct.replace("<", ">")
        alt_boundary = correct
        choices_vals = [correct, opposite]
        # two more by shifting boundary text is hard; add nearby integers as relations with same op
        op_token = ">=" if ">=" in correct else "<=" if "<=" in correct else ">" if ">" in correct else "<"
        _shown, boundary_value = solve_inequality(
            Fraction(params[0]["left_a"]),
            Fraction(params[0]["left_b"]),
            Fraction(params[0]["right_a"]),
            Fraction(params[0]["right_b"]),
            params[0]["op"],
        )
        boundary = canonical_exact(boundary_value)
        for delta in (1, -1):
            choices_vals.append(f"x {op_token} {canonical_exact(Fraction(boundary) + delta)}")
        uniq = []
        for v in choices_vals:
            if v not in uniq:
                uniq.append(v)
        while len(uniq) < 4:
            uniq.append(f"x {op_token} {canonical_exact(Fraction(boundary) + len(uniq))}")
        labels = ["A", "B", "C", "D"]
        vals = uniq[:4]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["distractors"] = [c["value"] for c in choices if c["value"] != correct]
        _ = flipped, alt_boundary
    return matrix


def _build_minimum(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    if spec.get("stem") == "save":
        price = _pick(rng, 10, 40) * 100
        have = _pick(rng, 2, 12) * 100
        daily = _pick(rng, 2, 8) * 25
        if have >= price:
            have = price // 2
        need = price - have
        days = (need + daily - 1) // daily
        q = (
            f"想買{price}元的物品，已有存款{have}元，每天再存{daily}元。"
            f"至少要存幾天才足夠？"
        )
        answer = Fraction(days)
        params = {"price": price, "have": have, "daily": daily}
    else:
        single = _pick(rng, 4, 12) * 50
        group_price = single * 4 // 5
        if group_price * 5 != single * 4:
            group_price = single - 50
        threshold = _pick(rng, 15, 30)
        # n * single > threshold * group_price, n < threshold, minimal such n
        # n > threshold * group_price / single
        bound = Fraction(threshold * group_price, single)
        n = int(bound) + 1
        if n >= threshold:
            group_price = single - 100
            bound = Fraction(threshold * group_price, single)
            n = int(bound) + 1
        q = (
            f"門票每張{single}元，{threshold}人以上團體票每張{group_price}元。"
            f"班級人數不足{threshold}人，但買{threshold}張團體票比較便宜。班級最少有多少人？"
        )
        answer = Fraction(n)
        params = {"single": single, "group": group_price, "threshold": threshold}
    return _finish_scalar(INEQUALITY_WORD_MINIMUM, q, answer, ["由嚴格不等決定最小整數。"], spec, params, rng)


def _build_bmi(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    # w - lose = high * h^2, choose h so product is integer.
    h = Fraction(3, 2)  # 1.5 m
    high = Fraction(_pick(rng, 20, 24))
    lose = _pick(rng, 2, 6)
    current = high * h * h + lose
    if current.denominator != 1:
        high = Fraction(24)
        current = high * h * h + lose
    q = (
        f"身高{canonical_exact(h)}公尺，BMI 要不高於{canonical_exact(high)}才符合體位上限。"
        f"必須再減{lose}公斤才會符合。現在體重可能是幾公斤？"
    )
    return _finish_scalar(
        INEQUALITY_BMI_BOUND, q, current, ["現重 = 上限BMI × 身高平方 + 需減公斤"], spec,
        {"height": canonical_exact(h), "high": canonical_exact(high), "lose": lose},
        rng,
    )


def _integer_quadratic(rng: random.Random) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
    r1 = Fraction(_pick(rng, -6, 6))
    r2 = Fraction(_pick(rng, -6, 6))
    if r1 == r2 and rng.random() < 0.7:
        r2 = r1 + _pick(rng, 1, 4, nonzero=True)
    lead = Fraction(_pick(rng, 1, 3))
    a, b, c = quadratic_coeffs(lead, r1, r2)
    return lead, r1, r2, b, c


def _ordered_roots(r1: Fraction, r2: Fraction) -> tuple[Fraction, Fraction]:
    a, b = (r1, r2) if r1 <= r2 else (r2, r1)
    return a, b


def _root_pair_text(r1: Fraction, r2: Fraction) -> str:
    a, b = _ordered_roots(r1, r2)
    if a == b:
        return canonical_exact(a)
    return f"{canonical_exact(a)} 或 {canonical_exact(b)}"


def _build_integer_roots(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec.get("parts") or 1)
    mcq = spec.get("presentation") == "single_choice" and n == 1
    items = []
    parts = {}
    params = []
    label_names: list[str] = []
    part_i = 1
    for i in range(1, n + 1):
        lead, r1, r2, b, c = _integer_quadratic(rng)
        a = lead
        tex = _tex_quad(a, b, c)
        lo, hi = _ordered_roots(r1, r2)
        if mcq:
            items.append({"group_label": f"({i})", "text": f"\\({tex}=0\\)"})
            parts["(1)"] = _root_pair_text(lo, hi)
        else:
            items.append({"group_label": f"({i})", "text": f"\\({tex}=0\\)"})
            parts[f"({part_i})"] = canonical_exact(lo)
            parts[f"({part_i+1})"] = canonical_exact(hi)
            if n == 1:
                label_names.extend(["較小根", "較大根"])
            else:
                label_names.extend([f"第{i}式較小根", f"第{i}式較大根"])
            part_i += 2
        params.append({"a": canonical_exact(a), "b": canonical_exact(b), "c": canonical_exact(c)})
    if mcq:
        q = f"試求方程式\\({items[0]['text'][2:-2]}\\)的解。"
        answer: Any = parts["(1)"]
        answer_type = "expression"
        stem = None
        presentation = "single_choice"
    elif len(parts) == 2 and n == 1:
        stem = build_stem_structure("試求方程式的兩根（由小到大）：", items)
        q = stem_structure_to_question_text(stem)
        answer = {"parts": parts}
        answer_type = "multi_part"
        presentation = "short_answer"
    else:
        stem = build_stem_structure("解下列方程式，每式由小到大寫出兩根：", items)
        q = stem_structure_to_question_text(stem)
        answer = {"parts": parts}
        answer_type = "multi_part"
        presentation = "short_answer"
    matrix = _matrix(
        QUADRATIC_INTEGER_ROOTS,
        question_text=q,
        answer=answer,
        explanation=["先選整數根再展開。"],
        answer_type=answer_type,
        presentation=presentation,
        params={"equations": params},
        stem_structure=stem,
        part_label_map=_part_label_map(*label_names) if label_names else None,
    )
    if mcq:
        correct = parts["(1)"]
        roots = sp.solve(
            sp.Eq(
                Fraction(params[0]["a"]) * sp.symbols("x") ** 2
                + Fraction(params[0]["b"]) * sp.symbols("x")
                + Fraction(params[0]["c"]),
                0,
            ),
            sp.symbols("x"),
        )
        r1, r2 = (Fraction(roots[0]), Fraction(roots[0])) if len(roots) == 1 else _ordered_roots(Fraction(roots[0]), Fraction(roots[1]))
        distractors = [
            _root_pair_text(-r1, r2),
            _root_pair_text(r1, -r2),
            _root_pair_text(-r1, -r2),
        ]
        labels = ["A", "B", "C", "D"]
        vals = [correct]
        for d in distractors:
            if d not in vals:
                vals.append(d)
        while len(vals) < 4:
            vals.append(_root_pair_text(r1, r2 + len(vals)))
        vals = vals[:4]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["distractors"] = [c["value"] for c in choices if c["value"] != correct]
    return matrix


def _pretty_radical_quadratic(rng: random.Random) -> tuple[Fraction, Fraction, Fraction, str]:
    # a=1, b even, disc = 4*s with s square-free-ish positive not square.
    b_half = _pick(rng, -5, 5, nonzero=True)
    b = Fraction(2 * b_half)
    s = rng.choice([2, 3, 5, 6, 7, 10])
    # disc = b^2 - 4c = 4*s => c = (b^2 - 4s)/4 = b_half^2 - s
    c = Fraction(b_half * b_half - s)
    a = Fraction(1)
    d = discriminant(a, b, c)
    if d <= 0 or int(d) != d or int(sp.integer_nthroot(int(d), 2)[1]):
        a, b, c = Fraction(1), Fraction(6), Fraction(3)
    roots = sp.solve(sp.Eq(a * sp.symbols("x") ** 2 + b * sp.symbols("x") + c, 0), sp.symbols("x"))
    text = " 或 ".join(canonical_exact(r) for r in roots)
    return a, b, c, text


def _build_formula(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec.get("parts") or 2)
    items = []
    parts = {}
    params = []
    label_names: list[str] = []
    part_i = 1
    for eq_index in range(1, n + 1):
        a, b, c, _text = _pretty_radical_quadratic(rng)
        roots = sp.solve(sp.Eq(a * sp.symbols("x") ** 2 + b * sp.symbols("x") + c, 0), sp.symbols("x"))
        roots = sorted(roots, key=lambda r: float(sp.N(r)))
        tex = _tex_quad(a, b, c)
        items.append({"group_label": f"({eq_index})", "text": f"\\({tex}=0\\)"})
        parts[f"({part_i})"] = canonical_exact(roots[0])
        parts[f"({part_i+1})"] = canonical_exact(roots[1])
        if n == 1:
            label_names.extend(["較小根", "較大根"])
        else:
            label_names.extend([f"第{eq_index}式較小根", f"第{eq_index}式較大根"])
        params.append({"a": canonical_exact(a), "b": canonical_exact(b), "c": canonical_exact(c)})
        part_i += 2
    stem = build_stem_structure("利用公式解，由小到大寫出各方程式的兩根：", items)
    return _matrix(
        QUADRATIC_FORMULA_EXACT,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=["判別式不是完全平方，根以最簡根式表示。"],
        answer_type="multi_part",
        presentation="short_answer",
        params={"equations": params},
        stem_structure=stem,
        part_label_map=_part_label_map(*label_names),
    )


def _build_projectile(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    land = _pick(rng, 2, 8)
    height0 = _pick(rng, 1, 5)
    # h = height0 + v t - a t^2, roots 0? Start above ground and land at `land`.
    # Use h = a (land - t) t  with a>0 so h>0 between 0 and land, wait upward then down.
    # Textbook asks time to ground, positive root. h = k*t*(land-t) starts at 0.
    # Better vertex form: h = -a (t-m)^2 + a (m)^2 so roots 0 and 2m if m chosen.
    m = land
    a = _pick(rng, 1, 5)
    # h = -a (t-m)^2 + a*m^2 => h(0)=0, h(2m)=0. Not starting positive uniquely.
    # h = -a (t-land)^2 + a*land^2 has roots 0 and 2*land. Ask the positive landing besides start: 2*land if launched from 0.
    q = (
        f"一物於 t 秒後的高度為 h=-{a}\\left(t-{land}\\right)^2+{a * land * land}（公尺）。"
        f"它於幾秒後落到地面？（取正的時刻）"
    )
    # roots: (t-land)^2 = land^2 => t-land = ±land => t=0 or t=2*land
    answer = Fraction(2 * land)
    return _finish_scalar(
        QUADRATIC_PROJECTILE_TIME, q, answer, ["令 h=0，捨去 t=0。"], spec,
        {"a": a, "land_shift": land}, rng,
    )


def _count_quadratic(rng: random.Random, kind: str) -> tuple[str, int, Fraction, Fraction, Fraction]:
    if kind == "two":
        r1, r2 = Fraction(_pick(rng, -4, 4)), Fraction(_pick(rng, -4, 4))
        if r1 == r2:
            r2 = r1 + 1
        a, b, c = quadratic_coeffs(Fraction(1), r1, r2)
    elif kind == "one":
        r = Fraction(_pick(rng, -4, 4))
        a, b, c = quadratic_coeffs(Fraction(_pick(rng, 1, 3)), r, r)
    else:
        a = Fraction(_pick(rng, 1, 3))
        b = Fraction(_pick(rng, -4, 4))
        c = Fraction(int(b * b / (4 * a)) + _pick(rng, 1, 5))
        if discriminant(a, b, c) >= 0:
            c = c + 3
    return f"{_tex_quad(a, b, c)}=0", root_count(a, b, c), a, b, c


def _build_root_count(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    kinds = ["two", "none", "one"]
    items = []
    parts = {}
    params = []
    for i, kind in enumerate(kinds, 1):
        tex, count, a, b, c = _count_quadratic(rng, kind)
        items.append({"group_label": f"({i})", "text": f"\\({tex}\\)"})
        parts[f"({i})"] = str(count)
        params.append({"a": canonical_exact(a), "b": canonical_exact(b), "c": canonical_exact(c)})
    stem = build_stem_structure("判定下列方程式的實根個數（兩相異記 2、重根記 1、無實根記 0）：", items)
    return _matrix(
        QUADRATIC_ROOT_COUNT,
        question_text=stem_structure_to_question_text(stem),
        answer={"parts": parts},
        explanation=["由判別式正、零、負決定。"],
        answer_type="multi_part",
        presentation="short_answer",
        params={"items": params},
        stem_structure=stem,
        part_label_map=_numbered_labels(len(parts), "第{n}式"),
    )


def _build_equal_roots(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    # (k+1) x^2 - k x - 1 = 0 has equal roots when disc=0.
    # Use x^2 - 2*r*x + r^2 + k = 0? Simpler: x^2 + k x + 1 = 0 equal => k^2-4=0, k=±2, two values.
    # Ask one parameter value family that is unique: (x-r)^2 = x^2 - 2 r x + r^2, so k = r^2 unique if monic constant is k and linear fixed.
    r = _pick(rng, -5, 5, nonzero=True)
    # x^2 - 2*r*x + k = 0 equal roots => k = r^2
    k = r * r
    q = f"方程式\\({_tex_quad_with_parameter(Fraction(1), Fraction(-2 * r))}=0\\)有兩相等實根，試求實數 k。"
    return _finish_scalar(
        QUADRATIC_PARAMETER_EQUAL_ROOTS, q, Fraction(k), ["判別式為 0。"], spec,
        {"root": r}, rng,
    )


def _build_no_real(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    # x^2 - 6x + k = 0 has no real roots when disc<0 => 36-4k<0 => k>9
    shift = _pick(rng, 2, 7)
    # x^2 - 2*shift*x + k = 0, disc = 4*shift^2 - 4k < 0 => k > shift^2
    bound = shift * shift
    q = f"若方程式\\({_tex_quad_with_parameter(Fraction(1), Fraction(-2 * shift))}=0\\)沒有實根，試求 k 的範圍。"
    answer = f"k > {bound}"
    matrix = _matrix(
        QUADRATIC_PARAMETER_NO_REAL,
        question_text=q,
        answer=answer,
        explanation=["判別式小於 0。"],
        answer_type="expression",
        presentation=spec["presentation"],
        params={"shift": shift},
    )
    if spec["presentation"] == "single_choice":
        correct = answer
        vals = [correct, f"k < {bound}", f"k >= {bound}", f"k <= {bound}"]
        labels = ["A", "B", "C", "D"]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
    return matrix


def _build_two_distinct(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    shift = _pick(rng, 2, 6)
    bound = shift * shift
    q = f"方程式\\({_tex_quad_with_parameter(Fraction(1), Fraction(-2 * shift))}=0\\)有兩相異實根，則 k 的範圍為"
    answer = f"k < {bound}"
    return _finish_scalar(
        QUADRATIC_PARAMETER_TWO_DISTINCT, q, answer, ["判別式大於 0。"], spec,  # type: ignore[arg-type]
        {"bound": bound}, rng,
    ) if False else _matrix_choice_relation(
        QUADRATIC_PARAMETER_TWO_DISTINCT, q, answer, spec, {"shift": shift}, rng,
    )


def _matrix_choice_relation(op, q, answer, spec, params, rng):
    matrix = _matrix(
        op, question_text=q, answer=answer, explanation=["判別式符號。"],
        answer_type="expression", presentation=spec["presentation"], params=params,
    )
    if spec["presentation"] == "single_choice":
        bound = params["shift"] * params["shift"]
        correct = answer
        vals = [correct, f"k > {bound}", f"k >= {bound}", f"k <= {bound}"]
        labels = ["A", "B", "C", "D"]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["distractors"] = [v for v in vals if v != correct]
    return matrix


def _build_vieta_expr(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    exprs = list(spec.get("exprs") or ["sum_sq"])
    lead, r1, r2, b, c = _integer_quadratic(rng)
    a = lead
    if any(k in exprs for k in ("recip_sum", "recip_sq_sum", "two_recip", "sum_over_prod")) and r1 * r2 == 0:
        if r1 == 0:
            r1 = Fraction(1)
        r2 = r1 + 2
        if r2 == 0:
            r2 = Fraction(3)
        a, b, c = quadratic_coeffs(lead, r1, r2)
    items = []
    parts = {}
    for i, kind in enumerate(exprs, 1):
        val = vieta_value(kind, a, b, c)
        items.append({"group_label": f"({i})", "text": kind})
        parts[f"({i})"] = canonical_exact(val)
    labels = {
        "sum_sq": r"\alpha^2+\beta^2",
        "recip_sum": r"\frac{1}{\alpha}+\frac{1}{\beta}",
        "recip_sq_sum": r"\frac{1}{\alpha^2}+\frac{1}{\beta^2}",
        "two_recip": r"\frac{2}{\alpha}+\frac{2}{\beta}",
        "abs_diff": r"\left|\alpha-\beta\right|",
        "ordered_diff": r"\beta-\alpha",
        "sum_over_prod": r"\frac{\alpha+\beta}{\alpha\beta}",
    }
    tex = _tex_quad(a, b, c)
    if len(exprs) == 1:
        q = f"設\\(\\alpha\\)、\\(\\beta\\)為\\({tex}=0\\)的兩根，則\\({labels[exprs[0]]}=\\)"
        answer: Any = parts["(1)"]
        answer_type = "expression"
        stem = None
        presentation = spec["presentation"]
    else:
        shown = [{"group_label": f"({i})", "text": f"\\({labels[kind]}\\)"} for i, kind in enumerate(exprs, 1)]
        stem = build_stem_structure(f"設\\(\\alpha\\)、\\(\\beta\\)為\\({tex}=0\\)的兩根，試求：", shown)
        q = stem_structure_to_question_text(stem)
        answer = {"parts": parts}
        answer_type = "multi_part"
        presentation = "short_answer"
    matrix = _matrix(
        QUADRATIC_VIETA_EXPRESSIONS,
        question_text=q,
        answer=answer,
        explanation=["和 = -b/a，積 = c/a。"],
        answer_type=answer_type,
        presentation=presentation,
        params={"a": canonical_exact(a), "b": canonical_exact(b), "c": canonical_exact(c), "exprs": exprs},
        stem_structure=stem,
    )
    if presentation == "single_choice":
        correct = parts["(1)"]
        wrong = []
        base = sp.sympify(correct)
        for delta in (1, -1, 2):
            cand = canonical_exact(base + delta)
            if cand != correct:
                wrong.append(cand)
        labels_mcq = ["A", "B", "C", "D"]
        vals = [correct] + wrong[:3]
        rng.shuffle(vals)
        choices = []
        correct_label = "A"
        for lab, val in zip(labels_mcq, vals):
            choices.append({"label": lab, "text": f"\\({val}\\)", "value": val})
            if val == correct:
                correct_label = lab
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["semantic_answer"] = correct
        matrix["answer_type"] = "single_choice"
        matrix["presentation_mode"] = "single_choice"
        matrix["validation_facts"]["answer_type"] = "single_choice"
        matrix["distractors"] = [c["value"] for c in choices if c["value"] != correct]
    return matrix


def _build_vieta_param(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    relation = spec.get("relation") or "double"
    r = _pick(rng, 2, 6)
    if relation == "double":
        r1, r2 = Fraction(r), Fraction(2 * r)
    elif relation in {"diff_one", "consecutive", "consecutive_then_sum", "diff"}:
        gap = 1 if relation != "diff" else _pick(rng, 2, 4)
        r1, r2 = Fraction(r), Fraction(r + gap)
    else:
        r1, r2 = Fraction(r), Fraction(r + 1)
    a = Fraction(_pick(rng, 1, 3))
    aa, bb, cc = quadratic_coeffs(a, r1, r2)
    # Present with k as constant term when a,b fixed and c=k, so k must equal cc and a,b shown.
    q = f"方程式\\({_tex_quad_with_parameter(aa, bb)}=0\\)"
    if relation == "double":
        q += "的一根為另一根的兩倍，試求 k。"
        answer = cc
    elif relation == "consecutive_then_sum":
        # new equation k x^2 - (sum of original? ) user item: consecutive roots then sum of kx^2 -9x +1.
        # Keep isomorphic: roots consecutive, k=product, then sum of roots of k x^2 + b2 x + 1 = 0 is -b2/k.
        new_sum = -bb / cc if cc != 0 else Fraction(1)
        q += "的兩根為連續整數。則以該積為首項係數的方程式其兩根和為"
        answer = -bb / cc
        return _finish_scalar(
            QUADRATIC_VIETA_PARAMETER, q, answer, ["連續整數根之積為 k，新方程兩根和為 -b/k。"], spec,
            {"lead": canonical_exact(a), "r1": canonical_exact(r1), "r2": canonical_exact(r2), "relation": relation},
            rng,
        )
    else:
        q += "的兩根為相差固定的整數，試求 k。"
        answer = cc
    return _finish_scalar(
        QUADRATIC_VIETA_PARAMETER, q, answer, ["由根與係數反推常數項。"], spec,
        {"lead": canonical_exact(a), "r1": canonical_exact(r1), "r2": canonical_exact(r2), "relation": relation}, rng,
    )


def _build_symmetric(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    lead, r1, r2, b, c = _integer_quadratic(rng)
    a = lead
    s, p = vieta(a, b, c)
    # new monic with roots s and p
    na, nb, nc = quadratic_coeffs(Fraction(1), s, p)
    q = (
        f"設\\(\\alpha\\)、\\(\\beta\\)為\\({_tex_quad(a, b, c)}=0\\)的兩根，"
        f"試求以\\(\\alpha+\\beta\\)與\\(\\alpha\\beta\\)為兩根的首項係數為 1 的方程式。"
    )
    answer = f"{_tex_quad(na, nb, nc)}=0"
    return _matrix(
        QUADRATIC_BUILD_FROM_SYMMETRIC,
        question_text=q,
        answer=answer,
        explanation=["新根是原方程的和與積。"],
        answer_type="expression",
        presentation="short_answer",
        params={"a": canonical_exact(a), "b": canonical_exact(b), "c": canonical_exact(c)},
    )


def _build_factor_identity(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    chosen: tuple[int, int, int, int] | None = None
    for _ in range(24):
        m = _pick(rng, -4, 5)
        n = _pick(rng, -5, 5)
        if m == n:
            continue
        b = -(2 * m + n)
        c = m * n
        sols = _integer_factor_solutions(b, c)
        if sols == [(m, n)]:
            chosen = (m, n, b, c)
            break
    if chosen is None:
        m, n, b, c = 1, 2, -4, 2
    else:
        m, n, b, c = chosen
    left = _tex_quad(Fraction(2), Fraction(b), Fraction(c))
    q = f"設\\({left}=(x-m)(2x-n)\\)，則\\(m-n=\\)"
    return _finish_scalar(
        QUADRATIC_FACTOR_IDENTITY, q, Fraction(m - n), ["展開比較係數，整數分解唯一。"], spec,
        {"b": b, "c": c}, rng,
    )


def _build_pythagoras(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    k = _pick(rng, 2, 8)
    slower = 3 * k
    faster = 4 * k
    dist = 5 * k
    diff = faster - slower
    q = (
        f"甲、乙同時同地出發，甲向北、乙向東，甲比乙每小時快{diff}公里，"
        f"1小時後相距{dist}公里。甲每小時走幾公里？"
    )
    return _finish_scalar(
        QUADRATIC_WORD_PYTHAGORAS, q, Fraction(faster), ["(v)^2+(v-diff)^2=dist^2"], spec,
        {"diff": diff, "dist": dist}, rng,
    )


def _leg_gap_quadratic(gap: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """x^2 + (x+d)^2 = (x+2d)^2 rearranges to x^2 - 2 d x - 3 d^2 = 0."""
    return Fraction(1), -2 * gap, -3 * gap * gap


def _build_right_triangle_side(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    forced = spec.get("gap_d")
    if forced is None:
        gap = Fraction(rng.choice(LEG_GAP_POOL))
    else:
        gap = Fraction(int(forced))
    if gap <= 0 or gap.denominator != 1:
        raise ValueError("invalid_leg_gap")
    a, b, c = _leg_gap_quadratic(gap)
    algebraic = quadratic_real_roots(a, b, c)
    valid = tuple(root for root in algebraic if root > 0 and root + gap > 0 and root + 2 * gap > 0)
    if valid != (3 * gap,):
        raise ValueError("geometry_root_filter_failed")
    shortest = valid[0]
    longer = shortest + gap
    hypotenuse = shortest + 2 * gap
    if not (shortest < longer < hypotenuse):
        raise ValueError("side_order_failed")
    if shortest ** 2 + longer ** 2 != hypotenuse ** 2:
        raise ValueError("pythagoras_failed")
    discarded = [root for root in algebraic if root not in valid]
    q = (
        "一直角三角形的兩股長分別為 \\(x\\) 公分與 "
        f"\\((x+{canonical_exact(gap)})\\) 公分，斜邊長為 "
        f"\\((x+{canonical_exact(2 * gap)})\\) 公分，試求此三角形最短邊的長度。"
    )
    explanation = [
        f"由畢氏定理，x^2+(x+{canonical_exact(gap)})^2=(x+{canonical_exact(2 * gap)})^2。",
        f"整理得 x^2+({canonical_exact(b)})x+({canonical_exact(c)})=0。",
        "代數根為 " + "、".join(canonical_exact(root) for root in algebraic) + "。",
        "邊長必須為正，故捨去 " + "、".join(canonical_exact(root) for root in discarded) + "。",
        f"最短邊為 {canonical_exact(shortest)}。",
    ]
    matrix = _matrix(
        QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION,
        question_text=q,
        answer=shortest,
        explanation=explanation,
        answer_type="expression",
        presentation="short_answer",
        params={"d": int(gap)},
    )
    matrix["validation_facts"]["algebraic_roots"] = [canonical_exact(root) for root in algebraic]
    matrix["validation_facts"]["valid_geometry_roots"] = [canonical_exact(root) for root in valid]
    matrix["validation_facts"]["text_surrogate"] = True
    return matrix


def _build_pairs(rng: random.Random, spec: dict[str, Any]) -> dict[str, Any]:
    n = _pick(rng, 8, 20)
    total = n * (n - 1)
    q = (
        f"有 n 支球隊，每支與其他球隊各賽一場，總場數 M=n(n-1)。"
        f"若 M={total}，請問有幾支球隊？"
    )
    return _finish_scalar(
        QUADRATIC_WORD_PAIR_COUNT, q, Fraction(n), ["n^2-n-M=0，取正根。"], spec,
        {"total": total}, rng,
    )


_BUILDERS = {
    LINEAR_SOLVE_ISOLATED: _build_isolated,
    LINEAR_SOLVE_GENERAL: _build_general,
    LINEAR_WORD_UNIT_TOTAL: _build_unit_total,
    LINEAR_WORD_TWO_CONDITIONS: _build_two_conditions,
    LINEAR_WORD_RATIO_SUM: _build_ratio_sum,
    LINEAR_WORD_THREE_SHARES: _build_three,
    LINEAR_WORD_MARKUP: _build_markup,
    LINEAR_WORD_TWO_PLANS: _build_plans,
    LINEAR_WORD_CLASS_SHARE: _build_class,
    INEQUALITY_SOLVE: _build_inequality,
    INEQUALITY_WORD_MINIMUM: _build_minimum,
    INEQUALITY_BMI_BOUND: _build_bmi,
    QUADRATIC_INTEGER_ROOTS: _build_integer_roots,
    QUADRATIC_FORMULA_EXACT: _build_formula,
    QUADRATIC_PROJECTILE_TIME: _build_projectile,
    QUADRATIC_ROOT_COUNT: _build_root_count,
    QUADRATIC_PARAMETER_EQUAL_ROOTS: _build_equal_roots,
    QUADRATIC_PARAMETER_NO_REAL: _build_no_real,
    QUADRATIC_PARAMETER_TWO_DISTINCT: _build_two_distinct,
    QUADRATIC_VIETA_EXPRESSIONS: _build_vieta_expr,
    QUADRATIC_VIETA_PARAMETER: _build_vieta_param,
    QUADRATIC_BUILD_FROM_SYMMETRIC: _build_symmetric,
    QUADRATIC_FACTOR_IDENTITY: _build_factor_identity,
    QUADRATIC_WORD_PYTHAGORAS: _build_pythagoras,
    QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION: _build_right_triangle_side,
    QUADRATIC_WORD_PAIR_COUNT: _build_pairs,
}


def build_equation_solving_matrix(
    *,
    operation: str | None = None,
    domain_operation: str | None = None,
    constraints: dict[str, Any] | None = None,
    seed: int | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    **data: Any,
) -> dict[str, Any]:
    raw = dict(constraints or {})
    raw.update(data)
    op = str(operation or domain_operation or raw.get("problem_type_id") or "").strip()
    source_id = raw.get("textbook_example_id") or raw.get("source_example_id")
    spec = dict(SOURCE_SPECS.get(int(source_id), {})) if source_id else {}
    if not op:
        op = str(spec.get("op") or "")
    if op not in OPS:
        raise ValueError(f"unsupported_equation_operation:{op}")
    spec.setdefault("op", op)
    spec.setdefault("presentation", str(raw.get("presentation_mode") or "short_answer"))
    if raw.get("gap_d") is not None:
        spec["gap_d"] = raw["gap_d"]
    rng = random.Random(0 if seed is None else int(seed))
    # Difficulty changes structure: more sign changes / fractions, not just bigger integers.
    if str(difficulty_profile or "") in {"hard", "3"}:
        rng = random.Random((0 if seed is None else int(seed)) + 17)
        spec["fraction"] = True
    matrix = _BUILDERS[op](rng, spec)
    matrix["curriculum_profile"] = curriculum_profile
    matrix["difficulty_profile"] = difficulty_profile
    matrix["seed"] = 0 if seed is None else int(seed)
    return matrix


def validate_equation_solving_matrix(matrix: dict[str, Any]) -> bool:
    if not isinstance(matrix, dict):
        return False
    if matrix.get("domain_key") != DOMAIN_KEY:
        return False
    op = str(matrix.get("domain_operation") or "")
    if op not in OPS:
        return False
    if not str(matrix.get("question_text") or "").strip():
        return False
    ans = matrix.get("answer")
    if not isinstance(ans, dict) or "canonical_form" not in ans:
        return False
    if matrix.get("answer_type") == "single_choice":
        choices = matrix.get("choices")
        if not isinstance(choices, list) or len(choices) != 4:
            return False
        values = [c.get("value") for c in choices]
        if len(set(values)) != 4:
            return False
        if matrix.get("semantic_answer") not in values:
            return False
    return True


def _as_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    rat = sp.Rational(sp.nsimplify(value))
    return Fraction(int(rat.p), int(rat.q))


def _quad_root_texts(a: Fraction, b: Fraction, c: Fraction) -> list[str]:
    x = sp.symbols("x")
    roots = list(sp.solve(sp.Eq(a * x**2 + b * x + c, 0), x))
    roots = sorted(roots, key=lambda r: float(sp.N(r)))
    if len(roots) == 1:
        roots = [roots[0], roots[0]]
    return [canonical_exact(r) for r in roots]


def _linear_parts(equations: list[dict[str, Any]]) -> dict[str, str]:
    parts = {}
    for i, row in enumerate(equations, 1):
        if "left_a" in row:
            left_a, left_b, right_a, right_b = row["left_a"], row["left_b"], row["right_a"], row["right_b"]
        else:
            left_a, left_b, right_a, right_b = row["a1"], row["b1"], row["a2"], row["b2"]
        root = solve_linear(Fraction(left_a), Fraction(left_b), Fraction(right_a), Fraction(right_b))
        parts[f"({i})"] = canonical_exact(root)
    return parts


def _positive_quadratic_root(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    d = discriminant(a, b, c)
    root = sp.sqrt(sp.Integer(int(d)))
    if not root.is_integer:
        raise ValueError("quadratic_root_not_integer_disc")
    hi = (-b + _as_fraction(root)) / (2 * a)
    lo = (-b - _as_fraction(root)) / (2 * a)
    for cand in (hi, lo):
        if cand > 0 and cand.denominator == 1:
            return cand
    raise ValueError("quadratic_positive_root_missing")


def recompute_answer(matrix: dict[str, Any]) -> Any:
    """Recompute the canonical answer from stored givens, without reading the answer block."""
    op = str(matrix.get("domain_operation") or "")
    g = matrix.get("givens") if isinstance(matrix.get("givens"), dict) else {}
    if op in {LINEAR_SOLVE_ISOLATED, LINEAR_SOLVE_GENERAL}:
        parts = _linear_parts(list(g.get("equations") or []))
        return parts if len(parts) > 1 else parts["(1)"]
    if op == LINEAR_WORD_UNIT_TOTAL:
        return canonical_exact(solve_linear(Fraction(g["unit"]), Fraction(g["fixed"]), Fraction(0), Fraction(g["total"])))
    if op == LINEAR_WORD_TWO_CONDITIONS:
        per_a, per_b = Fraction(g["per_a"]), Fraction(g["per_b"])
        if "rem" in g:
            students = (Fraction(g["rem"]) + Fraction(g["short"])) / (per_b - per_a)
            items = per_a * students + Fraction(g["rem"])
            return {"(1)": canonical_exact(students), "(2)": canonical_exact(items)}
        rooms = (Fraction(g["leftover"]) + per_b * Fraction(g["extra"])) / (per_b - per_a)
        people = per_a * rooms + Fraction(g["leftover"])
        return {"(1)": canonical_exact(rooms), "(2)": canonical_exact(people)}
    if op == LINEAR_WORD_RATIO_SUM:
        english = (Fraction(g["total"]) + Fraction(g["gap"])) / 3
        math = Fraction(g["total"]) - english
        return {"(1)": canonical_exact(math), "(2)": canonical_exact(english)}
    if op == LINEAR_WORD_THREE_SHARES:
        sister = 2 * (Fraction(g["total"]) + Fraction(g["big_gap"]) - Fraction(g["little_extra"])) / 7
        big = 2 * sister - Fraction(g["big_gap"])
        little = sister / 2 + Fraction(g["little_extra"])
        return {"(1)": canonical_exact(big), "(2)": canonical_exact(sister), "(3)": canonical_exact(little)}
    if op == LINEAR_WORD_MARKUP:
        return canonical_exact(Fraction(g["cost_price"]) * 5 / 6)
    if op == LINEAR_WORD_TWO_PLANS:
        rate_a = Fraction(g["rate_a"])
        included = Fraction(g["included"])
        got = solve_linear(rate_a, Fraction(g["fee_a"]) - rate_a * included, Fraction(g["rate_b"]), Fraction(g["fee_b"]))
        return canonical_exact(got)
    if op == LINEAR_WORD_CLASS_SHARE:
        return canonical_exact(2 * (Fraction(g["extra"]) + Fraction(g["high"])))
    if op == INEQUALITY_SOLVE:
        parts = {}
        for i, row in enumerate(g.get("relations") or [], 1):
            shown, _boundary = solve_inequality(
                Fraction(row["left_a"]), Fraction(row["left_b"]), Fraction(row["right_a"]), Fraction(row["right_b"]), row["op"],
            )
            parts[f"({i})"] = shown
        return parts if len(parts) > 1 else parts["(1)"]
    if op == INEQUALITY_WORD_MINIMUM:
        if "daily" in g:
            need = int(g["price"]) - int(g["have"])
            days = (need + int(g["daily"]) - 1) // int(g["daily"])
            return canonical_exact(Fraction(days))
        bound = Fraction(int(g["threshold"]) * int(g["group"]), int(g["single"]))
        return canonical_exact(Fraction(int(bound) + 1))
    if op == INEQUALITY_BMI_BOUND:
        weight = Fraction(g["high"]) * Fraction(g["height"]) ** 2 + Fraction(g["lose"])
        return canonical_exact(weight)
    if op in {QUADRATIC_INTEGER_ROOTS, QUADRATIC_FORMULA_EXACT}:
        parts = {}
        idx = 1
        for row in g.get("equations") or []:
            lo, hi = _quad_root_texts(Fraction(row["a"]), Fraction(row["b"]), Fraction(row["c"]))
            if matrix.get("answer_type") == "single_choice":
                return _root_pair_text(_as_fraction(sp.sympify(lo)), _as_fraction(sp.sympify(hi)))
            parts[f"({idx})"] = lo
            parts[f"({idx + 1})"] = hi
            idx += 2
        return parts
    if op == QUADRATIC_PROJECTILE_TIME:
        return canonical_exact(Fraction(2 * int(g["land_shift"])))
    if op == QUADRATIC_ROOT_COUNT:
        parts = {}
        for i, row in enumerate(g.get("items") or [], 1):
            parts[f"({i})"] = str(root_count(Fraction(row["a"]), Fraction(row["b"]), Fraction(row["c"])))
        return parts
    if op == QUADRATIC_PARAMETER_EQUAL_ROOTS:
        return canonical_exact(Fraction(int(g["root"]) ** 2))
    if op == QUADRATIC_PARAMETER_NO_REAL:
        return f"k > {int(g['shift']) ** 2}"
    if op == QUADRATIC_PARAMETER_TWO_DISTINCT:
        return f"k < {int(g['shift']) ** 2}"
    if op == QUADRATIC_VIETA_EXPRESSIONS:
        a, b, c = Fraction(g["a"]), Fraction(g["b"]), Fraction(g["c"])
        parts = {f"({i})": canonical_exact(vieta_value(kind, a, b, c)) for i, kind in enumerate(g["exprs"], 1)}
        return parts if len(parts) > 1 else parts["(1)"]
    if op == QUADRATIC_VIETA_PARAMETER:
        lead, r1, r2 = Fraction(g["lead"]), Fraction(g["r1"]), Fraction(g["r2"])
        if g.get("relation") == "consecutive_then_sum":
            return canonical_exact((r1 + r2) / (r1 * r2))
        return canonical_exact(lead * r1 * r2)
    if op == QUADRATIC_BUILD_FROM_SYMMETRIC:
        a, b, c = Fraction(g["a"]), Fraction(g["b"]), Fraction(g["c"])
        s, p = vieta(a, b, c)
        na, nb, nc = quadratic_coeffs(Fraction(1), s, p)
        return f"{_tex_quad(na, nb, nc)}=0"
    if op == QUADRATIC_FACTOR_IDENTITY:
        sols = _integer_factor_solutions(int(g["b"]), int(g["c"]))
        if len(sols) != 1:
            raise ValueError("factor_identity_not_unique")
        m, n = sols[0]
        return canonical_exact(Fraction(m - n))
    if op == QUADRATIC_WORD_PYTHAGORAS:
        diff, dist = Fraction(g["diff"]), Fraction(g["dist"])
        # 2 v^2 - 2 diff v + diff^2 - dist^2 = 0
        root = _positive_quadratic_root(Fraction(2), -2 * diff, diff * diff - dist * dist)
        return canonical_exact(root)
    if op == QUADRATIC_WORD_PAIR_COUNT:
        total = Fraction(g["total"])
        root = _positive_quadratic_root(Fraction(1), Fraction(-1), -total)
        return canonical_exact(root)
    if op == QUADRATIC_RIGHT_TRIANGLE_SIDE_RELATION:
        gap = Fraction(int(g["d"]))
        coeff_a, coeff_b, coeff_c = _leg_gap_quadratic(gap)
        algebraic = quadratic_real_roots(coeff_a, coeff_b, coeff_c)
        valid = [root for root in algebraic if root > 0 and root + gap > 0 and root + 2 * gap > 0]
        if len(valid) != 1:
            raise ValueError("geometry_root_not_unique")
        return canonical_exact(valid[0])
    raise ValueError(f"recompute_unsupported:{op}")


def _integer_factor_solutions(b: int, c: int) -> list[tuple[int, int]]:
    disc = b * b - 8 * c
    if disc < 0:
        return []
    root = int(disc ** 0.5)
    if root * root != disc:
        return []
    sols: list[tuple[int, int]] = []
    for sign in (1, -1):
        num = -b + sign * root
        if num % 4 == 0:
            m = num // 4
            n = -b - 2 * m
            pair = (m, n)
            if pair not in sols:
                sols.append(pair)
    return sols
