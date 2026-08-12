# -*- coding: utf-8 -*-
"""Report-only / commit runner for AbsoluteValue artifact reconciliation."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.v3_artifact_reconciliation_service import (
    DEFAULT_RECONCILE_TARGETS,
    reconcile_existing_artifacts,
)


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    commit = "--commit" in args
    db_path = ROOT / "instance" / "kumon_math.db"
    out_path = ROOT / "reports" / "gencode_closed_loop" / (
        "absolute_value_artifact_reconciliation_commit.json"
        if commit
        else "absolute_value_artifact_reconciliation_dryrun.json"
    )
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        result = reconcile_existing_artifacts(
            conn=conn,
            targets=DEFAULT_RECONCILE_TARGETS,
            project_root=ROOT,
            commit=commit,
        )
    finally:
        conn.close()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "commit": result["commit"],
        "total": result["total"],
        "passed_count": result["passed_count"],
        "failed_count": result["failed_count"],
        "synced_count": result["synced_count"],
        "all_passed": result["all_passed"],
        "all_hashes_unchanged": result["all_hashes_unchanged"],
        "report": str(out_path),
        "failed_ids": [
            row["textbook_example_id"]
            for row in result["components"]
            if not row.get("passed")
        ],
        "blockers_preview": {
            str(row["textbook_example_id"]): row.get("blockers")[:5]
            for row in result["components"]
            if not row.get("passed")
        },
    }, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] and result["all_hashes_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
