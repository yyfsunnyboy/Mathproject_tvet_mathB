# -*- coding: utf-8 -*-
"""Read-only inventory for B1 section 2-1 Gencode artifacts."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.gencode.services.gencode_status_query_service import (
    build_admin_examples_gencode_status_map,
    build_admin_skills_gencode_status_map,
)

SKILLS = (
    "vh_數學B1_SlopeOfALine",
    "vh_數學B1_PropertiesOfParallelLines",
    "vh_數學B1_PropertiesOfPerpendicularLines",
)
DRY = ROOT / "reports" / "gencode_v3_dryrun"
PROD = ROOT / "agent_skills_v3"
OUT = ROOT / "scratch" / "_b1_21_inventory.json"


def sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    skill_status = build_admin_skills_gencode_status_map(conn, list(SKILLS))
    payload: dict = {"skills": {}}
    for skill_id in SKILLS:
        examples = [
            int(r[0])
            for r in conn.execute(
                "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
                (skill_id,),
            ).fetchall()
        ]
        rows = []
        for eid in examples:
            cid = f"src_{eid}"
            dry = DRY / skill_id / "components" / cid / "generate.py"
            prod = PROD / skill_id / "components" / cid / "generate.py"
            dry_h = sha(dry)
            prod_h = sha(prod)
            tracker = conn.execute(
                """
                SELECT gencode_status, gencode_error_log
                FROM gencode_component_tracker
                WHERE textbook_example_id = ?
                """,
                (eid,),
            ).fetchone()
            rows.append(
                {
                    "id": eid,
                    "component_id": cid,
                    "dryrun": dry_h is not None,
                    "production": prod_h is not None,
                    "hash_aligned": bool(dry_h and prod_h and dry_h == prod_h),
                    "dry_only": dry_h is not None and prod_h is None,
                    "prod_only": prod_h is not None and dry_h is None,
                    "tracker_status": None if tracker is None else tracker["gencode_status"],
                    "tracker_error": None if tracker is None else tracker["gencode_error_log"],
                    "dry_hash": dry_h,
                    "prod_hash": prod_h,
                }
            )
        view = skill_status.get(skill_id) or {}
        teacher = view.get("teacher_status") if isinstance(view, dict) else {}
        payload["skills"][skill_id] = {
            "example_ids": examples,
            "count": len(examples),
            "ui_status": teacher.get("status_key") if isinstance(teacher, dict) else None,
            "ui_label": teacher.get("label") if isinstance(teacher, dict) else None,
            "verified": view.get("verified_count") if isinstance(view, dict) else None,
            "wrapper": (ROOT / "skills" / f"{skill_id}.py").is_file(),
            "prod_package": (PROD / skill_id / "component_manifest.json").is_file(),
            "hash_aligned": sum(1 for r in rows if r["hash_aligned"]),
            "dry_only": [r["id"] for r in rows if r["dry_only"]],
            "prod_only": [r["id"] for r in rows if r["prod_only"]],
            "mismatch": [r["id"] for r in rows if r["dryrun"] and r["production"] and not r["hash_aligned"]],
            "missing_both": [r["id"] for r in rows if not r["dryrun"] and not r["production"]],
            "missing_tracker": [r["id"] for r in rows if r["tracker_status"] is None],
            "rows": rows,
        }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        skill: {
            k: v
            for k, v in data.items()
            if k != "rows"
        }
        for skill, data in payload["skills"].items()
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
