# -*- coding: utf-8 -*-
"""Read-only: next Gencode skill by curriculum order."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from core.gencode.services.gencode_status_query_service import build_admin_skills_gencode_status_map

OUT = PROJECT_ROOT / "scratch" / "_gencode_next_skill_audit.json"


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    try:
        skill_rows = conn.execute(
            """
            SELECT
                si.skill_id,
                si.skill_ch_name,
                sc.volume,
                sc.chapter,
                sc.section,
                sc.display_order
            FROM skills_info si
            LEFT JOIN skill_curriculum sc ON sc.skill_id = si.skill_id
            WHERE si.skill_id LIKE '%數學B1_%'
            ORDER BY sc.volume, sc.chapter, sc.section, sc.display_order, si.skill_id
            """
        ).fetchall()

        # Fallback if encoding / join fails to match
        if not skill_rows:
            skill_rows = conn.execute(
                """
                SELECT skill_id, display_name, NULL AS book, NULL AS chapter,
                       NULL AS section, NULL AS display_order
                FROM skills_info
                WHERE skill_id LIKE '%B1_%'
                ORDER BY skill_id
                """
            ).fetchall()

        skill_ids = [str(r["skill_id"]) for r in skill_rows]
        status_map = build_admin_skills_gencode_status_map(conn, skill_ids) if skill_ids else {}

        example_counts = {
            str(r[0]): int(r[1])
            for r in conn.execute(
                """
                SELECT skill_id, COUNT(*)
                FROM textbook_examples
                WHERE skill_id LIKE '%B1_%'
                GROUP BY skill_id
                """
            ).fetchall()
        }

        tracker_rows = conn.execute(
            """
            SELECT skill_id, gencode_status, COUNT(*) AS n
            FROM gencode_component_tracker
            GROUP BY skill_id, gencode_status
            """
        ).fetchall()
        tracker = {}
        for r in tracker_rows:
            tracker.setdefault(str(r["skill_id"]), {})[str(r["gencode_status"] or "")] = int(r["n"])

        out_skills = []
        for r in skill_rows:
            sid = str(r["skill_id"])
            view = status_map.get(sid) or {}
            teacher = (view.get("teacher_status") or {}) if isinstance(view, dict) else {}
            out_skills.append(
                {
                    "skill_id": sid,
                    "display_name": r["skill_ch_name"],
                    "book": r["volume"],
                    "chapter": r["chapter"],
                    "section": r["section"],
                    "display_order": r["display_order"],
                    "textbook_examples": example_counts.get(sid, 0),
                    "tracker": tracker.get(sid, {}),
                    "ui_status": teacher.get("status_key") if isinstance(teacher, dict) else None,
                    "verified": view.get("verified_count") if isinstance(view, dict) else None,
                    "failed": view.get("failed_count") if isinstance(view, dict) else None,
                    "published": view.get("published_count") if isinstance(view, dict) else None,
                    "wrapper": view.get("production_wrapper_exists") if isinstance(view, dict) else None,
                    "package": view.get("v3_package_exists") if isinstance(view, dict) else None,
                    "generate_files": view.get("production_component_count") if isinstance(view, dict) else None,
                }
            )

        # Also dump B1 curriculum nodes even if skill_id join used different encoding
        curr = [
            {
                "skill_id": str(r["skill_id"]),
                "book": r["volume"],
                "chapter": r["chapter"],
                "section": r["section"],
                "unit_title": r["unit_title"] if "unit_title" in r.keys() else None,
            }
            for r in conn.execute(
                """
                SELECT skill_id, volume, chapter, section
                FROM skill_curriculum
                WHERE skill_id LIKE '%數學B1_%' OR volume LIKE '%B1%'
                ORDER BY chapter, section, skill_id
                """
            ).fetchall()
        ]

        payload = {
            "db": Config.db_path,
            "b1_skill_count": len(out_skills),
            "skills": out_skills,
            "curriculum_sample": curr[:80],
        }
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(OUT))
        print("skill_count", len(out_skills), "curriculum_count", len(curr))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
