# -*- coding: utf-8 -*-
"""Shared exact acute-angle trigonometry operations for Math B2."""

from __future__ import annotations

import random
from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Any

import sympy as sp

from core.domain.trigonometry_angle_domain import pi_coeff_to_degrees


RIGHT_TRIANGLE_OP = "compute_right_triangle_trig_ratios"
SPECIAL_ANGLE_OP = "evaluate_exact_special_angle_expression"
COFUNCTION_OP = "complete_cofunction_identity"
ACUTE_CONSTRAINT_OP = "solve_acute_trig_constraints"
PROJECTION_OP = "solve_right_triangle_projection"
DECIMAL_OP = "evaluate_trig_decimal"
SIMPLIFY_OP = "simplify_fundamental_trig_expression"
COLLINEAR_OP = "collinear_three_points_parameter"
SECTOR_OP = "sector_arc_and_area"
CHORD_ARC_OP = "compute_chord_and_arc_length"
SUPPORTED_OPERATIONS = frozenset(
    {
        RIGHT_TRIANGLE_OP, SPECIAL_ANGLE_OP, COFUNCTION_OP,
        ACUTE_CONSTRAINT_OP, PROJECTION_OP, DECIMAL_OP, SIMPLIFY_OP,
        COLLINEAR_OP, SECTOR_OP, CHORD_ARC_OP,
    }
)
_TRIG_FUNCTIONS = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
_COFUNCTION = {"sin": "cos", "cos": "sin"}


def canonical_exact(value: Any) -> str:
    """Return a stable exact expression, never a floating approximation."""
    return sp.sstr(sp.radsimp(sp.simplify(value)), order="lex")


def _positive_exact(value: Any, *, name: str) -> sp.Expr:
    try:
        result = sp.sympify(value)
    except (sp.SympifyError, TypeError) as exc:
        raise ValueError(f"{name}_must_be_exact_numeric") from exc
    if result.is_real is not True or result.is_positive is not True:
        raise ValueError(f"{name}_must_be_positive")
    return result


def _acute_degrees(angle: Any, unit: str = "degree") -> sp.Rational:
    if unit in {"radian", "radians", "pi_radian", "pi_coefficient"}:
        degrees = sp.Rational(pi_coeff_to_degrees(angle))
    elif unit in {"degree", "degrees", "deg"}:
        degrees = sp.Rational(str(angle))
    else:
        raise ValueError("angle_unit_unsupported")
    if not (0 < degrees < 90):
        raise ValueError("angle_must_be_positive_acute")
    return degrees


def compute_right_triangle_ratios(*, opposite: Any, adjacent: Any, hypotenuse: Any | None = None) -> dict[str, sp.Expr]:
    opposite_expr = _positive_exact(opposite, name="opposite")
    adjacent_expr = _positive_exact(adjacent, name="adjacent")
    calculated_hypotenuse = sp.sqrt(opposite_expr**2 + adjacent_expr**2)
    if hypotenuse is not None:
        supplied = _positive_exact(hypotenuse, name="hypotenuse")
        if sp.simplify(supplied**2 - calculated_hypotenuse**2) != 0:
            raise ValueError("right_triangle_pythagorean_inconsistent")
        calculated_hypotenuse = supplied
    return {
        "sin": sp.simplify(opposite_expr / calculated_hypotenuse),
        "cos": sp.simplify(adjacent_expr / calculated_hypotenuse),
        "tan": sp.simplify(opposite_expr / adjacent_expr),
        "hypotenuse": sp.simplify(calculated_hypotenuse),
    }


def exact_special_angle_value(function: str, angle: Any, *, unit: str = "degree") -> sp.Expr:
    function_key = str(function).strip().lower()
    if function_key not in _TRIG_FUNCTIONS:
        raise ValueError("trig_function_unsupported")
    degrees = _acute_degrees(angle, unit)
    if degrees not in {sp.Rational(30), sp.Rational(45), sp.Rational(60)}:
        raise ValueError("exact_special_angle_unsupported")
    return sp.simplify(_TRIG_FUNCTIONS[function_key](sp.pi * degrees / 180))


def evaluate_special_angle_terms(terms: list[dict[str, Any]]) -> sp.Expr:
    if not isinstance(terms, list) or not terms:
        raise ValueError("special_angle_expression_requires_terms")
    total = sp.S.Zero
    for term in terms:
        if not isinstance(term, dict):
            raise ValueError("special_angle_term_must_be_mapping")
        coefficient = sp.sympify(term.get("coefficient", 1))
        power = int(term.get("power", 1))
        if power < 0:
            raise ValueError("special_angle_power_must_be_nonnegative")
        value = exact_special_angle_value(
            str(term.get("function") or ""),
            term.get("angle"),
            unit=str(term.get("unit") or "degree"),
        )
        total += coefficient * value**power
    return sp.simplify(total)


def complete_cofunction(function: str, angle: Any, *, unit: str = "degree") -> dict[str, Any]:
    function_key = str(function).strip().lower()
    if function_key not in _COFUNCTION:
        raise ValueError("cofunction_requires_sin_or_cos")
    degrees = _acute_degrees(angle, unit)
    complement = sp.Rational(90) - degrees
    return {
        "cofunction": _COFUNCTION[function_key],
        "complement_degrees": complement,
        "left_value": sp.simplify(_TRIG_FUNCTIONS[function_key](sp.pi * degrees / 180)),
        "right_value": sp.simplify(_TRIG_FUNCTIONS[_COFUNCTION[function_key]](sp.pi * complement / 180)),
    }


def _trusted_trig_expr(value: Any, *, symbols: dict[str, Any]) -> sp.Expr:
    """Parse repository-owned constraint/expression data with a closed namespace."""
    if isinstance(value, sp.Expr):
        return value
    try:
        return sp.sympify(str(value), locals=symbols, evaluate=True)
    except (sp.SympifyError, TypeError) as exc:
        raise ValueError("invalid_trig_expression") from exc


def solve_acute_trig_constraints(
    *,
    known: dict[str, Any] | None = None,
    relations: list[Any] | tuple[Any, ...] | None = None,
    targets: dict[str, Any] | list[Any] | tuple[Any, ...] | None = None,
) -> dict[str, Any]:
    """Solve exact trig constraints on 0 < theta < pi/2.

    Invalid negative branches are discarded. If a target genuinely remains
    ambiguous, its exact solution set is retained rather than guessing a sign.
    """
    s, c, t = sp.symbols("sin_theta cos_theta tan_theta", real=True)
    namespace = {
        "sin_theta": s, "cos_theta": c, "tan_theta": t,
        "s": s, "c": c, "t": t, "sqrt": sp.sqrt, "pi": sp.pi,
    }
    aliases = {"sin": s, "sin_theta": s, "cos": c, "cos_theta": c, "tan": t, "tan_theta": t}
    equations: list[sp.Expr] = [s**2 + c**2 - 1, t * c - s]
    for key, raw_value in dict(known or {}).items():
        normalized_key = str(key).strip().lower()
        if normalized_key not in aliases:
            raise ValueError("known_trig_function_unsupported")
        equations.append(aliases[normalized_key] - sp.sympify(raw_value))
    for relation in relations or ():
        if isinstance(relation, sp.Equality):
            equations.append(relation.lhs - relation.rhs)
        elif isinstance(relation, (list, tuple)) and len(relation) == 2:
            equations.append(
                _trusted_trig_expr(relation[0], symbols=namespace)
                - _trusted_trig_expr(relation[1], symbols=namespace)
            )
        else:
            text = str(relation)
            if "=" not in text:
                raise ValueError("trig_relation_requires_equality")
            lhs, rhs = text.split("=", 1)
            equations.append(
                _trusted_trig_expr(lhs, symbols=namespace)
                - _trusted_trig_expr(rhs, symbols=namespace)
            )
    if len(equations) == 2:
        raise ValueError("acute_trig_constraints_require_a_given")

    raw_solutions = sp.solve(equations, (s, c, t), dict=True)
    solutions: list[dict[str, sp.Expr]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in raw_solutions:
        values = {"sin": sp.simplify(row[s]), "cos": sp.simplify(row[c]), "tan": sp.simplify(row[t])}
        if not all(value.is_real is True and value.is_positive is True for value in values.values()):
            continue
        identity = tuple(canonical_exact(values[name]) for name in ("sin", "cos", "tan"))
        if identity not in seen:
            seen.add(identity)
            solutions.append(values)
    if not solutions:
        raise ValueError("acute_trig_constraints_have_no_positive_solution")
    solutions.sort(key=lambda row: tuple(canonical_exact(row[name]) for name in ("sin", "cos", "tan")))

    if targets is None:
        target_map: dict[str, Any] = {"sin": s, "cos": c, "tan": t}
    elif isinstance(targets, dict):
        target_map = dict(targets)
    else:
        target_map = {f"part_{index}": value for index, value in enumerate(targets, 1)}
    target_results: dict[str, dict[str, Any]] = {}
    for key, raw_expr in target_map.items():
        expr = _trusted_trig_expr(raw_expr, symbols=namespace)
        unique: dict[str, sp.Expr] = {}
        for solution in solutions:
            value = sp.simplify(expr.subs({s: solution["sin"], c: solution["cos"], t: solution["tan"]}))
            unique[canonical_exact(value)] = value
        ordered = tuple(unique[name] for name in sorted(unique))
        target_results[str(key)] = {
            "values": ordered,
            "unique": len(ordered) == 1,
            "canonical": canonical_exact(ordered[0]) if len(ordered) == 1 else "{" + ",".join(canonical_exact(v) for v in ordered) + "}",
        }
    return {"solutions": solutions, "targets": target_results, "angle_domain": "acute"}


def solve_right_triangle_projection(
    *, hypotenuse: Any, angle: Any, unit: str = "degree", base_elevation: Any | None = None
) -> dict[str, Any]:
    length = _positive_exact(hypotenuse, name="hypotenuse")
    degrees = _acute_degrees(angle, unit)
    horizontal = sp.simplify(length * sp.cos(sp.pi * degrees / 180))
    vertical = sp.simplify(length * sp.sin(sp.pi * degrees / 180))
    result: dict[str, Any] = {
        "horizontal_projection": horizontal,
        "vertical_projection": vertical,
        "hypotenuse": length,
        "angle_degrees": degrees,
    }
    if base_elevation is not None:
        base = sp.sympify(base_elevation)
        if base.is_real is not True:
            raise ValueError("base_elevation_must_be_real")
        result.update({"base_elevation": base, "elevation": sp.simplify(base + vertical)})
    return result


def evaluate_trig_decimal(
    function: str,
    degrees: Any,
    *,
    minutes: Any = 0,
    precision: int = 8,
    rounding: str = "ROUND_HALF_UP",
) -> dict[str, Any]:
    function_key = str(function).strip().lower()
    if function_key not in _TRIG_FUNCTIONS:
        raise ValueError("trig_function_unsupported")
    if not isinstance(precision, int) or not 1 <= precision <= 15:
        raise ValueError("decimal_precision_out_of_range")
    if rounding != "ROUND_HALF_UP":
        raise ValueError("decimal_rounding_policy_unsupported")
    total_minutes = sp.Rational(str(degrees)) * 60 + sp.Rational(str(minutes))
    normalized_degrees = sp.simplify(total_minutes / 60)
    if not (0 < normalized_degrees < 90):
        raise ValueError("angle_must_be_positive_acute")
    radians = sp.pi * normalized_degrees / 180
    with localcontext() as context:
        context.prec = precision + 18
        raw = Decimal(str(sp.N(_TRIG_FUNCTIONS[function_key](radians), precision + 16)))
        quantum = Decimal(1).scaleb(-precision)
        rounded = raw.quantize(quantum, rounding=ROUND_HALF_UP)
    return {
        "value": rounded,
        "canonical": format(rounded, f".{precision}f"),
        "normalized_degrees": normalized_degrees,
        "precision": precision,
        "rounding": rounding,
        "tolerance": Decimal(5).scaleb(-(precision + 1)),
    }


def simplify_fundamental_trig_expression(expression: Any) -> sp.Expr:
    theta = sp.symbols("theta", real=True)
    namespace = {
        "theta": theta,
        "sin_theta": sp.sin(theta), "cos_theta": sp.cos(theta), "tan_theta": sp.tan(theta),
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt, "pi": sp.pi,
    }
    expr = _trusted_trig_expr(expression, symbols=namespace)
    return sp.simplify(sp.trigsimp(sp.expand(expr), method="fu"))


def _build_collinear_delegate(*, seed: int | None, constraints: dict[str, Any]) -> dict[str, Any]:
    """Delegate without copying coordinate-geometry collinearity solving logic."""
    from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix

    matrix = build_line_equation_matrix(
        seed=seed,
        line_type=COLLINEAR_OP,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    matrix.setdefault("validation_facts", {})["domain_operation"] = COLLINEAR_OP
    matrix["validation_facts"]["cross_domain_delegate"] = "coordinate_geometry.line_equation"
    return matrix


def _build_sector_delegate(*, seed: int | None, constraints: dict[str, Any]) -> dict[str, Any]:
    """Delegate the complete sector operation to its existing angle domain."""
    from core.domain.trigonometry_angle_domain import build_trigonometry_angle_matrix

    matrix = build_trigonometry_angle_matrix(seed=seed, domain_operation=SECTOR_OP, constraints=constraints)
    matrix.setdefault("validation_facts", {})["cross_domain_delegate"] = "trigonometry.angle.sector_arc_and_area"
    return matrix


def compute_chord_and_arc_length(*, radius: Any, central_angle: Any, unit: str = "degree") -> dict[str, Any]:
    radius_expr = _positive_exact(radius, name="radius")
    degrees = _acute_degrees(central_angle, unit)
    chord = sp.simplify(2 * radius_expr * exact_special_angle_value("sin", degrees / 2))

    # Arc calculation is delegated to the existing sector operation. This
    # operation intentionally contains no local copy of s=r*theta.
    from core.domain.trigonometry_angle_domain import build_trigonometry_angle_matrix

    sector = build_trigonometry_angle_matrix(
        seed=0,
        domain_operation=SECTOR_OP,
        constraints={
            "variant": "given_angle",
            "radius": int(radius_expr) if radius_expr.is_Integer else str(radius_expr),
            "theta_degrees": str(degrees),
            "include_convert": False,
        },
    )
    arc = sp.sympify(sector["answer"]["parts"]["part_1"])
    return {
        "chord_length": chord,
        "arc_length": arc,
        "radius": radius_expr,
        "central_angle_degrees": degrees,
        "sector_delegate": sector,
    }


def _answer_bundle(canonical: str, *, parts: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": [],
        "parts": parts or {},
        "value": parts if parts is not None else canonical,
    }


def build_trigonometry_acute_matrix(
    *, seed: int | None,
    line_type: str | None = None,
    domain_operation: str | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    op = str(domain_operation or line_type or "").strip()
    if op not in SUPPORTED_OPERATIONS:
        raise ValueError(f"Unsupported trigonometry.acute operation: {op!r}")
    rng = random.Random(0 if seed is None else seed)
    data = dict(constraints or {})
    distractors: list[str] = []
    if op == COLLINEAR_OP:
        return _build_collinear_delegate(seed=seed, constraints=data)
    if op == SECTOR_OP:
        return _build_sector_delegate(seed=seed, constraints=data)
    if op == RIGHT_TRIANGLE_OP:
        opposite, adjacent, hypotenuse = data.get("opposite"), data.get("adjacent"), data.get("hypotenuse")
        if opposite is None or adjacent is None:
            opposite, adjacent, hypotenuse = rng.choice(((3, 4, 5), (5, 12, 13), (8, 15, 17)))
        ratios = compute_right_triangle_ratios(opposite=opposite, adjacent=adjacent, hypotenuse=hypotenuse)
        parts = {key: canonical_exact(ratios[key]) for key in ("sin", "cos", "tan")}
        question = f"直角三角形中，銳角的對邊為 {opposite}、鄰邊為 {adjacent}，求 sin、cos、tan。"
        answer = _answer_bundle(";".join(f"{k}={v}" for k, v in parts.items()), parts=parts)
        givens = {"question_text": question, "opposite": opposite, "adjacent": adjacent, "hypotenuse": canonical_exact(ratios["hypotenuse"])}
        steps = ["先以畢氏定理解出斜邊。", "依 sin=對邊/斜邊、cos=鄰邊/斜邊、tan=對邊/鄰邊計算。"]
    elif op == SPECIAL_ANGLE_OP:
        terms = data.get("terms") or [{"coefficient": 1, "function": "sin", "angle": rng.choice((30, 45, 60)), "unit": "degree", "power": 1}]
        result = evaluate_special_angle_terms(terms)
        canonical = canonical_exact(result)
        question = "求指定特殊銳角三角函數式的精確值。"
        answer = _answer_bundle(canonical)
        givens = {"question_text": question, "terms": terms}
        steps = ["將各特殊角代入精確三角函數值。", "以符號運算化簡，不取小數近似。"]
    elif op == COFUNCTION_OP:
        function = str(data.get("function") or rng.choice(("sin", "cos")))
        angle = data.get("angle", rng.choice((20, 30, 35, 40)))
        unit = str(data.get("unit") or "degree")
        result = complete_cofunction(function, angle, unit=unit)
        parts = {"cofunction": result["cofunction"], "complement_degrees": canonical_exact(result["complement_degrees"])}
        question = f"完成餘函數關係：{function}({angle}°)=＿＿(＿＿°)。"
        answer = _answer_bundle(f"{parts['cofunction']}({parts['complement_degrees']}*pi/180)", parts=parts)
        givens = {"question_text": question, "function": function, "angle": angle, "unit": unit}
        steps = ["兩個互餘銳角的和為 90°。", "sin 與 cos 互為餘函數。"]
    elif op == ACUTE_CONSTRAINT_OP:
        # The default sample is only valid when no explicit relation was supplied.
        # Relation-only textbook items must not receive an unrelated tan constraint.
        known = data.get("known") or ({} if data.get("relations") else {"tan": sp.Rational(3, 4)})
        targets = data.get("targets") or {"sin": "sin_theta", "cos": "cos_theta"}
        result = solve_acute_trig_constraints(known=known, relations=data.get("relations"), targets=targets)
        parts = {key: row["canonical"] for key, row in result["targets"].items()}
        question = "在銳角條件下，依已知三角關係求指定各式的精確值。"
        choice_options = list(data.get("choice_options") or [])
        if choice_options:
            if len(result["targets"]) != 1:
                raise ValueError("semantic_choice_requires_one_target")
            target = next(iter(result["targets"].values()))
            if not target["unique"]:
                raise ValueError("semantic_choice_requires_unique_target_value")
            target_value = target["values"][0]
            matching = [
                option for option in choice_options
                if sp.sympify(option["lower"]) < target_value < sp.sympify(option["upper"])
            ]
            if len(matching) != 1:
                raise ValueError("single_choice_requires_unique_semantic_answer")
            semantic = str(matching[0]["semantic"])
            answer = _answer_bundle(semantic)
            answer["target_value"] = canonical_exact(target_value)
            distractors = [str(option["semantic"]) for option in choice_options if option is not matching[0]]
        else:
            answer = _answer_bundle(";".join(f"{k}={v}" for k, v in parts.items()), parts=parts)
        givens = {
            "question_text": question, "known": {str(key): canonical_exact(value) for key, value in known.items()},
            "relations": data.get("relations") or [], "targets": targets,
            "source_choices": [
                {"label": str(option.get("label") or chr(65 + index)), "text": str(option["semantic"]), "value": str(option["semantic"])}
                for index, option in enumerate(choice_options)
            ],
            "choice_options": choice_options,
        }
        steps = ["加入 sin²θ+cos²θ=1 與 tanθ=sinθ/cosθ。", "只保留三角函數值皆為正的銳角解。"]
    elif op == PROJECTION_OP:
        result = solve_right_triangle_projection(
            hypotenuse=data.get("hypotenuse", 10), angle=data.get("angle", 30),
            unit=str(data.get("unit") or "degree"), base_elevation=data.get("base_elevation"),
        )
        requested = list(data.get("requested") or (
            ["elevation", "horizontal_projection"]
            if data.get("base_elevation") is not None
            else ["vertical_projection", "horizontal_projection"]
        ))
        parts = {key: canonical_exact(result[key]) for key in requested}
        question = "由斜邊與銳角求直角三角形的水平、垂直投影或標高。"
        answer = _answer_bundle(";".join(f"{k}={v}" for k, v in parts.items()), parts=parts)
        givens = {
            "question_text": question, "hypotenuse": canonical_exact(result["hypotenuse"]),
            "angle": data.get("angle", 30), "unit": str(data.get("unit") or "degree"),
            "base_elevation": data.get("base_elevation"), "requested": requested,
            "length_unit": str(data.get("length_unit") or "unit"),
        }
        steps = ["水平投影為斜邊乘 cosθ，垂直投影為斜邊乘 sinθ。", "若有起點標高，再加上垂直投影。"]
    elif op == DECIMAL_OP:
        requests = list(data.get("requests") or [
            {"function": "sin", "degrees": 40, "minutes": 0, "precision": 9}
        ])
        evaluated = [
            evaluate_trig_decimal(
                str(row["function"]), row["degrees"], minutes=row.get("minutes", 0),
                precision=int(row.get("precision", 8)), rounding=str(row.get("rounding") or "ROUND_HALF_UP"),
            )
            for row in requests
        ]
        parts = {f"part_{index}": row["canonical"] for index, row in enumerate(evaluated, 1)}
        question = "計算指定銳角三角函數的十進位近似值。"
        answer = _answer_bundle(";".join(parts.values()), parts=parts)
        givens = {"question_text": question, "requests": requests}
        steps = ["將度、分正規化為總角度。", "以 Decimal 與明示 ROUND_HALF_UP 位數輸出。"]
    elif op == SIMPLIFY_OP:
        expressions = data.get("expressions") or {"part_1": "tan_theta*cos_theta"}
        if not isinstance(expressions, dict):
            expressions = {"part_1": expressions}
        parts = {
            str(key): canonical_exact(simplify_fundamental_trig_expression(value))
            for key, value in expressions.items()
        }
        question = "使用基本三角恆等式化簡各式。"
        answer = _answer_bundle(";".join(f"{k}={v}" for k, v in parts.items()), parts=parts)
        givens = {
            "question_text": question, "expressions": expressions,
            "required_form": data.get("required_form") or "simplified_trig",
        }
        steps = ["使用 tanθ=sinθ/cosθ。", "再用 sin²θ+cos²θ=1 展開或化簡。"]
    else:
        result = compute_chord_and_arc_length(
            radius=data.get("radius", 2), central_angle=data.get("central_angle", 60),
            unit=str(data.get("unit") or "degree"),
        )
        parts = {
            "chord_length": canonical_exact(result["chord_length"]),
            "arc_length": canonical_exact(result["arc_length"]),
        }
        question = "由半徑與圓心角求弦長與弧長。"
        answer = _answer_bundle(";".join(f"{k}={v}" for k, v in parts.items()), parts=parts)
        givens = {
            "question_text": question, "radius": canonical_exact(result["radius"]),
            "central_angle": data.get("central_angle", 60), "unit": str(data.get("unit") or "degree"),
            "length_unit": str(data.get("length_unit") or "unit"),
        }
        steps = ["弦長使用 shared exact trig capability。", "弧長委派既有 sector_arc_and_area operation。"]
    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": steps,
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "exact_arithmetic": op != DECIMAL_OP,
            "cross_domain_delegate": (
                "coordinate_geometry.line_equation" if op == COLLINEAR_OP
                else "trigonometry.angle.sector_arc_and_area" if op in {SECTOR_OP, CHORD_ARC_OP}
                else None
            ),
        },
        "visual_spec": {"kind": "none", "points": [], "lines": []},
        "question_text": question,
        "question": question,
    }


def validate_acute_trigonometry_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = str(matrix["validation_facts"]["domain_operation"])
        givens, answer = matrix["givens"], matrix["answer"]
        if op == RIGHT_TRIANGLE_OP:
            expected = compute_right_triangle_ratios(opposite=givens["opposite"], adjacent=givens["adjacent"], hypotenuse=givens["hypotenuse"])
            parts = answer["parts"]
            return all(sp.simplify(sp.sympify(parts[key]) - expected[key]) == 0 for key in ("sin", "cos", "tan")) and sp.simplify(expected["sin"]**2 + expected["cos"]**2 - 1) == 0 and sp.simplify(expected["tan"] - expected["sin"] / expected["cos"]) == 0
        if op == SPECIAL_ANGLE_OP:
            return sp.simplify(sp.sympify(answer["canonical_form"]) - evaluate_special_angle_terms(givens["terms"])) == 0
        if op == COFUNCTION_OP:
            expected = complete_cofunction(givens["function"], givens["angle"], unit=givens["unit"])
            parts = answer["parts"]
            return parts["cofunction"] == expected["cofunction"] and sp.Rational(parts["complement_degrees"]) == expected["complement_degrees"] and sp.simplify(expected["left_value"] - expected["right_value"]) == 0
        if op == ACUTE_CONSTRAINT_OP:
            expected = solve_acute_trig_constraints(
                known=givens["known"], relations=givens.get("relations"), targets=givens["targets"]
            )
            if givens.get("choice_options"):
                target = next(iter(expected["targets"].values()))
                if not target["unique"]:
                    return False
                value = target["values"][0]
                matching = [
                    option for option in givens["choice_options"]
                    if sp.sympify(option["lower"]) < value < sp.sympify(option["upper"])
                ]
                return len(matching) == 1 and answer["canonical_form"] == str(matching[0]["semantic"])
            return all(
                answer["parts"][key] == row["canonical"]
                for key, row in expected["targets"].items()
            ) and all(
                sp.simplify(row["sin"]**2 + row["cos"]**2 - 1) == 0
                and sp.simplify(row["tan"] * row["cos"] - row["sin"]) == 0
                and all(value.is_positive is True for value in row.values())
                for row in expected["solutions"]
            )
        if op == PROJECTION_OP:
            expected = solve_right_triangle_projection(
                hypotenuse=givens["hypotenuse"], angle=givens["angle"], unit=givens["unit"],
                base_elevation=givens.get("base_elevation"),
            )
            return all(
                sp.simplify(sp.sympify(answer["parts"][key]) - expected[key]) == 0
                for key in givens["requested"]
            ) and sp.simplify(
                expected["horizontal_projection"]**2
                + expected["vertical_projection"]**2
                - expected["hypotenuse"]**2
            ) == 0 and expected["horizontal_projection"].is_positive is True and expected["vertical_projection"].is_positive is True
        if op == DECIMAL_OP:
            expected = [
                evaluate_trig_decimal(
                    str(row["function"]), row["degrees"], minutes=row.get("minutes", 0),
                    precision=int(row.get("precision", 8)), rounding=str(row.get("rounding") or "ROUND_HALF_UP"),
                )
                for row in givens["requests"]
            ]
            return all(
                answer["parts"][f"part_{index}"] == row["canonical"]
                for index, row in enumerate(expected, 1)
            )
        if op == SIMPLIFY_OP:
            theta = sp.symbols("theta", real=True)
            locals_map = {"theta": theta, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
            return all(
                sp.trigsimp(
                    sp.sympify(answer["parts"][str(key)], locals=locals_map)
                    - simplify_fundamental_trig_expression(expr)
                ) == 0
                for key, expr in givens["expressions"].items()
            )
        if op == CHORD_ARC_OP:
            expected = compute_chord_and_arc_length(
                radius=givens["radius"], central_angle=givens["central_angle"], unit=givens["unit"]
            )
            parts = answer["parts"]
            return (
                sp.simplify(sp.sympify(parts["chord_length"]) - expected["chord_length"]) == 0
                and sp.simplify(sp.sympify(parts["arc_length"]) - expected["arc_length"]) == 0
                and expected["chord_length"].is_positive is True
                and sp.simplify(expected["chord_length"] - 2 * expected["radius"]).is_nonpositive is True
            )
        if op == COLLINEAR_OP:
            a, b, c = givens["point_a"], givens["point_b"], givens["point_c"]
            parameter = sp.sympify(answer["canonical_form"])
            determinant = (
                (sp.sympify(b[0]) - sp.sympify(a[0])) * (sp.sympify(c[1]) - sp.sympify(a[1]))
                - (sp.sympify(c[0]) - sp.sympify(a[0])) * (parameter - sp.sympify(a[1]))
            )
            return sp.simplify(determinant) == 0
        if op == SECTOR_OP:
            parts = answer.get("parts") or {}
            facts = matrix.get("validation_facts") or {}
            return (
                bool(parts)
                and facts.get("cross_domain_delegate") == "trigonometry.angle.sector_arc_and_area"
                and all(sp.sympify(value).is_real is True for value in parts.values())
            )
    except (KeyError, TypeError, ValueError, sp.SympifyError):
        return False
    return False
