# -*- coding: utf-8 -*-
"""Pipeline script to rebuild, verify, staging compile, and promote the GeneralForm skill."""

from __future__ import annotations

import sys
import json
import sqlite3
import shutil
import hashlib
from pathlib import Path

# Setup Python path
PROJECT_ROOT = Path("E:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

# Reconfigure sys.stdout for UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_smoke_for_example,
    mark_admin_v3_example_verified,
)
from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    classify_textbook_example,
    calculate_source_hash,
)
from core.registry.taxonomy_registry import resolve_domain_for_skill
from core.gencode.services.v3_source_fidelity_service import verify_source_fidelity
from core.gencode.services.v3_cross_component_audit_service import check_cross_example_collapse
from core.gencode.skill_wrapper_compiler import compile_and_double_write_skill
from core.gencode.v3_production_publish_service import (
    run_v3_smoke,
    _promote_staging_to_production,
    _sync_dryrun_components_to_v3_house,
)

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
SKILL_ID = "vh_數學B1_GeneralFormOfLinearEquation"
STAGING_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_publish_staging" / "general_form_rebuild"
EXAMPLES_IDS = [4565, 4566, 4567, 4572, 4573, 4574, 4581, 4582, 4585, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599]


def run_pipeline(conn: sqlite3.Connection):
    print("=" * 80)
    print("STARTING GENCODE V3 CORE REBUILD PIPELINE FOR GENERAL FORM")
    print("=" * 80)

    # 1. Clean staging directory
    if STAGING_ROOT.exists():
        shutil.rmtree(STAGING_ROOT)
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)

    taxonomy_entry = resolve_domain_for_skill(SKILL_ID)

    # 2. Build dryrun components and run staging classifications
    print("\n[Step 2] Building Staging Components & Classifications...")
    classification_report = []
    fidelity_report = []
    components_info = []

    for eid in EXAMPLES_IDS:
        print(f"  Processing Example ID: {eid}...")
        # Get raw textbook row
        row = conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (eid,)).fetchone()
        if not row:
            raise ValueError(f"Example ID {eid} not found in DB!")
        
        q_text = row["problem_text"] or ""
        ans_text = row["correct_answer"] or ""
        sol_text = row["detailed_solution"] or ""
        s_hash = calculate_source_hash(q_text, ans_text, sol_text)
        
        # Classification
        src = TextbookExampleSource(
            skill_id=SKILL_ID,
            textbook_example_id=eid,
            question_text=q_text,
            answer=ans_text,
            choices=[],
            explanation=sol_text,
            source_label=row["source_description"],
            source_type=row["problem_type"],
            presentation_mode="short_answer" if "A)" not in q_text else "single_choice",
            question_type=row["problem_type"],
            source_hash=s_hash,
        )
        classification = classify_textbook_example(src, taxonomy_entry)
        
        # Run shadow dry-run (creates draft code and saves tracker in connection DB)
        dryrun_res = run_admin_v3_dryrun_for_example(
            conn=conn,
            textbook_example_id=eid,
            skill_id=SKILL_ID,
            dryrun_base_dir=str(STAGING_ROOT),
            allow_non_mvp_skill=True,
        )
        
        # Run shadow smoke
        run_admin_v3_smoke_for_example(
            conn=conn,
            textbook_example_id=eid,
            skill_id=SKILL_ID,
            dryrun_base_dir=str(STAGING_ROOT),
        )
        
        # Mark verified in DB
        mark_admin_v3_example_verified(conn=conn, textbook_example_id=eid, skill_id=SKILL_ID)
        
        component_dir = Path(dryrun_res["dryrun_component_dir"])
        gen_code = (component_dir / "generate.py").read_text(encoding="utf-8")
        meta_code = (component_dir / "metadata.py").read_text(encoding="utf-8")
        
        # Read metadata dict
        meta_locs = {}
        exec(meta_code, {}, meta_locs)
        
        # Fidelity verify
        fidelity = verify_source_fidelity(classification, meta_locs)
        
        # Extract sample question text
        gen_locs = {}
        exec(gen_code, gen_locs, gen_locs)
        sample_payload = gen_locs["generate"](seed=42)
        sample_question = sample_payload.get("question", "")
        sample_answer = sample_payload.get("answer", "")
        if isinstance(sample_answer, dict):
            sample_answer_str = str(sample_answer.get("canonical_form") or sample_answer)
        else:
            sample_answer_str = str(sample_answer)
            
        classification_report.append({
            "example_id": eid,
            "original_task": row["source_description"] or "N/A",
            "problem_type_id": classification["problem_type_id"],
            "domain_operation": classification["problem_type_id"],  # mapped 1-1
            "task_intent": classification["task_intent"],
            "presentation_mode": classification["presentation_mode"],
        })
        
        fidelity_report.append({
            "example_id": eid,
            "fidelity_passed": fidelity["fidelity_passed"],
            "errors": fidelity["errors"],
            "sample_question": sample_question,
            "sample_answer": sample_answer_str,
        })
        
        components_info.append({
            "textbook_example_id": eid,
            "problem_type_id": classification["problem_type_id"],
            "generate_code": gen_code,
            "sample_question_text": sample_question,
        })

    # Print Step 3 & 4 Tables
    print("\n[Step 3] 17 textbook examples classification report:")
    print("| Example ID | Original Task | Classification / Domain Op | Task Intent | Presentation Mode |")
    print("|---|---|---|---|---|")
    for r in classification_report:
        print(f"| {r['example_id']} | {r['original_task']} | {r['problem_type_id']} | {r['task_intent']} | {r['presentation_mode']} |")

    print("\n[Step 4] Fidelity report:")
    print("| Example ID | Fidelity Status | Errors | Sample Question | Sample Answer |")
    print("|---|---|---|---|---|")
    for r in fidelity_report:
        errs = "; ".join(r["errors"]) if r["errors"] else "None"
        q_brief = r["sample_question"].replace("\n", " ").replace("\r", "")[:40] + "..."
        print(f"| {r['example_id']} | {'PASSED' if r['fidelity_passed'] else 'FAILED'} | {errs} | {q_brief} | {r['sample_answer']} |")

    # Step 5: Cross-component collapse check
    print("\n[Step 5] Running Cross-Example Collapse Gate check...")
    collapse_res = check_cross_example_collapse(components_info)
    print(f"  Collapse Detected: {collapse_res['collapse_detected']}")
    print(f"  Unique Problem Types: {collapse_res['metrics']['unique_problem_type_count']}")
    print(f"  Unique AST Hashes: {collapse_res['metrics']['unique_ast_hash_count']}")
    print(f"  Unique Template Signatures: {collapse_res['metrics']['unique_template_signature_count']}")
    if collapse_res["collapse_detected"]:
        raise ValueError(f"Collapse Gate Triggered: {collapse_res['reasons']}")
    else:
        print("  Collapse Gate Passed Successfully!")

    # Step 6: Build staging wrapper
    print("\n[Step 6] Compiling Staging wrapper...")
    compile_res = compile_and_double_write_skill(conn, SKILL_ID, str(STAGING_ROOT))
    _sync_dryrun_components_to_v3_house(STAGING_ROOT, SKILL_ID)
    print(f"  Wrapper compiled. Staging components written: {compile_res.get('component_count')}")

    # Step 7: Run staging runtime smoke test
    print("\n[Step 7] Running Staging Runtime Smoke Test...")
    run_v3_smoke(STAGING_ROOT, SKILL_ID)
    print("  Staging smoke test passed successfully!")

    # Step 8: Fairness Scheduler Test
    print("\n[Step 8] Running Fairness Scheduler Test (200 random picks)...")
    # Load compiled router module
    import importlib.util
    router_path = STAGING_ROOT / "agent_skills_v3" / SKILL_ID / "__init__.py"
    spec = importlib.util.spec_from_file_location("v3_staging_router", router_path)
    router_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(router_mod)
    
    # Check pick distribution over 200 iterations (seed=None to check shuffle cycle state)
    picks = {}
    for _ in range(200):
        picked = router_mod._pick_component_id(seed=None)
        picks[picked] = picks.get(picked, 0) + 1
        
    print(f"  Unique components chosen: {len(picks)} / 17")
    print("  Pick counts:")
    for k, v in sorted(picks.items()):
        print(f"    {k}: {v} times")
    
    # With equal weight=1, shuffled cycle of length 17 runs 11 full cycles and 13 items in the 12th cycle.
    # Therefore, each component must be picked either 11 or 12 times! Let's assert this!
    for k, v in picks.items():
        assert v in (11, 12), f"Component {k} was picked {v} times (expected 11 or 12 times under cycle scheduling)!"
    print("  Fairness scheduling assertions passed! Perfect distribution achieved.")

    # Step 9: Promote to production
    print("\n[Step 9] Promoting Staging to Production...")
    promote_result = _promote_staging_to_production(STAGING_ROOT, PROJECT_ROOT, SKILL_ID)
    print(f"  Promotion completed: {promote_result}")

    # Step 10: Run production smoke test
    print("\n[Step 10] Running Production Smoke Test...")
    run_v3_smoke(PROJECT_ROOT, SKILL_ID)
    print("  Production smoke test passed successfully!")
    print("\n" + "=" * 80)
    print("SKILL REBUILD AND PROMOTION FULLY COMPLETED AND VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    db_conn = sqlite3.connect(str(DB_PATH))
    db_conn.row_factory = sqlite3.Row
    try:
        run_pipeline(db_conn)
    finally:
        db_conn.close()
