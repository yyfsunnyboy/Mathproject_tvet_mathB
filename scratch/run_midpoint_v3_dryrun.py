import sys
import os
import shutil
import sqlite3
import json
from pathlib import Path

# Add current workspace path to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.services.gencode_status_query_service import load_v3_skill_generator_specs

def main():
    skill_id = "vh_數學B1_MidpointCoordinates"
    db_path = PROJECT_ROOT / "instance" / "kumon_math.db"
    
    # 1. Clean previous state
    # A. Delete dryrun generated components directory in an encoding-safe way
    dryrun_base = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
    if dryrun_base.exists():
        for sub in dryrun_base.iterdir():
            if "MidpointCoordinates" in sub.name:
                print(f"Cleaning encoding-safe dryrun directory: {sub}")
                try:
                    shutil.rmtree(sub)
                except Exception as e:
                    print(f"Failed to delete {sub}: {e}")
        
    # B. Delete records from gencode_component_tracker DB table
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gencode_component_tracker WHERE skill_id = ?", (skill_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"Deleted {deleted_count} component tracker records for {skill_id}.")
    finally:
        conn.close()

    # 2. Execute local gencode pipeline
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        print(f"\nRunning run_admin_v3_dryrun_for_skill for {skill_id}...")
        result = run_admin_v3_dryrun_for_skill(
            conn=conn,
            skill_id=skill_id,
            smoke=True,
            verify=True,
            force=True,
        )
        print("\nDryrun Result Summary:")
        print(f"  Success: {result.get('success')}")
        print(f"  Success Count: {result.get('success_count')}")
        print(f"  Failed Count: {result.get('failed_count')}")
        print(f"  Unsupported Count: {result.get('unsupported_count')}")
        print(f"  Verified Count: {result.get('verified_count')}")
        
        # Check details of failures if any
        results = result.get("results") or []
        for r in results:
            if r.get("status") == "failed" or r.get("error"):
                print(f"  Example ID: {r.get('textbook_example_id')} - Component: {r.get('component_id')} - Status: {r.get('status')}")
                print(f"    Error: {r.get('error')}")
                
        # Check coverage
        coverage = get_v3_skill_component_coverage(conn, skill_id)
        print("\nCoverage Status:")
        print(f"  Total Examples: {coverage.get('total_examples')}")
        print(f"  Verified Count: {coverage.get('verified_count')}")
        print(f"  Failed Count: {coverage.get('failed_count')}")
        
        # Check generator specs
        specs = load_v3_skill_generator_specs(
            skill_id=skill_id,
            production_base_dir="agent_skills_v3",
            project_root=PROJECT_ROOT,
        )
        print(f"\nGenerator specs count (production): {len(specs)}")
        
        # Save output result
        out_path = PROJECT_ROOT / "scratch" / "dryrun_midpoint_output.json"
        with open(out_path, "w", encoding="utf-8") as f:
            clean_res = {k: result[k] for k in result if k not in ("conn",)}
            json.dump(clean_res, f, ensure_ascii=False, indent=2)
            
    finally:
        conn.close()

if __name__ == '__main__':
    main()
