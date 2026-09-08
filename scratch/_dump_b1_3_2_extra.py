# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row

skills = conn.execute(
    """
    SELECT DISTINCT skill_id FROM textbook_examples
    WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-2%'
    ORDER BY skill_id
    """
).fetchall()

extra = conn.execute(
    """
    SELECT id, skill_id, source_section, source_description, substr(problem_text,1,80) AS p
    FROM textbook_examples
    WHERE skill_id IN (
      'vh_數學B1_RemainderTheorem',
      'vh_數學B1_FactorTheorem',
      'vh_數學B1_DivisionAlgorithm',
      'vh_數學B1_SubSection322'
    )
    AND id NOT IN (SELECT id FROM textbook_examples WHERE source_section LIKE '3-2%')
    ORDER BY id
    """
).fetchall()

ids = [r["id"] for r in conn.execute(
    "SELECT id FROM textbook_examples WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-2%' ORDER BY id"
)]

out = {
    "skills": [r["skill_id"] for r in skills],
    "ids": ids,
    "count": len(ids),
    "extra_same_skill_not_3_2": [dict(r) for r in extra],
}
(ROOT / "scratch" / "_b1_3_2_scope_meta.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("wrote meta", out["count"], out["skills"])
