# -*- coding: utf-8 -*-
"""P1 repair: swing/cable Skill remap + correct PDF crops (B2 only).

- TE 11583 (鞦韆 / chord+arc) -> vh_數學B2_ArcLengthAndAreaOfSector
- TE 11584 (纜車 / 45° projection) -> vh_數學B2_TrigonometricFunctionsOfAcuteAngles
- Recrop page-20 figures; overwrite existing asset paths; refresh notes.image_assets
- Does NOT delete student_problem_type_mastery rows
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
PAGE_INDEX = 19  # source page 20

SWING_ID = 11583
CABLE_ID = 11584
SECTOR = "vh_數學B2_ArcLengthAndAreaOfSector"
ACUTE = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
SPECIAL = "vh_數學B2_TrigonometricValuesOfSpecialAngles"

# Audited bboxes (PDF user space) from page-20 layout — exclude 熟習度自評表.
SWING_BBOX = (410.0, 255.0, 555.0, 400.0)
CABLE_BBOX = (400.0, 412.0, 560.0, 598.0)

SWING_REL = (
    "uploads/question_assets/vocational/longteng/數學B2/"
    "ch01_unknown/sec_1-2_銳角三角函數/advanced_exercise_1-2習題_進階題9_vocation_fig1.png"
)
CABLE_REL = (
    "uploads/question_assets/vocational/longteng/數學B2/"
    "ch01_unknown/sec_1-2_銳角三角函數/advanced_exercise_1-2習題_進階題10_vocation_fig1.png"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def backup_db() -> Path:
    bak_dir = ROOT / "instance" / "backups"
    bak_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = bak_dir / f"kumon_math_pre_b2_p1_swing_cable_{stamp}.db"
    shutil.copy2(DB, dest)
    for suffix in ("-wal", "-shm"):
        side = Path(str(DB) + suffix)
        if side.exists():
            shutil.copy2(side, Path(str(dest) + suffix))
    return dest


def crop_to(rel_path: str, bbox: tuple[float, float, float, float]) -> dict:
    abs_path = ROOT / "static" / Path(rel_path).as_posix().removeprefix("uploads/")
    # static serves uploads/question_assets from static/question_assets
    if rel_path.startswith("uploads/question_assets/"):
        abs_path = ROOT / "static" / "question_assets" / rel_path[len("uploads/question_assets/") :]
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    # keep previous bytes
    bak = abs_path.with_suffix(abs_path.suffix + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    if abs_path.exists():
        shutil.copy2(abs_path, bak)
    doc = fitz.open(PDF)
    page = doc[PAGE_INDEX]
    pix = page.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72), clip=fitz.Rect(*bbox))
    pix.save(str(abs_path))
    data = abs_path.read_bytes()
    return {
        "abs_path": str(abs_path),
        "backup": str(bak) if bak.exists() else None,
        "width": pix.width,
        "height": pix.height,
        "file_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bbox": list(bbox),
        "rel_path": rel_path,
    }


def parse_notes(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {"raw": raw}
    except Exception:
        return {"raw": raw}


def upsert_asset(notes: dict, *, te_id: int, crop: dict, anchor_id: str) -> dict:
    asset = {
        "asset_type": "pdf_visual_crop",
        "asset_slot": "pdf_visual_01",
        "source": "pdf",
        "path": crop["rel_path"],
        "display_path": crop["rel_path"],
        "page_index": PAGE_INDEX,
        "source_page": PAGE_INDEX + 1,
        "bbox": crop["bbox"],
        "needs_crop_review": False,
        "needs_image_conversion": False,
        "reason": "audited_B2_1-2_p1_swing_cable_repair",
        "image_description": "required",
        "visual_type": "diagram",
        "visual_classification": "required",
        "visual_status": "accepted",
        "match_method": "audited_B2_1-2_pdf_page20_manual_bbox",
        "match_score": 1.0,
        "question_anchor": anchor_id,
        "width": crop["width"],
        "height": crop["height"],
        "file_size": crop["file_size"],
        "sha256": crop["sha256"],
        "dpi": DPI,
        "repaired_at": now_iso(),
        "repair_ticket": "P1_swing_cable_skill_and_visual",
    }
    notes = dict(notes)
    notes["has_image"] = True
    notes["needs_image_review"] = False
    notes["image_assets"] = [asset]
    notes["pdf_visual_status"] = "accepted"
    notes["p1_swing_cable_repair"] = {
        "textbook_example_id": te_id,
        "repaired_at": now_iso(),
        "bbox": crop["bbox"],
        "sha256": crop["sha256"],
    }
    return notes


def main() -> None:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    if not DB.is_file():
        raise FileNotFoundError(DB)

    bak = backup_db()
    swing_crop = crop_to(SWING_REL, SWING_BBOX)
    cable_crop = crop_to(CABLE_REL, CABLE_BBOX)

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    report = {"backup": str(bak), "crops": {"11583": swing_crop, "11584": cable_crop}, "db": []}

    plan = [
        (SWING_ID, SECTOR, swing_crop, "vocational_math_B2_1-2_advanced_exercise_009_030"),
        (CABLE_ID, ACUTE, cable_crop, "vocational_math_B2_1-2_advanced_exercise_010_031"),
    ]
    for te_id, new_skill, crop, anchor in plan:
        row = con.execute(
            "SELECT id, skill_id, notes FROM textbook_examples WHERE id=?", (te_id,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"missing TE {te_id}")
        old_skill = row["skill_id"]
        notes = upsert_asset(parse_notes(row["notes"]), te_id=te_id, crop=crop, anchor_id=anchor)
        con.execute(
            "UPDATE textbook_examples SET skill_id=?, notes=? WHERE id=?",
            (new_skill, json.dumps(notes, ensure_ascii=False, sort_keys=True), te_id),
        )
        report["db"].append(
            {
                "id": te_id,
                "old_skill_id": old_skill,
                "new_skill_id": new_skill,
                "asset_sha256": crop["sha256"],
                "bbox": crop["bbox"],
            }
        )

    con.commit()
    con.close()

    out = ROOT / "reports" / "b2_p1_swing_cable_visual" / "repair_db_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
