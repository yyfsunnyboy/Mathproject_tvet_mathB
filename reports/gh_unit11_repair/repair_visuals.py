"""Link PDF figures to the five Unit 11 questions whose required figure was not imported
(12635, 12640, 12650, 12663, 12666).

    python reports/gh_unit11_repair/repair_visuals.py            # dry run
    python reports/gh_unit11_repair/repair_visuals.py --apply    # DB backup, write PNGs, update only these five rows
"""
from __future__ import annotations

import glob
import json
import re
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from core.textbook_pdf_visual import build_pdf_visual_asset_record, crop_pdf_bbox, fingerprint_file, upsert_notes_image_asset  # noqa: E402

PDF = glob.glob(str(ROOT / "textbook_import/uploaded_sources/general/數學1/*單元11*.pdf"))[0]
PDF_SHA256_PREFIX = "bdad0e5945f1"
REGIONS = {  # question id -> (pdf page, bbox in PDF points, description); read off the rendered pages
    12635: (7, [390, 280, 516, 420], "inscribed rectangle in the triangular leather (stem figure)"),
    12640: (14, [438, 154, 518, 257], "cuboid frame with edges x, x, y"),
    12650: (15, [336, 338, 523, 419], "triangular prism frame with edges 3x, 4x, 5x, y"),
    12663: (17, [438, 548, 531, 650], "rectangular plot with a path of equal width, sides 10 and 12"),
    12666: (18, [444, 458, 527, 577], "open cuboid box with edges x, x, y"),
}
DB = ROOT / "instance" / "kumon_math.db"
ASSET_DIR = Path("uploads/question_assets/general/longteng/數學1/ch_unknown_單元11_多項式不等式/sec_unknown_11多項式不等式")
APPLY = "--apply" in sys.argv


def main() -> None:
    assert fingerprint_file(Path(PDF)).startswith(PDF_SHA256_PREFIX), "PDF differs from the imported source"
    conn = sqlite3.connect(DB, timeout=60)
    conn.row_factory = sqlite3.Row
    rows = {r["id"]: r for r in conn.execute(f"select * from textbook_examples where id in ({','.join(map(str, REGIONS))})")}
    assert set(rows) == set(REGIONS)
    if APPLY:
        backup = ROOT / "backups" / "unit11_visual_repair" / time.strftime("%Y%m%d_%H%M%S")
        backup.mkdir(parents=True)
        dst = sqlite3.connect(backup / "kumon_math.db")
        conn.backup(dst)
        ok = dst.execute("pragma integrity_check").fetchone()[0]
        n = dst.execute("select count(*) from textbook_examples").fetchone()[0]
        dst.close()
        print("backup", backup, "integrity", ok, "rows", n)
        assert ok == "ok"
    out_root = ROOT if APPLY else Path(tempfile.mkdtemp(prefix="u11_dry_"))
    plan = []
    for qid, (page, bbox, why) in REGIONS.items():
        row = rows[qid]
        notes = json.loads(row["notes"])
        desc = row["source_description"]
        anchor = notes.get("question_anchor")
        if not anchor:  # the importer attaches an anchor only when the PDF matched; record the identity that is certain
            qtype = {"例題": "example", "隨堂練習": "in_class_practice", "進階題": "advanced_exercise"}[re.search(r"(例題|隨堂練習|進階題)", desc).group(1)]
            number = re.search(r"(\d+)\s*\[", desc).group(1)
            stype = re.search(r"source_type=(\w+)", desc).group(1)
            anchor = {"anchor_id": f"general_1_section_{qtype}_{int(number):03d}_manual", "curriculum": "general", "publisher": "longteng",
                      "volume": "數學1", "chapter": "11", "section": "", "question_type": qtype, "question_number": number,
                      "question_label": desc.split(" [")[0], "source_type": stype, "source_order": None, "added_by": "unit11_visual_repair"}
            notes["question_anchor"] = anchor
        dedupe = re.search(r"dedupe=([0-9a-f]+)", desc).group(1)
        label = desc.split(" [")[0].replace(" ", "")
        rel = ASSET_DIR / f"{anchor['question_type']}_{label}_source_type{anchor['source_type']}_dedupe{dedupe}_general__fig1.png"
        meta = crop_pdf_bbox(PDF, page, bbox, out_root / rel, dpi=200)
        asset = build_pdf_visual_asset_record(rel_path=rel.as_posix(), page_1based=page, bbox=bbox, classification="required", visual_type="diagram",
                                              match_method="manual_page_region", match_score=1.0, reason=f"verified_pdf_region: {why}",
                                              image_meta=meta, anchor_id=anchor["anchor_id"])
        notes["image_assets"] = []
        upsert_notes_image_asset(notes, asset)
        notes.update({"has_image": True, "needs_image": True, "image_role": "required_diagram", "needs_review": False,
                      "image_dependency_reason": "figure_required_by_stem_verified_against_pdf", "needs_review_before_visual": False,
                      "visual_required_missing": False, "needs_image_review": False, "visual_status": "accepted",
                      "image_warning_resolved_by": "pdf_visual", "pdf_visual_status": "VISUAL_ATTACHED"})
        notes.pop("image_warning", None)
        notes["pdf_visual_enrichment"] = {**(notes.get("pdf_visual_enrichment") or {}), "result": "mounted", "classification": "required",
                                          "match_method": "manual_page_region", "match_score": 1.0, "page": page, "visual_bbox": bbox}
        plan.append((json.dumps(notes, ensure_ascii=False), qid))
        print(qid, "page", page, rel.name[:40])
    if APPLY:
        with conn:
            for n, q in plan:
                conn.execute("update textbook_examples set notes=? where id=?", (n, q))
        print("updated", len(plan))
    else:
        print("dry run; crops in", out_root)


if __name__ == "__main__":
    main()
