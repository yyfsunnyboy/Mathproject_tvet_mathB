# -*- coding: utf-8 -*-
"""Stage 1 source-fidelity gate for imported textbook rows.

"Import complete" only says rows were written.  ``Stage 1 READY`` says the written rows are a trustworthy
source for Gencode V3 (SOP_Gencode_V3_Lean §2.2-§2.3, Specification §10.4 / §10.6.1):

* BLOCKED       - a key figure is missing, the stem is incomplete, or math symbols are corrupted;
* NEEDS_REVIEW  - something is present but a human has not confirmed it (low-confidence or uncertain visual,
                  confidence-based review flags, damaged solution text);
* READY         - none of the above.

Pure functions over row-like objects (``notes`` JSON, ``problem_text``, ``detailed_solution``,
``problem_type``, ``source_description``, ``id``); no database access and no writes.
"""
from __future__ import annotations

import json
import re
from typing import Any

STATUS_READY = "READY"
STATUS_NEEDS_REVIEW = "NEEDS_REVIEW"
STATUS_BLOCKED = "BLOCKED"

_TERMINAL = ("。", "？", "！", "）", "」", ")", "?", "…", "\\)", "\\]", "$", "|")
_FIGURE_LEAD_IN_RE = re.compile(r"(如下圖所示|如右圖所示|如圖所示|依序數數字|右圖的方式)[：。:]?\s*$")
_STRONG_FIGURE_RE = re.compile(r"如圖|下圖|上圖|右圖|左圖|圖中|附圖|如下圖|如上圖")
_SUB_RE = re.compile(r"(?:^|(?<=[\s。，；：！？]))[\(（]\s*(\d{1,2})\s*[\)）]", re.M)
_LOST_SYMBOL_RE = re.compile(r"[A-Za-z0-9\)]\s{2,}[A-Za-z0-9]")
_CORRUPT_MARKERS = ("MATH_PARSE_FAILED", "[FORMULA_MISSING]", "[FORMULA_IMAGE_", "[MATH")
_PROOF_CLAIM_RE = re.compile(r"恆|成立|倍數|整除|相等|等於|為真|不等式")


def _notes(row: Any) -> dict[str, Any]:
    raw = row.get("notes") if isinstance(row, dict) else getattr(row, "notes", None)
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(raw or "{}")
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _field(row: Any, name: str) -> str:
    value = row.get(name) if isinstance(row, dict) else getattr(row, name, "")
    return str(value or "")


def _strip_math(text: str) -> str:
    return re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", "", text, flags=re.S)


def stem_completeness_issues(problem_text: str, problem_type: str = "") -> list[str]:
    """Structural signs that a stem was cut short.  Language-structure only; never compares to a book."""
    text = str(problem_text or "").strip()
    if not text:
        return ["stem_empty"]
    issues: list[str] = []
    if not text.endswith(_TERMINAL):
        issues.append("stem_without_terminal_punctuation")
    subs = [int(n) for n in _SUB_RE.findall(_strip_math(text))]
    if subs and subs != list(range(1, len(subs) + 1)):
        issues.append("sub_question_numbering_gap")
    if _FIGURE_LEAD_IN_RE.search(text) and not subs and "求" not in text:
        issues.append("stem_ends_at_figure_lead_in")
    if "證明" in text:
        tail = _strip_math(text.split("證明", 1)[1])
        if text.endswith(("\\)", "\\]")) and not _PROOF_CLAIM_RE.search(tail):
            issues.append("proof_stem_without_claim")
    return issues


def math_fidelity_issues(text: str) -> list[str]:
    value = str(text or "")
    issues: list[str] = []
    if any(m in value for m in _CORRUPT_MARKERS):
        issues.append("math_parse_marker")
    if value.count("\\(") != value.count("\\)") or value.count("\\[") != value.count("\\]"):
        issues.append("unbalanced_math_delimiters")
    if _LOST_SYMBOL_RE.search(value):
        issues.append("lost_symbol_gap")
    return issues


def evaluate_row(row: Any) -> dict[str, list[str]]:
    notes = _notes(row)
    stem = _field(row, "problem_text")
    solution = _field(row, "detailed_solution")
    blockers: list[str] = []
    reviews: list[str] = []

    blockers.extend(stem_completeness_issues(stem, _field(row, "problem_type")))
    blockers.extend(f"stem_{i}" for i in math_fidelity_issues(stem))
    reviews.extend(f"solution_{i}" for i in math_fidelity_issues(solution))

    assets = [a for a in (notes.get("image_assets") or []) if isinstance(a, dict) and a.get("path")]
    accepted = [a for a in assets if str(a.get("visual_status") or "accepted").lower() == "accepted" and not a.get("needs_crop_review")]
    needs_figure = bool(_STRONG_FIGURE_RE.search(stem)) and notes.get("pdf_visual_status") != "NO_VISUAL_REQUIRED"
    if notes.get("visual_required_missing") or notes.get("pdf_visual_status") == "VISUAL_REQUIRED_MISSING" \
            or (needs_figure and not assets):
        blockers.append("required_figure_missing")
    elif assets and not accepted:
        reviews.append("visual_uncertain")
    elif needs_figure and len(accepted) < len(assets):
        reviews.append("visual_partially_uncertain")
    if notes.get("needs_image_review"):
        reviews.append("image_review_flag")
    if notes.get("needs_review") and not blockers:
        reviews.append("needs_review_flag")
    if notes.get("review_required_by_confidence") and not (notes.get("manual_stem_review") or notes.get("manual_visual_review")):
        reviews.append("low_import_confidence")
    return {"blockers": list(dict.fromkeys(blockers)), "reviews": list(dict.fromkeys(reviews))}


def evaluate_stage1_gate(rows: list[Any]) -> dict[str, Any]:
    """Aggregate gate for one import scope.  ``import_complete`` is always separate from ``stage1_ready``."""
    blocked, review, reasons = [], [], {}
    for row in rows or []:
        verdict = evaluate_row(row)
        rid = row.get("id") if isinstance(row, dict) else getattr(row, "id", None)
        label = re.sub(r"\s*\[[^\]]*\]\s*$", "", _field(row, "source_description"))
        for r in verdict["blockers"] + verdict["reviews"]:
            reasons[r] = reasons.get(r, 0) + 1
        if verdict["blockers"]:
            blocked.append({"id": rid, "label": label, "reasons": verdict["blockers"] + verdict["reviews"]})
        elif verdict["reviews"]:
            review.append({"id": rid, "label": label, "reasons": verdict["reviews"]})
    status = STATUS_BLOCKED if blocked else STATUS_NEEDS_REVIEW if review else STATUS_READY
    return {
        "import_complete": True,
        "stage1_ready": status == STATUS_READY,
        "status": status,
        "rows": len(rows or []),
        "blocked": blocked,
        "needs_review": review,
        "reasons": reasons,
    }


def format_gate_log_line(gate: dict[str, Any]) -> str:
    return (f"[STAGE1 GATE] status={gate['status']} rows={gate['rows']} blocked={len(gate['blocked'])} "
            f"needs_review={len(gate['needs_review'])} reasons={json.dumps(gate['reasons'], ensure_ascii=False, sort_keys=True)}")
