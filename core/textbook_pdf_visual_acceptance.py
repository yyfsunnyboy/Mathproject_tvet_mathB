# -*- coding: utf-8 -*-
"""Deterministic PDF visual acceptance / confidence gate.

Asset existence is not sufficient evidence of visual correctness.
Low-confidence or structurally suspicious mappings must not be silently
treated as accepted student-ready assets.

Production rules are layout/ownership/boundary based — never example_id
or chapter hardcodes.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

VISUAL_STATUS_ACCEPTED = "accepted"
VISUAL_STATUS_NEEDS_REVIEW = "needs_review"
VISUAL_STATUS_REJECTED = "rejected"

REASON_CROSSES_QUESTION_BOUNDARY = "crosses_question_boundary"
REASON_SUSPICIOUS_SHARED_ASSET = "suspicious_shared_asset"
REASON_INCOMPLETE_MULTI_FIGURE = "incomplete_multi_figure"
REASON_NON_QUESTION_CONTAMINATION = "non_question_contamination"
REASON_LOW_MAPPING_CONFIDENCE = "low_mapping_confidence"
REASON_OVERSPAN_MULTI_QUESTION = "overspan_multi_question"

_MULTI_FIGURE_RE = re.compile(
    r"圖\s*[（(]\s*[一二三四五六七八九十1-9]\s*[）)]|"
    r"圖\s*[一二三四五六七八九十1-9]"
)
_CONTAMINATION_MARKERS = (
    "熟習度自評",
    "自我評量結果",
    "輸入訊息",
    "學習成果",
)
# Standalone solution marker often appears as a left-column 「解」 header.
_SOLUTION_HEADER_RE = re.compile(r"(?:^|[\s　])解(?:[\s　]|$)")


def normalize_stem_fingerprint(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or ""))
    t = re.sub(r"\\\((.*?)\\\)", r"\1", t, flags=re.DOTALL)
    t = re.sub(r"\\\[(.*?)\\\]", r"\1", t, flags=re.DOTALL)
    t = re.sub(r"\\[a-zA-Z]+\b", "", t)
    t = re.sub(r"[{}^_\\]", "", t)
    t = re.sub(r"\s+", "", t)
    return t[:180]


def detect_multi_figure_labels(problem_text: str) -> list[str]:
    labels = _MULTI_FIGURE_RE.findall(str(problem_text or ""))
    # Normalize for uniqueness: 圖（一） / 圖(一)
    out: list[str] = []
    seen: set[str] = set()
    for raw in labels:
        key = re.sub(r"\s+", "", unicodedata.normalize("NFKC", raw))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def bbox_area(bbox: list[float] | None) -> float:
    if not bbox or len(bbox) < 4:
        return 0.0
    return max(0.0, float(bbox[2] - bbox[0]) * float(bbox[3] - bbox[1]))


def bbox_iou(a: list[float] | None, b: list[float] | None) -> float:
    if not a or not b or len(a) < 4 or len(b) < 4:
        return 0.0
    x0 = max(float(a[0]), float(b[0]))
    y0 = max(float(a[1]), float(b[1]))
    x1 = min(float(a[2]), float(b[2]))
    y1 = min(float(a[3]), float(b[3]))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    union = bbox_area(a) + bbox_area(b) - inter
    return inter / union if union > 0 else 0.0


def clip_bbox_to_question_boundary(
    bbox: list[float],
    *,
    question_bbox: list[float] | None,
    next_question_y: float | None = None,
    safe_margin: float = 4.0,
) -> list[float]:
    """Guard A: clip only when the crop *materially* crosses the next question.

    Small overflows (labels) and diagrams that sit just below a short stem band
    must not be inverted/destroyed — that breaks legitimate 例/隨堂 shared figures.
    """
    out = [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])]
    if next_question_y is None:
        return out
    limit_y = float(next_question_y) - safe_margin
    if out[3] <= limit_y:
        return out
    height = max(1.0, out[3] - out[1])
    overflow = out[3] - limit_y
    # Material cross: large fraction of the crop lies below the next anchor.
    if overflow >= 0.35 * height and out[1] < limit_y:
        out[3] = limit_y
    return out


def search_band_bottom(
    question_bbox: list[float],
    *,
    page_height: float,
    next_question_y: float | None,
    footer_margin: float = 48.0,
    shared_look_ahead: float = 160.0,
) -> float:
    """Downward search stops at next question, with limited look-ahead for shared figures."""
    qb_bottom = float(question_bbox[3])
    if next_question_y is not None:
        # Allow a short look-ahead so 例/隨堂 shared diagrams just below the
        # stem boundary remain discoverable; material cross is gated later.
        return min(float(next_question_y) - 4.0 + shared_look_ahead, float(page_height) - footer_margin)
    return min(float(page_height) - footer_margin, qb_bottom)


def words_text_in_bbox(words: list[Any], bbox: list[float], *, pad: float = 2.0) -> str:
    """Concatenate PDF text-layer words overlapping bbox (no OCR)."""
    if not words or not bbox:
        return ""
    x0, y0, x1, y1 = [float(v) for v in bbox[:4]]
    x0 -= pad
    y0 -= pad
    x1 += pad
    y1 += pad
    parts: list[str] = []
    for w in words:
        # PyMuPDF words: (x0,y0,x1,y1, text, ...)
        if len(w) < 5:
            continue
        wx0, wy0, wx1, wy1 = float(w[0]), float(w[1]), float(w[2]), float(w[3])
        if wx1 < x0 or wx0 > x1 or wy1 < y0 or wy0 > y1:
            continue
        parts.append(str(w[4]))
    return "".join(parts)


def detect_contamination(text_in_crop: str) -> str | None:
    t = unicodedata.normalize("NFKC", str(text_in_crop or ""))
    for marker in _CONTAMINATION_MARKERS:
        if marker in t:
            return marker
    if "輸入" in t and "訊息" in t:
        return "輸入訊息"
    # Large crops that swallow a dedicated 解 block are suspicious.
    if "解" in t and ("答" in t or "：" in t or len(t) > 40):
        if _SOLUTION_HEADER_RE.search(t) or t.strip().startswith("解"):
            return "解"
    return None


def legitimate_shared_visual(
    row_a: dict[str, Any],
    row_b: dict[str, Any],
    *,
    min_iou: float = 0.85,
    min_stem_overlap: float = 0.72,
) -> bool:
    """True when two questions may legitimately share one visual (e.g. 例/隨堂 pair).

    Evidence required: near-identical crop AND near-identical figure stem.
    Same bbox / SHA alone is not enough.
    """
    ba = row_a.get("visual_bbox") or row_a.get("bbox")
    bb = row_b.get("visual_bbox") or row_b.get("bbox")
    if bbox_iou(ba, bb) < min_iou:
        return False
    page_a = row_a.get("visual_page") or (row_a.get("pdf_match") or {}).get("page")
    page_b = row_b.get("visual_page") or (row_b.get("pdf_match") or {}).get("page")
    if page_a is not None and page_b is not None and int(page_a) != int(page_b):
        return False
    fa = normalize_stem_fingerprint(str(row_a.get("problem_text") or ""))
    fb = normalize_stem_fingerprint(str(row_b.get("problem_text") or ""))
    if not fa or not fb:
        return False
    if fa == fb:
        return True
    # Prefix overlap for near-identical stems (例 N / 隨堂練習 N pairs).
    n = min(len(fa), len(fb), 120)
    if n < 24:
        return False
    same = sum(1 for i in range(n) if fa[i] == fb[i])
    return (same / n) >= min_stem_overlap


def evaluate_visual_acceptance(
    *,
    problem_text: str,
    visual_bbox: list[float] | None,
    question_bbox: list[float] | None,
    next_question_y: float | None,
    page_words: list[Any] | None,
    match_score: float | None,
    strong_cue: bool,
    page_height: float | None = None,
    question_start_y: float | None = None,
) -> dict[str, Any]:
    """Return visual_status + reasons for a candidate crop (pre-write gate)."""
    reasons: list[str] = []
    if not visual_bbox or len(visual_bbox) < 4:
        return {
            "visual_status": VISUAL_STATUS_REJECTED,
            "visual_review_reasons": [REASON_LOW_MAPPING_CONFIDENCE],
            "clipped_bbox": None,
        }

    clipped = clip_bbox_to_question_boundary(
        visual_bbox,
        question_bbox=question_bbox,
        next_question_y=next_question_y,
    )
    if clipped[3] <= clipped[1] + 8 or clipped[2] <= clipped[0] + 5:
        return {
            "visual_status": VISUAL_STATUS_NEEDS_REVIEW,
            "visual_review_reasons": [REASON_CROSSES_QUESTION_BOUNDARY],
            "clipped_bbox": clipped if clipped[2] > clipped[0] else visual_bbox,
        }

    vw = max(0.0, float(clipped[2] - clipped[0]))
    vh = max(0.0, float(clipped[3] - clipped[1]))
    # Degenerate strips after boundary clip are not usable diagrams.
    if vh < 40 or (vh > 0 and vw / vh > 12):
        reasons.append(REASON_LOW_MAPPING_CONFIDENCE)
    # Tiny right-panel slivers often clip critical vertex labels (F4 class).
    if strong_cue and (vw * vh) < 9000 and vw < 140:
        reasons.append(REASON_LOW_MAPPING_CONFIDENCE)
    # Wide left-anchored bars are usually multi-question frames, not the diagram.
    # Require tall or extreme-aspect evidence so legitimate full-width shared
    # figures (例/隨堂) are not auto-demoted.
    if question_bbox and vw > 0.70 * max(1.0, float(question_bbox[2] - question_bbox[0])):
        if float(clipped[0]) < float(question_bbox[0]) + 80 and (
            vh > 260 or (vh > 0 and vw / max(vh, 1.0) > 8)
        ):
            reasons.append(REASON_OVERSPAN_MULTI_QUESTION)

    # Guard A evidence: material overflow past next question.
    if next_question_y is not None and float(visual_bbox[3]) > float(next_question_y) + 8.0:
        overflow = float(visual_bbox[3]) - float(next_question_y)
        if overflow >= 0.35 * max(vh, 1.0):
            reasons.append(REASON_CROSSES_QUESTION_BOUNDARY)

    # Tall unmatched bands: crop sitting deep in the lower portion is often the
    # next figure on the page (no next-question anchor available).
    if (
        question_bbox
        and next_question_y is None
        and (float(question_bbox[3]) - float(question_bbox[1])) > 280
    ):
        cy = (float(clipped[1]) + float(clipped[3])) / 2.0
        stem = float(question_start_y) if question_start_y is not None else float(question_bbox[1])
        lower_gate = stem + 0.55 * (float(question_bbox[3]) - stem)
        if cy > lower_gate:
            reasons.append(REASON_LOW_MAPPING_CONFIDENCE)
    if question_bbox and len(question_bbox) >= 4:
        qh = max(1.0, float(question_bbox[3] - question_bbox[1]))
        if vh > 0.85 * qh and qh > 120:
            reasons.append(REASON_OVERSPAN_MULTI_QUESTION)

    labels = detect_multi_figure_labels(problem_text)
    if len(labels) >= 2:
        page_w_guess = float(question_bbox[2] - question_bbox[0]) if question_bbox else vw
        if vw < 0.55 * max(page_w_guess, vw) and vw < 280:
            reasons.append(REASON_INCOMPLETE_MULTI_FIGURE)

    if page_words:
        blob = words_text_in_bbox(page_words, clipped)
        hit = detect_contamination(blob)
        if hit:
            reasons.append(REASON_NON_QUESTION_CONTAMINATION)

    score = float(match_score or 0.0)
    if score < 0.75 and not strong_cue:
        reasons.append(REASON_LOW_MAPPING_CONFIDENCE)

    # Deduplicate while preserving order.
    deduped: list[str] = []
    for r in reasons:
        if r not in deduped:
            deduped.append(r)
    reasons = deduped

    if REASON_NON_QUESTION_CONTAMINATION in reasons:
        status = VISUAL_STATUS_REJECTED
    elif reasons:
        status = VISUAL_STATUS_NEEDS_REVIEW
    else:
        status = VISUAL_STATUS_ACCEPTED

    return {
        "visual_status": status,
        "visual_review_reasons": reasons,
        "clipped_bbox": clipped,
        "multi_figure_labels": labels,
    }


def _region_ownership_score(row: dict[str, Any]) -> float:
    """How well the crop sits inside this question's authoritative region."""
    vb = row.get("visual_bbox")
    qb = row.get("question_bbox")
    if not vb or not qb or len(vb) < 4 or len(qb) < 4:
        return 0.0
    inter = bbox_iou(
        vb,
        # Use a pseudo-IoU against the question band via intersection ratio on visual.
        [
            max(float(vb[0]), float(qb[0])),
            max(float(vb[1]), float(qb[1])),
            min(float(vb[2]), float(qb[2])),
            min(float(vb[3]), float(qb[3])),
        ],
    )
    # Prefer containment of visual center inside question band.
    cx = (float(vb[0]) + float(vb[2])) / 2.0
    cy = (float(vb[1]) + float(vb[3])) / 2.0
    inside = float(qb[0]) <= cx <= float(qb[2]) and float(qb[1]) <= cy <= float(qb[3])
    return (0.65 if inside else 0.0) + 0.35 * inter


def annotate_shared_asset_ownership(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Guard B/E: mark suspicious cross-question reuse; keep legitimate shares.

    Does not auto-FAIL every shared crop — 例/隨堂 identical-stem pairs remain allowed.
    When two different stems claim the same crop, demote the weaker owner only when
    region ownership is clearly asymmetric (protects rightful PASS neighbors).
    """
    claims: list[tuple[int, dict[str, Any]]] = []
    for i, row in enumerate(rows):
        if not row.get("visual_bbox"):
            continue
        if row.get("should_mount") or row.get("visual_status") in {
            VISUAL_STATUS_ACCEPTED,
            VISUAL_STATUS_NEEDS_REVIEW,
        }:
            claims.append((i, row))

    def _demote(row: dict[str, Any]) -> None:
        reasons = list(row.get("visual_review_reasons") or [])
        if REASON_SUSPICIOUS_SHARED_ASSET not in reasons:
            reasons.append(REASON_SUSPICIOUS_SHARED_ASSET)
        row["visual_review_reasons"] = reasons
        if row.get("visual_status") == VISUAL_STATUS_ACCEPTED:
            row["visual_status"] = VISUAL_STATUS_NEEDS_REVIEW
        row["needs_review"] = True
        row["should_mount"] = False
        row["visual_reason"] = (
            str(row.get("visual_reason") or "") + "|suspicious_shared_asset"
        ).strip("|")

    for a_i in range(len(claims)):
        i, row_a = claims[a_i]
        for b_i in range(a_i + 1, len(claims)):
            j, row_b = claims[b_i]
            page_a = row_a.get("visual_page")
            page_b = row_b.get("visual_page")
            if page_a is not None and page_b is not None and int(page_a) != int(page_b):
                continue
            same_box = bbox_iou(row_a.get("visual_bbox"), row_b.get("visual_bbox")) >= 0.92
            if legitimate_shared_visual(row_a, row_b) or (
                same_box
                and legitimate_shared_visual(
                    row_a, row_b, min_iou=0.50, min_stem_overlap=0.72
                )
            ):
                row_a.setdefault("shared_with", [])
                row_b.setdefault("shared_with", [])
                if row_b.get("id") not in row_a["shared_with"]:
                    row_a["shared_with"].append(row_b.get("id"))
                if row_a.get("id") not in row_b["shared_with"]:
                    row_b["shared_with"].append(row_a.get("id"))
                row_a["legitimate_shared_visual"] = True
                row_b["legitimate_shared_visual"] = True
                for row in (row_a, row_b):
                    drop = {
                        REASON_OVERSPAN_MULTI_QUESTION,
                        REASON_CROSSES_QUESTION_BOUNDARY,
                        REASON_SUSPICIOUS_SHARED_ASSET,
                    }
                    reasons = [
                        r
                        for r in (row.get("visual_review_reasons") or [])
                        if r not in drop
                    ]
                    row["visual_review_reasons"] = reasons
                    if row.get("visual_bbox") and not reasons:
                        row["visual_status"] = VISUAL_STATUS_ACCEPTED
                        row["should_mount"] = True
                        row["needs_review"] = False
                        if str(row.get("visual_classification")) == "skipped_low_confidence":
                            row["visual_classification"] = "required"
                continue
            if not same_box:
                continue
            if legitimate_shared_visual(row_a, row_b):
                continue
            own_a = _region_ownership_score(row_a)
            own_b = _region_ownership_score(row_b)
            if own_a >= own_b + 0.25:
                _demote(row_b)
            elif own_b >= own_a + 0.25:
                _demote(row_a)
            else:
                _demote(row_a)
                _demote(row_b)
    return rows


def student_asset_is_accepted(asset: dict[str, Any], *, notes: dict[str, Any] | None = None) -> bool:
    """Student-ready gate: existence alone is not enough."""
    if not isinstance(asset, dict):
        return False
    status = str(asset.get("visual_status") or "").strip().lower()
    if status in {VISUAL_STATUS_NEEDS_REVIEW, VISUAL_STATUS_REJECTED}:
        return False
    if asset.get("needs_crop_review") is True:
        return False
    if notes and notes.get("needs_image_review") is True and status == VISUAL_STATUS_NEEDS_REVIEW:
        return False
    # Legacy assets without visual_status remain accepted (backward compatible).
    return True
