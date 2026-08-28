# -*- coding: utf-8 -*-
"""Generic chapter-3 skill dryrun + publish helper."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-id", required=True)
    ap.add_argument("--skip-publish", action="store_true")
    args = ap.parse_args()
    skill = args.skill_id
    conn = sqlite3.connect(Config.db_path)
    ids = [
        int(r[0])
        for r in conn.execute(
            "SELECT id FROM textbook_examples WHERE skill_id = ? ORDER BY id",
            (skill,),
        ).fetchall()
    ]
    results = []
    for eid in ids:
        try:
            res = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=eid,
                skill_id=skill,
                force_regenerate=True,
                allow_non_mvp_skill=True,
            )
            conn.commit()
            st = res.get("tracker_status") or res.get("status")
            ok = str(st).lower() in {"verified", "published"} or bool(res.get("ok", True)) and not res.get("error_code")
            results.append({"id": eid, "ok": ok, "status": st, "error": res.get("error_code")})
            print(("OK" if ok else "FAIL"), eid, st, res.get("error_code"))
        except Exception as exc:
            conn.rollback()
            results.append({"id": eid, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            print("EXC", eid, exc)

    publish = None
    if not args.skip_publish and any(r.get("ok") for r in results):
        try:
            publish = run_admin_v3_publish_for_skill(
                conn=conn,
                skill_id=skill,
                project_root=str(ROOT),
                staging_root=str(ROOT / "reports" / "gencode_v3_publish_staging"),
                force_publish=True,
                strict_coverage=False,
            )
            conn.commit()
            print("PUBLISH", publish.get("status"), "components", publish.get("component_count"))
        except Exception as exc:
            conn.rollback()
            publish = {"error": f"{type(exc).__name__}: {exc}"}
            print("PUBLISH_FAIL", exc)

    out = ROOT / "scratch" / f"_ch3_batch_{skill.split('_')[-1]}.json"
    payload = {
        "skill": skill,
        "ok": sum(1 for r in results if r.get("ok")),
        "total": len(results),
        "results": results,
        "publish": publish,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", out, payload["ok"], "/", payload["total"])
    conn.close()


if __name__ == "__main__":
    main()
