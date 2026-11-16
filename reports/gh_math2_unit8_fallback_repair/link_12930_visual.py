"""Link 隨堂練習10 (12930) to the already-verified 例題9 (12926) bar-chart crop.

    python reports/gh_math2_unit8_fallback_repair/link_12930_visual.py                       # dry run on the formal DB (read-only)
    python reports/gh_math2_unit8_fallback_repair/link_12930_visual.py --db COPY.db --apply  # write into an isolated DB copy
    python reports/gh_math2_unit8_fallback_repair/link_12930_visual.py --apply --confirm-formal  # formal DB: online backup first

12930 reads "承例題9，…哪一科的前標比較高？": it needs the two grade-distribution bar charts of 例題9.  Source evidence:
the DOCX 隨堂練習10 paragraph and the PDF page 18 block carry no picture (only the page decoration); the charts exist once,
on PDF page 17, verified for 12926 (configs/stage1_verified_visual_regions.json, 例題9).  The existing crop file is reused
as is (no re-crop, no copy); only 12930's notes change.  12930's problem_text, skill binding, anchor and source provenance
are kept; the previous values of every changed notes key are stored under notes.visual_repair.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMAL_DB = ROOT / "instance" / "kumon_math.db"
SOURCE_ID, TARGET_ID = 12926, 12930
CROP_SHA256 = "0c6de2758ff8d4ad9136544e0ecaf533212add33eded56d05d983a27bffbb5c5"
TARGET_STEM_SHA256 = hashlib.sha256("承例題9，成績位於第 \\(75\\) 百分位數的考生級分稱為前標，試問哪一科的前標比較高？".encode("utf-8")).hexdigest()
TARGET_ANCHOR = "general_2_section_in_class_practice_010_019"
REASON = ("隨堂練習10「承例題9」須用例題9的兩科級分分布長條圖；DOCX 隨堂練習10 段落與 PDF p.18 題框皆無題圖，"
          "長條圖僅在 PDF p.17 例題9（已人工驗證區域），故沿用 12926 的同一 crop，不重新擷取")
CHANGED_KEYS = ("image_assets", "has_image", "needs_image", "image_role", "image_dependency_reason", "visual_status",
                "pdf_visual_status", "needs_image_review")


def _stem_sha(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def plan(conn: sqlite3.Connection) -> dict:
    """The new notes for 12930, after checking every precondition (raises AssertionError otherwise)."""
    rows = {r[0]: r for r in conn.execute(
        "select id, skill_id, problem_text, notes from textbook_examples where id in (?, ?)", (SOURCE_ID, TARGET_ID))}
    assert set(rows) == {SOURCE_ID, TARGET_ID}, "rows missing"
    source_notes, target_notes = json.loads(rows[SOURCE_ID][3]), json.loads(rows[TARGET_ID][3])
    assets = [a for a in source_notes.get("image_assets") or [] if isinstance(a, dict)]
    assert len(assets) == 1 and assets[0].get("sha256") == CROP_SHA256 and assets[0].get("visual_status") == "accepted", "12926 crop changed"
    crop = ROOT / assets[0]["path"]
    assert crop.is_file() and hashlib.sha256(crop.read_bytes()).hexdigest() == CROP_SHA256, "crop file missing or changed"
    assert _stem_sha(rows[TARGET_ID][2]) == TARGET_STEM_SHA256, "12930 stem changed"
    assert (target_notes.get("question_anchor") or {}).get("anchor_id") == TARGET_ANCHOR, "12930 anchor changed"
    assert rows[TARGET_ID][1] == "gh_VarianceAndStandardDeviation", "12930 skill binding changed"
    if target_notes.get("visual_repair", {}).get("shared_from_textbook_example_id") == SOURCE_ID:
        return {"already_applied": True, "notes": target_notes}
    assert not target_notes.get("image_assets"), "12930 already has other image assets"

    asset = copy.deepcopy(assets[0])
    asset.update({"shared_from_textbook_example_id": SOURCE_ID, "linked_question_anchor": TARGET_ANCHOR, "shared_reason": REASON})
    new_notes = dict(target_notes)
    new_notes.update({"image_assets": [asset], "has_image": True, "needs_image": True, "image_role": "required_diagram",
                      "image_dependency_reason": "cross_reference_to_example_9_figure", "visual_status": "accepted",
                      "pdf_visual_status": "VISUAL_ATTACHED", "needs_image_review": False})
    new_notes["visual_repair"] = {
        "repaired_by": "math2_unit8_fallback_p0a_link_12930_visual",
        "shared_from_textbook_example_id": SOURCE_ID,
        "crop_sha256": CROP_SHA256,
        "evidence": "DOCX 隨堂練習10 無圖；PDF p.18 題框無圖；PDF p.17 例題9 region (110,179,515,282) verified",
        "reason": REASON,
        "previous": {k: target_notes.get(k) for k in CHANGED_KEYS},
    }
    return {"already_applied": False, "notes": new_notes}


def apply(conn: sqlite3.Connection) -> dict:
    """Write the plan in one transaction; every other row and column stays as it was."""
    result = plan(conn)
    if result["already_applied"]:
        return result
    other = "select count(*), sum(length(coalesce(notes,''))), sum(length(coalesce(problem_text,''))) from textbook_examples where id <> ?"
    before = conn.execute(other, (TARGET_ID,)).fetchone()
    target_before = conn.execute("select skill_id, problem_text, correct_answer, detailed_solution from textbook_examples where id=?", (TARGET_ID,)).fetchone()
    with conn:
        conn.execute("update textbook_examples set notes=? where id=?", (json.dumps(result["notes"], ensure_ascii=False), TARGET_ID))
    assert conn.execute(other, (TARGET_ID,)).fetchone() == before
    assert conn.execute("select skill_id, problem_text, correct_answer, detailed_solution from textbook_examples where id=?", (TARGET_ID,)).fetchone() == target_before
    return result


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    target = Path(args[args.index("--db") + 1]).resolve() if "--db" in args else FORMAL_DB
    formal = target == FORMAL_DB.resolve()
    write = "--apply" in args
    if write and formal and "--confirm-formal" not in args:
        raise SystemExit("formal DB: add --confirm-formal (requires owner approval)")
    conn = sqlite3.connect(f"file:{target.as_posix()}?mode=ro", uri=True) if not write else sqlite3.connect(target, timeout=60)
    if not write:
        result = plan(conn)
        print(json.dumps({"db": str(target), "dry_run": True, "already_applied": result["already_applied"],
                          "image_assets": result["notes"].get("image_assets")}, ensure_ascii=False, indent=1))
        return
    if formal:
        backup = ROOT / "backups" / "math2_unit8_fallback_repair" / time.strftime("%Y%m%d_%H%M%S")
        backup.mkdir(parents=True)
        dst = sqlite3.connect(backup / "kumon_math.db")
        conn.backup(dst)
        assert dst.execute("pragma integrity_check").fetchone()[0] == "ok"
        dst.close()
        print("backup", backup)
    result = apply(conn)
    print(json.dumps({"db": str(target), "applied": not result["already_applied"], "already_applied": result["already_applied"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
