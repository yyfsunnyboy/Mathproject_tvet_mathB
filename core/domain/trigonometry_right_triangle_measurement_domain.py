# -*- coding: utf-8 -*-
"""Exact right-triangle measurement ops for Math B2 §2-2-3 (elevation / depression)."""

from __future__ import annotations

import math
import random
from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Any

import sympy as sp


HEIGHT_FROM_SIGHT_OP = "solve_height_from_sight_line_elevation"
ADJACENT_FROM_LADDER_OP = "solve_adjacent_from_hypotenuse_ground_angle"
OPPOSITE_FROM_ADJACENT_OP = "solve_opposite_from_adjacent_elevation"
HORIZONTAL_FROM_HEIGHT_ELEV_OP = "solve_horizontal_from_height_elevation"
HORIZONTAL_FROM_HEIGHT_DEP_OP = "solve_horizontal_from_height_depression"
TWO_ELEV_SHIFT_OP = "solve_two_elevation_horizontal_shift"
TWO_ELEV_HEIGHT_OP = "solve_two_elevation_unknown_height"
FLAGPOLE_BUILDING_OP = "solve_building_height_with_flagpole_elevations"
BROKEN_TREE_OP = "solve_broken_tree_original_height"
DECIMAL_HEIGHT_OP = "solve_height_decimal_from_sight_line_elevation"

OPS = frozenset(
    {
        HEIGHT_FROM_SIGHT_OP,
        ADJACENT_FROM_LADDER_OP,
        OPPOSITE_FROM_ADJACENT_OP,
        HORIZONTAL_FROM_HEIGHT_ELEV_OP,
        HORIZONTAL_FROM_HEIGHT_DEP_OP,
        TWO_ELEV_SHIFT_OP,
        TWO_ELEV_HEIGHT_OP,
        FLAGPOLE_BUILDING_OP,
        BROKEN_TREE_OP,
        DECIMAL_HEIGHT_OP,
    }
)

_SPECIAL_ACUTE = (30, 45, 60)
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


def _acute_degrees(value: Any, *, name: str = "angle") -> sp.Rational:
    degrees = sp.Rational(str(_exact(value, name=name)))
    if not (0 < degrees < 90):
        raise ValueError(f"{name}_must_be_acute")
    return degrees


def _sin_deg(degrees: Any) -> sp.Expr:
    return sp.simplify(sp.sin(sp.rad(_acute_degrees(degrees))))


def _cos_deg(degrees: Any) -> sp.Expr:
    return sp.simplify(sp.cos(sp.rad(_acute_degrees(degrees))))


def _tan_deg(degrees: Any) -> sp.Expr:
    return sp.simplify(sp.tan(sp.rad(_acute_degrees(degrees))))


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, sp.Basic):
        return canonical_exact(value)
    return value


def solve_height_from_sight_line_elevation(*, sight_length: Any, elevation_degrees: Any) -> dict[str, Any]:
    length = _positive_exact(sight_length, name="sight_length")
    angle = _acute_degrees(elevation_degrees, name="elevation")
    height = sp.simplify(length * _sin_deg(angle))
    return {
        "height": height,
        "canonical": canonical_exact(height),
        "sight_length": length,
        "elevation_degrees": angle,
    }


def solve_adjacent_from_hypotenuse_ground_angle(*, hypotenuse: Any, ground_angle_degrees: Any) -> dict[str, Any]:
    hyp = _positive_exact(hypotenuse, name="hypotenuse")
    angle = _acute_degrees(ground_angle_degrees, name="ground_angle")
    adjacent = sp.simplify(hyp * _cos_deg(angle))
    return {
        "adjacent": adjacent,
        "canonical": canonical_exact(adjacent),
        "hypotenuse": hyp,
        "ground_angle_degrees": angle,
    }


def solve_opposite_from_adjacent_elevation(*, adjacent: Any, elevation_degrees: Any) -> dict[str, Any]:
    adj = _positive_exact(adjacent, name="adjacent")
    angle = _acute_degrees(elevation_degrees, name="elevation")
    opposite = sp.simplify(adj * _tan_deg(angle))
    return {
        "opposite": opposite,
        "canonical": canonical_exact(opposite),
        "adjacent": adj,
        "elevation_degrees": angle,
    }


def solve_horizontal_from_height_and_angle(*, height: Any, angle_degrees: Any) -> dict[str, Any]:
    h = _positive_exact(height, name="height")
    angle = _acute_degrees(angle_degrees, name="angle")
    horizontal = sp.simplify(h / _tan_deg(angle))
    return {
        "horizontal": horizontal,
        "canonical": canonical_exact(horizontal),
        "height": h,
        "angle_degrees": angle,
    }


def solve_two_elevation_horizontal_shift(
    *,
    height: Any,
    near_elevation_degrees: Any,
    far_elevation_degrees: Any,
) -> dict[str, Any]:
    """Known height; move between two elevation stations; return |d_far - d_near|."""
    h = _positive_exact(height, name="height")
    near = _acute_degrees(near_elevation_degrees, name="near_elevation")
    far = _acute_degrees(far_elevation_degrees, name="far_elevation")
    if near == far:
        raise ValueError("elevations_must_differ")
    d_near = sp.simplify(h / _tan_deg(near))
    d_far = sp.simplify(h / _tan_deg(far))
    shift = sp.simplify(sp.Abs(d_far - d_near))
    if shift.is_real is not True or shift <= 0:
        raise ValueError("horizontal_shift_invalid")
    return {
        "shift": shift,
        "near_distance": d_near,
        "far_distance": d_far,
        "canonical": canonical_exact(shift),
        "height": h,
        "near_elevation_degrees": near,
        "far_elevation_degrees": far,
    }


def solve_two_elevation_unknown_height(
    *,
    advance_distance: Any,
    near_elevation_degrees: Any,
    far_elevation_degrees: Any,
) -> dict[str, Any]:
    """Advance toward object from far elev to near elev; find height."""
    advance = _positive_exact(advance_distance, name="advance_distance")
    near = _acute_degrees(near_elevation_degrees, name="near_elevation")
    far = _acute_degrees(far_elevation_degrees, name="far_elevation")
    if not (near > far):
        raise ValueError("near_elevation_must_exceed_far")
    # h/tan(far) - h/tan(near) = advance
    coeff = sp.simplify(1 / _tan_deg(far) - 1 / _tan_deg(near))
    if coeff.is_real is not True or coeff <= 0:
        raise ValueError("two_elevation_height_coeff_invalid")
    height = sp.simplify(advance / coeff)
    return {
        "height": height,
        "canonical": canonical_exact(height),
        "advance_distance": advance,
        "near_elevation_degrees": near,
        "far_elevation_degrees": far,
    }


def solve_building_height_with_flagpole_elevations(
    *,
    flagpole_length: Any,
    building_top_elevation_degrees: Any,
    flagpole_top_elevation_degrees: Any,
) -> dict[str, Any]:
    flag = _positive_exact(flagpole_length, name="flagpole_length")
    elev_b = _acute_degrees(building_top_elevation_degrees, name="building_top_elevation")
    elev_f = _acute_degrees(flagpole_top_elevation_degrees, name="flagpole_top_elevation")
    if not (elev_f > elev_b):
        raise ValueError("flagpole_elevation_must_exceed_building")
    # tan(elev_b)=H/d, tan(elev_f)=(H+flag)/d => (H+flag)/H = tan_f/tan_b
    ratio = sp.simplify(_tan_deg(elev_f) / _tan_deg(elev_b))
    if ratio.is_real is not True or ratio <= 1:
        raise ValueError("flagpole_elevation_ratio_invalid")
    height = sp.simplify(flag / (ratio - 1))
    return {
        "building_height": height,
        "canonical": canonical_exact(height),
        "flagpole_length": flag,
        "building_top_elevation_degrees": elev_b,
        "flagpole_top_elevation_degrees": elev_f,
    }


def solve_broken_tree_original_height(*, tip_to_root: Any, broken_angle_degrees: Any) -> dict[str, Any]:
    """Broken tip on ground tip_to_root away; broken segment makes angle with ground."""
    ground = _positive_exact(tip_to_root, name="tip_to_root")
    angle = _acute_degrees(broken_angle_degrees, name="broken_angle")
    stump = sp.simplify(ground * _tan_deg(angle))
    broken = sp.simplify(ground / _cos_deg(angle))
    total = sp.simplify(stump + broken)
    return {
        "stump_height": stump,
        "broken_length": broken,
        "original_height": total,
        "canonical": canonical_exact(total),
        "tip_to_root": ground,
        "broken_angle_degrees": angle,
    }


def solve_height_decimal_from_sight_line_elevation(
    *,
    sight_length: Any,
    elevation_degrees: Any,
    precision: int = 3,
) -> dict[str, Any]:
    length = float(sp.N(_positive_exact(sight_length, name="sight_length")))
    angle = float(sp.N(_acute_degrees(elevation_degrees, name="elevation")))
    if not (0 < precision <= 8):
        raise ValueError("decimal_precision_out_of_range")
    raw_value = length * math.sin(math.radians(angle))
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        raw = Decimal(str(raw_value))
        quantum = Decimal("1").scaleb(-precision)
        rounded = raw.quantize(quantum, rounding=ROUND_HALF_UP)
    canonical = format(rounded, f".{precision}f")
    return {
        "height": float(rounded),
        "canonical": canonical,
        "sight_length": length,
        "elevation_degrees": angle,
        "precision": precision,
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


def _sample_special_pair(rng: random.Random) -> tuple[int, int]:
    far, near = rng.sample(_SPECIAL_ACUTE, 2)
    if near < far:
        far, near = near, far
    if near == far:
        far, near = 30, 45
    return far, near


def build_trigonometry_right_triangle_measurement_matrix(
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
        raise ValueError(f"unsupported_right_triangle_measurement_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    raw_constraints = dict(constraints or {})
    presentation_hint = str(raw_constraints.get("presentation_mode") or data.get("presentation_mode") or "").strip()
    answer_hint = str(raw_constraints.get("answer_type") or data.get("answer_type") or "").strip()
    payload = {**raw_constraints, **data}
    for key in _BOOKKEEPING:
        payload.pop(key, None)
    if presentation_hint == "single_choice" or answer_hint in {"single_choice", "choice"}:
        payload.setdefault("as_choice", True)

    as_choice_requested = bool(payload.get("as_choice"))
    force_choice_requested = bool(payload.get("force_choice"))
    distractors: list[str] = []
    choice_ops = {
        HORIZONTAL_FROM_HEIGHT_ELEV_OP,
        HORIZONTAL_FROM_HEIGHT_DEP_OP,
        TWO_ELEV_SHIFT_OP,
        FLAGPOLE_BUILDING_OP,
        OPPOSITE_FROM_ADJACENT_OP,
    }

    if op == HEIGHT_FROM_SIGHT_OP:
        if not {"sight_length", "elevation_degrees"} <= set(payload):
            payload.setdefault("sight_length", sp.Integer(rng.choice((80, 100, 120, 150))))
            payload.setdefault("elevation_degrees", rng.choice(_SPECIAL_ACUTE))
        result = solve_height_from_sight_line_elevation(
            sight_length=payload["sight_length"],
            elevation_degrees=payload["elevation_degrees"],
        )
        sight = result["sight_length"]
        elev = result["elevation_degrees"]
        question = (
            f"放出長度 ${canonical_exact(sight)}$ 公尺的風箏線，"
            f"仰角為 ${canonical_exact(elev)}^\\circ$，試求風箏高度。"
        )
        answer_value = result["canonical"]
        parts = {"height": answer_value}
        distractors = [
            canonical_exact(sp.simplify(result["height"] * sp.Integer(2))),
            canonical_exact(sp.simplify(sight * _cos_deg(elev))),
            canonical_exact(sp.simplify(sight * _tan_deg(elev))),
        ]
        payload = {"sight_length": sight, "elevation_degrees": elev}
    elif op == ADJACENT_FROM_LADDER_OP:
        if not {"hypotenuse", "ground_angle_degrees"} <= set(payload):
            payload.setdefault("hypotenuse", sp.Integer(rng.choice((5, 6, 8, 10))))
            payload.setdefault("ground_angle_degrees", rng.choice(_SPECIAL_ACUTE))
        result = solve_adjacent_from_hypotenuse_ground_angle(
            hypotenuse=payload["hypotenuse"],
            ground_angle_degrees=payload["ground_angle_degrees"],
        )
        hyp = result["hypotenuse"]
        g_ang = result["ground_angle_degrees"]
        question = (
            f"長 ${canonical_exact(hyp)}$ 公尺的梯子斜靠牆壁，"
            f"與地面夾角 ${canonical_exact(g_ang)}^\\circ$，"
            f"試求梯子底端到牆角的距離。"
        )
        answer_value = result["canonical"]
        parts = {"distance": answer_value}
        distractors = [
            canonical_exact(sp.simplify(hyp * _sin_deg(g_ang))),
            canonical_exact(sp.simplify(hyp * _tan_deg(g_ang))),
            canonical_exact(hyp),
        ]
        payload = {"hypotenuse": hyp, "ground_angle_degrees": g_ang}
    elif op == OPPOSITE_FROM_ADJACENT_OP:
        if not {"adjacent", "elevation_degrees"} <= set(payload):
            payload.setdefault("adjacent", sp.Integer(rng.choice((30, 50, 60, 80))))
            payload.setdefault("elevation_degrees", rng.choice(_SPECIAL_ACUTE))
        stem_kind = str(payload.get("stem_kind") or "tower")
        result = solve_opposite_from_adjacent_elevation(
            adjacent=payload["adjacent"],
            elevation_degrees=payload["elevation_degrees"],
        )
        adj = result["adjacent"]
        elev = result["elevation_degrees"]
        if stem_kind == "river":
            question = (
                f"已知水平邊長 ${canonical_exact(adj)}$ 公尺，"
                f"觀測角 ${canonical_exact(elev)}^\\circ$，"
                f"試求對邊（河寬）長度。"
            )
        else:
            question = (
                f"在離塔基 ${canonical_exact(adj)}$ 公尺處測得塔頂仰角為 "
                f"${canonical_exact(elev)}^\\circ$，試求塔高。"
            )
        answer_value = result["canonical"]
        parts = {"opposite": answer_value}
        distractors = [
            canonical_exact(sp.simplify(adj * _sin_deg(elev))),
            canonical_exact(sp.simplify(adj / _tan_deg(elev))),
            canonical_exact(adj),
            canonical_exact(sp.simplify(adj * sp.sqrt(3))),
        ]
        payload = {"adjacent": adj, "elevation_degrees": elev, "stem_kind": stem_kind}
    elif op in {HORIZONTAL_FROM_HEIGHT_ELEV_OP, HORIZONTAL_FROM_HEIGHT_DEP_OP}:
        if not {"height", "angle_degrees"} <= set(payload):
            payload.setdefault("height", sp.Integer(rng.choice((100, 200, 300, 508))))
            payload.setdefault("angle_degrees", rng.choice(_SPECIAL_ACUTE))
        result = solve_horizontal_from_height_and_angle(
            height=payload["height"],
            angle_degrees=payload["angle_degrees"],
        )
        height = result["height"]
        ang = result["angle_degrees"]
        if op == HORIZONTAL_FROM_HEIGHT_DEP_OP:
            question = (
                f"大樓高 ${canonical_exact(height)}$ 公尺，自樓頂測得地面一點俯角為 "
                f"${canonical_exact(ang)}^\\circ$，試求該點與大樓的水平距離。"
            )
        else:
            question = (
                f"大樓高 ${canonical_exact(height)}$ 公尺，測得樓頂仰角為 "
                f"${canonical_exact(ang)}^\\circ$，試求觀測點到大樓的水平距離。"
            )
        answer_value = result["canonical"]
        parts = {"horizontal": answer_value}
        distractors = [
            canonical_exact(sp.simplify(height * _tan_deg(ang))),
            canonical_exact(sp.simplify(height / 2)),
            canonical_exact(height),
            canonical_exact(sp.simplify(height * sp.sqrt(3))),
        ]
        payload = {"height": height, "angle_degrees": ang}
    elif op == TWO_ELEV_SHIFT_OP:
        if not {"height", "near_elevation_degrees", "far_elevation_degrees"} <= set(payload):
            far, near = _sample_special_pair(rng)
            payload.setdefault("height", sp.Integer(rng.choice((100, 200, 300))))
            payload.setdefault("near_elevation_degrees", near)
            payload.setdefault("far_elevation_degrees", far)
        result = solve_two_elevation_horizontal_shift(
            height=payload["height"],
            near_elevation_degrees=payload["near_elevation_degrees"],
            far_elevation_degrees=payload["far_elevation_degrees"],
        )
        height = result["height"]
        near = result["near_elevation_degrees"]
        far = result["far_elevation_degrees"]
        question = (
            f"已知高度 ${canonical_exact(height)}$ 公尺，先測得仰角 "
            f"${canonical_exact(near)}^\\circ$，再水平移動後仰角變為 "
            f"${canonical_exact(far)}^\\circ$，試求水平移動距離。"
        )
        answer_value = result["canonical"]
        parts = {"shift": answer_value}
        distractors = [
            canonical_exact(height),
            canonical_exact(sp.simplify(height * sp.sqrt(3))),
            canonical_exact(sp.simplify(height * (sp.sqrt(3) + 1))),
            canonical_exact(sp.simplify(height * (sp.sqrt(3) - 1))),
        ]
        payload = {
            "height": height,
            "near_elevation_degrees": near,
            "far_elevation_degrees": far,
        }
    elif op == TWO_ELEV_HEIGHT_OP:
        if not {"advance_distance", "near_elevation_degrees", "far_elevation_degrees"} <= set(payload):
            far, near = _sample_special_pair(rng)
            payload.setdefault("advance_distance", sp.Integer(rng.choice((40, 100, 200, 500))))
            payload.setdefault("near_elevation_degrees", near)
            payload.setdefault("far_elevation_degrees", far)
        result = solve_two_elevation_unknown_height(
            advance_distance=payload["advance_distance"],
            near_elevation_degrees=payload["near_elevation_degrees"],
            far_elevation_degrees=payload["far_elevation_degrees"],
        )
        advance = result["advance_distance"]
        near = result["near_elevation_degrees"]
        far = result["far_elevation_degrees"]
        question = (
            f"自遠處測得仰角 ${canonical_exact(far)}^\\circ$，"
            f"朝目標前進 ${canonical_exact(advance)}$ 公尺後仰角為 "
            f"${canonical_exact(near)}^\\circ$，試求目標高度。"
        )
        answer_value = result["canonical"]
        parts = {"height": answer_value}
        distractors = [
            canonical_exact(advance),
            canonical_exact(sp.simplify(advance * sp.sqrt(3))),
            canonical_exact(sp.simplify(advance / 2)),
            canonical_exact(sp.simplify(result["height"] + 10)),
        ]
        payload = {
            "advance_distance": advance,
            "near_elevation_degrees": near,
            "far_elevation_degrees": far,
        }
    elif op == FLAGPOLE_BUILDING_OP:
        if not {
            "flagpole_length",
            "building_top_elevation_degrees",
            "flagpole_top_elevation_degrees",
        } <= set(payload):
            payload.setdefault("flagpole_length", sp.Integer(rng.choice((10, 20, 30))))
            far, near = _sample_special_pair(rng)
            payload.setdefault("building_top_elevation_degrees", far)
            payload.setdefault("flagpole_top_elevation_degrees", near)
        result = solve_building_height_with_flagpole_elevations(
            flagpole_length=payload["flagpole_length"],
            building_top_elevation_degrees=payload["building_top_elevation_degrees"],
            flagpole_top_elevation_degrees=payload["flagpole_top_elevation_degrees"],
        )
        flag = result["flagpole_length"]
        elev_b = result["building_top_elevation_degrees"]
        elev_f = result["flagpole_top_elevation_degrees"]
        question = (
            f"建築物上旗桿長 ${canonical_exact(flag)}$ 公尺，"
            f"測得建築物頂端仰角 ${canonical_exact(elev_b)}^\\circ$，"
            f"旗桿頂端仰角 ${canonical_exact(elev_f)}^\\circ$，"
            f"試求建築物高度。"
        )
        answer_value = result["canonical"]
        parts = {"building_height": answer_value}
        distractors = [
            canonical_exact(sp.simplify(flag * (sp.sqrt(3) + 1))),
            canonical_exact(sp.simplify(flag * (sp.sqrt(3) - 1))),
            canonical_exact(flag),
            canonical_exact(sp.simplify(flag * sp.sqrt(3))),
        ]
        payload = {
            "flagpole_length": flag,
            "building_top_elevation_degrees": elev_b,
            "flagpole_top_elevation_degrees": elev_f,
        }
    elif op == BROKEN_TREE_OP:
        if not {"tip_to_root", "broken_angle_degrees"} <= set(payload):
            payload.setdefault("tip_to_root", sp.Integer(rng.choice((4, 6, 8, 9))))
            payload.setdefault("broken_angle_degrees", rng.choice((30, 45, 60)))
        result = solve_broken_tree_original_height(
            tip_to_root=payload["tip_to_root"],
            broken_angle_degrees=payload["broken_angle_degrees"],
        )
        ground = result["tip_to_root"]
        bang = result["broken_angle_degrees"]
        question = (
            f"大樹吹折後樹頂著地與樹根相距 ${canonical_exact(ground)}$ 公尺，"
            f"折斷段與地面夾角 ${canonical_exact(bang)}^\\circ$，"
            f"試求大樹原本高度。"
        )
        answer_value = result["canonical"]
        parts = {"original_height": answer_value}
        distractors = [
            canonical_exact(result["stump_height"]),
            canonical_exact(result["broken_length"]),
            canonical_exact(ground),
            canonical_exact(sp.simplify(ground * sp.sqrt(3))),
        ]
        payload = {"tip_to_root": ground, "broken_angle_degrees": bang}
    else:  # DECIMAL_HEIGHT_OP
        if not {"sight_length", "elevation_degrees"} <= set(payload):
            payload.setdefault("sight_length", rng.choice((50, 80, 100, 120)))
            payload.setdefault("elevation_degrees", rng.choice((35, 40, 50, 55, 65, 70)))
        precision = int(payload.get("precision") or 3)
        result = solve_height_decimal_from_sight_line_elevation(
            sight_length=payload["sight_length"],
            elevation_degrees=payload["elevation_degrees"],
            precision=precision,
        )
        sight = result["sight_length"]
        elev = result["elevation_degrees"]
        question = (
            f"放出 ${canonical_exact(sight)}$ 公尺長的線，仰角為 "
            f"${canonical_exact(elev)}^\\circ$，"
            f"試求高度（四捨五入到小數點後第 {precision} 位）。"
        )
        answer_value = result["canonical"]
        parts = {"height": answer_value}
        alt = solve_height_decimal_from_sight_line_elevation(
            sight_length=sight,
            elevation_degrees=elev,
            precision=max(1, precision - 1),
        )
        distractors = [
            alt["canonical"],
            format(
                Decimal(str(float(sight) * math.cos(math.radians(float(elev))))).quantize(
                    Decimal("0.001")
                ),
                ".3f",
            ),
            format(Decimal(str(float(sight))).quantize(Decimal("0.001")), ".3f"),
        ]
        payload = {
            "sight_length": sight,
            "elevation_degrees": elev,
            "precision": precision,
        }
    use_choice = bool(as_choice_requested or (force_choice_requested and op in choice_ops))
    if op == DECIMAL_HEIGHT_OP:
        use_choice = False
        presentation = "short_answer"
        answer_type = "expression"
    elif use_choice:
        presentation = "single_choice"
        answer_type = "single_choice"
    else:
        presentation = "short_answer"
        answer_type = "expression"

    choice_meta = _choice_payload(answer_value, distractors, rng) if use_choice else None

    # Persist only solver inputs in givens (stable rebuild).
    givens: dict[str, Any] = {}
    for key, value in payload.items():
        if key in {"stem_kind"}:
            givens[key] = value
            continue
        if isinstance(value, (int, float, str, bool)) or isinstance(value, sp.Basic):
            givens[key] = _json_value(value) if isinstance(value, sp.Basic) else value

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
        "explanation_steps": ["由直角三角形三角函數關係計算。"],
        "distractors": distractors,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": op != DECIMAL_HEIGHT_OP,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
            "presentation_mode": presentation,
            "answer_type": answer_type,
        },
        "visual_spec": {"kind": "none"},
        "domain_result": _json_value(result),
    }
    if choice_meta:
        matrix["choices"] = choice_meta["choices"]
        matrix["correct_label"] = choice_meta["correct_label"]
        matrix["semantic_answer"] = choice_meta["semantic_answer"]
    return matrix


def validate_trigonometry_right_triangle_measurement_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = matrix["validation_facts"]["domain_operation"]
        rebuilt = build_trigonometry_right_triangle_measurement_matrix(operation=op, **matrix["givens"])
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
