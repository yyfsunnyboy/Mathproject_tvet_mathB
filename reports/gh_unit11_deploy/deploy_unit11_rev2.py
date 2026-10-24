"""Formal deployment of 普高數學1 Unit 11 Gencode V3 (function.cubic_graph revision_0001).

Run ONLY after the project owner has approved the bundle, one step at a time, in this order:

    python reports/gh_unit11_deploy/deploy_unit11_rev2.py backup     --confirm
    (owner edits revision_0001/promotion_bundle.json review: status=human_approved, approved_by, approved_revision=1)
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py promote    --confirm --teacher-approved
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py quarantine --confirm
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py rebuild    --confirm
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py publish    --confirm
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py verify-live
    python reports/gh_unit11_deploy/deploy_unit11_rev2.py accept

    python reports/gh_unit11_deploy/deploy_unit11_rev2.py rollback-publish --confirm

``accept`` drives the real practice routes in a FRESH process (Flask test client) against a copy of the DB, so
no student record is written; the running Flask service only sees the new skill bindings after its next restart
(bindings are read at import time) - the owner decides when.  Every step writes deploy_unit11_rev2_<step>.json next to
this file.  The approval itself is never written by this script, and it never restarts or stops any service.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.polynomial_inequality import build_sandbox as B  # noqa: E402
from agent_domains_candidate.polynomial_inequality.polynomial_inequality_specs import OP, SKILLS  # noqa: E402
from build_bundle_rev2 import COMPONENTS, DEFERRED, WORKSPACE  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
PROMOTED_PACKAGE = ROOT / "core" / "domain" / "promoted" / "polynomial_inequality"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = ROOT / "runtime" / "v3_publish_staging"
BACKUP_ROOT = ROOT / "backups" / "unit11_polynomial_inequality_rev2"
STAMP = time.strftime("%Y%m%d_%H%M%S")
DOMAIN = B.DOMAIN_KEY
EXAMPLE_IDS = sorted(set(COMPONENTS) | set(DEFERRED))
ONLY = {12650, 12662, 12664}  # revision 2 adds only these three; the 35 published components are left untouched
if "--only" in sys.argv:  # targeted re-verification, e.g. --only 12555 (quarantine / rebuild / publish of its skill)
    ONLY = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    assert ONLY <= set(COMPONENTS), ONLY
ONLY_SKILLS = sorted({SKILLS[COMPONENTS[c][0]] for c in ONLY})
# --from-skill <skill>: the components were previously published under another skill (rebind); that skill is
# quarantined from and republished as well.
FROM_SKILL = sys.argv[sys.argv.index("--from-skill") + 1] if "--from-skill" in sys.argv else None
if FROM_SKILL:
    ONLY_SKILLS = sorted(set(ONLY_SKILLS) | {FROM_SKILL})


def _write(step: str, payload) -> None:
    (HERE / f"deploy_unit11_rev2_{step}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
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


def _latest_backup() -> Path:
    dirs = sorted(p for p in BACKUP_ROOT.iterdir() if p.is_dir() and (p / "kumon_math.db").is_file())
    if not dirs:
        raise SystemExit("no backup found; run the backup step first")
    return dirs[-1]


def backup() -> None:
    target = BACKUP_ROOT / STAMP
    target.mkdir(parents=True)
    src = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target / "kumon_math.db")
    src.backup(dst)
    integrity = dst.execute("pragma integrity_check").fetchone()[0]
    marks = ",".join("?" * len(EXAMPLE_IDS))
    rows = dst.execute(f"select * from gencode_component_tracker where textbook_example_id in ({marks})", EXAMPLE_IDS)
    columns = [d[0] for d in rows.description]
    tracker = [dict(zip(columns, r)) for r in rows.fetchall()]
    bindings = dict(dst.execute(f"select id, skill_id from textbook_examples where id in ({marks})", EXAMPLE_IDS).fetchall())
    dst.close()
    src.close()
    (target / "unit9_tracker_rows.json").write_text(json.dumps(tracker, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (target / "unit9_skill_bindings.json").write_text(json.dumps(bindings, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy2(STORE, target / STORE.name)
    for skill in SKILLS.values():
        for path in (ROOT / "skills" / f"{skill}.py", ROOT / "agent_skills_v3" / skill):
            if path.exists():
                (target / "published").mkdir(parents=True, exist_ok=True)
                (shutil.copytree if path.is_dir() else shutil.copy2)(path, target / "published" / path.name)
    if PROMOTED_PACKAGE.is_dir():
        shutil.copytree(PROMOTED_PACKAGE, target / PROMOTED_PACKAGE.name, ignore=shutil.ignore_patterns("__pycache__"))
    mismatched = {cid: bindings.get(cid) for cid in COMPONENTS if bindings.get(cid) != SKILLS[COMPONENTS[cid][0]]}
    _write("backup", {"backup_dir": str(target), "db_integrity": integrity, "tracker_rows": len(tracker),
                      "binding_mismatches": mismatched})
    if mismatched:
        raise SystemExit("formal DB skill bindings differ from the component specs; stop")


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
        if FROM_SKILL:
            _move(DRYRUN / FROM_SKILL / "components" / f"src_{cid}", target, moved)
    _write("quarantine", {"quarantine_dir": str(target), "moved": moved})


def rebuild() -> None:
    import importlib.util
    import uuid

    from agent_domains_candidate.polynomial_inequality import verification as V
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.registry.domain_operation_registry import operation_is_registered

    if not all(operation_is_registered(DOMAIN, op) for op in set(OP.values())):
        raise SystemExit(f"{DOMAIN} is not promoted in this process; run the promote step first")
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
                    "variants": len(variants), "failures": []}
            gen = DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
            if gen.is_file():
                spec_ = importlib.util.spec_from_file_location(f"u9_{uuid.uuid4().hex}", gen)
                module = importlib.util.module_from_spec(spec_)
                spec_.loader.exec_module(module)
                for seed in range(20):
                    problems = V.verify_payload(module.generate(seed=seed, component_id=f"src_{cid}"), skill, f"src_{cid}")
                    if problems:
                        item["failures"].append(f"seed{seed}:{problems}")
            report[cid] = item
            print(cid, skill[3:], item["tracker"], item["failures"][:2], flush=True)
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
            try:
                result = pub.publish_single_v3_skill_to_production(conn=conn, skill_id=skill, project_root=str(ROOT), staging_root=str(STAGING),
                                                                   allow_partial_coverage=False)
                out[skill] = {k: result.get(k) for k in ("status", "component_count", "smoke_status", "staging_smoke_status",
                                                         "production_smoke_status", "variation_status", "dynamic_count", "static_count")}
            except Exception as exc:  # noqa: BLE001
                out[skill] = {"exception": f"{type(exc).__name__}: {exc}"}
                break
    finally:
        conn.close()
    _write("publish", out)


def verify_live() -> None:
    """Manifest / tracker / facade consistency for the published skills (read-only)."""
    from rehearse_unit11_rev2 import facade_smoke

    out: dict = {"facade": facade_smoke(ROOT)}
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        tracker = dict(conn.execute("select textbook_example_id, gencode_status from gencode_component_tracker "
                                    f"where textbook_example_id in ({','.join('?' * len(EXAMPLE_IDS))})", EXAMPLE_IDS).fetchall())
    finally:
        conn.close()
    manifest = {}
    for skill in SKILLS.values():
        path = ROOT / "agent_skills_v3" / skill / "component_manifest.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        comps = [c for c in data.get("components") or [] if isinstance(c, dict)]
        manifest[skill] = sorted(int(c["textbook_example_id"]) for c in comps if c.get("status") == "verified")
        out.setdefault("manifest_status", {})[skill] = {"publish_status": data.get("publish_status"),
                                                       "component_count": data.get("component_count")}
    expected = {skill: sorted(c for c in COMPONENTS if SKILLS[COMPONENTS[c][0]] == skill) for skill in SKILLS.values()}
    out["manifest_components"] = {k: len(v) for k, v in manifest.items()}
    out["manifest_matches_specs"] = manifest == expected
    out["tracker_not_verified"] = {cid: s for cid, s in tracker.items() if s != "verified"}
    out["tracker_missing"] = [cid for cid in COMPONENTS if cid not in tracker]
    _write("verify-live", out)


def accept() -> None:
    """Runtime acceptance through the real practice routes in a fresh process against a DB copy."""
    import collections
    import logging

    copy = BACKUP_ROOT / STAMP / "accept" / "kumon_math_accept.db"
    copy.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(copy)
    src.backup(dst)
    student = dst.execute("select id from users where role='student' order by id limit 1").fetchone()
    dst.close()
    src.close()
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{copy.as_posix()}"

    from agent_domains_candidate.polynomial_inequality import verification as V
    from app import app
    from core import practice_question_store as QS

    errors: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            if any(k in msg for k in ("DOMAIN_CAPABILITY_UNRESOLVED", "domain_binding_mismatch", "QUESTION DELIVERY REJECTED", "Traceback")):
                errors.append(msg[:300])

    for name in ("", "app", "core"):
        logging.getLogger(name).addHandler(Capture())
    app.logger.addHandler(Capture())
    app.config["WTF_CSRF_ENABLED"] = False
    assert app.config["SQLALCHEMY_DATABASE_URI"].endswith("kumon_math_accept.db"), app.config["SQLALCHEMY_DATABASE_URI"]

    def stored(uid: str) -> dict:
        for bucket in QS._STORE.values():
            if uid in bucket:
                return bucket[uid]
        return {}

    def as_typed(value):
        """What the practice UI sends: every input box is a string ("3, -5" for a solution set)."""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        if isinstance(value, dict):
            return {k: as_typed(v) for k, v in value.items()}
        return value

    def submit(client, skill, body, answer) -> bool | None:
        answer = as_typed(answer)
        res = client.post("/check_answer", json={"skill_id": skill, "question_uid": body.get("question_uid", ""),
                                                 "problem_type_id": body.get("problem_type_id", ""),
                                                 "answer": answer, **({"answers": answer} if isinstance(answer, dict) else {})})
        data = res.get_json(silent=True) or {}
        return data.get("correct") if res.status_code == 200 else None

    out: dict = {"db_copy": str(copy), "student_id": student[0] if student else None, "skills": {}}
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        for skill in SKILLS.values():
            page = client.get(f"/practice/{skill}")
            report = {"practice_page": page.status_code, "served": collections.Counter(), "http_errors": [], "grading": [],
                      "figures": 0, "multi_part": 0}
            plan = [None] * 12 + [f"src_{cid}" for cid in sorted(COMPONENTS) if SKILLS[COMPONENTS[cid][0]] == skill]
            for component in plan:  # first the natural next-question flow, then every component explicitly
                query = f"/get_next_question?skill={skill}&level=1" + (f"&component_id={component}" if component else "")
                res = client.get(query)
                body = res.get_json(silent=True) or {}
                if res.status_code != 200 or not body.get("question_uid"):
                    report["http_errors"].append(f"{component or 'next'}:{res.status_code}:{str(body)[:160]}")
                    continue
                payload = stored(body["question_uid"]) or body
                cid = payload.get("textbook_example_id")
                report["served"][cid] += 1
                report["figures"] += bool(body.get("visual_spec"))  # what the browser receives
                contract = payload.get("answer_contract") or {}
                if contract.get("answer_type") == "drawing" or any(p.get("answer_type") == "drawing" for p in contract.get("parts") or []):
                    report.setdefault("drawing_served_only", []).append(cid)  # AI-graded canvas: served and contract-checked, not submitted here
                    continue
                multi = contract.get("answer_type") == "multi_part"
                report["multi_part"] += multi
                expected = payload.get("correct_answer")
                parts = V.parts_of(payload)
                # Wrong answers first (each may be resubmitted); exactly one correct answer closes the question.
                checks = [("wrong", {**expected, p["key"]: V.wrong_value(p)} if multi else V.wrong_value(p), False) for p in parts]
                equivalents = {p["key"]: V.equivalent_value(p) for p in parts}
                if component and any(v is not None for v in equivalents.values()):
                    final = {k: (v if v is not None else expected[k]) for k, v in equivalents.items()} if multi else equivalents[None]
                    checks.append(("equivalent", final, True))
                else:
                    checks.append(("canonical", expected, True))
                for kind, answer, want in checks:
                    got = submit(client, skill, body, answer)
                    if got is not want:
                        report["grading"].append(f"{cid}:{kind}:{got}")
            report["served"] = dict(sorted(report["served"].items(), key=lambda kv: str(kv[0])))
            out["skills"][skill] = report
    out["runtime_errors"] = errors[:20]
    out["passed"] = all(not r["http_errors"] and not r["grading"] and r["practice_page"] == 200 for r in out["skills"].values()) \
        and not any("DOMAIN_CAPABILITY_UNRESOLVED" in e or "domain_binding_mismatch" in e for e in errors)
    _write("accept", out)


def rollback_publish() -> None:
    target = BACKUP_ROOT / STAMP / "rollback_publish"
    moved: list = []
    for skill in SKILLS.values():
        _move(ROOT / "skills" / f"{skill}.py", target, moved)
        _move(ROOT / "agent_skills_v3" / skill, target, moved)
    _write("rollback-publish", {"moved": moved, "next": "restart the Flask service if it already loaded the wrappers"})


STEPS = {"backup": backup, "promote": promote, "quarantine": quarantine, "rebuild": rebuild, "publish": publish,
         "verify-live": verify_live, "accept": accept, "rollback-publish": rollback_publish}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in STEPS:
        raise SystemExit(f"usage: deploy_unit11_rev2.py {{{'|'.join(STEPS)}}} --confirm")
    if step not in {"verify-live", "accept"} and "--confirm" not in sys.argv:
        raise SystemExit("formal step: add --confirm after the owner approved the bundle")
    STEPS[step]()
