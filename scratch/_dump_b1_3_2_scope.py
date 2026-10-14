# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cols = [c[1] for c in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
print("COLS", cols)
rows = conn.execute(
    """
    SELECT id, skill_id, source_description, problem_text, correct_answer,
           problem_type, source_paragraph, source_section, source_chapter,
           source_volume
    FROM textbook_examples
    WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-2%'
    ORDER BY id
    """
).fetchall()
print("COUNT", len(rows))
print("SKILLS", dict(Counter(r["skill_id"] for r in rows)))
print("TYPES", dict(Counter(r["problem_type"] for r in rows)))
out = []
for r in rows:
    t = r["problem_text"] or ""
    rec = {
        "example_id": r["id"],
        "skill_id": r["skill_id"],
        "source_description": r["source_description"],
        "problem_type": r["problem_type"],
        "source_paragraph": r["source_paragraph"],
        "correct_answer": r["correct_answer"],
        "problem_text": t,
        "text_len": len(t),
    }
    out.append(rec)
    print("---", r["id"], r["skill_id"], r["problem_type"], r["source_description"])
    print("ans=", r["correct_answer"])
    print(t[:320].replace("\n", " / "))
    print()

(ROOT / "scratch" / "_b1_3_2_scope_dump.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("wrote scratch/_b1_3_2_scope_dump.json")
