"""Exact shared capabilities for affine trigonometric function graphs."""

from __future__ import annotations

from typing import Any
import sympy as sp

from core.domain.trigonometry_acute_domain import evaluate_trig_decimal

OPS = (
    "compare_trig_values_by_monotonicity", "solve_trig_value_quadratic_constraint",
    "analyze_affine_transformed_trig_graph", "calculate_trig_period_from_argument_scale",
    "classify_trig_expression_sign_change", "classify_trig_equation_feasibility",
    "analyze_tangent_absolute_graph_period", "evaluate_trig_decimal",
    "count_sine_cosine_intersections",
)


def _q(value: Any) -> sp.Expr:
    result = sp.sympify(value)
    if result.is_real is not True:
        raise ValueError("real_value_required")
    return result


def _angle(value: Any, unit: str) -> sp.Expr:
    value = _q(value)
    if unit == "degree":
        return sp.simplify(value * sp.pi / 180)
    if unit == "radian":
        return value
    raise ValueError("angle_unit_unsupported")


def _canon(value: Any) -> str:
    return sp.sstr(sp.simplify(value))


def _json_value(value: Any) -> Any:
    if isinstance(value, sp.Basic): return _canon(value)
    if isinstance(value, dict): return {str(key): _json_value(item) for key,item in value.items()}
    if isinstance(value, (list,tuple)): return [_json_value(item) for item in value]
    return value


def _fn(name: str):
    functions = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
    try:
        return functions[str(name).lower()]
    except KeyError as exc:
        raise ValueError("trig_function_unsupported") from exc


def calculate_trig_period_from_argument_scale(function: str, B: Any, C: Any = 0) -> dict[str, Any]:
    function = str(function).lower()
    _fn(function)
    coefficient = _q(B)
    if coefficient == 0:
        raise ValueError("argument_scale_must_be_nonzero")
    base = sp.pi if function == "tan" else 2 * sp.pi
    period = sp.simplify(base / sp.Abs(coefficient))
    return {"function": function, "B": coefficient, "C": _q(C), "period": period,
            "canonical": _canon(period)}


def analyze_affine_transformed_trig_graph(function: str, A: Any, B: Any, C: Any = 0, D: Any = 0) -> dict[str, Any]:
    function = str(function).lower()
    if function not in {"sin", "cos"}:
        raise ValueError("affine_graph_supports_sin_cos")
    amplitude, scale, shift, midline = sp.Abs(_q(A)), _q(B), _q(C), _q(D)
    if scale == 0:
        raise ValueError("argument_scale_must_be_nonzero")
    period = calculate_trig_period_from_argument_scale(function, scale, shift)["period"]
    phase = sp.simplify(-shift / scale)
    return {"function": function, "A": _q(A), "B": scale, "C": shift, "D": midline,
            "amplitude": amplitude, "period": period, "phase_shift": phase,
            "midline": midline, "maximum": sp.simplify(midline + amplitude),
            "minimum": sp.simplify(midline - amplitude),
            "canonical": {k: _canon(v) for k, v in {"amplitude": amplitude, "period": period,
                "phase_shift": phase, "midline": midline, "maximum": midline + amplitude,
                "minimum": midline - amplitude}.items()},
            "drawing_reference": {"kind": "affine_trig_graph", "preserve_source_visual": True}}


def solve_trig_value_quadratic_constraint(function: str, coefficients: list[Any]) -> dict[str, Any]:
    function = str(function).lower()
    _fn(function)
    if len(coefficients) != 3:
        raise ValueError("quadratic_coefficients_required")
    a, b, c = map(_q, coefficients)
    if a == 0:
        raise ValueError("leading_coefficient_must_be_nonzero")
    t = sp.symbols("t", real=True)
    roots = list(sp.solve(a*t**2 + b*t + c, t))
    valid = [r for r in roots if r.is_real is True and (function == "tan" or sp.Le(-1, r) is sp.true and sp.Le(r, 1) is sp.true)]
    valid = sorted(set(valid), key=sp.default_sort_key)
    return {"function": function, "polynomial": sp.expand(a*t**2+b*t+c), "roots": roots,
            "valid_roots": valid, "unique_root": valid[0] if len(valid) == 1 else None,
            "canonical": "{" + ",".join(_canon(v) for v in valid) + "}"}


def classify_trig_equation_feasibility(options: list[dict[str, Any]], target: str = "feasible") -> dict[str, Any]:
    rows = []
    for index, option in enumerate(options):
        function, value = str(option["function"]).lower(), _q(option["value"])
        _fn(function)
        feasible = bool(function == "tan" or (sp.Le(-1, value) is sp.true and sp.Le(value, 1) is sp.true))
        rows.append({"key": str(option.get("key", index)), "function": function, "value": value, "feasible": feasible})
    if target not in {"feasible", "infeasible"}: raise ValueError("feasibility_target_unsupported")
    feasible_keys = [row["key"] for row in rows if row["feasible"]]
    selected = [row["key"] for row in rows if row["feasible"] == (target == "feasible")]
    return {"options": rows, "feasible_keys": feasible_keys,
            "infeasible_keys": [row["key"] for row in rows if not row["feasible"]],
            "target": target, "canonical_option": selected[0] if len(selected) == 1 else None}


def compare_trig_values_by_monotonicity(terms: list[dict[str, Any]], unit: str = "degree") -> dict[str, Any]:
    evaluated = []
    for index, term in enumerate(terms):
        function = str(term["function"]).lower()
        radians = _angle(term["angle"], str(term.get("unit") or unit))
        value = sp.simplify(_fn(function)(radians))
        evaluated.append({"key": str(term.get("key", index)), "function": function,
                          "angle": radians, "value": value})
    def compare(a, b):
        difference = sp.simplify(a["value"] - b["value"])
        if difference.is_negative: return -1
        if difference.is_positive: return 1
        if difference.is_zero: return 0
        raise ValueError("comparison_not_exactly_decidable")
    from functools import cmp_to_key
    ordered = sorted(evaluated, key=cmp_to_key(compare))
    inequality = " < ".join(row["key"] for row in ordered)
    return {"ordered_keys": [row["key"] for row in ordered], "canonical_inequality": inequality,
            "normalized_terms": evaluated, "reasoning": "exact_symbolic_monotonic_order"}


def _critical_points(function: str, lo: sp.Expr, hi: sp.Expr) -> list[sp.Expr]:
    step, offset = sp.pi, (sp.pi/2 if function == "cos" else 0)
    k0 = sp.ceiling((lo-offset)/step); k1 = sp.floor((hi-offset)/step)
    return [sp.simplify(offset+k*step) for k in range(int(k0), int(k1)+1)]


def classify_trig_expression_sign_change(function: str, B: Any, C: Any, interval: list[Any], unit: str = "degree") -> dict[str, Any]:
    if len(interval) != 2: raise ValueError("closed_interval_required")
    function = str(function).lower(); fn = _fn(function)
    x0, x1 = (_angle(v, unit) for v in interval)
    if x0 > x1: x0, x1 = x1, x0
    B, C = _q(B), _angle(C, unit)
    u0, u1 = sp.simplify(B*x0+C), sp.simplify(B*x1+C)
    lo, hi = (u0, u1) if u0 <= u1 else (u1, u0)
    zeros = _critical_points(function, lo, hi)
    s0, s1 = sp.sign(fn(u0)), sp.sign(fn(u1))
    midpoint = sp.simplify((x0+x1)/2)
    derivative_sign = sp.sign(B * ({"sin": sp.cos, "cos": lambda v: -sp.sin(v), "tan": lambda v: sp.sec(v)**2}[function])(B*midpoint+C))
    monotonic = "increasing" if derivative_sign == 1 else "decreasing" if derivative_sign == -1 else "stationary"
    labels = {(1,-1): "positive_to_negative", (-1,1): "negative_to_positive", (1,1): "always_positive", (-1,-1): "always_negative", (0,0): "zero_at_both_endpoints"}
    label = labels.get((int(s0), int(s1)), "touches_zero")
    if len([z for z in zeros if lo < z < hi]) > 1: label = "multiple_sign_changes"
    return {"normalized_interval": [x0,x1], "argument_interval": [u0,u1], "endpoint_signs": [int(s0),int(s1)],
            "zero_boundaries": zeros, "monotonic_direction": monotonic,
            "classification": label, "canonical": label}


def analyze_tangent_absolute_graph_period(A: Any = 1, B: Any = 1, C: Any = 0, D: Any = 0) -> dict[str, Any]:
    A, B, C, D = map(_q, (A,B,C,D))
    if B == 0: raise ValueError("argument_scale_must_be_nonzero")
    period = sp.simplify(sp.pi/sp.Abs(B))
    range_text = f"[{_canon(D)},oo)" if A > 0 else f"(-oo,{_canon(D)}]" if A < 0 else "{"+_canon(D)+"}"
    return {"period": period, "canonical": _canon(period), "domain_exclusion": _canon((sp.pi/2-C)/B)+" + k*"+_canon(sp.pi/B),
            "range": range_text, "absolute_value": True, "drawing_reference": {"kind":"absolute_tangent_graph"}}


def count_sine_cosine_intersections(B: Any, C: Any, interval: list[Any], unit: str = "radian") -> dict[str, Any]:
    if len(interval) != 2: raise ValueError("closed_interval_required")
    B, C = _q(B), _angle(C, unit)
    if B == 0: raise ValueError("argument_scale_must_be_nonzero")
    lo, hi = (_angle(v, unit) for v in interval)
    if lo > hi: lo, hi = hi, lo
    # sin(u)=cos(u) iff u=pi/4+k*pi; solve closed interval exactly.
    low_k = sp.ceiling((min(B*lo+C, B*hi+C)-sp.pi/4)/sp.pi)
    high_k = sp.floor((max(B*lo+C, B*hi+C)-sp.pi/4)/sp.pi)
    roots = sorted(set(sp.simplify((sp.pi/4+k*sp.pi-C)/B) for k in range(int(low_k), int(high_k)+1)
                       if lo <= sp.simplify((sp.pi/4+k*sp.pi-C)/B) <= hi), key=sp.default_sort_key)
    return {"solutions": roots, "canonical_solutions": [_canon(v) for v in roots], "count": len(roots), "canonical": str(len(roots))}


def build_trigonometry_function_graph_matrix(*, operation: str | None = None,
        domain_operation: str | None = None, constraints: dict[str, Any] | None = None,
        seed: int | None = None, curriculum_profile: str | None = None,
        difficulty_profile: str | None = None, **data: Any) -> dict[str, Any]:
    op = str(operation or domain_operation or "")
    data = {**dict(constraints or {}), **data}
    if op not in OPS: raise ValueError(f"unsupported_trigonometry_function_graph_operation:{op}")
    if op == "evaluate_trig_decimal":
        requests = list(data.get("requests") or [data])
        result = [evaluate_trig_decimal(str(r["function"]), r["degrees"], minutes=r.get("minutes",0), precision=int(r.get("precision",8)), rounding=str(r.get("rounding","ROUND_HALF_UP"))) for r in requests]
        parts = {f"part_{i}": row["canonical"] for i,row in enumerate(result,1)}
        givens = {"requests": _json_value(requests)}; canonical = ";".join(parts.values())
    else:
        fn = globals()[op]; result = fn(**data); givens = _json_value(data); canonical = result.get("canonical", result.get("canonical_inequality", result.get("canonical_option")))
        if isinstance(canonical, dict):
            parts = canonical
        else: parts = {"part_1": str(canonical)}
    return {"givens": givens, "answer": {"value": canonical, "canonical_form": canonical,
                "general_form": canonical, "coefficients": [], "parts": parts},
            "question_text": data.get("question_text", op), "question": data.get("question_text", op),
            "explanation_steps": ["由 shared exact trigonometry Domain operation 計算。"], "distractors": [],
            "validation_facts": {"domain_operation": op, "exact_arithmetic": op != "evaluate_trig_decimal"},
            "visual_spec": result.get("drawing_reference", {"kind":"none"}) if isinstance(result,dict) else {"kind":"none"},
            "domain_result": _json_value(result)}


def validate_trigonometry_function_graph_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = matrix["validation_facts"]["domain_operation"]
        rebuilt = build_trigonometry_function_graph_matrix(operation=op, **matrix["givens"])
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
