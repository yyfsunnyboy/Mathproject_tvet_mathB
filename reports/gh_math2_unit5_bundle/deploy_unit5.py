"""Formal deployment of 普高數學2 Unit 5 組合 Gencode V3 (discrete.combinations revision_0001; gh_Combination 22 + gh_BinomialTheorem 12 components,
plus the ungraded proof self-check rows 12838 / 12845 merged into configs/fixed_textbook_practice.json; the graded row 12834 is already live).

Run ONLY after the project owner has approved the bundle, one step at a time, in this order (same SOP as Unit 4):

    python reports/gh_math2_unit5_bundle/deploy_unit5.py precheck                       # read-only
    python reports/gh_math2_unit5_bundle/deploy_unit5.py backup     --confirm
    (record_approval.py writes the owner's chat authorization into revision_0001/promotion_bundle.json)
    python reports/gh_math2_unit5_bundle/deploy_unit5.py promote    --confirm --teacher-approved
    python reports/gh_math2_unit5_bundle/deploy_unit5.py quarantine --confirm
    python reports/gh_math2_unit5_bundle/deploy_unit5.py rebuild    --confirm
    python reports/gh_math2_unit5_bundle/deploy_unit5.py publish    --confirm
    python reports/gh_math2_unit5_bundle/deploy_unit5.py fixed      --confirm      # merge 12838 / 12845 (existing 7 entries kept)
    python reports/gh_math2_unit5_bundle/deploy_unit5.py verify-live
    python reports/gh_math2_unit5_bundle/deploy_unit5.py accept

    python reports/gh_math2_unit5_bundle/deploy_unit5.py rollback-publish --confirm [--restore-config]

``accept`` drives the real practice routes in a FRESH process (Flask test client) against a copy of the DB, so no student record is
written; the running Flask service only sees the new skill bindings after its next restart (bindings are read at import time) - the
owner decides when.  Every step writes deploy_unit5_rev1_<step>.json next to this file.  The approval itself is never written by this
script, and it never restarts or stops any service.
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

from agent_domains_candidate.combinations import build_sandbox as B  # noqa: E402
from agent_domains_candidate.combinations.combinations_specs import OP, SKILLS  # noqa: E402
from build_bundle import COMPONENTS, FIXED_ROWS, REVISION, WORKSPACE  # noqa: E402

APPROVED_BUNDLE_SHA = "bbdc6bad00c4f7f046184553f14b8397c1e97989964883edc947f6201d41cd15"
DB = ROOT / "instance" / "kumon_math.db"
STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
FIXED_CONFIG = ROOT / "configs" / "fixed_textbook_practice.json"
PROOF_IDS = [12838, 12845]
GRADED_FIXED_ID = 12834
EXISTING_FIXED = ["12719", "12727", "12731", "12735", "12746", "12801", "12834"]  # Units 2-5, kept untouched
PROOF_STAGED = ROOT / "reports" / "gh_math2_unit5_fixed" / "staged_proof_entries.json"
PROMOTED_PACKAGE = ROOT / "core" / "domain" / "promoted" / "combinations"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = ROOT / "runtime" / "v3_publish_staging"
BACKUP_ROOT = ROOT / "backups" / "math2_unit5_combinations"
STAMP = time.strftime("%Y%m%d_%H%M%S")
DOMAIN = B.DOMAIN_KEY
USED_SKILLS = sorted({SKILLS[spec[0]] for spec in COMPONENTS.values()})
UNIT4_SKILLS = ["gh_LinearPermutation", "gh_PermutationWithIdenticalItems", "gh_RepeatedPermutation"]
UNIT = ("general", "數學2", "單元5 組合")
EXAMPLE_IDS = sorted(set(COMPONENTS) | set(FIXED_ROWS))
ONLY = set(COMPONENTS)
ONLY_SKILLS = USED_SKILLS


def _write(step: str, payload) -> None:
    (HERE / f"deploy_unit5_rev{REVISION}_{step}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1, default=str))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digest(paths) -> dict:
    """SHA-256 of every file under the given paths (no __pycache__), keyed by repo-relative path."""
    out = {}
    for base in paths:
        files = [base] if base.is_file() else sorted(Path(d) / n for d, _ds, ns in os.walk(base) for n in ns if "__pycache__" not in d) if base.exists() else []
        for f in files:
            out[str(f.relative_to(ROOT)).replace("\\", "/")] = _sha(f)
    return out


def _unit4_paths():
    return [ROOT / "skills" / f"{s}.py" for s in UNIT4_SKILLS] + [ROOT / "agent_skills_v3" / s for s in UNIT4_SKILLS] + [ROOT / "core/domain/promoted/permutations"]


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


def _proof_entries_from_formal_db() -> dict:
    sys.path.insert(0, str(ROOT / "reports" / "gh_math2_unit5_fixed"))
    import build_proof_entries as PE

    return PE.build_entries(DB)


def precheck() -> None:
    """Read-only release preconditions; any False stops the release."""
    from core.textbook_stage1_gate import evaluate_stage1_gate
    from core import fixed_textbook_practice as FT

    out: dict = {"bundle_file_sha256": _sha(WORKSPACE / "promotion_bundle.json")}
    out["bundle_sha_matches_approved"] = out["bundle_file_sha256"] == APPROVED_BUNDLE_SHA
    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    out["bundle_review_status"] = bundle["review"]["status"]
    out["bundle_package_intact"] = all(_sha(WORKSPACE / "production_package" / n) == h for n, h in bundle["files"].items())
    rehearsal = json.loads((HERE / "rehearsal_unit5_report.json").read_text(encoding="utf-8"))
    out["rehearsal_verified"] = sum(1 for it in rehearsal["rebuild"].values() if (it.get("tracker") or [None, None])[1] == "verified")
    con = _ro()
    try:
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
        W = "source_curriculum=? and source_volume=? and source_chapter=?"
        rows = con.execute(f"select id, skill_id, problem_text, correct_answer, detailed_solution, notes, source_description from textbook_examples where {W} order by id", UNIT).fetchall()
        gate = evaluate_stage1_gate([SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2], correct_answer=r[3], detailed_solution=r[4], notes=r[5],
                                                     source_description=r[6]) for r in rows])
        out["stage1_gate"] = {"status": gate["status"], "blocked": len(gate["blocked"]), "needs_review": len(gate["needs_review"])}
        out["unit5_rows"] = len(rows)
        out["unit5_ids_match_specs"] = sorted(r[0] for r in rows) == EXAMPLE_IDS
        out["binding_mismatches"] = {r[0]: r[1] for r in rows if r[0] in COMPONENTS and r[1] != SKILLS[COMPONENTS[r[0]][0]]}
        marks = ",".join("?" * len(EXAMPLE_IDS))
        out["unit5_tracker_rows_before"] = [tuple(r) for r in con.execute(f"select textbook_example_id, skill_id, gencode_status from gencode_component_tracker where textbook_example_id in ({marks})", EXAMPLE_IDS)]
        out["unit4_tracker"] = [tuple(r) for r in con.execute("select skill_id, gencode_status, count(*) from gencode_component_tracker where skill_id in (?,?,?) group by 1, 2", UNIT4_SKILLS)]
        out["journal_mode"] = con.execute("pragma journal_mode").fetchone()[0]
    finally:
        con.close()
    # -wal / -shm exist whenever a WAL-mode connection is open (the running Flask); a hot rollback journal or a held write lock means a writer
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
    out["unit5_already_published"] = {s: [str(p.relative_to(ROOT)) for p in (ROOT / "skills" / f"{s}.py", ROOT / "agent_skills_v3" / s) if p.exists()] for s in USED_SKILLS}
    out["promoted_package_exists"] = PROMOTED_PACKAGE.exists()
    store = json.loads(STORE.read_text(encoding="utf-8"))
    out["domain_in_store"] = DOMAIN in json.dumps(store, ensure_ascii=False)
    out["unit4_manifests"] = {}
    for s in UNIT4_SKILLS:
        m = ROOT / "agent_skills_v3" / s / "component_manifest.json"
        data = json.loads(m.read_text(encoding="utf-8")) if m.is_file() else {}
        out["unit4_manifests"][s] = {"publish_status": data.get("publish_status"), "component_count": data.get("component_count")}
    out["unit4_digest"] = _tree_digest(_unit4_paths())
    live = json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))["entries"]
    out["fixed_entries"] = sorted(live)
    out["fixed_existing_complete"] = sorted(live) == sorted(EXISTING_FIXED)
    staged = json.loads(PROOF_STAGED.read_text(encoding="utf-8"))["entries"]
    fresh = _proof_entries_from_formal_db()
    out["proof_staged_equals_formal_rebind"] = fresh == staged
    out["proof_not_yet_live"] = not set(staged) & set(live)
    con = _ro()
    try:
        out["proof_bound_to_formal_rows"] = {}
        for rid in PROOF_IDS:
            skill_id, text = con.execute("select skill_id, problem_text from textbook_examples where id=?", (rid,)).fetchone()
            e = staged[str(rid)]
            out["proof_bound_to_formal_rows"][rid] = e["skill_id"] == skill_id and e["problem_text_sha256"] == FT.stem_sha256(text) and e["mode"] == "ungraded"
    finally:
        con.close()
    ok = (out["bundle_sha_matches_approved"] and out["bundle_review_status"] == "ready_for_human_review" and out["bundle_package_intact"]
          and out["rehearsal_verified"] == len(COMPONENTS) and out["db_integrity"] == "ok" and out["stage1_gate"]["status"] == "READY"
          and out["unit5_rows"] == 37 and out["unit5_ids_match_specs"] and not out["binding_mismatches"] and not out["hot_rollback_journal"] and out["write_lock_free"] is True
          and not any(out["unit5_already_published"].values()) and not out["promoted_package_exists"] and not out["domain_in_store"]
          and all(v["publish_status"] for v in out["unit4_manifests"].values()) and out["fixed_existing_complete"]
          and out["proof_staged_equals_formal_rebind"] and out["proof_not_yet_live"] and all(out["proof_bound_to_formal_rows"].values()))
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
    marks = ",".join("?" * len(EXAMPLE_IDS))
    rows = dst.execute(f"select * from gencode_component_tracker where textbook_example_id in ({marks})", EXAMPLE_IDS)
    columns = [d[0] for d in rows.description]
    tracker = [dict(zip(columns, r)) for r in rows.fetchall()]
    full = dst.execute("select * from gencode_component_tracker")
    full_cols = [d[0] for d in full.description]
    full_rows = [dict(zip(full_cols, r)) for r in full.fetchall()]
    bindings = dict(dst.execute(f"select id, skill_id from textbook_examples where id in ({marks})", EXAMPLE_IDS).fetchall())
    dst.close()
    src.close()
    (target / "unit5_tracker_rows.json").write_text(json.dumps(tracker, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (target / "gencode_component_tracker_full.json").write_text(json.dumps(full_rows, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (target / "unit5_skill_bindings.json").write_text(json.dumps(bindings, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy2(STORE, target / STORE.name)
    shutil.copy2(FIXED_CONFIG, target / FIXED_CONFIG.name)
    shutil.copy2(WORKSPACE / "promotion_bundle.json", target / "promotion_bundle.reviewed.json")
    for skill in USED_SKILLS:
        for path in (ROOT / "skills" / f"{skill}.py", ROOT / "agent_skills_v3" / skill, DRYRUN / skill, STAGING / skill):
            if path.exists():
                dest = target / "published" / path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                (shutil.copytree if path.is_dir() else shutil.copy2)(path, dest)
    if PROMOTED_PACKAGE.is_dir():
        shutil.copytree(PROMOTED_PACKAGE, target / PROMOTED_PACKAGE.name, ignore=shutil.ignore_patterns("__pycache__"))
    for s in UNIT4_SKILLS:  # Unit 4 published state, for comparison / restore only
        for path in (ROOT / "skills" / f"{s}.py", ROOT / "agent_skills_v3" / s):
            if path.exists():
                dest = target / "unit4_published" / path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                (shutil.copytree if path.is_dir() else shutil.copy2)(path, dest, **({"ignore": shutil.ignore_patterns("__pycache__")} if path.is_dir() else {}))
    files = {str(p.relative_to(target)).replace("\\", "/"): _sha(p) for p in sorted(target.rglob("*")) if p.is_file()}
    (target / "SHA256SUMS.json").write_text(json.dumps(files, ensure_ascii=False, indent=1), encoding="utf-8")
    mismatched = {cid: bindings.get(cid) for cid in COMPONENTS if bindings.get(cid) != SKILLS[COMPONENTS[cid][0]]}
    _write("backup", {"backup_dir": str(target), "db_integrity": integrity, "db_sha256": files["kumon_math.db"],
                      "store_sha256": files[STORE.name], "fixed_config_sha256": files[FIXED_CONFIG.name],
                      "tracker_rows_unit5": len(tracker), "tracker_rows_total": len(full_rows), "files": len(files), "binding_mismatches": mismatched})
    if mismatched or integrity != "ok":
        raise SystemExit("backup check failed; stop")


def promote() -> None:
    from core.gencode.reviewed_capability_promotion import preflight_reviewed_bundle, promote_reviewed_workspace

    record = json.loads((HERE / f"deploy_unit5_rev{REVISION}_approval_record.json").read_text(encoding="utf-8"))
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
        skill = SKILLS[COMPONENTS[cid][0]]
        _move(DRYRUN / skill / "components" / f"src_{cid}", target, moved)
    _write("quarantine", {"quarantine_dir": str(target), "moved": moved})


def rebuild() -> None:
    import importlib.util
    import uuid

    from agent_domains_candidate.combinations import verification as V
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.registry.domain_operation_registry import operation_is_registered

    if not all(operation_is_registered(DOMAIN, op) for op in set(OP.values())):
        raise SystemExit(f"{DOMAIN} is not promoted in this process; run the promote step first")
    rehearsal = json.loads((HERE / "rehearsal_unit5_report.json").read_text(encoding="utf-8"))["rebuild"]
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
                    "variants": len(variants), "same_variants_as_rehearsal": len(variants) == rehearsal[str(cid)]["variants"], "failures": []}
            gen = DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
            if gen.is_file():
                spec_ = importlib.util.spec_from_file_location(f"u5_{uuid.uuid4().hex}", gen)
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
    _write("rebuild", {"failures": failures, "deferred": {str(k): v for k, v in FIXED_ROWS.items()}, "report": report})
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
    if any("exception" in v or v.get("status") != "production_published" for v in out.values()) or len(out) != len(ONLY_SKILLS):
        raise SystemExit("publish did not complete for every skill; stop and follow rollback-publish")


def fixed() -> None:
    """Merge the two staged proof entries into the live fixed config: the 7 existing entries are kept as data, no key is overwritten."""
    live_bytes = FIXED_CONFIG.read_bytes()
    data = json.loads(live_bytes.decode("utf-8"))
    before = dict(data["entries"])
    assert sorted(before) == sorted(EXISTING_FIXED), sorted(before)
    staged = json.loads(PROOF_STAGED.read_text(encoding="utf-8"))["entries"]
    assert sorted(int(k) for k in staged) == PROOF_IDS, staged.keys()
    assert _proof_entries_from_formal_db() == staged, "staged proof entries differ from a re-bind on the formal DB"
    assert not set(staged) & set(before), "a proof entry already exists in the live config"
    data["entries"].update(staged)
    FIXED_CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    after = json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))["entries"]
    unchanged = all(after[k] == v for k, v in before.items())
    _write("fixed", {"before": sorted(before), "after": sorted(after), "added": sorted(set(after) - set(before)),
                     "existing_entries_unchanged": unchanged, "sha256_before": hashlib.sha256(live_bytes).hexdigest(), "sha256_after": _sha(FIXED_CONFIG)})
    if not unchanged or sorted(after) != sorted(EXISTING_FIXED + [str(i) for i in PROOF_IDS]):
        raise SystemExit("fixed config merge check failed; restore it from the backup")


def verify_live() -> None:
    """Manifest / tracker / store / facade / fixed-config consistency for the published skills (read-only)."""
    from core import fixed_textbook_practice as FT
    from rehearse_unit5 import facade_smoke

    out: dict = {"facade": facade_smoke(ROOT)}
    con = _ro()
    try:
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
        tracker = {r[0]: (r[1], r[2]) for r in con.execute("select textbook_example_id, skill_id, gencode_status from gencode_component_tracker "
                                                          f"where textbook_example_id in ({','.join('?' * len(EXAMPLE_IDS))})", EXAMPLE_IDS)}
        out["tracker_duplicates"] = [tuple(r) for r in con.execute("select textbook_example_id, count(*) from gencode_component_tracker "
                                                                    f"where textbook_example_id in ({','.join('?' * len(EXAMPLE_IDS))}) group by 1 having count(*) > 1", EXAMPLE_IDS)]
        out["unit4_tracker"] = [tuple(r) for r in con.execute("select skill_id, gencode_status, count(*) from gencode_component_tracker where skill_id in (?,?,?) group by 1, 2", UNIT4_SKILLS)]
        rows = {rid: (skill, text) for rid, skill, text in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12812 and 12848")}
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
    out["manifest_matches_specs"] = manifest == expected
    out["fixed_rows_not_in_manifest"] = not any(i in sum(manifest.values(), []) for i in FIXED_ROWS)
    store = json.loads(STORE.read_text(encoding="utf-8"))
    out["store_mentions_domain"] = DOMAIN in json.dumps(store, ensure_ascii=False)
    out["promoted_package_files"] = sorted(p.name for p in PROMOTED_PACKAGE.iterdir() if p.is_file()) if PROMOTED_PACKAGE.is_dir() else []
    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    out["promoted_package_matches_bundle"] = all((PROMOTED_PACKAGE / n).is_file() and _sha(PROMOTED_PACKAGE / n) == h for n, h in bundle["files"].items())
    live_fixed = json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))["entries"]
    out["fixed_entries"] = sorted(live_fixed)
    out["fixed_bound"] = {}
    for rid in [GRADED_FIXED_ID] + PROOF_IDS:
        skill, text = rows[rid]
        entry = FT.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text))
        out["fixed_bound"][rid] = entry["mode"] if entry else None
    out["unit5_fixed_keys"] = sorted(k for k in live_fixed if int(k) in rows)
    out["tracker_not_verified"] = {cid: s for cid, s in tracker.items() if s[1] != "verified" and cid in COMPONENTS}
    out["tracker_missing"] = [cid for cid in COMPONENTS if cid not in tracker]
    out["tracker_for_fixed_rows"] = {cid: tracker.get(cid) for cid in FIXED_ROWS if cid in tracker}
    pre = json.loads((HERE / f"deploy_unit5_rev{REVISION}_precheck.json").read_text(encoding="utf-8"))
    out["unit4_files_unchanged"] = _tree_digest(_unit4_paths()) == pre["unit4_digest"]
    out["unit4_tracker_unchanged"] = [list(t) for t in out["unit4_tracker"]] == [list(t) for t in pre["unit4_tracker"]]
    out["passed"] = bool(out["db_integrity"] == "ok" and out["manifest_matches_specs"] and out["fixed_rows_not_in_manifest"]
                         and all(v["publish_status"] and v["facade"] for v in out["manifest_status"].values())
                         and out["store_mentions_domain"] and out["promoted_package_matches_bundle"]
                         and out["fixed_bound"] == {GRADED_FIXED_ID: "graded", 12838: "ungraded", 12845: "ungraded"}
                         and out["fixed_entries"] == sorted(EXISTING_FIXED + [str(i) for i in PROOF_IDS])
                         and not out["tracker_not_verified"] and not out["tracker_missing"] and not out["tracker_duplicates"]
                         and out["unit4_files_unchanged"] and out["unit4_tracker_unchanged"]
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

    from agent_domains_candidate.combinations import verification as V
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
        """What the practice UI sends: every input box is a string ("1, 3" for a solution set)."""
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

    def counts() -> dict:
        con = sqlite3.connect(copy)
        try:
            return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                    for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
        finally:
            con.close()

    out: dict = {"db_copy": str(copy), "student_id": student[0] if student else None, "skills": {}}
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        for skill in USED_SKILLS:
            page = client.get(f"/practice/{skill}")
            report = {"practice_page": page.status_code, "served": collections.Counter(), "http_errors": [], "grading": [],
                      "figures": 0, "figure_cues": 0, "multi_part": 0}
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
                if cid in COMPONENTS:
                    report["figures"] += bool(body.get("visual_spec") or body.get("image_assets"))
                    report["figure_cues"] += any(w in body.get("question_text", "") for w in ("如圖", "右圖", "下圖"))
                if body.get("fixed_textbook_practice"):
                    continue  # fixed rows met in the natural flow are checked separately below
                contract = payload.get("answer_contract") or {}
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
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        skill = "gh_Combination"
        served = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation&textbook_example_id={GRADED_FIXED_ID}").get_json(silent=True) or {}
        assets = served.get("image_assets") or []
        wrong = client.post("/check_answer", json={"skill_id": skill, "question_uid": served.get("question_uid", ""),
                                                   "answer": {"part_1": "④", "part_2": "120"}}).get_json(silent=True) or {}
        served2 = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation&textbook_example_id={GRADED_FIXED_ID}").get_json(silent=True) or {}
        right = client.post("/check_answer", json={"skill_id": skill, "question_uid": served2.get("question_uid", ""),
                                                   "answer": {"part_1": "③", "part_2": "116"}}).get_json(silent=True) or {}
        out["fixed_12834"] = {"served": int(served.get("textbook_example_id") or 0) == GRADED_FIXED_ID, "mode": served.get("fixed_textbook_practice"),
                              "graded_flag": served.get("graded") is not False, "image": len(assets) == 1 and (ROOT / assets[0]["path"]).is_file(),
                              "answer_not_sent": not served.get("correct_answer") and not served.get("answer"),
                              "wrong": wrong.get("correct"), "right": right.get("correct")}
        out["proofs"] = {}
        for rid in PROOF_IDS:
            q = client.get(f"/get_next_question?skill=gh_BinomialTheorem&level=1&mode=type_rotation&textbook_example_id={rid}").get_json(silent=True) or {}
            before = counts()
            verdicts = []
            for answer in ("", "證明：略", "代入 x=y=1"):
                body = client.post("/check_answer", json={"skill_id": "gh_BinomialTheorem", "question_uid": q.get("question_uid", ""),
                                                          "answer": answer}).get_json(silent=True) or {}
                verdicts.append((body.get("correct"), body.get("graded"), len(body.get("reference_solution") or [])))
            out["proofs"][rid] = {"served": int(q.get("textbook_example_id") or 0) == rid, "mode": q.get("fixed_textbook_practice"),
                                  "check_mode": q.get("check_mode"), "scaffold": len(q.get("practice_scaffold") or []), "no_image": not q.get("image_assets"),
                                  "verdicts": verdicts, "records_unchanged": counts() == before}
        for skill in USED_SKILLS:
            seq = [int((client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation").get_json(silent=True) or {}).get("textbook_example_id") or 0)
                   for _ in range(40)]
            out.setdefault("next_sequence", {})[skill] = seq
    out["runtime_errors"] = errors[:20]
    f = out["fixed_12834"]
    out["passed"] = bool(all(not r["http_errors"] and not r["grading"] and r["practice_page"] == 200 and not r["figures"] and not r["figure_cues"]
                             for r in out["skills"].values())
                         and f["served"] and f["mode"] == "graded" and f["graded_flag"] and f["image"] and f["answer_not_sent"]
                         and f["wrong"] is False and f["right"] is True
                         and all(p["served"] and p["mode"] == "ungraded" and p["check_mode"] == "ungraded_self_study" and p["scaffold"] == 3
                                 and p["no_image"] and p["records_unchanged"] and all(v[0] is None and v[1] is False and v[2] == 3 for v in p["verdicts"])
                                 for p in out["proofs"].values())
                         and not any("DOMAIN_CAPABILITY_UNRESOLVED" in e or "domain_binding_mismatch" in e for e in errors))
    _write("accept", out)


def rollback_publish() -> None:
    target = BACKUP_ROOT / STAMP / "rollback_publish"
    moved: list = []
    for skill in USED_SKILLS:
        _move(ROOT / "skills" / f"{skill}.py", target, moved)
        _move(ROOT / "agent_skills_v3" / skill, target, moved)
    restored = {}
    if "--restore-config" in sys.argv:  # also put back the promoted-capability store and the fixed config from the latest backup
        latest = _latest_backup()
        for path in (STORE, FIXED_CONFIG):
            shutil.copy2(latest / path.name, path)
            restored[path.name] = str(latest / path.name)
        if PROMOTED_PACKAGE.is_dir():
            _move(PROMOTED_PACKAGE, target, moved)
    _write("rollback-publish", {"moved": moved, "restored": restored, "next": "restart the Flask service if it already loaded the wrappers"})


STEPS = {"precheck": precheck, "backup": backup, "promote": promote, "quarantine": quarantine, "rebuild": rebuild, "publish": publish,
         "fixed": fixed, "verify-live": verify_live, "accept": accept, "rollback-publish": rollback_publish}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in STEPS:
        raise SystemExit(f"usage: deploy_unit5.py {{{'|'.join(STEPS)}}} --confirm")
    if step not in {"precheck", "verify-live", "accept"} and "--confirm" not in sys.argv:
        raise SystemExit("formal step: add --confirm after the owner approved the bundle")
    STEPS[step]()
