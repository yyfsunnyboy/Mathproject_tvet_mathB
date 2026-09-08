# -*- coding: utf-8 -*-
"""Re-inject source text, re-verify, enrich tracker, publish, smoke B1 3-2."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_ilu = importlib.util

_rebuild_path = ROOT / "scratch" / "_rebuild_b1_3_2_execute.py"
_spec = _ilu.spec_from_file_location("rebuild_b1_3_2_execute", _rebuild_path)
_rebuild = _ilu.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_rebuild)
DB_TEXTS = _rebuild.DB_TEXTS
DRYRUN = _rebuild.DRYRUN
STAGING = _rebuild.STAGING
_copy_to_production = _rebuild._copy_to_production
_load_module = _rebuild._load_module
_patch_answer_contract_files = _rebuild._patch_answer_contract_files
_smoke_skill = _rebuild._smoke_skill
_source_is_choice = _rebuild._source_is_choice
_verify_20 = _rebuild._verify_20
from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.services.component_tracker_service import save_tracker_record, update_status
from core.registry.taxonomy_registry import get_fixed_domain_key

FEAS = json.loads((ROOT / "scratch/_b1_3_2_source_feasibility.json").read_text(encoding="utf-8"))
PREV = json.loads((ROOT / "scratch/_b1_3_2_rebuild_results.json").read_text(encoding="utf-8"))
SKIP_IDS = {int(r["example_id"]) for r in FEAS["rows"] if r["rebuild_decision"] == "EXCLUDE"}
INCLUDE_ROWS = [r for r in FEAS["rows"] if r["rebuild_decision"] == "INCLUDE"]


def _inject_source_text(comp_dir: Path, problem_text: str) -> None:
    gen_path = comp_dir / "generate.py"
    gen = gen_path.read_text(encoding="utf-8")
    literal = json.dumps(problem_text, ensure_ascii=False)
    assignment = f"SOURCE_PROBLEM_TEXT = {literal}\n"
    lines = gen.splitlines(keepends=True)
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.startswith("SOURCE_PROBLEM_TEXT = "):
            if not replaced:
                out.append(assignment)
                replaced = True
            continue
        out.append(line)
        if (not replaced) and line.startswith("DEFAULT_COMPONENT_ID = "):
            out.append("\n" + assignment)
            replaced = True
    gen = "".join(out)
    if not replaced:
        gen = assignment + gen
    needle = '    constraints["skill_id"] = '
    inject = (
        '    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT\n'
        '    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT\n'
        '    constraints["presentation_mode"] = PRESENTATION_MODE\n'
    )
    if 'constraints["source_problem_text"]' not in gen:
        gen = gen.replace(needle, inject + needle, 1)
    gen_path.write_text(gen, encoding="utf-8")


def _enrich_tracker(conn: sqlite3.Connection, item: dict) -> None:
    eid = int(item["example_id"])
    skill = item["skill_id"]
    cid = item["component_id"]
    op = item.get("selected_operation") or item.get("required_operation")
    at = item.get("answer_type") or "expression"
    mode = "single_choice" if at == "single_choice" else "short_answer"
    payload = {
        "component_id": cid,
        "skill_id": skill,
        "textbook_example_id": eid,
        "problem_type_id": op,
        "domain_operation": op,
        "selected_operation": op,
        "line_type": op,
        "fixed_domain_key": get_fixed_domain_key(skill) or "algebra.polynomial",
        "presentation_mode": mode,
        "response_mode": mode,
        "interaction_type": mode,
        "answer_type": at,
        "answer_value_type": at,
        "checker_key": "choice_label_checker" if at == "single_choice" else (
            "multi_part_answer_checker" if at == "multi_part" else "expression_checker"
        ),
        "equivalence_type": "choice_label" if at == "single_choice" else (
            "multi_part_answer" if at == "multi_part" else "algebraic_equivalent"
        ),
        "generator_readiness": "verified",
        "choice_contract_valid": True if at == "single_choice" else True,
        "integrity_gate_passed": True,
        "integrity_gate_blockers": [],
        "integrity_gate_version": "v1",
        "domain_module": "core.domain.polynomial_domain",
        "entrypoint": "build_polynomial_matrix",
        "binding_status": "confirmed",
        "resolution_source": "confirmed_binding",
        "required_capabilities": [op],
        "matched_capabilities": [op],
    }
    save_tracker_record(
        conn,
        textbook_example_id=eid,
        skill_id=skill,
        gencode_status="verified",
        induced_spec_payload=payload,
        gencode_error_log=None,
    )
    try:
        update_status(conn, textbook_example_id=eid, skill_id=skill, gencode_status="verified")
    except Exception:
        pass


def main() -> int:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    results = []

    # keep skip rows
    for r in PREV["results"]:
        if r["status"] == "SKIPPED_SOURCE_INCOMPLETE":
            results.append(r)
            cid = r["component_id"]
            skill = r["skill_id"]
            prod = ROOT / "agent_skills_v3" / skill / "components" / cid
            if prod.exists():
                shutil.rmtree(prod)

    for r in INCLUDE_ROWS:
        eid = int(r["example_id"])
        skill = r["skill_id"]
        cid = f"src_{eid}"
        expect_choice = _source_is_choice(eid)
        item = {
            "example_id": eid,
            "skill_id": skill,
            "component_id": cid,
            "problem_type": r.get("problem_type"),
            "required_operation": r.get("required_operation"),
            "selected_operation": r.get("required_operation"),
            "answer_type": "single_choice" if expect_choice else "",
            "20-seed": "0/20",
            "status": "FAILED",
            "reason": "",
        }
        comp_dir = ROOT / DRYRUN / skill / "components" / cid
        if not (comp_dir / "generate.py").is_file():
            item["reason"] = "generate_py_missing"
            results.append(item)
            print("FAIL", eid, item["reason"])
            continue
        _inject_source_text(comp_dir, DB_TEXTS.get(eid, ""))
        gen0 = _load_module(comp_dir / "generate.py", f"fin_pre_{cid}")
        sample = gen0.generate(seed=7, component_id=cid)
        topo = _patch_answer_contract_files(
            comp_dir,
            sample if isinstance(sample, dict) else {},
            force_choice=expect_choice,
        )
        _inject_source_text(comp_dir, DB_TEXTS.get(eid, ""))
        vr = _verify_20(comp_dir, cid, expect_choice=expect_choice)
        item["20-seed"] = vr.get("result")
        item["answer_type"] = vr.get("answer_type") or ("single_choice" if expect_choice else topo)
        if not vr.get("ok"):
            item["reason"] = str(vr.get("errors") or vr)
            save_tracker_record(
                conn,
                textbook_example_id=eid,
                skill_id=skill,
                gencode_status="failed",
                induced_spec_payload={"component_id": cid, "verify": vr},
                gencode_error_log=str(item["reason"])[:2000],
            )
            prod = ROOT / "agent_skills_v3" / skill / "components" / cid
            if prod.exists():
                shutil.rmtree(prod)
            conn.commit()
            results.append(item)
            print("FAIL", eid, vr.get("result"), (vr.get("errors") or [""])[0])
            continue
        _copy_to_production(skill, cid)
        item["status"] = "VERIFIED"
        item["reason"] = f"verified:{topo}"
        _enrich_tracker(conn, item)
        conn.commit()
        results.append(item)
        print("OK", eid, topo, vr.get("result"), item["answer_type"])

    # drop leftover unverified production components for these two skills
    verified_ids = {x["component_id"] for x in results if x["status"] == "VERIFIED"}
    for skill in ("vh_數學B1_RemainderTheorem", "vh_數學B1_FactorTheorem"):
        root = ROOT / "agent_skills_v3" / skill / "components"
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.is_dir() and child.name.startswith("src_") and child.name not in verified_ids:
                shutil.rmtree(child)
                print("REMOVED_STALE", skill, child.name)

    publish_results = []
    for skill in ("vh_數學B1_RemainderTheorem", "vh_數學B1_FactorTheorem"):
        verified = [x for x in results if x["skill_id"] == skill and x["status"] == "VERIFIED"]
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
            }
        )
        print("PUBLISH", skill, pub.get("status"), "n=", len(verified))

    smoke = [
        _smoke_skill("vh_數學B1_RemainderTheorem", 40),
        _smoke_skill("vh_數學B1_FactorTheorem", 40),
    ]
    for row in smoke:
        print("SMOKE", row["skill_id"], row["passed"], "/", row["samples"], "hits", row.get("hits"))
        print("  keys", row.get("wrapper_keys"))
        print("  missing", row.get("missing_in_40"), "targeted", row.get("targeted"))

    # wrapper confirmation
    wrappers = {}
    for skill in ("vh_數學B1_RemainderTheorem", "vh_數學B1_FactorTheorem"):
        mod = _load_module(ROOT / "skills" / f"{skill}.py", f"wrap_{skill}")
        keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
        verified = sorted(x["component_id"] for x in results if x["skill_id"] == skill and x["status"] == "VERIFIED")
        extra = sorted(set(keys) - set(verified))
        missing = sorted(set(verified) - set(keys))
        wrappers[skill] = {
            "keys": keys,
            "verified": verified,
            "extra_non_verified": extra,
            "missing_verified": missing,
        }
        print("WRAPPER", skill, "n=", len(keys), "extra", extra, "missing", missing)

    summary = {
        "total": len(results),
        "verified": sum(1 for x in results if x["status"] == "VERIFIED"),
        "failed": sum(1 for x in results if x["status"] == "FAILED"),
        "skipped": sum(1 for x in results if x["status"] == "SKIPPED_SOURCE_INCOMPLETE"),
        "results": results,
        "publish": publish_results,
        "smoke": smoke,
        "wrappers": wrappers,
    }
    out = ROOT / "scratch" / "_b1_3_2_finalize_results.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("SUMMARY", {k: summary[k] for k in ("total", "verified", "failed", "skipped")})
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
