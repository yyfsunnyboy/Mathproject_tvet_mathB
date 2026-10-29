"""discrete.combinations (數學2 Unit 5) deployment rehearsal on a DB copy and a sandbox project root.

1. isolated promotion of the reviewed bundle into a TEMP store / TEMP package root (the approval label is
   ``isolated_test_only`` on a temp copy of the workspace; production store and core/domain/promoted are
   asserted unchanged afterwards - this is NOT the human approval),
2. official Phase 2 (run_gencode_phase2_raw) for every component into the sandbox dry-run dir,
3. per-component verification of the promoted package through the generated components (20 seeds),
4. official Phase 3 publish into the sandbox project / staging roots, then student-side facade smoke
   (canonical, equivalent and wrong answers on every served payload).

Usage: rehearse_unit5.py [--sandbox tmp/gh_math2u5_rehearsal/run] [--no-publish]
Nothing here writes instance/kumon_math.db, configs/, core/domain/promoted, skills/, agent_skills_v3/,
reports/gencode_v3_dryrun or runtime/v3_publish_staging; a write scan over those paths is in the report.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.combinations import build_sandbox as B  # noqa: E402
from agent_domains_candidate.combinations import verification as V  # noqa: E402
from agent_domains_candidate.combinations.combinations_specs import OP, SKILLS  # noqa: E402

sys.path.insert(0, str(HERE))
from build_bundle import COMPONENTS, FIXED_ROWS, WORKSPACE  # noqa: E402

USED_SKILLS = sorted({SKILLS[spec[0]] for spec in COMPONENTS.values()})  #

PRODUCTION_STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN = B.DOMAIN_KEY
WATCH = [ROOT / p for p in ("configs", "core/domain/promoted", "skills", "agent_skills_v3", "reports/gencode_v3_dryrun",
                            "runtime/v3_publish_staging", "instance/kumon_math.db")]


def _opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        value = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return value
    return default


def scan_written(start: float) -> list[str]:
    changed = []
    for base in WATCH:
        files = [base] if base.is_file() else [Path(d) / n for d, ds, ns in os.walk(base) for n in ns if "__pycache__" not in d] if base.exists() else []
        for path in files:
            try:
                if path.stat().st_mtime >= start:
                    changed.append(str(path.relative_to(ROOT)))
            except OSError:
                pass
    return sorted(changed)


@contextlib.contextmanager
def isolated_promotion():
    from core.gencode.reviewed_capability_promotion import BUNDLE_FILENAME, promote_reviewed_workspace
    from core.registry import promoted_capability_store as store_mod

    store_bytes = PRODUCTION_STORE.read_bytes()
    packages_before = sorted(p.name for p in (ROOT / "core/domain/promoted").iterdir() if p.name != "__pycache__")
    prefix_dir = f"gh_math2u5_rehearsal_{uuid.uuid4().hex[:10]}"
    base = ROOT / "tmp" / "gh_math2u5_rehearsal" / prefix_dir
    (base / "packages").mkdir(parents=True)
    workspace = base / "workspace"
    shutil.copytree(WORKSPACE, workspace, ignore=shutil.ignore_patterns("__pycache__"))
    store = base / "store" / "promoted_capabilities.json"
    store.parent.mkdir(parents=True)
    store.write_bytes(store_bytes)
    bundle = json.loads((workspace / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    bundle["review"].update(status="human_approved", approved_by="isolated_test_only", approved_revision=bundle["proposal_revision"])
    (workspace / BUNDLE_FILENAME).write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    prefix = f"tmp.gh_math2u5_rehearsal.{prefix_dir}.packages"
    package_import = f"{prefix}.{bundle['package_name']}"
    snapshot = store_mod.snapshot_runtime_state(DOMAIN, USED_SKILLS, package_import)
    try:
        result = promote_reviewed_workspace(workspace, teacher_approved=True, store_path=store, package_root=base / "packages",
                                            package_import_prefix=prefix)
        yield result
    finally:
        store_mod.restore_runtime_state(snapshot)
        for name in [n for n in sys.modules if n.startswith(f"tmp.gh_math2u5_rehearsal.{prefix_dir}")]:
            sys.modules.pop(name, None)
        assert PRODUCTION_STORE.read_bytes() == store_bytes, "production promoted store changed"
        assert sorted(p.name for p in (ROOT / "core/domain/promoted").iterdir() if p.name != "__pycache__") == packages_before


def _load_generate(path: Path):
    spec = importlib.util.spec_from_file_location(f"rehearse_{uuid.uuid4().hex}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate


def verify_component(dryrun: Path, skill: str, cid: int, seeds: int = 20) -> dict:
    gen = dryrun / skill / "components" / f"src_{cid}" / "generate.py"
    out = {"generate_sha256": hashlib.sha256(gen.read_bytes()).hexdigest(), "checked_seeds": 0, "failures": []}
    generate = _load_generate(gen)
    surfaces = set()
    for seed in range(seeds):
        payload = generate(seed=seed, component_id=f"src_{cid}")
        problems = []
        if payload.get("skill_id") != skill or payload.get("textbook_example_id") != cid:
            problems.append("identity")
        problems += V.verify_payload(payload, skill, f"src_{cid}")
        if problems:
            out["failures"].append(f"seed{seed}:{problems}")
        surfaces.add(json.dumps([payload["question_text"], payload.get("visual_spec"), payload["correct_answer"]],
                                sort_keys=True, ensure_ascii=False, default=str))
        out["checked_seeds"] += 1
    out["distinct_surfaces"] = len(surfaces)
    return out


def rebuild(conn, dryrun: Path) -> dict:
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    report = {}
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        skill = SKILLS[skill_key]
        variants = B.collect_variants(cid, op, source, sampler)
        payload = dispatch_registered_operation(DOMAIN, op, seed=0, constraints=dict(source))[1]
        spec = {"fixed_domain_key": DOMAIN, "required_capabilities": [op], "domain_operation": OP[op], "problem_type_id": OP[op],
                "presentation_mode": payload["presentation_mode"], "answer_type": payload["answer_type"],
                "generation_constraints": {"variants": variants}}
        try:
            result = run_gencode_phase2_raw(skill, dry_run=True, v3_textbook_example_id=cid, v3_conn=conn,
                                            v3_dryrun_base_dir=str(dryrun), force_regenerate=True, v3_induced_spec=spec)
        except Exception as exc:  # noqa: BLE001
            report[cid] = {"skill": skill, "exception": f"{type(exc).__name__}: {exc}"}
            print(cid, "EXC", report[cid]["exception"][:200], flush=True)
            continue
        bridge = result.get("v3_shadow_bridge") or {}
        item = {"skill": skill, "operation": op, "variants": len(variants), "phase_status": result.get("phase_status"),
                "tracker_status": result.get("tracker_status"), "error_code": bridge.get("error_code"),
                "error": bridge.get("error") or bridge.get("error_message")}
        row = conn.execute("select skill_id, gencode_status from gencode_component_tracker where textbook_example_id=?", (cid,)).fetchone()
        item["tracker"] = list(row) if row else None
        if (dryrun / skill / "components" / f"src_{cid}" / "generate.py").is_file():
            item["verify"] = verify_component(dryrun, skill, cid)
        report[cid] = item
        print(cid, skill[3:], item["tracker"], (item.get("verify") or {}).get("failures"), flush=True)
    return report


def publish(conn, project: Path, staging: Path) -> dict:
    import core.gencode.v3_production_publish_service as pub

    pub.PROJECT_ROOT = project
    out = {}
    for skill in USED_SKILLS:
        try:
            result = pub.publish_single_v3_skill_to_production(conn=conn, skill_id=skill, project_root=str(project),
                                                               staging_root=str(staging), allow_partial_coverage=False)
            out[skill] = {k: result.get(k) for k in ("status", "component_count", "smoke_status", "staging_smoke_status",
                                                     "production_smoke_status", "variation_status", "dynamic_count", "static_count",
                                                     "variation_warning")}
            out[skill]["published_components"] = sorted(p.name for p in (project / "agent_skills_v3" / skill / "components").iterdir()
                                                        if p.is_dir() and not p.name.startswith("__"))
        except Exception as exc:  # noqa: BLE001
            out[skill] = {"exception": f"{type(exc).__name__}: {exc}"}
        print("publish", skill, out[skill].get("status") or out[skill].get("exception"), flush=True)
    return out


def _verdict(res, default: bool) -> bool:
    return res if isinstance(res, bool) else bool(res.get("correct", res.get("is_correct", default)))


def facade_smoke(project: Path, seeds: int = 80) -> dict:
    """Student-side grading through the published facades: canonical / equivalent accepted, wrong rejected."""
    out = {}
    for skill in USED_SKILLS:
        facade = project / "skills" / f"{skill}.py"
        if not facade.is_file():
            out[skill] = "no facade"
            continue
        spec = importlib.util.spec_from_file_location(f"facade_{uuid.uuid4().hex}", facade)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        served: dict = {}
        problems = []
        drawing_only: set = set()
        for seed in range(seeds):
            payload = module.generate(seed=seed)
            served[payload.get("textbook_example_id")] = served.get(payload.get("textbook_example_id"), 0) + 1
            expected = payload["correct_answer"]
            if payload["answer_contract"].get("answer_type") == "drawing" or any(p.get("answer_type") == "drawing" for p in payload["answer_contract"].get("parts") or []):
                drawing_only.add(payload.get("textbook_example_id"))  # AI-graded canvas: served and contract-checked by verify_payload, not submitted
                continue
            if not _verdict(module.check(expected, expected, question_payload=payload), True):
                problems.append(f"seed{seed}:canonical_rejected")
            if not isinstance(module.get_hint(1, question_payload=payload), str):
                problems.append(f"seed{seed}:hint")
            multi = payload["answer_contract"]["answer_type"] == "multi_part"
            for part in V.parts_of(payload):
                for kind, value, want in (("wrong", V.wrong_value(part), False), ("equivalent", V.equivalent_value(part), True)):
                    if value is None:  # no distinct equivalent rendering for this checker
                        continue
                    answer = {**expected, part["key"]: value} if multi else value
                    if _verdict(module.check(answer, expected, question_payload=payload), not want) != want:
                        problems.append(f"seed{seed}:{part['key']}:{kind}_misgraded")
        out[skill] = {"served_examples": dict(sorted(served.items())), "problems": problems, "drawing_served_only": sorted(drawing_only)}
    return out


def main() -> None:
    sandbox = Path(_opt("--sandbox", str(ROOT / "tmp" / "gh_math2u5_rehearsal" / "run"))).resolve()
    project, staging = sandbox / "project", sandbox / "staging"
    dryrun = project / "reports" / "gencode_v3_dryrun"
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (project / "skills").mkdir(parents=True)
    staging.mkdir(parents=True)
    db = sandbox / "rehearsal.db"
    source = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
    target = sqlite3.connect(db)
    source.backup(target)
    target.close()
    source.close()
    start = time.time() - 1
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    report = {"sandbox": str(sandbox), "deferred": {str(k): v for k, v in FIXED_ROWS.items()}}
    try:
        with isolated_promotion() as promotion:
            report["promotion"] = {k: promotion.get(k) for k in ("domain_key", "registry_revision", "unchanged") if k in promotion}
            report["promotion"]["operations_executed"] = (promotion.get("verification") or {}).get("operations_executed")
            report["rebuild"] = rebuild(conn, dryrun)
            if "--no-publish" not in sys.argv:
                report["publish"] = publish(conn, project, staging)
                report["student_side"] = facade_smoke(project)
    finally:
        conn.close()
        report["production_paths_written"] = scan_written(start)
        (HERE / "rehearsal_unit5_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    failures = {cid: item for cid, item in report.get("rebuild", {}).items()
                if item.get("exception") or (item.get("verify") or {}).get("failures") or (item.get("tracker") or [None, None])[1] != "verified"}
    print(json.dumps({"components": len(report.get("rebuild", {})), "failures": failures,
                      "production_paths_written": report["production_paths_written"],
                      "publish": {k: v.get("status") or v.get("exception") for k, v in (report.get("publish") or {}).items()},
                      "student_side": {k: (v if isinstance(v, str) else {"problems": v["problems"][:10], "examples": len(v["served_examples"])})
                                       for k, v in (report.get("student_side") or {}).items()}}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
