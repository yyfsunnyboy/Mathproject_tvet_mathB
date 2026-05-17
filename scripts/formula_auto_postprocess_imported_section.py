#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auto postprocess formula placeholders for imported textbook section.

Safe defaults:
- dry-run by default
- only replace placeholders
- never modify answer/solution fields
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLACEHOLDER_RE = re.compile(r"\[FORMULA_IMAGE_(\d+)\]|\[FORMULA_MISSING\]")
VECTOR_FORMATS = {"wmf", "emf"}
READABLE_FORMATS = {"png", "jpg", "jpeg"}
MATH_HINT_RE = re.compile(r"[<>=≤≥\|\(\)\[\]\{\}xXyY÷\+\-\*/\^_]")
NOISE_ONLY_RE = re.compile(r"^[\W_]+$")


def normalize_title(raw: str) -> str:
    text = str(raw or "").strip()
    text = re.sub(r"\s*\[source_type=.*$", "", text)
    compact = re.sub(r"\s+", "", text)
    m = re.match(r"^例題?(\d+)$", compact)
    if m:
        return f"例題{int(m.group(1))}"
    m = re.match(r"^隨堂練習(\d+)$", compact)
    if m:
        return f"隨堂練習{int(m.group(1))}"
    m = re.match(r"^((?:\d+-\d+)?)習題基礎題(\d+)$", compact)
    if m:
        return f"{m.group(1)}習題基礎題{int(m.group(2))}"
    return compact.lower()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_meta(notes: str) -> dict[str, Any]:
    if not str(notes or "").strip():
        return {}
    try:
        obj = json.loads(notes)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def dump_meta(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


def pick_asset_path(asset: dict[str, Any], root: Path) -> tuple[str | None, str | None]:
    for key in ("converted_path", "display_path", "path", "original_path"):
        rel = str(asset.get(key) or "").strip()
        if not rel:
            continue
        ext = os.path.splitext(rel)[1].lower().lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        if ext in READABLE_FORMATS:
            abs_path = Path(rel) if os.path.isabs(rel) else (root / rel)
            if abs_path.exists():
                return str(abs_path), rel.replace("\\", "/")
    return None, None


def try_convert_vector(asset: dict[str, Any], root: Path) -> tuple[bool, str, str]:
    rel = str(asset.get("path") or asset.get("original_path") or "").strip()
    if not rel:
        return False, "", "missing_vector_source"
    src = Path(rel) if os.path.isabs(rel) else (root / rel)
    if not src.exists():
        return False, "", f"source_not_found:{src.as_posix()}"
    ext = os.path.splitext(str(src))[1].lower().lstrip(".")
    if ext not in VECTOR_FORMATS:
        return False, "", "not_vector_format"
    dst_dir = root / "uploads" / "tmp_formula_asset_conversion"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"post_{src.stem}_{abs(hash(str(src))) % 999999}.png"
    try:
        sys.path.insert(0, str(project_root()))
        from core.question_image_assets import convert_vector_image_to_png  # pylint: disable=import-outside-toplevel

        ok, err = convert_vector_image_to_png(str(src), str(dst))
        if ok and dst.exists():
            return True, str(dst.relative_to(root).as_posix()), ""
        return False, "", str(err or "conversion_failed")
    except Exception as exc:
        return False, "", str(exc)


def ocr_local(abs_path: str) -> tuple[str, float, str]:
    try:
        import pytesseract  # pylint: disable=import-outside-toplevel
        from PIL import Image  # pylint: disable=import-outside-toplevel

        with Image.open(abs_path) as img:
            text = str(pytesseract.image_to_string(img, lang="chi_tra+eng") or "").strip()
        if not text:
            return "", 0.0, "local_ocr_empty"
        return text, 0.88, "local_ocr"
    except Exception as exc:
        return "", 0.0, f"local_ocr_failed:{exc}"


def ocr_gemini(abs_path: str) -> tuple[str, float, str]:
    try:
        from PIL import Image  # pylint: disable=import-outside-toplevel
        sys.path.insert(0, str(project_root()))
        from core.ai_analyzer import get_model  # pylint: disable=import-outside-toplevel

        model = get_model("vision_analyzer")
        with Image.open(abs_path) as img:
            resp = model.generate_content(
                [
                    "Transcribe the formula only. Return plain formula text, no explanation.",
                    img,
                ],
                generation_config={"temperature": 0.0, "max_output_tokens": 256},
            )
        text = str(getattr(resp, "text", "") or "").strip()
        if not text or text == "[UNREADABLE_FORMULA]":
            return "", 0.0, "gemini_unreadable"
        return text, 0.92, "gemini_vision"
    except Exception as exc:
        return "", 0.0, f"gemini_failed:{exc}"


def replace_placeholders(problem_text: str, replacements: dict[str, str]) -> tuple[str, bool]:
    updated = str(problem_text or "")
    changed = False
    for token, latex in replacements.items():
        if token in updated and latex:
            updated = updated.replace(token, latex)
            changed = True
    return updated, changed


def clean_candidate_text(text: str) -> str:
    t = str(text or "").strip()
    t = re.sub(r"\s+", " ", t)
    return t


def candidate_reject_reason(text: str) -> str:
    t = clean_candidate_text(text)
    if not t:
        return "empty"
    if NOISE_ONLY_RE.match(t):
        return "noise_only"
    if re.fullmatch(r"\d+", t):
        return "single_number"
    if re.search(r"(圖|表)\s*\d+", t):
        return "diagram_label"
    if re.fullmatch(r"[A-Za-z]\(\d+\)", t):
        return "label_like"
    if re.search(r"(得|故|解為|所以|答案|區間)", t):
        return "solution_like"
    if not MATH_HINT_RE.search(t):
        return "non_formula_text"
    if len(t) <= 2 and not MATH_HINT_RE.search(t):
        return "too_short"
    return ""


def candidate_features(text: str) -> dict[str, bool]:
    t = clean_candidate_text(text)
    return {
        "formula_like": bool(MATH_HINT_RE.search(t)),
        "contains_comparator": bool(re.search(r"[<>=≤≥]", t)),
        "solution_like": bool(re.search(r"(得|故|解為|所以|答案|區間)", t)),
        "label_like": bool(re.search(r"(圖|表)\s*\d+", t)),
    }


def placeholder_mode(problem_text: str, token: str) -> str:
    text = str(problem_text or "")
    idx = text.find(token)
    if idx < 0:
        return "unknown"
    window = text[max(0, idx - 20) : idx + len(token) + 20]
    # token already wrapped by inequality context => should prefer expression core (e.g. |x|)
    if re.search(re.escape(token) + r"\s*[<>=≤≥]\s*[-]?\d", window) or re.search(r"[-]?\d\s*[<>=≤≥]\s*" + re.escape(token), window):
        return "expression_core"
    return "full_formula_ok"


def select_candidates_for_placeholders(
    problem_text: str,
    placeholders: list[str],
    raw_items: list[dict[str, Any]],
    threshold: float,
) -> tuple[dict[str, str], list[dict[str, Any]], list[str], str]:
    rejected: list[str] = []
    # A) reject noise and dedupe by latex (keep highest confidence)
    dedup: dict[str, dict[str, Any]] = {}
    for item in raw_items:
        latex = clean_candidate_text(item.get("latex", ""))
        rej = candidate_reject_reason(latex)
        if rej:
            rejected.append(rej)
            continue
        conf = float(item.get("confidence", 0.0) or 0.0)
        prev = dedup.get(latex)
        if prev is None or conf > float(prev.get("confidence", 0.0) or 0.0):
            next_item = dict(item)
            next_item["latex"] = latex
            dedup[latex] = next_item

    filtered = list(dedup.values())
    if not placeholders:
        return {}, filtered, rejected, "no_placeholders"
    if not filtered:
        return {}, filtered, rejected, "no_filtered_candidates"

    # B/C) score by formula_like and placeholder mode
    ranked = []
    for c in filtered:
        feat = candidate_features(c.get("latex", ""))
        base = float(c.get("confidence", 0.0) or 0.0)
        score = base
        if feat["formula_like"]:
            score += 0.2
        if feat["solution_like"]:
            score -= 0.2
        if feat["label_like"]:
            score -= 0.4
        c2 = dict(c)
        c2["_score"] = score
        c2["_features"] = feat
        ranked.append(c2)
    ranked.sort(key=lambda x: float(x.get("_score", 0.0)), reverse=True)

    selected: dict[str, str] = {}
    selected_items: list[dict[str, Any]] = []
    used_latex: set[str] = set()
    for token in placeholders:
        mode = placeholder_mode(problem_text, token)
        best = None
        for c in ranked:
            latex = str(c.get("latex") or "")
            if not latex or latex in used_latex:
                continue
            feat = c.get("_features", {})
            local_score = float(c.get("_score", 0.0))
            if mode == "expression_core":
                if feat.get("contains_comparator"):
                    local_score -= 0.25
                else:
                    local_score += 0.1
            if best is None or local_score > best[0]:
                best = (local_score, c)
        if best is None:
            continue
        chosen = dict(best[1])
        latex = str(chosen.get("latex") or "")
        selected[token] = latex
        selected_items.append(
            {
                "token": token,
                "latex": latex,
                "confidence": float(chosen.get("confidence", 0.0) or 0.0),
                "score": float(best[0]),
                "mode": mode,
            }
        )
        used_latex.add(latex)

    if len(selected) != len(placeholders):
        return {}, filtered, rejected, "selected_count_mismatch"
    avg_conf = sum(float(x.get("confidence", 0.0) or 0.0) for x in selected_items) / max(1, len(selected_items))
    if avg_conf < float(threshold):
        return {}, filtered, rejected, "selected_avg_conf_below_threshold"
    return selected, filtered, rejected, "aligned"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--limit-records", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--ocr-mode", default="local_first_gemini_fallback", choices=["convert_only", "local_ocr", "local_first_gemini_fallback"])
    parser.add_argument("--confidence-threshold", type=float, default=0.85)
    parser.add_argument("--report", default="reports/import_debug/formula_postprocess_report.md")
    parser.add_argument("--title", action="append", default=[], help="Filter by title/source_description, repeatable.")
    args = parser.parse_args()

    dry_run = True
    if args.write:
        dry_run = False
    elif args.dry_run:
        dry_run = True

    root = project_root()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(default_db_path()))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, source_description, source_volume, source_section, problem_text, notes
        FROM textbook_examples
        WHERE source_volume = ? AND source_section = ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (args.volume, args.section, int(args.limit_records)),
    )
    rows = cur.fetchall()
    title_filters = [str(t or "").strip() for t in (args.title or []) if str(t or "").strip()]
    normalized_filters = [normalize_title(t) for t in title_filters]
    missing_titles: list[str] = []
    if normalized_filters:
        available = {}
        for row in rows:
            norm = normalize_title(str(row["source_description"] or ""))
            available.setdefault(norm, []).append(row)
        filtered_rows = []
        seen_ids = set()
        for raw_title, norm_title in zip(title_filters, normalized_filters):
            matched = available.get(norm_title, [])
            if not matched:
                missing_titles.append(raw_title)
                continue
            for r in matched:
                if int(r["id"]) in seen_ids:
                    continue
                seen_ids.add(int(r["id"]))
                filtered_rows.append(r)
        rows = filtered_rows

    stats = {
        "processed_records": 0,
        "formula_assets_total": 0,
        "conversion_success": 0,
        "conversion_failed": 0,
        "readable_assets": 0,
        "ocr_success": 0,
        "ocr_failed": 0,
        "auto_applied_records": 0,
        "auto_applied_placeholders": 0,
        "low_confidence_records": 0,
        "alignment_failed_records": 0,
        "still_needs_review": 0,
        "rollback_available_count": 0,
    }
    lines: list[str] = []
    lines.append(f"# Formula Auto Postprocess Report")
    lines.append(f"- volume: `{args.volume}`")
    lines.append(f"- section: `{args.section}`")
    lines.append(f"- mode: `{args.ocr_mode}`")
    lines.append(f"- dry_run: `{dry_run}`")
    lines.append(f"- confidence_threshold: `{args.confidence_threshold}`")
    lines.append(f"- title_filter: `{title_filters}`")
    lines.append(f"- missing_titles: `{missing_titles}`")
    lines.append("")

    for row in rows:
        meta = load_meta(row["notes"])
        problem_text = str(row["problem_text"] or "")
        has_placeholder = bool(PLACEHOLDER_RE.search(problem_text))
        needs_formula_review = bool(meta.get("needs_formula_review", False))
        if not has_placeholder and not needs_formula_review:
            continue
        stats["processed_records"] += 1
        assets = meta.get("formula_assets", [])
        if not isinstance(assets, list):
            assets = []
        stats["formula_assets_total"] += len(assets)

        placeholders = [m.group(0) for m in PLACEHOLDER_RE.finditer(problem_text)]
        candidates: dict[str, dict[str, Any]] = {}
        raw_items: list[dict[str, Any]] = []
        replacements: dict[str, str] = {}
        row_flags: list[str] = []

        for asset in assets:
            if not isinstance(asset, dict):
                continue
            token = str(asset.get("placeholder_token") or "").strip()
            if not token:
                continue
            abs_path, rel_path = pick_asset_path(asset, root)
            if not abs_path:
                ok, converted_rel, conv_err = try_convert_vector(asset, root)
                if ok:
                    stats["conversion_success"] += 1
                    asset["converted_path"] = converted_rel
                    asset["display_path"] = converted_rel
                    asset["conversion_status"] = "success"
                    abs_path, rel_path = pick_asset_path(asset, root)
                else:
                    stats["conversion_failed"] += 1
                    asset["conversion_status"] = "failed"
                    asset["conversion_error"] = conv_err
                    row_flags.append("conversion_failed")
            if not abs_path:
                continue
            stats["readable_assets"] += 1
            text = ""
            conf = 0.0
            source = ""
            if args.ocr_mode == "convert_only":
                source = "convert_only"
            elif args.ocr_mode == "local_ocr":
                text, conf, source = ocr_local(abs_path)
            else:
                text, conf, source = ocr_local(abs_path)
                if not text:
                    text, conf, source = ocr_gemini(abs_path)
            if text:
                stats["ocr_success"] += 1
            else:
                stats["ocr_failed"] += 1
            candidates[token] = {"latex": text, "confidence": conf, "source": source, "asset_path": rel_path}
            if text:
                raw_items.append(
                    {
                        "token_hint": token,
                        "latex": text,
                        "confidence": conf,
                        "source": source,
                        "asset_path": rel_path,
                    }
                )

        replacements, filtered_items, rejected_reasons, alignment_reason = select_candidates_for_placeholders(
            problem_text,
            placeholders,
            raw_items,
            float(args.confidence_threshold),
        )
        alignment_ok = alignment_reason == "aligned"
        high_conf = bool(replacements)
        apply_allowed = alignment_ok and high_conf
        if not alignment_ok:
            stats["alignment_failed_records"] += 1
            row_flags.append("alignment_failed")
        if not high_conf:
            stats["low_confidence_records"] += 1
            row_flags.append("low_confidence")

        before_text = problem_text
        after_text = problem_text
        apply_status = "not_applied"
        if apply_allowed:
            after_text, changed = replace_placeholders(problem_text, replacements)
            if changed:
                apply_status = "applied"
                stats["auto_applied_records"] += 1
                stats["auto_applied_placeholders"] += len(placeholders)
                stats["rollback_available_count"] += 1

        meta["formula_ocr_candidates"] = candidates
        meta["formula_auto_replacements"] = replacements
        meta["formula_auto_apply_status"] = apply_status if apply_allowed else "low_confidence_or_alignment_failed"
        meta["formula_auto_apply_confidence"] = min([c.get("confidence", 0.0) for c in candidates.values()] + [0.0])
        meta["raw_ocr_candidates_count"] = len(raw_items)
        meta["filtered_candidates_count"] = len(filtered_items)
        meta["selected_candidates_count"] = len(replacements)
        meta["selected_candidates"] = replacements
        meta["rejected_candidates_summary"] = {
            "reasons": sorted(rejected_reasons),
            "count": len(rejected_reasons),
        }
        meta["alignment_reason"] = alignment_reason
        meta["formula_auto_apply_updated_at"] = now_iso()
        if apply_allowed and apply_status == "applied":
            meta.setdefault("original_problem_text", before_text)
            meta["rollback_available"] = True
            meta["needs_review"] = False
            meta["needs_formula_review"] = False
        else:
            meta["needs_review"] = True
            meta["needs_formula_review"] = True
            stats["still_needs_review"] += 1

        if not dry_run:
            cur.execute(
                "UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                (after_text, dump_meta(meta), int(row["id"])),
            )

        lines.append(f"## id={row['id']} {row['source_description']}")
        lines.append(f"- status: `{meta.get('formula_auto_apply_status')}`")
        lines.append(f"- flags: `{','.join(sorted(set(row_flags))) or 'none'}`")
        lines.append(f"- placeholder_count: `{len(placeholders)}`")
        lines.append(f"- raw_ocr_candidates_count: `{len(raw_items)}`")
        lines.append(f"- filtered_candidates_count: `{len(filtered_items)}`")
        lines.append(f"- selected_candidates_count: `{len(replacements)}`")
        lines.append(f"- selected_candidates: `{replacements}`")
        lines.append(f"- rejected_candidates_summary: `{meta.get('rejected_candidates_summary')}`")
        lines.append(f"- alignment_reason: `{alignment_reason}`")
        lines.append("")

    if not dry_run:
        conn.commit()
    conn.close()

    lines.append("## Summary")
    for k, v in stats.items():
        lines.append(f"- {k}: `{v}`")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
