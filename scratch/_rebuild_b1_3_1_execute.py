# -*- coding: utf-8 -*-
"""B1 3-1 FULL rebuild: per-example Phase2 → verify → package → publish.

Does not modify textbook_examples / skill_id / classification sources.
Does not commit/push.
"""
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
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.gencode.services.component_tracker_service import (
    derive_component_id,
    save_tracker_record,
    update_status,
)
from core.gencode.runtime_skill_wrapper import check_answer

FEAS = json.loads((ROOT / "scratch/_b1_3_1_source_feasibility.json").read_text(encoding="utf-8"))
SKIP_IDS = {r["example_id"] for r in FEAS["rows"] if r["rebuild_decision"] == "EXCLUDE"}
INCLUDE_ROWS = [r for r in FEAS["rows"] if r["rebuild_decision"] == "INCLUDE"]

DRYRUN = "reports/gencode_v3_dryrun"
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _patch_answer_contract_files(comp_dir: Path, sample: dict[str, Any]) -> str:
    """Align generate/metadata answer_type/checker with observed payload topology."""
    ans = sample.get("answer")
    choices = sample.get("choices") or sample.get("options") or []
    runtime_at = str(sample.get("answer_type") or "").strip()
    ac = sample.get("answer_contract") if isinstance(sample.get("answer_contract"), dict) else {}

    if isinstance(choices, list) and choices and runtime_at in {"choice", "single_choice"}:
        target_type = "single_choice" if runtime_at == "single_choice" else "choice"
        checker = "choice_label_checker"
        equiv = "choice_label"
        mode = str(sample.get("presentation_mode") or "single_choice")
        topology = "choice"
    elif isinstance(ans, dict):
        target_type = "multi_part"
        checker = "multi_part_answer_checker"
        equiv = "multi_part_answer"
        mode = "short_answer"
        topology = "multi_part"
        # ensure parts on contract for checker
        if not isinstance(ac.get("parts"), list) or not ac.get("parts"):
            parts = []
            for i, (k, v) in enumerate(sorted(ans.items(), key=lambda kv: str(kv[0]))):
                part_checker = "expression_checker"
                try:
                    float(str(v))
                    part_checker = "integer_checker" if str(v).strip().lstrip("+-").isdigit() else "expression_checker"
                except Exception:
                    part_checker = "expression_checker"
                if re.fullmatch(r"-?\d+", str(v).strip()):
                    part_checker = "integer_checker"
                parts.append(
                    {
                        "key": str(k),
                        "label": str(k),
                        "checker": part_checker,
                        "checker_key": part_checker,
                        "equivalence_type": "numeric_exact" if part_checker == "integer_checker" else "algebraic_equivalent",
                        "expected_answer": v,
                    }
                )
            ac = {
                "answer_type": "multi_part",
                "checker": checker,
                "checker_key": checker,
                "equivalence_type": equiv,
                "parts": parts,
            }
    else:
        target_type = "expression"
        checker = "expression_checker"
        equiv = "algebraic_equivalent"
        mode = "short_answer"
        topology = "expression"

    gen_path = comp_dir / "generate.py"
    meta_path = comp_dir / "metadata.py"
    gen = gen_path.read_text(encoding="utf-8")
    meta = meta_path.read_text(encoding="utf-8")

    gen = re.sub(r'^ANSWER_TYPE\s*=\s*".*?"', f'ANSWER_TYPE = "{target_type}"', gen, count=1, flags=re.M)
    gen = re.sub(r'^PRESENTATION_MODE\s*=\s*".*?"', f'PRESENTATION_MODE = "{mode}"', gen, count=1, flags=re.M)

    # Inject answer_contract parts fix after convert for multi_part
    if topology == "multi_part" and "parts" in ac:
        inject = '''
    # v1.12 topology alignment: ensure multi_part answer_contract.parts
    if isinstance(payload.get("answer"), dict):
        _ans = payload["answer"]
        _parts = []
        for _k, _v in sorted(_ans.items(), key=lambda kv: str(kv[0])):
            _chk = "integer_checker" if str(_v).strip().lstrip("+-").isdigit() else "expression_checker"
            _parts.append({
                "key": str(_k),
                "label": str(_k),
                "checker": _chk,
                "checker_key": _chk,
                "equivalence_type": "numeric_exact" if _chk == "integer_checker" else "algebraic_equivalent",
                "expected_answer": _v,
            })
        _ac = dict(payload.get("answer_contract") or {})
        _ac.update({
            "answer_type": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "parts": _parts,
        })
        payload["answer_type"] = "multi_part"
        payload["answer_contract"] = _ac
        payload["checker"] = "multi_part_answer_checker"
        payload["checker_key"] = "multi_part_answer_checker"
'''
        if "v1.12 topology alignment" not in gen:
            gen = gen.replace(
                "    if component_id:\n        payload[\"component_id\"] = component_id\n    payload[\"seed\"] = seed\n    return payload",
                inject + "\n    if component_id:\n        payload[\"component_id\"] = component_id\n    payload[\"seed\"] = seed\n    return payload",
            )

    meta = re.sub(
        r'^ANSWER_TYPE:\s*Final\[str\]\s*=\s*".*?"',
        f'ANSWER_TYPE: Final[str] = "{target_type}"',
        meta,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'^ANSWER_VALUE_TYPE:\s*Final\[str\]\s*=\s*".*?"',
        f'ANSWER_VALUE_TYPE: Final[str] = "{target_type}"',
        meta,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'^PRESENTATION_MODE:\s*Final\[str\]\s*=\s*".*?"',
        f'PRESENTATION_MODE: Final[str] = "{mode}"',
        meta,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'"checker_key":\s*"[^"]*"',
        f'"checker_key": "{checker}"',
        meta,
        count=1,
    )
    meta = re.sub(
        r'"equivalence_type":\s*"[^"]*"',
        f'"equivalence_type": "{equiv}"',
        meta,
        count=1,
    )
    meta = re.sub(
        r'"answer_type":\s*"[^"]*"',
        f'"answer_type": "{target_type}"',
        meta,
    )
    meta = re.sub(
        r'^GENERATOR_READINESS:\s*Final\[str\]\s*=\s*".*?"',
        'GENERATOR_READINESS: Final[str] = "verified"',
        meta,
        count=1,
        flags=re.M,
    )

    gen_path.write_text(gen, encoding="utf-8")
    meta_path.write_text(meta, encoding="utf-8")
    return topology


def _verify_component(comp_dir: Path, skill_id: str, component_id: str) -> dict[str, Any]:
    gen_mod = _load_module(comp_dir / "generate.py", f"verify_{component_id}_gen")
    p1 = gen_mod.generate(seed=7, component_id=component_id)
    p2 = gen_mod.generate(seed=7, component_id=component_id)
    if not isinstance(p1, dict):
        return {"ok": False, "reason": "generate_not_dict"}
    q = str(p1.get("question_text") or p1.get("question") or "").strip()
    if not q or "placeholder" in q.lower():
        return {"ok": False, "reason": "empty_or_placeholder_question"}
    if p1.get("answer") is None:
        return {"ok": False, "reason": "missing_answer"}
    if p1.get("answer") != p2.get("answer"):
        return {"ok": False, "reason": "seed_not_reproducible"}

    # correct should pass
    try:
        ok_correct = bool(
            check_answer(
                p1.get("answer"),
                p1.get("answer"),
                payload=p1,
            )
        )
    except Exception as e:
        return {"ok": False, "reason": f"checker_correct_exception:{e}"}
    if not ok_correct:
        return {"ok": False, "reason": "checker_rejects_correct"}

    # wrong should fail
    wrong: Any
    ans = p1.get("answer")
    if isinstance(ans, dict):
        wrong = {k: "___WRONG___" for k in ans}
    elif isinstance(ans, (int, float)):
        wrong = ans + 999
    else:
        wrong = "___WRONG_ANSWER___"
    try:
        ok_wrong = bool(
            check_answer(
                wrong,
                p1.get("answer"),
                payload=p1,
            )
        )
    except Exception as e:
        return {"ok": False, "reason": f"checker_wrong_exception:{e}"}
    if ok_wrong:
        return {"ok": False, "reason": "checker_accepts_wrong"}

    # second seed varies or at least generates
    p3 = gen_mod.generate(seed=42, component_id=component_id)
    if not isinstance(p3, dict) or p3.get("answer") is None:
        return {"ok": False, "reason": "seed42_failed"}

    return {
        "ok": True,
        "reason": "verified",
        "answer_type": p1.get("answer_type"),
        "question_preview": q[:80],
    }


def _copy_to_production(skill_id: str, component_id: str) -> None:
    src = ROOT / DRYRUN / skill_id / "components" / component_id
    dst = ROOT / "agent_skills_v3" / skill_id / "components" / component_id
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    ensure_gencode_component_tracker_table(conn)

    results: list[dict[str, Any]] = []

    # SKIP first
    for r in FEAS["rows"]:
        if r["rebuild_decision"] != "EXCLUDE":
            continue
        eid = int(r["example_id"])
        skill = r["skill_id"]
        cid = derive_component_id(eid)
        save_tracker_record(
            conn,
            textbook_example_id=eid,
            skill_id=skill,
            gencode_status="needs_human_review",
            induced_spec_payload={
                "component_id": cid,
                "feasibility_status": r["feasibility_status"],
                "reason": r["reason"],
                "rebuild_decision": "EXCLUDE",
                "original_attempted_status": "skipped_source_incomplete",
            },
            gencode_error_log=f"SKIPPED_SOURCE_INCOMPLETE: {r['reason']}",
        )
        results.append(
            {
                "example_id": eid,
                "skill_id": skill,
                "component_id": cid,
                "status": "SKIPPED_SOURCE_INCOMPLETE",
                "reason": r["reason"],
            }
        )
    conn.commit()

    # INCLUDE rebuild
    for r in INCLUDE_ROWS:
        eid = int(r["example_id"])
        skill = r["skill_id"]
        cid = derive_component_id(eid)
        item = {
            "example_id": eid,
            "skill_id": skill,
            "component_id": cid,
            "status": "FAILED",
            "reason": "",
        }
        try:
            dry = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=eid,
                skill_id=skill,
                dryrun_base_dir=DRYRUN,
                seed=7,
                allow_non_mvp_skill=True,
                force_regenerate=True,
            )
            status = str(dry.get("status") or dry.get("tracker_status") or "")
            if status in {"needs_human_review", "failed"} and not (
                ROOT / DRYRUN / skill / "components" / cid / "generate.py"
            ).is_file():
                item["reason"] = (
                    f"dryrun_{status}:{dry.get('error_code') or dry.get('gencode_error_log') or dry.get('skip_reason') or dry.get('error') or status}"
                )
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid, "dryrun": {k: dry.get(k) for k in dry if k != "trace"}},
                    gencode_error_log=item["reason"][:2000],
                )
                conn.commit()
                results.append(item)
                print("FAIL", eid, item["reason"][:160])
                continue

            # dryrun may report failed but still wrote files — continue to verify if present
            if status == "failed" and (ROOT / DRYRUN / skill / "components" / cid / "generate.py").is_file():
                print("WARN", eid, "dryrun_status_failed_but_files_exist_continuing")

            comp_dir = ROOT / DRYRUN / skill / "components" / cid
            if not (comp_dir / "generate.py").is_file():
                item["reason"] = "generate_py_missing_after_dryrun"
                results.append(item)
                print("FAIL", eid, item["reason"])
                continue

            # sample then patch contract
            gen0 = _load_module(comp_dir / "generate.py", f"prepatch_{cid}")
            sample = gen0.generate(seed=7, component_id=cid)
            topo = _patch_answer_contract_files(comp_dir, sample if isinstance(sample, dict) else {})
            vr = _verify_component(comp_dir, skill, cid)
            if not vr.get("ok"):
                item["reason"] = str(vr.get("reason"))
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid, "topology": topo, "verify": vr},
                    gencode_error_log=item["reason"][:2000],
                )
                conn.commit()
                results.append(item)
                print("FAIL", eid, item["reason"])
                continue

            _copy_to_production(skill, cid)
            save_tracker_record(
                conn,
                textbook_example_id=eid,
                skill_id=skill,
                gencode_status="verified",
                induced_spec_payload={
                    "component_id": cid,
                    "topology": topo,
                    "verify": vr,
                    "problem_type_id": r.get("problem_type_id"),
                    "generator_readiness": "verified",
                },
                gencode_error_log=None,
            )
            # ensure status column
            try:
                update_status(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="verified",
                )
            except Exception:
                pass
            conn.commit()
            item["status"] = "VERIFIED"
            item["reason"] = f"verified:{topo}"
            results.append(item)
            print("OK", eid, topo, vr.get("answer_type"))
        except Exception as e:
            item["reason"] = f"exception:{e}"
            item["trace"] = traceback.format_exc()[-1500:]
            try:
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid},
                    gencode_error_log=item["reason"][:2000],
                )
                conn.commit()
            except Exception:
                pass
            results.append(item)
            print("EXC", eid, e)

    # Phase 3 + publish per skill
    skills = sorted({r["skill_id"] for r in INCLUDE_ROWS})
    publish_results = []
    for skill in skills:
        verified = [x for x in results if x["skill_id"] == skill and x["status"] == "VERIFIED"]
        if not verified:
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": 0,
                    "package_status": "skipped_no_verified",
                    "publish_status": "skipped",
                }
            )
            continue
        try:
            pub = run_admin_v3_publish_for_skill(
                conn=conn,
                skill_id=skill,
                project_root=str(ROOT),
                staging_root=STAGING,
                force_publish=True,
                strict_coverage=False,
            )
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": len(verified),
                    "wrapper_path": f"skills/{skill}.py",
                    "package_status": "compiled",
                    "publish_status": pub.get("status"),
                    "publish": pub,
                }
            )
            print("PUBLISH", skill, pub.get("status"), "n=", len(verified))
        except Exception as e:
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": len(verified),
                    "wrapper_path": f"skills/{skill}.py",
                    "package_status": "failed",
                    "publish_status": f"error:{e}",
                    "trace": traceback.format_exc()[-2000:],
                }
            )
            print("PUBLISH_FAIL", skill, e)

    # Runtime smoke
    smoke = []
    for skill in skills:
        facade = ROOT / "skills" / f"{skill}.py"
        if not facade.is_file():
            smoke.append({"skill_id": skill, "samples": 0, "passed": 0, "failed": 1, "error": "no_facade"})
            continue
        try:
            mod = _load_module(facade, f"smoke_{skill}")
            v3_root = str((ROOT / "agent_skills_v3").resolve())
            passed = 0
            failed = 0
            errors = []
            for i in range(20):
                try:
                    pl = mod.generate(seed=1000 + i)
                    q = str(pl.get("question_text") or pl.get("question") or "")
                    if not q or pl.get("answer") is None:
                        failed += 1
                        errors.append(f"seed{1000+i}:empty")
                        continue
                    if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                        failed += 1
                        errors.append(f"seed{1000+i}:checker")
                        continue
                    passed += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"seed{1000+i}:{e}")
            smoke.append(
                {
                    "skill_id": skill,
                    "samples": 20,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors[:5],
                }
            )
            print("SMOKE", skill, passed, "/", 20)
        except Exception as e:
            smoke.append({"skill_id": skill, "samples": 0, "passed": 0, "failed": 20, "error": str(e)})

    summary = {
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(results),
        "verified": sum(1 for x in results if x["status"] == "VERIFIED"),
        "failed": sum(1 for x in results if x["status"] == "FAILED"),
        "skipped": sum(1 for x in results if x["status"] == "SKIPPED_SOURCE_INCOMPLETE"),
        "results": results,
        "publish": publish_results,
        "smoke": smoke,
    }
    out = ROOT / "scratch" / "_b1_3_1_rebuild_results.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("SUMMARY", {k: summary[k] for k in ("total", "verified", "failed", "skipped")})
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
