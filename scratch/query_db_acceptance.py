# -*- coding: utf-8 -*-
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db = os.path.join(ROOT, "instance", "kumon_math.db")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== SKILL COUNTS ===")
cur.execute("SELECT COUNT(*) c FROM skills_info")
print("skills_info total:", cur.fetchone()["c"])
cur.execute("SELECT COUNT(*) c FROM skill_curriculum")
print("skill_curriculum total:", cur.fetchone()["c"])

print("\n=== FALLBACK SKILL IDS ===")
for pat in ["SelfAssessment", "MixedExercise", "Unknown", "Concept_", "SubSection_"]:
    cur.execute("SELECT skill_id, skill_ch_name FROM skills_info WHERE skill_id LIKE ? ORDER BY skill_id", (f"%{pat}%",))
    rows = cur.fetchall()
    print(pat, len(rows))
    for r in rows:
        print(" ", dict(r))

print("\n=== SELF ASSESSMENT TEXTBOOK EXAMPLES (latest 25) ===")
cur.execute(
    """
    SELECT te.id, te.skill_id, si.skill_ch_name, te.source_section, te.source_description, te.problem_type
    FROM textbook_examples te
    LEFT JOIN skills_info si ON si.skill_id = te.skill_id
    WHERE te.problem_type = 'self_assessment'
       OR te.source_description LIKE '%自我評量%'
       OR te.source_description LIKE '%CH1%'
    ORDER BY te.id DESC
    LIMIT 25
    """
)
for r in cur.fetchall():
    print(dict(r))

conn.close()
