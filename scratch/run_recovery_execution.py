import sys
import os
import json
import sqlite3
import shutil
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.failed_component_recovery_service import recover_failed_components

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
PROPOSALS_DIR = PROJECT_ROOT / "reports" / "domain_capability_proposals"
SKILL_ID = "vh_數學B1_LinearFunction"
DRYRUN_BASE = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components"

def clean_proposals():
    if PROPOSALS_DIR.exists():
        for f in PROPOSALS_DIR.glob("*.json"):
            f.unlink()
        print("Cleaned up existing proposal files.")

def reset_tracker_records():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        UPDATE gencode_component_tracker
        SET gencode_status = 'failed',
            gencode_error_log = 'DOMAIN_CAPABILITY_UNRESOLVED: cannot resolve domain'
        WHERE skill_id = ? AND textbook_example_id NOT IN (4424, 4441, 4444)
        """,
        (SKILL_ID,)
    )
    conn.commit()
    conn.close()
    print("Reset 12 tracker records to failed/unresolved baseline.")

def get_tracker_snapshot():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT textbook_example_id, component_id, gencode_status, gencode_error_log FROM gencode_component_tracker WHERE skill_id = ?",
        (SKILL_ID,)
    ).fetchall()
    conn.close()
    return {r["textbook_example_id"]: dict(r) for r in rows}

def main():
    print("=================== PREPARATION ===================")
    clean_proposals()
    reset_tracker_records()
    
    snapshot_before = get_tracker_snapshot()
    print(f"Total tracker records for {SKILL_ID}: {len(snapshot_before)}")
    
    print("\n=================== FIRST RUN (EXECUTION) ===================")
    report_1 = recover_failed_components(skill_id=SKILL_ID, dry_run=False)
    
    print("\nFIRST RUN REPORT:")
    print(json.dumps({
        "rebuilt": report_1["rebuilt"],
        "verified": report_1["verified"],
        "still_failed": report_1["still_failed"],
        "proposals_created": report_1["proposals_created"],
        "proposals_reused": report_1["proposals_reused"]
    }, indent=2))
    
    # Assertions for First Run
    assert len(report_1["rebuilt"]) == 0, "No components should be rebuilt"
    assert len(report_1["verified"]) == 0, "No components should be verified"
    assert len(report_1["proposals_created"]) == 9, f"Expected 9 proposals created, got {len(report_1['proposals_created'])}"
    assert len(report_1["proposals_reused"]) == 3, f"Expected 3 proposals reused within first run, got {len(report_1['proposals_reused'])}"
    
    print("\n=================== VERIFICATIONS ===================")
    
    # 1. Verify no generator directories created
    for comp_id in report_1["unresolved_groups"].values():
        for cid in comp_id["components"]:
            comp_path = DRYRUN_BASE / cid
            if comp_path.exists():
                raise AssertionError(f"Generator directory should not exist: {comp_path}")
    print("Verification Passed: No new generator folders were created.")
    
    # 2. Verify tracker changes
    snapshot_after_1 = get_tracker_snapshot()
    assert len(snapshot_after_1) == len(snapshot_before)
    
    print("\nTracker updates:")
    changed_count = 0
    for ex_id, row_after in snapshot_after_1.items():
        row_before = snapshot_before[ex_id]
        if row_before != row_after:
            changed_count += 1
            print(f"Component {row_after['component_id']}:")
            print(f"  Before: status={row_before['gencode_status']}, error={row_before['gencode_error_log']}")
            print(f"  After:  status={row_after['gencode_status']}, error={row_after['gencode_error_log']}")
            
            # Error log must contain PARTIAL_CAPABILITY and gate missing details
            assert row_after["gencode_status"] == "failed"
            assert "PARTIAL_CAPABILITY: missing nodes:" in row_after["gencode_error_log"]
            
    assert changed_count == 12, f"Expected 12 records updated, got {changed_count}"
    
    # 3. Verify sibling records (e.g. verified ones) are unchanged
    # src_4424, src_4441, src_4444 should remain verified and unchanged
    for cid in [4424, 4441, 4444]:
        assert snapshot_after_1[cid]["gencode_status"] == "verified"
        assert snapshot_after_1[cid]["gencode_error_log"] is None
        assert snapshot_before[cid] == snapshot_after_1[cid]
    print("Verification Passed: Sibling records are completely unchanged.")
    
    print("\n=================== SECOND RUN (IDEMPOTENCY CHECK) ===================")
    report_2 = recover_failed_components(skill_id=SKILL_ID, dry_run=False)
    
    print("\nSECOND RUN REPORT:")
    print(json.dumps({
        "rebuilt": report_2["rebuilt"],
        "verified": report_2["verified"],
        "still_failed": report_2["still_failed"],
        "proposals_created": report_2["proposals_created"],
        "proposals_reused": report_2["proposals_reused"]
    }, indent=2))
    
    # Assertions for Second Run (Idempotency)
    assert len(report_2["rebuilt"]) == 0
    assert len(report_2["verified"]) == 0
    assert len(report_2["proposals_created"]) == 0, "No new proposals should be created in the second run"
    assert len(report_2["proposals_reused"]) == 9, f"Expected 9 proposals reused, got {len(report_2['proposals_reused'])}"
    print("Verification Passed: Proposal creation is fully idempotent (all reused).")

    # Display final proposal paths and source_example_ids
    print("\n=================== PROPOSALS DETAILED PLAN ===================")
    for p_file in sorted(PROPOSALS_DIR.glob("*.json")):
        data = json.loads(p_file.read_text(encoding="utf-8"))
        print(f"Proposal ID: {data['proposal_id']}")
        print(f"  Capabilities:       {data['required_capabilities']}")
        print(f"  Source Example IDs: {data['source_example_ids']}")
        print(f"  Recommended Action: {data['recommended_action']}")

if __name__ == "__main__":
    main()
