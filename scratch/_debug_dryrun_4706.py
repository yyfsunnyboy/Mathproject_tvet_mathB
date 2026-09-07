# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example

conn = sqlite3.connect("instance/kumon_math.db")
conn.row_factory = sqlite3.Row
eid = 4706
row = conn.execute("SELECT skill_id FROM textbook_examples WHERE id=?", (eid,)).fetchone()
dry = run_admin_v3_dryrun_for_example(
    conn=conn,
    textbook_example_id=eid,
    skill_id=row["skill_id"],
    dryrun_base_dir="reports/gencode_v3_dryrun",
    seed=7,
    allow_non_mvp_skill=True,
    force_regenerate=True,
)
print(json.dumps(dry, ensure_ascii=False, indent=2, default=str)[:4000])
