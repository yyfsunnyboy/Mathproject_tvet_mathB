"""Unit 8 Stage 1：12525（例題6）、12536（基礎題6）改綁 gh_RemainderTheorem（只改這兩列）。

證據：DOCX 段落順序 丙 餘式定理(131) → 例題6(146)；12536 為與例題7 同型的 f(12) 綜合除法計算。
先備份並確認 integrity，再於單一 transaction 寫入；列內容與預期不符時中止（避免覆蓋他人的新修改）。
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
OLD, NEW, PARA = "gh_ArithmeticOperationsOfPolynomials", "gh_RemainderTheorem", "餘式定理"
BASIS = {
    12525: "DOCX order: 丙 餘式定理 heading (para 131) precedes 例題6 (para 146); importer attached it to the previous section",
    12536: "基礎題6 evaluates f(12) by synthetic division, same type as 例題7 (餘式定理); exercises have no section heading",
}


def main() -> None:
    dry = "--dry" in sys.argv
    con = sqlite3.connect(DB, isolation_level=None)
    rows = {i: con.execute("select skill_id, source_paragraph, notes from textbook_examples where id=?", (i,)).fetchone() for i in BASIS}
    for i, (skill, para, notes) in rows.items():
        if skill != OLD or para != "多項式的四則運算":
            raise SystemExit(f"{i} no longer matches the investigated state: {skill} / {para}; stop")
    if not dry:
        backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit8_rebind_{datetime.now():%Y%m%d_%H%M%S}.db"
        dst = sqlite3.connect(backup)
        con.backup(dst)
        integrity = dst.execute("pragma integrity_check").fetchone()[0]
        dst.close()
        print("backup:", backup.name, "integrity:", integrity)
        if integrity != "ok":
            raise SystemExit("backup integrity failed")
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        con.execute("begin")
        for i, (skill, para, notes) in rows.items():
            n = json.loads(notes)
            n["skill_binding"] = {"source": "manual_topic_audit_unit8", "previous_skill_id": skill, "previous_source_paragraph": para,
                                  "basis": BASIS[i], "date": today}
            con.execute("update textbook_examples set skill_id=?, source_paragraph=?, notes=? where id=?",
                        (NEW, PARA, json.dumps(n, ensure_ascii=False), i))
        con.execute("rollback" if dry else "commit")
    except Exception:
        con.execute("rollback")
        raise
    print("rebound", sorted(BASIS), "dry" if dry else "committed")


if __name__ == "__main__":
    main()
