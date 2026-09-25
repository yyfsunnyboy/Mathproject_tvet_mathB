# -*- coding: utf-8 -*-
"""B2 Chapter 3 PDF visual backfill (uploads/question_assets + notes.image_assets).

Reuses core.textbook_pdf_visual.enrich_textbook_examples_with_pdf_visuals.
Scoped V3 import skipped PDF_VISUAL; this script mounts only Ch3.

Usage:
  python scripts/pdf_visual_backfill_b2_ch3.py --dry-run
  python scripts/pdf_visual_backfill_b2_ch3.py --apply

Does NOT: reimport text, change skill_id/section/problem_text, touch B1/Ch1 assets,
RAG, correct_answer, or pending skill status.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.question_image_assets import list_student_image_assets_from_notes  # noqa: E402
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals  # noqa: E402
from core.textbook_question_anchor import (  # noqa: E402
    build_question_anchor,
    detect_anchor_id_collisions,
    normalize_question_label,
)

SRC = ROOT / "textbook_import" / "source" / "vocational" / "math_B2"
DB = ROOT / "instance" / "kumon_math.db"
OUT_DIR = ROOT / "scratch"
VOLUME = "數學B2"
CHAPTER_DB = "第3章 向 量"
CURRICULUM = "vocational"
PUBLISHER = "longteng"
CHAPTER_TITLE = "3 向量"

SECTION_PDFS = {
    "3-1": next(SRC.glob("第三章 3-1*課本.pdf")),
    "3-2": next(SRC.glob("第三章 3-2*課本.pdf")),
    "3-3": next(SRC.glob("第三章 3-3*課本.pdf")),
    "self": next(SRC.glob("第三章 自我評量*課本.pdf")),
}
SECTION_TITLES = {
    "3-1": "3-1 向量的作圖",
    "3-2": "3-2 向量的坐標表示法",
    "3-3": "3-3 向量的內積",
    "self": "第三章 自我評量",
}


def _notes(raw: str | None) -> dict[str, Any]:
    try:
        data = json.loads(raw or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _bucket(desc: str, sec: str) -> str:
    if "自我評量" in (desc or ""):
        return "self"
    if (sec or "").startswith("3-1"):
        return "3-1"
    if (sec or "").startswith("3-2"):
        return "3-2"
    if (sec or "").startswith("3-3"):
        return "3-3"
    return "other"


def _infer_source_type(desc: str, notes: dict[str, Any]) -> str:
    for key in ("question_type", "source_type"):
        val = notes.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    d = desc or ""
    if d.startswith("例"):
        return "textbook_example"
    if d.startswith("隨堂"):
        return "in_class_practice"
    if "進階" in d:
        return "advanced_exercise"
    if "習題" in d or "基礎" in d:
        return "textbook_exercise"
    if "統測" in d:
        return "exam_practice"
    if "自我評量" in d:
        return "self_assessment"
    return "textbook_exercise"


def _section_code(bucket: str, sec: str) -> str:
    if bucket == "self":
        return "3"
    m = __import__("re").search(r"(3-\d+)", sec or "")
    return m.group(1) if m else bucket


def load_examples(conn: sqlite3.Connection) -> list[SimpleNamespace]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, skill_id, source_curriculum, source_volume, source_chapter,
               source_section, source_description, problem_text, problem_type, notes
        FROM textbook_examples
        WHERE source_volume=? AND source_chapter=?
        ORDER BY id
        """,
        (VOLUME, CHAPTER_DB),
    ).fetchall()
    out: list[SimpleNamespace] = []
    for r in rows:
        notes = _notes(r["notes"])
        out.append(
            SimpleNamespace(
                id=r["id"],
                skill_id=r["skill_id"],
                source_curriculum=r["source_curriculum"] or CURRICULUM,
                source_volume=r["source_volume"],
                source_chapter=r["source_chapter"],
                source_section=r["source_section"],
                source_description=r["source_description"],
                problem_text=r["problem_text"],
                problem_type=r["problem_type"]
                or notes.get("question_type")
                or notes.get("source_type"),
                notes=r["notes"],
                source_order=notes.get("source_order")
                or (notes.get("question_anchor") or {}).get("source_order"),
            )
        )
    return out


def ensure_anchors(
    conn: sqlite3.Connection,
    examples: list[SimpleNamespace],
    *,
    apply: bool,
) -> dict[str, Any]:
    """Fill missing question_anchor for Ch3 image candidates only (如圖)."""
    filled = 0
    kept = 0
    anchors: list[dict[str, Any]] = []
    # Stable order within each bucket for source_order fallback
    by_bucket: dict[str, list[SimpleNamespace]] = {}
    for ex in examples:
        if "如圖" not in (ex.problem_text or ""):
            continue
        by_bucket.setdefault(_bucket(ex.source_description or "", ex.source_section or ""), []).append(ex)

    for bucket, items in by_bucket.items():
        for idx, ex in enumerate(items, start=1):
            notes = _notes(ex.notes)
            existing = notes.get("question_anchor")
            if isinstance(existing, dict) and existing.get("anchor_id"):
                kept += 1
                anchors.append(existing)
                continue
            label = normalize_question_label(str(ex.source_description or ""))
            source_type = _infer_source_type(str(ex.source_description or ""), notes)
            source_order = int(ex.source_order or idx)
            anchor = build_question_anchor(
                curriculum=CURRICULUM,
                publisher=PUBLISHER,
                volume=VOLUME,
                chapter="3",
                section=_section_code(bucket, str(ex.source_section or "")),
                source_type=source_type,
                question_label=label,
                source_order=source_order,
                problem_text=str(ex.problem_text or ""),
                occurrence_index=1,
            )
            payload = {
                k: anchor.get(k)
                for k in (
                    "anchor_id",
                    "anchor_key",
                    "curriculum",
                    "publisher",
                    "volume",
                    "chapter",
                    "section",
                    "question_type",
                    "question_number",
                    "source_order",
                    "block_index",
                    "occurrence_index",
                    "question_label",
                    "source_type",
                    "text_fingerprint",
                )
            }
            notes["question_anchor"] = payload
            notes.setdefault("question_type", source_type)
            dumped = json.dumps(notes, ensure_ascii=False)
            ex.notes = dumped
            if apply:
                conn.execute(
                    "UPDATE textbook_examples SET notes=? WHERE id=?",
                    (dumped, ex.id),
                )
            filled += 1
            anchors.append(payload)
    if apply:
        conn.commit()
    return {
        "filled": filled,
        "kept": kept,
        "collisions": detect_anchor_id_collisions(anchors),
    }


def run_enrich(
    examples: list[SimpleNamespace],
    *,
    write_notes: bool,
    conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    mutables = {ex.id: ex for ex in examples}
    own_conn = False
    write_conn = conn
    if write_notes and write_conn is None:
        write_conn = sqlite3.connect(str(DB))
        own_conn = True
    try:
        for bucket, pdf in SECTION_PDFS.items():
            subset = [
                mutables[ex.id]
                for ex in examples
                if _bucket(ex.source_description or "", ex.source_section or "") == bucket
            ]
            if not subset:
                continue
            info = {
                "curriculum": CURRICULUM,
                "publisher": PUBLISHER,
                "volume": VOLUME,
                "chapter": CHAPTER_TITLE,
                "section": SECTION_TITLES[bucket],
            }
            summary = enrich_textbook_examples_with_pdf_visuals(
                pdf_path=pdf,
                examples=subset,
                curriculum_info=info,
                project_root=ROOT,
                write_notes=write_notes,
                publish_assets=False,
            )
            if write_notes and write_conn is not None:
                for ex in subset:
                    payload = (
                        ex.notes
                        if isinstance(ex.notes, str)
                        else json.dumps(ex.notes, ensure_ascii=False)
                    )
                    write_conn.execute(
                        "UPDATE textbook_examples SET notes=? WHERE id=?",
                        (payload, ex.id),
                    )
                write_conn.commit()
            summaries[bucket] = {
                "pdf": str(pdf.relative_to(ROOT)),
                "examples": len(subset),
                "ok": summary.get("ok"),
                "mounted": summary.get("mounted"),
                "visual_candidates": summary.get("visual_candidates"),
                "questions_matched": summary.get("questions_matched"),
                "high_confidence": summary.get("high_confidence"),
                "skipped_low_confidence": summary.get("skipped_low_confidence"),
                "skipped_decorative": summary.get("skipped_decorative"),
                "skipped_none": summary.get("skipped_none"),
                "errors": summary.get("errors"),
                "warnings": summary.get("warnings"),
                "rows": summary.get("rows"),
            }
    finally:
        if own_conn and write_conn is not None:
            write_conn.close()
    return summaries


def verify_like_tu(examples: list[SimpleNamespace]) -> dict[str, Any]:
    like = [ex for ex in examples if "如圖" in (ex.problem_text or "")]
    ok = []
    missing = []
    broken = []
    for ex in like:
        notes = _notes(ex.notes if isinstance(ex.notes, str) else json.dumps(ex.notes or {}))
        assets = notes.get("image_assets") or []
        student = list_student_image_assets_from_notes(notes, root_path=str(ROOT))
        entry = {
            "id": ex.id,
            "source_description": ex.source_description,
            "section": ex.source_section,
            "asset_count": len(assets) if isinstance(assets, list) else 0,
            "student_urls": [a.get("url") for a in student],
            "paths": [
                (a.get("path") or a.get("display_path"))
                for a in (assets if isinstance(assets, list) else [])
                if isinstance(a, dict)
            ],
        }
        if not assets:
            missing.append(entry)
            continue
        paths_ok = True
        for rel in entry["paths"]:
            if not rel or not (ROOT / str(rel).replace("\\", "/")).is_file():
                paths_ok = False
                break
        if not paths_ok or not student:
            broken.append(entry)
        else:
            ok.append(entry)
    return {
        "like_tu_total": len(like),
        "ok": len(ok),
        "missing_asset": missing,
        "broken_binding": broken,
        "ok_ids": [x["id"] for x in ok],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="B2 Ch3 PDF visual backfill")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply = bool(args.apply)

    conn = sqlite3.connect(str(DB))
    try:
        examples = load_examples(conn)
        like_ids = [ex.id for ex in examples if "如圖" in (ex.problem_text or "")]
        anchor_report = ensure_anchors(conn, examples, apply=apply)
        # Reload notes after anchor fill when applying
        if apply:
            examples = load_examples(conn)
        summaries = run_enrich(examples, write_notes=apply, conn=conn if apply else None)
        # Reload for verify after apply
        if apply:
            examples = load_examples(conn)
        # For dry-run, enrich mutates in-memory notes only when write_notes=True;
        # dry-run uses write_notes=False so verify against enrich row statuses.
        if apply:
            coverage = verify_like_tu(examples)
        else:
            row_by_id = {}
            for s in summaries.values():
                for row in s.get("rows") or []:
                    row_by_id[row.get("id")] = row
            like = [ex for ex in examples if "如圖" in (ex.problem_text or "")]
            would_mount = [
                ex.id
                for ex in like
                if (row_by_id.get(ex.id) or {}).get("status") == "mounted"
            ]
            coverage = {
                "like_tu_total": len(like),
                "would_mount": len(would_mount),
                "would_mount_ids": would_mount,
                "not_mounted": [
                    {
                        "id": ex.id,
                        "source_description": ex.source_description,
                        "status": (row_by_id.get(ex.id) or {}).get("status"),
                        "classification": (row_by_id.get(ex.id) or {}).get("classification"),
                        "score": (row_by_id.get(ex.id) or {}).get("match_score"),
                        "reason": (row_by_id.get(ex.id) or {}).get("visual_reason"),
                    }
                    for ex in like
                    if (row_by_id.get(ex.id) or {}).get("status") != "mounted"
                ],
            }
    finally:
        conn.close()

    payload = {
        "mode": "apply" if apply else "dry-run",
        "like_tu_ids": like_ids,
        "anchor_report": anchor_report,
        "enrich_summaries": {
            k: {kk: vv for kk, vv in v.items() if kk != "rows"}
            for k, v in summaries.items()
        },
        "enrich_rows": {k: v.get("rows") for k, v in summaries.items()},
        "coverage": coverage,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / (
        "_b2_ch3_pdf_visual_backfill_apply.json"
        if apply
        else "_b2_ch3_pdf_visual_backfill_dryrun.json"
    )
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "mode": payload["mode"],
        "like_tu_count": len(like_ids),
        "anchors": anchor_report,
        "enrich_mounted": {k: v.get("mounted") for k, v in summaries.items()},
        "coverage": {
            k: (len(v) if isinstance(v, list) else v)
            for k, v in coverage.items()
            if k not in {"ok_ids", "would_mount_ids"}
        },
        "out": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
