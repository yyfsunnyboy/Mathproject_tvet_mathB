from __future__ import annotations

import json
import py_compile
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.services.admin_gencode_action_service import (
    _load_module_from_file,
    run_admin_v3_dryrun_for_example,
)
import core.gencode.services.admin_gencode_action_service as service_module
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

SKILL_ID = "vh_數學B1_LinearFunction"
OP = "graph_based_tiered_linear_application_multi_part"
DRYRUN_BASE = "reports/gencode_v3_dryrun"
SEEDS = [7, 42, 101]
TARGETS = [(4425, "src_4425"), (4445, "src_4445")]


def snapshot(conn: sqlite3.Connection) -> dict[int, tuple[str, str]]:
    rows = conn.execute(
        "SELECT textbook_example_id, component_id, gencode_status "
        "FROM gencode_component_tracker WHERE skill_id=?",
        (SKILL_ID,),
    ).fetchall()
    return {int(r[0]): (str(r[1]), str(r[2])) for r in rows}


def main() -> int:
    resolved = resolve_domain_authority(
        SKILL_ID,
        problem_type_id=OP,
        extra={"required_capabilities": [OP]},
    )
    assert resolved.selected_operation == OP
    assert resolved.fixed_domain_key == "coordinate_geometry.division_point_coordinates"
    print("READY", resolved.selected_operation, resolved.fixed_domain_key)

    conn = sqlite3.connect(str(PROJECT_ROOT / "instance" / "kumon_math.db"))
    before_all = snapshot(conn)
    print("TRACKER_BEFORE", {k: before_all[k] for k in (4425, 4445, 4424, 4441, 4444)})

    results: dict[str, dict] = {}
    orig_flag = service_module.V3_PRODUCTION_PUBLISH_ENABLED
    service_module.V3_PRODUCTION_PUBLISH_ENABLED = False
    try:
        for example_id, component_id in TARGETS:
            print(f"\n=== REBUILD {component_id} ===")
            before = snapshot(conn)
            dry = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=example_id,
                skill_id=SKILL_ID,
                force_regenerate=True,
                allow_non_mvp_skill=True,
                dryrun_base_dir=DRYRUN_BASE,
            )
            print("dryrun_status", dry.get("status"), dry.get("dryrun_component_dir"))
            comp_dir_raw = dry.get("dryrun_component_dir")
            if not comp_dir_raw:
                results[component_id] = {
                    "ok": False,
                    "stage": "dryrun",
                    "detail": dry.get("status") or dry.get("error") or dry.get("message"),
                }
                continue

            comp_dir = Path(comp_dir_raw)
            files = {name: comp_dir / name for name in ("generate.py", "metadata.py", "get_hint.py")}
            for name, path in files.items():
                if not path.is_file():
                    results[component_id] = {"ok": False, "stage": "files", "detail": name}
                    break
                py_compile.compile(str(path), doraise=True)
            else:
                generate_fn = getattr(_load_module_from_file(files["generate.py"]), "generate")
                hint_fn = getattr(_load_module_from_file(files["get_hint.py"]), "get_hint")
                blockers = []
                for seed in SEEDS:
                    payload = generate_fn(seed=seed)
                    ac = payload["answer_contract"]
                    answer = payload["correct_answer"]
                    correct = check_multi_part_answer(
                        answer, answer, answer_contract=ac, payload=payload
                    )
                    wrong = {k: int(v) + 1 for k, v in answer.items()}
                    incorrect = check_multi_part_answer(
                        wrong, answer, answer_contract=ac, payload=payload
                    )
                    integrity = validate_component_payload(payload, component_id=component_id)
                    hint_fn(1, payload)
                    print(
                        f"  seed={seed} integrity={integrity.get('passed')} "
                        f"checker={correct.get('is_correct')}/{incorrect.get('is_correct')}"
                    )
                    if not (
                        correct.get("is_correct") is True
                        and incorrect.get("is_correct") is False
                        and integrity.get("passed") is True
                    ):
                        blockers.append(
                            {
                                "seed": seed,
                                "integrity": integrity,
                                "correct": correct.get("is_correct"),
                                "incorrect": incorrect.get("is_correct"),
                            }
                        )
                if blockers:
                    results[component_id] = {
                        "ok": False,
                        "stage": "validation",
                        "blockers": blockers,
                    }
                    continue

                row = conn.execute(
                    "SELECT induced_spec_payload FROM gencode_component_tracker "
                    "WHERE textbook_example_id=?",
                    (example_id,),
                ).fetchone()
                induced: dict = {}
                if row and row[0]:
                    try:
                        induced = json.loads(row[0])
                    except Exception:
                        induced = {}
                induced["integrity_gate_passed"] = True
                induced["integrity_gate_version"] = "v1"
                induced["integrity_gate_blockers"] = []
                induced["validation_evidence"] = {
                    "seeds_verified": SEEDS,
                    "payload_schema_passed": True,
                    "answer_contract_passed": True,
                    "checker_logic_verified": True,
                    "operation": OP,
                }
                save_tracker_record(
                    conn=conn,
                    textbook_example_id=example_id,
                    skill_id=SKILL_ID,
                    gencode_status="verified",
                    induced_spec_payload=induced,
                    gencode_error_log=None,
                )
                after = snapshot(conn)
                changed = [eid for eid, rec in after.items() if before.get(eid) != rec]
                if changed != [example_id]:
                    conn.rollback()
                    results[component_id] = {
                        "ok": False,
                        "stage": "tracker_isolation",
                        "changed": changed,
                    }
                    continue
                for eid, rec in before.items():
                    if eid != example_id and after[eid] != rec:
                        conn.rollback()
                        results[component_id] = {
                            "ok": False,
                            "stage": "sibling_mutation",
                            "example_id": eid,
                        }
                        break
                else:
                    conn.commit()
                    results[component_id] = {
                        "ok": True,
                        "dir": str(comp_dir),
                        "tracker_before": before_all.get(example_id),
                        "tracker_after": after.get(example_id),
                    }
                    print("VERIFIED", component_id, after.get(example_id))
    finally:
        service_module.V3_PRODUCTION_PUBLISH_ENABLED = orig_flag
        conn.close()

    print("SUMMARY", results)
    return 0 if all(item.get("ok") for item in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
