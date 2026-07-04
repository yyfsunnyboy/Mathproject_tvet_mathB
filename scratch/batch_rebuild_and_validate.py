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
DRYRUN_BASE = "reports/gencode_v3_dryrun"

EXAMPLES_TO_PROCESS = [4441, 4444]

def get_tracker_snapshot(conn):
    rows = conn.execute(
        """
        SELECT textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload, gencode_error_log, created_at, updated_at
        FROM gencode_component_tracker
        WHERE skill_id = ?
        """,
        (SKILL_ID,)
    ).fetchall()
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
            b_str = str(b_val).encode('cp950', errors='replace').decode('cp950')
            a_str = str(a_val).encode('cp950', errors='replace').decode('cp950')
            print(f"    Before: {b_str}")
            print(f"    After:  {a_str}")

def main():
    print("=================== 1. RESOLVER RESOLUTION ===================")
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
    
    for ex_id in EXAMPLES_TO_PROCESS:
        resolver_res = resolve_domain_authority(
            skill_id=SKILL_ID,
            problem_type_id="graph_intercepts_and_linear_equation"
        )
        print(f"Example {ex_id}:")
        print(f"  Selected Operation: {resolver_res.selected_operation}")
        print(f"  Fixed Domain Key:   {resolver_res.fixed_domain_key}")
        assert resolver_res.selected_operation == "graph_intercepts_and_linear_equation"
        assert resolver_res.fixed_domain_key == "coordinate_geometry.line_equation"
    print("Resolver resolved successfully for both examples.")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Snapshot before changes
    snapshot_before = get_tracker_snapshot(conn)
    print(f"\nTotal tracker records for {SKILL_ID} before change: {len(snapshot_before)}")

    # We patch V3_PRODUCTION_PUBLISH_ENABLED to False during dryrun to satisfy safety checks
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example
    import core.gencode.services.admin_gencode_action_service as service_module
    from core.gencode.services.admin_gencode_action_service import _load_module_from_file
    from core.gencode.services.v3_question_integrity_validator import validate_component_payload
    from core.domain.coordinate_geometry.line_equation_domain import check_multi_part_answer
    from core.gencode.services.component_tracker_service import save_tracker_record
    
    orig_flag = service_module.V3_PRODUCTION_PUBLISH_ENABLED
    service_module.V3_PRODUCTION_PUBLISH_ENABLED = False

    try:
        updated_examples = []
        for ex_id in EXAMPLES_TO_PROCESS:
            comp_id = f"src_{ex_id}"
            print(f"\n=================== PROCESSING {comp_id} ===================")
            
            # 2. Rebuild component via dryrun
            dryrun_res = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=ex_id,
                skill_id=SKILL_ID,
                force_regenerate=True,
                allow_non_mvp_skill=True,
                dryrun_base_dir=DRYRUN_BASE
            )
            print(f"Dryrun Result Status for {comp_id}: {dryrun_res['status']}")
            
            # 3. Validation & seed checks
            comp_dir = Path(dryrun_res['dryrun_component_dir'])
            required_files = {
                "metadata.py": comp_dir / "metadata.py",
                "generate.py": comp_dir / "generate.py",
                "get_hint.py": comp_dir / "get_hint.py",
            }
            for name, path in required_files.items():
                if not path.is_file():
                    raise FileNotFoundError(f"Missing required file for {comp_id}: {name}")
                py_compile.compile(str(path), doraise=True)
                print(f"Compilation passed for {name}")

            generate_module = _load_module_from_file(required_files["generate.py"])
            hint_module = _load_module_from_file(required_files["get_hint.py"])
            generate_fn = getattr(generate_module, "generate")
            hint_fn = getattr(hint_module, "get_hint")
            
            seeds_to_test = [7, 42, 101]
            for seed in seeds_to_test:
                payload = generate_fn(seed=seed)
                assert isinstance(payload, dict), "Payload must be a dictionary"
                ac = payload["answer_contract"]
                assert ac.get("presentation_mode") == "graph_multi_part"
                assert ac.get("answer_type") == "multi_part"
                
                val = validate_component_payload(payload, comp_id)
                if not val.get("passed"):
                    raise ValueError(f"Integrity validation failed for {comp_id} seed {seed}: {val.get('blockers')}")
                
                hint_fn(1, payload)
                
                correct_ans = payload["correct_answer"]
                assert check_multi_part_answer(correct_ans, correct_ans) is True
                wrong_ans = {k: "999" for k in correct_ans}
                assert check_multi_part_answer(wrong_ans, correct_ans) is False
                
            print(f"All validation checks passed for {comp_id}.")
            
            # 4. Database Transactional Update (Memory)
            # Retrieve current record's induced spec
            row = conn.execute(
                "SELECT induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = ?",
                (ex_id,)
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
            induced_spec_payload["validation_evidence"] = {
                "seeds_verified": seeds_to_test,
                "payload_schema_passed": True,
                "answer_contract_passed": True,
                "checker_logic_verified": True
            }

            save_tracker_record(
                conn=conn,
                textbook_example_id=ex_id,
                skill_id=SKILL_ID,
                gencode_status="verified",
                induced_spec_payload=induced_spec_payload,
                gencode_error_log=None
            )
            print(f"Updated tracker status to verified for {comp_id}.")
            updated_examples.append(ex_id)
            
        print("\n=================== 5. POST-UPDATE VERIFICATION ===================")
        # Snapshot after changes
        snapshot_after = get_tracker_snapshot(conn)
        assert len(snapshot_after) == 15, f"Expected 15 records, found {len(snapshot_after)}"
        
        # Verify only the requested examples were changed
        changed_keys = []
        for example_id, record_after in snapshot_after.items():
            record_before = snapshot_before.get(example_id)
            if record_before != record_after:
                changed_keys.append(example_id)
                
        print(f"Changed tracker records: {changed_keys}")
        assert sorted(changed_keys) == sorted(EXAMPLES_TO_PROCESS), f"Expected only {EXAMPLES_TO_PROCESS} to change, but changed: {changed_keys}"
        
        for ex_id in EXAMPLES_TO_PROCESS:
            print(f"\nDetails of changes in tracker record {ex_id}:")
            print_row_diff(snapshot_before[ex_id], snapshot_after[ex_id])
            
        # Verify the remaining 12 sibling records are exactly unchanged
        # Wait, the total is 15. Sibling records include: 4424 (which is already verified) and the other 12 failed components.
        # So we assert that all 13 examples not in EXAMPLES_TO_PROCESS are exactly unchanged.
        for example_id, record_before in snapshot_before.items():
            if example_id in EXAMPLES_TO_PROCESS:
                continue
            assert record_before == snapshot_after[example_id], f"Sibling record {example_id} was modified!"
            
        print("\nVerification passed! Committing transaction...")
        conn.commit()
        print("COMMIT SUCCESSFUL.")
        
    except Exception as e:
        print("VERIFICATION FAILED! Rolling back transaction...", file=sys.stderr)
        conn.rollback()
        raise e
    finally:
        service_module.V3_PRODUCTION_PUBLISH_ENABLED = orig_flag
        conn.close()

if __name__ == "__main__":
    main()
