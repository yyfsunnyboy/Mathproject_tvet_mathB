# -*- coding: utf-8 -*-
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")
c = sqlite3.connect("instance/kumon_math.db")
c.row_factory = sqlite3.Row
sql = """
SELECT id, skill_id, source_description, source_section, source_chapter,
       substr(problem_text,1,180) p, correct_answer
FROM textbook_examples
WHERE source_description LIKE '%自我評量%'
  AND (
    skill_id LIKE '%Polynomial%'
    OR source_paragraph LIKE '%多項式%'
    OR problem_text LIKE '%f\\left( x \\right)=x+1%'
    OR problem_text LIKE '%2{{x}^{2}}+9x+11%'
    OR problem_text LIKE '%h\\left( x \\right)=3x+5%'
  )
ORDER BY id
"""
rows = c.execute(sql).fetchall()
print("n=", len(rows))
for r in rows:
    print(r["id"], r["source_description"], r["skill_id"], r["source_section"], r["p"], "|", r["correct_answer"])

print("--- Q1-like ---")
for r in c.execute(
    """
    SELECT id, skill_id, source_description, substr(problem_text,1,200) p
    FROM textbook_examples
    WHERE problem_text LIKE '%2x+1%' AND problem_text LIKE '%3x+5%'
       OR problem_text LIKE '%2{{x}}+1%' AND problem_text LIKE '%3{{x}}+5%'
       OR (problem_text LIKE '%f\\left( x \\right)=x+1%' AND problem_text LIKE '%g\\left( x \\right)=2x+1%')
    """
).fetchall():
    print(r["id"], r["source_description"], r["skill_id"], r["p"])
