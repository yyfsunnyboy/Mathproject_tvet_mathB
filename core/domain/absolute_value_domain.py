"""Generic absolute-value domain capabilities."""

from __future__ import annotations

import math
import random
from typing import Any


def _finite_number(value: Any, *, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an integer or float.")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    return value


def solve_abs_equation(rhs: int | float) -> list[int | float]:
    """Return the real solution set of |x| = rhs in ascending order."""
    value = _finite_number(rhs, name="rhs")
    if value < 0:
        return []
    if value == 0:
        return [0]
    return [-value, value]


def solve_basic_absolute_value_equation(rhs: int | float) -> list[int | float]:
    return solve_abs_equation(rhs)


def solve_basic_absolute_value_equation_no_solution(
    rhs: int | float,
) -> list[int | float]:
    return solve_abs_equation(rhs)


def solve_absolute_value_inequality(a: int | float, b: int | float, op: str, c: int | float) -> str:
    from fractions import Fraction
    fa = Fraction(a)
    fb = Fraction(b)
    fc = Fraction(c)
    if fc < 0:
        if op in {"<", "<="}:
            return "(1,0)"
        return "(-∞,∞)"
    left = (-fc - fb) / fa
    right = (fc - fb) / fa
    lo = min(left, right)
    hi = max(left, right)
    if op == "<":
        return f"({lo},{hi})"
    if op == "<=":
        return f"[{lo},{hi}]"
    if op == ">":
        return f"(-∞,{lo}) ∪ ({hi},∞)"
    if op == ">=":
        return f"(-∞,{lo}] ∪ [{hi},∞]"
    raise ValueError(f"Unsupported inequality operator: {op}")


def count_integer_solutions_for_inequality(a: int | float, b: int | float, op: str, c: int | float) -> int:
    from fractions import Fraction
    from math import ceil, floor
    fa = Fraction(a)
    fb = Fraction(b)
    fc = Fraction(c)
    if fc < 0:
        if op in {"<", "<="}:
            return 0
        raise ValueError("Infinite integer solutions")
    left = (-fc - fb) / fa
    right = (fc - fb) / fa
    lo = min(left, right)
    hi = max(left, right)
    
    if op in {"<", "<="}:
        if op == "<=":
            start = ceil(lo)
            end = floor(hi)
        else:
            start = floor(lo) + 1
            end = ceil(hi) - 1
        if start > end:
            return 0
        return end - start + 1
    else:
        raise ValueError("Infinite integer solutions")


def number_line_distance(a: int | float, b: int | float) -> int | float:
    """Return the distance between two real coordinates on a number line."""
    left = _finite_number(a, name="a")
    right = _finite_number(b, name="b")
    return abs(left - right)


def build_absolute_value_matrix(
    *,
    seed: int | None,
    line_type: str | None = None,
    domain_operation: str | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a domain matrix for an absolute-value scenario.

    This function implements the official production domain operation protocol.
    `seed` is part of the common operation protocol and is used to initialize the Random generator.
    """
    op = str(domain_operation or line_type or "").strip()
    supported = {
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_integer_solution_count_choice",
    }
    if op not in supported:
        raise ValueError(f"Unsupported absolute-value operation: {op!r}")

    rng = random.Random(0 if seed is None else seed)
    extra = dict(constraints or {})

    # Extract target task parameters from constraints if available
    rhs_val = extra.get("rhs")
    if rhs_val is None:
        rhs_val = extra.get("rhs_value")
    a_val = extra.get("a")
    b_val = extra.get("b")

    spec = extra.get("v3_induced_spec") or extra.get("phase1_classification") or {}
    if not isinstance(spec, dict):
        spec = {}
    if rhs_val is None:
        rhs_val = spec.get("rhs")
    if a_val is None:
        a_val = spec.get("a")
    if b_val is None:
        b_val = spec.get("b")

    if op == "solve_basic_absolute_value_equation":
        if rhs_val is None:
            rhs_val = rng.randint(1, 20)
        else:
            rhs_val = float(rhs_val)
            if rhs_val.is_integer():
                rhs_val = int(rhs_val)
            if rhs_val < 0:
                rhs_val = abs(rhs_val)

        sol_set = solve_abs_equation(rhs_val)
        canonical_str = ", ".join(str(x) for x in sol_set) if sol_set else "0"

        givens = {"rhs": rhs_val}
        answer = {
            "canonical_form": canonical_str,
            "general_form": canonical_str,
            "coefficients": sol_set,
        }

        if len(sol_set) == 2:
            val = abs(sol_set[0])
            distractors = [
                f"-{val-1}, {val-1}" if val > 1 else "0",
                f"-{val+1}, {val+1}",
                f"{val}",
            ]
        else:
            distractors = ["-1, 1", "2", "-2"]

    elif op == "solve_basic_absolute_value_equation_no_solution":
        if rhs_val is None:
            rhs_val = -rng.randint(1, 20)
        else:
            rhs_val = float(rhs_val)
            if rhs_val.is_integer():
                rhs_val = int(rhs_val)
            if rhs_val >= 0:
                rhs_val = -rhs_val if rhs_val > 0 else -1

        sol_set = solve_abs_equation(rhs_val)
        canonical_str = "無解"

        givens = {"rhs": rhs_val}
        answer = {
            "canonical_form": canonical_str,
            "general_form": canonical_str,
            "coefficients": sol_set,
        }
        distractors = ["0", "-1, 1", "2"]

    elif op == "number_line_distance_between_two_points":
        if a_val is None:
            a_val = rng.randint(-20, 20)
        else:
            a_val = float(a_val)
            if a_val.is_integer():
                a_val = int(a_val)

        if b_val is None:
            for _ in range(100):
                b_val = rng.randint(-20, 20)
                if b_val != a_val:
                    break
        else:
            b_val = float(b_val)
            if b_val.is_integer():
                b_val = int(b_val)

        dist = number_line_distance(a_val, b_val)
        givens = {"a": a_val, "b": b_val}
        answer = {
            "canonical_form": str(dist),
            "general_form": str(dist),
            "coefficients": [dist],
        }
        distractors = [str(dist + 1), str(abs(dist - 1)), str(dist + 2)]

    elif op in {
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_integer_solution_count_choice",
    }:
        if op == "absolute_value_inequality_zero_center_basic":
            a_val = 1
            b_val = 0
            c_val = extra.get("c") or extra.get("rhs") or extra.get("rhs_value")
            if c_val is None:
                c_val = rng.randint(1, 20)
            op_val = extra.get("op") or rng.choice(["<", "<=", ">", ">="])
        elif op == "absolute_value_inequality_shifted_basic":
            a_val = 1
            b_val = extra.get("b")
            if b_val is None:
                b_val = rng.choice([-1, 1]) * rng.randint(1, 10)
            c_val = extra.get("c") or extra.get("rhs") or extra.get("rhs_value")
            if c_val is None:
                c_val = rng.randint(1, 15)
            op_val = extra.get("op") or rng.choice(["<", "<=", ">", ">="])
        elif op == "absolute_value_inequality_linear_expression_basic":
            a_val = extra.get("a")
            if a_val is None:
                a_val = rng.randint(2, 9)
            b_val = extra.get("b")
            if b_val is None:
                b_val = rng.choice([-1, 1]) * rng.randint(1, 15)
            c_val = extra.get("c") or extra.get("rhs") or extra.get("rhs_value")
            if c_val is None:
                c_val = rng.randint(1, 20)
            op_val = extra.get("op") or rng.choice(["<", "<=", ">", ">="])
        else:
            a_val = extra.get("a")
            if a_val is None:
                a_val = rng.randint(2, 6)
            b_val = extra.get("b")
            if b_val is None:
                b_val = rng.choice([-1, 1]) * rng.randint(1, 10)
            c_val = extra.get("c") or extra.get("rhs") or extra.get("rhs_value")
            if c_val is None:
                c_val = rng.randint(1, 15)
            op_val = extra.get("op") or rng.choice(["<", "<="])

        if op == "absolute_value_inequality_integer_solution_count_choice":
            ans_val = count_integer_solutions_for_inequality(a_val, b_val, op_val, c_val)
            canonical_str = str(ans_val)
            distractors = [str(ans_val - 1), str(ans_val + 1), str(ans_val + 2)]
            distractors = [d if int(d) >= 0 else "0" for d in distractors]
            distractors = list(set(distractors))
            if len(distractors) < 3:
                distractors = [str(ans_val + 3), str(ans_val + 4)]
        else:
            canonical_str = solve_absolute_value_inequality(a_val, b_val, op_val, c_val)
            distractors = []

        givens = {"a": a_val, "b": b_val, "op": op_val, "c": c_val}
        answer = {
            "canonical_form": canonical_str,
            "general_form": canonical_str,
            "coefficients": [a_val, b_val, c_val],
        }

    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": [
            f"Given operation: {op}.",
            "Perform absolute-value calculation or solve equations.",
        ],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
        },
        "visual_spec": {
            "points": [],
            "lines": [],
            "x_range": [-10, 10],
            "y_range": [-10, 10],
        },
    }

