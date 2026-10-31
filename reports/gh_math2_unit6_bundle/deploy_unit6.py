"""Formal deployment of 普高數學2 Unit 6 古典機率 Gencode V3 (discrete.classical_probability revision_0001;
gh_SampleSpace 6 + gh_Event 5 + gh_DefinitionOfClassicalProbability 25 + gh_PropertiesOfProbability 6 components; no fixed rows).

Run ONLY after the project owner has approved the bundle, one step at a time, in this order (same SOP as Units 4 / 5):

    python reports/gh_math2_unit6_bundle/deploy_unit6.py precheck                       # read-only
    python reports/gh_math2_unit6_bundle/deploy_unit6.py backup     --confirm
    (record_approval.py writes the owner's chat authorization into revision_0001/promotion_bundle.json)
    python reports/gh_math2_unit6_bundle/deploy_unit6.py promote    --confirm --teacher-approved
    python reports/gh_math2_unit6_bundle/deploy_unit6.py quarantine --confirm
    python reports/gh_math2_unit6_bundle/deploy_unit6.py rebuild    --confirm
    python reports/gh_math2_unit6_bundle/deploy_unit6.py publish    --confirm
    python reports/gh_math2_unit6_bundle/deploy_unit6.py verify-live
    python reports/gh_math2_unit6_bundle/deploy_unit6.py accept

    python reports/gh_math2_unit6_bundle/deploy_unit6.py rollback-publish --confirm [--restore-config]

``accept`` drives the real practice routes in a FRESH process (Flask test client) against a copy of the DB, so no student record is
written.  The approval itself is never written by this script, and it never restarts or stops any service.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.classical_probability import build_sandbox as B  # noqa: E402
from agent_domains_candidate.classical_probability.classical_probability_specs import OP, SKILLS  # noqa: E402
from build_bundle import COMPONENTS, FIXED_ROWS, REVISION, WORKSPACE  # noqa: E402

APPROVED_BUNDLE_SHA = "b920d03905aa917a85575e55441aaa61a7d65b0c9c6f45c012160bb46e981239"
DB = ROOT / "instance" / "kumon_math.db"
STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
FIXED_CONFIG = ROOT / "configs" / "fixed_textbook_practice.json"
PROMOTED_PACKAGE = ROOT / "core" / "domain" / "promoted" / "classical_probability"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = ROOT / "runtime" / "v3_publish_staging"
BACKUP_ROOT = ROOT / "backups" / "math2_unit6_classical_probability"
STAMP = time.strftime("%Y%m%d_%H%M%S")
DOMAIN = B.DOMAIN_KEY
USED_SKILLS = sorted({SKILLS[spec[0]] for spec in COMPONENTS.values()})
PROTECTED_SKILLS = ["gh_LinearPermutation", "gh_PermutationWithIdenticalItems", "gh_RepeatedPermutation", "gh_Combination", "gh_BinomialTheorem"]
PROTECTED_PACKAGES = ["permutations", "combinations"]
UNIT = ("general", "數學2", "單元6 古典機率")
EXAMPLE_IDS = sorted(COMPONENTS)
ONLY = set(COMPONENTS)


def _write(step: str, payload) -> None:
    (HERE / f"deploy_unit6_rev{REVISION}_{step}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1, default=str))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digest(paths) -> dict:
    out = {}
    for base in paths:
        files = [base] if base.is_file() else sorted(Path(d) / n for d, _ds, ns in os.walk(base) for n in ns if "__pycache__" not in d) if base.exists() else []
        for f in files:
            out[str(f.relative_to(ROOT)).replace("\\", "/")] = _sha(f)
    return out


def _protected_paths():
    return ([ROOT / "skills" / f"{s}.py" for s in PROTECTED_SKILLS] + [ROOT / "agent_skills_v3" / s for s in PROTECTED_SKILLS]
            + [ROOT / "core/domain/promoted" / p for p in PROTECTED_PACKAGES] + [FIXED_CONFIG])


def _protected_tracker(con):
    marks = ",".join("?" * len(PROTECTED_SKILLS))
    return [list(r) for r in con.execute(f"select skill_id, gencode_status, count(*) from gencode_component_tracker where skill_id in ({marks}) group by 1, 2 order by 1, 2",
                                         PROTECTED_SKILLS)]


def _connect():
    conn = sqlite3.connect(str(DB), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _ro():
    return sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)


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


def _textbook_digest(con) -> str:
    rows = con.execute("select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id", UNIT).fetchall()
    return hashlib.sha256(json.dumps([list(r) for r in rows], ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def precheck() -> None:
    """Read-only release preconditions; any False stops the release."""
    from core.textbook_stage1_gate import evaluate_stage1_gate

    out: dict = {"bundle_file_sha256": _sha(WORKSPACE / "promotion_bundle.json")}
    out["bundle_sha_matches_approved"] = out["bundle_file_sha256"] == APPROVED_BUNDLE_SHA
    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    out["bundle_review_status"] = bundle["review"]["status"]
    out["bundle_package_intact"] = all(_sha(WORKSPACE / "production_package" / n) == h for n, h in bundle["files"].items())
    out["bundle_package_matches_source"] = all(_sha(ROOT / "agent_domains_candidate/classical_probability" / n) == h for n, h in bundle["files"].items())
    rehearsal = json.loads((HERE / "rehearsal_unit6_report.json").read_text(encoding="utf-8"))
    out["rehearsal_verified"] = sum(1 for it in rehearsal["rebuild"].values() if (it.get("tracker") or [None, None])[1] == "verified")
    out["rehearsal_production_paths_written"] = rehearsal.get("production_paths_written")
    api = json.loads((HERE / "runtime_api_report.json").read_text(encoding="utf-8"))
    out["isolated_api_failures"] = api["failures"]
    con = _ro()
    try:
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
        W = "source_curriculum=? and source_volume=? and source_chapter=?"
        rows = con.execute(f"select id, skill_id, problem_text, correct_answer, detailed_solution, notes, source_description from textbook_examples where {W} order by id", UNIT).fetchall()
        gate = evaluate_stage1_gate([SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2], correct_answer=r[3], detailed_solution=r[4], notes=r[5],
                                                     source_description=r[6]) for r in rows])
        out["stage1_gate"] = {"status": gate["status"], "blocked": len(gate["blocked"]), "needs_review": len(gate["needs_review"])}
        out["unit6_rows"] = len(rows)
        out["unit6_ids_match_specs"] = sorted(r[0] for r in rows) == EXAMPLE_IDS
        out["binding_mismatches"] = {r[0]: r[1] for r in rows if r[0] in COMPONENTS and r[1] != SKILLS[COMPONENTS[r[0]][0]]}
        out["textbook_digest"] = _textbook_digest(con)
        marks = ",".join("?" * len(EXAMPLE_IDS))
        out["unit6_tracker_rows_before"] = [tuple(r) for r in con.execute(f"select textbook_example_id, skill_id, gencode_status from gencode_component_tracker where textbook_example_id in ({marks})", EXAMPLE_IDS)]
        out["protected_tracker"] = _protected_tracker(con)
        out["journal_mode"] = con.execute("pragma journal_mode").fetchone()[0]
    finally:
        con.close()
    out["hot_rollback_journal"] = (DB.parent / "kumon_math.db-journal").exists()
    probe = sqlite3.connect(str(DB), timeout=0)
    try:
        probe.execute("begin immediate")
        probe.execute("rollback")
        out["write_lock_free"] = True
    except sqlite3.OperationalError as exc:
        out["write_lock_free"] = f"busy: {exc}"
    finally:
        probe.close()
    out["unit6_already_published"] = {s: [str(p.relative_to(ROOT)) for p in (ROOT / "skills" / f"{s}.py", ROOT / "agent_skills_v3" / s, DRYRUN / s, STAGING / s) if p.exists()]
                                      for s in USED_SKILLS}
    out["promoted_package_exists"] = PROMOTED_PACKAGE.exists()
    out["domain_in_store"] = DOMAIN in STORE.read_text(encoding="utf-8")
    out["protected_manifests"] = {}
    for s in PROTECTED_SKILLS:
        m = ROOT / "agent_skills_v3" / s / "component_manifest.json"
        data = json.loads(m.read_text(encoding="utf-8")) if m.is_file() else {}
        out["protected_manifests"][s] = {"publish_status": data.get("publish_status"), "component_count": data.get("component_count")}
    out["protected_digest"] = _tree_digest(_protected_paths())
    out["unit6_fixed_entries"] = sorted(k for k in json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))["entries"] if int(k) in COMPONENTS)
    ok = (out["bundle_sha_matches_approved"] and out["bundle_review_status"] == "ready_for_human_review" and out["bundle_package_intact"]
          and out["bundle_package_matches_source"] and out["rehearsal_verified"] == len(COMPONENTS) and out["rehearsal_production_paths_written"] == []
          and out["isolated_api_failures"] == 0 and out["db_integrity"] == "ok" and out["stage1_gate"]["status"] == "READY"
          and out["unit6_rows"] == 42 and out["unit6_ids_match_specs"] and not out["binding_mismatches"] and not out["unit6_tracker_rows_before"]
          and not out["hot_rollback_journal"] and out["write_lock_free"] is True
          and not any(out["unit6_already_published"].values()) and not out["promoted_package_exists"] and not out["domain_in_store"]
          and all(v["publish_status"] for v in out["protected_manifests"].values()) and not out["unit6_fixed_entries"] and not FIXED_ROWS)
    out["passed"] = bool(ok)
    _write("precheck", out)
    if not ok:
        raise SystemExit("precheck failed; do not release")


def backup() -> None:
    target = BACKUP_ROOT / STAMP
    target.mkdir(parents=True)
    src = _ro()
    dst = sqlite3.connect(target / "kumon_math.db")
    src.backup(dst)
    integrity = dst.execute("pragma integrity_check").fetchone()[0]
    full = dst.execute("select * from gencode_component_tracker")
    full_cols = [d[0] for d in full.description]
    full_rows = [dict(zip(full_cols, r)) for r in full.fetchall()]
    marks = ",".join("?" * len(EXAMPLE_IDS))
    bindings = dict(dst.execute(f"select id, skill_id from textbook_examples where id in ({marks})", EXAMPLE_IDS).fetchall())
    dst.close()
    src.close()
    (target / "gencode_component_tracker_full.json").write_text(json.dumps(full_rows, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (target / "unit6_skill_bindings.json").write_text(json.dumps(bindings, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy2(STORE, target / STORE.name)
    shutil.copy2(FIXED_CONFIG, target / FIXED_CONFIG.name)
    shutil.copy2(WORKSPACE / "promotion_bundle.json", target / "promotion_bundle.reviewed.json")
    for s in PROTECTED_SKILLS:  # previously published units, for comparison / restore only
        for path in (ROOT / "skills" / f"{s}.py", ROOT / "agent_skills_v3" / s):
            if path.exists():
                dest = target / "protected_published" / path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                (shutil.copytree if path.is_dir() else shutil.copy2)(path, dest, **({"ignore": shutil.ignore_patterns("__pycache__")} if path.is_dir() else {}))
    files = {str(p.relative_to(target)).replace("\\", "/"): _sha(p) for p in sorted(target.rglob("*")) if p.is_file()}
    (target / "SHA256SUMS.json").write_text(json.dumps(files, ensure_ascii=False, indent=1), encoding="utf-8")
    mismatched = {cid: bindings.get(cid) for cid in COMPONENTS if bindings.get(cid) != SKILLS[COMPONENTS[cid][0]]}
    _write("backup", {"backup_dir": str(target), "db_integrity": integrity, "db_sha256": files["kumon_math.db"],
                      "store_sha256": files[STORE.name], "fixed_config_sha256": files[FIXED_CONFIG.name],
                      "tracker_rows_total": len(full_rows), "files": len(files), "binding_mismatches": mismatched})
    if mismatched or integrity != "ok":
        raise SystemExit("backup check failed; stop")


def promote() -> None:
    from core.gencode.reviewed_capability_promotion import preflight_reviewed_bundle, promote_reviewed_workspace

    record = json.loads((HERE / f"deploy_unit6_rev{REVISION}_approval_record.json").read_text(encoding="utf-8"))
    if record["bundle_file_sha256_before_approval"] != APPROVED_BUNDLE_SHA or _sha(WORKSPACE / "promotion_bundle.json") != record["bundle_file_sha256_after_approval"]:
        raise SystemExit("bundle differs from the approved / recorded file; stop")
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
        _move(DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}", target, moved)
    _write("quarantine", {"quarantine_dir": str(target), "moved": moved})


def rebuild() -> None:
    import importlib.util
    import uuid

    from agent_domains_candidate.classical_probability import verification as V
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.registry.domain_operation_registry import operation_is_registered

    if not all(operation_is_registered(DOMAIN, op) for op in set(OP.values())):
        raise SystemExit(f"{DOMAIN} is not promoted in this process; run the promote step first")
    rehearsal = json.loads((HERE / "rehearsal_unit6_report.json").read_text(encoding="utf-8"))["rebuild"]
    conn = _connect()
    report: dict = {}
    try:
        for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
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
                    "variants": len(variants), "same_variants_as_rehearsal": len(variants) == rehearsal[str(cid)]["variants"], "failures": []}
            gen = DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
            if gen.is_file():
                item["generate_sha256"] = _sha(gen)
                item["same_generate_as_rehearsal"] = item["generate_sha256"] == rehearsal[str(cid)]["verify"]["generate_sha256"]
                spec_ = importlib.util.spec_from_file_location(f"u6_{uuid.uuid4().hex}", gen)
                module = importlib.util.module_from_spec(spec_)
                spec_.loader.exec_module(module)
                surfaces = set()
                for seed in range(20):
                    p = module.generate(seed=seed, component_id=f"src_{cid}")
                    surfaces.add(json.dumps([p["question_text"], p["correct_answer"]], ensure_ascii=False, sort_keys=True, default=str))
                    problems = V.verify_payload(p, skill, f"src_{cid}")
                    if problems:
                        item["failures"].append(f"seed{seed}:{problems}")
                item["distinct_surfaces"] = len(surfaces)
                item["same_surfaces_as_rehearsal"] = len(surfaces) == rehearsal[str(cid)]["verify"]["distinct_surfaces"]
            report[cid] = item
            print(cid, skill[3:], item["tracker"], item["failures"][:2], flush=True)
    finally:
        conn.close()
    failures = {cid: it for cid, it in report.items() if it.get("exception") or it.get("failures") or (it.get("tracker") or [None, None])[1] != "verified"
                or not it.get("same_variants_as_rehearsal") or not it.get("same_surfaces_as_rehearsal")}
    _write("rebuild", {"failures": failures, "report": report})
    if failures:
        raise SystemExit("rebuild verification failed; do not publish")


def publish() -> None:
    import core.gencode.v3_production_publish_service as pub

    conn = _connect()
    out: dict = {}
    try:
        for skill in USED_SKILLS:
            try:
                result = pub.publish_single_v3_skill_to_production(conn=conn, skill_id=skill, project_root=str(ROOT), staging_root=str(STAGING),
                                                                   allow_partial_coverage=False)
                out[skill] = {k: result.get(k) for k in ("status", "component_count", "smoke_status", "staging_smoke_status",
                                                         "production_smoke_status", "variation_status", "dynamic_count", "static_count",
                                                         "partially_dynamic_count", "variation_warning")}
                out[skill]["non_dynamic_components"] = {k: {x: v.get(x) for x in ("variation_status", "error")}
                                                        for k, v in (result.get("variation_status_by_component") or {}).items() if v.get("variation_status") != "dynamic"}
            except Exception as exc:  # noqa: BLE001
                out[skill] = {"exception": f"{type(exc).__name__}: {exc}"}
                break
    finally:
        conn.close()
    _write("publish", out)
    if any("exception" in v or v.get("status") != "production_published" for v in out.values()) or len(out) != len(USED_SKILLS):
        raise SystemExit("publish did not complete for every skill; stop and follow rollback-publish")


def verify_live() -> None:
    """Manifest / tracker / store / facade consistency for the published skills (read-only)."""
    from agent_domains_candidate.classical_probability.classical_probability_specs import FAMILY
    from rehearse_unit6 import facade_smoke

    out: dict = {"facade": facade_smoke(ROOT)}
    con = _ro()
    try:
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
        marks = ",".join("?" * len(EXAMPLE_IDS))
        tracker = {r[0]: (r[1], r[2]) for r in con.execute(f"select textbook_example_id, skill_id, gencode_status from gencode_component_tracker where textbook_example_id in ({marks})", EXAMPLE_IDS)}
        out["tracker_duplicates"] = [tuple(r) for r in con.execute(f"select textbook_example_id, count(*) from gencode_component_tracker where textbook_example_id in ({marks}) group by 1 having count(*) > 1", EXAMPLE_IDS)]
        out["protected_tracker"] = _protected_tracker(con)
        out["textbook_digest"] = _textbook_digest(con)
    finally:
        con.close()
    manifest = {}
    for skill in USED_SKILLS:
        path = ROOT / "agent_skills_v3" / skill / "component_manifest.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        comps = [c for c in data.get("components") or [] if isinstance(c, dict)]
        manifest[skill] = sorted(int(c["textbook_example_id"]) for c in comps if c.get("status") == "verified")
        out.setdefault("manifest_status", {})[skill] = {"publish_status": data.get("publish_status"), "component_count": data.get("component_count"),
                                                       "facade": (ROOT / "skills" / f"{skill}.py").is_file()}
    expected = {skill: sorted(c for c in COMPONENTS if SKILLS[COMPONENTS[c][0]] == skill) for skill in USED_SKILLS}
    out["manifest_components"] = {k: len(v) for k, v in manifest.items()}
    out["manifest_total"] = sum(out["manifest_components"].values())
    out["manifest_matches_specs"] = manifest == expected
    out["families"] = len(set(FAMILY.values()))
    out["store_mentions_domain"] = DOMAIN in STORE.read_text(encoding="utf-8")
    out["promoted_package_files"] = sorted(p.name for p in PROMOTED_PACKAGE.iterdir() if p.is_file()) if PROMOTED_PACKAGE.is_dir() else []
    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    out["promoted_package_matches_bundle"] = all((PROMOTED_PACKAGE / n).is_file() and _sha(PROMOTED_PACKAGE / n) == h for n, h in bundle["files"].items())
    from core.registry.domain_operation_registry import operation_is_registered
    out["operations_registered"] = sum(operation_is_registered(DOMAIN, op) for op in set(OP.values()))
    out["tracker_not_verified"] = {cid: s for cid, s in tracker.items() if s[1] != "verified"}
    out["tracker_missing"] = [cid for cid in COMPONENTS if cid not in tracker]
    pre = json.loads((HERE / f"deploy_unit6_rev{REVISION}_precheck.json").read_text(encoding="utf-8"))
    out["protected_files_unchanged"] = _tree_digest(_protected_paths()) == pre["protected_digest"]
    out["protected_tracker_unchanged"] = out["protected_tracker"] == pre["protected_tracker"]
    out["textbook_unchanged"] = out["textbook_digest"] == pre["textbook_digest"]
    out["passed"] = bool(out["db_integrity"] == "ok" and out["manifest_matches_specs"] and out["manifest_total"] == 42 and out["families"] == 14
                         and all(v["publish_status"] and v["facade"] for v in out["manifest_status"].values())
                         and out["store_mentions_domain"] and out["promoted_package_matches_bundle"] and out["operations_registered"] == 14
                         and not out["tracker_not_verified"] and not out["tracker_missing"] and not out["tracker_duplicates"]
                         and out["protected_files_unchanged"] and out["protected_tracker_unchanged"] and out["textbook_unchanged"]
                         and all(isinstance(v, dict) and not v["problems"] for v in out["facade"].values()))
    _write("verify-live", out)


def accept() -> None:
    """Runtime acceptance through the real practice routes in a fresh process against a DB copy."""
    import collections
    import logging

    copy = BACKUP_ROOT / STAMP / "accept" / "kumon_math_accept.db"
    copy.parent.mkdir(parents=True, exist_ok=True)
    src = _ro()
    dst = sqlite3.connect(copy)
    src.backup(dst)
    student = dst.execute("select id from users where role='student' order by id limit 1").fetchone()
    dst.close()
    src.close()
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{copy.as_posix()}"

    from agent_domains_candidate.classical_probability import verification as V
    from app import app
    from core import practice_question_store as QS

    errors: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            if any(k in msg for k in ("DOMAIN_CAPABILITY_UNRESOLVED", "domain_binding_mismatch", "QUESTION DELIVERY REJECTED", "Traceback", "模組載入錯誤")):
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

    def ui_value(part, value):
        """What the practice UI sends: a select posts the option value, every input box posts a string."""
        if part.get("input_type") == "select":
            return next(str(c["value"]) for c in part["choices"] if str(c["label"]) == str(value))
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return value

    def submit(client, skill, body, answer):
        res = client.post("/check_answer", json={"skill_id": skill, "question_uid": body.get("question_uid", ""),
                                                 "problem_type_id": body.get("problem_type_id", ""),
                                                 "answer": answer, **({"answers": answer} if isinstance(answer, dict) else {})})
        data = res.get_json(silent=True) or {}
        return (data.get("correct") if res.status_code == 200 else None), data

    out: dict = {"db_copy": str(copy), "student_id": student[0] if student else None, "skills": {}}
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        for skill in USED_SKILLS:
            page = client.get(f"/practice/{skill}")
            report = {"practice_page": page.status_code, "served": collections.Counter(), "http_errors": [], "grading": [], "load_errors": 0,
                      "multi_part": 0, "stem_mismatch": [], "route_modes": collections.Counter()}
            plan = [None] * 12 + [f"src_{cid}" for cid in sorted(COMPONENTS) if SKILLS[COMPONENTS[cid][0]] == skill]
            for component in plan:
                res = client.get(f"/get_next_question?skill={skill}&level=1" + (f"&component_id={component}" if component else ""))
                body = res.get_json(silent=True) or {}
                if res.status_code != 200 or not body.get("question_uid"):
                    report["http_errors"].append(f"{component or 'next'}:{res.status_code}:{str(body)[:160]}")
                    continue
                payload = stored(body["question_uid"]) or body
                cid = payload.get("textbook_example_id")
                report["served"][cid] += 1
                report["route_modes"][str(body.get("route_mode"))] += 1
                contract = body.get("answer_contract") or {}
                multi = contract.get("answer_type") == "multi_part"
                report["multi_part"] += multi
                if multi:
                    stem = (body.get("metadata") or {}).get("stem_structure") or {}
                    labels = [p.get("group_label") for p in contract["parts"]]
                    if [i.get("group_label") for i in stem.get("items") or []] != labels or labels != [f"({i})" for i in range(1, len(labels) + 1)]:
                        report["stem_mismatch"].append(cid)
                expected = payload.get("correct_answer")
                parts = V.parts_of(payload)
                if multi:
                    right = {p["key"]: ui_value(p, expected[p["key"]]) for p in parts}
                    checks = [("wrong", {**right, p["key"]: ui_value(p, V.wrong_value(p))}, False) for p in parts] + [("right", right, True)]
                else:
                    checks = [("wrong", ui_value(parts[0], V.wrong_value(parts[0])), False), ("right", ui_value(parts[0], expected), True)]
                for kind, answer, want in checks:
                    got, data = submit(client, skill, body, answer)
                    report["load_errors"] += "模組載入錯誤" in json.dumps(data, ensure_ascii=False)
                    if got is not want:
                        report["grading"].append(f"{cid}:{kind}:{got}")
            report["served"] = dict(sorted(report["served"].items(), key=lambda kv: str(kv[0])))
            report["route_modes"] = dict(report["route_modes"])
            out["skills"][skill] = report
        for skill in USED_SKILLS:
            seq = [int((client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation").get_json(silent=True) or {}).get("textbook_example_id") or 0)
                   for _ in range(20)]
            out.setdefault("next_sequence", {})[skill] = seq
    out["runtime_errors"] = errors[:20]
    covered = {cid for r in out["skills"].values() for cid in r["served"]}
    out["components_served"] = len(covered & set(COMPONENTS))
    out["passed"] = bool(all(not r["http_errors"] and not r["grading"] and r["practice_page"] == 200 and not r["load_errors"] and not r["stem_mismatch"]
                             and set(r["route_modes"]) == {"v3"} for r in out["skills"].values())
                         and out["components_served"] == 42 and all(all(out["next_sequence"][s]) for s in USED_SKILLS) and not errors)
    _write("accept", out)


def rollback_publish() -> None:
    target = BACKUP_ROOT / STAMP / "rollback_publish"
    moved: list = []
    for skill in USED_SKILLS:
        _move(ROOT / "skills" / f"{skill}.py", target, moved)
        _move(ROOT / "agent_skills_v3" / skill, target, moved)
    restored = {}
    if "--restore-config" in sys.argv:
        latest = _latest_backup()
        shutil.copy2(latest / STORE.name, STORE)
        restored[STORE.name] = str(latest / STORE.name)
        if PROMOTED_PACKAGE.is_dir():
            _move(PROMOTED_PACKAGE, target, moved)
    _write("rollback-publish", {"moved": moved, "restored": restored, "next": "restart Flask 5001 if it already loaded the wrappers"})


STEPS = {"precheck": precheck, "backup": backup, "promote": promote, "quarantine": quarantine, "rebuild": rebuild, "publish": publish,
         "verify-live": verify_live, "accept": accept, "rollback-publish": rollback_publish}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in STEPS:
        raise SystemExit(f"usage: deploy_unit6.py {{{'|'.join(STEPS)}}} --confirm")
    if step not in {"precheck", "verify-live", "accept"} and "--confirm" not in sys.argv:
        raise SystemExit("formal step: add --confirm after the owner approved the bundle")
    STEPS[step]()
