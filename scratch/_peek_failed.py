# -*- coding: utf-8 -*-
import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect("instance/kumon_math.db")
conn.row_factory = sqlite3.Row
tabs = [t[0] for t in conn.execute("select name from sqlite_master where type='table'").fetchall()]
print("tracker-ish", [t for t in tabs if "track" in t.lower() or "gencode" in t.lower()])
# find tracker
for t in tabs:
    if "component" in t.lower() or "tracker" in t.lower():
        cols = [c[1] for c in conn.execute(f"pragma table_info({t})").fetchall()]
        print(t, cols[:12])

for eid in [4628, 4718, 4719, 4720]:
    for t in tabs:
        if "tracker" in t.lower() or t == "gencode_component_tracker":
            try:
                row = conn.execute(f"select * from {t} where textbook_example_id=?", (eid,)).fetchone()
            except Exception:
                continue
            if row:
                d = dict(row)
                print("EID", eid, "status", d.get("gencode_status"), "err", (d.get("gencode_error_log") or "")[:300])
                break
    # also question text snippet
    for t in ("textbook_examples",):
        if t in tabs:
            cols = [c[1] for c in conn.execute(f"pragma table_info({t})").fetchall()]
            qcol = "question_text" if "question_text" in cols else ("stem" if "stem" in cols else None)
            if qcol:
                r = conn.execute(f"select id, skill_id, substr({qcol},1,120) q from {t} where id=?", (eid,)).fetchone()
                if r:
                    print("SRC", eid, r["skill_id"], r["q"])
