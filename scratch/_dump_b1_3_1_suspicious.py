# -*- coding: utf-8 -*-
"""Dump suspicious 3-1 texts for manual feasibility review."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(ROOT / "instance" / "kumon_math.db")
conn.row_factory = sqlite3.Row
ids = [4618, 4629, 4706, 4716, 4717, 4628, 4718, 4719, 4720, 4609, 4620]
out = []
for eid in ids:
    r = conn.execute(
        "SELECT id, skill_id, problem_type, source_description, problem_text, correct_answer, detailed_solution, source_paragraph FROM textbook_examples WHERE id=?",
        (eid,),
    ).fetchone()
    out.append({k: r[k] for k in r.keys()})

(ROOT / "scratch" / "_b1_3_1_suspicious_texts.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
for r in out:
    print("=" * 60, r["id"], r["source_description"])
    print("TYPE", r["problem_type"])
    print("TEXT:", r["problem_text"])
    print("ANS:", (r["correct_answer"] or "")[:200])
    print("SOL preview:", (r["detailed_solution"] or "")[:150].replace("\n", " "))
    print("source_paragraph type/len:", type(r["source_paragraph"]).__name__, len(str(r["source_paragraph"] or "")))
