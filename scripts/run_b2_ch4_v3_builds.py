# -*- coding: utf-8 -*-
"""Run V3 orchestrator builds for B2 Ch4 circle skills."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.gencode.services.v3_build_orchestrator_service import run_v3_build_orchestrator
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
STAGING = ROOT / "runtime" / "v3_publish_staging"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
OUT = ROOT / "reports" / "_b2_ch4_v3_build_results.json"

SKILLS = [
    "vh_數學B2_SubSection_4_1_1",
    "vh_數學B2_SubSection_4_1_2",
    "vh_數學B2_SubSection_4_2_1",
    "vh_數學B2_SubSection_4_2_2",
    "vh_數學B2_SubSection_4_2_3",
    "vh_數學B2_SubSection_4_2_4",
]


def main() -> None:
    conn = sqlite3.connect(str(DB))
    results = []
    try:
        for sid in SKILLS:
            pre = evaluate_skill_v3_capability(conn, sid, probe_examples=True)
            resolvable = int(pre.get("resolvable_example_count") or 0)
            entry = {
                "skill_id": sid,
                "preflight_status": pre.get("capability_status"),
                "resolvable": resolvable,
                "skip": int(pre.get("intentional_skip_count") or 0),
                "needs_capability": int(pre.get("needs_capability_count") or 0),
                "domain_key": pre.get("domain_key"),
            }
            print(
                sid,
                "preflight=",
                entry["preflight_status"],
                "resolvable=",
                resolvable,
                "needs=",
                entry["needs_capability"],
                flush=True,
            )
            if resolvable <= 0:
                entry["build"] = "skipped_no_resolvable"
                results.append(entry)
                continue
            try:
                result = run_v3_build_orchestrator(
                    conn,
                    sid,
                    project_root=str(ROOT),
                    staging_root=str(STAGING),
                    dryrun_base_dir=str(DRYRUN),
                    mode="auto",
                    force=True,
                )
                counts = (result or {}).get("counts") or {}
                entry["build"] = {
                    "job_id": (result or {}).get("job_id"),
                    "final_status": (result or {}).get("final_status") or (result or {}).get("status"),
                    "generated": counts.get("generated_count") or counts.get("built_count"),
                    "validated": counts.get("validated_count"),
                    "published": counts.get("published_count"),
                    "needs_capability": counts.get("needs_capability_count"),
                    "failed": counts.get("failed_count"),
                    "eligible": counts.get("eligible_count"),
                    "skip": counts.get("skip_count"),
                    "errors": (result or {}).get("errors"),
                }
                print(" ->", entry["build"]["final_status"], "published=", entry["build"]["published"], flush=True)
            except Exception as exc:
                entry["build"] = {"error": str(exc)}
                print(" -> ERROR", exc, flush=True)
            results.append(entry)
    finally:
        conn.close()
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
