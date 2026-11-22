# -*- coding: utf-8 -*-
"""Recrop TE 11584 cable figure so vertex B label is fully visible.

Root cause: previous bbox y0=412 clipped the top of italic 'B' (ink at PNG y=0),
so the peak looked unlabeled / like a truncated D. Expand top margin only;
keep bottom below 熟習度自評表 (y≈620).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "textbook_import" / "source" / "vocational" / "math_B2" / "第一章 1-2 銳角三角函數-課本.pdf"
DB = ROOT / "instance" / "kumon_math.db"
DPI = 200
PAGE_INDEX = 19
TE_ID = 11584
# Top expanded 412→392 so full 'B'; bottom unchanged to avoid 自評表.
CABLE_BBOX = (395.0, 392.0, 562.0, 598.0)
CABLE_REL = (
    "uploads/question_assets/vocational/longteng/數學B2/"
    "ch01_unknown/sec_1-2_銳角三角函數/advanced_exercise_1-2習題_進階題10_vocation_fig1.png"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def asset_paths(rel_path: str) -> list[Path]:
    """Student /uploads/ route and static mirror must stay identical."""
    rel = rel_path[len("uploads/question_assets/") :]
    return [
        ROOT / "uploads" / "question_assets" / rel,
        ROOT / "static" / "question_assets" / rel,
    ]


def backup_db() -> Path:
    bak_dir = ROOT / "instance" / "backups"
    bak_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = bak_dir / f"kumon_math_pre_b2_p1_cable_crop_{stamp}.db"
    shutil.copy2(DB, dest)
    for suffix in ("-wal", "-shm"):
        side = Path(str(DB) + suffix)
        if side.exists():
            shutil.copy2(side, Path(str(dest) + suffix))
    return dest


def crop() -> dict:
    paths = asset_paths(CABLE_REL)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups: list[str] = []
    doc = fitz.open(PDF)
    page = doc[PAGE_INDEX]
    pix = page.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72), clip=fitz.Rect(*CABLE_BBOX))
    for abs_path in paths:
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        bak = abs_path.with_suffix(abs_path.suffix + f".bak_{stamp}")
        if abs_path.exists():
            shutil.copy2(abs_path, bak)
            backups.append(str(bak))
        pix.save(str(abs_path))
    primary = paths[0]
    data = primary.read_bytes()
    return {
        "abs_path": str(primary),
        "mirrored_paths": [str(p) for p in paths],
        "backup": backups,
        "width": pix.width,
        "height": pix.height,
        "file_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bbox": list(CABLE_BBOX),
        "rel_path": CABLE_REL,
    }


def parse_notes(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {"raw": raw}
    except Exception:
        return {"raw": raw}


def main() -> None:
    report_dir = ROOT / "reports" / "b2_p1_swing_cable_visual"
    report_dir.mkdir(parents=True, exist_ok=True)
    bak = backup_db()
    crop_info = crop()
    # Keep a verified copy beside prior evidence.
    shutil.copy2(crop_info["abs_path"], report_dir / "crop_fixed_11584_full_B.png")

    con = sqlite3.connect(str(DB))
    try:
        row = con.execute(
            "SELECT id, skill_id, notes FROM textbook_examples WHERE id=?",
            (TE_ID,),
        ).fetchone()
        if not row:
            raise SystemExit(f"missing textbook_examples id={TE_ID}")
        notes = parse_notes(row[2])
        assets = notes.get("image_assets") if isinstance(notes.get("image_assets"), list) else []
        asset = {
            "asset_type": "pdf_visual_crop",
            "asset_slot": "pdf_visual_01",
            "source": "pdf",
            "path": CABLE_REL,
            "page_index": PAGE_INDEX,
            "bbox": crop_info["bbox"],
            "width": crop_info["width"],
            "height": crop_info["height"],
            "sha256": crop_info["sha256"],
            "visual_status": "accepted",
            "visual_review_reasons": [],
            "match_method": "audited_B2_1-2_pdf_page20_manual_bbox_full_B",
            "updated_at": now_iso(),
        }
        # Replace same slot / same path; otherwise append.
        replaced = False
        new_assets = []
        for item in assets:
            if not isinstance(item, dict):
                continue
            same = (
                str(item.get("path") or "") == CABLE_REL
                or str(item.get("asset_slot") or "") == "pdf_visual_01"
            )
            if same and not replaced:
                new_assets.append(asset)
                replaced = True
            elif not same:
                new_assets.append(item)
        if not replaced:
            new_assets.append(asset)
        notes["image_assets"] = new_assets
        con.execute(
            "UPDATE textbook_examples SET notes=? WHERE id=?",
            (json.dumps(notes, ensure_ascii=False), TE_ID),
        )
        con.commit()
        report = {
            "backup_db": str(bak),
            "crop": crop_info,
            "db_id": TE_ID,
            "skill_id": row[1],
            "asset": asset,
            "reason": "expand bbox top so italic B is fully inside crop; bottom unchanged",
        }
        (report_dir / "repair_11584_crop_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        con.close()


if __name__ == "__main__":
    main()
