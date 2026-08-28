# -*- coding: utf-8 -*-
"""Read-only inventory for MathB B1 chapter 3 Gencode status."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.gencode.services.gencode_status_query_service import build_admin_skills_gencode_status_map

OUT = ROOT / "scratch" / "_b1_ch3_inventory.json"
PROD = ROOT / "agent_skills_v3"
DRY = ROOT / "reports" / "gencode_v3_dryrun"


def sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    curr = conn.execute(
        """
        SELECT skill_id, volume, chapter, section, display_order
        FROM skill_curriculum
        WHERE skill_id LIKE 'vh_%B1_%'
          AND chapter LIKE '3 %'
        ORDER BY section, display_order, skill_id
        """
    ).fetchall()
    skill_ids = [r["skill_id"] for r in curr if not str(r["skill_id"]).startswith("outline_")]
    status_map = build_admin_skills_gencode_status_map(conn, skill_ids)
    skills = {}
    for row in curr:
        sid = row["skill_id"]
        if sid.startswith("outline_"):
            continue
        examples = [
            int(r[0])
            for r in conn.execute(
                "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
                (sid,),
            ).fetchall()
        ]
        rows = []
        for eid in examples:
            cid = f"src_{eid}"
            dry = DRY / sid / "components" / cid / "generate.py"
            prod = PROD / sid / "components" / cid / "generate.py"
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
                    "tracker_error": None if tracker is None else (tracker["gencode_error_log"] or "")[:240],
                }
            )
        view = status_map.get(sid) or {}
        teacher = view.get("teacher_status") if isinstance(view, dict) else {}
        skills[sid] = {
            "volume": row["volume"],
            "chapter": row["chapter"],
            "section": row["section"],
            "display_order": row["display_order"],
            "example_count": len(examples),
            "example_ids": examples,
            "ui_status": teacher.get("status_key") if isinstance(teacher, dict) else None,
            "ui_label": teacher.get("label") if isinstance(teacher, dict) else None,
            "verified": view.get("verified_count"),
            "published": view.get("published_count"),
            "failed": view.get("failed_count"),
            "wrapper": (ROOT / "skills" / f"{sid}.py").is_file(),
            "prod_package": (PROD / sid / "component_manifest.json").is_file(),
            "hash_aligned": sum(1 for r in rows if r["hash_aligned"]),
            "dry_only": [r["id"] for r in rows if r["dry_only"]],
            "prod_only": [r["id"] for r in rows if r["prod_only"]],
            "mismatch": [r["id"] for r in rows if r["dryrun"] and r["production"] and not r["hash_aligned"]],
            "missing_both": [r["id"] for r in rows if not r["dryrun"] and not r["production"]],
            "missing_tracker": [r["id"] for r in rows if r["tracker_status"] is None],
            "tracker_counts": {},
            "rows": rows,
        }
        counts: dict[str, int] = {}
        for r in rows:
            key = r["tracker_status"] or "missing"
            counts[key] = counts.get(key, 0) + 1
        skills[sid]["tracker_counts"] = counts

    payload = {"skill_count": len(skills), "skills": skills}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        sid: {
            "section": v["section"],
            "examples": v["example_count"],
            "ui": v["ui_status"],
            "wrapper": v["wrapper"],
            "prod": v["prod_package"],
            "aligned": v["hash_aligned"],
            "missing_both": len(v["missing_both"]),
            "dry_only": len(v["dry_only"]),
            "prod_only": len(v["prod_only"]),
            "tracker": v["tracker_counts"],
        }
        for sid, v in skills.items()
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
