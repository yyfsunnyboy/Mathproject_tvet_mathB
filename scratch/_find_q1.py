# -*- coding: utf-8 -*-
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
conn = sqlite3.connect("instance/kumon_math.db")
conn.row_factory = sqlite3.Row

# find self-assessment related and Q1-like
rows = conn.execute(
    """
    SELECT id, skill_id, source_description, problem_type, substr(problem_text,1,200) AS preview, correct_answer
    FROM textbook_examples
    WHERE source_description LIKE '%自我評量%'
       OR problem_text LIKE '%3x+5%'
       OR problem_text LIKE '%3x + 5%'
       OR problem_text LIKE '%h\\left( x \\right)=3x%'
       OR problem_text LIKE '%2{{x}^{2}}+9x+11%'
       OR problem_text LIKE '%f\\left( x \\right)\\times g\\left( x \\right)+2h%'
    ORDER BY id
    """
).fetchall()
print("hits", len(rows))
for r in rows:
    print(r["id"], r["source_description"], r["skill_id"], r["preview"], "| ans=", r["correct_answer"])

# also nearby ids 4700-4725
print("--- nearby ---")
for r in conn.execute(
    "SELECT id, source_description, substr(problem_text,1,120) p FROM textbook_examples WHERE id BETWEEN 4700 AND 4725 ORDER BY id"
).fetchall():
    print(r["id"], r["source_description"], r["p"])
