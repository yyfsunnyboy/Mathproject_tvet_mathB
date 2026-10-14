# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (4680,)).fetchone()
d = dict(row) if row else None
out = ROOT / "scratch" / "_inspect_b1_3_3_4680.json"
out.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("FOUND" if d else "MISSING")
if d:
    print("skill_id", d["skill_id"])
    print("source_description", d["source_description"])
    print("problem_type", d["problem_type"])
    print("correct_answer", repr(d["correct_answer"]))
    print("chapter", d["source_chapter"])
    print("section", d["source_section"])
    print("paragraph", d["source_paragraph"])
    print("problem_text")
    print(d["problem_text"])
    print("LEN", len(d["problem_text"] or ""))
