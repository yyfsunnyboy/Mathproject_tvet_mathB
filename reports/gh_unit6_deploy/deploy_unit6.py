"""Formal deployment of 普高數學1 Unit 6 Gencode V3 (analytic_geometry.circle_equations revision_0001).

Run ONLY after the project owner has approved the bundle, one step at a time, in this order:

    python reports/gh_unit6_deploy/deploy_unit6.py backup     --confirm
    (owner edits revision_0001/promotion_bundle.json review: status=human_approved, approved_by, approved_revision=1)
    python reports/gh_unit6_deploy/deploy_unit6.py promote    --confirm --teacher-approved
    python reports/gh_unit6_deploy/deploy_unit6.py quarantine --confirm
    python reports/gh_unit6_deploy/deploy_unit6.py rebuild    --confirm
    python reports/gh_unit6_deploy/deploy_unit6.py publish    --confirm
    (the running Flask service picks the new wrappers up on its next restart - the owner decides when)
    python reports/gh_unit6_deploy/deploy_unit6.py verify-live

    python reports/gh_unit6_deploy/deploy_unit6.py rollback-publish --confirm

Every step writes deploy_unit6_<step>.json next to this file.  The approval itself is never written by
this script, and it never restarts or stops any service.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.analytic_geometry_circles import build_sandbox as B  # noqa: E402
from agent_domains_candidate.analytic_geometry_circles.unit6_specs import COMPONENTS, DEFERRED, OP, SKILLS  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
WORKSPACE = ROOT / "reports/domain_operation_workspaces/capability_analytic_geometry_circles_5c7b9e24/revision_0001"
STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
PROMOTED_PACKAGE = ROOT / "core" / "domain" / "promoted" / "analytic_geometry_circles"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = ROOT / "runtime" / "v3_publish_staging"
BACKUP_ROOT = ROOT / "backups" / "unit6_circle_equations"
STAMP = time.strftime("%Y%m%d_%H%M%S")
DOMAIN = B.DOMAIN_KEY
EXAMPLE_IDS = sorted(set(COMPONENTS) | set(DEFERRED))
ONLY = set(COMPONENTS)  # all 32 Unit 6 components are new
ONLY_SKILLS = sorted({SKILLS[COMPONENTS[c][0]] for c in ONLY})


def _write(step: str, payload) -> None:
    (HERE / f"deploy_unit6_{step}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1, default=str))


def _connect():
    conn = sqlite3.connect(str(DB), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _move(src: Path, dest_root: Path, moved: list) -> None:
    if src.exists():
        dest = dest_root / src.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        moved.append({"from": str(src), "to": str(dest)})


def backup() -> None:
    target = BACKUP_ROOT / STAMP
    target.mkdir(parents=True)
    src = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target / "kumon_math.db")
    src.backup(dst)
    integrity = dst.execute("pragma integrity_check").fetchone()[0]
    rows = dst.execute("select * from gencode_component_tracker where textbook_example_id in (%s)" % ",".join("?" * len(EXAMPLE_IDS)), EXAMPLE_IDS)
    columns = [d[0] for d in rows.description]
    tracker = [dict(zip(columns, r)) for r in rows.fetchall()]
    dst.close()
    src.close()
    (target / "unit6_tracker_rows.json").write_text(json.dumps(tracker, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    shutil.copy2(STORE, target / STORE.name)
    for skill in SKILLS.values():
        for path in (ROOT / "skills" / f"{skill}.py", ROOT / "agent_skills_v3" / skill):
            if path.exists():
                (target / "published").mkdir(parents=True, exist_ok=True)
                (shutil.copytree if path.is_dir() else shutil.copy2)(path, target / "published" / path.name)
    if PROMOTED_PACKAGE.is_dir():
        shutil.copytree(PROMOTED_PACKAGE, target / PROMOTED_PACKAGE.name, ignore=shutil.ignore_patterns("__pycache__"))
    _write("backup", {"backup_dir": str(target), "db_integrity": integrity, "tracker_rows": len(tracker)})


def promote() -> None:
    from core.gencode.reviewed_capability_promotion import preflight_reviewed_bundle, promote_reviewed_workspace

    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    review = bundle["review"]
    if review.get("status") != "human_approved" or not str(review.get("approved_by") or "").strip() \
            or review.get("approved_revision") != bundle["proposal_revision"]:
        raise SystemExit(f"bundle review is not human-approved for revision {bundle['proposal_revision']}: {review}")
    if "--teacher-approved" not in sys.argv:
        raise SystemExit("--teacher-approved must be given by the approving human")
    preflight = preflight_reviewed_bundle(WORKSPACE)
    if not preflight["passed"]:
        raise SystemExit(f"preflight blockers: {preflight['blockers']}")
    result = promote_reviewed_workspace(WORKSPACE, teacher_approved=True)
    _write("promote", {k: result.get(k) for k in result if k != "bundle"})


def quarantine() -> None:
    target = BACKUP_ROOT / STAMP / "quarantine"
    moved: list = []
    for cid in sorted(ONLY):
        skill = SKILLS[COMPONENTS[cid][0]]
        _move(DRYRUN / skill / "components" / f"src_{cid}", target, moved)
    _write("quarantine", {"quarantine_dir": str(target), "moved": moved})


def rebuild() -> None:
    from agent_domains_candidate.analytic_geometry_circles import verification as V  # noqa: F401
    import importlib.util
    import uuid

    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.registry.domain_operation_registry import operation_is_registered

    if not all(operation_is_registered(DOMAIN, op) for op in set(OP.values())):
        raise SystemExit("analytic_geometry.circle_equations is not promoted in this process; run the promote step first")
    conn = _connect()
    report: dict = {}
    try:
        for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
            if cid not in ONLY:
                continue
            skill = SKILLS[skill_key]
            variants = B.collect_variants(cid, op, source, sampler)
            payload = dispatch_registered_operation(DOMAIN, op, seed=0, constraints=dict(source))[1]
            spec = {"fixed_domain_key": DOMAIN, "required_capabilities": [op], "domain_operation": OP[op], "problem_type_id": OP[op],
                    "presentation_mode": payload["presentation_mode"], "answer_type": payload["answer_type"],
                    "generation_constraints": {"variants": variants}}
            try:
                result = run_gencode_phase2_raw(skill, dry_run=True, v3_textbook_example_id=cid, v3_conn=conn,
                                                v3_dryrun_base_dir=str(DRYRUN), force_regenerate=True, v3_induced_spec=spec)
            except Exception as exc:  # noqa: BLE001
                report[cid] = {"skill": skill, "exception": f"{type(exc).__name__}: {exc}"}
                continue
            row = conn.execute("select skill_id, gencode_status from gencode_component_tracker where textbook_example_id=?", (cid,)).fetchone()
            item = {"skill": skill, "operation": op, "phase_status": result.get("phase_status"), "tracker": list(row) if row else None,
                    "failures": []}
            gen = DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
            if gen.is_file():
                spec_ = importlib.util.spec_from_file_location(f"u5_{uuid.uuid4().hex}", gen)
                module = importlib.util.module_from_spec(spec_)
                spec_.loader.exec_module(module)
                for seed in range(20):
                    problems = V.verify_payload(module.generate(seed=seed, component_id=f"src_{cid}"), skill, f"src_{cid}")
                    if problems:
                        item["failures"].append(f"seed{seed}:{problems}")
            report[cid] = item
    finally:
        conn.close()
    failures = {cid: it for cid, it in report.items() if it.get("exception") or it.get("failures") or (it.get("tracker") or [None, None])[1] != "verified"}
    _write("rebuild", {"failures": failures, "deferred": {str(k): v for k, v in DEFERRED.items()}, "report": report})
    if failures:
        raise SystemExit("rebuild verification failed; do not publish")


def publish() -> None:
    import core.gencode.v3_production_publish_service as pub

    conn = _connect()
    out: dict = {}
    try:
        for skill in ONLY_SKILLS:
            partial = False
            try:
                result = pub.publish_single_v3_skill_to_production(conn=conn, skill_id=skill, project_root=str(ROOT), staging_root=str(STAGING),
                                                                   allow_partial_coverage=partial)
                out[skill] = {k: result.get(k) for k in ("status", "component_count", "smoke_status", "staging_smoke_status",
                                                         "production_smoke_status", "variation_status", "dynamic_count")}
            except Exception as exc:  # noqa: BLE001
                out[skill] = {"exception": f"{type(exc).__name__}: {exc}"}
                break
    finally:
        conn.close()
    _write("publish", out)


def verify_live() -> None:
    import importlib.util
    import uuid

    from agent_domains_candidate.analytic_geometry_circles import verification as V

    out: dict = {}
    for skill in SKILLS.values():
        facade = ROOT / "skills" / f"{skill}.py"
        if not facade.is_file():
            out[skill] = "no facade"
            continue
        spec = importlib.util.spec_from_file_location(f"facade_{uuid.uuid4().hex}", facade)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        served: dict = {}
        problems: list = []
        for seed in range(80):
            payload = module.generate(seed=seed)
            served[payload.get("textbook_example_id")] = served.get(payload.get("textbook_example_id"), 0) + 1
            if payload["answer_contract"]["answer_type"] == "drawing" or any(p.get("answer_type") == "drawing" for p in payload["answer_contract"].get("parts") or []):
                continue  # canvas answers are verified by verify_payload (mock vision), not by text grading
            ok = module.check(payload["correct_answer"], payload["correct_answer"], question_payload=payload)
            if not (ok if isinstance(ok, bool) else ok.get("correct", ok.get("is_correct", True))):
                problems.append(f"seed{seed}:canonical_rejected")
            part = V.parts_of(payload)[0]
            wrong = V.wrong_value(part)
            if payload["answer_contract"]["answer_type"] in {"multi_part", "table_fill"}:
                wrong = {**payload["correct_answer"], part["key"]: wrong}
            res = module.check(wrong, payload["correct_answer"], question_payload=payload)
            if res if isinstance(res, bool) else res.get("correct", res.get("is_correct", False)):
                problems.append(f"seed{seed}:wrong_accepted")
        out[skill] = {"served_examples": dict(sorted(served.items())), "problems": problems}
    _write("verify-live", out)


def rollback_publish() -> None:
    target = BACKUP_ROOT / STAMP / "rollback_publish"
    moved: list = []
    for skill in SKILLS.values():
        _move(ROOT / "skills" / f"{skill}.py", target, moved)
        _move(ROOT / "agent_skills_v3" / skill, target, moved)
    _write("rollback-publish", {"moved": moved, "next": "restart the Flask service if it already loaded the wrappers"})


STEPS = {"backup": backup, "promote": promote, "quarantine": quarantine, "rebuild": rebuild, "publish": publish,
         "verify-live": verify_live, "rollback-publish": rollback_publish}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in STEPS:
        raise SystemExit(f"usage: deploy_unit6.py {{{'|'.join(STEPS)}}} --confirm")
    if step != "verify-live" and "--confirm" not in sys.argv:
        raise SystemExit("formal step: add --confirm after the owner approved the bundle")
    STEPS[step]()
