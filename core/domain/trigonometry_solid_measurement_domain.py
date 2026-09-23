# -*- coding: utf-8 -*-
"""Simple solid / 3D-ish measurement for Math B2 §2-2-5.

Reuses right-triangle elevation solvers where possible; only adds
solid-layout compositions that 2-2-3 does not own.
"""

from __future__ import annotations

import random
from typing import Any

import sympy as sp

from core.domain.trigonometry_right_triangle_measurement_domain import (
    canonical_exact,
    solve_horizontal_from_height_and_angle,
    solve_opposite_from_adjacent_elevation,
)

TOWER_RIVER_OP = "solve_tower_two_elevation_path_and_river_width"
TAN_RATIO_HEIGHT_OP = "solve_height_from_two_elevation_tan_ratios"
BEARING_WALK_HEIGHT_OP = "solve_height_from_isosceles_bearing_walk_elevation"

OPS = frozenset({TOWER_RIVER_OP, TAN_RATIO_HEIGHT_OP, BEARING_WALK_HEIGHT_OP})

_BOOKKEEPING = (
    "operation",
    "domain_operation",
    "constraints",
    "seed",
    "curriculum_profile",
    "difficulty_profile",
    "presentation_mode",
    "answer_type",
    "as_choice",
    "force_choice",
)


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


def _acute_degrees(value: Any, *, name: str = "angle") -> sp.Rational:
    degrees = sp.Rational(str(_exact(value, name=name)))
    if not (0 < degrees < 90):
        raise ValueError(f"{name}_must_be_acute")
    return degrees


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, sp.Basic):
        return canonical_exact(value)
    return value


def solve_tower_two_elevation_path_and_river_width(
    *,
    tower_height: Any,
    near_elevation_degrees: Any,
    far_elevation_degrees: Any,
) -> dict[str, Any]:
    """Tower foot C; near/far stations with right angle path; river/path width AB.

    Reuses horizontal-from-height elevation for AC and BC, then Pythagoras.
    """
    height = _positive_exact(tower_height, name="tower_height")
    near = _acute_degrees(near_elevation_degrees, name="near_elevation")
    far = _acute_degrees(far_elevation_degrees, name="far_elevation")
    if near == far:
        raise ValueError("elevations_must_differ")
    ac = solve_horizontal_from_height_and_angle(height=height, angle_degrees=near)["horizontal"]
    bc = solve_horizontal_from_height_and_angle(height=height, angle_degrees=far)["horizontal"]
    # Right triangle ABC with right angle between AC and AB (classic river layout).
    larger, smaller = (bc, ac) if bc >= ac else (ac, bc)
    width_sq = sp.simplify(larger**2 - smaller**2)
    if width_sq.is_real is not True or width_sq <= 0:
        raise ValueError("river_width_invalid")
    width = sp.simplify(sp.sqrt(width_sq))
    return {
        "near_distance": ac,
        "far_distance": bc,
        "path_or_river_width": width,
        "canonical": {
            "AC": canonical_exact(ac),
            "BC": canonical_exact(bc),
            "AB": canonical_exact(width),
        },
        "tower_height": height,
        "near_elevation_degrees": near,
        "far_elevation_degrees": far,
    }


def solve_height_from_two_elevation_tan_ratios(
    *,
    advance_distance: Any,
    far_tan: Any,
    near_tan: Any,
    round_to_integer: bool = True,
) -> dict[str, Any]:
    """Approach object: elev tans increase; h = d / (1/tan_far - 1/tan_near)."""
    advance = _positive_exact(advance_distance, name="advance_distance")
    tan_far = _positive_exact(far_tan, name="far_tan")
    tan_near = _positive_exact(near_tan, name="near_tan")
    if not (tan_near > tan_far):
        raise ValueError("near_tan_must_exceed_far_tan")
    coeff = sp.simplify(1 / tan_far - 1 / tan_near)
    if coeff.is_real is not True or coeff <= 0:
        raise ValueError("tan_ratio_height_coeff_invalid")
    height = sp.simplify(advance / coeff)
    if round_to_integer:
        # 統測-style approximate integer choice.
        rounded = int(sp.Integer(sp.floor(height + sp.Rational(1, 2))))
        if rounded <= 0:
            raise ValueError("rounded_height_invalid")
        canonical = str(rounded)
        answer_value: Any = rounded
    else:
        canonical = canonical_exact(height)
        answer_value = height
    return {
        "height": height,
        "rounded_height": answer_value if round_to_integer else None,
        "canonical": canonical,
        "advance_distance": advance,
        "far_tan": tan_far,
        "near_tan": tan_near,
    }


def solve_height_from_isosceles_bearing_walk_elevation(
    *,
    walk_distance: Any,
    base_bearing_degrees: Any,
    elevation_degrees: Any,
) -> dict[str, Any]:
    """Walk AB; object C forms isosceles △ABC with base angles = bearing; elev at A.

    Horizontal AC = AB / (2 cos θ); height via reused opposite-from-adjacent elevation.
    """
    walk = _positive_exact(walk_distance, name="walk_distance")
    bearing = _acute_degrees(base_bearing_degrees, name="base_bearing")
    elev = _acute_degrees(elevation_degrees, name="elevation")
    # C = 180 - 2θ; AC = AB * sin(θ) / sin(C) = AB / (2 cos θ)
    cos_b = sp.simplify(sp.cos(sp.rad(bearing)))
    if cos_b.is_real is not True or cos_b <= 0:
        raise ValueError("bearing_cosine_invalid")
    adjacent = sp.simplify(walk / (2 * cos_b))
    height_result = solve_opposite_from_adjacent_elevation(
        adjacent=adjacent,
        elevation_degrees=elev,
    )
    height = height_result["opposite"]
    return {
        "horizontal_distance": adjacent,
        "height": height,
        "canonical": canonical_exact(height),
        "walk_distance": walk,
        "base_bearing_degrees": bearing,
        "elevation_degrees": elev,
        "reused_elevation_solver": True,
    }


def _choice_payload(canonical: str, distractors: list[str], rng: random.Random) -> dict[str, Any]:
    extras = [d for d in distractors if d != canonical]
    rng.shuffle(extras)
    options = [canonical] + extras[:3]
    filler = 2
    while len(options) < 4:
        candidate = str(filler)
        filler += 1
        if candidate not in options:
            options.append(candidate)
    rng.shuffle(options)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": labels[i], "text": options[i], "value": options[i]} for i in range(4)]
    correct = next(c["label"] for c in choices if c["value"] == canonical)
    return {"choices": choices, "correct_label": correct, "semantic_answer": canonical}


def build_trigonometry_solid_measurement_matrix(
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
        raise ValueError(f"unsupported_solid_measurement_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    raw = {**(constraints or {}), **data}
    presentation_hint = str(raw.get("presentation_mode") or "").strip()
    answer_hint = str(raw.get("answer_type") or "").strip()
    as_choice_requested = bool(raw.get("as_choice")) or presentation_hint == "single_choice" or answer_hint in {
        "single_choice",
        "choice",
    }
    for key in _BOOKKEEPING:
        raw.pop(key, None)

    if op == TOWER_RIVER_OP:
        if not {"tower_height", "near_elevation_degrees", "far_elevation_degrees"} <= set(raw):
            raw.setdefault("tower_height", sp.Integer(rng.choice((100, 200, 300))))
            pair = rng.sample((30, 45, 60), 2)
            near, far = (max(pair), min(pair))
            raw.setdefault("near_elevation_degrees", near)
            raw.setdefault("far_elevation_degrees", far)
        result = solve_tower_two_elevation_path_and_river_width(
            tower_height=raw["tower_height"],
            near_elevation_degrees=raw["near_elevation_degrees"],
            far_elevation_degrees=raw["far_elevation_degrees"],
        )
        question = (
            f"塔底為 C，塔高 ${canonical_exact(result['tower_height'])}$ 公尺。A、B 為地面觀測點，"
            f"在 A 點測得塔頂仰角 ${canonical_exact(result['near_elevation_degrees'])}^\\circ$，"
            f"在 B 點測得塔頂仰角 ${canonical_exact(result['far_elevation_degrees'])}^\\circ$。"
            "已知 AC 垂直河岸，AB 沿河岸，且 $AC\\perp AB$；A、C 位於同岸，B 位於對岸，"
            "線段 AB 代表河寬。試求 AC、BC 與河寬 AB。"
        )
        answer_value = result["canonical"]
        parts = dict(result["canonical"])
        distractors: list[str] = []
        use_choice = False
        presentation = "short_answer"
        answer_type = "multi_part"
        payload = {
            "tower_height": result["tower_height"],
            "near_elevation_degrees": result["near_elevation_degrees"],
            "far_elevation_degrees": result["far_elevation_degrees"],
        }
    elif op == TAN_RATIO_HEIGHT_OP:
        if not {"advance_distance", "far_tan", "near_tan"} <= set(raw):
            raw.setdefault("advance_distance", sp.Integer(rng.choice((24, 31, 35, 42))))
            # Keep near>far positive rationals like 統測-style.
            pairs = (
                (sp.Rational(3, 4), sp.Rational(4, 3)),
                (sp.Rational(1, 2), sp.Rational(3, 4)),
                (sp.Rational(2, 3), sp.Integer(1)),
                (sp.Rational(3, 5), sp.Rational(4, 3)),
            )
            far_t, near_t = rng.choice(pairs)
            raw.setdefault("far_tan", far_t)
            raw.setdefault("near_tan", near_t)
        round_flag = bool(raw.get("round_to_integer", True))
        result = solve_height_from_two_elevation_tan_ratios(
            advance_distance=raw["advance_distance"],
            far_tan=raw["far_tan"],
            near_tan=raw["near_tan"],
            round_to_integer=round_flag,
        )
        question = (
            f"測得目標仰角正切為 ${canonical_exact(result['far_tan'])}$，"
            f"朝目標前進 ${canonical_exact(result['advance_distance'])}$ 公尺後，"
            f"仰角正切變為 ${canonical_exact(result['near_tan'])}$，"
            f"試求目標高度"
            + ("（四捨五入至整數）" if round_flag else "。")
        )
        answer_value = result["canonical"]
        parts = {"height": answer_value}
        distractors = [
            str(int(answer_value) + 4) if str(answer_value).isdigit() else canonical_exact(result["height"] + 1),
            str(int(answer_value) - 4) if str(answer_value).isdigit() and int(answer_value) > 4 else "31",
            str(int(answer_value) + 16) if str(answer_value).isdigit() else "57",
            canonical_exact(result["advance_distance"]),
        ]
        use_choice = True
        presentation = "single_choice"
        answer_type = "single_choice"
        payload = {
            "advance_distance": result["advance_distance"],
            "far_tan": result["far_tan"],
            "near_tan": result["near_tan"],
            "round_to_integer": round_flag,
        }
    else:  # BEARING_WALK_HEIGHT_OP
        if not {"walk_distance", "base_bearing_degrees", "elevation_degrees"} <= set(raw):
            raw.setdefault("walk_distance", sp.Integer(rng.choice((100, 200, 300))))
            raw.setdefault("base_bearing_degrees", rng.choice((30, 45, 60)))
            raw.setdefault("elevation_degrees", rng.choice((30, 45, 60)))
        result = solve_height_from_isosceles_bearing_walk_elevation(
            walk_distance=raw["walk_distance"],
            base_bearing_degrees=raw["base_bearing_degrees"],
            elevation_degrees=raw["elevation_degrees"],
        )
        question = (
            f"自A測得目標在東偏北 ${canonical_exact(result['base_bearing_degrees'])}^\\circ$ 且仰角 "
            f"${canonical_exact(result['elevation_degrees'])}^\\circ$；向東行 "
            f"${canonical_exact(result['walk_distance'])}$ 公尺至B後，目標在西偏北 "
            f"${canonical_exact(result['base_bearing_degrees'])}^\\circ$。試求目標高度。"
        )
        answer_value = result["canonical"]
        parts = {"height": answer_value}
        distractors = [
            canonical_exact(result["walk_distance"]),
            canonical_exact(sp.simplify(result["walk_distance"] / 2)),
            canonical_exact(sp.simplify(result["walk_distance"] * sp.sqrt(2))),
            canonical_exact(sp.simplify(result["walk_distance"] * sp.sqrt(3))),
        ]
        use_choice = True
        presentation = "single_choice"
        answer_type = "single_choice"
        payload = {
            "walk_distance": result["walk_distance"],
            "base_bearing_degrees": result["base_bearing_degrees"],
            "elevation_degrees": result["elevation_degrees"],
        }

    if as_choice_requested and op != TOWER_RIVER_OP:
        use_choice = True
        presentation = "single_choice"
        answer_type = "single_choice"
    if op == TOWER_RIVER_OP:
        use_choice = False

    choice_meta = None
    if use_choice:
        scalar = answer_value if isinstance(answer_value, str) else canonical_exact(answer_value)
        choice_meta = _choice_payload(str(scalar), [str(d) for d in distractors], rng)
        answer_value = choice_meta["semantic_answer"]
        parts = {"height": answer_value}

    matrix = {
        "givens": {k: _json_value(v) if isinstance(v, sp.Basic) else v for k, v in payload.items()},
        "answer": {
            "value": answer_value,
            "canonical_form": answer_value,
            "general_form": answer_value,
            "coefficients": [],
            "parts": parts,
        },
        "question_text": question,
        "question": question,
        "explanation_steps": ["由立體測量化為直角三角形三角函數與水平圖形關係計算。"],
        "distractors": distractors,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": op != TAN_RATIO_HEIGHT_OP or not payload.get("round_to_integer", True),
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "presentation_mode": presentation,
            "answer_type": answer_type,
            "reused_capabilities": (
                ["solve_horizontal_from_height_elevation"]
                if op == TOWER_RIVER_OP
                else ["solve_opposite_from_adjacent_elevation"]
                if op == BEARING_WALK_HEIGHT_OP
                else ["solve_two_elevation_unknown_height_formula"]
            ),
        },
        "visual_spec": {"kind": "none"},
        "domain_result": _json_value(result),
    }
    if choice_meta:
        matrix["choices"] = choice_meta["choices"]
        matrix["correct_label"] = choice_meta["correct_label"]
        matrix["semantic_answer"] = choice_meta["semantic_answer"]
    return matrix


def validate_trigonometry_solid_measurement_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = matrix["validation_facts"]["domain_operation"]
        rebuilt = build_trigonometry_solid_measurement_matrix(operation=op, **matrix["givens"])
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
