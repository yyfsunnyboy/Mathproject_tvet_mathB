"""Exact domain operations for general-high Mathematics 1, Unit 3 (exponents).

Domain key ``algebra.exponent_laws``.  Every operation is one shared, source-agnostic
implementation: components pass *inputs only* (``constraints``); this module computes the
canonical answer and a validator re-derives it by an independent method.

* exact engine  : sympy (rational / algebraic values) and ``fractions.Fraction``
* independent   : mpmath high-precision evaluation, integer arithmetic, exact substitution
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import Any, Callable

import mpmath as mp
import sympy as sp

from .expr_tree import (
    canonical_text,
    classify,
    display_latex,
    exact_simplify,
    numeric_close,
    symbols_in,
    to_mpmath,
    to_sympy,
)

DOMAIN_KEY = "algebra.exponent_laws"
mp.mp.dps = 60

_SAMPLE_POINTS = (mp.mpf("1.7"), mp.mpf("2.3"), mp.mpf("0.6"))


# --- shared helpers ---------------------------------------------------------------

def frac_text(value: Fraction) -> str:
    """Terminating decimals as decimals, everything else as ``p/q``."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    d = value.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        return f"{value.numerator}/{value.denominator}"
    places = 0
    scaled = value
    if value.denominator > 10000:
        return f"{value.numerator}/{value.denominator}"
    while scaled.denominator != 1:
        scaled *= 10
        places += 1
    text = str(abs(scaled.numerator)).rjust(places + 1, "0")
    sign = "-" if value < 0 else ""
    return f"{sign}{text[:-places]}.{text[-places:]}"


def mp_text(value: Any, digits: int = 45) -> str:
    return mp.nstr(value, digits)


def _require(constraints: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in constraints]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _value_record(value: sp.Expr, original_numeric: Any, symbolic_tree: Any | None = None) -> dict[str, Any]:
    kind = classify(value)
    record = {"canonical": canonical_text(value), "display": display_latex(value), "kind": kind}
    if kind == "expression":
        record["srepr"] = sp.srepr(value)
    else:
        record["numeric"] = mp_text(sp.N(value, 50))
        if not numeric_close(sp.N(value, 50), original_numeric):
            raise ValueError("exact_value_disagrees_with_numeric_evaluation")
    return record


# --- 1. simplify_exponent_expressions ----------------------------------------------

def simplify_exponent_expressions(stem: str, items: list[Any]) -> dict[str, Any]:
    values = []
    for tree in items:
        names = symbols_in(tree)
        exact = exact_simplify(to_sympy(tree))
        if names:
            record = _value_record(exact, 0)
            if not exact.free_symbols:
                raise ValueError("symbolic_item_collapsed")
        else:
            record = _value_record(exact, to_mpmath(tree))
        values.append(record)
    return {"stem": stem, "values": values}


def _check_simplify_exponent_expressions(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    if len(answer["values"]) != len(givens["items"]):
        return False
    for tree, record in zip(givens["items"], answer["values"]):
        names = symbols_in(tree)
        if names:
            expr = sp.sympify(record["srepr"])
            for point in _SAMPLE_POINTS:
                env = {name: point for name in names}
                got = mp.mpf(str(sp.N(expr.subs({sp.Symbol(n, positive=True): sp.Float(str(point), 50) for n in names}), 40)))
                if not numeric_close(got, to_mpmath(tree, env), "1e-30"):
                    return False
        else:
            if not numeric_close(record["numeric"], to_mpmath(tree), "1e-35"):
                return False
            if record["kind"] == "rational" and Fraction(record["canonical"]) != Fraction(mp_text(mp.mpf(record["numeric"]), 40)).limit_denominator(10**15):
                return False
    return True


# --- 2. solve_exponent_blank_equations -------------------------------------------

def _exponent_of(base: Fraction, root: Fraction) -> int:
    """Integer k with root**k == base (exact)."""
    base, root = Fraction(base), Fraction(root)
    if root in (0, 1, -1) and base != root ** 1 and base != 1:
        raise ValueError("base_not_power_of_root")
    for k in range(-64, 65):
        if k == 0:
            continue
        try:
            if root ** k == base:
                return k
        except ZeroDivisionError:
            continue
    raise ValueError("base_not_power_of_root")


def _solve_blank(item: dict[str, Any]) -> int:
    kind = item["kind"]
    if kind == "product_to_base":
        root = Fraction(item["result_base"])
        total = sum(_exponent_of(Fraction(b), root) * int(e) for b, e in item["factors"])
        return total
    if kind == "power_power":
        base, root = Fraction(item["base"]), Fraction(item["result_base"])
        k = _exponent_of(root, base)  # root == base**k
        inner, outer = item.get("inner"), item.get("outer")
        if (inner is None) == (outer is None):
            raise ValueError("exactly_one_blank_required")
        target = k * int(item["result_exp"])
        known = int(inner if inner is not None else outer)
        if target % known:
            raise ValueError("blank_not_integer")
        return target // known
    if kind == "merge_bases":
        (b1, e1), (b2, e2) = item["factors"]
        n = int(item["common_exponent"])
        if int(e1) % n or int(e2) % n:
            raise ValueError("merge_exponents_not_divisible")
        return None  # handled by the base solver below
    raise ValueError(f"unknown_blank_kind:{kind}")


def _solve_merge(item: dict[str, Any]) -> Fraction:
    (b1, e1), (b2, e2) = item["factors"]
    n = int(item["common_exponent"])
    return Fraction(b1) ** (int(e1) // n) * Fraction(b2) ** (int(e2) // n)


def solve_exponent_blank_equations(stem: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    values = []
    for item in items:
        if item["kind"] == "merge_bases":
            _solve_blank(item)
            values.append({"kind": "rational", "canonical": frac_text(_solve_merge(item)), "blank": "base"})
        else:
            values.append({"kind": "rational", "canonical": str(_solve_blank(item)), "blank": "exponent"})
    return {"stem": stem, "values": values}


def _check_solve_exponent_blank_equations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    for item, record in zip(givens["items"], answer["values"]):
        x = Fraction(record["canonical"])
        kind = item["kind"]
        if kind == "product_to_base":
            left = Fraction(1)
            for b, e in item["factors"]:
                left *= Fraction(b) ** int(e)
            if left != Fraction(item["result_base"]) ** int(x):
                return False
        elif kind == "power_power":
            inner = int(item["inner"]) if item.get("inner") is not None else int(x)
            outer = int(item["outer"]) if item.get("outer") is not None else int(x)
            if (Fraction(item["base"]) ** inner) ** outer != Fraction(item["result_base"]) ** int(item["result_exp"]):
                return False
        else:
            (b1, e1), (b2, e2) = item["factors"]
            if x ** int(item["common_exponent"]) != Fraction(b1) ** int(e1) * Fraction(b2) ** int(e2):
                return False
    return len(answer["values"]) == len(givens["items"])


# --- 3. evaluate_conditional_exponent_values ---------------------------------------

def evaluate_conditional_exponent_values(
    var: str, condition: dict[str, Any], roots: list[str], targets: list[Any], assume_positive: bool = False, **text: Any
) -> dict[str, Any]:
    if not roots:
        raise ValueError("roots_required")
    per_root: list[list[sp.Expr]] = []
    for text_root in roots:
        root = sp.sympify(text_root)
        approx = sp.N(root, 40)
        if not approx.is_real or (assume_positive and approx <= 0):
            raise ValueError("root_must_be_real_and_respect_assumption")
        env = {var: root}
        if exact_simplify(to_sympy(condition["lhs"], env) - to_sympy(condition["rhs"], env)) != 0:
            raise ValueError("root_does_not_satisfy_condition")
        mp_env = {var: mp.mpf(str(sp.N(root, 55)))}
        if not numeric_close(to_mpmath(condition["lhs"], mp_env), to_mpmath(condition["rhs"], mp_env), "1e-35"):
            raise ValueError("root_fails_numeric_condition")
        per_root.append([exact_simplify(to_sympy(t, env)) for t in targets])
    for column in zip(*per_root):
        if any(sp.simplify(column[0] - other) != 0 for other in column[1:]):
            raise ValueError("targets_depend_on_root_choice")
    mp_env = {var: mp.mpf(str(sp.N(sp.sympify(roots[0]), 55)))}
    values = [
        _value_record(per_root[0][i], to_mpmath(t, mp_env)) for i, t in enumerate(targets)
    ]
    return {"values": values, "root_count": len(roots)}


def _check_evaluate_conditional_exponent_values(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    var = givens["var"]
    for text_root in givens["roots"]:
        root_mp = mp.mpf(str(sp.N(sp.sympify(text_root), 55)))
        env = {var: root_mp}
        if not numeric_close(to_mpmath(givens["condition"]["lhs"], env), to_mpmath(givens["condition"]["rhs"], env), "1e-35"):
            return False
        for tree, record in zip(givens["targets"], answer["values"]):
            if not numeric_close(record["numeric"], to_mpmath(tree, env), "1e-30"):
                return False
    return len(answer["values"]) == len(givens["targets"])


# --- 4. evaluate_exponent_statement_truth ----------------------------------------

def evaluate_exponent_statement_truth(
    statements: list[dict[str, Any]], definitions: dict[str, Any] | None = None, **text: Any
) -> dict[str, Any]:
    definitions = definitions or {}
    env = {name: exact_simplify(to_sympy(tree)) for name, tree in definitions.items()}
    mp_env = {name: to_mpmath(tree) for name, tree in definitions.items()}
    truths = []
    for statement in statements:
        exact_equal = exact_simplify(to_sympy(statement["lhs"], env) - to_sympy(statement["rhs"], env)) == 0
        numeric_equal = numeric_close(to_mpmath(statement["lhs"], mp_env), to_mpmath(statement["rhs"], mp_env), "1e-35")
        if exact_equal != numeric_equal:
            raise ValueError("exact_and_numeric_truth_disagree")
        truths.append(bool(exact_equal))
    return {"truth_values": truths}


def _check_evaluate_exponent_statement_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    mp_env = {name: to_mpmath(tree) for name, tree in (givens.get("definitions") or {}).items()}
    for statement, truth in zip(givens["statements"], answer["truth_values"]):
        equal = numeric_close(to_mpmath(statement["lhs"], mp_env), to_mpmath(statement["rhs"], mp_env), "1e-35")
        if equal != truth:
            return False
    return len(answer["truth_values"]) == len(givens["statements"])


# --- 5. evaluate_repeated_folding --------------------------------------------------

def evaluate_repeated_folding(thickness_cm: str, fold_count: int, distance_km: str, **text: Any) -> dict[str, Any]:
    t, n, d_cm = Fraction(thickness_cm), int(fold_count), Fraction(distance_km) * 100000
    if t <= 0 or n < 1 or d_cm <= 0:
        raise ValueError("invalid_folding_inputs")
    after = t * 2 ** n
    needed = 0
    while t * 2 ** needed <= d_cm:
        needed += 1
    return {
        "values": [
            {"kind": "rational", "canonical": frac_text(after)},
            {"kind": "rational", "canonical": str(needed)},
        ],
        "thickness_after_cm": frac_text(after),
        "min_folds": needed,
    }


def _check_evaluate_repeated_folding(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    t, d_cm = Fraction(givens["thickness_cm"]), Fraction(givens["distance_km"]) * 100000
    n = answer["min_folds"]
    if Fraction(answer["thickness_after_cm"]) != t * 2 ** int(givens["fold_count"]):
        return False
    # independent: logarithmic bound agrees with the integer search
    bound = mp.log(mp.mpf(d_cm.numerator) / mp.mpf(d_cm.denominator) / mp.mpf(t.numerator) * t.denominator, 2)
    return t * 2 ** n > d_cm >= (t * 2 ** (n - 1) if n else 0) and int(mp.floor(bound)) + 1 == n


# --- 6. select_nearest_model_value --------------------------------------------------

def _model_value(model: str, givens: dict[str, Any]) -> mp.mpf:
    if model == "folding":
        t = Fraction(givens["thickness_cm"])
        return mp.mpf(t.numerator) / t.denominator * mp.power(2, int(givens["fold_count"])) / 100
    if model == "tsunami":
        return mp.sqrt(10 * mp.mpf(str(givens["depth_m"])))
    raise ValueError(f"unknown_model:{model}")


def select_nearest_model_value(model: str, options: list[dict[str, Any]], **givens: Any) -> dict[str, Any]:
    value = _model_value(model, givens)
    ranked = sorted(options, key=lambda o: abs(mp.mpf(str(o["value"])) - value))
    if len(ranked) < 2:
        raise ValueError("at_least_two_options")
    best, second = (abs(mp.mpf(str(o["value"])) - value) for o in ranked[:2])
    if not best * 2 <= second:
        raise ValueError("nearest_option_not_clear")
    return {"value": mp_text(value, 20), "choice": options.index(ranked[0]) + 1, "chosen_name": ranked[0]["name"]}


def _check_select_nearest_model_value(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    value = _model_value(givens["model"], givens)
    distances = [abs(mp.mpf(str(o["value"])) - value) for o in givens["options"]]
    return distances.index(min(distances)) + 1 == answer["choice"] and numeric_close(answer["value"], value, "1e-15")


# --- 7. evaluate_power_law_model ---------------------------------------------------

def evaluate_power_law_model(mode: str, k: str, exponent: int, **dist: Any) -> dict[str, Any]:
    p = int(exponent)
    if mode == "value":
        value = Fraction(k) * Fraction(dist["distance_m"]) ** p
    elif mode == "ratio":
        value = (Fraction(dist["to_distance_m"]) / Fraction(dist["from_distance_m"])) ** p
    else:
        raise ValueError(f"unknown_power_law_mode:{mode}")
    return {"values": [{"kind": "rational", "canonical": frac_text(value)}], "value": frac_text(value)}


def _check_evaluate_power_law_model(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    p = int(givens["exponent"])
    if givens["mode"] == "value":
        expected = mp.mpf(str(givens["k"])) * mp.power(mp.mpf(str(givens["distance_m"])), p)
    else:
        expected = mp.power(mp.mpf(str(givens["to_distance_m"])) / mp.mpf(str(givens["from_distance_m"])), p)
    got = Fraction(answer["value"])
    return numeric_close(mp.mpf(got.numerator) / got.denominator, expected, "1e-30")


# --- 8. solve_metabolic_scaling ----------------------------------------------------

def solve_metabolic_scaling(exponent: str, weight_ratio: int, options: list[int], metabolic_ratio: int, **text: Any) -> dict[str, Any]:
    e = Fraction(exponent)
    ratio_1 = mp.power(int(weight_ratio), mp.mpf(e.numerator) / e.denominator)
    ranked = sorted(options, key=lambda o: abs(mp.mpf(o) - ratio_1))
    if not abs(mp.mpf(ranked[0]) - ratio_1) * 2 <= abs(mp.mpf(ranked[1]) - ratio_1):
        raise ValueError("nearest_option_not_clear")
    # (2): B ratio Q  =>  M ratio Q^(1/e), must be exact
    inverse = Fraction(1) / e
    root_index = inverse.denominator
    base = Fraction(int(metabolic_ratio))
    root = round(float(base) ** (1 / root_index))
    if root ** root_index != base:
        raise ValueError("metabolic_ratio_not_a_perfect_root")
    mass_ratio = Fraction(root) ** inverse.numerator
    return {
        "values": [
            {"kind": "choice", "canonical": str(options.index(ranked[0]) + 1)},
            {"kind": "rational", "canonical": frac_text(mass_ratio)},
        ],
        "choice": options.index(ranked[0]) + 1,
        "value_1": mp_text(ratio_1, 20),
        "mass_ratio": frac_text(mass_ratio),
    }


def _check_solve_metabolic_scaling(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    e = Fraction(givens["exponent"])
    mass_ratio = Fraction(answer["mass_ratio"])
    # forward check of (2): (mass ratio)^e must reproduce the metabolic ratio
    forward = mp.power(mp.mpf(mass_ratio.numerator) / mass_ratio.denominator, mp.mpf(e.numerator) / e.denominator)
    distances = [abs(mp.mpf(o) - mp.power(int(givens["weight_ratio"]), mp.mpf(e.numerator) / e.denominator)) for o in givens["options"]]
    return numeric_close(forward, int(givens["metabolic_ratio"]), "1e-30") and distances.index(min(distances)) + 1 == answer["choice"]


# --- 9. solve_half_life_model ------------------------------------------------------

def solve_half_life_model(half_life_hours: int, threshold_exponent: int, days: int, **text: Any) -> dict[str, Any]:
    t, m, d = int(half_life_hours), int(threshold_exponent), int(days)
    hours_needed = m * t
    if (24 * d) % t:
        raise ValueError("elapsed_hours_not_multiple_of_half_life")
    remaining = Fraction(1, 2 ** ((24 * d) // t))
    return {
        "values": [
            {"kind": "rational", "canonical": str(hours_needed)},
            {"kind": "rational", "canonical": frac_text(remaining)},
        ],
        "hours_needed": hours_needed,
        "remaining": frac_text(remaining),
        "remaining_power": (24 * d) // t,
    }


def _check_solve_half_life_model(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    t = mp.mpf(givens["half_life_hours"])
    y = lambda h: mp.power(mp.mpf(1) / 2, mp.mpf(h) / t)
    rem = Fraction(answer["remaining"])
    return (
        numeric_close(y(answer["hours_needed"]), mp.power(mp.mpf(1) / 2, int(givens["threshold_exponent"])), "1e-35")
        and numeric_close(y(24 * int(givens["days"])), mp.mpf(rem.numerator) / rem.denominator, "1e-35")
    )


# --- 10. evaluate_scale_energy_ratio ----------------------------------------------

def evaluate_scale_energy_ratio(factor_exponent: int, high: int, low: int, partial_scale: str, reference: int, **text: Any) -> dict[str, Any]:
    f = int(factor_exponent)
    n = f * (int(high) - int(low))
    exponent = Fraction(partial_scale) - int(reference)
    value = mp.power(2, mp.mpf(f) * mp.mpf(exponent.numerator) / exponent.denominator)
    fractional = abs(value - mp.floor(value) - mp.mpf("0.5"))
    if fractional < mp.mpf("0.01"):
        raise ValueError("rounding_boundary_too_close")
    rounded = int(Decimal(mp_text(value, 30)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return {
        "values": [
            {"kind": "rational", "canonical": str(n)},
            {"kind": "rational", "canonical": str(rounded)},
        ],
        "n": n,
        "rounded": rounded,
        "exact_value": mp_text(value, 25),
    }


def _check_evaluate_scale_energy_ratio(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    factor = mp.power(2, int(givens["factor_exponent"]))
    n_ok = numeric_close(mp.power(factor, int(givens["high"]) - int(givens["low"])), mp.power(2, answer["n"]), "1e-35")
    partial = Fraction(givens["partial_scale"]) - int(givens["reference"])
    direct = mp.power(factor, mp.mpf(partial.numerator) / partial.denominator)
    return n_ok and abs(direct - answer["rounded"]) <= mp.mpf("0.5") and numeric_close(direct, answer["exact_value"], "1e-20")


# --- 11. solve_cooling_coefficient ------------------------------------------------

def solve_cooling_coefficient(ambient: str, initial: str, measured: str, minutes: int, decimals: int, **text: Any) -> dict[str, Any]:
    ta, h0, hm, t = Fraction(ambient), Fraction(initial), Fraction(measured), int(minutes)
    if not (ta < hm < h0) or t < 1:
        raise ValueError("invalid_cooling_inputs")
    ratio = (h0 - ta) / (hm - ta)
    coefficient = mp.root(mp.mpf(ratio.numerator) / ratio.denominator, t)
    scale = mp.power(10, int(decimals))
    shifted = coefficient * scale
    if abs(shifted - mp.floor(shifted) - mp.mpf("0.5")) < mp.mpf("0.002"):
        raise ValueError("rounding_boundary_too_close")
    rounded = Decimal(mp_text(coefficient, 40)).quantize(Decimal(1).scaleb(-int(decimals)), rounding=ROUND_HALF_UP)
    return {
        "values": [{"kind": "rational", "canonical": format(rounded, "f")}],
        "rounded": format(rounded, "f"),
        "exact_power": f"{ratio.numerator}/{ratio.denominator}" if ratio.denominator != 1 else str(ratio.numerator),
        "coefficient": mp_text(coefficient, 30),
    }


def _check_solve_cooling_coefficient(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ta, h0, hm, t = (mp.mpf(str(givens[k])) for k in ("ambient", "initial", "measured", "minutes"))
    a = mp.mpf(answer["coefficient"])
    return numeric_close(ta + (h0 - ta) * mp.power(a, -t), hm, "1e-25") and abs(a - mp.mpf(answer["rounded"])) <= mp.mpf(10) ** -int(givens["decimals"]) / 2


# --- 12. express_rational_powers_as_radicals -----------------------------------------

def radical_parts(base: int, exponent: str) -> dict[str, Any]:
    """Exact radical-notation decomposition of ``base**exponent`` (base positive integer).

    value = c * m**(1/q)  (positive exponent)  or  1 / (c * m**(1/q))  (negative exponent)
    with m free of q-th power factors and the index reduced.
    """
    import math

    b, e = int(base), Fraction(exponent)
    if b < 2 or e == 0:
        raise ValueError("invalid_radical_input")
    negative = e < 0
    p, q = abs(e.numerator), e.denominator
    factors = {int(k): int(v) for k, v in sp.factorint(b).items()}
    coefficient, radicand_exps = 1, {}
    for prime, mult in factors.items():
        total = mult * p
        coefficient *= prime ** (total // q)
        if total % q:
            radicand_exps[prime] = total % q
    index = q
    if radicand_exps:
        g = math.gcd(index, *radicand_exps.values())
        index //= g
        radicand_exps = {k: v // g for k, v in radicand_exps.items()}
    radicand = 1
    for prime, mult in radicand_exps.items():
        radicand *= prime ** mult
    return {"coefficient": coefficient, "index": index, "radicand": radicand, "negative": negative}


def radical_parts_latex(parts: dict[str, Any]) -> str:
    c, k, m = parts["coefficient"], parts["index"], parts["radicand"]
    if m == 1:
        body = str(c)
    else:
        root = f"\\sqrt{{{m}}}" if k == 2 else f"\\sqrt[{k}]{{{m}}}"
        body = root if c == 1 else f"{c}{root}"
    return f"\\frac{{1}}{{{body}}}" if parts["negative"] else body


def _radical_value(parts: dict[str, Any]) -> mp.mpf:
    value = mp.mpf(parts["coefficient"]) * (mp.root(parts["radicand"], parts["index"]) if parts["radicand"] != 1 else 1)
    return 1 / value if parts["negative"] else value


def express_rational_powers_as_radicals(conversions: list[dict[str, Any]], solve: dict[str, Any] | None = None) -> dict[str, Any]:
    values = []
    for item in conversions:
        parts = radical_parts(item["base"], item["exponent"])
        exact = sp.Integer(int(item["base"])) ** sp.Rational(str(item["exponent"]))
        record = {
            "kind": "radical",
            "canonical": radical_parts_latex(parts),
            "display": radical_parts_latex(parts),
            "numeric": mp_text(sp.N(exact, 50)),
            "parts": parts,
        }
        values.append(record)
    out: dict[str, Any] = {"values": values}
    if solve is not None:
        base = sp.Integer(int(solve["base"]))
        rhs = exact_simplify(to_sympy(solve["rhs"]))
        r = sp.simplify(sp.log(rhs) / sp.log(base))
        if not r.is_Rational:
            raise ValueError("exponent_not_rational")
        if exact_simplify(base ** r - rhs) != 0:
            raise ValueError("exponent_fails_exact_check")
        values.append({"kind": "rational", "canonical": frac_text(Fraction(int(r.p), int(r.q))), "display": display_latex(r)})
    return out


def _check_express_rational_powers_as_radicals(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    vals = answer["values"]
    for item, record in zip(givens["conversions"], vals):
        e = Fraction(item["exponent"])
        direct = mp.power(int(item["base"]), mp.mpf(e.numerator) / e.denominator)
        if not numeric_close(_radical_value(record["parts"]), direct, "1e-35"):
            return False
        if record["parts"]["radicand"] != 1 and int(record["parts"]["radicand"]) < 2:
            return False
    if givens.get("solve") is not None:
        r = Fraction(vals[len(givens["conversions"])]["canonical"])
        rhs = to_mpmath(givens["solve"]["rhs"])
        if not numeric_close(mp.power(int(givens["solve"]["base"]), mp.mpf(r.numerator) / r.denominator), rhs, "1e-35"):
            return False
    return len(vals) == len(givens["conversions"]) + (1 if givens.get("solve") is not None else 0)


# --- 13. solve_cooling_initial_temperature -------------------------------------------

def solve_cooling_initial_temperature(ambient: str, measured: str, minutes: int, decay_base: str, **text: Any) -> dict[str, Any]:
    ta, hm, b, t = Fraction(ambient), Fraction(measured), Fraction(decay_base), int(minutes)
    if b <= 1 or t < 1 or hm <= ta:
        raise ValueError("invalid_cooling_inputs")
    exact = ta + (hm - ta) * b ** t
    fractional = abs(exact - int(exact) - Fraction(1, 2)) if exact >= 0 else Fraction(1)
    if fractional < Fraction(1, 50):
        raise ValueError("rounding_boundary_too_close")
    rounded = int(Decimal(mp_text(mp.mpf(exact.numerator) / exact.denominator, 30)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return {"values": [{"kind": "rational", "canonical": str(rounded)}], "rounded": rounded,
            "exact": mp_text(mp.mpf(exact.numerator) / exact.denominator, 25)}


def _check_solve_cooling_initial_temperature(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    ta, hm, b, t = (mp.mpf(str(givens[k])) for k in ("ambient", "measured", "decay_base", "minutes"))
    exact = mp.mpf(answer["exact"])
    forward = ta + (exact - ta) * mp.power(b, -t)
    return numeric_close(forward, hm, "1e-18") and abs(exact - answer["rounded"]) <= mp.mpf("0.5")


# --- 14. solve_linear_unknowns_from_exponential_table ---------------------------------

def solve_linear_unknowns_from_exponential_table(table: list[dict[str, Any]], known: list[dict[str, Any]], base: str, **text: Any) -> dict[str, Any]:
    n_of = {row["label"]: int(row["n"]) for row in table}
    if len(known) != 2:
        raise ValueError("two_known_rows_required")
    b = Fraction(base)
    (n1, d1), (n2, d2) = ((n_of[k["label"]], Fraction(k["distance"])) for k in known)
    if n1 == n2:
        raise ValueError("known_rows_must_differ")
    beta = (d2 - d1) / (b ** n2 - b ** n1)
    alpha = d1 - beta * b ** n1
    return {"values": [{"kind": "rational", "canonical": frac_text(alpha)},
                       {"kind": "rational", "canonical": frac_text(beta)}],
            "alpha": frac_text(alpha), "beta": frac_text(beta)}


def _check_solve_linear_unknowns_from_exponential_table(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n_of = {row["label"]: int(row["n"]) for row in givens["table"]}
    def _num(text: str) -> mp.mpf:
        fr_ = Fraction(text)
        return mp.mpf(fr_.numerator) / fr_.denominator

    a, bt, base = _num(answer["alpha"]), _num(answer["beta"]), _num(str(givens["base"]))
    return all(numeric_close(a + bt * mp.power(base, n_of[k["label"]]), mp.mpf(str(k["distance"])), "1e-30") for k in givens["known"])


# --- operation table ----------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "simplify_exponent_expressions": (simplify_exponent_expressions, _check_simplify_exponent_expressions, ("stem", "items")),
    "solve_exponent_blank_equations": (solve_exponent_blank_equations, _check_solve_exponent_blank_equations, ("stem", "items")),
    "evaluate_conditional_exponent_values": (evaluate_conditional_exponent_values, _check_evaluate_conditional_exponent_values, ("var", "condition", "roots", "targets")),
    "evaluate_exponent_statement_truth": (evaluate_exponent_statement_truth, _check_evaluate_exponent_statement_truth, ("statements",)),
    "evaluate_repeated_folding": (evaluate_repeated_folding, _check_evaluate_repeated_folding, ("thickness_cm", "fold_count", "distance_km")),
    "select_nearest_model_value": (select_nearest_model_value, _check_select_nearest_model_value, ("model", "options")),
    "evaluate_power_law_model": (evaluate_power_law_model, _check_evaluate_power_law_model, ("mode", "k", "exponent")),
    "solve_metabolic_scaling": (solve_metabolic_scaling, _check_solve_metabolic_scaling, ("exponent", "weight_ratio", "options", "metabolic_ratio")),
    "solve_half_life_model": (solve_half_life_model, _check_solve_half_life_model, ("half_life_hours", "threshold_exponent", "days")),
    "evaluate_scale_energy_ratio": (evaluate_scale_energy_ratio, _check_evaluate_scale_energy_ratio, ("factor_exponent", "high", "low", "partial_scale", "reference")),
    "solve_cooling_coefficient": (solve_cooling_coefficient, _check_solve_cooling_coefficient, ("ambient", "initial", "measured", "minutes", "decimals")),
    "express_rational_powers_as_radicals": (express_rational_powers_as_radicals, _check_express_rational_powers_as_radicals, ("conversions",)),
    "solve_cooling_initial_temperature": (solve_cooling_initial_temperature, _check_solve_cooling_initial_temperature, ("ambient", "measured", "minutes", "decay_base")),
    "solve_linear_unknowns_from_exponential_table": (solve_linear_unknowns_from_exponential_table, _check_solve_linear_unknowns_from_exponential_table, ("table", "known", "base")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_exponent_laws_matrix(
    *,
    domain_operation: str | None = None,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_exponent_laws_operation:{operation}")
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


# --- validators (never raise) -------------------------------------------------------

def _make_validator(operation: str) -> Callable[[Any], bool]:
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if (
                matrix.get("domain") != DOMAIN_KEY
                or matrix.get("domain_operation") != operation
                or facts.get("domain_operation") != operation
            ):
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
