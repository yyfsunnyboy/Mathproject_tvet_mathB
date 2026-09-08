# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row

ids = [4721, 4722, 4707, 4708, 4709, 4710, 4711, 4712]
out = []
for eid in ids:
    r = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
    t = (r.get("problem_text") or "").replace("（", "(").replace("）", ")")
    out.append(
        {
            "id": r["id"],
            "skill_id": r["skill_id"],
            "source_description": r["source_description"],
            "source_section": r["source_section"],
            "source_paragraph": r["source_paragraph"],
            "problem_type": r["problem_type"],
            "correct_answer": r["correct_answer"],
            "problem_text": r["problem_text"],
            "has_A": "(A)" in t,
            "has_B": "(B)" in t,
            "has_C": "(C)" in t,
            "has_D": "(D)" in t,
        }
    )

scope = [
    {
        "id": r["id"],
        "skill_id": r["skill_id"],
        "source_description": r["source_description"],
        "problem_type": r["problem_type"],
    }
    for r in conn.execute(
        """
        SELECT id, skill_id, source_description, problem_type
        FROM textbook_examples
        WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-2%'
        ORDER BY id
        """
    )
]
(ROOT / "scratch" / "_b1_3_2_after_select.json").write_text(
    json.dumps({"repaired": out, "scope": scope}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("wrote after select", len(out), "scope", len(scope))
