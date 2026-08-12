# -*- coding: utf-8 -*-
"""Validation-only reconcile for inventory-selected B1-B4 repairable examples."""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.v3_artifact_reconciliation_service import (
    reconcile_existing_artifacts,
)

INVENTORY = ROOT / "reports" / "gencode_closed_loop" / "b1_b4_full_lifecycle_inventory.json"


def _targets_from_inventory() -> dict[str, list[int]]:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    items = {int(i["textbook_example_id"]): i for i in data["items"]}
    grouped: dict[str, list[int]] = defaultdict(list)
    for eid in data.get("repairable_ids") or []:
        item = items[int(eid)]
        grouped[str(item["skill_id"])].append(int(eid))
    return {skill: sorted(ids) for skill, ids in sorted(grouped.items())}


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    commit = "--commit" in args
    targets = _targets_from_inventory()
    out_path = ROOT / "reports" / "gencode_closed_loop" / (
        "b1_b4_artifact_reconciliation_commit.json"
        if commit
        else "b1_b4_artifact_reconciliation_dryrun.json"
    )
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    try:
        result = reconcile_existing_artifacts(
            conn=conn,
            targets=targets,
            project_root=ROOT,
            commit=commit,
        )
    finally:
        conn.close()

    result["targets"] = targets
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "commit": result["commit"],
                "total": result["total"],
                "passed_count": result["passed_count"],
                "failed_count": result["failed_count"],
                "synced_count": result["synced_count"],
                "all_passed": result["all_passed"],
                "all_hashes_unchanged": result["all_hashes_unchanged"],
                "targets": targets,
                "report": str(out_path),
                "failed_ids": [
                    row["textbook_example_id"]
                    for row in result["components"]
                    if not row.get("passed")
                ],
                "blockers_preview": {
                    str(row["textbook_example_id"]): (row.get("blockers") or [])[:8]
                    for row in result["components"]
                    if not row.get("passed")
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if result["all_passed"] and result["all_hashes_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
