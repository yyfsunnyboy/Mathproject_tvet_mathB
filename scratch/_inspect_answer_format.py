# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
conn = sqlite3.connect("instance/kumon_math.db")
conn.row_factory = sqlite3.Row

# sample verified choice answers format
for eid in [4628, 4706, 4716, 4717, 4718, 4719, 4720]:
    r = conn.execute("SELECT id, problem_text, correct_answer, detailed_solution FROM textbook_examples WHERE id=?", (eid,)).fetchone()
    print("="*40, eid)
    print(r["problem_text"])
    print("ANS:", r["correct_answer"])
    print("SOL:", r["detailed_solution"])

# how other self_assessment store answers
rows = conn.execute(
    """
    SELECT id, source_description, substr(problem_text,1,80) p, correct_answer
    FROM textbook_examples
    WHERE problem_type='self_assessment' AND correct_answer IS NOT NULL AND correct_answer != ''
    ORDER BY id DESC LIMIT 15
    """
).fetchall()
print("\nSAMPLE ANSWERS:")
for r in rows:
    print(r["id"], r["source_description"], "ans=", r["correct_answer"], "|", r["p"])
