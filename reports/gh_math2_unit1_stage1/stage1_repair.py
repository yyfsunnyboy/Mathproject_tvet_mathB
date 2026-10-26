"""普高數學2 單元1「數列與遞迴關係」Stage 1 局部修復 —— 僅作用於隔離 DB 複本，絕不碰正式 DB。

    python reports/gh_math2_unit1_stage1/stage1_repair.py            # 重建複本 + 套用修復 + 寫 repair_log.json
    python reports/gh_math2_unit1_stage1/stage1_repair.py --dry      # 重建複本、在 transaction 內計算後 rollback

安全：
* 正式 DB 只以 ``mode=ro`` + sqlite backup API 讀取（建立複本）；程式內 assert 目標 DB 位於 sandbox/ 之下。
* 圖檔寫入 sandbox/uploads/...，不寫正式 uploads/。
* 每項修復皆有 PDF 頁碼／bbox 或 DOCX 段落依據；needs_review 只對「已逐項目視核對」的列清除並留下證據。
範圍：textbook_examples id 12667–12706（source_chapter = `單元1 數列與遞迴關係`）。
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
from core.textbook_pdf_visual import (  # noqa: E402
    build_pdf_visual_asset_record,
    crop_pdf_bbox,
    fingerprint_file,
    upsert_notes_image_asset,
)

PROD_DB = ROOT / "instance" / "kumon_math.db"
SANDBOX = HERE / "sandbox"
DB = SANDBOX / "kumon_math_copy.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/f2bef2bd0e2b_單元01-數列與遞迴關係.pdf"
PDF_SHA = "f2bef2bd0e2bf87494da3b9777a41f2a2ed894ee73ee182746db3d33f81e1789"
DOCX_SHA = "742ea24d3d43c759b659f2390e36871a781c34405fe86176ae7d494076146b38"
ASSET_DIR = Path("uploads/question_assets/general/longteng/數學2/ch_unknown_單元1_數列與遞迴關係/sec_unknown_1數列與遞迴關係")
TODAY = date.today().isoformat()
IDS = range(12667, 12707)

assert SANDBOX.resolve() in DB.resolve().parents and DB.resolve() != PROD_DB.resolve()

# ---------------------------------------------------------------- 圖片（PDF 頁 / bbox，pt，已逐一目視核對裁圖）
# qid -> [(slot, page, bbox, 說明)]
IMAGE_FIXES: dict[int, list[tuple[str, int, list[float], str]]] = {
    12668: [("pdf_visual_01", 3, [196, 556, 432, 612], "number spiral 1..12 with arrows"),
            ("pdf_visual_02", 3, [112, 643, 512, 697], "option diagrams (1)-(4)")],
    12673: [("pdf_visual_01", 4, [395, 396, 515, 522], "left hand with counting path 1..10 (replaces mis-cropped hand/sloth image)")],
    12686: [("pdf_visual_01", 8, [188, 578, 448, 644], "hexagon tiles, figures 1-3")],
    12687: [("pdf_visual_01", 9, [126, 628, 492, 718], "Sierpinski-type triangles, figures 1-4")],
    12688: [("pdf_visual_01", 11, [404, 246, 518, 342], "triangular formation of soldiers")],
    12690: [("pdf_visual_01", 10, [148, 620, 472, 652], "segment removal, figures 1-4")],
    12694: [("pdf_visual_01", 21, [186, 516, 426, 580], "black/white square tiles, figures 1-3")],
    12695: [("pdf_visual_01", 22, [146, 200, 462, 316], "9-subdivision squares, figures 1-3")],
    12698: [("pdf_visual_01", 23, [102, 370, 530, 484], "Escher flying fish, figures 1-3")],
    12699: [("pdf_visual_01", 24, [430, 386, 526, 492], "nested squares T1..T5")],
    12702: [("pdf_visual_01", 17, [112, 438, 512, 542], "Escher lizards, figures 1-3"),
            ("pdf_visual_02", 17, [124, 590, 310, 632], "option lizards (1)-(3)")],
}

# ---------------------------------------------------------------- 題幹 / 詳解（依 DOCX 段落與 PDF 頁面逐字還原）
SRC_NOTE = {
    12673: "DOCX paras 52-56 / PDF p.4: lines after the first were dropped",
    12690: "DOCX paras 150-154 / PDF p.10: trailing 'a_n' definition and (1)(2) dropped",
    12701: "DOCX paras 255-258 / PDF p.16: '恆為6的倍數' dropped (formula a_n=4^n+2 is genuinely in the source, PDF p.16)",
    12704: "DOCX paras 272-275 / PDF p.17: '恆為12的倍數' dropped",
    12671: "DOCX para 102 (w:sym F02D minus lost) / PDF p.7",
    12676: "DOCX para 112 (superscript run '2' flattened) / PDF p.8",
    12674: "DOCX paras 87-88 (two w:sym F02D minus signs lost: 3, -6, 12, ..., -384)",
}
# in-place edits where the stored stem is otherwise correct
TEXT_REPLACE = {12674: [("3, 6, 12,…, 384", "3, −6, 12,…, −384"), ("試問 384是第幾項", "試問 −384是第幾項")]}
NEW_PROBLEM = {
    12673: ("伸出左手，從大拇指開始，按照右圖的方式依序數數字：\n"
            "1, 2, 3, 4, 5, 6, 7, 8, 9, 10,…。\n"
            r"設 \(a_{ n }\) 是第n次對應到大拇指時所數到的數字。" "\n"
            r"(1)數數看：寫出 \(a_{ 1 }\)、\(a_{ 2 }\)、\(a_{ 3 }\)、\(a_{ 4 }\) 的值。" "\n"
            r"(2)數到 \(999\) 時，所對應的是哪根手指頭？（單選）" "\n"
            "①大拇指　②食指　③中指　④無名指　⑤小指。"),
    12690: None,  # append, see APPEND
    12701: "使用數學歸納法證明：對於所有的正整數n,\n" r"\(a_{ n } =4 ^ { n } +2\)" "\n恆為 \\(6\\) 的倍數。",
    12704: "使用數學歸納法證明：對於所有的正整數n,\n" r"\(9 ^ { n } +3\) 恆為 \(12\) 的倍數。",
    12671: r"已知a, 2, b三數成等比數列，且a, 2, \(b-1\) 三數成等差數列，求a的值。",
    12676: r"已知成等比的1, r, \(r ^ { 2 }\) 三數恰為另一等差數列之第1, 2, 5項，求r的值。（有兩解）",
}
APPEND = {
    12690: ("\n" r"依此規律可畫第 \(5\) 圖、第 \(6\) 圖、……，並設 \(a_{ n }\) 為第n圖中的線段個數（\(a_{ 1 }=1\)、\(a_{ 2 }=2\)）。" "\n"
            r"(1)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。" "\n"
            r"(2)求 \(a_{ 9 }\) 的值。"),
}
OLD_SOLUTION_FIX = {12671: ("a, 2, b  1三數成等差數列", r"a, 2, \(b-1\) 三數成等差數列")}

# ---------------------------------------------------------------- 偽題與編號
PSEUDO_ID = 12691  # 「數學超展開」側欄句「隨堂練習中，一直重複…康托集」被誤判為隨堂練習8
# id -> (舊編號, 新編號, 新 linked_example 或 None=不變)；DOCX 只有 11 個「隨堂練習」標題
RENUMBER = {12692: (9, 8, None), 12703: (10, 9, "例題9"), 12704: (11, 10, "例題10"), 12705: (12, 11, None)}
# 目視核對題幹與來源一致、圖正確後才清除 needs_review（信心 0.4 僅因 PDF 對位低信心）
MANUAL_REVIEW = {
    12692: "stem compared with DOCX paras 172-174 and PDF p.12; figure (existing PDF crop of the whole question box) verified legible",
    12705: "stem compared with DOCX paras 293-297 and PDF p.18; figure (3 butterfly tilings) verified against PDF",
}


def make_copy() -> None:
    SANDBOX.mkdir(parents=True, exist_ok=True)
    for p in list(SANDBOX.glob("kumon_math_copy.db*")):
        p.unlink()
    if (SANDBOX / "uploads").exists():
        shutil.rmtree(SANDBOX / "uploads")
    src = sqlite3.connect(f"file:{PROD_DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(DB)
    src.backup(dst)
    src.close()
    ok = dst.execute("pragma integrity_check").fetchone()[0]
    dst.close()
    assert ok == "ok", ok


def main() -> None:
    dry = "--dry" in sys.argv
    assert fingerprint_file(PDF) == PDF_SHA, "PDF hash mismatch"
    make_copy()
    con = sqlite3.connect(DB, isolation_level=None)
    con.row_factory = sqlite3.Row
    log: list[dict] = []
    rows = {r["id"]: r for r in con.execute(
        "select * from textbook_examples where id between 12667 and 12706 and source_curriculum='general' "
        "and source_volume='數學2' and source_chapter='單元1 數列與遞迴關係'")}
    assert len(rows) == 40, len(rows)
    before = {i: dict(r) for i, r in rows.items()}
    try:
        con.execute("begin")
        # ---- 偽題：先確認無任何參照
        for t, c in (("gencode_component_tracker", "textbook_example_id"), ("quiz_attempts", "question_id"),
                     ("mistake_notebook_entries", "component_id")):
            n = con.execute(f'select count(*) from {t} where cast("{c}" as text) in (?, ?)', (str(PSEUDO_ID), f"src_{PSEUDO_ID}")).fetchone()[0]
            assert n == 0, (t, n)
        assert rows[PSEUDO_ID]["problem_text"].startswith("中，一直重複其步驟")
        con.execute("delete from textbook_examples where id=?", (PSEUDO_ID,))
        log.append({"id": PSEUDO_ID, "fix": "delete_pseudo_item",
                    "reason": "sidebar sentence (數學超展開/圖4 stamp) parsed as 隨堂練習8; DOCX has only 11 隨堂練習 headings",
                    "removed_problem_text": rows[PSEUDO_ID]["problem_text"]})

        # ---- 編號與關聯（含檔案改名）
        for rid, (old_n, new_n, linked) in RENUMBER.items():
            r = rows[rid]
            notes = json.loads(r["notes"])
            desc = r["source_description"]
            assert desc.startswith(f"隨堂練習{old_n} ["), desc
            new_desc = desc.replace(f"隨堂練習{old_n} [", f"隨堂練習{new_n} [", 1).replace("| needs_review=true", "")
            if linked:
                new_desc = re.sub(r"linked_example=例題\d+", f"linked_example={linked}", new_desc)
            qa = notes["question_anchor"]
            assert qa["question_number"] == str(old_n)
            qa["anchor_id"] = qa["anchor_id"].replace(f"in_class_practice_{old_n:03d}_", f"in_class_practice_{new_n:03d}_")
            qa["anchor_key"] = qa["anchor_key"].replace(f"|in_class_practice|{old_n}|", f"|in_class_practice|{new_n}|")
            qa["question_number"] = str(new_n)
            qa["question_label"] = f"隨堂練習{new_n}"
            notes["stage1_renumber"] = {"date": TODAY, "from_label": f"隨堂練習{old_n}", "to_label": f"隨堂練習{new_n}",
                                        "reason": f"pseudo item {PSEUDO_ID} removed; source_order/block_index kept from original parse",
                                        **({"linked_example_to": linked} if linked else {})}
            for a in notes.get("image_assets") or []:
                a["question_anchor"] = qa["anchor_id"]
                if rid in (12692, 12705):
                    old_rel = a["path"]
                    new_rel = old_rel.replace(f"隨堂練習{old_n}_", f"隨堂練習{new_n}_").replace("_needs_reviewtrue", "")
                    src = ROOT / old_rel
                    assert src.exists(), src
                    (SANDBOX / new_rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, SANDBOX / new_rel)
                    assert fingerprint_file(SANDBOX / new_rel) == a["sha256"]
                    a["path"] = a["display_path"] = new_rel
            con.execute("update textbook_examples set source_description=?, notes=? where id=?",
                        (new_desc, json.dumps(notes, ensure_ascii=False), rid))
            log.append({"id": rid, "fix": "renumber", "from": f"隨堂練習{old_n}", "to": f"隨堂練習{new_n}",
                        "linked_example": linked or "unchanged", "anchor_id": qa["anchor_id"]})
            rows[rid] = con.execute("select * from textbook_examples where id=?", (rid,)).fetchone()

        # ---- 題幹 / 詳解
        for rid in sorted(set(NEW_PROBLEM) | set(OLD_SOLUTION_FIX) | set(TEXT_REPLACE)):
            r = con.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(r["notes"])
            old_text, old_sol = r["problem_text"], r["detailed_solution"] or ""
            new_text = old_text
            if rid in APPEND:
                new_text = old_text.rstrip() + APPEND[rid]
            elif NEW_PROBLEM.get(rid):
                new_text = NEW_PROBLEM[rid]
            for a, b in TEXT_REPLACE.get(rid, []):
                assert a in new_text, (rid, a)
                new_text = new_text.replace(a, b)
            new_sol = old_sol
            if rid in OLD_SOLUTION_FIX:
                a, b = OLD_SOLUTION_FIX[rid]
                assert a in old_sol, rid
                new_sol = old_sol.replace(a, b)
            notes.setdefault("repair_log", []).append(
                f"{TODAY} Stage1 isolated repair: stem restored from authoritative DOCX/PDF ({SRC_NOTE.get(rid, '')})")
            notes["stem_before_repair"] = old_text
            notes["stem_repair_source"] = {"docx_sha256": DOCX_SHA, "pdf_sha256": PDF_SHA, "basis": SRC_NOTE.get(rid, "")}
            con.execute("update textbook_examples set problem_text=?, detailed_solution=?, notes=? where id=?",
                        (new_text, new_sol, json.dumps(notes, ensure_ascii=False), rid))
            log.append({"id": rid, "fix": "stem", "before": old_text, "after": new_text,
                        **({"solution_fix": OLD_SOLUTION_FIX[rid]} if rid in OLD_SOLUTION_FIX else {})})

        # ---- 圖片
        for rid, regions in IMAGE_FIXES.items():
            r = con.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(r["notes"])
            anchor = notes["question_anchor"]
            dedupe = re.search(r"dedupe=([0-9a-f]+)", r["source_description"]).group(1)
            label = r["source_description"].split(" [")[0].replace(" ", "")
            qtype = anchor["question_type"]
            notes["image_assets"] = []
            shas = []
            for slot, page, bbox, why in regions:
                fig = slot[-2:].lstrip("0")
                rel = ASSET_DIR / f"{qtype}_{label}_source_type{anchor['source_type']}_dedupe{dedupe}_general__fig{fig}.png"
                meta = crop_pdf_bbox(PDF, page, bbox, SANDBOX / rel, dpi=200)
                asset = build_pdf_visual_asset_record(
                    rel_path=rel.as_posix(), page_1based=page, bbox=bbox, classification="required", visual_type="diagram",
                    match_method="manual_page_region", match_score=1.0, reason=f"verified_pdf_region: {why}", image_meta=meta,
                    anchor_id=anchor["anchor_id"], asset_slot=slot)
                upsert_notes_image_asset(notes, asset, slot=slot)
                shas.append({"slot": slot, "page": page, "bbox": bbox, "sha256": meta["sha256"], "size": [meta["width"], meta["height"]]})
            notes.update({"has_image": True, "needs_image": True, "image_role": "required_diagram", "needs_review": False,
                          "image_dependency_reason": "figure_required_by_stem_verified_against_pdf",
                          "needs_review_before_visual": False, "visual_required_missing": False, "needs_image_review": False,
                          "visual_status": "accepted", "image_warning_resolved_by": "pdf_visual", "pdf_visual_status": "VISUAL_ATTACHED"})
            notes.pop("image_warning", None)
            enrich = dict(notes.get("pdf_visual_enrichment") or {})
            enrich.update({"result": "mounted", "classification": "required", "match_method": "manual_page_region", "match_score": 1.0,
                           "page": regions[0][1], "page_source": "manual_verified", "visual_bbox": regions[0][2],
                           "visual_reason": "manual_verified_region"})
            notes["pdf_visual_enrichment"] = enrich
            notes["manual_visual_review"] = {"date": TODAY, "source_pdf_sha256": PDF_SHA,
                                             "result": "each crop viewed against the PDF page render; complete figure, no neighbouring question content",
                                             "crops": shas}
            con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), rid))
            log.append({"id": rid, "fix": "image", "crops": shas})

        # ---- 低信心但已核對者
        for rid, why in MANUAL_REVIEW.items():
            r = con.execute("select notes from textbook_examples where id=?", (rid,)).fetchone()
            notes = json.loads(r["notes"])
            notes.update({"needs_review": False, "review_required_by_confidence": False, "needs_review_before_visual": False})
            notes["manual_stem_review"] = {"date": TODAY, "result": why, "source_docx_sha256": DOCX_SHA, "source_pdf_sha256": PDF_SHA}
            con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), rid))
            log.append({"id": rid, "fix": "manual_review_cleared", "evidence": why})
        con.execute("rollback" if dry else "commit")
    except Exception:
        con.execute("rollback")
        raise
    con.close()
    if not dry:
        (HERE / "repair_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
        (HERE / "before_rows.json").write_text(json.dumps({str(i): {k: v for k, v in d.items() if k in ("problem_text", "detailed_solution", "source_description", "skill_id")} for i, d in before.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(("DRY " if dry else "") + f"{len(log)} log entries; sandbox DB: {DB.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
