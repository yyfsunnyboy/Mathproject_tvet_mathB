"""普高數學1 Unit 5 Stage 1 局部修復（只改 id 12403-12448 的指定列，不重新匯入）。

證據來源：uploaded_sources 內已驗證雜湊的 DOCX / PDF。每項修復都有 PDF 頁碼與 bbox。
先備份 DB 再於單一 transaction 寫入；可重跑（idempotent）。
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
PDF = ROOT / "textbook_import/uploaded_sources/general/數學1/c1b9452d216e_單元05-直線方程式.pdf"
PDF_SHA = "c1b9452d216e10b03cad75be0f055a79dd70d34c08de0134d0901d1a2a43a3bd"
ASSET_DIR = "uploads/question_assets/general/longteng/數學1/ch_unknown_單元5_直線方程式/sec_unknown_5直線方程式"
REVIEWED_AT = datetime.now().strftime("%Y-%m-%d")

# row id -> (pdf page, bbox pt, why)
IMAGE_FIXES = {
    12421: (20, [368, 274, 520, 440], "recrop: original crop clipped the (34,5) label, dimension arrows and axis labels"),
    12436: (28, [392, 372, 538, 508], "recrop: original crop clipped the L1 label and axes"),
    12416: (13, [420, 528, 520, 625], "missing figure (A, B, L with right-angle mark)"),
    12417: (15, [392, 565, 518, 652], "missing figure (S, A, B points and line SA)"),
    12430: (27, [398, 292, 520, 414], "missing figure (shaded region of the inequality system)"),
    12443: (29, [392, 468, 534, 592], "missing figure (shaded triangle O, A(2,6), B(5,0))"),
    12448: (30, [370, 518, 532, 678], "missing figure (parallel lines L1..Ln, points A, B, P)"),
}

# truncated / lost stems (DOCX paragraphs 205-206, 472 and PDF page 8 table)
TEXT_FIXES = {
    12416: ("\n點 \\(B\\left ( { 5,\\ 3 } \\right )\\) 為 \\(L\\) 外一點，使得 \\({\\overline{ AB }}\\bot L\\)，求 \\(a,\\ c\\) 的值。", "append"),
    12443: ("\n的解區域，求 \\(a,\\ b,\\ c\\)。", "append"),
    12410: (
        "在下列的表格中填入適當的答案：\n"
        "| 直線的方程式 | 斜率 | *x*截距 | *y*截距 |\n| --- | --- | --- | --- |\n"
        "| \\(2x+y-4=0\\) |  |  |  |\n"
        "|  | \\(3\\) |  | \\(-2\\) |\n"
        "|  | \\(-2\\) | \\(3\\) |  |",
        "replace",
    ),
}

PARAGRAPH = {
    "gh_LineSlope": "直線的斜率", "gh_EquationOfALine": "直線方程式", "gh_TranslationOfALine": "直線的平移",
    "gh_ParallelAndPerpendicularLines": "直線的平行與垂直", "gh_DistanceFromPointToLine": "點到直線的距離",
    "gh_LinearInequalityInTwoVariables": "二元一次不等式",
}
# 習題（含觀念澄清）依題目數學內容重新歸屬；原本 18 題全部落在最後一個 heading 的 Skill。
EXERCISE_BINDING = {
    12431: ("gh_ParallelAndPerpendicularLines", "矩形對邊平行→斜率相等"),
    12432: ("gh_EquationOfALine", "y 截距定義"),
    12433: ("gh_ParallelAndPerpendicularLines", "兩直線垂直判定"),
    12434: ("gh_DistanceFromPointToLine", "與已知直線平行且距離為定值的直線"),
    12435: ("gh_LinearInequalityInTwoVariables", "點與直線的相對側（半平面）"),
    12436: ("gh_LineSlope", "由圖比較斜率"),
    12437: ("gh_EquationOfALine", "求直線方程式"),
    12438: ("gh_TranslationOfALine", "直線平移"),
    12439: ("gh_ParallelAndPerpendicularLines", "兩直線互相垂直"),
    12440: ("gh_ParallelAndPerpendicularLines", "外心(中垂線)與垂心(高)"),
    12441: ("gh_LinearInequalityInTwoVariables", "半平面"),
    12442: ("gh_LinearInequalityInTwoVariables", "圖示聯立不等式"),
    12443: ("gh_LinearInequalityInTwoVariables", "由圖求聯立不等式係數"),
    12444: ("gh_ParallelAndPerpendicularLines", "對角線互相垂直"),
    12445: ("gh_EquationOfALine", "由截距與面積求直線"),
    12446: ("gh_ParallelAndPerpendicularLines", "對稱點與最短路徑"),
    12447: ("gh_LinearInequalityInTwoVariables", "圖示聯立不等式與格子點"),
    12448: ("gh_DistanceFromPointToLine", "平行線間距與點到直線距離"),
}


def _safe(label: str, bracket: str) -> str:
    bracket = bracket.replace("=", "").replace(" | ", "_").replace("|", "_").replace(" ", "")
    return f"{label}_{bracket}"


def main() -> None:
    dry = "--dry" in sys.argv
    if not dry:
        backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit5_stage1_{datetime.now():%Y%m%d_%H%M%S}.db"
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
        for rid, (page, bbox, why) in IMAGE_FIXES.items():
            row = con.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(row["notes"])
            m = re.match(r"^(.*?)\s*\[(.*)\]\s*$", row["source_description"])
            label, bracket = m.group(1), m.group(2)
            old = [a for a in notes.get("image_assets", []) if a.get("source") == "pdf"]
            rel = old[0]["path"] if old else f"{ASSET_DIR}/{row['problem_type']}_{_safe(label, bracket)}_general__fig1.png"
            meta = crop_pdf_bbox(PDF, page, bbox, ROOT / rel, dpi=200, pad_pt=2)
            asset = build_pdf_visual_asset_record(
                rel_path=rel, page_1based=page, bbox=bbox, classification="required", visual_type="diagram",
                match_method="manual_pdf_review", match_score=1.0, reason=why, image_meta=meta,
                anchor_id=notes["question_anchor"]["anchor_id"],
            )
            upsert_notes_image_asset(notes, asset)
            notes["visual_required_missing"] = False
            notes["needs_review"] = False
            notes.pop("image_warning", None)
            notes["image_warning_resolved_by"] = "manual_pdf_review"
            notes["pdf_visual_status"] = "VISUAL_ATTACHED"
            notes["manual_visual_review"] = {
                "date": REVIEWED_AT, "source_pdf_sha256": PDF_SHA, "page": page, "bbox": bbox,
                "result": "figure verified against PDF page image", "reason": why, "crop_sha256": meta["sha256"],
            }
            report.append({"id": rid, "fix": "image", "page": page, "sha256": meta["sha256"], "why": why})
            con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), rid))
        for rid, (text, mode) in TEXT_FIXES.items():
            row = con.execute("select problem_text, notes from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(row["notes"])
            if mode == "append" and text.strip() in row["problem_text"]:
                continue
            new_text = row["problem_text"].rstrip() + text if mode == "append" else text
            notes.setdefault("repair_log", []).append(f"{REVIEWED_AT} manual Stage1 repair: stem restored from DOCX/PDF ({mode})")
            if rid == 12410:
                notes["needs_table_review"] = False
                notes["needs_review"] = False
                notes["pdf_visual_status"] = "NO_VISUAL_REQUIRED"
                notes["visual_required_missing"] = False
                notes["has_image"] = False
                notes.pop("image_warning", None)
                notes["table_source"] = {"pdf_page": 8, "sha256": PDF_SHA, "table": "3 rows x 4 cols (equation, slope, x-intercept, y-intercept)"}
            con.execute("update textbook_examples set problem_text=?, notes=? where id=?", (new_text, json.dumps(notes, ensure_ascii=False), rid))
            report.append({"id": rid, "fix": "text", "mode": mode})
        for rid, (skill, why) in EXERCISE_BINDING.items():
            row = con.execute("select skill_id, notes from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(row["notes"])
            if row["skill_id"] == skill:
                continue
            notes["skill_binding"] = {"source": "manual_topic_audit_unit5", "previous_skill_id": row["skill_id"], "basis": why, "date": REVIEWED_AT}
            con.execute("update textbook_examples set skill_id=?, source_paragraph=?, notes=? where id=?",
                        (skill, PARAGRAPH[skill], json.dumps(notes, ensure_ascii=False), rid))
            report.append({"id": rid, "fix": "rebind", "to": skill})
        con.execute("rollback" if dry else "commit")
    except Exception:
        con.execute("rollback")
        raise
    if not dry:
        out = ROOT / "reports" / "gh_unit5_stage1" / "stage1_repair_log.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(report), "changes")


if __name__ == "__main__":
    main()
