# -*- coding: utf-8 -*-
"""Drop ignored 3-2 examples from houses/wrappers, then republish RemainderTheorem."""
from __future__ import annotations

import importlib.util
import json
import shutil
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
STAGING = ROOT / "reports" / "gencode_v3_publish_staging"
HOUSES = [
    ROOT / "agent_skills_v3" / SKILL / "components",
    ROOT / "reports" / "gencode_v3_dryrun" / SKILL / "components",
    STAGING / "agent_skills_v3" / SKILL / "components",
    STAGING / SKILL / "components",
]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    removed = []
    for house in HOUSES:
        if not house.is_dir():
            continue
        for eid in SKIP:
            dest = house / f"src_{eid}"
            if dest.exists():
                shutil.rmtree(dest)
                removed.append(str(dest))
    print("REMOVED", len(removed))
    for p in removed:
        print(" ", p)

    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    for eid in SKIP:
        save_tracker_record(
            conn,
            textbook_example_id=eid,
            skill_id=SKILL,
            gencode_status="needs_human_review",
            induced_spec_payload={
                "component_id": f"src_{eid}",
                "rebuild_decision": "EXCLUDE",
                "original_attempted_status": "skipped_source_incomplete",
                "ignored_by_operator": True,
            },
            gencode_error_log="SKIPPED_SOURCE_INCOMPLETE: ignored incomplete source",
        )
        try:
            update_status(conn, textbook_example_id=eid, skill_id=SKILL, gencode_status="needs_human_review")
        except Exception:
            pass
    conn.commit()

    verified = [
        int(r["textbook_example_id"])
        for r in conn.execute(
            "SELECT textbook_example_id FROM gencode_component_tracker WHERE skill_id=? AND gencode_status='verified' ORDER BY textbook_example_id",
            (SKILL,),
        ).fetchall()
    ]
    print("VERIFIED_TRACKER", verified, "n=", len(verified))

    pub = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=SKILL,
        project_root=str(ROOT),
        staging_root=str(STAGING.resolve()),
        force_publish=True,
        strict_coverage=False,
    )
    print("PUBLISH", pub.get("status"), "component_count", pub.get("component_count"))

    wrap = _load_module(ROOT / "skills" / f"{SKILL}.py", "wrap_remainder_after_drop")
    keys = list(getattr(wrap, "GENERATOR_KEYS", []) or [])
    extras = [k for k in keys if k in {f"src_{i}" for i in SKIP}]
    print("WRAPPER_KEYS", keys)
    print("WRAPPER_HAS_IGNORED", extras)

    spec = importlib.util.spec_from_file_location(
        "rebuild_b1_3_2_execute", ROOT / "scratch" / "_rebuild_b1_3_2_execute.py"
    )
    rebuild = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(rebuild)
    smoke_r = rebuild._smoke_skill(SKILL, 40)
    smoke_f = rebuild._smoke_skill("vh_數學B1_FactorTheorem", 40)
    print("SMOKE_R", smoke_r["passed"], "/", smoke_r["samples"], smoke_r.get("hits"))
    print("SMOKE_F", smoke_f["passed"], "/", smoke_f["samples"], smoke_f.get("hits"))

    out = {
        "removed": removed,
        "verified_tracker": verified,
        "publish_status": pub.get("status"),
        "wrapper_keys": keys,
        "wrapper_has_ignored": extras,
        "smoke_remainder": smoke_r,
        "smoke_factor": smoke_f,
    }
    path = ROOT / "scratch" / "_b1_3_2_drop_ignored_report.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
