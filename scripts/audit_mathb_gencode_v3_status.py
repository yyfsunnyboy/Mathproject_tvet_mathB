"""Read-only inventory of MathB V3 tracker and deployed artifacts."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from core.gencode.services.gencode_status_query_service import build_admin_skills_gencode_status_map


def main() -> int:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    try:
        skill_ids = [str(row[0]) for row in conn.execute("SELECT skill_id FROM skills_info WHERE skill_id LIKE 'vh_%B%' ORDER BY skill_id")]
        status_map = build_admin_skills_gencode_status_map(conn, skill_ids)
    finally:
        conn.close()
    rows = [
        {
            "skill_id": skill_id,
            "tracker_components": view["component_count"],
            "verified": view["verified_count"],
            "published": view["published_count"],
            "failed": view["failed_count"],
            "manifest_components": view.get("manifest_component_count", 0),
            "generate_files": view.get("production_component_count", 0),
            "wrapper": view.get("production_wrapper_exists"),
            "package": view.get("v3_package_exists"),
            "ui_status": view["teacher_status"]["status_key"],
        }
        for skill_id, view in status_map.items()
    ]
    print(json.dumps({"database_uri": Config.SQLALCHEMY_DATABASE_URI, "skills": rows}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
