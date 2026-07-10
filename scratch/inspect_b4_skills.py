import sqlite3
import json
from pathlib import Path
from core.gencode.services.gencode_status_query_service import (
    build_admin_skill_gencode_status_view,
    _get_tracker_rows_for_skill,
    inspect_gencode_files,
    inspect_skill_production_files,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from models import db
from app import app

with app.app_context():
    # SQLite DB is typically at instance/db.sqlite or from config
    # Let's get the connection
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "").replace("sqlite:///", "")
    print("DB Path:", db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    for skill_id in ["vh_數學B4_LinearTransformationOfData", "vh_數學B4_NormalDistributionAndEmpiricalRule"]:
        print("\n=== Skill ID:", skill_id, "===")
        coverage = get_v3_skill_component_coverage(conn, skill_id)
        print("Coverage total_examples:", coverage.get("total_examples"))
        print("Coverage verified_count:", coverage.get("verified_count"))
        print("Coverage examples status:")
        for ex in coverage.get("examples", []):
            print(f"  Example {ex.get('textbook_example_id')}: status={ex.get('status')}, component_id={ex.get('component_id')}")
        
        rows = _get_tracker_rows_for_skill(conn, skill_id)
        print("Tracker rows count:", len(rows))
        for row in rows:
            print(f"  Row: component_id={row.get('component_id')}, textbook_example_id={row.get('textbook_example_id')}, status={row.get('status')}, has_payload={row.get('has_payload')}")
            
        prod_info = inspect_skill_production_files(skill_id=skill_id, project_root=Path("."))
        print("Prod info:", prod_info)
        
        view = build_admin_skill_gencode_status_view(conn, skill_id=skill_id, project_root=Path("."))
        print("View summary:", {k: v for k, v in view.items() if k not in ["coverage", "tracker_rows"]})
