import sys
import os
import json
import sqlite3
import py_compile
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
SKILL_ID = "vh_數學B1_LinearFunction"
COMPONENT_ID = "src_4424"
EXAMPLE_ID = 4424
DRYRUN_BASE = "reports/gencode_v3_dryrun"

def get_tracker_snapshot(conn):
    rows = conn.execute(
        """
        SELECT textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload, gencode_error_log, created_at, updated_at
        FROM gencode_component_tracker
        WHERE skill_id = ?
        """,
        (SKILL_ID,)
    ).fetchall()
    # Normalize rows to dictionaries
    snapshot = {}
    for r in rows:
        snapshot[r[0]] = {
            "textbook_example_id": r[0],
            "skill_id": r[1],
            "component_id": r[2],
            "gencode_status": r[3],
            "induced_spec_payload": r[4],
            "gencode_error_log": r[5],
            "created_at": r[6],
            "updated_at": r[7]
        }
    return snapshot

def print_row_diff(before, after):
    for key in ["gencode_status", "gencode_error_log", "induced_spec_payload", "updated_at"]:
        b_val = before.get(key)
        a_val = after.get(key)
        if b_val != a_val:
            print(f"  {key}:")
            print(f"    Before: {b_val}")
            print(f"    After:  {a_val}")

def main():
    print("=================== 1. RESOLVER RESOLUTION ===================")
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
    resolver_res = resolve_domain_authority(
        skill_id=SKILL_ID,
        problem_type_id="graph_intercepts_and_linear_equation"
    )
    print(f"Selected Operation: {resolver_res.selected_operation}")
    print(f"Fixed Domain Key:   {resolver_res.fixed_domain_key}")
    assert resolver_res.selected_operation == "graph_intercepts_and_linear_equation"
    assert resolver_res.fixed_domain_key == "coordinate_geometry.line_equation"
    print("Resolver resolved successfully.")

    print("\n=================== 2. COMPONENT BUILD (DRYRUN) ===================")
    conn = sqlite3.connect(str(DB_PATH))
    # Enable Row factory
    conn.row_factory = sqlite3.Row
    
    # Take database snapshot before changes
    snapshot_before = get_tracker_snapshot(conn)
    print(f"Total tracker records for {SKILL_ID} before change: {len(snapshot_before)}")

    # We patch V3_PRODUCTION_PUBLISH_ENABLED to False during dryrun to satisfy safety checks
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example
    import core.gencode.services.admin_gencode_action_service as service_module
    
    # Backup original publish flag
    orig_flag = service_module.V3_PRODUCTION_PUBLISH_ENABLED
    service_module.V3_PRODUCTION_PUBLISH_ENABLED = False
    
    try:
        dryrun_res = run_admin_v3_dryrun_for_example(
            conn=conn,
            textbook_example_id=EXAMPLE_ID,
            skill_id=SKILL_ID,
            force_regenerate=True,
            allow_non_mvp_skill=True,
            dryrun_base_dir=DRYRUN_BASE
        )
    finally:
        service_module.V3_PRODUCTION_PUBLISH_ENABLED = orig_flag

    print(f"Dryrun Result Status: {dryrun_res['status']}")
    print(f"Component Directory:  {dryrun_res['dryrun_component_dir']}")

    print("\n=================== 3. VALIDATIONS & SEED TESTING ===================")
    # Check that component files exist and compile
    comp_dir = Path(dryrun_res['dryrun_component_dir'])
    required_files = {
        "metadata.py": comp_dir / "metadata.py",
        "generate.py": comp_dir / "generate.py",
        "get_hint.py": comp_dir / "get_hint.py",
    }
    for name, path in required_files.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing required file: {name}")
        py_compile.compile(str(path), doraise=True)
        print(f"Compilation passed for {name}")

    # Load generate and get_hint modules
    from core.gencode.services.admin_gencode_action_service import _load_module_from_file
    from core.gencode.services.v3_question_integrity_validator import validate_component_payload
    from core.domain.coordinate_geometry.line_equation_domain import check_multi_part_answer
    
    generate_module = _load_module_from_file(required_files["generate.py"])
    hint_module = _load_module_from_file(required_files["get_hint.py"])
    
    generate_fn = getattr(generate_module, "generate")
    hint_fn = getattr(hint_module, "get_hint")
    
    seeds_to_test = [7, 42, 101]
    seed_payloads = {}
    for seed in seeds_to_test:
        print(f"\nTesting Seed {seed}:")
        payload = generate_fn(seed=seed)
        
        # 1. Payload Schema Checks
        assert isinstance(payload, dict), "Payload must be a dictionary"
        assert "question_text" in payload, "Missing question_text"
        assert "answer_contract" in payload, "Missing answer_contract"
        assert "correct_answer" in payload, "Missing correct_answer"
        
        # 2. Answer Contract Checks
        ac = payload["answer_contract"]
        assert ac.get("presentation_mode") == "graph_multi_part", f"Invalid presentation_mode: {ac.get('presentation_mode')}"
        assert ac.get("answer_type") == "multi_part", f"Invalid answer_type: {ac.get('answer_type')}"
        assert ac.get("checker") == "multi_part_answer_checker", f"Invalid checker: {ac.get('checker')}"
        
        # 3. Component Validator Checks
        val = validate_component_payload(payload, COMPONENT_ID)
        print(f"  Integrity validation passed: {val.get('passed')}")
        if not val.get("passed"):
            raise ValueError(f"Integrity validation failed: {val.get('blockers')}")
            
        # 4. Hint generation check
        hint_fn(1, payload)
        
        # 5. Checker Right/Wrong Answer Checks
        correct_ans = payload["correct_answer"]
        print(f"  Correct Answer: {correct_ans}")
        # Right answer validation
        assert check_multi_part_answer(correct_ans, correct_ans) is True, "Checker rejected correct answer!"
        # Wrong answer validation
        wrong_ans = {k: "999" for k in correct_ans}
        assert check_multi_part_answer(wrong_ans, correct_ans) is False, "Checker accepted incorrect answer!"
        
        seed_payloads[seed] = payload

    print("\n=================== 4. DATABASE TRANSACTIONAL UPDATE ===================")
    # Get the current record's induced spec payload
    row = conn.execute(
        "SELECT induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (EXAMPLE_ID,)
    ).fetchone()
    
    induced_spec_payload = {}
    if row and row[0]:
        try:
            induced_spec_payload = json.loads(row[0])
        except Exception:
            induced_spec_payload = {}
            
    # Update integrity gate fields
    induced_spec_payload["integrity_gate_passed"] = True
    induced_spec_payload["integrity_gate_version"] = "v1"
    induced_spec_payload["integrity_gate_blockers"] = []
    # Add validation evidence details
    induced_spec_payload["validation_evidence"] = {
        "seeds_verified": seeds_to_test,
        "payload_schema_passed": True,
        "answer_contract_passed": True,
        "checker_logic_verified": True
    }

    # Save verified tracker record
    from core.gencode.services.component_tracker_service import save_tracker_record
    
    # We execute inside a try-rollback block to guarantee atomicity
    try:
        updated_row = save_tracker_record(
            conn=conn,
            textbook_example_id=EXAMPLE_ID,
            skill_id=SKILL_ID,
            gencode_status="verified",
            induced_spec_payload=induced_spec_payload,
            gencode_error_log=None
        )
        print("Updated tracker record in memory/transaction.")
        
        # Fetch snapshot after change
        snapshot_after = get_tracker_snapshot(conn)
        
        print("\n=================== 5. POST-UPDATE VERIFICATION ===================")
        # Check that total count is still 15
        assert len(snapshot_after) == 15, f"Expected 15 records, found {len(snapshot_after)}"
        
        # Verify only src_4424 changed
        changed_keys = []
        for example_id, record_after in snapshot_after.items():
            record_before = snapshot_before.get(example_id)
            if record_before is None:
                print(f"Record for example {example_id} was added!")
                changed_keys.append(example_id)
            elif record_before != record_after:
                changed_keys.append(example_id)
                
        print(f"Changed tracker records: {changed_keys}")
        assert changed_keys == [EXAMPLE_ID], f"Expected only {EXAMPLE_ID} to change, but changed: {changed_keys}"
        
        # Print the detailed differences for src_4424
        print(f"\nDetails of changes in tracker record {EXAMPLE_ID}:")
        print_row_diff(snapshot_before[EXAMPLE_ID], snapshot_after[EXAMPLE_ID])
        
        # Verify the remaining 14 records are exactly unchanged
        for example_id, record_before in snapshot_before.items():
            if example_id == EXAMPLE_ID:
                continue
            assert record_before == snapshot_after[example_id], f"Sibling record {example_id} was modified!"
            
        print("Verification passed! Committing transaction...")
        conn.commit()
        print("COMMIT SUCCESSFUL.")
        
    except Exception as e:
        print("VERIFICATION FAILED! Rolling back transaction...", file=sys.stderr)
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    main()
