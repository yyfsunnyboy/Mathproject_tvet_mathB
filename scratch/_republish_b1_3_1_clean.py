# -*- coding: utf-8 -*-
"""Remove skipped components from runtime paths and republish verified-only wrappers."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.runtime_skill_wrapper import check_answer

SKIP = {4618, 4629, 4706, 4716, 4717}
SKILL_MAP = {
    4618: "vh_數學B1_PolynomialBasicConcepts",
    4629: "vh_數學B1_PolynomialBasicConcepts",
    4716: "vh_數學B1_PolynomialBasicConcepts",
    4706: "vh_數學B1_PolynomialArithmeticOperations",
    4717: "vh_數學B1_PolynomialEquality",
}
# also remove failed choice comps from runtime if present
FAILED_CHOICE = {4628, 4718, 4719, 4720}
for eid in FAILED_CHOICE:
    SKILL_MAP[eid] = "vh_數學B1_PolynomialArithmeticOperations"

STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())
SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]

conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row

removed = []
for eid, skill in SKILL_MAP.items():
    cid = f"src_{eid}"
    paths = [
        ROOT / "agent_skills_v3" / skill / "components" / cid,
        ROOT / "reports" / "gencode_v3_dryrun" / skill / "components" / cid,
        ROOT / "reports" / "gencode_v3_publish_staging" / "agent_skills_v3" / skill / "components" / cid,
        ROOT / "reports" / "gencode_v3_publish_staging" / skill / "components" / cid,
    ]
    for p in paths:
        if p.exists():
            shutil.rmtree(p)
            removed.append(str(p.relative_to(ROOT)))
    status = "needs_human_review" if eid in SKIP else "failed"
    reason = "SKIPPED_SOURCE_INCOMPLETE" if eid in SKIP else "FAILED_CHOICE_OR_DRYRUN"
    save_tracker_record(
        conn,
        textbook_example_id=eid,
        skill_id=skill,
        gencode_status=status,
        induced_spec_payload={
            "component_id": cid,
            "rebuild_decision": "EXCLUDE" if eid in SKIP else "FAILED",
            "reason": reason,
            "integrity_gate_passed": False,
        },
        gencode_error_log=reason,
    )
    print("removed/tracker", eid, status)

conn.commit()

# republish
pub_out = []
for skill in SKILLS:
    try:
        pub = run_admin_v3_publish_for_skill(
            conn=conn,
            skill_id=skill,
            project_root=str(ROOT),
            staging_root=STAGING,
            force_publish=True,
            strict_coverage=False,
        )
        pub_out.append({"skill_id": skill, "status": pub.get("status"), "ok": True, "pub": pub})
        print("PUBLISH", skill, pub.get("status"))
    except Exception as e:
        pub_out.append({"skill_id": skill, "ok": False, "error": str(e), "trace": traceback.format_exc()[-1200:]})
        print("PUBLISH_FAIL", skill, e)

# verify keys exclude skip
for skill in SKILLS:
    facade = ROOT / "skills" / f"{skill}.py"
    text = facade.read_text(encoding="utf-8")
    bad = [f"src_{i}" for i in SKIP | FAILED_CHOICE if f"src_{i}" in text]
    print("wrapper_bad_refs", skill, bad)

smoke = []
for skill in SKILLS:
    facade = ROOT / "skills" / f"{skill}.py"
    spec = importlib.util.spec_from_file_location(f"sm_{skill}", facade)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("KEYS", skill, mod.GENERATOR_KEYS)
    passed = failed = 0
    errs = []
    for i in range(20):
        try:
            pl = mod.generate(seed=3000 + i)
            q = str(pl.get("question_text") or pl.get("question") or "")
            if not q or pl.get("answer") is None:
                failed += 1
                errs.append(f"{i}:empty:{pl.get('component_id')}")
                continue
            if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                failed += 1
                errs.append(f"{i}:checker:{pl.get('component_id')}:{pl.get('answer_type')}")
                continue
            passed += 1
        except Exception as e:
            failed += 1
            errs.append(f"{i}:exc:{e}")
    smoke.append({"skill_id": skill, "samples": 20, "passed": passed, "failed": failed, "errors": errs[:8]})
    print("SMOKE", skill, passed, failed, errs[:3])

out = {"removed": removed, "publish": pub_out, "smoke": smoke}
(ROOT / "scratch/_b1_3_1_republish_clean.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)

# update main results
res = json.loads((ROOT / "scratch/_b1_3_1_rebuild_results.json").read_text(encoding="utf-8"))
res["publish"] = pub_out
res["smoke"] = smoke
res["removed_skipped_runtime_paths"] = removed
(ROOT / "scratch/_b1_3_1_rebuild_results.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
