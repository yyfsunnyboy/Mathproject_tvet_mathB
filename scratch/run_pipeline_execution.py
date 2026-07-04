import sys
import json
import sqlite3
import shutil
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.failed_component_recovery_service import recover_failed_components
from core.gencode.services.proposal_advance_pipeline_service import advance_capability_proposals

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
PROPOSALS_DIR = PROJECT_ROOT / "reports" / "domain_capability_proposals"
DRAFTS_DIR = PROJECT_ROOT / "reports" / "domain_operation_drafts"
SKILL_ID = "vh_數學B1_LinearFunction"

def clean_all():
    # Clean proposals
    if PROPOSALS_DIR.exists():
        for f in PROPOSALS_DIR.glob("*.json"):
            f.unlink()
    # Clean drafts
    if DRAFTS_DIR.exists():
        shutil.rmtree(DRAFTS_DIR)
        DRAFTS_DIR.mkdir()
    print("Cleaned up existing proposals and drafts.")

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

def main():
    print("=================== 1. PREPARATION ===================")
    clean_all()
    reset_tracker_records()

    # Re-run recovery orchestrator to generate proposed proposals (status = proposed)
    print("\nRunning recovery orchestrator to generate 9 proposals...")
    recovery_report = recover_failed_components(skill_id=SKILL_ID, dry_run=False)
    print(f"Generated proposals: {len(recovery_report['proposals_created'])} created.")

    # Let's verify all generated proposals are proposed
    for p_file in PROPOSALS_DIR.glob("*.json"):
        data = json.loads(p_file.read_text(encoding="utf-8"))
        assert data["status"] == "proposed"
    print("Verified: all generated proposals are in 'proposed' status.")

    print("\n=================== 2. PIPELINE DRY RUN ===================")
    dryrun_report = advance_capability_proposals(skill_id=SKILL_ID, dry_run=True)
    print("DRY RUN REPORT:")
    print(json.dumps(dryrun_report, indent=2, ensure_ascii=False))

    # Assertions for dry run
    assert dryrun_report["total_proposals"] == 9
    assert dryrun_report["auto_approved"] == 9
    assert dryrun_report["approval_failed"] == 0
    assert dryrun_report["ready_for_human_review"] == 0
    
    # Check no files written in drafts directory yet
    draft_files = list(DRAFTS_DIR.glob("**/*"))
    assert len(draft_files) == 0, f"Expected 0 draft files, found {len(draft_files)}"
    print("Verification Passed: Dry run has zero side effects.")

    print("\n=================== 3. PIPELINE REAL EXECUTION ===================")
    execution_report = advance_capability_proposals(skill_id=SKILL_ID, dry_run=False)
    print("REAL EXECUTION REPORT:")
    print(json.dumps(execution_report, indent=2, ensure_ascii=False))

    # Assertions for real execution
    assert execution_report["total_proposals"] == 9
    assert execution_report["auto_approved"] == 9
    assert execution_report["ready_for_human_review"] == 0
    assert execution_report["drafts_created"] == 9
    assert execution_report["workspaces_created"] == 9
    assert execution_report["validation_passed"] == 0
    print("Verification Passed: Execution completed successfully.")

    print("\n=================== 4. POST-EXECUTION VERIFICATIONS ===================")
    
    # 1. Verify status updated to implementation_incomplete in all proposal files
    for p_file in sorted(PROPOSALS_DIR.glob("*.json")):
        data = json.loads(p_file.read_text(encoding="utf-8"))
        print(f"Proposal {data['proposal_id']} status on disk: {data['status']}")
        assert data["status"] == "implementation_incomplete"
    print("Verification Passed: All proposal files updated to 'implementation_incomplete'.")

    # 2. Verify workspace folders contain stubs
    for p_file in sorted(PROPOSALS_DIR.glob("*.json")):
        data = json.loads(p_file.read_text(encoding="utf-8"))
        pid = data["proposal_id"]
        ws_dir = DRAFTS_DIR / pid / "revision_0001" / "workspace"
        assert (ws_dir / "implementation_candidate.py").is_file()
        assert (ws_dir / "test_candidate.py").is_file()
        assert (ws_dir / "registry_patch.json").is_file()
        assert (ws_dir / "adapter_patch.json").is_file()
    print("Verification Passed: All workspaces correctly populated with stubs.")

    # 3. Verify database tracker remains unchanged (no status updated to verified for the 12 proposed ones)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    failed_rows = conn.execute(
        "SELECT textbook_example_id, component_id, gencode_status FROM gencode_component_tracker WHERE skill_id = ? AND gencode_status = 'failed'",
        (SKILL_ID,)
    ).fetchall()
    verified_rows = conn.execute(
        "SELECT textbook_example_id, component_id, gencode_status FROM gencode_component_tracker WHERE skill_id = ? AND gencode_status = 'verified'",
        (SKILL_ID,)
    ).fetchall()
    conn.close()

    assert len(failed_rows) == 12, f"Expected 12 failed components, got {len(failed_rows)}"
    assert len(verified_rows) == 3, f"Expected 3 verified components, got {len(verified_rows)}"
    print("Verification Passed: Database tracker remains completely unmodified.")

if __name__ == "__main__":
    main()
