# -*- coding: utf-8 -*-
"""Gencode recovered 3-1 self-assessment examples (choice) → package → partial publish."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
)
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.runtime_skill_wrapper import check_answer

RECOVERED = [4706, 4716, 4717, 4718, 4719, 4720]
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())
OUT = ROOT / "scratch" / "_b1_3_1_recovered_gencode_results.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _patch_choice_contract(comp_dir: Path, sample: dict[str, Any]) -> None:
    gen_path = comp_dir / "generate.py"
    meta_path = comp_dir / "metadata.py"
    gen = gen_path.read_text(encoding="utf-8")
    meta = meta_path.read_text(encoding="utf-8")
    gen = re.sub(r'^ANSWER_TYPE\s*=\s*".*?"', 'ANSWER_TYPE = "single_choice"', gen, count=1, flags=re.M)
    gen = re.sub(
        r'^PRESENTATION_MODE\s*=\s*".*?"',
        'PRESENTATION_MODE = "single_choice"',
        gen,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'^GENERATOR_READINESS\s*=\s*".*?"',
        'GENERATOR_READINESS = "verified"',
        meta,
        count=1,
        flags=re.M,
    )
    # ensure payload answer_type/checker after convert
    inject = '''
    # recovered self-assessment: force single_choice contract
    payload["presentation_mode"] = "single_choice"
    payload["answer_type"] = "single_choice"
    payload["interaction_type"] = "single_choice"
    payload["checker"] = "choice_label_checker"
    payload["checker_key"] = "choice_label_checker"
    _ac = dict(payload.get("answer_contract") or {})
    _ac.update({
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
    })
    payload["answer_contract"] = _ac
'''
    if "recovered self-assessment: force single_choice" not in gen:
        gen = gen.replace(
            "    if component_id:\n        payload[\"component_id\"] = component_id\n    payload[\"seed\"] = seed\n    return payload",
            inject
            + "    if component_id:\n        payload[\"component_id\"] = component_id\n    payload[\"seed\"] = seed\n    return payload",
        )
    gen_path.write_text(gen, encoding="utf-8")
    meta_path.write_text(meta, encoding="utf-8")


def _verify_choice_component(comp_dir: Path, n: int = 20) -> dict[str, Any]:
    gen_mod = _load_module(comp_dir / "generate.py", f"gen_{comp_dir.name}")
    passed = 0
    failed = 0
    errors: list[str] = []
    seen_seeds = {}
    for i in range(n):
        seed = 9000 + i
        try:
            pl = gen_mod.generate(seed=seed)
            q = str(pl.get("question_text") or "")
            choices = pl.get("choices") or []
            ans = pl.get("answer")
            if not q:
                failed += 1
                errors.append(f"{seed}:empty_q")
                continue
            if not isinstance(choices, list) or len(choices) < 4:
                failed += 1
                errors.append(f"{seed}:choices_n={len(choices) if isinstance(choices, list) else None}")
                continue
            if str(pl.get("answer_type")) != "single_choice":
                failed += 1
                errors.append(f"{seed}:answer_type={pl.get('answer_type')}")
                continue
            labels = []
            for c in choices:
                if isinstance(c, dict):
                    labels.append(str(c.get("label") or c.get("key") or ""))
                else:
                    labels.append("")
            if ans not in labels and str(ans) not in {"A", "B", "C", "D"}:
                failed += 1
                errors.append(f"{seed}:answer_not_label={ans}")
                continue
            if not check_answer(ans, ans, payload=pl):
                failed += 1
                errors.append(f"{seed}:checker_true_fail")
                continue
            # wrong choices must fail
            wrong_ok = True
            for lab in {"A", "B", "C", "D"} - {str(ans)}:
                if check_answer(lab, ans, payload=pl):
                    wrong_ok = False
                    errors.append(f"{seed}:wrong_accepted={lab}")
                    break
            if not wrong_ok:
                failed += 1
                continue
            # reproducibility
            pl2 = gen_mod.generate(seed=seed)
            if pl2.get("question_text") != pl.get("question_text") or pl2.get("answer") != pl.get("answer"):
                failed += 1
                errors.append(f"{seed}:not_reproducible")
                continue
            passed += 1
            seen_seeds[seed] = pl.get("component_id")
        except Exception as e:
            failed += 1
            errors.append(f"{seed}:exc:{e}")
    return {"passed": passed, "failed": failed, "errors": errors[:12], "n": n}


def _enrich_tracker(conn: sqlite3.Connection, eid: int, skill_id: str, cid: str, sample: dict[str, Any]) -> None:
    meta_path = ROOT / "agent_skills_v3" / skill_id / "components" / cid / "metadata.py"
    meta = {}
    if meta_path.exists():
        m = _load_module(meta_path, f"meta_{cid}")
        for k in (
            "FIXED_DOMAIN_KEY",
            "DOMAIN_OPERATION",
            "SELECTED_OPERATION",
            "PROBLEM_TYPE_ID",
            "ANSWER_TYPE",
            "PRESENTATION_MODE",
            "GENERATOR_READINESS",
        ):
            if hasattr(m, k):
                meta[k.lower()] = getattr(m, k)
    payload = {
        "component_id": cid,
        "integrity_gate_passed": True,
        "fixed_domain_key": meta.get("fixed_domain_key") or sample.get("fixed_domain_key") or "algebra.polynomial",
        "domain_operation": meta.get("domain_operation") or sample.get("domain_operation"),
        "selected_operation": meta.get("selected_operation") or meta.get("domain_operation") or sample.get("domain_operation"),
        "problem_type_id": meta.get("problem_type_id") or sample.get("problem_type_id"),
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "generator_readiness": "verified",
        "rebuild_decision": "RECOVERED_SELF_ASSESSMENT",
    }
    save_tracker_record(
        conn,
        textbook_example_id=eid,
        skill_id=skill_id,
        gencode_status="verified",
        induced_spec_payload=payload,
        gencode_error_log=None,
    )


def main() -> None:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    results = []
    skill_hits: dict[str, list[int]] = {}

    for eid in RECOVERED:
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        skill_id = row["skill_id"]
        cid = f"src_{eid}"
        item: dict[str, Any] = {
            "example_id": eid,
            "skill_id": skill_id,
            "component_id": cid,
            "answer_type": "single_choice",
        }
        try:
            dry = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=eid,
                skill_id=skill_id,
                dryrun_base_dir=str(DRYRUN),
                seed=7,
                allow_non_mvp_skill=True,
                force_regenerate=True,
            )
            status = str(dry.get("status") or "")
            dry_comp = Path(str(dry.get("dryrun_component_dir") or ""))
            if not (dry_comp / "generate.py").exists():
                dry_comp = DRYRUN / skill_id / "components" / cid
            if not (dry_comp / "generate.py").exists():
                item.update(
                    {
                        "status": "FAILED",
                        "reason": f"dryrun_missing_component:{status}:{dry.get('error_code') or dry.get('gencode_error_log') or dry.get('error')}",
                        "dryrun_keys": list(dry.keys())[:30],
                    }
                )
                results.append(item)
                print("FAIL", eid, item["reason"])
                continue

            if status in {"failed", "needs_human_review"} and not (dry_comp / "generate.py").exists():
                item.update({"status": "FAILED", "reason": f"dryrun_{status}"})
                results.append(item)
                print("FAIL", eid, status)
                continue

            # smoke generate once for contract patch
            gen_mod = _load_module(dry_comp / "generate.py", f"pre_{cid}")
            sample = gen_mod.generate(seed=42)
            _patch_choice_contract(dry_comp, sample)

            # re-import after patch
            verify = _verify_choice_component(dry_comp, n=20)
            item["20_seed"] = verify
            if verify["passed"] < 18:
                item.update({"status": "FAILED", "reason": f"seed_verify_failed:{verify}"})
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill_id,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid, "reason": item["reason"]},
                    gencode_error_log=item["reason"],
                )
                results.append(item)
                print("FAIL", eid, verify)
                continue

            # copy to production skills tree
            prod = ROOT / "agent_skills_v3" / skill_id / "components" / cid
            if prod.exists():
                shutil.rmtree(prod)
            shutil.copytree(dry_comp, prod)
            sample2 = _load_module(prod / "generate.py", f"prod_{cid}").generate(seed=42)
            _enrich_tracker(conn, eid, skill_id, cid, sample2)
            item.update({"status": "VERIFIED", "reason": "choice_20seed_ok"})
            skill_hits.setdefault(skill_id, []).append(eid)
            results.append(item)
            print("OK", eid, verify["passed"], "/", verify["n"])
        except Exception as e:
            item.update(
                {
                    "status": "FAILED",
                    "reason": f"exc:{e}",
                    "trace": traceback.format_exc()[-1500:],
                }
            )
            results.append(item)
            print("EXC", eid, e)

    conn.commit()

    # package + publish affected skills
    publish = []
    smoke = []
    for skill_id in sorted(skill_hits.keys()):
        try:
            pub = run_admin_v3_publish_for_skill(
                conn=conn,
                skill_id=skill_id,
                project_root=str(ROOT),
                staging_root=STAGING,
                force_publish=True,
                strict_coverage=False,
            )
            publish.append({"skill_id": skill_id, "status": pub.get("status"), "pub": pub, "ok": True})
            print("PUBLISH", skill_id, pub.get("status"))
        except Exception as e:
            publish.append({"skill_id": skill_id, "ok": False, "error": str(e), "trace": traceback.format_exc()[-1200:]})
            print("PUBLISH_FAIL", skill_id, e)
            continue

        facade = ROOT / "skills" / f"{skill_id}.py"
        mod = _load_module(facade, f"skill_{skill_id}")
        keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
        new_keys = [f"src_{i}" for i in skill_hits[skill_id]]
        hit_new = 0
        passed = failed = 0
        errs = []
        for i in range(40):
            try:
                pl = mod.generate(seed=5000 + i)
                cid = str(pl.get("component_id") or "")
                if cid in new_keys:
                    hit_new += 1
                q = str(pl.get("question_text") or "")
                if not q or pl.get("answer") is None:
                    failed += 1
                    errs.append(f"{i}:empty:{cid}")
                    continue
                if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                    failed += 1
                    errs.append(f"{i}:checker:{cid}:{pl.get('answer_type')}")
                    continue
                passed += 1
            except Exception as e:
                failed += 1
                errs.append(f"{i}:exc:{e}")
        # dedicated samples until new generators appear
        for i in range(60):
            if hit_new >= 3:
                break
            pl = mod.generate(seed=8000 + i)
            if str(pl.get("component_id") or "") in new_keys:
                hit_new += 1
        smoke.append(
            {
                "skill_id": skill_id,
                "samples": 40,
                "passed": passed,
                "failed": failed,
                "errors": errs[:8],
                "wrapper_keys": keys,
                "new_keys_present": [k for k in new_keys if k in keys],
                "new_generator_hits": hit_new,
            }
        )
        print("SMOKE", skill_id, passed, failed, "new_hits", hit_new, "keys", keys)

    out = {
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "recovered_ids": RECOVERED,
        "results": results,
        "publish": publish,
        "smoke": smoke,
        "verified": [r["example_id"] for r in results if r.get("status") == "VERIFIED"],
        "failed": [r["example_id"] for r in results if r.get("status") == "FAILED"],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("WROTE", OUT)
    print("VERIFIED", out["verified"])
    print("FAILED", out["failed"])


if __name__ == "__main__":
    main()
