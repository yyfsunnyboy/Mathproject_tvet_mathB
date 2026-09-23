# -*- coding: utf-8 -*-
"""Exact Law-of-Sines operations for Math B2 §2-1 (no cosine-law mixing)."""

from __future__ import annotations

import random
from typing import Any

import sympy as sp


AREA_SAS_OP = "compute_triangle_area_sas"
SIDE_AND_R_OP = "solve_side_and_circumradius_by_sines"
ANGLE_BY_SINES_OP = "solve_angle_by_law_of_sines"
SIN_FROM_R_OP = "compute_sin_from_side_and_circumradius"
SIDE_RATIO_OP = "solve_side_ratio_by_law_of_sines"
SIDE_BY_SINES_OP = "solve_side_by_law_of_sines"

OPS = frozenset(
    {
        AREA_SAS_OP,
        SIDE_AND_R_OP,
        ANGLE_BY_SINES_OP,
        SIN_FROM_R_OP,
        SIDE_RATIO_OP,
        SIDE_BY_SINES_OP,
    }
)

_SPECIAL_ACUTE = (30, 45, 60)
_SPECIAL_OBTUSE = (120, 135, 150)


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


def _sin_deg(degrees: Any) -> sp.Expr:
    return sp.simplify(sp.sin(sp.rad(_angle_degrees(degrees))))


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, sp.Basic):
        return canonical_exact(value)
    return value


def compute_triangle_area_sas(*, side1: Any, side2: Any, included_angle_degrees: Any) -> dict[str, Any]:
    a = _positive_exact(side1, name="side1")
    b = _positive_exact(side2, name="side2")
    angle = _angle_degrees(included_angle_degrees, name="included_angle")
    area = sp.simplify(sp.Rational(1, 2) * a * b * _sin_deg(angle))
    return {
        "area": area,
        "canonical": canonical_exact(area),
        "side1": a,
        "side2": b,
        "included_angle_degrees": angle,
    }


def solve_side_and_circumradius_by_sines(
    *,
    known_side: Any,
    known_side_angle_degrees: Any,
    other_angle_degrees: Any,
    target_side_angle_degrees: Any | None = None,
) -> dict[str, Any]:
    """Given one side and its opposite angle plus another angle, find target side and R."""
    side = _positive_exact(known_side, name="known_side")
    angle_known = _angle_degrees(known_side_angle_degrees, name="known_side_angle")
    angle_other = _angle_degrees(other_angle_degrees, name="other_angle")
    if angle_known + angle_other >= 180:
        raise ValueError("triangle_angle_sum_exceeds_180")
    angle_third = sp.simplify(180 - angle_known - angle_other)
    allowed = {
        sp.simplify(angle_known),
        sp.simplify(angle_other),
        sp.simplify(angle_third),
    }
    if target_side_angle_degrees is None:
        target_angle = angle_third
    else:
        target_angle = _angle_degrees(target_side_angle_degrees, name="target_side_angle")
        if sp.simplify(target_angle) not in allowed:
            raise ValueError("target_angle_not_in_triangle")
    target_side = sp.simplify(side * _sin_deg(target_angle) / _sin_deg(angle_known))
    radius = sp.simplify(side / (2 * _sin_deg(angle_known)))
    return {
        "target_side": target_side,
        "circumradius": radius,
        "target_angle_degrees": target_angle,
        "canonical_side": canonical_exact(target_side),
        "canonical_radius": canonical_exact(radius),
        "canonical": {
            "side": canonical_exact(target_side),
            "R": canonical_exact(radius),
        },
    }


def solve_angle_by_law_of_sines(
    *,
    side_a: Any,
    side_b: Any,
    angle_a_degrees: Any,
    find: str = "B",
) -> dict[str, Any]:
    """SSA: find unique triangle angle by law of sines (reject ambiguous / invalid)."""
    a = _positive_exact(side_a, name="side_a")
    b = _positive_exact(side_b, name="side_b")
    angle_a = _angle_degrees(angle_a_degrees, name="angle_a")
    sin_b = sp.simplify(b * _sin_deg(angle_a) / a)
    if sin_b.is_real is not True or sin_b < 0 or sin_b > 1:
        raise ValueError("ssa_no_triangle")
    acute = sp.simplify(sp.deg(sp.asin(sin_b)))
    obtuse = sp.simplify(180 - acute)
    candidates: list[sp.Expr] = []
    for cand in (acute, obtuse):
        if cand <= 0 or cand >= 180:
            continue
        if angle_a + cand >= 180:
            continue
        candidates.append(sp.simplify(cand))
    # Prefer the unique valid candidate; if both valid (ambiguous), keep acute only
    # when a > b (standard textbook unique-acute path).
    if len(candidates) == 0:
        raise ValueError("ssa_no_triangle")
    if len(candidates) == 2 and a > b:
        candidates = [candidates[0]]
    if len(candidates) != 1:
        raise ValueError("ssa_ambiguous_case_unsupported")
    angle_b = candidates[0]
    angle_c = sp.simplify(180 - angle_a - angle_b)
    find_key = str(find or "B").strip().upper()
    if find_key == "B":
        answer = angle_b
    elif find_key == "C":
        answer = angle_c
    else:
        raise ValueError("find_must_be_B_or_C")
    return {
        "angle_B_degrees": angle_b,
        "angle_C_degrees": angle_c,
        "answer_degrees": answer,
        "canonical": canonical_exact(answer),
        "find": find_key,
    }


def compute_sin_from_side_and_circumradius(*, side: Any, circumradius: Any) -> dict[str, Any]:
    a = _positive_exact(side, name="side")
    radius = _positive_exact(circumradius, name="circumradius")
    value = sp.simplify(a / (2 * radius))
    if value.is_real is not True or value < 0 or value > 1:
        raise ValueError("sin_value_out_of_range")
    return {"sin_value": value, "canonical": canonical_exact(value)}


def solve_side_ratio_by_law_of_sines(
    *,
    angle_p_degrees: Any,
    angle_q_degrees: Any,
    ratio_of: str = "opposite_p_over_opposite_q",
) -> dict[str, Any]:
    """Return side ratio equal to sin(P):sin(Q) for the requested pair."""
    angle_p = _angle_degrees(angle_p_degrees, name="angle_p")
    angle_q = _angle_degrees(angle_q_degrees, name="angle_q")
    if angle_p + angle_q >= 180:
        raise ValueError("triangle_angle_sum_exceeds_180")
    ratio = sp.simplify(_sin_deg(angle_p) / _sin_deg(angle_q))
    return {
        "ratio": ratio,
        "canonical": canonical_exact(ratio),
        "ratio_of": ratio_of,
        "angle_p_degrees": angle_p,
        "angle_q_degrees": angle_q,
    }


def solve_side_by_law_of_sines(
    *,
    known_side: Any,
    known_angle_degrees: Any,
    target_angle_degrees: Any,
) -> dict[str, Any]:
    side = _positive_exact(known_side, name="known_side")
    known_angle = _angle_degrees(known_angle_degrees, name="known_angle")
    target_angle = _angle_degrees(target_angle_degrees, name="target_angle")
    if known_angle + target_angle >= 180:
        raise ValueError("triangle_angle_sum_exceeds_180")
    target = sp.simplify(side * _sin_deg(target_angle) / _sin_deg(known_angle))
    return {"target_side": target, "canonical": canonical_exact(target)}


def _sample_area_sas(rng: random.Random) -> dict[str, Any]:
    angle = rng.choice(_SPECIAL_ACUTE + _SPECIAL_OBTUSE)
    side1 = sp.Integer(rng.choice((2, 3, 4, 6)))
    # Pick side2 so area is exact and nice with special sin.
    side2 = sp.sqrt(rng.choice((2, 3, 6))) if angle in (30, 150, 120, 60) else sp.Integer(rng.choice((2, 3, 4)))
    if rng.random() < 0.5:
        side1, side2 = side2, side1
    return {"side1": side1, "side2": side2, "included_angle_degrees": angle}


def _sample_side_and_r(rng: random.Random) -> dict[str, Any]:
    # Two angles; known side opposite known_side_angle.
    a1 = rng.choice(_SPECIAL_ACUTE)
    a2 = rng.choice([x for x in (_SPECIAL_ACUTE + _SPECIAL_OBTUSE) if x != a1 and a1 + x < 180])
    known_side = sp.Integer(rng.choice((3, 4, 6))) * sp.sqrt(rng.choice((1, 2, 3, 6)))
    # Target is the remaining angle opposite the unknown side.
    target = 180 - a1 - a2
    return {
        "known_side": known_side,
        "known_side_angle_degrees": a1,
        "other_angle_degrees": a2,
        "target_side_angle_degrees": target,
    }


def _sample_angle_ssa(rng: random.Random) -> dict[str, Any]:
    # Unique SSA: keep A,B acute with A >= B so a >= b (no ambiguous case).
    for _ in range(40):
        angle_a = rng.choice(_SPECIAL_ACUTE)
        angle_b = rng.choice([x for x in _SPECIAL_ACUTE if angle_a + x < 180])
        if angle_a < angle_b:
            angle_a, angle_b = angle_b, angle_a
        scale = sp.Integer(rng.choice((2, 3, 4, 6)))
        side_a = sp.simplify(scale * _sin_deg(angle_a))
        side_b = sp.simplify(scale * _sin_deg(angle_b))
        find = rng.choice(("B", "C"))
        try:
            solve_angle_by_law_of_sines(
                side_a=side_a,
                side_b=side_b,
                angle_a_degrees=angle_a,
                find=find,
            )
        except ValueError:
            continue
        return {
            "side_a": side_a,
            "side_b": side_b,
            "angle_a_degrees": angle_a,
            "find": find,
        }
    raise ValueError("unable_to_sample_unique_ssa")


def _sample_sin_from_r(rng: random.Random) -> dict[str, Any]:
    radius = sp.Integer(rng.choice((2, 3, 4, 5, 6)))
    # Choose sin from {1/2, √2/2, √3/2}
    sin_val = rng.choice((sp.Rational(1, 2), sp.sqrt(2) / 2, sp.sqrt(3) / 2))
    side = sp.simplify(2 * radius * sin_val)
    return {"side": side, "circumradius": radius}


def _sample_side_ratio(rng: random.Random) -> dict[str, Any]:
    # Model AB/AC = c/b = sinC/sinB with given A,B.
    angle_a = rng.choice((105, 120, 135, 75, 90))
    angle_b = rng.choice([x for x in _SPECIAL_ACUTE if angle_a + x < 180])
    angle_c = 180 - angle_a - angle_b
    # AB opposite C, AC opposite B → AB/AC = sinC/sinB
    return {
        "angle_p_degrees": angle_c,
        "angle_q_degrees": angle_b,
        "ratio_of": "AB_over_AC",
        "display_angle_A": angle_a,
        "display_angle_B": angle_b,
    }


def _sample_side_by_sines(rng: random.Random) -> dict[str, Any]:
    known_angle = rng.choice(_SPECIAL_ACUTE)
    target_angle = rng.choice([x for x in (_SPECIAL_ACUTE + _SPECIAL_OBTUSE) if x != known_angle and known_angle + x < 180])
    known_side = sp.Integer(rng.choice((3, 4, 6, 8)))
    return {
        "known_side": known_side,
        "known_angle_degrees": known_angle,
        "target_angle_degrees": target_angle,
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


def build_trigonometry_law_of_sines_matrix(
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
        raise ValueError(f"unsupported_trigonometry_law_of_sines_operation:{op}")
    rng = random.Random(0 if seed is None else int(seed))
    payload = {**dict(constraints or {}), **data}
    # Drop non-math bookkeeping keys from scaffold constraints.
    for bookkeeping in (
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
    ):
        payload.pop(bookkeeping, None)

    if op == AREA_SAS_OP:
        if not {"side1", "side2", "included_angle_degrees"} <= set(payload):
            payload = {**_sample_area_sas(rng), **payload}
        result = compute_triangle_area_sas(**{k: payload[k] for k in ("side1", "side2", "included_angle_degrees")})
        question = (
            f"在△ABC中，已知兩邊長分別為 ${canonical_exact(result['side1'])}$、"
            f"${canonical_exact(result['side2'])}$，夾角為 "
            f"${canonical_exact(result['included_angle_degrees'])}^\\circ$，試求△ABC的面積。"
        )
        parts = {"area": result["canonical"]}
        answer_value = result["canonical"]
        distractors: list[str] = []
    elif op == SIDE_AND_R_OP:
        if not {"known_side", "known_side_angle_degrees", "other_angle_degrees"} <= set(payload):
            payload = {**_sample_side_and_r(rng), **payload}
        kwargs = {
            "known_side": payload["known_side"],
            "known_side_angle_degrees": payload["known_side_angle_degrees"],
            "other_angle_degrees": payload["other_angle_degrees"],
        }
        if payload.get("target_side_angle_degrees") is not None:
            kwargs["target_side_angle_degrees"] = payload["target_side_angle_degrees"]
        result = solve_side_and_circumradius_by_sines(**kwargs)
        question = (
            f"在△ABC中，若$\\angle A={canonical_exact(payload['known_side_angle_degrees'])}^\\circ$，"
            f"$\\angle B={canonical_exact(payload['other_angle_degrees'])}^\\circ$，"
            f"且對應$\\angle A$的邊長為 ${canonical_exact(payload['known_side'])}$，"
            f"試求對應$\\angle C$的邊長及其外接圓半徑 $R$。"
        )
        # Re-label: known is A-side a; other is B; target is C-side c.
        # Override question when caller provides explicit labels.
        if payload.get("question_text"):
            question = str(payload["question_text"])
        parts = {"side": result["canonical_side"], "R": result["canonical_radius"]}
        answer_value = parts
        distractors = []
    elif op == ANGLE_BY_SINES_OP:
        if not {"side_a", "side_b", "angle_a_degrees"} <= set(payload):
            payload = {**_sample_angle_ssa(rng), **payload}
        result = solve_angle_by_law_of_sines(
            side_a=payload["side_a"],
            side_b=payload["side_b"],
            angle_a_degrees=payload["angle_a_degrees"],
            find=str(payload.get("find") or "B"),
        )
        find = result["find"]
        question = (
            f"△ABC中，已知$\\angle A={canonical_exact(payload['angle_a_degrees'])}^\\circ$，"
            f"$a={canonical_exact(payload['side_a'])}$，$b={canonical_exact(payload['side_b'])}$，"
            f"試求$\\angle {find}$。"
        )
        if payload.get("question_text"):
            question = str(payload["question_text"])
        parts = {"angle": result["canonical"]}
        answer_value = result["canonical"]
        distractors = []
    elif op == SIN_FROM_R_OP:
        if not {"side", "circumradius"} <= set(payload):
            # Allow circumcircle area πR^2 as alternate input.
            if payload.get("circumcircle_area") is not None and payload.get("side") is not None:
                area = _positive_exact(payload["circumcircle_area"], name="circumcircle_area")
                radius = sp.simplify(sp.sqrt(area / sp.pi))
                payload = {**payload, "circumradius": radius}
            else:
                payload = {**_sample_sin_from_r(rng), **payload}
        if payload.get("circumcircle_area") is not None and "circumradius" not in payload:
            area = _positive_exact(payload["circumcircle_area"], name="circumcircle_area")
            payload["circumradius"] = sp.simplify(sp.sqrt(area / sp.pi))
        result = compute_sin_from_side_and_circumradius(
            side=payload["side"],
            circumradius=payload["circumradius"],
        )
        if payload.get("circumcircle_area") is not None:
            question = (
                f"已知△ABC中，外接圓面積為 ${canonical_exact(payload['circumcircle_area'])}$ "
                f"且對應$\\angle A$的邊長為 ${canonical_exact(payload['side'])}$，試求$\\sin A$之值。"
            )
        else:
            question = (
                f"已知△ABC外接圓半徑 $R={canonical_exact(payload['circumradius'])}$，"
                f"且 $a={canonical_exact(payload['side'])}$，試求 $\\sin A$。"
            )
        if payload.get("question_text"):
            question = str(payload["question_text"])
        parts = {"sinA": result["canonical"]}
        answer_value = result["canonical"]
        distractors = []
    elif op == SIDE_RATIO_OP:
        if not {"angle_p_degrees", "angle_q_degrees"} <= set(payload):
            payload = {**_sample_side_ratio(rng), **payload}
        result = solve_side_ratio_by_law_of_sines(
            angle_p_degrees=payload["angle_p_degrees"],
            angle_q_degrees=payload["angle_q_degrees"],
            ratio_of=str(payload.get("ratio_of") or "opposite_p_over_opposite_q"),
        )
        angle_a = payload.get("display_angle_A")
        angle_b = payload.get("display_angle_B")
        if angle_a is not None and angle_b is not None:
            question = (
                f"已知△ABC中，$\\angle A={canonical_exact(angle_a)}^\\circ$，"
                f"$\\angle B={canonical_exact(angle_b)}^\\circ$，則"
                f"$\\overline{{AB}}$ 與 $\\overline{{AC}}$ 的比值"
                f"$\\dfrac{{\\overline{{AB}}}}{{\\overline{{AC}}}}$ 為何？"
            )
        else:
            question = (
                f"在△ABC中，兩邊對應角分別為 ${canonical_exact(payload['angle_p_degrees'])}^\\circ$ 與 "
                f"${canonical_exact(payload['angle_q_degrees'])}^\\circ$，求該兩邊長比值。"
            )
        if payload.get("question_text"):
            question = str(payload["question_text"])
        parts = {"ratio": result["canonical"]}
        answer_value = result["canonical"]
        # Common wrong ratios from swapped angles / complementary mistakes.
        distractors = [
            canonical_exact(sp.simplify(1 / result["ratio"])),
            canonical_exact(_sin_deg(payload.get("display_angle_A") or 30) / _sin_deg(payload["angle_q_degrees"])),
            canonical_exact(sp.sqrt(3) / 3),
            canonical_exact(sp.sqrt(2)),
            canonical_exact(sp.sqrt(3)),
        ]
    else:  # SIDE_BY_SINES_OP
        if not {"known_side", "known_angle_degrees", "target_angle_degrees"} <= set(payload):
            payload = {**_sample_side_by_sines(rng), **payload}
        result = solve_side_by_law_of_sines(
            known_side=payload["known_side"],
            known_angle_degrees=payload["known_angle_degrees"],
            target_angle_degrees=payload["target_angle_degrees"],
        )
        question = (
            f"已知△ABC中，$a={canonical_exact(payload['known_side'])}$，"
            f"$\\angle A={canonical_exact(payload['known_angle_degrees'])}^\\circ$，"
            f"$\\angle C={canonical_exact(payload['target_angle_degrees'])}^\\circ$，試求 $c$。"
        )
        if payload.get("question_text"):
            question = str(payload["question_text"])
        parts = {"side": result["canonical"]}
        answer_value = result["canonical"]
        distractors = [
            canonical_exact(sp.simplify(result["target_side"] * sp.sqrt(2))),
            canonical_exact(sp.simplify(result["target_side"] / 2)),
            canonical_exact(sp.Integer(2) * sp.sqrt(3)),
            canonical_exact(sp.Integer(2) * sp.sqrt(6)),
            canonical_exact(sp.Integer(3) * sp.sqrt(2)),
        ]

    choice_meta: dict[str, Any] = {}
    presentation = "short_answer"
    answer_type = "multi_part" if isinstance(answer_value, dict) else "expression"
    use_choice = op in {SIDE_RATIO_OP, SIDE_BY_SINES_OP} and bool(payload.get("as_choice", True))
    if use_choice:
        scalar = (
            str(answer_value)
            if not isinstance(answer_value, dict)
            else str(next(iter(answer_value.values())))
        )
        choice_meta = _choice_payload(scalar, distractors, rng)
        presentation = "single_choice"
        answer_type = "single_choice"
        answer_value = choice_meta["semantic_answer"]
        parts = {"value": choice_meta["semantic_answer"]}

    givens = _json_value({k: v for k, v in payload.items() if k != "question_text"})
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
        "explanation_steps": ["由正弦定理／外接圓關係 $a/\\sin A=2R$ 計算。"],
        "distractors": distractors,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
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


def validate_trigonometry_law_of_sines_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = matrix["validation_facts"]["domain_operation"]
        rebuilt = build_trigonometry_law_of_sines_matrix(operation=op, **matrix["givens"])
        return rebuilt["answer"] == matrix["answer"]
    except (KeyError, TypeError, ValueError):
        return False
