"""Exact shared operations for arbitrary-angle trigonometry.

The module composes the established B2 angle/acute primitives.  It owns no
textbook-example branches and accepts only structured mathematical inputs.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

import sympy as sp

from core.domain.trigonometry_angle_domain import min_pos_max_neg_degrees
from core.domain.trigonometry_acute_domain import (
    build_trigonometry_acute_matrix,
    canonical_exact,
    compute_right_triangle_ratios,
    evaluate_special_angle_terms,
    simplify_fundamental_trig_expression,
    solve_right_triangle_projection,
)


CLASSIFY_ANGLE = "classify_standard_position_angle"
TERMINAL_RATIOS = "compute_terminal_ray_trig_ratios"
SIGNED_CONSTRAINTS = "solve_signed_trig_constraints"
ARBITRARY_EXPRESSION = "evaluate_exact_arbitrary_angle_trig_expression"
REFERENCE_CONVERSION = "complete_reference_angle_conversion"
DERIVED_POINT_QUADRANT = "classify_trig_derived_point_quadrant"
VERTICAL_PROJECTION = "solve_arbitrary_angle_vertical_projection"
FUNDAMENTAL_SIMPLIFICATION = "simplify_fundamental_trig_expression"
SUPPORTED_OPERATIONS = frozenset({
    CLASSIFY_ANGLE, TERMINAL_RATIOS, SIGNED_CONSTRAINTS,
    ARBITRARY_EXPRESSION, REFERENCE_CONVERSION,
    DERIVED_POINT_QUADRANT, VERTICAL_PROJECTION, FUNDAMENTAL_SIMPLIFICATION,
})

_FUNCS = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
_QUADRANT_SIGNS = {
    1: {"sin": 1, "cos": 1, "tan": 1},
    2: {"sin": 1, "cos": -1, "tan": -1},
    3: {"sin": -1, "cos": -1, "tan": 1},
    4: {"sin": -1, "cos": 1, "tan": -1},
}


def _rational(value: Any) -> sp.Rational:
    if isinstance(value, sp.Rational):
        return value
    if isinstance(value, Fraction):
        return sp.Rational(value.numerator, value.denominator)
    return sp.Rational(str(value))


def _degrees(angle: Any, unit: str) -> sp.Rational:
    key = str(unit or "degree").lower()
    value = _rational(angle)
    if key in {"degree", "degrees", "deg"}:
        return value
    if key in {"pi_coefficient", "pi_radian", "radian", "radians"}:
        return sp.simplify(value * 180)
    raise ValueError("angle_unit_unsupported")


def normalize_coterminal_degrees(angle: Any, *, unit: str = "degree") -> sp.Rational:
    """Normalize to [0, 360), delegating modular arithmetic to B2 1-1."""
    degrees = _degrees(angle, unit)
    pos, _ = min_pos_max_neg_degrees(Fraction(int(degrees.p), int(degrees.q)))
    return sp.S.Zero if pos == 360 else sp.Rational(pos.numerator, pos.denominator)


def classify_standard_position_angle(angle: Any, *, unit: str = "degree") -> dict[str, Any]:
    normalized = normalize_coterminal_degrees(angle, unit=unit)
    if normalized % 90 == 0:
        axis = {sp.S.Zero: "positive_x", sp.Integer(90): "positive_y",
                sp.Integer(180): "negative_x", sp.Integer(270): "negative_y"}[normalized]
        return {"kind": "quadrantal", "axis": axis, "quadrant": None, "normalized_degrees": normalized}
    quadrant = int(normalized // 90) + 1
    return {"kind": "quadrant", "axis": None, "quadrant": quadrant, "normalized_degrees": normalized}


def compute_terminal_ray_trig_ratios(*, x: Any, y: Any) -> dict[str, Any]:
    x_expr, y_expr = sp.sympify(x), sp.sympify(y)
    if x_expr.is_real is not True or y_expr.is_real is not True or (x_expr == 0 and y_expr == 0):
        raise ValueError("terminal_point_must_be_nonzero_real")
    # Reuse the exact right-triangle primitive for magnitudes; signs belong here.
    magnitude = compute_right_triangle_ratios(opposite=abs(y_expr), adjacent=abs(x_expr)) if x_expr != 0 and y_expr != 0 else None
    radius = sp.sqrt(sp.simplify(x_expr**2 + y_expr**2))
    sin_value = sp.simplify(y_expr / radius)
    cos_value = sp.simplify(x_expr / radius)
    tan_value = None if x_expr == 0 else sp.simplify(y_expr / x_expr)
    if magnitude is not None:
        assert sp.simplify(abs(sin_value) - magnitude["sin"]) == 0
        assert sp.simplify(abs(cos_value) - magnitude["cos"]) == 0
    return {"radius": radius, "sin": sin_value, "cos": cos_value, "tan": tan_value,
            "tan_defined": tan_value is not None}


def _sign(value: sp.Expr) -> int:
    value = sp.simplify(value)
    if value.is_positive is True:
        return 1
    if value.is_negative is True:
        return -1
    if value.is_zero is True:
        return 0
    raise ValueError("expression_sign_not_exactly_determinable")


def _structured_expr(node: Any, symbols: dict[str, sp.Expr], trig_resolver=None) -> sp.Expr:
    if isinstance(node, (int, Fraction, sp.Expr)):
        return sp.sympify(node)
    if isinstance(node, str):
        if node not in symbols:
            raise ValueError("unknown_symbol")
        return symbols[node]
    if not isinstance(node, dict):
        raise ValueError("structured_expression_required")
    if "value" in node:
        return sp.sympify(node["value"])
    if "symbol" in node:
        return _structured_expr(str(node["symbol"]), symbols, trig_resolver)
    if "trig" in node:
        if trig_resolver is None:
            raise ValueError("trig_expression_not_allowed")
        return trig_resolver(node)
    op, args = str(node.get("op") or ""), list(node.get("args") or [])
    values = [_structured_expr(arg, symbols, trig_resolver) for arg in args]
    if op == "add": return sp.Add(*values)
    if op == "mul": return sp.Mul(*values)
    if op == "sub" and len(values) == 2: return values[0] - values[1]
    if op == "div" and len(values) == 2: return values[0] / values[1]
    if op == "pow" and len(values) == 2: return values[0] ** values[1]
    if op == "neg" and len(values) == 1: return -values[0]
    raise ValueError("structured_expression_operator_invalid")


def solve_signed_trig_constraints(*, known: dict[str, Any] | None = None,
                                  signs: dict[str, int] | None = None,
                                  quadrant: int | None = None,
                                  relations: list[dict[str, Any]] | None = None,
                                  targets: dict[str, Any] | None = None) -> dict[str, Any]:
    s, c, t = sp.symbols("sin_theta cos_theta tan_theta", real=True)
    symbols = {"sin": s, "cos": c, "tan": t}
    requested_signs = {str(k): int(v) for k, v in dict(signs or {}).items()}
    if quadrant is not None:
        if int(quadrant) not in _QUADRANT_SIGNS: raise ValueError("quadrant_out_of_range")
        for key, value in _QUADRANT_SIGNS[int(quadrant)].items():
            if key in requested_signs and requested_signs[key] != value: raise ValueError("inconsistent_sign_constraints")
            requested_signs[key] = value
    allowed_quadrants = [q for q, row in _QUADRANT_SIGNS.items()
                         if all(row.get(k) == v for k, v in requested_signs.items())]
    equations = [s**2 + c**2 - 1, t*c-s]
    for key, value in dict(known or {}).items():
        if key not in symbols: raise ValueError("known_trig_function_unsupported")
        equations.append(symbols[key] - sp.sympify(value))
    for relation in relations or []:
        equations.append(_structured_expr(relation["lhs"], symbols) - _structured_expr(relation["rhs"], symbols))
    if len(equations) == 2:
        if len(allowed_quadrants) != 1: raise ValueError("signed_constraints_not_unique")
        return {"quadrant": allowed_quadrants[0], "solutions": [], "targets": {}}
    raw = sp.solve(equations, (s, c, t), dict=True)
    solutions = []
    for row in raw:
        values = {key: sp.simplify(row[symbols[key]]) for key in symbols}
        if all(_sign(values[key]) == value for key, value in requested_signs.items()):
            q = next((q for q in allowed_quadrants if all(_sign(values[k]) == v for k, v in _QUADRANT_SIGNS[q].items())), None)
            if q is not None: solutions.append((q, values))
    if len(solutions) != 1: raise ValueError("signed_constraints_not_unique")
    target_nodes = targets or {"sin": "sin", "cos": "cos", "tan": "tan"}
    result_targets = {key: sp.simplify(_structured_expr(node, symbols).subs({s: solutions[0][1]["sin"], c: solutions[0][1]["cos"], t: solutions[0][1]["tan"]})) for key, node in target_nodes.items()}
    return {"quadrant": solutions[0][0], "solutions": [solutions[0][1]], "targets": result_targets}


def reference_angle_conversion(function: str, angle: Any, *, unit: str = "degree") -> dict[str, Any]:
    fn = str(function).lower()
    if fn not in _FUNCS: raise ValueError("trig_function_unsupported")
    normalized = normalize_coterminal_degrees(angle, unit=unit)
    classification = classify_standard_position_angle(normalized)
    if classification["kind"] == "quadrantal":
        reference = sp.S.Zero
    else:
        q = classification["quadrant"]
        reference = {1: normalized, 2: 180-normalized, 3: normalized-180, 4: 360-normalized}[q]
    sign = 0 if classification["kind"] == "quadrantal" else _QUADRANT_SIGNS[classification["quadrant"]][fn]
    return {"function": fn, "normalized_degrees": normalized, "reference_degrees": sp.simplify(reference),
            "sign": sign, "quadrant": classification["quadrant"], "axis": classification["axis"]}


def exact_arbitrary_trig_value(function: str, angle: Any, *, unit: str = "degree") -> sp.Expr:
    conv = reference_angle_conversion(function, angle, unit=unit)
    normalized, fn = conv["normalized_degrees"], conv["function"]
    if conv["axis"] is not None:
        rad = sp.pi * normalized / 180
        value = sp.simplify(_FUNCS[fn](rad))
        if value in {sp.zoo, sp.nan}: raise ValueError("trig_value_undefined")
        return value
    # Reuse the exact B2 1-2 special-angle operation; no local value table.
    magnitude = evaluate_special_angle_terms([{"function": fn, "angle": conv["reference_degrees"], "unit": "degree", "power": 1}])
    return sp.simplify(conv["sign"] * magnitude)


def evaluate_exact_arbitrary_angle_trig_expression(expression: Any) -> sp.Expr:
    def resolve(node: dict[str, Any]) -> sp.Expr:
        return exact_arbitrary_trig_value(node["trig"], node["angle"], unit=node.get("unit", "degree"))
    # Delegate final identity reduction to the established B2 1-2 operation.
    return simplify_fundamental_trig_expression(_structured_expr(expression, {}, resolve))


def complete_reference_angle_conversion(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items: raise ValueError("reference_conversion_items_required")
    return [reference_angle_conversion(item["function"], item["angle"], unit=item.get("unit", "degree")) for item in items]


def validate_reference_angle_conversion_ast(submission: dict[str, Any], expected: dict[str, Any]) -> bool:
    """Validate required form from parsed structure, without text/regex grading."""
    try:
        if set(submission) != {"function", "reference_degrees", "sign"}:
            return False
        if str(submission["function"]).lower() != str(expected["function"]).lower():
            return False
        if int(submission["sign"]) != int(expected["sign"]):
            return False
        return sp.simplify(sp.sympify(submission["reference_degrees"]) - sp.sympify(expected["reference_degrees"])) == 0
    except (TypeError, ValueError, sp.SympifyError):
        return False


def classify_trig_derived_point_quadrant(*, source: dict[str, Any], x_expression: Any, y_expression: Any) -> dict[str, Any]:
    if source.get("kind") == "terminal_point":
        ratios = compute_terminal_ray_trig_ratios(x=source["x"], y=source["y"])
        symbols = {k: v for k, v in ratios.items() if k in _FUNCS and v is not None}
        trig_resolver = None
    elif source.get("kind") == "angle":
        symbols = {}
        def trig_resolver(node: dict[str, Any]) -> sp.Expr:
            fn = node["trig"]
            raw_angle = node.get("angle", source["angle"])
            raw_unit = node.get("unit", source.get("unit", "degree"))
            try:
                return exact_arbitrary_trig_value(fn, raw_angle, unit=raw_unit)
            except ValueError as exc:
                if str(exc) != "exact_special_angle_unsupported":
                    raise
                conversion = reference_angle_conversion(fn, raw_angle, unit=raw_unit)
                if conversion["sign"] == 0:
                    return sp.S.Zero
                magnitude = sp.Symbol(
                    f"abs_{fn}_{canonical_exact(conversion['reference_degrees'])}",
                    positive=True,
                )
                return conversion["sign"] * magnitude
    else:
        raise ValueError("derived_point_source_invalid")
    x_value = sp.simplify(_structured_expr(x_expression, symbols, trig_resolver))
    y_value = sp.simplify(_structured_expr(y_expression, symbols, trig_resolver))
    sx, sy = _sign(x_value), _sign(y_value)
    if sx == 0 or sy == 0: return {"quadrant": None, "axis": "y" if sx == 0 else "x", "x": x_value, "y": y_value}
    quadrant = {(1,1):1,(-1,1):2,(-1,-1):3,(1,-1):4}[(sx,sy)]
    return {"quadrant": quadrant, "axis": None, "x": x_value, "y": y_value}


def solve_arbitrary_angle_vertical_projection(*, radius: Any, angle: Any, unit: str = "degree", base_elevation: Any = 0) -> dict[str, Any]:
    radius_expr = sp.sympify(radius)
    if radius_expr.is_positive is not True: raise ValueError("radius_must_be_positive")
    conv = reference_angle_conversion("sin", angle, unit=unit)
    if conv["axis"] is None:
        delegated = solve_right_triangle_projection(
            hypotenuse=radius_expr, angle=conv["reference_degrees"], unit="degree"
        )
        vertical_magnitude = delegated["vertical_projection"]
        vertical = sp.simplify(conv["sign"] * vertical_magnitude)
    else:
        delegated = None
        vertical = sp.simplify(radius_expr * exact_arbitrary_trig_value("sin", angle, unit=unit))
    return {"vertical_projection": vertical, "elevation": sp.simplify(sp.sympify(base_elevation)+vertical),
            "reference_conversion": conv, "projection_delegate": delegated}


def _answer(canonical: str, parts: dict[str, str] | None = None) -> dict[str, Any]:
    return {"canonical_form": canonical, "general_form": canonical, "coefficients": [],
            "parts": parts or {}, "value": parts if parts is not None else canonical}


def _json_exact(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return canonical_exact(value)
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): _json_exact(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_exact(item) for item in value]
    return value


def build_trigonometry_arbitrary_matrix(*, seed: int | None, domain_operation: str | None = None,
        line_type: str | None = None, curriculum_profile: str | None = None,
        difficulty_profile: str | None = None, constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    op = str(domain_operation or line_type or "")
    if op not in SUPPORTED_OPERATIONS: raise ValueError(f"unsupported_trigonometry_arbitrary_operation:{op}")
    rng, data = random.Random(0 if seed is None else seed), dict(constraints or {})
    if op == CLASSIFY_ANGLE:
        data.setdefault("angle", rng.choice([-420, -135, 630, 855])); data.setdefault("unit", "degree")
        result = classify_standard_position_angle(data["angle"], unit=data["unit"]); answer = _answer(result["axis"] or str(result["quadrant"])); question = "判斷標準位置角的終邊位置。"
    elif op == TERMINAL_RATIOS:
        data.setdefault("x", -4); data.setdefault("y", 3); result = compute_terminal_ray_trig_ratios(x=data["x"], y=data["y"])
        parts={k:("undefined" if result[k] is None else canonical_exact(result[k])) for k in ("sin","cos","tan")}; answer=_answer(";".join(parts.values()),parts); question="由終邊點求 sin、cos、tan。"
    elif op == SIGNED_CONSTRAINTS:
        if not any(key in data for key in ("known", "signs", "quadrant", "relations", "targets")):
            data.update({"known": {"sin": sp.Rational(-5,13)}, "signs": {"tan":1}, "targets": {"cos":"cos","tan":"tan"}})
        result=solve_signed_trig_constraints(known=data.get("known"),signs=data.get("signs"),quadrant=data.get("quadrant"),relations=data.get("relations"),targets=data.get("targets")); parts={k:canonical_exact(v) for k,v in result["targets"].items()} or {"quadrant":str(result["quadrant"])}; answer=_answer(";".join(parts.values()),parts); question="依任意角符號與三角關係求解。"
    elif op == ARBITRARY_EXPRESSION:
        data.setdefault("expression", {"trig":"sin","angle":-930,"unit":"degree"}); result=evaluate_exact_arbitrary_angle_trig_expression(data["expression"]); answer=_answer(canonical_exact(result)); question="求任意角三角函數式的精確值。"
    elif op == REFERENCE_CONVERSION:
        data.setdefault("items", [{"function":"sin","angle":-30,"unit":"degree"}]); result=complete_reference_angle_conversion(data["items"]); parts={f"part_{i}":f"{row['sign']}:{canonical_exact(row['reference_degrees'])}" for i,row in enumerate(result,1)}; answer=_answer(";".join(parts.values()),parts); question="完成參考角與正負號轉換。"
    elif op == DERIVED_POINT_QUADRANT:
        data.setdefault("source", {"kind":"angle","angle":120,"unit":"degree"}); data.setdefault("x_expression", {"trig":"sin","angle":120}); data.setdefault("y_expression", {"trig":"cos","angle":120}); result=classify_trig_derived_point_quadrant(source=data["source"],x_expression=data["x_expression"],y_expression=data["y_expression"]); answer=_answer(str(result["quadrant"] or result["axis"])); question="判斷三角函數衍生點所在象限。"
    elif op == VERTICAL_PROJECTION:
        data.setdefault("radius",50); data.setdefault("angle",120); data.setdefault("unit","degree"); data.setdefault("base_elevation",100); result=solve_arbitrary_angle_vertical_projection(radius=data["radius"],angle=data["angle"],unit=data["unit"],base_elevation=data["base_elevation"]); answer=_answer(canonical_exact(result["elevation"])); question="求任意角垂直投影後的高度。"
    else:
        return build_trigonometry_acute_matrix(
            seed=seed,
            domain_operation=FUNDAMENTAL_SIMPLIFICATION,
            line_type=line_type,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            constraints=data,
        )
    return {"givens":{"question_text":question,**_json_exact(data)},"answer":answer,"distractors":[],
        "explanation_steps":["使用共用精確三角運算求得 canonical answer。"],
        "validation_facts":{"domain_operation":op,"task_type":op,"curriculum_profile":curriculum_profile or "vocational_high_b","difficulty_profile":difficulty_profile or "easy","exact_arithmetic":True},
        "visual_spec":{"kind":"none","points":[],"lines":[]},"question_text":question,"question":question}


def validate_trigonometry_arbitrary_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op=matrix["validation_facts"]["domain_operation"]
        if op not in SUPPORTED_OPERATIONS or matrix["validation_facts"].get("exact_arithmetic") is not True:
            return False
        rebuilt=build_trigonometry_arbitrary_matrix(seed=0,domain_operation=op,constraints={k:v for k,v in matrix["givens"].items() if k!="question_text"})
        if rebuilt["answer"] != matrix["answer"]:
            return False
        givens = matrix["givens"]
        if op == TERMINAL_RATIOS:
            ratios = compute_terminal_ray_trig_ratios(x=givens["x"], y=givens["y"])
            if sp.simplify(ratios["sin"] ** 2 + ratios["cos"] ** 2 - 1) != 0:
                return False
            if ratios["tan_defined"] and sp.simplify(ratios["tan"] - ratios["sin"] / ratios["cos"]) != 0:
                return False
            if not ratios["tan_defined"] and sp.sympify(givens["x"]) != 0:
                return False
        elif op == SIGNED_CONSTRAINTS:
            result = solve_signed_trig_constraints(
                known=givens.get("known"), signs=givens.get("signs"), quadrant=givens.get("quadrant"),
                relations=givens.get("relations"), targets=givens.get("targets"),
            )
            for row in result["solutions"]:
                if sp.simplify(row["sin"] ** 2 + row["cos"] ** 2 - 1) != 0:
                    return False
                if row["cos"] != 0 and sp.simplify(row["tan"] - row["sin"] / row["cos"]) != 0:
                    return False
        elif op == VERTICAL_PROJECTION:
            result = solve_arbitrary_angle_vertical_projection(
                radius=givens["radius"], angle=givens["angle"], unit=givens["unit"],
                base_elevation=givens.get("base_elevation", 0),
            )
            if sp.simplify(result["elevation"] - sp.sympify(givens.get("base_elevation", 0)) - result["vertical_projection"]) != 0:
                return False
        return True
    except (KeyError, TypeError, ValueError, AssertionError, ZeroDivisionError):
        return False
