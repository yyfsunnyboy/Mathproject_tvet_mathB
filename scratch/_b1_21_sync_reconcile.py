# -*- coding: utf-8 -*-
"""B1 section 2-1: sync production → dryrun, then validation-only reconcile."""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.v3_artifact_reconciliation_service import reconcile_existing_artifacts

SKILLS = (
    "vh_數學B1_SlopeOfALine",
    "vh_數學B1_PropertiesOfParallelLines",
    "vh_數學B1_PropertiesOfPerpendicularLines",
)
DRY = ROOT / "reports" / "gencode_v3_dryrun"
PROD = ROOT / "agent_skills_v3"
OUT_DIR = ROOT / "reports" / "gencode_closed_loop"


def _example_ids(conn: sqlite3.Connection, skill_id: str) -> list[int]:
    return [
        int(r[0])
        for r in conn.execute(
            "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
            (skill_id,),
        ).fetchall()
    ]


def _sync_skill(skill_id: str, example_ids: list[int]) -> list[dict]:
    log = []
    src_skill = PROD / skill_id
    dst_skill = DRY / skill_id
    dst_skill.mkdir(parents=True, exist_ok=True)
    for helper in ("component_runtime.py", "component_hint.py", "component_manifest.json", "__init__.py"):
        src_h = src_skill / helper
        if src_h.is_file():
            shutil.copy2(src_h, dst_skill / helper)
    for eid in example_ids:
        cid = f"src_{eid}"
        src = src_skill / "components" / cid
        dst = dst_skill / "components" / cid
        if not src.is_dir():
            log.append({"id": eid, "synced": False, "reason": "missing_production"})
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        log.append({"id": eid, "synced": True, "component_id": cid})
    return log


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--skip-sync", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    targets: dict[str, list[int]] = {}
    sync_log: dict[str, list] = {}
    for skill_id in SKILLS:
        ids = _example_ids(conn, skill_id)
        targets[skill_id] = ids
        if not args.skip_sync:
            sync_log[skill_id] = _sync_skill(skill_id, ids)

    result = reconcile_existing_artifacts(
        conn=conn,
        targets=targets,
        project_root=ROOT,
        commit=bool(args.commit),
    )
    if args.commit:
        conn.commit()
    conn.close()

    out = {
        "commit": bool(args.commit),
        "sync_log": sync_log,
        "total": result.get("total"),
        "passed_count": result.get("passed_count"),
        "failed_count": result.get("failed_count"),
        "synced_count": result.get("synced_count"),
        "all_hashes_unchanged": result.get("all_hashes_unchanged"),
        "failed_ids": [
            c.get("textbook_example_id")
            for c in (result.get("components") or [])
            if not c.get("passed")
        ],
        "blockers": {
            str(c.get("textbook_example_id")): c.get("blockers")
            for c in (result.get("components") or [])
            if not c.get("passed")
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / (
        "b1_21_sync_reconcile_commit.json" if args.commit else "b1_21_sync_reconcile_dryrun.json"
    )
    path.write_text(json.dumps({**out, "components": result.get("components")}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({**out, "report": str(path)}, ensure_ascii=False, indent=2))
    return 0 if not out["failed_ids"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
