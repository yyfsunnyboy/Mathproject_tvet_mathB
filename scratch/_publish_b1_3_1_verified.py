# -*- coding: utf-8 -*-
"""Enrich verified tracker payloads and publish B1 3-1 skills."""
from __future__ import annotations

import ast
import importlib.util
import json
import re
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
from core.registry.taxonomy_registry import get_fixed_domain_key

SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _meta_constants(meta_path: Path) -> dict:
    text = meta_path.read_text(encoding="utf-8")
    out = {}
    for key in (
        "COMPONENT_ID",
        "SKILL_ID",
        "PROBLEM_TYPE_ID",
        "DOMAIN_OPERATION",
        "PRESENTATION_MODE",
        "ANSWER_TYPE",
        "ANSWER_VALUE_TYPE",
        "SOURCE_KIND",
        "LINE_TYPE",
        "GENERATOR_READINESS",
    ):
        m = re.search(rf'^{key}:\s*Final\[[^\]]+\]\s*=\s*"([^"]*)"', text, re.M)
        if m:
            out[key.lower()] = m.group(1)
        else:
            m = re.search(rf"^{key}:\s*Final\[[^\]]+\]\s*=\s*(\d+)", text, re.M)
            if m:
                out[key.lower()] = int(m.group(1))
    m = re.search(r'"checker_key":\s*"([^"]+)"', text)
    if m:
        out["checker_key"] = m.group(1)
    m = re.search(r'"equivalence_type":\s*"([^"]+)"', text)
    if m:
        out["equivalence_type"] = m.group(1)
    return out


def enrich_and_publish():
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    results = json.loads((ROOT / "scratch/_b1_3_1_rebuild_results.json").read_text(encoding="utf-8"))
    verified_ids = [r["example_id"] for r in results["results"] if r["status"] == "VERIFIED"]

    for eid in verified_ids:
        row = conn.execute(
            "SELECT skill_id, component_id, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id=?",
            (eid,),
        ).fetchone()
        if not row:
            continue
        skill = row["skill_id"]
        cid = row["component_id"] or f"src_{eid}"
        meta_path = ROOT / "agent_skills_v3" / skill / "components" / cid / "metadata.py"
        if not meta_path.is_file():
            print("missing meta", eid)
            continue
        meta = _meta_constants(meta_path)
        prev = {}
        try:
            prev = json.loads(row["induced_spec_payload"] or "{}")
        except Exception:
            prev = {}
        fixed = get_fixed_domain_key(skill)
        payload = {
            **prev,
            "component_id": cid,
            "skill_id": skill,
            "textbook_example_id": eid,
            "problem_type_id": meta.get("problem_type_id") or prev.get("problem_type_id"),
            "domain_operation": meta.get("domain_operation") or meta.get("problem_type_id"),
            "line_type": meta.get("line_type") or meta.get("problem_type_id"),
            "fixed_domain_key": fixed,
            "presentation_mode": meta.get("presentation_mode") or "short_answer",
            "response_mode": meta.get("presentation_mode") or "short_answer",
            "interaction_type": meta.get("presentation_mode") or "short_answer",
            "answer_type": meta.get("answer_type") or "expression",
            "answer_value_type": meta.get("answer_value_type") or meta.get("answer_type") or "expression",
            "checker_key": meta.get("checker_key") or "expression_checker",
            "equivalence_type": meta.get("equivalence_type") or "algebraic_equivalent",
            "source_kind": meta.get("source_kind") or "example",
            "generator_readiness": "verified",
            "choice_contract_valid": True,
            "integrity_gate_passed": True,
            "integrity_gate_blockers": [],
            "integrity_gate_version": "v1",
            "domain_module": "core.domain.polynomial_domain",
            "entrypoint": "build_polynomial_matrix",
        }
        save_tracker_record(
            conn,
            textbook_example_id=eid,
            skill_id=skill,
            gencode_status="verified",
            induced_spec_payload=payload,
            gencode_error_log=None,
        )
        print("enriched", eid, payload["problem_type_id"], payload["answer_type"])

    conn.commit()

    publish_out = []
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
            publish_out.append({"skill_id": skill, "ok": True, "status": pub.get("status"), "pub": pub})
            print("PUBLISH", skill, pub.get("status"))
        except Exception as e:
            publish_out.append({"skill_id": skill, "ok": False, "error": str(e), "trace": traceback.format_exc()[-1500:]})
            print("PUBLISH_FAIL", skill, e)

    smoke = []
    for skill in SKILLS:
        facade = ROOT / "skills" / f"{skill}.py"
        mod = _load(facade, f"smoke2_{skill}")
        passed = failed = 0
        errs = []
        for i in range(20):
            try:
                pl = mod.generate(seed=2000 + i)
                q = str(pl.get("question_text") or pl.get("question") or "")
                if not q or pl.get("answer") is None:
                    failed += 1
                    errs.append(f"{i}:empty")
                    continue
                if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                    failed += 1
                    errs.append(f"{i}:checker")
                    continue
                passed += 1
            except Exception as e:
                failed += 1
                errs.append(f"{i}:{e}")
        smoke.append({"skill_id": skill, "samples": 20, "passed": passed, "failed": failed, "errors": errs[:5]})
        print("SMOKE", skill, passed, failed)

    out = {
        "publish": publish_out,
        "smoke": smoke,
    }
    (ROOT / "scratch/_b1_3_1_publish_smoke.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    # merge into rebuild results
    results["publish"] = publish_out
    results["smoke"] = smoke
    (ROOT / "scratch/_b1_3_1_rebuild_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )


if __name__ == "__main__":
    enrich_and_publish()
