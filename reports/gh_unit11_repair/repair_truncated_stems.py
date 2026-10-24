"""Restore the cut-off tails of three Unit 11 stems (12650, 12662, 12664) from the authoritative DOCX / PDF.

    python reports/gh_unit11_repair/repair_truncated_stems.py            # dry run
    python reports/gh_unit11_repair/repair_truncated_stems.py --apply    # DB backup, then update only these three rows

Only problem_text and a notes record change; skill binding, figure assets, anchors, raw_problem_backup are kept.
The wording below is read from the PDF (page 15 for 12650, page 17 for 12662, page 18 for 12664) and the DOCX text.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
APPLY = "--apply" in sys.argv
sys.stdout.reconfigure(encoding="utf-8")

TAIL_12650 = (
    "長度 \\(3x\\), \\(4x\\), \\(5x\\)（單位）的各兩段，長度 \\(y\\)（單位）的有三段。\n請回答下列問題。\n"
    "(1)寫出 \\(x\\) 與 \\(y\\) 的關係式。\n"
    "(2)已知帳棚的體積為 \\(x\\) 的三次多項式 \\(f\\left ( { x } \\right )\\)，求 \\(f\\left ( { x } \\right )\\)。\n"
    "(3)下列何者是 \\(f\\left ( { x } \\right )-1728\\) 的因式？（單選）\n"
    "\\(\\o\\ac(○,1)\\)\\(x+1\\) \\(\\o\\ac(○,2)\\)\\(x+2\\) \\(\\o\\ac(○,3)\\)\\(x+3\\) \\(\\o\\ac(○,4)\\)\\(x+4\\) \\(\\o\\ac(○,5)\\)\\(x\\)。\n"
    "(4)若此帳棚的內部空間至少要 \\(1728\\)（立方單位），則 \\(x\\) 的範圍為何？"
)
REPAIRS = {
    12650: ("長度3x,", TAIL_12650, "PDF p.15 / DOCX 例題11 隨堂練習"),
    12662: ("的解為 \\(-1\\le x\\le 3\\)，", "的解為 \\(-1\\le x\\le 3\\)，求 a, b 的值。", "PDF p.17 / DOCX 11習題 進階題7"),
    12664: ("的關係式為\n\\(y=kt\\left ( { 4-t } \\right )\\)，",
            "的關係式為\n\\(y=kt\\left ( { 4-t } \\right )\\)，其中正數 k 為大砲上可調整的變數。為了不讓砲彈打中高 \\(16\\) 公尺的天花板，請問：變數 k 應限制在什麼範圍內。",
            "PDF p.18 / DOCX 11習題 進階題9"),
}


def main() -> None:
    conn = sqlite3.connect(DB, timeout=60)
    rows = {r[0]: r for r in conn.execute(f"select id, problem_text, notes, skill_id from textbook_examples where id in ({','.join(map(str, REPAIRS))})")}
    assert set(rows) == set(REPAIRS)
    before_other = conn.execute("select count(*), sum(length(coalesce(problem_text,''))) from textbook_examples where id not in (12650,12662,12664)").fetchone()
    plan = {}
    for qid, (anchor, tail, where) in REPAIRS.items():
        text = rows[qid][1]
        assert text.endswith(anchor) or text.rstrip().endswith(anchor.rstrip()), (qid, text[-40:])
        new = text[: len(text) - len(anchor)] + tail if text.endswith(anchor) else text.rstrip()[: len(text.rstrip()) - len(anchor.rstrip())] + tail
        plan[qid] = (new, where)
        print(qid, "\n", new, "\n")
    if not APPLY:
        return
    backup = ROOT / "backups" / "unit11_stem_repair" / time.strftime("%Y%m%d_%H%M%S")
    backup.mkdir(parents=True)
    dst = sqlite3.connect(backup / "kumon_math.db")
    conn.backup(dst)
    assert dst.execute("pragma integrity_check").fetchone()[0] == "ok"
    dst.close()
    print("backup", backup)
    with conn:
        for qid, (new, where) in plan.items():
            notes = json.loads(rows[qid][2])
            notes["stage1_text_repair"] = {"repaired_by": "unit11_truncated_stem_repair", "source": where, "reason": "stem tail cut off at import",
                                           "previous_problem_text": rows[qid][1]}
            conn.execute("update textbook_examples set problem_text=?, notes=? where id=?", (new, json.dumps(notes, ensure_ascii=False), qid))
    after_other = conn.execute("select count(*), sum(length(coalesce(problem_text,''))) from textbook_examples where id not in (12650,12662,12664)").fetchone()
    assert before_other == after_other
    skills = dict(conn.execute("select id, skill_id from textbook_examples where id in (12650,12662,12664)").fetchall())
    assert skills == {qid: rows[qid][3] for qid in REPAIRS}
    print("applied; other rows unchanged:", after_other, "skills", skills)


if __name__ == "__main__":
    main()
