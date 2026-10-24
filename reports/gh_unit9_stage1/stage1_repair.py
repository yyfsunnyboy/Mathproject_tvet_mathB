"""普高數學1 Unit 9 Stage 1 局部修復：修 8 題（id 12571/12573/12574/12585/12586/12591/12592/12593）、新增 5 題觀念題。

證據來源：uploaded_sources 內已驗證雜湊的 DOCX / PDF（逐題對照見 STAGE1_REPORT.md）。
用法：
  python stage1_repair.py --db <path>   # 在 DB 複本上預演（不備份）
  python stage1_repair.py               # 正式 DB：先備份並確認 integrity，再於單一 transaction 寫入
寫入前重新確認指定資料仍符合調查結果；不符即中止。不重新匯入、不碰其餘 30 題與其他單元。
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.textbook_pdf_visual import build_pdf_visual_asset_record, crop_pdf_bbox, upsert_notes_image_asset  # noqa: E402

REAL_DB = ROOT / "instance" / "kumon_math.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學1/94c28e39fe3c_單元09-一次與二次函數.pdf"
PDF_SHA = "94c28e39fe3ce1ef5d816ae5c35e55a275fe0617867a12f249401f87b29f6ff3"
DOCX_SHA = "e61b79199c183f482f1bf8ed7f12b57eb9f8a853e645775c536358f4ceaf3381"
ASSET_DIR = "uploads/question_assets/general/longteng/數學1/ch_unknown_單元9_一次與二次函數/sec_unknown_9一次與二次函數"
TODAY = datetime.now().strftime("%Y-%m-%d")

IMAGE_FIXES = {
    12573: (15, [230, 230, 398, 327], "missing figures (a)(b): square ABCD with E on BC, F on CD, and the 4-tile pattern (b)"),
    12591: (22, [388, 139, 538, 264], "missing figure: parabola y=ax^2+bx+c through (-2,0) and (1/2,0)"),
}

DERIVATION = (
    "\\(y=-x ^ { 2 } +3x+1\\)\n"
    "\\(=-\\left ( { x ^ { 2 } -3x } \\right )+1\\)\n"
    "\\(=-\\left ( { x ^ { 2 } -3x+\\left ( { \\frac { 3 } { 2 } } \\right ) ^ { 2 } } \\right )+\\frac { 9 } { 4 }+1\\)\n"
    "\\(=-\\left ( { x-\\frac { 3 } { 2 } } \\right ) ^ { 2 } +\\frac { 13 } { 4 }\\)。"
)
TABLE = "\n訂單數量（千個）\t5\t10\n收入（萬元）\t45\t80"
Q12592 = ("某人將一顆球置於地上後，再將球擊出，如圖所示。\n假設此球的飛行路線是一條拋物線，且飛行時間x秒與飛行高度y公尺的關係式為\n"
          "\\(y=-5x ^ { 2 } +20x\\)。\n關於此球的飛行過程，回答下列問題。\n(1)當飛行時間是多少秒時，飛行高度為15公尺？\n"
          "(2)從飛出到落地共用了多少時間？\n(3)飛行高度何時最大？又此時高度為多少公尺？")
Q12593_TAIL = "求 \\(f\\left ( { x } \\right )\\) 及其頂點坐標。"

# 觀念題 1-5：DOCX「9習題」觀念題（段落 296-301），五個獨立的 ○× 敘述；教材未附答案，correct_answer 保持空白。
CONCEPT_INTRO = "下列敘述對的打「○」，錯的打「×」。"
CONCEPTS = [
    ("gh_LinearFunctions", "一次函數", "一次函數 \\(y=2x+3\\) 的圖形是一條斜率為3的直線。"),
    ("gh_QuadraticFunctions", "二次函數", "將拋物線 \\(y=2x ^ { 2 }\\) 往左平移1單位，可得拋物線 \\(y=2\\left ( { x+1 } \\right ) ^ { 2 }\\)。"),
    ("gh_QuadraticFunctions", "二次函數", "拋物線 \\(y=\\left ( { 2x+1 } \\right ) ^ { 2 } +3\\) 的對稱軸為直線 \\(2x+1=0\\)。"),
    ("gh_QuadraticFunctions", "二次函數", "在 \\(2\\le x\\le 4\\) 的範圍內，函數 \\(f\\left ( { x } \\right )=-\\left ( { x-1 } \\right ) ^ { 2 } +5\\) 的最大值為 \\(f\\left ( { 2 } \\right )\\)。"),
    ("gh_QuadraticFunctions", "二次函數", "二次函數的圖形與y軸一定有一交點，但與x軸不一定有交點。"),
]


def dedupe_hash(problem: str, source_type: str, title: str) -> str:
    normalized = re.sub(r"\s+", " ", problem).strip()
    payload = {"source_type": source_type, "title": title, "problem": normalized, "sub_questions": []}
    return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _row(con, rid):
    return con.execute("select problem_text, detailed_solution, source_description, notes, problem_type from textbook_examples where id=?", (rid,)).fetchone()


def preflight(con: sqlite3.Connection) -> None:
    def need(cond: bool, msg: str) -> None:
        if not cond:
            raise SystemExit(f"preflight failed (not the investigated state): {msg}")

    p, s, d, n, _t = _row(con, 12571)
    need("[MATH_PARSE_FAILED_220]" in s, "12571 placeholder")
    p, s, d, n, _t = _row(con, 12574)
    need("下表是該工廠" in p and "\t5\t10" not in p and "45" not in p.split("下表是")[1].split("利用上表")[0], "12574 table absent")
    p, *_ = _row(con, 12592)
    need(p == "某人將一顆球置於地上後，再將球擊出，如圖所示。", "12592 truncated stem")
    p, *_ = _row(con, 12593)
    need(p.endswith("\\)，") and "頂點坐標" not in p, "12593 truncated stem")
    for rid in IMAGE_FIXES:
        n = json.loads(_row(con, rid)[3])
        need(not n.get("image_assets"), f"{rid} already has an image")
    for rid in (12585, 12586):
        n = json.loads(_row(con, rid)[3])
        need(n.get("needs_review") is True and n.get("import_confidence") == 0.4, f"{rid} flag state")
    need(con.execute("select count(*) from textbook_examples where source_volume like '%數學1%' and source_chapter like '%單元9%'").fetchone()[0] == 38, "Unit 9 row count")
    need(con.execute("select count(*) from textbook_examples where source_description like '%觀念題%' and source_chapter like '%單元9%'").fetchone()[0] == 0, "觀念題 already present")
    need(con.execute("select max(id) from textbook_examples").fetchone()[0] == 12597, "id space (another writer?)")


def main() -> None:
    db_path = Path(sys.argv[sys.argv.index("--db") + 1]) if "--db" in sys.argv else REAL_DB
    formal = db_path.resolve() == REAL_DB.resolve()
    if formal:
        backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit9_stage1_{datetime.now():%Y%m%d_%H%M%S}.db"
        src = sqlite3.connect(db_path)
        dst = sqlite3.connect(backup)
        src.backup(dst)
        integrity = dst.execute("pragma integrity_check").fetchone()[0]
        dst.close()
        src.close()
        print("backup:", backup.name, "integrity:", integrity)
        if integrity != "ok":
            raise SystemExit("backup integrity failed")
    con = sqlite3.connect(db_path, isolation_level=None)
    preflight(con)
    log: list[dict] = []
    created: list[Path] = []
    try:
        con.execute("begin")

        def update(rid, *, problem=None, solution=None, mutate=None, tag=""):
            p, s, d, notes, _t = _row(con, rid)
            n = json.loads(notes)
            if mutate:
                mutate(n)
            n.setdefault("repair_log", []).append(f"{TODAY} manual Stage1 repair (unit9): {tag}")
            con.execute("update textbook_examples set problem_text=?, detailed_solution=?, notes=? where id=?",
                        (problem if problem is not None else p, solution if solution is not None else s, json.dumps(n, ensure_ascii=False), rid))
            log.append({"id": rid, "fix": tag})

        # 12571: failed MathType formula 220 -> completing-the-square derivation from PDF p.13
        _p, s, *_ = _row(con, 12571)
        update(12571, solution=s.replace("[MATH_PARSE_FAILED_220]", DERIVATION),
               mutate=lambda n: n.__setitem__("manual_formula_repair", {"date": TODAY, "formula_index": 220, "source_pdf_sha256": PDF_SHA, "page": 13,
                                                                          "result": "MATH_PARSE_FAILED_220 replaced by the 4-step derivation printed in the PDF"}),
               tag="MATH_PARSE_FAILED_220 replaced by derivation from PDF p.13")
        # 12574: data table of the stem
        p, *_ = _row(con, 12574)
        marker = "下表是該工廠過去二筆交易中，訂單數量與收入的關係："
        update(12574, problem=p.replace(marker, marker + TABLE), tag="stem table (5,10 -> 45,80) restored from PDF p.16")
        # 12592 / 12593: truncated stems
        update(12592, problem=Q12592, tag="stem completed from DOCX (y=-5x^2+20x and sub-questions (1)-(3))")
        p, *_ = _row(con, 12593)
        update(12593, problem=p + Q12593_TAIL, tag="stem completed from DOCX (求 f(x) 及其頂點坐標)")
        # 12585 / 12586: stems verified against DOCX/PDF; low match confidence only
        for rid, page in ((12585, 17), (12586, 19)):
            def clear(n, page=page):
                n["needs_review"] = False
                n["review_required_by_confidence"] = False
                n["manual_stem_review"] = {"date": TODAY, "source_pdf_sha256": PDF_SHA, "page": page,
                                           "result": "stem matches DOCX/PDF; flag was low match confidence only"}
            _p, _s, d, _n, _t = _row(con, rid)
            update(rid, mutate=clear, tag="needs_review cleared after manual stem review")
            con.execute("update textbook_examples set source_description=? where id=?", (d.replace(" | needs_review=true", ""), rid))
        # 12573 / 12591: figures from the authoritative PDF
        for rid, (page, bbox, why) in IMAGE_FIXES.items():
            p, s, d, notes, ptype = _row(con, rid)
            n = json.loads(notes)
            m = re.match(r"^(.*?)\s*\[(.*)\]\s*$", d)
            label, bracket = m.group(1), m.group(2)
            safe = f"{label}_" + bracket.replace("=", "").replace(" | ", "_").replace("|", "_").replace(" ", "")
            rel = f"{ASSET_DIR}/{ptype}_{safe}_general__fig1.png"
            meta = crop_pdf_bbox(PDF, page, bbox, ROOT / rel, dpi=200, pad_pt=2)
            created.append(ROOT / rel)
            asset = build_pdf_visual_asset_record(rel_path=rel, page_1based=page, bbox=bbox, classification="required", visual_type="diagram",
                                                  match_method="manual_pdf_review", match_score=1.0, reason=why, image_meta=meta,
                                                  anchor_id=n["question_anchor"]["anchor_id"])
            upsert_notes_image_asset(n, asset)
            n.update(has_image=True, visual_required_missing=False, needs_review=False, image_role="required_diagram",
                     image_warning_resolved_by="manual_pdf_review", pdf_visual_status="VISUAL_ATTACHED")
            n.pop("image_warning", None)
            n["manual_visual_review"] = {"date": TODAY, "source_pdf_sha256": PDF_SHA, "page": page, "bbox": bbox,
                                         "result": "figure verified against PDF page image", "reason": why, "crop_sha256": meta["sha256"]}
            n.setdefault("repair_log", []).append(f"{TODAY} manual Stage1 repair (unit9): figure attached from PDF p.{page}")
            desc = d.replace(" | needs_review=true", "")
            con.execute("update textbook_examples set notes=?, source_description=? where id=?", (json.dumps(n, ensure_ascii=False), desc, rid))
            log.append({"id": rid, "fix": "image", "page": page, "bbox": bbox, "sha256": meta["sha256"]})

        # 觀念題 1-5: new rows modelled on the imported 習題 rows (chapter_exercise)
        template_notes = json.loads(_row(con, 12564)[3])
        ref = con.execute("select source_curriculum, source_volume, source_chapter, source_section from textbook_examples where id=12564").fetchone()
        for i, (skill, paragraph, statement) in enumerate(CONCEPTS, start=1):
            problem = f"{CONCEPT_INTRO}\n{statement}"
            title = f"9習題 觀念題{i}"
            h = dedupe_hash(problem, "chapter_exercise", title)
            n = json.loads(json.dumps(template_notes))
            n.update(raw_problem_backup=problem, needs_review=False, import_confidence=0.9, auto_fill_applied=False,
                     review_required_by_confidence=False, image_role="unknown", needs_image=False,
                     image_dependency_reason="no_diagram_dependency_detected", pdf_visual_status="NO_VISUAL_REQUIRED")
            n["pdf_visual_enrichment"] = {"source_pdf": "09-.pdf", "source_pdf_sha256": PDF_SHA, "result": "not_applicable_added_by_stage1_repair"}
            n["question_anchor"] = {"anchor_id": f"general_1_section_exercise_c{i:02d}_024", "anchor_key": f"general|longteng|1|9|section|exercise|c{i}|24",
                                    "curriculum": "general", "publisher": "longteng", "volume": "數學1", "chapter": "9", "section": "",
                                    "question_type": "exercise", "question_number": f"c{i}", "source_order": 24, "block_index": 23,
                                    "occurrence_index": i, "question_label": title, "source_type": "chapter_exercise",
                                    "text_fingerprint": hashlib.sha256(problem.encode("utf-8")).hexdigest()}
            n["stage1_added"] = {"date": TODAY, "reason": "觀念題 block (DOCX paragraphs 296-301) was not recognised by the importer",
                                 "source_docx_sha256": DOCX_SHA, "statement_index": i,
                                 "answer": "textbook prints no answer; correct_answer left empty (not guessed)"}
            con.execute(
                "insert into textbook_examples (skill_id, source_curriculum, source_volume, source_chapter, source_section, source_description,"
                " source_paragraph, problem_text, problem_type, correct_answer, detailed_solution, notes, difficulty_level, difficulty_h)"
                " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (skill, ref[0], ref[1], ref[2], ref[3], f"{title} [source_type=chapter_exercise | dedupe={h}]", paragraph, problem,
                 "chapter_exercise", "", "", json.dumps(n, ensure_ascii=False), 1, 1.0))
            log.append({"fix": "insert", "title": title, "skill": skill, "dedupe": h})
        con.execute("commit")
    except BaseException:
        con.execute("rollback")
        for path in created:  # a failed run leaves no orphan crops
            path.unlink(missing_ok=True)
        raise
    out = Path(__file__).with_name("stage1_repair_log.json" if formal else "stage1_repair_rehearsal_log.json")
    out.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(log), "changes", "(formal DB)" if formal else f"(rehearsal on {db_path.name})")


if __name__ == "__main__":
    main()
