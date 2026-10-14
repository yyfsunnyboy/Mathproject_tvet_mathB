# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(root / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """
    SELECT id, skill_id, source_description, source_section, source_chapter,
           source_volume, problem_type, correct_answer, problem_text
    FROM textbook_examples
    WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'
    ORDER BY id
    """
).fetchall()
print("ALL_3_3", len(rows))
for r in rows:
    desc = str(r["source_description"] or "")
    if any(tok in desc for tok in ("自我評量", "題16", "題18")):
        print("=" * 60)
        print("id", r["id"])
        print("skill_id", r["skill_id"])
        print("desc", desc)
        print("section", r["source_section"])
        print("chapter", r["source_chapter"])
        print("volume", r["source_volume"])
        print("problem_type", r["problem_type"])
        print("correct_answer", r["correct_answer"])
        print("problem_text", r["problem_text"])
for eid in (4713, 4715):
    r = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
    print("ROW", eid, "FOUND" if r else "MISSING")
