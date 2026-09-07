# -*- coding: utf-8 -*-
"""Read-only scope + dependency check for B1 3-1 quarantine (before any write)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

EXPECTED = [
    4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620,
    4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632,
    4633, 4634, 4635, 4636, 4637, 4706, 4716, 4717, 4718, 4719, 4720,
]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Discover 3-1 via source_description / section if possible
rows = conn.execute(
    """
    SELECT id, skill_id, problem_type, source_description,
           substr(coalesce(problem_text,''),1,40) AS preview
    FROM textbook_examples
    WHERE id IN ({})
    ORDER BY id
    """.format(",".join("?" * len(EXPECTED))),
    EXPECTED,
).fetchall()

found_ids = [int(r["id"]) for r in rows]
missing_from_db = [i for i in EXPECTED if i not in found_ids]
extra = []  # if we find more 3-1 later

# Also search by source patterns for 3-1
cand = conn.execute(
    """
    SELECT id, skill_id, source_description FROM textbook_examples
    WHERE skill_id LIKE '%PolynomialBasicConcepts%'
       OR skill_id LIKE '%PolynomialArithmeticOperations%'
       OR skill_id LIKE '%PolynomialEquality%'
    ORDER BY id
    """
).fetchall()
skill_all_ids = [int(r["id"]) for r in cand]
extra_in_skills = [i for i in skill_all_ids if i not in EXPECTED]
missing_in_skills = [i for i in EXPECTED if i not in skill_all_ids]

# tracker
tracker_cols = [c[1] for c in conn.execute("PRAGMA table_info(gencode_component_tracker)").fetchall()]
tracker_rows = []
if tracker_cols:
    placeholders = ",".join("?" * len(EXPECTED))
    id_col = "textbook_example_id" if "textbook_example_id" in tracker_cols else None
    if id_col:
        tracker_rows = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM gencode_component_tracker WHERE textbook_example_id IN ({placeholders})",
                EXPECTED,
            ).fetchall()
        ]

out = {
    "expected_count": len(EXPECTED),
    "found_count": len(found_ids),
    "missing_from_db": missing_from_db,
    "extra_in_three_skills": extra_in_skills,
    "missing_in_three_skills": missing_in_skills,
    "skill_all_count": len(skill_all_ids),
    "tracker_count": len(tracker_rows),
    "tracker_cols": tracker_cols,
    "rows": [dict(r) for r in rows],
    "scope_match": found_ids == EXPECTED and not missing_from_db and set(found_ids) == set(EXPECTED),
}
# exact match ordered
out["ids_equal_ordered"] = found_ids == EXPECTED
out["ids_equal_set"] = set(found_ids) == set(EXPECTED)

(ROOT / "scratch" / "_b1_3_1_scope_verify.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("found", len(found_ids), "expected", len(EXPECTED))
print("missing_from_db", missing_from_db)
print("extra_in_skills", extra_in_skills)
print("missing_in_skills", missing_in_skills)
print("tracker", len(tracker_rows))
print("scope_match_set", out["ids_equal_set"])
for r in rows:
    print(r["id"], r["skill_id"], (r["source_description"] or "")[:40])
