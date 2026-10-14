# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
OUT = ROOT / "scratch" / "_b2_1_1_db_audit.json"

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")]
te_cols = [r[1] for r in cur.execute("PRAGMA table_info(textbook_examples)")]

rows = cur.execute(
    """
    SELECT *
    FROM textbook_examples
    WHERE skill_id LIKE 'vh_數學B2_%'
       OR IFNULL(source_section,'') LIKE '%1-1%'
       OR IFNULL(source_description,'') LIKE '%1-1%'
       OR CAST(IFNULL(source_volume,'') AS TEXT) LIKE '%B2%'
    ORDER BY id
    """
).fetchall()

examples = []
for r in rows:
    d = dict(r)
    examples.append(
        {
            "id": d.get("id"),
            "skill_id": d.get("skill_id"),
            "source_description": d.get("source_description"),
            "source_volume": d.get("source_volume"),
            "source_chapter": d.get("source_chapter"),
            "source_section": d.get("source_section"),
            "problem_text": d.get("problem_text") or "",
            "correct_answer": d.get("correct_answer") or "",
            "detailed_solution": d.get("detailed_solution") or "",
            "ca_len": len(str(d.get("correct_answer") or "")),
            "ds_len": len(str(d.get("detailed_solution") or "")),
        }
    )

b2_skills = [
    dict(r)
    for r in cur.execute(
        "SELECT skill_id, COUNT(*) AS c FROM textbook_examples WHERE skill_id LIKE 'vh_數學B2_%' GROUP BY 1"
    )
]

skills_info = []
if "skills_info" in tables:
    skills_info = [
        dict(r)
        for r in cur.execute("SELECT * FROM skills_info WHERE skill_id LIKE 'vh_數學B2_%'")
    ]

skill_curriculum = []
if "skill_curriculum" in tables:
    skill_curriculum = [
        dict(r)
        for r in cur.execute("SELECT * FROM skill_curriculum WHERE skill_id LIKE 'vh_數學B2_%'")
    ]

tracker = []
if "gencode_component_tracker" in tables:
    tracker = [
        dict(r)
        for r in cur.execute(
            """
            SELECT textbook_example_id, skill_id, component_id, gencode_status,
                   substr(IFNULL(gencode_error_log,''),1,200) AS err
            FROM gencode_component_tracker
            WHERE skill_id LIKE 'vh_數學B2_%'
               OR textbook_example_id BETWEEN 11500 AND 11750
            ORDER BY textbook_example_id
            """
        )
    ]

# also dump 1-2 vs 1-1 split by section
sec_counts = [
    dict(r)
    for r in cur.execute(
        """
        SELECT source_section, skill_id, COUNT(*) AS c
        FROM textbook_examples
        WHERE skill_id LIKE 'vh_數學B2_%'
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
    )
]

payload = {
    "db_exists": DB.exists(),
    "tables_count": len(tables),
    "te_cols": te_cols,
    "example_count": len(examples),
    "b2_skills": b2_skills,
    "sec_counts": sec_counts,
    "skills_info": skills_info,
    "skill_curriculum": skill_curriculum,
    "tracker": tracker,
    "examples": examples,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", OUT, "examples", len(examples), "skills_info", len(skills_info), "curriculum", len(skill_curriculum), "tracker", len(tracker))
