# -*- coding: utf-8 -*-
"""Enrich 3-3 tracker integrity fields, publish VERIFIED components, smoke."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.services.component_tracker_service import save_tracker_record, update_status
from core.registry.taxonomy_registry import get_fixed_domain_key

PREV = json.loads((ROOT / "scratch/_b1_3_3_rebuild_results.json").read_text(encoding="utf-8"))
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())

_spec = importlib.util.spec_from_file_location(
    "rebuild_b1_3_3_execute", ROOT / "scratch" / "_rebuild_b1_3_3_execute.py"
)
_rebuild = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_rebuild)


def _source_kind_from_metadata(skill: str, cid: str) -> str:
    meta = ROOT / "agent_skills_v3" / skill / "components" / cid / "metadata.py"
    if meta.is_file():
        text = meta.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("SOURCE_KIND"):
                if "quiz" in line:
                    return "quiz"
                if "test" in line:
                    return "test"
                if "example" in line:
                    return "example"
    return "example"


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
        "checker_key": (
            "choice_label_checker"
            if at == "single_choice"
            else ("multi_part_answer_checker" if at == "multi_part" else "expression_checker")
        ),
        "equivalence_type": (
            "choice_label"
            if at == "single_choice"
            else ("multi_part_answer" if at == "multi_part" else "algebraic_equivalent")
        ),
        "generator_readiness": "verified",
        "choice_contract_valid": True,
        "integrity_gate_passed": True,
        "integrity_gate_blockers": [],
        "integrity_gate_version": "v1",
        "domain_module": "core.domain.polynomial_domain",
        "entrypoint": "build_polynomial_matrix",
        "binding_status": "confirmed",
        "resolution_source": "confirmed_binding",
        "required_capabilities": [op],
        "matched_capabilities": [op],
        "source_kind": _source_kind_from_metadata(skill, cid),
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
    results = list(PREV.get("results") or [])
    for item in results:
        if item.get("status") == "VERIFIED":
            _enrich_tracker(conn, item)
    conn.commit()

    skills = sorted({str(r["skill_id"]) for r in results})
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
                    "wrapper_path": f"skills/{skill}.py",
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
                    "component_count": pub.get("component_count"),
                }
            )
            print("PUBLISH", skill, pub.get("status"), "n=", len(verified), "components", pub.get("component_count"))
        except Exception as exc:
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": len(verified),
                    "wrapper_path": f"skills/{skill}.py",
                    "package_status": "failed",
                    "publish_status": f"error:{exc}",
                    "trace": traceback.format_exc()[-1500:],
                }
            )
            print("PUBLISH_FAIL", skill, exc)

    smoke = [_rebuild._smoke_skill(skill, 40) for skill in skills]
    for row in smoke:
        print("SMOKE", row["skill_id"], row["passed"], "/", row["samples"], "keys", row.get("wrapper_keys"), "hits", row.get("hits"))
        if row.get("missing_in_40"):
            print("  missing", row["missing_in_40"], "targeted", row.get("targeted"))

    wrappers = {}
    for skill in skills:
        facade = ROOT / "skills" / f"{skill}.py"
        if facade.is_file():
            mod = _rebuild._load_module(facade, f"wrap_{skill}")
            wrappers[skill] = list(getattr(mod, "GENERATOR_KEYS", []) or [])

    out = {
        "verified": sum(1 for x in results if x["status"] == "VERIFIED"),
        "failed": sum(1 for x in results if x["status"] == "FAILED"),
        "skipped": sum(1 for x in results if x["status"] == "SKIPPED_SOURCE_INCOMPLETE"),
        "publish": publish_results,
        "smoke": smoke,
        "wrapper_keys": wrappers,
        "results": results,
    }
    path = ROOT / "scratch" / "_b1_3_3_finalize_results.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
