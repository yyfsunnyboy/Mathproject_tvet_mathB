# -*- coding: utf-8 -*-
"""Trace Gencode V3 admin /skills status for one or more skill_ids."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from core.gencode.services.gencode_status_query_service import (
    TEACHER_V3_STATUS,
    build_admin_skills_gencode_status_map,
)
from core.routes.admin import _load_skills_v3_gencode_status_map, _resolve_admin_project_root
from models import db


def _count_generated_components(components_dir: Path) -> int:
    if not components_dir.is_dir():
        return 0
    return sum(
        1
        for component_dir in components_dir.iterdir()
        if component_dir.is_dir() and (component_dir / "generate.py").is_file()
    )


def trace_skill(skill_id: str) -> dict[str, object]:
    project_root = _resolve_admin_project_root()
    conn = db.engine.raw_connection()
    try:
        textbook_rows = conn.execute(
            "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
            (skill_id,),
        ).fetchall()
        tracker_rows = conn.execute(
            """
            SELECT textbook_example_id, component_id, gencode_status
            FROM gencode_component_tracker
            WHERE skill_id = ?
            ORDER BY textbook_example_id
            """,
            (skill_id,),
        ).fetchall()
        status_map = build_admin_skills_gencode_status_map(
            conn,
            [skill_id],
            project_root=project_root,
        )
    finally:
        conn.close()

    view = status_map.get(skill_id, {})
    teacher = view.get("teacher_status") or {}
    production_root = project_root / "agent_skills_v3" / skill_id / "components"
    dryrun_root = project_root / "reports" / "gencode_v3_dryrun" / skill_id / "components"
    wrapper_path = project_root / "skills" / f"{skill_id}.py"
    manifest_path = project_root / "agent_skills_v3" / skill_id / "component_manifest.json"

    verified_tracker = sum(1 for row in tracker_rows if str(row[2]) == "verified")
    return {
        "skill_id": skill_id,
        "textbook_count": len(textbook_rows),
        "tracker_count": len(tracker_rows),
        "generated_count": max(
            _count_generated_components(production_root),
            _count_generated_components(dryrun_root),
        ),
        "verified_count": int(view.get("verified_count") or 0),
        "packaged_count": int(view.get("generated_not_packaged_count") or 0),
        "published_count": int(view.get("published_count") or 0),
        "production_exists": wrapper_path.is_file(),
        "v3_package_exists": (project_root / "agent_skills_v3" / skill_id / "__init__.py").is_file(),
        "manifest_exists": manifest_path.is_file(),
        "verified_tracker_rows": verified_tracker,
        "final_ui_status": str(teacher.get("label") or TEACHER_V3_STATUS["not_generated"]["label"]),
        "publish_ready": bool(view.get("publish_ready")),
        "total_examples_ui": int(view.get("total_examples") or 0),
        "available_count_ui": int(view.get("available_count") or view.get("verified_count") or 0),
    }


def main() -> None:
    skill_ids = sys.argv[1:] or [
        "vh_數學B4_FrequencyDistributionTableConstruction",
        "vh_數學B4_HistogramsAndFrequencyPolygons",
    ]
    app = create_app()
    with app.app_context():
        print(
            "| skill_id | textbook_count | tracker_count | generated_count | verified_count | "
            "packaged_count | published_count | production_exists | final_ui_status |"
        )
        print("|" + "---|" * 9)
        for skill_id in skill_ids:
            row = trace_skill(skill_id)
            route_map = _load_skills_v3_gencode_status_map([skill_id]).get(skill_id, {})
            print(
                f"| {row['skill_id']} | {row['textbook_count']} | {row['tracker_count']} | "
                f"{row['generated_count']} | {row['verified_count']} | {row['packaged_count']} | "
                f"{row['published_count']} | {row['production_exists']} | {row['final_ui_status']} |"
            )
            print(
                f"  route_map: total={route_map.get('total_examples')} "
                f"available={route_map.get('available_count')} "
                f"teacher={((route_map.get('teacher_status') or {}).get('label'))}"
            )


if __name__ == "__main__":
    main()
