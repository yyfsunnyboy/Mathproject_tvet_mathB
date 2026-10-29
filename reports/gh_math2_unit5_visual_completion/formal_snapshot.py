"""Content snapshot of the formal DB textbook tables (read-only, mode=ro): before / after the isolated work.

    python formal_snapshot.py before|after
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FORMAL = ROOT / "instance/kumon_math.db"
TABLES = ("textbook_examples", "skills_info", "skill_curriculum")


def snapshot() -> dict:
    con = sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True)
    try:
        out = {}
        for t in TABLES:
            h = hashlib.sha256()
            n = 0
            for row in con.execute(f"select * from {t} order by rowid"):
                h.update(json.dumps(row, ensure_ascii=False, default=str).encode("utf-8"))
                n += 1
            out[t] = {"rows": n, "sha256": h.hexdigest()}
        out["unit5_rows"] = con.execute("select count(*) from textbook_examples where source_curriculum='general' and source_volume='數學2' "
                                        "and source_chapter='單元5 組合'").fetchone()[0]
        return out
    finally:
        con.close()


if __name__ == "__main__":
    stage = sys.argv[1]
    snap = snapshot()
    path = HERE / "formal_db_snapshot.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data[stage] = snap
    if "before" in data and "after" in data:
        data["zero_change"] = data["before"] == data["after"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(stage, json.dumps(snap, ensure_ascii=False), "| zero_change:", data.get("zero_change"))
