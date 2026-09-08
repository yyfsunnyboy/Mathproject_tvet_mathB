# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """
    SELECT id, skill_id, source_description, source_section, source_chapter,
           problem_type, correct_answer, problem_text
    FROM textbook_examples
    WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'
    ORDER BY id
    """
).fetchall()
out = []
print("COUNT", len(rows))
for r in rows:
    d = dict(r)
    desc = str(d["source_description"] or "")
    text = str(d["problem_text"] or "")
    mark = ""
    if any(tok in desc for tok in ("題16", "題 16", "題18", "題 18")):
        mark = " TARGET"
    print(f"{d['id']}\t{d['skill_id']}\t{desc}\ttype={d['problem_type']}\tans={d['correct_answer']!r}{mark}")
    if mark or "評量" in desc:
        print(" ", text[:240])
    out.append(d)
(ROOT / "scratch" / "_inspect_b1_3_3_q16_q18.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
