"""Unit 10 Stage 1 closing repair: 12608 flight-path figure, 12615 / 12616 review flags.

    python reports/gh_unit10_stage1/stage1_repair.py          # dry run
    python reports/gh_unit10_stage1/stage1_repair.py --apply  # backup + update exactly these three rows
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports" / "gh_unit10_repair"))
sys.stdout.reconfigure(encoding="utf-8")

from regions import PDF, PDF_SHA256  # noqa: E402
from core.textbook_pdf_visual import build_pdf_visual_asset_record, crop_pdf_bbox, fingerprint_file, upsert_notes_image_asset  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
APPLY = "--apply" in sys.argv
ASSET = Path("uploads/question_assets/general/longteng/數學1/ch_unknown_單元10_三次函數的圖形特徵/sec_unknown_10三次函數的圖形特徵/example_例題6_source_typetextbook_example_dedupe{d}_general__fig1.png")
BBOX_12608 = [358, 490, 512, 583]  # PDF p.9 例題6 flight-path figure (起飛點 O, (2,1), 起降點)
NOTE = "stem compared line by line with DOCX paragraph text (and PDF page); identical apart from formula spacing"


def main() -> None:
    assert fingerprint_file(ROOT / PDF) == PDF_SHA256
    conn = sqlite3.connect(DB, timeout=60)
    if APPLY:
        backup = ROOT / "backups" / "unit10_stage1" / time.strftime("%Y%m%d_%H%M%S")
        backup.mkdir(parents=True)
        dst = sqlite3.connect(backup / "kumon_math.db")
        conn.backup(dst)
        assert dst.execute("pragma integrity_check").fetchone()[0] == "ok"
        dst.close()
        print("backup", backup)
    updates = []
    for qid in (12608, 12615, 12616):
        row = conn.execute("select notes, source_description from textbook_examples where id=?", (qid,)).fetchone()
        notes = json.loads(row[0])
        if qid == 12608:
            import re
            dedupe = re.search(r"dedupe=([0-9a-f]+)", row[1]).group(1)
            rel = Path(str(ASSET).format(d=dedupe))
            meta = crop_pdf_bbox(ROOT / PDF, 9, BBOX_12608, (ROOT if APPLY else Path(tempfile.mkdtemp())) / rel, dpi=200)
            asset = build_pdf_visual_asset_record(rel_path=rel.as_posix(), page_1based=9, bbox=BBOX_12608, classification="required", visual_type="diagram",
                                                  match_method="manual_page_region", match_score=1.0, reason="verified_pdf_region: flight path figure",
                                                  image_meta=meta, anchor_id=notes["question_anchor"]["anchor_id"])
            notes["image_assets"] = []
            upsert_notes_image_asset(notes, asset)
            notes.update({"needs_image": True, "image_role": "required_diagram", "needs_review_before_visual": False, "visual_required_missing": False,
                          "needs_image_review": False, "visual_status": "accepted", "image_warning_resolved_by": "pdf_visual", "pdf_visual_status": "VISUAL_ATTACHED"})
            notes.pop("image_warning", None)
            notes["pdf_visual_enrichment"] = {**(notes.get("pdf_visual_enrichment") or {}), "result": "mounted", "classification": "required",
                                              "match_method": "manual_page_region", "match_score": 1.0, "page": 9, "visual_bbox": BBOX_12608}
        else:
            notes["manual_stem_review"] = NOTE
            notes["review_required_by_confidence"] = False
        notes["needs_review"] = False
        updates.append((json.dumps(notes, ensure_ascii=False), qid))
        print(qid, "ready")
    if APPLY:
        with conn:
            for n, q in updates:
                conn.execute("update textbook_examples set notes=? where id=?", (n, q))
        print("updated", len(updates))
    else:
        print("dry run")


if __name__ == "__main__":
    main()
