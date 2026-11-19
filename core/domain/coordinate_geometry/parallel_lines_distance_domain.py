"""Parallel lines distance domain: pure math, no skill_id branching."""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

_SUPPORTED_OPERATIONS = frozenset(
    {
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "area_using_parallel_distance",
    }
)

_ROAD_NAME_POOL = (
    ("建國北路", "新生北路"),
    ("忠孝東路", "仁愛路"),
    ("中山高架道路", "環河快速道路"),
    ("和平西路", "羅斯福路"),
    ("民權東路", "南京東路"),
)


def _format_general_expression(a: int, b: int, c: int) -> str:
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x")
        elif a == -1:
            parts.append("-x")
        else:
            parts.append(f"{a}x")
    if b != 0:
        sign = "+" if b > 0 and parts else ""
        if b == 1:
            parts.append(f"{sign}y")
        elif b == -1:
            parts.append("-y")
        else:
            parts.append(f"{sign}{b}y")
    if c != 0:
        sign = "+" if c > 0 and parts else ""
        parts.append(f"{sign}{c}")
    return "".join(parts) if parts else "0"


def _format_general_form(a: int, b: int, c: int) -> str:
    return f"{_format_general_expression(a, b, c)} = 0"


def _expr_text(value: Any) -> str:
    import sympy

    return str(sympy.simplify(value))


def _normalize_line(a: int, b: int, c: int) -> tuple[int, int, Fraction]:
    gcd_ab = math.gcd(abs(a), abs(b))
    if gcd_ab == 0:
        raise ValueError("invalid_line_coefficients")
    if a < 0 or (a == 0 and b < 0):
        gcd_ab = -gcd_ab
    return a // gcd_ab, b // gcd_ab, Fraction(c, gcd_ab)


def _parallel_distance_expr(a1: int, b1: int, c1: int, a2: int, b2: int, c2: int) -> Any:
    import sympy

    na1, nb1, nc1 = _normalize_line(a1, b1, c1)
    na2, nb2, nc2 = _normalize_line(a2, b2, c2)
    if (na1, nb1) != (na2, nb2):
        raise ValueError("lines_are_not_parallel_after_normalization")
    if nc1 == nc2:
        raise ValueError("parallel_lines_are_coincident")
    c1_expr = sympy.Rational(nc1.numerator, nc1.denominator)
    c2_expr = sympy.Rational(nc2.numerator, nc2.denominator)
    return sympy.simplify(sympy.Abs(c1_expr - c2_expr) / sympy.sqrt(na1 * na1 + nb1 * nb1))


def _empty_visual() -> dict[str, object]:
    return {
        "kind": "coordinate_plane_spec",
        "points": [],
        "lines": [],
        "x_range": [-8, 8],
        "y_range": [-8, 8],
    }


def _sample_parallel_pair(
    rng: random.Random,
    *,
    force_scaled: bool | None = None,
) -> tuple[int, int, int, int, int, int, Any]:
    normal_pairs = [(3, 4), (5, 12), (3, 1), (2, 1), (1, 2), (1, -2), (2, -3), (8, 15)]
    a, b = rng.choice(normal_pairs)
    c1 = rng.randint(-10, 10)
    c2 = c1 + rng.choice([-12, -8, -5, -3, 3, 5, 8, 12])
    while c2 == c1:
        c2 = c1 + rng.choice([-8, -5, 5, 8])
    use_scaled = rng.choice([True, False]) if force_scaled is None else bool(force_scaled)
    if use_scaled:
        scale = rng.choice([-3, -2, 2, 3])
        a2, b2, c2_scaled = a * scale, b * scale, c2 * scale
    else:
        a2, b2, c2_scaled = a, b, c2
    dist = _parallel_distance_expr(a, b, c1, a2, b2, c2_scaled)
    return a, b, c1, a2, b2, c2_scaled, dist


def _pair_payload(
    a: int,
    b: int,
    c1: int,
    a2: int,
    b2: int,
    c2: int,
    dist: Any,
) -> tuple[dict[str, object], str]:
    line_1 = _format_general_form(a, b, c1)
    line_2 = _format_general_form(a2, b2, c2)
    canonical = _expr_text(dist)
    return (
        {
            "line_1": line_1,
            "line_2": line_2,
            "coefficients_line_1": {"A": a, "B": b, "C": c1},
            "coefficients_line_2": {"A": a2, "B": b2, "C": c2},
            "distance": canonical,
        },
        canonical,
    )


def _build_distance_between_parallel_lines(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    variant = str(constraints.get("presentation_variant") or "single").strip().lower()
    if variant in {"multipart", "multi_part", "multi"}:
        return _build_distance_multipart(rng, constraints)
    if variant in {"life_context", "context", "word_problem"}:
        return _build_distance_life_context(rng, constraints)

    force_scaled = constraints.get("force_scaled_coefficients")
    a, b, c1, a2, b2, c2, dist = _sample_parallel_pair(
        rng,
        force_scaled=None if force_scaled is None else bool(force_scaled),
    )
    pair, canonical = _pair_payload(a, b, c1, a2, b2, c2, dist)
    givens = {
        **pair,
        "presentation_variant": "single",
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c1},
        "distance": canonical,
        "value": canonical,
        "presentation_variant": "single",
    }
    return givens, answer


def _build_distance_multipart(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    del constraints
    items = []
    answers: dict[str, str] = {}
    used_signatures: set[tuple[int, int, int, int, int, int]] = set()
    for index in (1, 2):
        for _ in range(20):
            force_scaled = index == 2  # second item prefers proportional coefficients
            a, b, c1, a2, b2, c2, dist = _sample_parallel_pair(rng, force_scaled=force_scaled)
            signature = (a, b, c1, a2, b2, c2)
            if signature in used_signatures:
                continue
            used_signatures.add(signature)
            pair, canonical = _pair_payload(a, b, c1, a2, b2, c2, dist)
            key = f"({index})"
            items.append({"key": key, **pair})
            answers[key] = canonical
            break
        else:
            raise RuntimeError("unable_to_sample_distinct_multipart_pairs")

    givens = {
        "presentation_variant": "multipart",
        "items": items,
        # Keep first pair mirrors for legacy readers.
        "line_1": items[0]["line_1"],
        "line_2": items[0]["line_2"],
    }
    answer = {
        "canonical_form": answers,
        "general_form": answers,
        "parts": answers,
        "coefficients": items[0]["coefficients_line_1"],
        "distance": answers["(1)"],
        "value": answers,
        "presentation_variant": "multipart",
    }
    return givens, answer


def _build_distance_life_context(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    del constraints
    a, b, c1, a2, b2, c2, dist = _sample_parallel_pair(rng, force_scaled=rng.choice([True, False]))
    pair, canonical = _pair_payload(a, b, c1, a2, b2, c2, dist)
    road_a, road_b = rng.choice(_ROAD_NAME_POOL)
    role = rng.choice(["宅急便送貨員", "外送員", "巡路工程師"])
    city = rng.choice(["臺北", "新北", "高雄"])
    givens = {
        **pair,
        "presentation_variant": "life_context",
        "context_role": role,
        "context_city": city,
        "road_a": road_a,
        "road_b": road_b,
        "ask": "shortest_road_distance",
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c1},
        "distance": canonical,
        "value": canonical,
        "presentation_variant": "life_context",
    }
    return givens, answer


def _is_integer_sympy(value: Any) -> bool:
    import sympy

    try:
        return bool(sympy.simplify(value).is_integer)
    except Exception:
        return False


def _sample_parameter_geometry(
    rng: random.Random,
    *,
    prefer_integer_roots: bool = False,
) -> tuple[int, int, int, int, int, int, Any, Any, Any, Any]:
    import sympy

    a1, b1 = 2, 4
    a2, b2 = 1, 2
    g1 = abs(math.gcd(a1, b1))
    norm_a1, norm_b1, _ = _normalize_line(a1, b1, 0)
    # Integer Δk when target^2 ∈ {5, 20} with this normal; keep radicals available otherwise.
    dist_choices = [5, 20] if prefer_integer_roots else [5, 10, 20, 40]
    for _ in range(40):
        c2 = rng.choice([-10, -5, -3, 3, 5, 10])
        target_dist_sq = rng.choice(dist_choices)
        target_distance = sympy.sqrt(target_dist_sq)
        _, _, normalized_c2 = _normalize_line(a2, b2, c2)
        normalized_c2_expr = sympy.Rational(normalized_c2.numerator, normalized_c2.denominator)
        center = sympy.simplify(-g1 * normalized_c2_expr)
        delta_c = sympy.simplify(
            g1 * target_distance * sympy.sqrt(norm_a1 * norm_a1 + norm_b1 * norm_b1)
        )
        lower = sympy.simplify(center - delta_c)
        upper = sympy.simplify(center + delta_c)
        if prefer_integer_roots and not (_is_integer_sympy(lower) and _is_integer_sympy(upper)):
            continue
        return a1, b1, a2, b2, c2, g1, target_distance, center, lower, upper
    raise RuntimeError("unable_to_sample_parameter_geometry")


def _build_solve_parameter_from_parallel_distance(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    branch = str(constraints.get("parameter_branch") or "").strip().lower()
    sign_condition = str(
        constraints.get("sign_condition") or constraints.get("parameter_condition") or ""
    ).strip().lower()
    param_sign = str(constraints.get("parameter_sign") or "").strip().lower()
    if not sign_condition and param_sign:
        if param_sign in {"positive", "pos", ">0", "k>0"}:
            sign_condition = "k>0"
        elif param_sign in {"negative", "neg", "<0", "k<0"}:
            sign_condition = "k<0"
    require_all = bool(constraints.get("require_all_solutions")) or branch in {"both", "all"}

    a1, b1, a2, b2, c2, _g1, target_distance, center, lower, upper = _sample_parameter_geometry(
        rng,
        prefer_integer_roots=require_all,
    )

    if sign_condition in {"k>0", "k > 0", "positive"}:
        candidates = [v for v in (lower, upper) if v > 0]
        if not candidates:
            for _ in range(30):
                a1, b1, a2, b2, c2, _g1, target_distance, center, lower, upper = _sample_parameter_geometry(
                    rng,
                    prefer_integer_roots=False,
                )
                candidates = [v for v in (lower, upper) if v > 0]
                if candidates:
                    break
        k_val = rng.choice(candidates) if candidates else upper
        condition = "k > 0"
        require_all = False
    elif sign_condition in {"k<0", "k < 0", "negative"}:
        candidates = [v for v in (lower, upper) if v < 0]
        if not candidates:
            for _ in range(30):
                a1, b1, a2, b2, c2, _g1, target_distance, center, lower, upper = _sample_parameter_geometry(
                    rng,
                    prefer_integer_roots=False,
                )
                candidates = [v for v in (lower, upper) if v < 0]
                if candidates:
                    break
        k_val = rng.choice(candidates) if candidates else lower
        condition = "k < 0"
        require_all = False
    elif require_all:
        condition = ""
        k_val = None
    else:
        if branch not in {"upper", "lower"}:
            branch = rng.choice(["upper", "lower"])
        if branch == "upper":
            k_val = upper
            condition = f"k > {_expr_text(center)}"
        else:
            k_val = lower
            condition = f"k < {_expr_text(center)}"

    param_name = "k"
    line_1 = f"{_format_general_expression(a1, b1, 0)} - {param_name} = 0"
    line_2 = _format_general_form(a2, b2, c2)
    if require_all:
        values = sorted({_expr_text(lower), _expr_text(upper)}, key=lambda s: (len(s), s))
        canonical = " 或 ".join(values)
        givens = {
            "line_1": line_1,
            "line_2": line_2,
            "target_distance": _expr_text(target_distance),
            "parameter_name": param_name,
            "parameter_condition": "",
            "require_all_solutions": True,
            "solution_values": values,
        }
        answer = {
            "canonical_form": canonical,
            "general_form": canonical,
            "coefficients": {"A": a1, "B": b1, "C": canonical},
            "distance": _expr_text(target_distance),
            "parameter": canonical,
            "parameter_name": param_name,
            "parameter_condition": "",
            "solution_set": values,
            "value": canonical,
            "answer_type": "solution_set",
        }
        return givens, answer

    canonical = _expr_text(k_val)
    givens = {
        "line_1": line_1,
        "line_2": line_2,
        "target_distance": _expr_text(target_distance),
        "parameter_name": param_name,
        "parameter_condition": condition,
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a1, "B": b1, "C": canonical},
        "distance": _expr_text(target_distance),
        "parameter": canonical,
        "parameter_name": param_name,
        "parameter_condition": condition,
        "value": canonical,
    }
    return givens, answer


def _build_area_using_parallel_distance(
    rng: random.Random,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    del constraints
    import sympy

    a, b = rng.choice([(3, -4), (5, 12), (3, 1), (2, 1), (1, 2), (1, -1)])
    c = rng.randint(-10, 10)
    x0, y0 = rng.randint(-6, 6), rng.randint(-6, 6)
    while a * x0 + b * y0 + c == 0:
        x0, y0 = rng.randint(-6, 6), rng.randint(-6, 6)
    base_len = rng.randint(2, 8)
    height = sympy.simplify(sympy.Abs(a * x0 + b * y0 + c) / sympy.sqrt(a * a + b * b))
    area = sympy.simplify(sympy.Rational(base_len, 2) * height)
    canonical = _expr_text(area)
    givens = {
        "point_a": [x0, y0],
        "line": _format_general_form(a, b, c),
        "segment_length": base_len,
    }
    answer = {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": {"A": a, "B": b, "C": c},
        "distance": _expr_text(height),
        "area": canonical,
        "value": canonical,
    }
    return givens, answer


def build_parallel_lines_distance_matrix(
    *,
    seed: int | None,
    domain_operation: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
    line_type: str | None = None,
) -> dict[str, object]:
    """Build Full Matrix Dictionary for parallel-lines distance operations."""
    op = str(domain_operation or line_type or "").strip()
    if op not in _SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported_domain_operation: {op!r}")

    rng = random.Random(0 if seed is None else seed)
    extra = dict(constraints or {})

    if op == "distance_between_parallel_lines":
        givens, answer = _build_distance_between_parallel_lines(rng, extra)
        distractors: list[str] = []
    elif op == "solve_parameter_from_parallel_distance":
        givens, answer = _build_solve_parameter_from_parallel_distance(rng, extra)
        distractors = []
    elif op == "construct_parallel_line_at_distance":
        givens, answer = _build_distance_between_parallel_lines(rng, extra)
        distractors = []
    elif op == "area_using_parallel_distance":
        givens, answer = _build_area_using_parallel_distance(rng, extra)
        distractors = []
    else:
        raise ValueError(f"unsupported_domain_operation: {op!r}")

    presentation_variant = str(
        givens.get("presentation_variant")
        or answer.get("presentation_variant")
        or extra.get("presentation_variant")
        or "single"
    )
    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": [
            "Normalize proportional parallel-line equations to the same A and B.",
            "Use distance |C1-C2|/sqrt(A^2+B^2) after normalization.",
            "For parameter problems, solve the absolute-value equation and apply the stated branch condition.",
            "For area problems, use point-to-line distance as triangle height.",
        ],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "presentation_variant": presentation_variant,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "visual_spec": _empty_visual(),
    }
