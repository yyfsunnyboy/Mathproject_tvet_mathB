# -*- coding: utf-8 -*-
"""Batch V3 dryrun for PolynomialBasicConcepts (force regenerate)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example

SKILL = "vh_數學B1_PolynomialBasicConcepts"
OUT = ROOT / "scratch" / "_pbc_dryrun_batch.json"


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    ids = [
        int(r[0])
        for r in conn.execute(
            "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
            (SKILL,),
        ).fetchall()
    ]
    results = []
    for eid in ids:
        try:
            res = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=eid,
                skill_id=SKILL,
                force_regenerate=True,
                allow_non_mvp_skill=True,
            )
            conn.commit()
            results.append(
                {
                    "id": eid,
                    "ok": bool(res.get("ok", True)),
                    "tracker_status": res.get("tracker_status") or res.get("status"),
                    "error_code": res.get("error_code"),
                    "reason": res.get("reason") or res.get("gencode_error_log"),
                    "problem_type_id": (res.get("phase1_classification") or {}).get("problem_type_id")
                    if isinstance(res.get("phase1_classification"), dict)
                    else res.get("problem_type_id"),
                    "keys": sorted(res.keys())[:20],
                }
            )
            print("OK" if results[-1]["ok"] else "FAIL", eid, results[-1].get("tracker_status"), results[-1].get("error_code"), results[-1].get("problem_type_id"))
        except Exception as exc:
            conn.rollback()
            results.append({"id": eid, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            print("EXC", eid, exc)
    OUT.write_text(json.dumps({"skill": SKILL, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "ok", sum(1 for r in results if r.get("ok")), "/", len(results))
    conn.close()


if __name__ == "__main__":
    main()
