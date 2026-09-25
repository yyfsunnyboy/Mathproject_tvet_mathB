# -*- coding: utf-8 -*-
"""Deterministic directed-segment vector drawing checker.

Activated only when answer metadata enables drawing_check (or equivalent).
Does not replace keyboard vector answers or legacy handwriting/AI paths.
"""

from __future__ import annotations

import math
import re
from typing import Any

_OVERRIGHTARROW = re.compile(
    r"(?:\\overrightarrow|overrightarrow)\s*\{([A-Za-z])([A-Za-z])\}",
    re.IGNORECASE,
)
_BARE_SEG = re.compile(r"^([A-Za-z])([A-Za-z])$")


def drawing_check_enabled(
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Semantic gate: only explicit drawing_check / directed_segment_drawing."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    dc = ac.get("drawing_check") if isinstance(ac.get("drawing_check"), dict) else {}
    if not dc:
        dc = pl.get("drawing_check") if isinstance(pl.get("drawing_check"), dict) else {}
    if dc.get("enabled") is True:
        return True
    shape = str(ac.get("answer_shape") or pl.get("answer_shape") or "").strip().lower()
    return shape in {"directed_segment_drawing", "vector_drawing"}


def parse_directed_segment_endpoints(expected: object) -> tuple[str, str] | None:
    """Return (from_label, to_label) for a directed-segment oracle."""
    text = str(expected or "").replace("$", "").replace(" ", "")
    if not text:
        return None
    match = _OVERRIGHTARROW.search(text)
    if match:
        return match.group(1).upper(), match.group(2).upper()
    bare = _BARE_SEG.fullmatch(text)
    if bare and text.isupper():
        return bare.group(1).upper(), bare.group(2).upper()
    return None


def resolve_expected_endpoints(
    *,
    expected_answer: object = None,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> tuple[str, str] | None:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    dc = ac.get("drawing_check") if isinstance(ac.get("drawing_check"), dict) else {}
    if not dc:
        dc = pl.get("drawing_check") if isinstance(pl.get("drawing_check"), dict) else {}
    from_label = str(dc.get("expected_from") or "").strip().upper()
    to_label = str(dc.get("expected_to") or "").strip().upper()
    if len(from_label) == 1 and len(to_label) == 1:
        return from_label, to_label
    for candidate in (
        expected_answer,
        ac.get("expected_answer"),
        ac.get("semantic_answer"),
        ac.get("canonical_answer"),
        pl.get("correct_answer"),
        pl.get("answer"),
    ):
        parsed = parse_directed_segment_endpoints(candidate)
        if parsed:
            return parsed
    return None


def _dist(a: dict[str, float], b: dict[str, float]) -> float:
    return math.hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"]))


def _as_point(raw: Any) -> dict[str, float] | None:
    if not isinstance(raw, dict):
        return None
    try:
        x = float(raw.get("x"))
        y = float(raw.get("y"))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x) or not math.isfinite(y):
        return None
    return {"x": x, "y": y}


def _stroke_endpoints(stroke: dict[str, Any]) -> tuple[dict[str, float], dict[str, float]] | None:
    points = stroke.get("points") if isinstance(stroke, dict) else None
    if not isinstance(points, list) or len(points) < 2:
        start = _as_point(stroke.get("start") if isinstance(stroke, dict) else None)
        end = _as_point(stroke.get("end") if isinstance(stroke, dict) else None)
        if start and end:
            return start, end
        return None
    start = _as_point(points[0])
    end = _as_point(points[-1])
    if not start or not end:
        return None
    return start, end


def _stroke_length(stroke: dict[str, Any]) -> float:
    ends = _stroke_endpoints(stroke)
    if not ends:
        return 0.0
    return _dist(ends[0], ends[1])


def _default_tolerance(
    *,
    canvas_size: dict[str, Any] | None,
    labeled_points: dict[str, dict[str, float]],
) -> float:
    cw = float((canvas_size or {}).get("width") or 0) or 300.0
    ch = float((canvas_size or {}).get("height") or 0) or 200.0
    base = 0.08 * min(cw, ch)
    # Scale with typical point separation when available.
    coords = list(labeled_points.values())
    if len(coords) >= 2:
        spreads = []
        for i, p in enumerate(coords):
            for q in coords[i + 1 :]:
                spreads.append(_dist(p, q))
        if spreads:
            base = max(base, 0.18 * (sum(spreads) / len(spreads)))
    return max(18.0, min(base, 64.0))


def _nearest_label(
    point: dict[str, float],
    labeled_points: dict[str, dict[str, float]],
    *,
    tolerance: float,
) -> tuple[str | None, float]:
    best_label = None
    best_dist = float("inf")
    for label, pos in labeled_points.items():
        d = _dist(point, pos)
        if d < best_dist:
            best_dist = d
            best_label = label
    if best_label is None or best_dist > tolerance:
        return None, best_dist
    return best_label, best_dist


def _feedback_for(
    status: str,
    *,
    expected_from: str,
    expected_to: str,
    detected_from: str | None = None,
    detected_to: str | None = None,
) -> str:
    if status == "correct":
        return f"作圖正確：你畫的是從 {expected_from} 指向 {expected_to} 的向量。"
    if status == "fail_direction":
        return f"方向相反。請確認箭頭應由 {expected_from} 指向 {expected_to}。"
    if status == "fail_endpoint":
        if detected_from == expected_from and detected_to and detected_to != expected_to:
            return f"終點應在 {expected_to}。"
        if detected_to == expected_to and detected_from and detected_from != expected_from:
            return f"起點應在 {expected_from}。"
        return f"終點應在 {expected_to}。"
    if status == "uncertain":
        return "目前無法清楚判斷箭頭方向，請再畫一次。"
    return f"請畫出由 {expected_from} 指向 {expected_to} 的向量。"


def check_vector_drawing_answer(
    *,
    student_strokes: list[Any] | None,
    labeled_point_canvas_positions: dict[str, Any] | None,
    expected_answer: object = None,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    canvas_css_size: dict[str, Any] | None = None,
    tolerance: float | None = None,
) -> dict[str, Any]:
    """Grade a directed-segment drawing against labeled visual points (canvas CSS space)."""
    endpoints = resolve_expected_endpoints(
        expected_answer=expected_answer,
        answer_contract=answer_contract,
        payload=payload,
    )
    out: dict[str, Any] = {
        "status": "uncertain",
        "correct": None,
        "expected_from": None,
        "expected_to": None,
        "detected_from": None,
        "detected_to": None,
        "confidence": 0.0,
        "reason": "missing_expected_segment",
        "result": "目前無法清楚判斷箭頭方向，請再畫一次。",
        "checker": "vector_drawing_checker",
    }
    if not endpoints:
        return out
    expected_from, expected_to = endpoints
    out["expected_from"] = expected_from
    out["expected_to"] = expected_to

    labeled: dict[str, dict[str, float]] = {}
    for key, value in (labeled_point_canvas_positions or {}).items():
        pt = _as_point(value)
        label = str(key or "").strip().upper()
        if pt and label:
            labeled[label] = pt
    if expected_from not in labeled or expected_to not in labeled:
        out["reason"] = "missing_labeled_geometry"
        out["result"] = _feedback_for("uncertain", expected_from=expected_from, expected_to=expected_to)
        return out

    strokes = [s for s in (student_strokes or []) if isinstance(s, dict)]
    # Drop tiny accidental marks.
    tol = float(tolerance) if tolerance is not None else _default_tolerance(
        canvas_size=canvas_css_size, labeled_points=labeled
    )
    min_len = max(8.0, 0.35 * tol)
    candidates = []
    for stroke in strokes:
        if stroke.get("erasing") is True:
            continue
        length = _stroke_length(stroke)
        if length < min_len:
            continue
        ends = _stroke_endpoints(stroke)
        if not ends:
            continue
        start, end = ends
        start_label, start_d = _nearest_label(start, labeled, tolerance=tol)
        end_label, end_d = _nearest_label(end, labeled, tolerance=tol)
        candidates.append(
            {
                "stroke": stroke,
                "length": length,
                "start_label": start_label,
                "end_label": end_label,
                "start_d": start_d,
                "end_d": end_d,
            }
        )

    if not candidates:
        out["reason"] = "no_usable_stroke"
        out["result"] = _feedback_for("incorrect", expected_from=expected_from, expected_to=expected_to)
        out["status"] = "incorrect"
        out["correct"] = False
        out["confidence"] = 0.55
        return out

    # Prefer longest stroke as dominant intent.
    candidates.sort(key=lambda row: row["length"], reverse=True)
    dominant = candidates[0]
    contradictory = []
    for row in candidates[1:]:
        if not row["start_label"] or not row["end_label"]:
            continue
        if (row["start_label"], row["end_label"]) == (dominant["start_label"], dominant["end_label"]):
            continue
        if row["length"] >= 0.7 * dominant["length"]:
            contradictory.append(row)
    if contradictory:
        out["status"] = "uncertain"
        out["correct"] = None
        out["confidence"] = 0.35
        out["reason"] = "conflicting_strokes"
        out["detected_from"] = dominant["start_label"]
        out["detected_to"] = dominant["end_label"]
        out["result"] = _feedback_for("uncertain", expected_from=expected_from, expected_to=expected_to)
        return out

    detected_from = dominant["start_label"]
    detected_to = dominant["end_label"]
    out["detected_from"] = detected_from
    out["detected_to"] = detected_to

    if detected_from == expected_from and detected_to == expected_to:
        out["status"] = "correct"
        out["correct"] = True
        out["confidence"] = 0.95
        out["reason"] = "directed_segment_match"
        out["result"] = _feedback_for("correct", expected_from=expected_from, expected_to=expected_to)
        return out

    if detected_from == expected_to and detected_to == expected_from:
        out["status"] = "incorrect"
        out["correct"] = False
        out["confidence"] = 0.92
        out["reason"] = "fail_direction"
        out["result"] = _feedback_for(
            "fail_direction",
            expected_from=expected_from,
            expected_to=expected_to,
            detected_from=detected_from,
            detected_to=detected_to,
        )
        return out

    if detected_from and detected_to:
        out["status"] = "incorrect"
        out["correct"] = False
        out["confidence"] = 0.88
        out["reason"] = "fail_endpoint"
        out["result"] = _feedback_for(
            "fail_endpoint",
            expected_from=expected_from,
            expected_to=expected_to,
            detected_from=detected_from,
            detected_to=detected_to,
        )
        return out

    out["status"] = "uncertain"
    out["correct"] = None
    out["confidence"] = 0.4
    out["reason"] = "endpoints_not_near_labels"
    out["result"] = _feedback_for("uncertain", expected_from=expected_from, expected_to=expected_to)
    return out
