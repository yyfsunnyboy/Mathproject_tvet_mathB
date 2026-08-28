# -*- coding: utf-8 -*-
"""Dump B1 chapter 3 textbook examples for domain design."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import Config

OUT = ROOT / "scratch" / "_b1_ch3_examples.json"

con = sqlite3.connect(Config.db_path)
con.row_factory = sqlite3.Row
rows = con.execute(
    """
    SELECT te.id, te.skill_id, te.source_section, te.source_description,
           te.problem_type, te.problem_text, te.correct_answer,
           substr(te.detailed_solution, 1, 200) AS solution_preview
    FROM textbook_examples te
    JOIN skill_curriculum sc ON sc.skill_id = te.skill_id
    WHERE te.skill_id LIKE 'vh_%B1_%' AND sc.chapter LIKE '3 %'
    ORDER BY sc.section, sc.display_order, te.id
    """
).fetchall()
payload = [dict(r) for r in rows]
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
# compact preview by skill
by = {}
for r in payload:
    by.setdefault(r["skill_id"], []).append(
        {
            "id": r["id"],
            "desc": r["source_description"],
            "type": r["problem_type"],
            "stem": (r["problem_text"] or "")[:180].replace("\n", " "),
            "ans": (r["correct_answer"] or "")[:120].replace("\n", " "),
        }
    )
print(json.dumps({k: {"n": len(v), "samples": v[:3]} for k, v in by.items()}, ensure_ascii=False, indent=2))
print("wrote", OUT, "total", len(payload))
