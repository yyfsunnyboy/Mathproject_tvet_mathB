# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config

sid = "vh_數學B1_SubSection332"
con = sqlite3.connect(Config.db_path)
con.row_factory = sqlite3.Row
out = {"skill_id": sid, "db": Config.db_path}

row = con.execute(
    "SELECT skill_id, skill_ch_name, skill_en_name, is_active, input_type FROM skills_info WHERE skill_id=?",
    (sid,),
).fetchone()
out["skills_info"] = dict(row) if row else None

curr = con.execute("SELECT * FROM skill_curriculum WHERE skill_id=?", (sid,)).fetchone()
out["curriculum"] = dict(curr) if curr else None

ex = [
    dict(r)
    for r in con.execute(
        "SELECT id, source_section, source_description, substr(problem_text,1,120) AS pt FROM textbook_examples WHERE skill_id=? ORDER BY id",
        (sid,),
    )
]
out["example_count"] = len(ex)
out["examples"] = ex

neighbors = [
    dict(r)
    for r in con.execute(
        """
        SELECT te.skill_id, COUNT(*) AS n
        FROM textbook_examples te
        JOIN skill_curriculum sc ON sc.skill_id = te.skill_id
        WHERE sc.chapter LIKE '3 %' AND sc.section LIKE '3-3%'
        GROUP BY te.skill_id
        ORDER BY te.skill_id
        """
    )
]
out["section_33_example_counts"] = neighbors
out["wrapper"] = (ROOT / "skills" / f"{sid}.py").is_file()
out["v3_dir"] = (ROOT / "agent_skills_v3" / sid).is_dir()

frac = [
    dict(r)
    for r in con.execute(
        """
        SELECT id, skill_id, source_section, source_description
        FROM textbook_examples
        WHERE (problem_text LIKE '%分式%' OR source_description LIKE '%分式%' OR source_section LIKE '%分式%')
          AND skill_id LIKE 'vh_%B1_%'
        ORDER BY id
        LIMIT 50
        """
    )
]
out["fraction_related_examples_sample"] = frac

# curriculum siblings under 3-3
sibs = [
    dict(r)
    for r in con.execute(
        """
        SELECT skill_id, section, display_order
        FROM skill_curriculum
        WHERE chapter LIKE '3 %' AND section LIKE '3-3%'
        ORDER BY display_order, skill_id
        """
    )
]
out["section_33_skills"] = sibs

Path(ROOT / "scratch" / "_subsection332_probe.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
print(json.dumps({k: out[k] for k in out if k != "fraction_related_examples_sample"}, ensure_ascii=False, indent=2))
print("fraction_related_count_sample", len(frac))
for r in frac[:15]:
    print(r)
