# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.services.component_tracker_service import save_tracker_record, update_status

SKIP = [4638, 4640, 4664, 4666]
SKILL = "vh_數學B1_RemainderTheorem"
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())

conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
print("BEFORE")
for eid in SKIP:
    rows = conn.execute(
        "SELECT textbook_example_id, component_id, gencode_status FROM gencode_component_tracker WHERE textbook_example_id=?",
        (eid,),
    ).fetchall()
    print(eid, [dict(r) for r in rows])
    save_tracker_record(
        conn,
        textbook_example_id=eid,
        skill_id=SKILL,
        gencode_status="needs_human_review",
        induced_spec_payload={
            "component_id": f"src_{eid}",
            "rebuild_decision": "EXCLUDE",
            "original_attempted_status": "skipped_source_incomplete",
        },
        gencode_error_log="SKIPPED_SOURCE_INCOMPLETE: f(x) undefined",
    )
    try:
        update_status(conn, textbook_example_id=eid, skill_id=SKILL, gencode_status="needs_human_review")
    except Exception:
        pass
conn.commit()
print("AFTER")
rows = conn.execute(
    "SELECT textbook_example_id, component_id, gencode_status FROM gencode_component_tracker WHERE skill_id=? AND gencode_status='verified' ORDER BY textbook_example_id",
    (SKILL,),
).fetchall()
print("verified", [int(r["textbook_example_id"]) for r in rows], "n=", len(rows))

pub = run_admin_v3_publish_for_skill(
    conn=conn,
    skill_id=SKILL,
    project_root=str(ROOT),
    staging_root=STAGING,
    force_publish=True,
    strict_coverage=False,
)
print("PUBLISH", pub.get("status"))
