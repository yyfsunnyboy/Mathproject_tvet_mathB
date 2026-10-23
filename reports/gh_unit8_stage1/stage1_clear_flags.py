"""Unit 8 Stage 1：清除 6 題僅因 PDF 配對信心低而保留的 needs_review 旗標（題幹已逐題對 PDF 核對）。"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
PDF_SHA = "f48be281b1552afdb42f4c8577b9169f56e8d5a31e5c7c403117cc44c624a3c0"
TODAY = datetime.now().strftime("%Y-%m-%d")
# id -> PDF page of the stem
IDS = {12517: 2, 12531: 10, 12541: 12, 12542: 13, 12554: 16, 12555: 17}


def main() -> None:
    backup = ROOT / "instance" / "backups" / f"kumon_math_before_gh_unit8_clearflags_{datetime.now():%Y%m%d_%H%M%S}.db"
    src, dst = sqlite3.connect(DB), sqlite3.connect(backup)
    src.backup(dst)
    dst.close()
    src.close()
    print("backup:", backup.name)
    con = sqlite3.connect(DB, isolation_level=None)
    log = []
    try:
        con.execute("begin")
        for rid, page in IDS.items():
            desc, notes = con.execute("select source_description, notes from textbook_examples where id=?", (rid,)).fetchone()
            n = json.loads(notes)
            n["needs_review"] = False
            n["review_required_by_confidence"] = False
            n["manual_stem_review"] = {"date": TODAY, "source_pdf_sha256": PDF_SHA, "page": page,
                                       "result": "stem/conditions match PDF; flag was low match confidence only"}
            n.setdefault("repair_log", []).append(f"{TODAY} manual Stage1 review (unit8): needs_review cleared")
            desc = desc.replace(" | needs_review=true", "")
            con.execute("update textbook_examples set source_description=?, notes=? where id=?",
                        (desc, json.dumps(n, ensure_ascii=False), rid))
            log.append({"id": rid, "page": page, "fix": "needs_review cleared"})
        con.execute("commit")
    except Exception:
        con.execute("rollback")
        raise
    (ROOT / "reports" / "gh_unit8_stage1" / "stage1_clear_flags_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(log), "rows")


if __name__ == "__main__":
    main()
