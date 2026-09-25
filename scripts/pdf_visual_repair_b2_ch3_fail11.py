# -*- coding: utf-8 -*-
"""Surgical repair for B2 Ch3 FAIL-11 PDF visual crops.

Only updates notes.image_assets + PNG files for the 11 FAIL example_ids.
Does not reimport, does not touch problem_text/skill/section/answers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.question_image_assets import (  # noqa: E402
    build_question_asset_dir,
    build_question_asset_filename,
    list_student_image_assets_from_notes,
)
from core.textbook_pdf_visual import build_pdf_visual_asset_record, upsert_notes_image_asset  # noqa: E402
from core.textbook_question_anchor import normalize_question_label  # noqa: E402

SRC = ROOT / "textbook_import" / "source" / "vocational" / "math_B2"
DB = ROOT / "instance" / "kumon_math.db"
OUT = ROOT / "scratch" / "_b2_ch3_visual_qa"
DPI = 200

PDFS = {
    "3-1": next(SRC.glob("第三章 3-1*課本.pdf")),
    "3-2": next(SRC.glob("第三章 3-2*課本.pdf")),
    "3-3": next(SRC.glob("第三章 3-3*課本.pdf")),
    "self": next(SRC.glob("第三章 自我評量*課本.pdf")),
}

# Manually verified MOUNT_PLAN after Visual QA FAIL inspection.
# page is 1-based; bbox in PDF points.
MOUNT_PLAN: dict[int, dict[str, Any]] = {
    11732: {
        "bucket": "3-1",
        "page": 5,
        "bbox": [400.0, 395.0, 530.0, 520.0],
        "reason": "隨堂練習1 平行四邊形ABCD（非航線圖）",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11736: {
        "bucket": "3-1",
        "page": 9,
        "bbox": [410.0, 350.0, 520.0, 440.0],
        "reason": "隨堂練習3 △ABC（非例4/隨堂4五邊形）",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11744: {
        "bucket": "3-1",
        "page": 15,
        "bbox": [420.0, 155.0, 555.0, 265.0],
        "reason": "基礎題1 三角形中點 D,E,F",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11748: {
        "bucket": "3-1",
        "page": 15,
        "bbox": [400.0, 505.0, 560.0, 610.0],
        "reason": "基礎題5 線段 A-C-D-B 等分（非基礎6網格）",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11751: {
        "bucket": "3-1",
        "page": 16,
        "bbox": [400.0, 235.0, 560.0, 350.0],
        "reason": "基礎題8 完整三角形標籤",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11752: {
        "bucket": "3-1",
        "page": 16,
        "bbox": [395.0, 365.0, 555.0, 475.0],
        "reason": "進階題9 獨立構形（不共用基礎8）",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11753: {
        "bucket": "3-1",
        "page": 16,
        "bbox": [400.0, 455.0, 560.0, 585.0],
        "reason": "進階題10 平行四邊形（排除熟習度自評表）",
        "section_title": "3-1 向量的作圖",
        "chapter_title": "3 向量",
    },
    11795: {
        "bucket": "3-3",
        "page": 11,
        "bbox": [380.0, 200.0, 540.0, 320.0],
        "reason": "108統測B 坐標向量圖（非輸入訊息UI）",
        "section_title": "3-3 向量的內積",
        "chapter_title": "3 向量",
    },
    11804: {
        "bucket": "3-3",
        "page": 14,
        "bbox": [120.0, 260.0, 540.0, 450.0],
        "reason": "進階題9 同時含圖（一）與圖（二）",
        "section_title": "3-3 向量的內積",
        "chapter_title": "3 向量",
    },
    11806: {
        "bucket": "self",
        "page": 1,
        "bbox": [430.0, 185.0, 540.0, 270.0],
        "reason": "自我評量題1 長方形ABCD（不含題2/3）",
        "section_title": "第三章 自我評量",
        "chapter_title": "3 向量",
    },
    11817: {
        "bucket": "self",
        "page": 1,
        "bbox": [400.0, 395.0, 540.0, 520.0],
        "reason": "自我評量題3 完整含 A/E/F/G/M",
        "section_title": "第三章 自我評量",
        "chapter_title": "3 向量",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_notes(raw: str | None) -> dict[str, Any]:
    try:
        obj = json.loads(raw or "{}")
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def infer_source_type(desc: str, notes: dict[str, Any]) -> str:
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


def crop_pdf(pdf: Path, page_1based: int, bbox: list[float], dest: Path, dpi: int = DPI) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf))
    try:
        page = doc.load_page(int(page_1based) - 1)
        zoom = float(dpi) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        x0, y0, x1, y1 = [int(round(v * zoom)) for v in bbox]
        pad = int(round(3 * zoom / 2.5))
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(img.width, x1 + pad)
        y1 = min(img.height, y1 + pad)
        crop = img.crop((x0, y0, x1, y1))
        crop.save(dest, format="PNG", optimize=True)
        return {
            "width": crop.width,
            "height": crop.height,
            "file_size": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "dpi": dpi,
        }
    finally:
        doc.close()


def load_row(conn: sqlite3.Connection, eid: int) -> sqlite3.Row:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT id, source_description, problem_text, problem_type, notes, "
        "source_section, skill_id FROM textbook_examples WHERE id=?",
        (eid,),
    ).fetchone()
    if row is None:
        raise KeyError(eid)
    return row


def repair_one(conn: sqlite3.Connection, eid: int, *, apply: bool) -> dict[str, Any]:
    plan = MOUNT_PLAN[eid]
    row = load_row(conn, eid)
    notes = parse_notes(row["notes"])
    old_assets = notes.get("image_assets") or []
    old = old_assets[0] if old_assets and isinstance(old_assets[0], dict) else {}
    old_path = old.get("path") or old.get("display_path")
    old_sha = old.get("sha256")
    old_bbox = old.get("bbox")

    pdf = PDFS[plan["bucket"]]
    anchor = notes.get("question_anchor") if isinstance(notes.get("question_anchor"), dict) else {}
    anchor_id = str(anchor.get("anchor_id") or f"repair_{eid}")
    label = normalize_question_label(str(row["source_description"] or ""))
    source_type = infer_source_type(str(row["source_description"] or ""), notes)

    rel_dir = build_question_asset_dir(
        "vocational",
        "longteng",
        "數學B2",
        plan["chapter_title"],
        plan["section_title"],
    )
    filename = build_question_asset_filename(
        source_type=source_type,
        question_title=label,
        question_id_or_dedupe=anchor_id,
        fig_index=1,
        ext="png",
    )
    rel_path = f"{rel_dir}/{filename}".replace("\\", "/")
    abs_path = ROOT / rel_path

    meta = {
        "id": eid,
        "desc": row["source_description"],
        "old_asset": old_path,
        "new_asset": rel_path,
        "old_bbox": old_bbox,
        "new_bbox": plan["bbox"],
        "old_sha": old_sha,
        "source_pdf_page": plan["page"],
        "repair_reason": plan["reason"],
        "pdf": str(pdf.relative_to(ROOT)),
    }

    if not apply:
        meta["status"] = "dry-run"
        return meta

    image_meta = crop_pdf(pdf, plan["page"], list(plan["bbox"]), abs_path, dpi=DPI)
    asset = build_pdf_visual_asset_record(
        rel_path=rel_path,
        page_1based=int(plan["page"]),
        bbox=list(plan["bbox"]),
        classification="required",
        visual_type="diagram",
        match_method="manual_fail11_surgical_mount",
        match_score=1.0,
        reason=str(plan["reason"]),
        image_meta=image_meta,
        anchor_id=anchor_id,
        asset_slot="pdf_visual_01",
    )
    notes = upsert_notes_image_asset(notes, asset, slot="pdf_visual_01")
    notes["has_image"] = True
    notes["needs_image_review"] = False
    notes["image_repair"] = {
        "at": now_iso(),
        "reason": plan["reason"],
        "method": "manual_fail11_surgical_mount",
        "previous_path": old_path,
        "previous_sha": old_sha,
    }
    conn.execute(
        "UPDATE textbook_examples SET notes=? WHERE id=?",
        (json.dumps(notes, ensure_ascii=False), eid),
    )
    meta["new_sha"] = image_meta["sha256"]
    meta["width"] = image_meta["width"]
    meta["height"] = image_meta["height"]
    meta["status"] = "repaired"
    return meta


def verify_all() -> dict[str, Any]:
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = conn.execute(
        """
        SELECT id, source_section, source_description, problem_text, notes
        FROM textbook_examples
        WHERE source_volume='數學B2' AND source_chapter='第3章 向 量'
        ORDER BY id
        """
    ).fetchall()
    conn.close()
    items = []
    for id_, sec, desc, pt, notes_raw in rows:
        if "如圖" not in (pt or ""):
            continue
        notes = parse_notes(notes_raw)
        assets = notes.get("image_assets") or []
        a = assets[0] if assets else {}
        rel = (a.get("path") or a.get("display_path") or "").replace("\\", "/")
        abs_p = ROOT / rel if rel else None
        exists = bool(abs_p and abs_p.is_file())
        readable = False
        w = h = None
        sha = None
        if exists and abs_p is not None:
            try:
                im = Image.open(abs_p)
                im.load()
                w, h = im.size
                readable = True
                sha = sha256_file(abs_p)
            except Exception:
                readable = False
        student = list_student_image_assets_from_notes(notes, root_path=str(ROOT))
        items.append(
            {
                "id": id_,
                "desc": desc,
                "section": sec,
                "path": rel,
                "exists": exists,
                "readable": readable,
                "width": w,
                "height": h,
                "sha": sha,
                "bbox": a.get("bbox"),
                "page": a.get("source_page"),
                "match_method": a.get("match_method"),
                "student_urls": [s.get("url") for s in student],
                "is_fail11": id_ in MOUNT_PLAN,
            }
        )
    return {
        "total": len(items),
        "exists": sum(1 for i in items if i["exists"]),
        "readable": sum(1 for i in items if i["readable"]),
        "missing": sum(1 for i in items if not i["exists"]),
        "broken": sum(1 for i in items if i["exists"] and not i["readable"]),
        "fail11_ok": all(
            i["exists"] and i["readable"] and i["bbox"] and i["student_urls"]
            for i in items
            if i["is_fail11"]
        ),
        "items": items,
    }


def build_contact_sheet(items: list[dict[str, Any]], dest: Path) -> None:
    prev = dest.parent / "previews_after"
    prev.mkdir(parents=True, exist_ok=True)
    cards = []
    for it in items:
        src = ROOT / it["path"] if it.get("path") else None
        preview_rel = ""
        if src and src.is_file():
            name = f"{it['id']}_{it['desc']}.png".replace("/", "_").replace(" ", "_")
            target = prev / name
            target.write_bytes(src.read_bytes())
            preview_rel = f"previews_after/{name}"
        flag = "FAIL11" if it.get("is_fail11") else ""
        cards.append(
            f"""
            <div class="card">
              <div class="meta">
                <b>#{it['id']}</b> {it['desc']} {flag}<br>
                page={it.get('page')} bbox={it.get('bbox')}<br>
                {it.get('width')}×{it.get('height')} · method={it.get('match_method')}<br>
                sha={(it.get('sha') or '')[:12]}
              </div>
              <img src="{preview_rel}" alt="png">
            </div>"""
        )
    html = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>B2 Ch3 Visual QA After FAIL11 Repair</title>
<style>
body{{font-family:Segoe UI,Microsoft JhengHei,sans-serif;background:#111;color:#eee;margin:16px}}
.card{{border:1px solid #444;margin:10px 0;padding:10px;background:#1a1a1a}}
img{{max-width:420px;max-height:320px;background:#fff}}
.meta{{font-size:13px;margin-bottom:8px}}
</style></head><body>
<h1>B2 Ch3 Visual QA — After FAIL-11 Surgical Repair</h1>
{''.join(cards)}
</body></html>"""
    dest.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    apply = bool(args.apply)

    conn = sqlite3.connect(str(DB))
    results = []
    try:
        for eid in sorted(MOUNT_PLAN):
            results.append(repair_one(conn, eid, apply=apply))
        if apply:
            conn.commit()
    finally:
        conn.close()

    verification = verify_all() if apply else None
    if apply and verification:
        OUT.mkdir(parents=True, exist_ok=True)
        after_json = OUT / "qa_after.json"
        after_html = OUT / "contact_sheet_after.html"
        payload = {
            "repaired_at": now_iso(),
            "repairs": results,
            "verification": verification,
        }
        after_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        build_contact_sheet(verification["items"], after_html)
        print(
            json.dumps(
                {
                    "mode": "apply",
                    "repaired": len(results),
                    "verification": {
                        k: verification[k]
                        for k in (
                            "total",
                            "exists",
                            "readable",
                            "missing",
                            "broken",
                            "fail11_ok",
                        )
                    },
                    "after_json": str(after_json),
                    "after_html": str(after_html),
                    "repairs": [
                        {
                            "id": r["id"],
                            "old_sha": (r.get("old_sha") or "")[:12],
                            "new_sha": (r.get("new_sha") or "")[:12],
                            "page": r["source_pdf_page"],
                            "reason": r["repair_reason"],
                        }
                        for r in results
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            json.dumps(
                {"mode": "dry-run", "planned": results},
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
