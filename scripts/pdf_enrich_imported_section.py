#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Use same-version PDF as secondary enrichment for DOCX-imported records."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLACEHOLDER_RE = re.compile(r"\[FORMULA_IMAGE_(\d+)\]|\[FORMULA_MISSING\]")
TITLE_PATTERNS = [
    re.compile(r"(例題\s*\d+|例\s*\d+)"),
    re.compile(r"(隨堂練習\s*\d+)"),
    re.compile(r"((?:\d+-\d+)?習題\s*基礎題\s*\d+)"),
    re.compile(r"((?:\d{2,3})\s*統測B)"),
]
MOJIBAKE_CHARS = set("�蝧蝯葫憿箇鞈摨隢")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def has_mojibake_text(text: str) -> bool:
    t = str(text or "")
    if not t:
        return False
    if any(ch in t for ch in MOJIBAKE_CHARS):
        return True
    weird = sum(1 for ch in t if ord(ch) == 0xFFFD or (0xE000 <= ord(ch) <= 0xF8FF))
    ratio = weird / max(1, len(t))
    return ratio >= 0.02


def norm_label(text: str) -> str:
    t = str(text or "").strip()
    t = re.sub(r"\s*\[source_type=.*$", "", t)
    t = re.sub(r"\s+", "", t)
    m = re.match(r"^例題?(\d+)$", t)
    if m:
        return f"例題{int(m.group(1))}"
    m = re.match(r"^隨堂練習(\d+)$", t)
    if m:
        return f"隨堂練習{int(m.group(1))}"
    m = re.match(r"^((?:\d+-\d+)?)習題基礎題(\d+)$", t)
    if m:
        return f"{m.group(1)}習題基礎題{int(m.group(2))}"
    m = re.match(r"^(\d{2,3})統測b$", t.lower())
    if m:
        return f"{m.group(1)}統測B"
    return t


def extract_label_from_line(line: str) -> str:
    raw = str(line or "").strip()
    if not raw:
        return ""
    for pat in TITLE_PATTERNS:
        m = pat.search(raw)
        if m:
            return str(m.group(1) or "").strip()
    return ""


def extract_pdf_candidates(pdf_path: Path) -> tuple[list[dict[str, Any]], str, str]:
    import fitz  # pylint: disable=import-outside-toplevel

    doc = fitz.open(str(pdf_path))
    lines: list[str] = []
    raw_parts: list[str] = []
    for p in doc:
        txt = p.get_text("text")
        raw_parts.append(txt)
        lines.extend([ln.strip() for ln in txt.splitlines() if ln.strip()])
    doc.close()

    raw_text = "\n".join(raw_parts)
    candidates: list[dict[str, Any]] = []
    for i, line in enumerate(lines):
        label = extract_label_from_line(line)
        if not label:
            continue
        body = [line]
        for j in range(i + 1, min(i + 10, len(lines))):
            nxt = lines[j]
            if any(p.search(nxt) for p in TITLE_PATTERNS):
                break
            body.append(nxt)
        text = "\n".join(body).strip()
        conf = 0.91 if len(text) >= 10 and not has_mojibake_text(text) else 0.3
        candidates.append(
            {
                "label": label,
                "label_norm": norm_label(label),
                "text": text,
                "confidence": conf,
            }
        )

    dedup: dict[str, dict[str, Any]] = {}
    for c in candidates:
        key = str(c.get("label_norm") or "")
        if key and key not in dedup:
            dedup[key] = c
    out = list(dedup.values())
    reason = "" if out else "no_title_pattern_matched"
    return out, raw_text, reason


def is_single_title_mode(title_filters: list[str]) -> bool:
    return len([x for x in title_filters if str(x or "").strip()]) <= 1


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", required=True)
    parser.add_argument("--title", action="append", default=[], help="Filter titles, repeatable.")
    args = parser.parse_args()

    dry_run = not bool(args.write)
    root = project_root()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = root / pdf_path
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    pdf_candidates, raw_text, extraction_failed_reason = extract_pdf_candidates(pdf_path)
    title_filters = [str(t or "").strip() for t in (args.title or []) if str(t or "").strip()]
    norm_filters = {norm_label(t) for t in title_filters if norm_label(t)}
    if norm_filters:
        pdf_candidates = [c for c in pdf_candidates if str(c.get("label_norm") or "") in norm_filters]

    raw_text_length = len(raw_text)
    pdf_text_too_short = raw_text_length < 300 and not is_single_title_mode(title_filters)
    pdf_text_has_mojibake = has_mojibake_text(raw_text)
    extraction_quality = "bad" if pdf_text_has_mojibake or (pdf_text_too_short and not pdf_candidates) else "ok"

    conn = sqlite3.connect(str(default_db_path()))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, skill_id, source_curriculum, source_volume, source_chapter, source_section,
               source_description, source_paragraph, problem_text, notes, correct_answer, detailed_solution
        FROM textbook_examples
        WHERE source_volume=? AND source_section=?
        ORDER BY id ASC
        """,
        (args.volume, args.section),
    )
    rows = cur.fetchall()

    by_label: dict[str, list[Any]] = {}
    db_titles_in_section: list[str] = []
    for r in rows:
        key = norm_label(r["source_description"])
        by_label.setdefault(key, []).append(r)
        db_titles_in_section.append(key)

    stats = {
        "pdf_candidates": len(pdf_candidates),
        "matched_existing": 0,
        "proposed_updates": 0,
        "proposed_inserts": 0,
        "low_confidence": 0,
        "ambiguous_match": 0,
        "skipped_already_complete": 0,
        "still_missing_formula": 0,
    }
    raw_preview = raw_text[:2000].replace("`", "'")
    lines = [
        "# PDF Enrich Report",
        f"- pdf: `{pdf_path.as_posix()}`",
        f"- volume: `{args.volume}`",
        f"- section: `{args.section}`",
        f"- dry_run: `{dry_run}`",
        f"- title_filter: `{title_filters}`",
        f"- raw_text_length: `{raw_text_length}`",
        f"- raw_text_preview: `{raw_preview}`",
        f"- extraction_failed_reason: `{extraction_failed_reason}`",
        f"- extraction_quality: `{extraction_quality}`",
        f"- pdf_text_too_short: `{pdf_text_too_short}`",
        f"- pdf_text_has_mojibake: `{pdf_text_has_mojibake}`",
        f"- candidate_titles: `{[c.get('label_norm') for c in pdf_candidates]}`",
        f"- db_titles_in_section: `{sorted(set(db_titles_in_section))}`",
        "",
    ]

    inserted = 0
    unmatched_pdf_candidates = []
    for cand in pdf_candidates:
        label_norm = str(cand["label_norm"] or "")
        label_raw = str(cand["label"] or "")
        text = str(cand["text"] or "")
        conf = float(cand["confidence"] or 0.0)

        if extraction_quality == "bad":
            stats["low_confidence"] += 1
            unmatched_pdf_candidates.append({"title": label_raw, "reason": "pdf_text_low_quality"})
            continue
        if has_mojibake_text(label_raw) or has_mojibake_text(label_norm) or has_mojibake_text(text):
            stats["low_confidence"] += 1
            unmatched_pdf_candidates.append({"title": label_raw, "reason": "mojibake_detected"})
            continue
        if conf < 0.85:
            stats["low_confidence"] += 1
            unmatched_pdf_candidates.append({"title": label_raw, "reason": "low_confidence"})
            continue

        matched_list = by_label.get(label_norm, [])
        if len(matched_list) > 1:
            stats["ambiguous_match"] += 1
            unmatched_pdf_candidates.append({"title": label_raw, "reason": "ambiguous_match"})
            continue
        matched = matched_list[0] if matched_list else None

        if matched is None:
            stats["proposed_inserts"] += 1
            lines.append(f"- proposed_insert: `{label_raw}` conf={conf:.2f} match_reason=no_db_match")
            if not dry_run and rows:
                seed = rows[0]
                meta = {
                    "pdf_enrich_candidate_text": text,
                    "pdf_enrich_source": pdf_path.as_posix(),
                    "pdf_enrich_confidence": conf,
                    "pdf_enrich_status": "applied_insert",
                    "pdf_enrich_updated_at": now_iso(),
                }
                cur.execute(
                    """
                    INSERT INTO textbook_examples
                    (skill_id, source_curriculum, source_volume, source_chapter, source_section,
                     source_description, source_paragraph, problem_text, problem_type, correct_answer,
                     detailed_solution, notes, difficulty_level, difficulty_h)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        seed["skill_id"],
                        seed["source_curriculum"],
                        seed["source_volume"],
                        seed["source_chapter"],
                        seed["source_section"],
                        label_raw,
                        "",
                        text,
                        None,
                        seed["correct_answer"],
                        seed["detailed_solution"],
                        dump_meta(meta),
                        1,
                        1.0,
                    ),
                )
                inserted += 1
            continue

        stats["matched_existing"] += 1
        lines.append(f"- matched_existing: id={matched['id']} `{label_raw}` match_reason=title_alias_exact")
        existing_text = str(matched["problem_text"] or "")
        if not PLACEHOLDER_RE.search(existing_text):
            stats["skipped_already_complete"] += 1
            continue

        stats["proposed_updates"] += 1
        lines.append(f"- proposed_update: id={matched['id']} `{label_raw}` conf={conf:.2f} match_reason=has_placeholder")
        meta = load_meta(matched["notes"])
        meta["pdf_enrich_candidate_text"] = text
        meta["pdf_enrich_source"] = pdf_path.as_posix()
        meta["pdf_enrich_confidence"] = conf
        meta["pdf_enrich_status"] = "proposed_update" if dry_run else "applied"
        meta["pdf_enrich_updated_at"] = now_iso()
        meta.setdefault("original_problem_text_before_pdf_enrich", existing_text)
        if not dry_run:
            cur.execute(
                "UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                (text, dump_meta(meta), int(matched["id"])),
            )

    cur.execute(
        "SELECT COUNT(*) AS c FROM textbook_examples WHERE source_volume=? AND source_section=? AND problem_text LIKE '%[FORMULA_%'",
        (args.volume, args.section),
    )
    stats["still_missing_formula"] = int(cur.fetchone()["c"])

    unmatched_db_placeholder_titles = []
    for r in rows:
        if PLACEHOLDER_RE.search(str(r["problem_text"] or "")):
            k = norm_label(r["source_description"])
            if not any(str(c.get("label_norm") or "") == k for c in pdf_candidates):
                unmatched_db_placeholder_titles.append(k)

    if not dry_run:
        conn.commit()
    conn.close()

    lines.append("")
    lines.append(f"- unmatched_pdf_candidates: `{unmatched_pdf_candidates}`")
    lines.append(f"- unmatched_db_placeholder_titles: `{sorted(set(unmatched_db_placeholder_titles))}`")
    lines.append("## Summary")
    for k, v in stats.items():
        lines.append(f"- {k}: `{v}`")
    lines.append(f"- inserted_rows: `{inserted}`")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

