# -*- coding: utf-8 -*-
"""Dump B1 3-3 textbook_examples scope. Read-only."""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
OUT = ROOT / "scratch" / "_b1_3_3_scope_dump.json"

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cols = [c[1] for c in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
print("COLS", cols)

rows = conn.execute(
    """
    SELECT *
    FROM textbook_examples
    WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'
    ORDER BY id
    """
).fetchall()
print("COUNT", len(rows))
data = []
for r in rows:
    d = dict(r)
    data.append(d)
    print(
        f"{d['id']}\t{d['skill_id']}\t{d['source_description']}\t"
        f"type={d['problem_type']}\tans={d['correct_answer']!r}\t"
        f"len={len(d['problem_text'] or '')}"
    )
    print("  ", (d["problem_text"] or "").replace("\n", " ")[:220])

skills = Counter(d["skill_id"] for d in data)
print("SKILLS", dict(skills))

# tracker / existing components
try:
    tr = conn.execute(
        """
        SELECT textbook_example_id, skill_id, gencode_status, component_id
        FROM gencode_component_tracker
        WHERE textbook_example_id IN ({})
        """.format(",".join("?" * len(data))),
        [d["id"] for d in data],
    ).fetchall()
    print("TRACKER", len(tr))
    for t in tr:
        print(" ", dict(t))
except Exception as e:
    print("TRACKER_ERR", e)

OUT.write_text(json.dumps({"count": len(data), "skills": dict(skills), "rows": data}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print("WROTE", OUT)
