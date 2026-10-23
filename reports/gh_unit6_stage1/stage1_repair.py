"""普高數學1 Unit 6 Stage 1 局部修復（只改 id 12449-12480 的指定列，不重新匯入）。

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
PDF = ROOT / "textbook_import/uploaded_sources/general/數學1/b52f3a355f19_單元06-圓方程式.pdf"
PDF_SHA = "b52f3a355f195db188d2b1f0192c08e126b55498588d053c0624131c200ddb13"
ASSET_DIR = "uploads/question_assets/general/longteng/數學1/ch_unknown_單元6_圓方程式/sec_unknown_6圓方程式"
REVIEWED_AT = datetime.now().strftime("%Y-%m-%d")

# row id -> (pdf page, bbox pt, why)
IMAGE_FIXES = {
    12457: (8, [372, 544, 516, 638], "missing figure (compass, A/B garbage stations on the road, incinerator P)"),
    12466: (12, [394, 176, 518, 270], "recrop: original crop was 600x1338 and covered the stem/options instead of the Mohr-circle figure"),
    12478: (15, [110, 482, 510, 574], "missing news-report box (typhoon centre 460 km south of Kinmen, storm radius 80 km, speed 25 km/h)"),
    12480: (16, [420, 296, 528, 392], "missing figure (arch with Q, A, P, B, R and the two posts)"),
}

NEWS = ("天天日報【臺北報導】中央氣象局觀測，米克拉颱風下午 \\(3\\) 時的中心位於金門正南方 \\(460\\) 公里的海面上，"
        "其暴風半徑為 \\(80\\) 公里，並以每小時 \\(25\\) 公里的速度朝正北方直線前進。\n")

EX10_SOLUTION_TAIL = (
    "\n將\\(\\o\\ac(○,3)\\)分別對x, y配方，得 \\(\\left ( { x+1 } \\right ) ^ { 2 } +y ^ { 2 } =6\\)，其圓心為\\(\\left ( { -1,0 } \\right )\\)，在x軸上。"
    "\n將\\(\\o\\ac(○,4)\\)分別對x, y配方，得 \\(\\left ( { x-1 } \\right ) ^ { 2 } +y ^ { 2 } =-4\\)，其圖形不存在。"
    "\n因為莫爾圓的圓心必須在x軸上，所以選\\(\\o\\ac(○,3)\\)。"
    "\n(2)因為\\({\\overline{ AB }}\\)是直徑，所以\\({\\overline{ AB }}\\)的中點\\(\\left ( { 3,0 } \\right )\\)即為圓心。由半徑的長度為"
    "\\(\\frac { 1 } { 2 } {\\overline{ AB }} =\\frac { 1 } { 2 }\\sqrt[] { \\left ( { 1-5 } \\right ) ^ { 2 } +\\left ( { 2-\\left ( { -2 } \\right ) } \\right ) ^ { 2 } }=2\\sqrt[] { 2 }\\)，"
    "可得莫爾圓方程式為\\(\\left ( { x-3 } \\right ) ^ { 2 } +y ^ { 2 } =8\\)。"
    "\n(3)將三個莫爾圓方程式分別對x, y配方，得 \\(\\left ( { x-6 } \\right ) ^ { 2 } +y ^ { 2 } =25\\)、\\(\\left ( { x-3 } \\right ) ^ { 2 } +y ^ { 2 } =4\\)、\\(\\left ( { x-8 } \\right ) ^ { 2 } +y ^ { 2 } =9\\)，"
    "並將其畫在坐標平面上。大莫爾圓內部、兩個小莫爾圓外部為藍色區域，其面積為大圓的面積減去兩個小圓的面積，即 "
    "\\(\\pi\\left ( { 5 ^ { 2 } -2 ^ { 2 } -3 ^ { 2 } } \\right )=12\\pi\\)。"
)

PARAGRAPH = {"gh_StandardFormOfACircle": "圓的標準式", "gh_GeneralFormOfACircle": "圓的一般式", "gh_PointAndCircleRelationship": "點與圓的關係"}
# 習題（觀念澄清／基礎題／進階題）原本全落在最後一個 heading 的 Skill，依題目數學內容重新歸屬。
EXERCISE_BINDING = {
    12470: ("gh_StandardFormOfACircle", "由標準式讀圓心所在象限"),
    12471: ("gh_GeneralFormOfACircle", "x²+y²+5=0 是否為圓（一般式 D 判別）"),
    12472: ("gh_GeneralFormOfACircle", "一般式圖形可為一點（D=0）"),
    12474: ("gh_StandardFormOfACircle", "由標準式求圓面積"),
    12475: ("gh_GeneralFormOfACircle", "由一般式/配方求圓心與半徑"),
    12476: ("gh_StandardFormOfACircle", "依條件求圓的標準式"),
    12479: ("gh_StandardFormOfACircle", "三點外接圓方程式"),
    12480: ("gh_StandardFormOfACircle", "以圓方程式建模求長度"),
}


def _safe(label: str, bracket: str) -> str:
    bracket = bracket.replace("=", "").replace(" | ", "_").replace("|", "_").replace(" ", "")
    return f"{label}_{bracket}"


def main() -> None:
    dry = "--dry" in sys.argv
    if not dry:
        backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit6_stage1_{datetime.now():%Y%m%d_%H%M%S}.db"
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
            notes["has_image"] = True
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

        def upd(rid, text=None, sol=None, note=None, desc=None, tag=""):
            row = con.execute("select problem_text, detailed_solution, source_description, notes from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(row["notes"])
            if note:
                note(notes)
            notes.setdefault("repair_log", []).append(f"{REVIEWED_AT} manual Stage1 repair (unit6): {tag}")
            con.execute(
                "update textbook_examples set problem_text=?, detailed_solution=?, source_description=?, notes=? where id=?",
                (text if text is not None else row["problem_text"], sol if sol is not None else row["detailed_solution"],
                 desc if desc is not None else row["source_description"], json.dumps(notes, ensure_ascii=False), rid))
            report.append({"id": rid, "fix": tag})

        # 12478: news box text restored into stem (image also attached above)
        r = con.execute("select problem_text from textbook_examples where id=12478").fetchone()
        if "天天日報" not in r["problem_text"]:
            upd(12478, text=NEWS + r["problem_text"], tag="stem restored from PDF p.15 news box (460 km, radius 80 km, 25 km/h)")
        # 12474: Symbol-font pi dropped by importer (DOCX para 187 w:sym Symbol F070)
        r = con.execute("select problem_text from textbook_examples where id=12474").fetchone()
        if "\\pi" not in r["problem_text"]:
            upd(12474, text=r["problem_text"].replace("面積為2。", "面積為 \\(2\\pi\\)。"),
                tag="Symbol pi (DOCX w:sym F070) restored: area is 2pi; PDF p.14 confirms")
        # 12466: solution truncated after part (1)
        r = con.execute("select detailed_solution from textbook_examples where id=12466").fetchone()
        if "12\\pi" not in r["detailed_solution"]:
            upd(12466, sol=r["detailed_solution"].rstrip() + EX10_SOLUTION_TAIL, tag="solution (1)-(3) restored from PDF p.12-13")
        # 12467-12469: practice->example linkage mislabeled; stems verified against PDF p.10/11/13
        link = {12467: ("例題10", "例題8"), 12468: ("例題8", "例題9"), 12469: ("例題9", "例題10")}
        for rid, (old, new) in link.items():
            r = con.execute("select source_description from textbook_examples where id=?", (rid,)).fetchone()
            if f"linked_example={new}" in r["source_description"] and "needs_review=true" not in r["source_description"]:
                continue
            d = r["source_description"].replace(f"linked_example={old}", f"linked_example={new}").replace(" | needs_review=true", "")

            def note(n, rid=rid, old=old, new=new):
                n["linked_example_audit"] = {"previous": old, "corrected": new, "basis": "PDF p.10/11/13 practice boxes", "date": REVIEWED_AT}
                if rid == 12467:
                    n["needs_review"] = False
                    n["review_required_by_confidence"] = False
                    n["manual_stem_review"] = {"date": REVIEWED_AT, "source_pdf_sha256": PDF_SHA, "page": 10,
                                               "result": "stem/conditions match PDF (P(1,-2) inside, Q(-3,3) outside, x^2+y^2=k)"}

            upd(rid, desc=d, note=note, tag=f"linked_example {old}->{new}")
        for rid, (skill, why) in EXERCISE_BINDING.items():
            row = con.execute("select skill_id, notes from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(row["notes"])
            if row["skill_id"] == skill:
                continue
            notes["skill_binding"] = {"source": "manual_topic_audit_unit6", "previous_skill_id": row["skill_id"], "basis": why, "date": REVIEWED_AT}
            con.execute("update textbook_examples set skill_id=?, source_paragraph=?, notes=? where id=?",
                        (skill, PARAGRAPH[skill], json.dumps(notes, ensure_ascii=False), rid))
            report.append({"id": rid, "fix": "rebind", "to": skill})
        con.execute("rollback" if dry else "commit")
    except Exception:
        con.execute("rollback")
        raise
    if not dry:
        out = ROOT / "reports" / "gh_unit6_stage1" / "stage1_repair_log.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(report), "changes")


if __name__ == "__main__":
    main()
