# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row

rows = conn.execute(
    """
    SELECT * FROM textbook_examples
    WHERE source_volume LIKE '%B1%'
      AND source_section LIKE '3-2%'
      AND (
        source_description LIKE '%112統測%'
        OR problem_text LIKE '%(x+2)%'
        OR problem_text LIKE '%x+2%x-7%'
        OR problem_text LIKE '%ax+3%'
        OR problem_text LIKE '%ax + 3%'
      )
    ORDER BY id
    """
).fetchall()
out = [dict(r) for r in rows]
(ROOT / "scratch" / "_b1_3_2_112_candidates.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("n=", len(out))
for r in out:
    print(r["id"], r["skill_id"], r["source_description"], r.get("correct_answer"))
