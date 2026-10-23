"""普高數學1 Unit 8 Stage 1 局部修復（只改 id 12537/12552/12518/12519，不重新匯入）。

證據來源：uploaded_sources 內已驗證雜湊的 DOCX / PDF。先備份 DB，單一 transaction 寫入；可重跑。
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.textbook_pdf_visual import build_pdf_visual_asset_record, crop_pdf_bbox, upsert_notes_image_asset  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學1/f48be281b155_單元08-多項式的除法原理.pdf"
PDF_SHA = "f48be281b1552afdb42f4c8577b9169f56e8d5a31e5c7c403117cc44c624a3c0"
ASSET_DIR = "uploads/question_assets/general/longteng/數學1/ch_unknown_單元8_多項式的除法原理/sec_unknown_8多項式的除法原理"
REVIEWED_AT = datetime.now().strftime("%Y-%m-%d")

IMG_ID, IMG_PAGE, IMG_BBOX = 12552, 16, [348, 565, 515, 670]
IMG_WHY = "missing figure (blackboard: 因式分解 x^3+3x^2-4x with erased constant term)"

Q14_TAIL = "\n求實數 a, b, c, d 的值。\n(2)求 \\(f\\left ( { 0.505 } \\right )\\) 的近似值到小數點以下第二位（第三位四捨五入）。"
REBIND = {
    12518: ("gh_RemainderTheorem", "餘式定理", "f(x)=(x-2)q(x)+(x+1) 除以 x-2 的餘式判斷"),
    12519: ("gh_FactorTheorem", "因式定理", "x^5+1 是否可被 x+1 整除（因式定理）"),
}


def main() -> None:
    dry = "--dry" in sys.argv
    if not dry:
        backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit8_stage1_{datetime.now():%Y%m%d_%H%M%S}.db"
        src = sqlite3.connect(DB)
        dst = sqlite3.connect(backup)
        src.backup(dst)
        dst.close()
        src.close()
        print("backup:", backup.name)
    con = sqlite3.connect(DB, isolation_level=None)
    con.row_factory = sqlite3.Row
    report = []
    try:
        con.execute("begin")
        row = con.execute("select * from textbook_examples where id=?", (IMG_ID,)).fetchone()
        notes = json.loads(row["notes"])
        m = re.match(r"^(.*?)\s*\[(.*)\]\s*$", row["source_description"])
        label, bracket = m.group(1), m.group(2)
        safe = f"{label}_" + bracket.replace("=", "").replace(" | ", "_").replace("|", "_").replace(" ", "")
        rel = f"{ASSET_DIR}/{row['problem_type']}_{safe}_general__fig1.png"
        meta = crop_pdf_bbox(PDF, IMG_PAGE, IMG_BBOX, ROOT / rel, dpi=200, pad_pt=2)
        asset = build_pdf_visual_asset_record(
            rel_path=rel, page_1based=IMG_PAGE, bbox=IMG_BBOX, classification="required", visual_type="diagram",
            match_method="manual_pdf_review", match_score=1.0, reason=IMG_WHY, image_meta=meta,
            anchor_id=notes["question_anchor"]["anchor_id"],
        )
        upsert_notes_image_asset(notes, asset)
        notes["has_image"] = True
        notes["visual_required_missing"] = False
        notes["needs_review"] = False
        notes.pop("image_warning", None)
        notes["image_warning_resolved_by"] = "manual_pdf_review"
        notes["pdf_visual_status"] = "VISUAL_ATTACHED"
        notes["manual_visual_review"] = {
            "date": REVIEWED_AT, "source_pdf_sha256": PDF_SHA, "page": IMG_PAGE, "bbox": IMG_BBOX,
            "result": "figure verified against PDF page image", "reason": IMG_WHY, "crop_sha256": meta["sha256"],
        }
        notes.setdefault("repair_log", []).append(f"{REVIEWED_AT} manual Stage1 repair (unit8): figure attached from PDF p.{IMG_PAGE}")
        con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), IMG_ID))
        report.append({"id": IMG_ID, "fix": "image", "page": IMG_PAGE, "sha256": meta["sha256"]})

        row = con.execute("select problem_text, notes from textbook_examples where id=12537").fetchone()
        if "0.505" not in row["problem_text"]:
            notes = json.loads(row["notes"])
            notes.setdefault("repair_log", []).append(f"{REVIEWED_AT} manual Stage1 repair (unit8): restored (1) tail and (2) from DOCX/PDF p.20")
            con.execute("update textbook_examples set problem_text=?, notes=? where id=12537",
                        (row["problem_text"].rstrip() + Q14_TAIL, json.dumps(notes, ensure_ascii=False)))
            report.append({"id": 12537, "fix": "stem (2) restored"})

        for rid, (skill, para, why) in REBIND.items():
            row = con.execute("select skill_id, notes from textbook_examples where id=?", (rid,)).fetchone()
            if row["skill_id"] == skill:
                continue
            notes = json.loads(row["notes"])
            notes["needs_review"] = False
            notes["review_required_by_confidence"] = False
            notes["skill_binding"] = {"source": "manual_topic_audit_unit8", "previous_skill_id": row["skill_id"], "basis": why, "date": REVIEWED_AT}
            con.execute("update textbook_examples set skill_id=?, source_paragraph=?, notes=? where id=?",
                        (skill, para, json.dumps(notes, ensure_ascii=False), rid))
            report.append({"id": rid, "fix": "rebind", "to": skill})
        con.execute("rollback" if dry else "commit")
    except Exception:
        con.execute("rollback")
        raise
    if not dry:
        (ROOT / "reports" / "gh_unit8_stage1" / "stage1_repair_log.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(report), "changes")


if __name__ == "__main__":
    main()
