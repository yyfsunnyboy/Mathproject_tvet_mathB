# -*- coding: utf-8 -*-
"""Exact Law-of-Cosines operations for Math B2 §2-1 (no sine-law mixing)."""

from __future__ import annotations

import random
from typing import Any

import sympy as sp


SIDE_BY_COSINES_OP = "solve_side_by_law_of_cosines"
ANGLE_BY_COSINES_OP = "solve_angle_by_law_of_cosines"
IDENTITY_ANGLE_OP = "solve_cosine_identity_angle"
EXTRA_PATH_OP = "solve_detour_extra_distance_by_cosines"
CIRCUMRADIUS_SSS_OP = "compute_circumradius_from_three_sides"

OPS = frozenset(
    {
        SIDE_BY_COSINES_OP,
        ANGLE_BY_COSINES_OP,
        IDENTITY_ANGLE_OP,
        EXTRA_PATH_OP,
        CIRCUMRADIUS_SSS_OP,
    }
)

_SPECIAL_ACUTE = (30, 45, 60)
_SPECIAL_OBTUSE = (120, 135, 150)
_SAMPLE_QUALITY_RETRIES = 24
_BOOKKEEPING = (
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
)


def canonical_exact(value: Any) -> str:
    return sp.sstr(sp.radsimp(sp.simplify(value)), order="lex")


def _exact(value: Any, *, name: str) -> sp.Expr:
    try:
        result = sp.sympify(value)
    except (sp.SympifyError, TypeError) as exc:
        raise ValueError(f"{name}_must_be_exact_numeric") from exc
    return sp.simplify(result)


def _positive_exact(value: Any, *, name: str) -> sp.Expr:
    result = _exact(value, name=name)
    if result.is_real is not True or result.is_positive is not True:
        raise ValueError(f"{name}_must_be_positive")
    return result


def _angle_degrees(value: Any, *, name: str = "angle") -> sp.Rational:
    degrees = sp.Rational(str(_exact(value, name=name)))
    if not (0 < degrees < 180):
        raise ValueError(f"{name}_must_be_interior_triangle_angle")
    return degrees


def _cos_deg(degrees: Any) -> sp.Expr:
    return sp.simplify(sp.cos(sp.rad(_angle_degrees(degrees))))


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, sp.Basic):
        return canonical_exact(value)
    return value


def solve_side_by_law_of_cosines(
    *,
    side_b: Any,
    side_c: Any,
    included_angle_degrees: Any,
) -> dict[str, Any]:
    """SAS: a^2 = b^2 + c^2 - 2bc cos A."""
    b = _positive_exact(side_b, name="side_b")
    c = _positive_exact(side_c, name="side_c")
    angle = _angle_degrees(included_angle_degrees, name="included_angle")
    a2 = sp.simplify(b**2 + c**2 - 2 * b * c * _cos_deg(angle))
    if a2.is_real is not True or a2 <= 0:
        raise ValueError("cosine_side_not_positive")
    side = sp.simplify(sp.sqrt(a2))
    return {
        "side": side,
        "side_squared": a2,
        "canonical": canonical_exact(side),
        "included_angle_degrees": angle,
    }


def solve_angle_by_law_of_cosines(
    *,
    side_a: Any,
    side_b: Any,
    side_c: Any,
    find: str = "A",
) -> dict[str, Any]:
    """SSS: find angle opposite the named side via cosines."""
    a = _positive_exact(side_a, name="side_a")
    b = _positive_exact(side_b, name="side_b")
    c = _positive_exact(side_c, name="side_c")
    # Triangle inequality
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("triangle_inequality_violated")
    find_key = str(find or "A").strip().upper()
    if find_key == "A":
        cos_val = sp.simplify((b**2 + c**2 - a**2) / (2 * b * c))
    elif find_key == "B":
        cos_val = sp.simplify((a**2 + c**2 - b**2) / (2 * a * c))
    elif find_key == "C":
        cos_val = sp.simplify((a**2 + b**2 - c**2) / (2 * a * b))
    else:
        raise ValueError("find_must_be_A_B_or_C")
    if cos_val.is_real is not True or cos_val < -1 or cos_val > 1:
        raise ValueError("cosine_out_of_range")
    angle = sp.simplify(sp.deg(sp.acos(cos_val)))
    return {
        "cos_value": cos_val,
        "answer_degrees": angle,
        "canonical": canonical_exact(angle),
        "find": find_key,
    }


def solve_cosine_identity_angle(*, relation: str = "a2_minus_b_plus_c_sq_eq_neg_bc") -> dict[str, Any]:
    """Deterministic textbook identity that yields cos A = -1/2 → 120°."""
    key = str(relation or "").strip()
    if key != "a2_minus_b_plus_c_sq_eq_neg_bc":
        raise ValueError(f"unsupported_cosine_identity:{key}")
    # a^2 - (b+c)^2 = -bc  ⇒  cos A = -1/2
    cos_val = sp.Rational(-1, 2)
    angle = sp.Integer(120)
    return {
        "cos_value": cos_val,
        "answer_degrees": angle,
        "canonical": canonical_exact(angle),
        "relation": key,
    }


def solve_detour_extra_distance_by_cosines(
    *,
    direct_side: Any,
    first_leg: Any,
    included_angle_degrees: Any,
) -> dict[str, Any]:
    """AB + BC - AC where BC from cosines with angle at A between AB and AC."""
    ac = _positive_exact(direct_side, name="direct_side")
    ab = _positive_exact(first_leg, name="first_leg")
    angle = _angle_degrees(included_angle_degrees, name="included_angle")
    bc = solve_side_by_law_of_cosines(side_b=ab, side_c=ac, included_angle_degrees=angle)["side"]
    extra = sp.simplify(ab + bc - ac)
    if extra.is_real is not True or extra < 0:
        raise ValueError("extra_distance_invalid")
    return {
        "detour_side": bc,
        "extra_distance": extra,
        "canonical": canonical_exact(extra),
        "included_angle_degrees": angle,
    }


def compute_circumradius_from_three_sides(*, side_a: Any, side_b: Any, side_c: Any) -> dict[str, Any]:
    """R = abc / (4K) with Heron area K (no sine-law operation)."""
    a = _positive_exact(side_a, name="side_a")
    b = _positive_exact(side_b, name="side_b")
    c = _positive_exact(side_c, name="side_c")
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("triangle_inequality_violated")
    semiperimeter = sp.simplify((a + b + c) / 2)
    area_sq = sp.simplify(
        semiperimeter
        * (semiperimeter - a)
        * (semiperimeter - b)
        * (semiperimeter - c)
    )
    if area_sq.is_real is not True or area_sq <= 0:
        raise ValueError("heron_area_invalid")
    area = sp.simplify(sp.sqrt(area_sq))
    radius = sp.simplify(a * b * c / (4 * area))
    return {
        "circumradius": radius,
        "area": area,
        "canonical": canonical_exact(radius),
        "side_a": a,
        "side_b": b,
        "side_c": c,
    }


def _choice_payload(canonical: str, distractors: list[str], rng: random.Random) -> dict[str, Any]:
    extras = [d for d in distractors if d != canonical]
    rng.shuffle(extras)
    options = [canonical] + extras[:3]
    filler = 2
    while len(options) < 4:
        candidate = canonical_exact(sp.Integer(filler))
        filler += 1
        if candidate not in options:
            options.append(candidate)
    rng.shuffle(options)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": labels[i], "text": options[i], "value": options[i]} for i in range(4)]
    correct = next(c["label"] for c in choices if c["value"] == canonical)
    return {"choices": choices, "correct_label": correct, "semantic_answer": canonical}


def _has_nested_radical(value: Any) -> bool:
    expr = _exact(value, name="quality_value")
    radicals = [
        node
        for node in sp.preorder_traversal(expr)
        if isinstance(node, sp.Pow) and node.exp == sp.Rational(1, 2)
    ]
    return any(
        any(
            isinstance(child, sp.Pow) and child.exp == sp.Rational(1, 2)
            for child in sp.preorder_traversal(radical.base)
        )
        for radical in radicals
    )


def _largest_integer_atom(value: Any) -> int:
    expr = _exact(value, name="quality_value")
    return max((abs(int(atom)) for atom in expr.atoms(sp.Integer)), default=0)


def _sample_quality_ok(
    operation: str,
    givens: dict[str, Any],
    result: dict[str, Any],
) -> bool:
    expressions = list(givens.values()) + list(result.values())
    numeric = [value for value in expressions if isinstance(value, (int, float, sp.Basic))]
    if any(_has_nested_radical(value) for value in numeric):
        return False

    if operation in {SIDE_BY_COSINES_OP, ANGLE_BY_COSINES_OP}:
        sides = [
            _positive_exact(value, name=key)
            for key, value in givens.items()
            if key.startswith("side_")
        ]
        if not sides or max(float(side) for side in sides) > 30:
            return False
        coefficient_values = [
            value
            for key, value in result.items()
            if key not in {"included_angle_degrees", "answer_degrees", "canonical", "find"}
            and isinstance(value, (int, float, sp.Basic))
        ]
        if operation == SIDE_BY_COSINES_OP and any(
            _largest_integer_atom(value) > 50 for value in coefficient_values
        ):
            return False
    elif operation == EXTRA_PATH_OP:
        distances = [givens.get("direct_side"), givens.get("first_leg")]
        if any(float(_positive_exact(value, name="distance")) > 1200 for value in distances):
            return False
        if any(_largest_integer_atom(value) > 3600 for value in numeric):
            return False
    return True


def _sample_with_quality(
    rng: random.Random,
    operation: str,
    sampler: Any,
    solver: Any,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    for attempt in range(1, _SAMPLE_QUALITY_RETRIES + 1):
        givens = sampler(rng)
        try:
            result = solver(givens)
        except ValueError:
            continue
        if _sample_quality_ok(operation, givens, result):
            return givens, result, attempt
    raise RuntimeError(f"law_of_cosines_quality_retry_exhausted:{operation}")


def _sample_side(rng: random.Random) -> dict[str, Any]:
    # Curated SAS families retain random variation while keeping the resulting
    # side integral or a single textbook-style radical.
    b, c, angle = rng.choice(
        (
            (3, 4, 60),
            (3, 5, 120),
            (5, 5, 60),
            (6, 8, 90),
            (2, 3, 90),
            (3, 3, 120),
            (4, 4, 90),
            (2, 6, 60),
        )
    )
    b = sp.Integer(b)
    c = sp.Integer(c)
    return {"side_b": b, "side_c": c, "included_angle_degrees": angle}


def _sample_angle(rng: random.Random) -> dict[str, Any]:
    # Integer SSS triples whose target cosine is a standard textbook value.
    a, b, c = rng.choice(
        (
            (7, 5, 3),   # A = 120 degrees
            (5, 3, 4),   # A = 90 degrees
            (3, 3, 3),   # A = 60 degrees
            (7, 8, 5),   # A = 60 degrees
        )
    )
    find = rng.choice(("A", "B", "C"))
    if find == "A":
        return {"side_a": a, "side_b": b, "side_c": c, "find": "A"}
    if find == "B":
        return {"side_a": b, "side_b": a, "side_c": c, "find": "B"}
    return {"side_a": b, "side_b": c, "side_c": a, "find": "C"}


def _sample_extra(rng: random.Random) -> dict[str, Any]:
    direct, first, angle = rng.choice(
        (
            (300, 800, 60),
            (300, 300, 60),
            (400, 300, 90),
            (300, 500, 120),
            (200, 200, 120),
            (300, 600, 60),
        )
    )
    return {
        "direct_side": sp.Integer(direct),
        "first_leg": sp.Integer(first),
        "included_angle_degrees": angle,
    }


def _sample_circumradius(rng: random.Random) -> dict[str, Any]:
    # Prefer Pythagorean-ish / nice Heron triples scaled.
    triples = (
        (3, 4, 5),
        (5, 5, 6),
        (5, 5, 4),
        (6, 8, 10),
        (5, 7, 8),
    )
    a, b, c = rng.choice(triples)
    return {"side_a": sp.Integer(a), "side_b": sp.Integer(b), "side_c": sp.Integer(c)}


def build_trigonometry_law_of_cosines_matrix(
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
        raise ValueError(f"unsupported_trigonometry_law_of_cosines_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    raw_constraints = dict(constraints or {})
    presentation_hint = str(raw_constraints.get("presentation_mode") or data.get("presentation_mode") or "").strip()
    answer_hint = str(raw_constraints.get("answer_type") or data.get("answer_type") or "").strip()
    payload = {**raw_constraints, **data}
    for key in _BOOKKEEPING:
        payload.pop(key, None)
    if presentation_hint == "single_choice" or answer_hint in {"single_choice", "choice"}:
        payload.setdefault("as_choice", True)

    distractors: list[str] = []
    sample_attempts = 0
    if op == SIDE_BY_COSINES_OP:
        if not {"side_b", "side_c", "included_angle_degrees"} <= set(payload):
            sampled, result, sample_attempts = _sample_with_quality(
                rng,
                op,
                _sample_side,
                lambda values: solve_side_by_law_of_cosines(
                    side_b=values["side_b"],
                    side_c=values["side_c"],
                    included_angle_degrees=values["included_angle_degrees"],
                ),
            )
            payload = {**sampled, **payload}
        else:
            result = solve_side_by_law_of_cosines(
                side_b=payload["side_b"],
                side_c=payload["side_c"],
                included_angle_degrees=payload["included_angle_degrees"],
            )
        question = (
            f"在△ABC中，已知 $b={canonical_exact(payload['side_b'])}$、"
            f"$c={canonical_exact(payload['side_c'])}$ 且 "
            f"$\\angle A={canonical_exact(payload['included_angle_degrees'])}^\\circ$，試求 $a$ 之長。"
        )
        answer_value = result["canonical"]
        parts = {"side": result["canonical"]}
        distractors = [
            canonical_exact(sp.simplify(result["side"] ** 2)),
            canonical_exact(sp.simplify(result["side"] + 1)),
            canonical_exact(sp.sqrt(19)),
            canonical_exact(sp.Integer(7)),
            canonical_exact(sp.sqrt(13)),
        ]
    elif op == ANGLE_BY_COSINES_OP:
        if not {"side_a", "side_b", "side_c"} <= set(payload):
            sampled, result, sample_attempts = _sample_with_quality(
                rng,
                op,
                _sample_angle,
                lambda values: solve_angle_by_law_of_cosines(
                    side_a=values["side_a"],
                    side_b=values["side_b"],
                    side_c=values["side_c"],
                    find=str(values.get("find") or "A"),
                ),
            )
            payload = {**sampled, **payload}
        else:
            result = solve_angle_by_law_of_cosines(
                side_a=payload["side_a"],
                side_b=payload["side_b"],
                side_c=payload["side_c"],
                find=str(payload.get("find") or "A"),
            )
        find = result["find"]
        question = (
            f"設△ABC的三邊長 $a={canonical_exact(payload['side_a'])}$、"
            f"$b={canonical_exact(payload['side_b'])}$、"
            f"$c={canonical_exact(payload['side_c'])}$，試求 $\\angle {find}$。"
        )
        answer_value = result["canonical"]
        parts = {"angle": result["canonical"]}
        distractors = [
            canonical_exact(sp.Integer(30)),
            canonical_exact(sp.Integer(45)),
            canonical_exact(sp.Integer(60)),
            canonical_exact(sp.Integer(90)),
            canonical_exact(sp.Integer(120)),
            canonical_exact(sp.Integer(150)),
        ]
    elif op == IDENTITY_ANGLE_OP:
        relation = str(payload.get("relation") or "a2_minus_b_plus_c_sq_eq_neg_bc")
        # Seeded variants: keep the same identity family (stable closed form).
        result = solve_cosine_identity_angle(relation=relation)
        # Controlled micro-variation via seed for stem diversity (answer fixed at 120°).
        seed_i = 0 if seed is None else int(seed)
        stems = [
            "設△ABC中，$a$、$b$、$c$ 為三邊長，若 $a^{2}-(b+c)^{2}=-bc$，試求 $\\angle A$。",
            "設△ABC中，$a$、$b$、$c$ 為三邊長，且滿足 $a^{2}-(b+c)^{2}+bc=0$，試求 $\\angle A$。",
            "已知△ABC 邊長關係 $a^{2}-(b+c)^{2}=-bc$，利用餘弦定理求 $\\angle A$。",
            "若△ABC 滿足 $a^{2}= (b+c)^{2}-bc$，試求 $\\angle A$。",
        ]
        question = stems[seed_i % len(stems)]
        answer_value = result["canonical"]
        parts = {"angle": result["canonical"]}
        distractors = [
            canonical_exact(sp.Integer(30)),
            canonical_exact(sp.Integer(60)),
            canonical_exact(sp.Integer(90)),
            canonical_exact(sp.Integer(150)),
        ]
    elif op == EXTRA_PATH_OP:
        if not {"direct_side", "first_leg", "included_angle_degrees"} <= set(payload):
            sampled, result, sample_attempts = _sample_with_quality(
                rng,
                op,
                _sample_extra,
                lambda values: solve_detour_extra_distance_by_cosines(
                    direct_side=values["direct_side"],
                    first_leg=values["first_leg"],
                    included_angle_degrees=values["included_angle_degrees"],
                ),
            )
            payload = {**sampled, **payload}
        else:
            result = solve_detour_extra_distance_by_cosines(
                direct_side=payload["direct_side"],
                first_leg=payload["first_leg"],
                included_angle_degrees=payload["included_angle_degrees"],
            )
        question = (
            f"小仲規劃從 A 地直線到 C 地，距離為 ${canonical_exact(payload['direct_side'])}$ 公尺，"
            f"因道路施工改繞 B 地。已知 AB=${canonical_exact(payload['first_leg'])}$ 公尺，"
            f"且 $\\angle BAC={canonical_exact(payload['included_angle_degrees'])}^\\circ$。"
            f"若 BC 亦為直線，試問他比原規劃多走了多少公尺？"
        )
        answer_value = result["canonical"]
        parts = {"extra": result["canonical"]}
        direct_num = _positive_exact(payload["direct_side"], name="direct_side")
        distractors = [
            canonical_exact(result["detour_side"]),
            canonical_exact(sp.simplify(result["extra_distance"] + direct_num)),
            canonical_exact(sp.Integer(700)),
            canonical_exact(sp.Integer(1100)),
            canonical_exact(sp.Integer(1800)),
        ]
    elif op == CIRCUMRADIUS_SSS_OP:
        if not {"side_a", "side_b", "side_c"} <= set(payload):
            payload = {**_sample_circumradius(rng), **payload}
        result = compute_circumradius_from_three_sides(
            side_a=payload["side_a"],
            side_b=payload["side_b"],
            side_c=payload["side_c"],
        )
        question = (
            f"已知△ABC 三邊長分別為 ${canonical_exact(payload['side_a'])}$、"
            f"${canonical_exact(payload['side_b'])}$、${canonical_exact(payload['side_c'])}$，"
            f"試求其外接圓半徑 $R$。"
        )
        answer_value = result["canonical"]
        parts = {"R": result["canonical"]}
        distractors = [
            canonical_exact(result["area"]),
            canonical_exact(sp.simplify(result["circumradius"] * 2)),
            canonical_exact(sp.Integer(50)),
            canonical_exact(sp.Integer(35)),
        ]
    else:
        raise ValueError(f"unsupported_trigonometry_law_of_cosines_operation:{op}")

    if payload.get("question_text"):
        question = str(payload["question_text"])

    choice_meta: dict[str, Any] = {}
    presentation = "short_answer"
    answer_type = "expression"
    use_choice = bool(payload.get("as_choice", op in {EXTRA_PATH_OP, SIDE_BY_COSINES_OP} and payload.get("force_choice")))
    # Assessment-style ops default to choice when flagged; EXTRA_PATH always choice-ready.
    if op == EXTRA_PATH_OP and payload.get("as_choice", True):
        use_choice = True
    if op == SIDE_BY_COSINES_OP and payload.get("as_choice"):
        use_choice = True
    if use_choice:
        choice_meta = _choice_payload(str(answer_value), distractors, rng)
        presentation = "single_choice"
        answer_type = "single_choice"
        answer_value = choice_meta["semantic_answer"]
        parts = {"value": choice_meta["semantic_answer"]}

    givens = _json_value({k: v for k, v in payload.items() if k != "question_text"})
    # Ensure choice ops re-validate with as_choice retained.
    if use_choice:
        givens["as_choice"] = True

    matrix = {
        "givens": givens,
        "answer": {
            "value": answer_value,
            "canonical_form": answer_value,
            "general_form": answer_value,
            "coefficients": [],
            "parts": parts,
        },
        "question_text": question,
        "question": question,
        "explanation_steps": ["由餘弦定理 $a^{2}=b^{2}+c^{2}-2bc\\cos A$ 計算。"],
        "distractors": distractors,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "presentation_mode": presentation,
            "answer_type": answer_type,
            "quality_sample_attempts": sample_attempts,
            "quality_gate_applied": sample_attempts > 0,
        },
        "visual_spec": {"kind": "none"},
        "domain_result": _json_value(result),
    }
    if choice_meta:
        matrix["choices"] = choice_meta["choices"]
        matrix["correct_label"] = choice_meta["correct_label"]
        matrix["semantic_answer"] = choice_meta["semantic_answer"]
    return matrix


def validate_trigonometry_law_of_cosines_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = matrix["validation_facts"]["domain_operation"]
        rebuilt = build_trigonometry_law_of_cosines_matrix(operation=op, **matrix["givens"])
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
