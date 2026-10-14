import sqlite3
from collections import Counter

from core.mathb_chapter4_calculator_skip import question_requires_calculator

con = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
rows = con.execute(
    "SELECT id, skill_id, problem_text FROM textbook_examples WHERE id BETWEEN 12127 AND 12272 ORDER BY id"
).fetchall()
flagged = [r[0] for r in rows if question_requires_calculator(r[2] or "")]
dup = Counter((r[1], (r[2] or "").strip()) for r in rows)
print("rows", len(rows), "calculator_required", len(flagged), flagged)
print("duplicate (skill, stem) pairs", sum(1 for v in dup.values() if v > 1))
print("distinct ids", len({r[0] for r in rows}))
