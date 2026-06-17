# -*- coding: utf-8 -*-
"""HV skill-only V3 pipeline verify (no other skills)."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.answer_payload import refresh_runtime_question_session
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.schema.gencode_component_tracker_inspection import ensure_gencode_component_tracker_table
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_skill,
    run_admin_v3_publish_for_skill,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.v3_presentation_inference import has_abcd_choice_group, infer_presentation_mode_from_textbook_row

SKILL = "vh_數學B1_HorizontalAndVerticalLineEquations"
EXAMPLE_IDS = (4544, 4553, 4562, 4591)


def main() -> None:
    db = PROJECT_ROOT / "instance" / "kumon_math.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    ensure_gencode_component_tracker_table(conn)

    print("=== TEXTBOOK EXAMPLES ===")
    for eid in EXAMPLE_IDS:
        row = conn.execute(
            "SELECT id, source_description, problem_type, problem_text FROM textbook_examples WHERE id=?",
            (eid,),
        ).fetchone()
        inferred = infer_presentation_mode_from_textbook_row(dict(row))
        print(
            json.dumps(
                {
                    "id": eid,
                    "source_description": row["source_description"],
                    "problem_type": row["problem_type"],
                    "has_abcd": has_abcd_choice_group(str(row["problem_text"] or "")),
                    "expected": inferred["presentation_mode"],
                },
                ensure_ascii=False,
            )
        )

    print("\n=== DRYRUN ===")
    dry = run_admin_v3_dryrun_for_skill(conn, SKILL, smoke=True, verify=True, force=True)
    print(json.dumps({k: dry[k] for k in ("success", "success_count", "failed_count")}, ensure_ascii=False))

    cov = get_v3_skill_component_coverage(conn, SKILL)
    print("\n=== COVERAGE ===")
    print(
        json.dumps(
            {
                "total_examples": cov["total_examples"],
                "verified_count": cov["verified_count"],
                "failed_count": cov["failed_count"],
                "missing_tracker_count": cov["missing_tracker_count"],
                "publish_ready": cov["publish_ready"],
            },
            ensure_ascii=False,
        )
    )

    staging = PROJECT_ROOT / "reports" / "gencode_v3_publish_staging" / "hv_line_publish"
    dryrun_skill = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    shutil.copytree(dryrun_skill, staging / SKILL)
    (staging / "agent_skills_v3").mkdir(parents=True)
    shutil.copytree(dryrun_skill, staging / "agent_skills_v3" / SKILL)

    print("\n=== PUBLISH ===")
    pub = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=SKILL,
        project_root=str(PROJECT_ROOT),
        staging_root=str(staging),
        force_publish=True,
        strict_coverage=True,
    )
    print(
        json.dumps(
            {
                "status": pub.get("status"),
                "component_count": pub.get("component_count"),
                "warnings": pub.get("warnings"),
            },
            ensure_ascii=False,
        )
    )

    spec = importlib.util.spec_from_file_location("facade", PROJECT_ROOT / "skills" / f"{SKILL}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    print("\n=== GENERATOR_SPECS ===")
    for row in mod.GENERATOR_SPECS:
        print(json.dumps(row, ensure_ascii=False))

    print("\n=== PER-COMPONENT CONTRACT ===")
    for eid in EXAMPLE_IDS:
        cid = f"src_{eid}"
        raw = mod.generate(seed=eid, component_id=cid)
        norm = refresh_runtime_question_session(dict(raw), skill_id=SKILL)
        meta = raw.get("metadata") or {}
        print(
            json.dumps(
                {
                    "id": eid,
                    "component_id": cid,
                    "presentation_mode": raw.get("presentation_mode"),
                    "answer_type": raw.get("answer_type"),
                    "answer": raw.get("answer"),
                    "correct_answer": raw.get("correct_answer"),
                    "choices_count": len(raw.get("choices") or []),
                    "semantic_answer": raw.get("semantic_answer"),
                    "problem_type_id": raw.get("problem_type_id"),
                    "metadata_presentation_mode": meta.get("presentation_mode"),
                    "answer_contract_nonempty": bool(norm.get("answer_contract")),
                },
                ensure_ascii=False,
            )
        )

    print("\n=== RUNTIME 12 SEEDS ===")
    seen = {"vertical_short": False, "horizontal_short": False, "single_choice": False}
    for seed in range(1, 13):
        raw = mod.generate(seed=seed)
        norm = refresh_runtime_question_session(dict(raw), skill_id=SKILL)
        ok = check_answer(raw.get("answer"), raw.get("correct_answer"), payload=norm, skill_id=SKILL)
        cid = str(raw.get("component_id") or "")
        pm = str(raw.get("presentation_mode") or "")
        qt = str(raw.get("question_text") or "")
        if pm == "short_answer" and "src_4544" in cid or "src_4562" in cid or "src_4591" not in cid:
            if "鉛直" in qt or "C(" in qt and "D(" in qt and "x" in str(raw.get("answer") or ""):
                seen["vertical_short"] = True
        if cid == "src_4553" or (pm == "short_answer" and "A(" in qt and "B(" in qt and str(raw.get("answer", "")).startswith("y")):
            seen["horizontal_short"] = True
        if pm == "single_choice":
            seen["single_choice"] = True
        print(
            json.dumps(
                {
                    "seed": seed,
                    "component_id": cid,
                    "presentation_mode": pm,
                    "question_text": qt[:70],
                    "answer": raw.get("answer"),
                    "correct_answer": raw.get("correct_answer"),
                    "choices_count": len(raw.get("choices") or []),
                    "semantic_answer": raw.get("semantic_answer"),
                    "problem_type_id": raw.get("problem_type_id"),
                    "metadata_pm": (raw.get("metadata") or {}).get("presentation_mode"),
                    "answer_contract_nonempty": bool(norm.get("answer_contract")),
                    "check_passed": ok,
                },
                ensure_ascii=False,
            )
        )
    print("\n=== SEEN ===", seen)
    conn.close()


if __name__ == "__main__":
    main()
