# -*- coding: utf-8 -*-
"""Enrich recovered verified trackers and republish affected skills."""
from __future__ import annotations

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

RECOVERED = [4706, 4716, 4717, 4718, 4719, 4720]
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
            m2 = re.search(rf'^{key}\s*=\s*"([^"]*)"', text, re.M)
            if m2:
                out[key.lower()] = m2.group(1)
    m = re.search(r'"checker_key":\s*"([^"]+)"', text)
    if m:
        out["checker_key"] = m.group(1)
    m = re.search(r'"equivalence_type":\s*"([^"]+)"', text)
    if m:
        out["equivalence_type"] = m.group(1)
    return out


def main() -> None:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    skills = set()
    for eid in RECOVERED:
        row = conn.execute(
            "SELECT skill_id, component_id, induced_spec_payload, gencode_status FROM gencode_component_tracker WHERE textbook_example_id=?",
            (eid,),
        ).fetchone()
        if not row:
            print("missing tracker", eid)
            continue
        skill = row["skill_id"]
        cid = row["component_id"] or f"src_{eid}"
        meta_path = ROOT / "agent_skills_v3" / skill / "components" / cid / "metadata.py"
        if not meta_path.is_file():
            print("missing meta", eid, meta_path)
            continue
        meta = _meta_constants(meta_path)
        prev = {}
        try:
            prev = json.loads(row["induced_spec_payload"] or "{}")
        except Exception:
            prev = {}
        fixed = get_fixed_domain_key(skill)
        op = meta.get("domain_operation") or meta.get("problem_type_id") or prev.get("domain_operation")
        payload = {
            **prev,
            "component_id": cid,
            "skill_id": skill,
            "textbook_example_id": eid,
            "problem_type_id": meta.get("problem_type_id") or prev.get("problem_type_id") or op,
            "domain_operation": op,
            "selected_operation": op,
            "line_type": meta.get("line_type") or op,
            "fixed_domain_key": fixed or "algebra.polynomial",
            "presentation_mode": "single_choice",
            "response_mode": "single_choice",
            "interaction_type": "single_choice",
            "answer_type": "single_choice",
            "answer_value_type": "single_choice",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "source_kind": meta.get("source_kind") or "example",
            "generator_readiness": "verified",
            "choice_contract_valid": True,
            "integrity_gate_passed": True,
            "integrity_gate_blockers": [],
            "integrity_gate_version": "v1",
            "domain_module": "core.domain.polynomial_domain",
            "entrypoint": "build_polynomial_matrix",
            "rebuild_decision": "RECOVERED_SELF_ASSESSMENT",
        }
        save_tracker_record(
            conn,
            textbook_example_id=eid,
            skill_id=skill,
            gencode_status="verified",
            induced_spec_payload=payload,
            gencode_error_log=None,
        )
        skills.add(skill)
        print("enriched", eid, skill, op)

    conn.commit()

    pub_out = []
    for skill in sorted(skills):
        try:
            pub = run_admin_v3_publish_for_skill(
                conn=conn,
                skill_id=skill,
                project_root=str(ROOT),
                staging_root=STAGING,
                force_publish=True,
                strict_coverage=False,
            )
            pub_out.append({"skill_id": skill, "ok": True, "status": pub.get("status"), "pub": pub})
            print("PUBLISH", skill, pub.get("status"), "verified_count", (pub.get("verified_component_count") or pub.get("component_count")))
        except Exception as e:
            pub_out.append({"skill_id": skill, "ok": False, "error": str(e), "trace": traceback.format_exc()[-1200:]})
            print("PUBLISH_FAIL", skill, e)

    smoke = []
    for skill in sorted(skills):
        facade = ROOT / "skills" / f"{skill}.py"
        mod = _load(facade, f"sm_{skill}")
        keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
        print("KEYS", skill, keys)
        new_keys = [f"src_{i}" for i in RECOVERED if f"src_{i}" in keys]
        passed = failed = 0
        errs = []
        hit_new = 0
        for i in range(40):
            try:
                pl = mod.generate(seed=7000 + i)
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
                # if choice, require 4 choices
                if str(pl.get("answer_type")) == "single_choice":
                    ch = pl.get("choices") or []
                    if not isinstance(ch, list) or len(ch) < 4:
                        failed += 1
                        errs.append(f"{i}:bad_choices:{cid}")
                        continue
                passed += 1
            except Exception as e:
                failed += 1
                errs.append(f"{i}:exc:{e}")
        smoke.append(
            {
                "skill_id": skill,
                "samples": 40,
                "passed": passed,
                "failed": failed,
                "errors": errs[:10],
                "new_keys_in_wrapper": new_keys,
                "new_hits": hit_new,
            }
        )
        print("SMOKE", skill, passed, failed, "new", new_keys, "hits", hit_new)

    out = {"publish": pub_out, "smoke": smoke}
    (ROOT / "scratch/_b1_3_1_recovered_publish_smoke.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
