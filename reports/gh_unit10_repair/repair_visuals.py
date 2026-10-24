"""Link PDF figures to the six Unit 10 BLOCKER questions (12609, 12610, 12611, 12621, 12626, 12628).

    python reports/gh_unit10_repair/repair_visuals.py            # dry run: crops to a temp dir, prints the DB plan
    python reports/gh_unit10_repair/repair_visuals.py --apply    # backup, write PNGs, update only these six rows

Only ``textbook_examples.notes`` (image fields) of the six rows - and ``problem_text`` of 12621 - are written.
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

from regions import PDF, PDF_SHA256, REGIONS  # noqa: E402
from core.textbook_pdf_visual import build_pdf_visual_asset_record, crop_pdf_bbox, fingerprint_file, upsert_notes_image_asset  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
ASSET_DIR = Path("uploads/question_assets/general/longteng/數學1/ch_unknown_單元10_三次函數的圖形特徵/sec_unknown_10三次函數的圖形特徵")
APPLY = "--apply" in sys.argv
STEM_FIX = {12621: ("，", "\n比較 \(a_{ 1 }\), \(a_{ 2 }\), \(a_{ 3 }\) 的大小關係。")}  # DOCX paragraph: "…，\n比較a1,a2,a3的大小關係。"


def main() -> None:
    assert fingerprint_file(ROOT / PDF) == PDF_SHA256, "PDF differs from the imported source"
    conn = sqlite3.connect(DB, timeout=60)
    conn.row_factory = sqlite3.Row
    rows = {r["id"]: r for r in conn.execute(f"select * from textbook_examples where id in ({','.join(map(str, REGIONS))})")}
    assert set(rows) == set(REGIONS) and all(r["skill_id"] == "gh_GraphsOfCubicFunctions" for r in rows.values())
    if APPLY:
        backup = ROOT / "backups" / "unit10_visual_repair" / time.strftime("%Y%m%d_%H%M%S")
        backup.mkdir(parents=True)
        dst = sqlite3.connect(backup / "kumon_math.db")
        conn.backup(dst)
        ok = dst.execute("pragma integrity_check").fetchone()[0]
        before = dst.execute("select count(*) from textbook_examples").fetchone()[0]
        dst.close()
        print("backup", backup, "integrity", ok, "rows", before)
        assert ok == "ok"
    out_root = ROOT if APPLY else Path(tempfile.mkdtemp(prefix="u10_dry_"))
    plan = []
    for qid, regions in REGIONS.items():
        row = rows[qid]
        notes = json.loads(row["notes"])
        anchor = notes["question_anchor"]
        desc = row["source_description"]
        dedupe = re.search(r"dedupe=([0-9a-f]+)", desc).group(1)
        label = desc.split(" [")[0].replace(" ", "")
        qtype = anchor["question_type"]
        notes["image_assets"] = []
        for slot, page, bbox, why in regions:
            fig = slot[-2:].lstrip("0")
            rel = ASSET_DIR / f"{qtype}_{label}_source_type{anchor['source_type']}_dedupe{dedupe}_general__fig{fig}.png"
            meta = crop_pdf_bbox(ROOT / PDF, page, bbox, out_root / rel, dpi=200)
            asset = build_pdf_visual_asset_record(
                rel_path=rel.as_posix(), page_1based=page, bbox=bbox, classification="required", visual_type="diagram",
                match_method="manual_page_region", match_score=1.0, reason=f"verified_pdf_region: {why}", image_meta=meta,
                anchor_id=anchor["anchor_id"], asset_slot=slot)
            upsert_notes_image_asset(notes, asset, slot=slot)
        notes.update({"has_image": True, "needs_image": True, "image_role": "required_diagram", "needs_review": False,
                      "image_dependency_reason": "figure_required_by_stem_verified_against_pdf", "needs_review_before_visual": False,
                      "visual_required_missing": False, "needs_image_review": False, "visual_status": "accepted",
                      "image_warning_resolved_by": "pdf_visual", "pdf_visual_status": "VISUAL_ATTACHED"})
        notes.pop("image_warning", None)
        enrich = dict(notes.get("pdf_visual_enrichment") or {})
        enrich.update({"result": "mounted", "classification": "required", "match_method": "manual_page_region", "match_score": 1.0,
                       "page": regions[0][1], "page_source": "manual_verified", "visual_bbox": regions[0][2], "visual_reason": "manual_verified_region"})
        notes["pdf_visual_enrichment"] = enrich
        text = row["problem_text"]
        if qid in STEM_FIX:
            tail, add = STEM_FIX[qid]
            assert text.rstrip().endswith(tail), repr(text[-20:])
            text = text.rstrip() + add
        plan.append((qid, text, json.dumps(notes, ensure_ascii=False), len(regions)))
        print(qid, "assets", len(regions), "| stem tail:", repr(text[-40:]))
    if APPLY:
        with conn:
            for qid, text, notes_json, _ in plan:
                conn.execute("update textbook_examples set problem_text=?, notes=? where id=?", (text, notes_json, qid))
        print("updated", len(plan))
    else:
        print("dry run only; crops in", out_root)


if __name__ == "__main__":
    main()
