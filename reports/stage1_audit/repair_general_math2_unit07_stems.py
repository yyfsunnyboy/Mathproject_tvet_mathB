"""Restore the two incomplete Unit 07 stems (12900, 12909) found by the Stage 1 fidelity audit.

    python reports/stage1_audit/repair_general_math2_unit07_stems.py                 # dry run, prints new stems
    python reports/stage1_audit/repair_general_math2_unit07_stems.py --apply BACKUP  # single transaction write

BACKUP is the SQLite Backup API copy taken right before the write; the target rows must still equal it.
Only problem_text and an added notes["stage1_text_repair"] change; every other column, row and table is
compared inside the same BEGIN IMMEDIATE transaction and the write is rolled back on any other difference.
The student stem is shown via textContent + MathJax (inline \\( \\) only), so the table uses a LaTeX array.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
AUDIT = "reports/stage1_audit/general_數學2_unit07_stage1_fidelity_audit.md"
DOCX = {
    "path": "textbook_import/uploaded_sources/general/數學2/360a978e359e_單元07-數學期望值.docx",
    "sha256": "360a978e359e1275af46f969194d2444c79690cd43e1e82c93d088f202bcffc1",
}
PDF = {
    "path": "textbook_import/uploaded_sources/general/數學2/6ccf4aeb4b77_單元07-數學期望值.pdf",
    "sha256": "6ccf4aeb4b77ee63f5ed3969782346ab2e50a789f695f43aa25bd3ef5d2a996d",
}
sys.stdout.reconfigure(encoding="utf-8")

TABLE_12900 = (
    "\\(\\begin{array}{|c|c|c|c|}\\hline "
    "\\text{經濟狀況} & \\text{成長} & \\text{持平} & \\text{衰退} \\\\ \\hline "
    "\\text{機率} & 0.4 & 0.5 & 0.1 \\\\ \\hline "
    "\\text{甲地利潤} & 40 & 15 & -10 \\\\ \\hline "
    "\\text{乙地利潤} & 55 & 10 & -30 \\\\ \\hline "
    "\\end{array}\\)"
)
SOURCE_TEXT_12909 = "今有一題某考生已經確定選項(1)與(2)是正確的，其餘3個選項則隨意猜測，求此考生在該題得分的期望值。"
# A bare "(1)" in the stem is taken for a sub-question marker by the practice page, and "\((1)\)" loses its parentheses.
QUESTION_12909 = (
    "今有一題某考生已經確定選項 \\(\\left( 1 \\right)\\) 與 \\(\\left( 2 \\right)\\) 是正確的，"
    "其餘 \\(3\\) 個選項則隨意猜測，求此考生在該題得分的期望值。"
)

EXPECTED = {
    12900: {"source_description": "隨堂練習5", "problem_type": "in_class_practice",
            "anchor_key": "general|longteng|2|7|section|in_class_practice|5|10"},
    12909: {"source_description": "7習題 進階題7", "problem_type": "advanced_exercise",
            "anchor_key": "general|longteng|2|7|section|advanced_exercise|7|19"},
}
IDENTITY = {"skill_id": "gh_MathematicalExpectation", "source_curriculum": "general",
            "source_volume": "數學2", "source_chapter": "單元7 數學期望值"}


def new_stem(qid: int, text: str) -> str:
    if qid == 12900:
        head = "（百萬／年）如下表："
        tail = "若以一年利潤期望值的大小為判斷準則，則公司應選擇在何地建廠較佳？"
        assert "\\begin{array}" not in text and text.count(head) == 1 and text.endswith("\n" + tail), text
        return text.replace(head + "\n", head + "\n" + TABLE_12900 + "\n", 1)
    assert "今有一題" not in text and text.endswith("該題以零分計算。」"), text
    return text + "\n" + QUESTION_12909


REPAIR_SOURCE = {
    12900: {"pdf_page": 7, "printed_page": 132, "docx_location": "table T15 nested sub-table (4 rows x 4 cols)",
            "reason": "required data table (經濟狀況/機率/甲地利潤/乙地利潤) not imported; question unsolvable without it",
            "format": "MathJax inline LaTeX array (student stem renders via textContent + MathJax; markdown tables are not rendered)",
            "sign_authority": "PDF p.7 shows -10 and -30; DOCX text extraction drops the minus signs"},
    12909: {"pdf_page": 10, "printed_page": 135, "docx_location": "paragraph 89 text after the line break",
            "reason": "final question sentence truncated at import; condition and target missing",
            "source_text": SOURCE_TEXT_12909,
            "format": "numbers wrapped as inline math like the rest of this stem; option labels as \\left( n \\right)"},
}


def table_digest(conn: sqlite3.Connection, table: str) -> str:
    h = hashlib.sha256()
    for row in conn.execute(f"SELECT * FROM [{table}] ORDER BY rowid"):
        h.update(repr(row).encode("utf-8"))
    return h.hexdigest()


def all_digests(conn: sqlite3.Connection) -> dict[str, str]:
    names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    return {n: table_digest(conn, n) for n in names}


def load_rows(conn: sqlite3.Connection) -> dict[int, dict]:
    conn.row_factory = sqlite3.Row
    rows = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM textbook_examples WHERE id IN (12900, 12909)")}
    conn.row_factory = None
    return rows


def check_identity(rows: dict[int, dict]) -> None:
    assert set(rows) == set(EXPECTED), rows.keys()
    for qid, exp in EXPECTED.items():
        row = rows[qid]
        for k, v in IDENTITY.items():
            assert row[k] == v, (qid, k, row[k])
        assert row["problem_type"] == exp["problem_type"], (qid, row["problem_type"])
        assert row["source_description"].startswith(exp["source_description"] + " ["), (qid, row["source_description"])
        notes = json.loads(row["notes"])
        assert notes["question_anchor"]["anchor_key"] == exp["anchor_key"], (qid, notes["question_anchor"])
        prov = notes["source_provenance"]
        assert prov["primary"]["sha256"] == DOCX["sha256"] and prov["optional_enrich_pdf"]["sha256"] == PDF["sha256"], qid
        assert "stage1_text_repair" not in notes, qid


def main() -> None:
    apply = "--apply" in sys.argv
    conn = sqlite3.connect(DB, timeout=60)
    rows = load_rows(conn)
    check_identity(rows)
    plan = {qid: new_stem(qid, rows[qid]["problem_text"]) for qid in rows}
    for qid, text in plan.items():
        print(f"--- {qid} new problem_text:\n{text}\n")
    (Path(__file__).with_name("unit07_repair_preview.json")).write_text(
        json.dumps({str(k): v for k, v in plan.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
    if not apply:
        print("DRY RUN: no write")
        return

    backup = Path(sys.argv[sys.argv.index("--apply") + 1])
    bconn = sqlite3.connect(f"file:{backup.as_posix()}?mode=ro", uri=True)
    backup_rows = load_rows(bconn)
    bconn.close()

    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        current = load_rows(conn)
        assert current == backup_rows, "target rows changed since backup"
        before = all_digests(conn)
        others_before = conn.execute(
            "SELECT count(*) FROM textbook_examples WHERE source_chapter='單元7 數學期望值'").fetchone()[0]
        stamp = datetime.now().isoformat(timespec="seconds")
        for qid, text in plan.items():
            notes = json.loads(current[qid]["notes"])
            notes["stage1_text_repair"] = {
                "repaired_by": "general_math2_unit07_stage1_stem_repair",
                "repaired_at": stamp,
                "audit": AUDIT,
                "source_docx": DOCX,
                "source_pdf": PDF,
                **REPAIR_SOURCE[qid],
                "previous_problem_text": current[qid]["problem_text"],
            }
            cur = conn.execute("UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                               (text, json.dumps(notes, ensure_ascii=False), qid))
            assert cur.rowcount == 1, qid
        after_rows = load_rows(conn)
        for qid in plan:
            changed = {k for k in after_rows[qid] if after_rows[qid][k] != current[qid][k]}
            assert changed == {"problem_text", "notes"}, (qid, changed)
            old_notes, new_notes = json.loads(current[qid]["notes"]), json.loads(after_rows[qid]["notes"])
            assert {k: v for k, v in new_notes.items() if k != "stage1_text_repair"} == old_notes, qid
            assert after_rows[qid]["problem_text"] == plan[qid], qid
        after = all_digests(conn)
        changed_tables = sorted(t for t in before if before[t] != after.get(t)) + sorted(set(after) - set(before))
        assert changed_tables == ["textbook_examples"], changed_tables
        h_other_before = hashlib.sha256(repr(
            sqlite3.connect(f"file:{backup.as_posix()}?mode=ro", uri=True).execute(
                "SELECT * FROM textbook_examples WHERE id NOT IN (12900, 12909) ORDER BY id").fetchall()).encode()).hexdigest()
        h_other_after = hashlib.sha256(repr(conn.execute(
            "SELECT * FROM textbook_examples WHERE id NOT IN (12900, 12909) ORDER BY id").fetchall()).encode()).hexdigest()
        assert h_other_before == h_other_after, "other textbook_examples rows differ from backup"
        others_after = conn.execute(
            "SELECT count(*) FROM textbook_examples WHERE source_chapter='單元7 數學期望值'").fetchone()[0]
        assert others_before == others_after == 21
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        print("ROLLED BACK")
        raise
    print("COMMITTED: textbook_examples ids 12900, 12909 (problem_text, notes); all other tables unchanged")


if __name__ == "__main__":
    main()
