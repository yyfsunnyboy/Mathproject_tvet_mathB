# -*- coding: utf-8 -*-
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db = os.path.join(ROOT, "instance", "kumon_math.db")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute(
    """
    SELECT id, skill_id, source_section, source_description
    FROM textbook_examples
    WHERE source_description LIKE '%CH1自我評量%'
       OR source_description LIKE '%第1章自我評量%'
    ORDER BY id
    """
)
print("=== ALL CH1 self-assessment rows ===")
for r in cur.fetchall():
    print(dict(r))

cur.execute("SELECT skill_id FROM skills_info")
all_skills = [r[0] for r in cur.fetchall()]
print("\n=== Fallback literal substring check ===")
for pat in ["SelfAssessment", "MixedExercise", "UnknownConcept", "UnknownFormalConcept", "Concept_", "SubSection_"]:
    hits = [s for s in all_skills if pat in s]
    print(f"{pat}: {len(hits)}")
    for h in hits:
        print(f"  {h}")

conn.close()
