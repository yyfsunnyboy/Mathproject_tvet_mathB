# -*- coding: utf-8 -*-
"""Shared angle-measure operations for vocational Math B2 section 1-1.

Operations are reusable primitives. Component generate.py supplies topology
via constraints; this module owns the mathematics.
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

_SUPPORTED_OPS = frozenset(
    {
        "convert_angle_measure",
        "sector_arc_and_area",
        "coterminal_angles",
    }
)

_SPECIAL_DEGREES = (0, 30, 45, 60, 90, 120, 135, 150, 180, 270, 360)


def _frac(val: Any) -> Fraction:
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val)
    text = str(val).strip().replace(" ", "")
    if "/" in text:
        num, den = text.split("/", 1)
        return Fraction(int(num), int(den))
    return Fraction(text)


def _pi_plain(coeff: Fraction) -> str:
    coeff = Fraction(coeff)
    if coeff == 0:
        return "0"
    sign = "-" if coeff < 0 else ""
    abs_c = abs(coeff)
    if abs_c.denominator == 1:
        if abs_c.numerator == 1:
            return f"{sign}pi"
        return f"{sign}{abs_c.numerator}*pi"
    if abs_c.numerator == 1:
        return f"{sign}pi/{abs_c.denominator}"
    return f"{sign}{abs_c.numerator}*pi/{abs_c.denominator}"


def _pi_latex(coeff: Fraction) -> str:
    coeff = Fraction(coeff)
    if coeff == 0:
        return "0"
    sign = "-" if coeff < 0 else ""
    abs_c = abs(coeff)
    if abs_c.denominator == 1:
        if abs_c.numerator == 1:
            return f"{sign}\\pi"
        return f"{sign}{abs_c.numerator}\\pi"
    num = "\\pi" if abs_c.numerator == 1 else f"{abs_c.numerator}\\pi"
    return f"{sign}\\dfrac{{{num}}}{{{abs_c.denominator}}}"


def _deg_plain(val: Fraction) -> str:
    val = Fraction(val)
    if val.denominator == 1:
        return str(val.numerator)
    return f"{val.numerator}/{val.denominator}"


def degrees_to_pi_coeff(degrees: Any) -> Fraction:
    """Convert a degree measure to the coefficient of π (radians / π)."""
    return _frac(degrees) / 180


def pi_coeff_to_degrees(coeff: Any) -> Fraction:
    """Convert a π-coefficient (radians / π) to degrees."""
    return _frac(coeff) * 180


def radians_plain_to_pi_coeff(radians_without_pi: Any) -> Fraction:
    """Interpret a raw radian number θ as θ/π * π."""
    return _frac(radians_without_pi)


def sector_arc_length_pi_coeff(radius: Any, theta_pi_coeff: Any) -> Fraction:
    """S = rθ with θ = kπ → coefficient of π in the arc length."""
    return _frac(radius) * _frac(theta_pi_coeff)


def sector_area_pi_coeff(radius: Any, theta_pi_coeff: Any) -> Fraction:
    """A = (1/2) r² θ with θ = kπ → coefficient of π in the area."""
    r = _frac(radius)
    return (r * r * _frac(theta_pi_coeff)) / 2


def is_coterminal_degrees(a: Any, b: Any) -> bool:
    diff = _frac(a) - _frac(b)
    if diff.denominator == 0:
        return False
    return diff % 360 == 0


def is_coterminal_pi(a_coeff: Any, b_coeff: Any) -> bool:
    diff = _frac(a_coeff) - _frac(b_coeff)
    return diff % 2 == 0


def min_pos_max_neg_degrees(degrees: Any) -> tuple[Fraction, Fraction]:
    """Smallest positive coterminal in (0, 360] and largest negative in [-360, 0)."""
    r = _frac(degrees) % 360
    if r == 0:
        return Fraction(360), Fraction(-360)
    return r, r - 360


def min_pos_max_neg_pi(coeff: Any) -> tuple[Fraction, Fraction]:
    """Smallest positive coterminal kπ with k in (0, 2] and largest negative in [-2, 0)."""
    r = _frac(coeff) % 2
    if r == 0:
        return Fraction(2), Fraction(-2)
    return r, r - 2


def clock_hour_interval_clockwise(degrees: Any) -> tuple[int, int]:
    """Clockwise from 12: return the two hour numbers the hand lies between.

    12 o'clock is hour 12 at 0°. Hour h (1–11) sits at 30h degrees.
    """
    pos = _frac(degrees) % 360
    if pos == 0:
        return (12, 12)
    hour_index = int(pos // 30)  # 0 at 12, 1 at 1 o'clock, ...
    if hour_index == 0:
        return (12, 1)
    if hour_index == 11:
        return (11, 12)
    return (hour_index, hour_index + 1)


def _answer_bundle(canonical: str, *, parts: dict[str, str] | None = None, value: Any = None) -> dict[str, Any]:
    payload_value = value if value is not None else (parts if parts is not None else canonical)
    return {
        "canonical_form": canonical,
        "general_form": canonical,
        "coefficients": [],
        "parts": parts or {},
        "value": payload_value,
    }


def _matrix(
    *,
    op: str,
    givens: dict[str, Any],
    answer: dict[str, Any],
    explanation_steps: list[str],
    distractors: list[Any] | None = None,
    visual_spec: dict[str, Any] | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
) -> dict[str, Any]:
    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors or [],
        "explanation_steps": explanation_steps,
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile or "vocational_high_b",
            "difficulty_profile": difficulty_profile or "easy",
        },
        "visual_spec": visual_spec or {"kind": "none", "points": [], "lines": []},
        "question_text": givens.get("question_text"),
        "question": givens.get("question_text"),
    }


def _sample_degree(rng: random.Random) -> int:
    pool = [
        30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330,
        -30, -45, -60, -90, -120, -135, -150, -180, -210, -240, -270, -300,
        390, 450, 540, 560, 720, -390, -450, -570,
    ]
    return int(rng.choice(pool))


def _sample_pi_coeff(rng: random.Random) -> Fraction:
    pool = [
        Fraction(1, 6), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2),
        Fraction(2, 3), Fraction(3, 4), Fraction(5, 6), Fraction(1),
        Fraction(5, 4), Fraction(4, 3), Fraction(3, 2), Fraction(5, 3),
        Fraction(7, 4), Fraction(11, 6), Fraction(2),
        Fraction(-1, 6), Fraction(-1, 3), Fraction(-1, 2), Fraction(-2, 3),
        Fraction(-5, 6), Fraction(-1), Fraction(-5, 3), Fraction(-7, 4),
        Fraction(5, 6), Fraction(23, 5), Fraction(15, 4), Fraction(-11, 3),
        Fraction(-21, 4),
    ]
    return Fraction(rng.choice(pool))


def _build_convert(rng: random.Random, constraints: dict[str, Any]) -> dict[str, Any]:
    variant = str(constraints.get("variant") or "two_way").strip()
    items = constraints.get("items")
    if variant == "special_angle_table":
        filled = constraints.get("filled_radian_degrees") or [30, 90, 180, 270]
        filled_set = {int(x) for x in filled}
        blanks: dict[str, str] = {}
        blank_cells: list[dict[str, Any]] = []
        radian_row: list[str] = []
        col = 0
        for deg in _SPECIAL_DEGREES:
            coeff = degrees_to_pi_coeff(deg)
            cell = _pi_plain(coeff)
            if deg in filled_set:
                radian_row.append(_pi_latex(coeff))
            else:
                radian_row.append("")
                key = f"c{col}"
                blanks[key] = cell
                blank_cells.append(
                    {
                        "row": 1,
                        "col": col + 1,
                        "field_key": key,
                        "expected_answer": cell,
                        "input_type": "expression",
                    }
                )
            col += 1
        header = ["度"] + [f"{d}^\\circ" for d in _SPECIAL_DEGREES]
        rows = [header, ["弧度"] + radian_row]
        question = "請完成下列常用特別角的「度度量」與「弧度量」之對照表。"
        canonical = "；".join(f"{k}={v}" for k, v in blanks.items())
        return {
            "givens": {
                "question_text": question,
                "variant": variant,
                "table_rows": rows,
                "blank_cells": blank_cells,
            },
            "answer": _answer_bundle(canonical, parts=blanks, value=blanks),
            "explanation_steps": ["利用 π = 180°，將度度量乘以 π/180 化為弧度。"],
            "visual_spec": {
                "kind": "table",
                "type": "table_fill",
                "rows": rows,
                "blank_cells": blank_cells,
                "show_blank_labels": False,
                "blank_label_mode": "complete_table",
            },
        }

    if variant in {"deg_to_rad_list", "rad_to_deg_list"}:
        if not isinstance(items, list) or not items:
            n = 2 if variant == "deg_to_rad_list" else 3
            items = []
            for _ in range(n):
                if variant == "deg_to_rad_list":
                    items.append({"kind": "deg_to_rad", "degrees": _sample_degree(rng)})
                else:
                    if rng.random() < 0.25:
                        items.append({"kind": "rad_number_to_deg", "radians": rng.choice([2, 3, 4, 5])})
                    else:
                        items.append({"kind": "rad_to_deg", "pi_coeff": str(_sample_pi_coeff(rng))})
        parts: dict[str, str] = {}
        prompts: list[str] = []
        for idx, item in enumerate(items, start=1):
            kind = str(item.get("kind") or variant.replace("_list", "")).strip()
            key = f"part_{idx}"
            if kind in {"deg_to_rad", "deg_to_rad_list"}:
                deg = _frac(item["degrees"])
                ans = _pi_plain(degrees_to_pi_coeff(deg))
                prompts.append(f"({idx}) 將 ${deg}\\circ$ 化為弧度。")
            elif kind in {"rad_number_to_deg"}:
                raw = _frac(item["radians"])
                # θ rad = θ * 180/π degrees
                deg_over_pi = raw * 180
                ans = f"{_deg_plain(deg_over_pi)}/pi"
                prompts.append(f"({idx}) 將 ${raw}$ 化為度。")
            else:
                coeff = _frac(item.get("pi_coeff") or item.get("coeff"))
                ans = _deg_plain(pi_coeff_to_degrees(coeff))
                prompts.append(f"({idx}) 將 ${_pi_latex(coeff)}$ 化為度。")
            parts[key] = ans
        question = "將下列各角化成指定單位：\n" + "\n".join(prompts)
        canonical = "；".join(f"{k}={v}" for k, v in parts.items())
        return {
            "givens": {"question_text": question, "variant": variant, "items": items},
            "answer": _answer_bundle(canonical, parts=parts, value=parts),
            "explanation_steps": ["利用 π = 180° 換算度與弧度。"],
        }

    # two_way default: (1) deg→rad (2) rad→deg
    if isinstance(items, list) and len(items) >= 2:
        deg = _frac(items[0]["degrees"])
        coeff = _frac(items[1].get("pi_coeff") or items[1].get("coeff"))
    else:
        deg = Fraction(_sample_degree(rng))
        coeff = _sample_pi_coeff(rng)
    rad_ans = _pi_plain(degrees_to_pi_coeff(deg))
    deg_ans = _deg_plain(pi_coeff_to_degrees(coeff))
    parts = {"part_1": rad_ans, "part_2": deg_ans}
    question = (
        f"(1)試將 ${ _deg_plain(deg) }^\\circ$ 化為弧度。\n"
        f"(2)試將 ${_pi_latex(coeff)}$ 化為度。"
    )
    canonical = f"{rad_ans}；{deg_ans}"
    return {
        "givens": {
            "question_text": question,
            "variant": "two_way",
            "degrees": str(deg),
            "pi_coeff": str(coeff),
        },
        "answer": _answer_bundle(canonical, parts=parts, value=parts),
        "explanation_steps": [
            "利用 π = 180°，所以 1° = π/180。",
            f"(1) {_deg_plain(deg)}° = {_deg_plain(deg)} × π/180 = {_pi_latex(degrees_to_pi_coeff(deg))}",
            f"(2) {_pi_latex(coeff)} = {coeff} × 180° = {deg_ans}°",
        ],
    }


def _build_sector(rng: random.Random, constraints: dict[str, Any]) -> dict[str, Any]:
    variant = str(constraints.get("variant") or "given_angle").strip()
    if variant == "equal_slices":
        radius = int(constraints.get("radius") or rng.choice([8, 9, 12, 15, 16, 18]))
        slices = int(constraints.get("slices") or rng.choice([3, 4, 6, 8, 9]))
        theta_deg = Fraction(360, slices)
        k = degrees_to_pi_coeff(theta_deg)
        area = _pi_plain(sector_area_pi_coeff(radius, k))
        arc = _pi_plain(sector_arc_length_pi_coeff(radius, k))
        include_theta = bool(constraints.get("include_theta", False))
        if include_theta:
            parts = {"part_1": _pi_plain(k), "part_2": arc, "part_3": area}
            question = (
                f"半徑為 {radius} 的圓被分成 {slices} 塊相等扇形。"
                "試求每一塊的 (1)圓心角弧度 (2)弧長 S (3)面積 A。"
            )
        else:
            parts = {"part_1": area, "part_2": arc}
            question = (
                f"半徑為 {radius} 公分的圓形被切成 {slices} 塊大小一樣的扇形，"
                "試求每一塊扇形的 (1)面積 A (2)弧長 S。"
            )
        canonical = "；".join(parts.values())
        return {
            "givens": {
                "question_text": question,
                "variant": variant,
                "radius": radius,
                "slices": slices,
                "theta_degrees": str(theta_deg),
            },
            "answer": _answer_bundle(canonical, parts=parts, value=parts),
            "explanation_steps": [
                f"圓心角 = 360°/{slices} = {theta_deg}° = {_pi_latex(k)}。",
                f"A = (1/2)r^2 θ，S = rθ。",
            ],
        }

    if variant == "pendulum":
        radius = int(constraints.get("radius") or rng.choice([10, 12, 15, 18]))
        half = int(constraints.get("half_angle_deg") or rng.choice([10, 12, 15, 18, 20]))
        theta_deg = 2 * half
        k = degrees_to_pi_coeff(theta_deg)
        area = _pi_plain(sector_area_pi_coeff(radius, k))
        arc = _pi_plain(sector_arc_length_pi_coeff(radius, k))
        parts = {"part_1": area, "part_2": arc}
        question = (
            f"鐘擺長為 {radius} 公分，左右最大擺角各為 {half}°，"
            "試求：(1)鐘擺掃出的最大面積 (2)鐘擺底端揮出的最大弧長。"
        )
        return {
            "givens": {
                "question_text": question,
                "variant": variant,
                "radius": radius,
                "half_angle_deg": half,
            },
            "answer": _answer_bundle(f"{area}；{arc}", parts=parts, value=parts),
            "explanation_steps": [
                f"總圓心角 = {half}° + {half}° = {theta_deg}° = {_pi_latex(k)}。",
                "A = (1/2)r^2 θ，S = rθ。",
            ],
        }

    if variant in {"equal_n_area", "single_area"}:
        radius = int(constraints.get("radius") or rng.choice([6, 8, 10, 12, 20]))
        if constraints.get("theta_degrees") is not None:
            theta_deg = _frac(constraints["theta_degrees"])
            k = degrees_to_pi_coeff(theta_deg)
            prompt = (
                f"半徑 {radius} 公尺、圓心角 { _deg_plain(theta_deg) }° 的扇形，"
                "其面積為何？"
            )
        else:
            slices = int(constraints.get("slices") or rng.choice([3, 4, 6]))
            k = degrees_to_pi_coeff(Fraction(360, slices))
            prompt = f"半徑 {radius} 公尺的圓平分成 {slices} 等分，每一等分的扇形面積為多少？"
        area = _pi_plain(sector_area_pi_coeff(radius, k))
        return {
            "givens": {"question_text": prompt, "variant": variant, "radius": radius},
            "answer": _answer_bundle(area, value=area),
            "explanation_steps": ["A = (1/2) r^2 θ，θ 以弧度計。"],
        }

    # given_angle: optional convert + S + A
    radius = int(constraints.get("radius") or rng.choice([6, 8, 9, 12, 15, 16]))
    theta_deg = _frac(constraints.get("theta_degrees") or rng.choice([30, 45, 60, 90, 120, 135, 150]))
    include_convert = bool(constraints.get("include_convert", True))
    k = degrees_to_pi_coeff(theta_deg)
    arc = _pi_plain(sector_arc_length_pi_coeff(radius, k))
    area = _pi_plain(sector_area_pi_coeff(radius, k))
    if include_convert:
        parts = {"part_1": _pi_plain(k), "part_2": arc, "part_3": area}
        question = (
            f"設一扇形半徑為 {radius} 公分，所對應的圓心角為 {_deg_plain(theta_deg)}°，試求：\n"
            "(1)將圓心角化為弧度。(2)此扇形弧長 S。(3)此扇形面積 A。"
        )
    else:
        parts = {"part_1": arc, "part_2": area}
        question = (
            f"設一扇形半徑為 {radius} 公分，所對應的圓心角為 {_deg_plain(theta_deg)}°，試求：\n"
            "(1)此扇形弧長 S。(2)此扇形面積 A。"
        )
    canonical = "；".join(parts.values())
    return {
        "givens": {
            "question_text": question,
            "variant": "given_angle",
            "radius": radius,
            "theta_degrees": str(theta_deg),
        },
        "answer": _answer_bundle(canonical, parts=parts, value=parts),
        "explanation_steps": [
            f"θ = {_deg_plain(theta_deg)}° = {_pi_latex(k)}。",
            "S = rθ，A = (1/2)r^2 θ。",
        ],
    }


def _build_coterminal(rng: random.Random, constraints: dict[str, Any]) -> dict[str, Any]:
    variant = str(constraints.get("variant") or "identify_which").strip()
    if variant == "clock_choice":
        degrees = int(constraints.get("degrees") or rng.choice([2019, 1819, 2219, 1080, 2190, 1470]))
        low, high = clock_hour_interval_clockwise(degrees)
        correct_text = f"分針指在{low} 跟{high} 之間"
        intervals = [(9, 10), (7, 8), (5, 6), (3, 4), (11, 12), (1, 2), (4, 5), (8, 9)]
        distractors: list[str] = []
        for a, b in intervals:
            text = f"分針指在{a} 跟{b} 之間"
            if {a, b} != {low, high} and text not in distractors:
                distractors.append(text)
            if len(distractors) >= 3:
                break
        question = (
            f"假設分針原始指在時鐘 12 的位置，現將分針依順時針的方向轉了 {degrees}°。"
            "試問下列敘述何者正確？"
        )
        return {
            "givens": {
                "question_text": question,
                "variant": variant,
                "degrees": degrees,
                "source_choices": [correct_text, *distractors],
            },
            "answer": _answer_bundle(correct_text, value=correct_text),
            "distractors": distractors,
            "explanation_steps": [
                "鐘面上每格 6°；最小正同界角為該轉角除以 360° 的餘數。",
                f"{degrees}° 的最小正同界角落在 {low} 點與 {high} 點之間。",
            ],
        }

    if variant == "min_pos_max_neg":
        items = constraints.get("items")
        if not isinstance(items, list) or not items:
            items = []
            for _ in range(int(constraints.get("n_items") or 2)):
                if rng.random() < 0.45:
                    items.append({"unit": "rad", "pi_coeff": str(_sample_pi_coeff(rng) * rng.choice([1, 3, 5]))})
                else:
                    items.append({"unit": "deg", "degrees": _sample_degree(rng) * rng.choice([1, 2, 3])})
        parts: dict[str, str] = {}
        prompts: list[str] = []
        for idx, item in enumerate(items, start=1):
            unit = str(item.get("unit") or "deg").strip()
            if unit == "rad":
                coeff = _frac(item.get("pi_coeff") or item.get("coeff"))
                pos, neg = min_pos_max_neg_pi(coeff)
                parts[f"part_{idx}_pos"] = _pi_plain(pos)
                parts[f"part_{idx}_neg"] = _pi_plain(neg)
                prompts.append(f"({idx}) ${_pi_latex(coeff)}$")
            else:
                deg = _frac(item["degrees"])
                pos, neg = min_pos_max_neg_degrees(deg)
                parts[f"part_{idx}_pos"] = _deg_plain(pos)
                parts[f"part_{idx}_neg"] = _deg_plain(neg)
                prompts.append(f"({idx}) ${_deg_plain(deg)}^\\circ$")
        question = "試求下列各角的最小正同界角與最大負同界角：\n" + "\n".join(prompts)
        canonical = "；".join(f"{k}={v}" for k, v in parts.items())
        return {
            "givens": {"question_text": question, "variant": variant, "items": items},
            "answer": _answer_bundle(canonical, parts=parts, value=parts),
            "explanation_steps": [
                "度度量以 360° 為週期；弧度量以 2π 為週期。",
                "最小正同界角 ∈ (0, 360°] 或 (0, 2π]；最大負同界角 = 最小正同界角 − 一週期。",
            ],
        }

    # identify_which
    unit = str(constraints.get("unit") or "deg").strip()
    candidates = constraints.get("candidates")
    if unit == "rad":
        ref = _frac(constraints.get("pi_coeff") or _sample_pi_coeff(rng))
        if not isinstance(candidates, list) or len(candidates) < 3:
            k = rng.choice([1, 2, 3, 4, 5, 6, -1, -2])
            good = ref + 2 * k
            bad1 = ref + 1
            bad2 = -ref
            candidates = [bad1, good, bad2]
            rng.shuffle(candidates)
        hits = [i + 1 for i, c in enumerate(candidates) if is_coterminal_pi(ref, c)]
        ref_tex = _pi_latex(ref)
        cand_tex = " ".join(f"({i}) ${_pi_latex(_frac(c))}$" for i, c in enumerate(candidates, start=1))
    else:
        ref = _frac(constraints.get("degrees") or _sample_degree(rng))
        if not isinstance(candidates, list) or len(candidates) < 3:
            k = rng.choice([1, 2, 3, -1, -2])
            good = ref + 360 * k
            bad = ref + 120
            other = ref + 360 * k + 40
            candidates = [good, other, bad]
            rng.shuffle(candidates)
        hits = [i + 1 for i, c in enumerate(candidates) if is_coterminal_degrees(ref, c)]
        ref_tex = f"{_deg_plain(ref)}^\\circ"
        cand_tex = " ".join(
            f"({i}) ${_deg_plain(_frac(c))}^\\circ$" for i, c in enumerate(candidates, start=1)
        )
    hit_str = ",".join(str(i) for i in hits) if hits else ""
    question = f"下列何者與 ${ref_tex}$ 互為同界角？\n{cand_tex}"
    return {
        "givens": {
            "question_text": question,
            "variant": "identify_which",
            "unit": unit,
            "reference": str(ref),
            "candidates": [str(c) for c in candidates],
        },
        "answer": _answer_bundle(hit_str, value=hit_str),
        "explanation_steps": [
            "兩角為同界角若且唯若其差為 360° 或 2π 的整數倍。",
        ],
    }


def build_trigonometry_angle_matrix(
    *,
    seed: int | None,
    line_type: str | None = None,
    domain_operation: str | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a Full Matrix Dictionary for B2 1-1 angle operations."""
    op = str(domain_operation or line_type or "").strip()
    if op not in _SUPPORTED_OPS:
        raise ValueError(f"Unsupported trigonometry.angle operation: {op!r}")
    rng = random.Random(0 if seed is None else seed)
    constraints = dict(constraints or {})
    builders = {
        "convert_angle_measure": _build_convert,
        "sector_arc_and_area": _build_sector,
        "coterminal_angles": _build_coterminal,
    }
    built = builders[op](rng, constraints)
    return _matrix(
        op=op,
        givens=built["givens"],
        answer=built["answer"],
        explanation_steps=built.get("explanation_steps") or [],
        distractors=built.get("distractors") or [],
        visual_spec=built.get("visual_spec"),
        curriculum_profile=curriculum_profile,
        difficulty_profile=difficulty_profile,
    )
