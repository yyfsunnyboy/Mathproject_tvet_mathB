# -*- coding: utf-8 -*-
"""Seed-driven practice variants for B2 §1-2 acute-trig components.

Textbook SPECs remain the pedagogical template.  For student practice, different
seeds must produce meaningful parameter changes while preserving the same
solution structure, answer contract shape, and Canvas-local diagram (no stem
figure relocation).  PDF crops with baked-in numbers are not reused when the
sampled parameters differ from the textbook instance.
"""

from __future__ import annotations

import math
import random
from copy import deepcopy
from typing import Any

from core.gencode.b2_12_component_specs import (
    CONSTRAINT,
    PROJECTION,
    RIGHT,
    SIMPLIFY,
)

# Textbook 進階題10 (TE 11584) canonical instance.
_CABLE_TEXTBOOK = (900, 45, 500)

_CABLE_LENGTHS = (200, 300, 400, 500, 600, 800, 900, 1000, 1200)
_CABLE_ANGLES = (30, 45, 60)
_CABLE_ELEVATIONS = (0, 100, 200, 300, 400, 500, 600, 800, 1000)

_RIGHT_TRIPLES = (
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
    (9, 12, 15),
    (20, 21, 29),
)

_CONSTRAINT_POOL = (
    {"known": {"tan": "3/4"}, "targets": {"sin": "sin_theta", "cos": "cos_theta"},
     "question": "已知 θ 為銳角且 tan θ=3/4，求 sin θ 與 cos θ。"},
    {"known": {"tan": "5/12"}, "targets": {"sin": "sin_theta", "cos": "cos_theta"},
     "question": "已知 θ 為銳角且 tan θ=5/12，求 sin θ 與 cos θ。"},
    {"known": {"cos": "12/13"}, "targets": {"sin": "sin_theta", "tan": "tan_theta"},
     "question": "已知 θ 為銳角且 cosθ=12/13，求 sinθ 與 tanθ。"},
    {"known": {"sin": "8/17"}, "targets": {"cos": "cos_theta", "tan": "tan_theta"},
     "question": "已知 θ 為銳角且 sinθ=8/17，求 cosθ 與 tanθ。"},
    {"known": {"sin": "7/25"}, "targets": {"cos": "cos_theta", "tan": "tan_theta"},
     "question": "已知 θ 為銳角且 sinθ=7/25，求 cosθ 與 tanθ。"},
)

_SIMPLIFY_POOL = (
    {"expressions": {"value": "(sin_theta+cos_theta)**2+(sin_theta-cos_theta)**2"},
     "question": "θ 為銳角，求 (sinθ+cosθ)²+(sinθ−cosθ)²。"},
    {"expressions": {"value": "sin_theta**2+cos_theta**2"},
     "question": "θ 為銳角，求 sin²θ+cos²θ。"},
    {"expressions": {"value": "(1-sin_theta)*(1+sin_theta)"},
     "question": "θ 為銳角，求 (1−sinθ)(1+sinθ)。"},
    {"expressions": {"value": "tan_theta*cos_theta"},
     "question": "θ 為銳角，求 tanθ·cosθ。"},
    {"expressions": {"value": "sin_theta/cos_theta"},
     "question": "θ 為銳角，求 sinθ/cosθ。"},
)


def _rng(seed: int | None) -> random.Random:
    return random.Random(0 if seed is None else int(seed))


def sample_cable_projection_params(seed: int | None) -> tuple[int, int, int]:
    """Return (L, theta_deg, base_elevation).  seed=0 keeps textbook 900/45/500."""
    if seed is None or int(seed) == 0:
        return _CABLE_TEXTBOOK
    rng = _rng(seed)
    for _ in range(40):
        params = (
            int(rng.choice(_CABLE_LENGTHS)),
            int(rng.choice(_CABLE_ANGLES)),
            int(rng.choice(_CABLE_ELEVATIONS)),
        )
        if params != _CABLE_TEXTBOOK:
            return params
    return (600, 30, 200)


def build_cable_projection_question(length: int, angle: int, base_elevation: int) -> str:
    return (
        f"纜車站 A 到山頂站 B 距離 {length} 公尺、仰角 {angle}°，"
        f"A 站海拔 {base_elevation} 公尺；求 B 站海拔與兩站水平距離。"
    )


def build_cable_projection_visual_spec(length: int, angle: int, base_elevation: int) -> dict[str, Any]:
    """Drawable right-triangle figure for Canvas; labels match stem parameters."""
    rad = math.radians(float(angle))
    # Display units: hypotenuse length 6 for readable proportions.
    hyp = 6.0
    adj = hyp * math.cos(rad)
    opp = hyp * math.sin(rad)
    # Place A above a ground reference so altitude label has room.
    ground = 0.0
    base_y = max(1.8, min(4.5, 1.5 + (base_elevation / 1000.0) * 2.5))
    ax, ay = 0.0, base_y
    cx, cy = adj, base_y
    bx, by = adj, base_y + opp
    return {
        "kind": "coordinate_plane",
        "required": True,
        "show_axes": False,
        "show_grid": False,
        "points": [
            {"id": "G0", "x": ax - 0.4, "y": ground, "label": ""},
            {"id": "G1", "x": cx + 0.6, "y": ground, "label": ""},
            {"id": "F", "x": ax, "y": ground, "label": ""},
            {"id": "A", "x": ax, "y": ay, "label": "A"},
            {"id": "C", "x": cx, "y": cy, "label": "C"},
            {"id": "B", "x": bx, "y": by, "label": "B"},
            {"id": "Ang", "x": ax + adj * 0.22, "y": ay + opp * 0.12, "label": f"{angle}°"},
        ],
        "lines": [
            {"through_points": ["G0", "G1"], "extend": False, "label": "", "style": "dashed"},
            {"through_points": ["A", "F"], "extend": False, "label": f"{base_elevation} 公尺"},
            {"through_points": ["A", "B"], "extend": False, "label": f"{length} 公尺"},
            {"through_points": ["A", "C"], "extend": False, "label": ""},
            {"through_points": ["C", "B"], "extend": False, "label": ""},
        ],
        "right_angle_marks": [{"at": [cx, cy], "axes": "x", "size": max(0.25, min(0.45, adj * 0.12))}],
        "alt": f"纜車直角三角形：斜距 {length} 公尺、仰角 {angle}°、A 站海拔 {base_elevation} 公尺",
    }


def _variant_right_triangle(seed: int | None, question: str, calls: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], None, None]:
    rng = _rng(seed)
    opp, adj, hyp = rng.choice(_RIGHT_TRIPLES)
    # Angle A at A: opposite BC=opp, adjacent AC=adj, hypotenuse AB=hyp.
    new_q = f"直角三角形 ABC 中，∠C=90°、AB={hyp}、BC={opp}，求 sin A、cos A、tan A。"
    new_calls = deepcopy(calls)
    new_calls[0]["constraints"] = {"opposite": opp, "adjacent": adj, "hypotenuse": hyp}
    return new_q, new_calls, None, None


def _variant_constraint(seed: int | None, question: str, calls: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], None, None]:
    rng = _rng(seed)
    # Only rewrite single-known / sin-cos target shapes; leave complex multi-relation SPECs alone.
    call0 = calls[0] if calls else {}
    constraints = dict(call0.get("constraints") or {})
    if constraints.get("relations") or constraints.get("choice_options"):
        return question, calls, None, None
    known = constraints.get("known") or {}
    if not isinstance(known, dict) or len(known) != 1:
        return question, calls, None, None
    pick = rng.choice(_CONSTRAINT_POOL)
    new_calls = deepcopy(calls)
    new_calls[0]["constraints"] = {"known": dict(pick["known"]), "targets": dict(pick["targets"])}
    return str(pick["question"]), new_calls, None, None


def _variant_simplify(seed: int | None, question: str, calls: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], None, None]:
    rng = _rng(seed)
    call0 = calls[0] if calls else {}
    expressions = (call0.get("constraints") or {}).get("expressions")
    if not isinstance(expressions, dict) or len(expressions) != 1:
        return question, calls, None, None
    pick = rng.choice(_SIMPLIFY_POOL)
    new_calls = deepcopy(calls)
    new_calls[0]["constraints"] = {"expressions": dict(pick["expressions"])}
    return str(pick["question"]), new_calls, None, None


def _variant_projection_cable(
    seed: int | None, question: str, calls: list[dict[str, Any]]
) -> tuple[str, list[dict[str, Any]], str | None, dict[str, Any] | None]:
    call0 = calls[0] if calls else {}
    constraints = dict(call0.get("constraints") or {})
    # Cable / elevation multipart only.
    if constraints.get("base_elevation") is None:
        return question, calls, None, None
    if "elevation" not in list(constraints.get("requested") or []):
        return question, calls, None, None
    length, angle, base = sample_cable_projection_params(seed)
    new_q = build_cable_projection_question(length, angle, base)
    new_calls = deepcopy(calls)
    new_calls[0]["constraints"] = {
        **constraints,
        "hypotenuse": length,
        "angle": angle,
        "base_elevation": base,
        "requested": ["elevation", "horizontal_projection"],
        "length_unit": "m",
    }
    visual = build_cable_projection_visual_spec(length, angle, base)
    # Never attach the fixed PDF crop when parameters may differ from printed numbers.
    return new_q, new_calls, None, visual


def apply_b2_12_practice_variants(
    *,
    domain_operation: str,
    question_text: str,
    calls: list[dict[str, Any]],
    seed: int | None,
    visual_asset: str = "",
    textbook_example_id: int | None = None,
) -> dict[str, Any]:
    """Return possibly rewritten question/calls/visual for practice variation.

    Keys: question_text, calls, visual_asset, visual_spec (optional override).
    """
    op = str(domain_operation or "").strip()
    out = {
        "question_text": question_text,
        "calls": deepcopy(calls),
        "visual_asset": visual_asset,
        "visual_spec": None,
    }
    if not calls:
        return out

    if op == PROJECTION and int(textbook_example_id or 0) == 11584:
        q, c, asset, vs = _variant_projection_cable(seed, question_text, calls)
        out.update({"question_text": q, "calls": c, "visual_asset": asset or "", "visual_spec": vs})
        return out

    if op == RIGHT and int(textbook_example_id or 0) in {11557, 11567, 11576}:
        q, c, _, _ = _variant_right_triangle(seed, question_text, calls)
        out.update({"question_text": q, "calls": c})
        return out

    if op == CONSTRAINT and int(textbook_example_id or 0) in {11558, 11568}:
        q, c, _, _ = _variant_constraint(seed, question_text, calls)
        out.update({"question_text": q, "calls": c})
        return out

    if op == SIMPLIFY and int(textbook_example_id or 0) == 11581:
        q, c, _, _ = _variant_simplify(seed, question_text, calls)
        out.update({"question_text": q, "calls": c})
        return out

    return out
