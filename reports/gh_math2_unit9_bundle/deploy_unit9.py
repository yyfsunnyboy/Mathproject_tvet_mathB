"""Formal deployment of 普高數學2 Unit 9 二維數據分析 Gencode V3 (statistics.bivariate_descriptive revision_0001;
gh_CorrelationCoefficient / gh_LeastSquaresMethodAndRegressionLine, components 21 verified; deferred originals 12947/12948/12954/12960/12963).

Same SOP as Unit 7 (deploy_unit7.py), with the publish moved into a maintenance window. One step at a time, in this order:

    python reports/gh_math2_unit9_bundle/deploy_unit9.py precheck                         # read-only
    (teacher fills revision_0001_teacher_review.json; owner runs record_approval_unit9.py)
    python reports/gh_math2_unit9_bundle/deploy_unit9.py backup       --confirm
    python reports/gh_math2_unit9_bundle/deploy_unit9.py promote      --confirm --teacher-approved
    python reports/gh_math2_unit9_bundle/deploy_unit9.py quarantine   --confirm
    python reports/gh_math2_unit9_bundle/deploy_unit9.py rebuild      --confirm
    python reports/gh_math2_unit9_bundle/deploy_unit9.py verify-build                       # read-only
    --- maintenance window: stop Flask 5000 and 5001 completely ---
    python reports/gh_math2_unit9_bundle/deploy_unit9.py publish      --confirm --maintenance-window
    python reports/gh_math2_unit9_bundle/deploy_unit9.py verify-consistency                 # read-only
    --- owner starts 5000 (original admin window, run_production.bat), then 5001 ---
    python reports/gh_math2_unit9_bundle/deploy_unit9.py verify-consistency                 # unchanged since publish
    python reports/gh_math2_unit9_bundle/deploy_unit9.py accept                             # DB copy, test client

    python reports/gh_math2_unit9_bundle/deploy_unit9.py rollback-publish --confirm --maintenance-window [--restore-config] [--restore-tracker]

Promote, quarantine, rebuild and verify-build do not change what Flask serves (wrappers are not written; promoted domains are
registered at process start). Only ``publish`` writes ``skills/`` / ``agent_skills_v3/``, and it refuses while 5000 / 5001 are
listening or a Flask / waitress Python process is alive. Publish is all-or-nothing: on any failure every Unit 9 wrapper written in
the run is moved out again. Rollback restores Unit 9 files and the Unit 9 tracker rows only; the DB file is never restored.
Components rejected by the teacher (approval record ``excluded_components``) are not rebuilt and are published as Partial Publish.
``--isolated-rehearsal`` is only accepted in a project copy without ``.git``.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ["BUNDLE_REVISION"] = "1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.bivariate_statistics import build_sandbox as B  # noqa: E402
from agent_domains_candidate.bivariate_statistics.bivariate_statistics_specs import COMPONENTS, DEFERRED_COMPONENTS, FIXED_ROWS, OP, SKILLS  # noqa: E402
from build_bundle import REVISION, WORKSPACE  # noqa: E402

APPROVED_BUNDLE_SHA = "8253427bb49d63f1d117a5d458476f779cbc7caa250ff98f5e82cd88748ce555"
APPROVED_BUNDLE_DIGEST = "35f1d19d8cb29197bf094a2badd703a381992fda6151b9b29bf83da91a04ad19"
DB = ROOT / "instance" / "kumon_math.db"
STORE = ROOT / "configs" / "gencode_promoted_capabilities.json"
FIXED_CONFIG = ROOT / "configs" / "fixed_textbook_practice.json"
PROMOTED_PACKAGE = ROOT / "core" / "domain" / "promoted" / "bivariate_statistics"
DRYRUN = ROOT / "reports" / "gencode_v3_dryrun"
STAGING = ROOT / "runtime" / "v3_publish_staging"
SANDBOX_REFERENCE = ROOT / "tmp" / "gh_math2_unit9_sandbox_dryrun"
BACKUP_ROOT = ROOT / "backups" / "math2_unit9_bivariate_statistics"
STATE = HERE / f"deploy_unit9_rev{REVISION}_state.json"
APPROVAL_RECORD = HERE / f"deploy_unit9_rev{REVISION}_approval_record.json"
REHEARSAL_REPORT = HERE / "rehearsal_deploy_unit9_report.json"
STAMP = time.strftime("%Y%m%d_%H%M%S")
DOMAIN = B.DOMAIN_KEY
USED_SKILLS = sorted({SKILLS[spec[0]] for spec in COMPONENTS.values()})
UNIT = ("general", "數學2", "單元9 二維數據分析")
EXAMPLE_IDS = sorted(COMPONENTS)
CHART_IDS = ()
SERVICE_PORTS = (5001,)  # Unit 9 publish window: stop 5001 only; 5000 may keep running
N_COMPONENTS = 21
N_TEXTBOOK = 26
N_OPERATIONS = 11  # published bundle operations (predict-only op retained in domain but excluded from Publish)
DEFERRED_IDS = frozenset(DEFERRED_COMPONENTS)
OTHER_SKILLS_SMOKE = ("gh_Mean", "gh_MathematicalExpectation")


def _rehearsal() -> bool:
    if "--isolated-rehearsal" not in sys.argv:
        return False
    if (ROOT / ".git").exists():
        raise SystemExit("--isolated-rehearsal is not allowed in the formal project")
    return True


def _write(step: str, payload) -> None:
    (HERE / f"deploy_unit9_rev{REVISION}_{step}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1, default=str))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _files(base: Path) -> list[Path]:
    if base.is_file():
        return [base]
    if not base.exists():
        return []
    return sorted(Path(d) / n for d, _ds, ns in os.walk(base) for n in ns if "__pycache__" not in d and not n.endswith(".pyc"))


def _tree_digest(paths) -> dict:
    return {str(f.relative_to(ROOT)).replace("\\", "/"): _sha(f) for base in paths for f in _files(base)}


def _protected_paths() -> list[Path]:
    """Every published skill / promoted package / fixed config that this release must not touch."""
    skills = [p for p in sorted((ROOT / "skills").glob("*.py")) if p.stem not in USED_SKILLS]
    v3 = [p for p in sorted((ROOT / "agent_skills_v3").iterdir()) if p.is_dir() and p.name not in USED_SKILLS and p.name != "__pycache__"]
    promoted = [p for p in sorted((ROOT / "core/domain/promoted").iterdir()) if p.is_dir() and p.name not in (PROMOTED_PACKAGE.name, "__pycache__")]
    return skills + v3 + promoted + [FIXED_CONFIG]


def _release_paths() -> list[Path]:
    return ([ROOT / "skills" / f"{s}.py" for s in USED_SKILLS] + [ROOT / "agent_skills_v3" / s for s in USED_SKILLS]
            + [PROMOTED_PACKAGE, STORE])


def _state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}


def _save_state(**kw) -> None:
    STATE.write_text(json.dumps({**_state(), **kw}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _record() -> dict:
    if not APPROVAL_RECORD.is_file():
        raise SystemExit("approval record missing; the owner must run record_approval_unit9.py first")
    record = json.loads(APPROVAL_RECORD.read_text(encoding="utf-8"))
    if record.get("rehearsal_only") and not _rehearsal():
        raise SystemExit("approval record is rehearsal-only; not valid for the formal release")
    if record["bundle_file_sha256_before_approval"] != APPROVED_BUNDLE_SHA or record["bundle_canonical_sha256_before"] != APPROVED_BUNDLE_DIGEST:
        raise SystemExit("approval record is for another bundle")
    if _sha(WORKSPACE / "promotion_bundle.json") != record["bundle_file_sha256_after_approval"]:
        raise SystemExit("bundle differs from the approved / recorded file; stop")
    return record


def _excluded() -> set[int]:
    return set(_record().get("excluded_components") or []) if APPROVAL_RECORD.is_file() else set()


def _expected() -> dict[str, list[int]]:
    excluded = _excluded()
    return {s: sorted(c for c in COMPONENTS if SKILLS[COMPONENTS[c][0]] == s and c not in excluded) for s in USED_SKILLS}


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


def _backup_dir() -> Path:
    path = Path(_state().get("backup_dir") or "")
    if not (path / "SHA256SUMS.json").is_file():
        raise SystemExit("no verified backup recorded for this release; run the backup step first")
    sums = json.loads((path / "SHA256SUMS.json").read_text(encoding="utf-8"))
    for name in ("unit9_tracker_rows.json", STORE.name):
        if _sha(path / name) != sums[name]:
            raise SystemExit(f"backup file {name} does not match SHA256SUMS; stop")
    return path


def _unit_rows(con) -> list[dict]:
    cur = con.execute(f"select * from gencode_component_tracker where textbook_example_id in ({','.join('?' * len(EXAMPLE_IDS))}) order by id", EXAMPLE_IDS)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _textbook_digest(con) -> str:
    rows = con.execute("select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id", UNIT).fetchall()
    return hashlib.sha256(json.dumps([list(r) for r in rows], ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def _release_snapshot() -> dict:
    con = _ro()
    try:
        tracker = [[r["textbook_example_id"], r["skill_id"], r["component_id"], r["gencode_status"]] for r in _unit_rows(con)]
    finally:
        con.close()
    files = _tree_digest(_release_paths())
    return {"files": files, "tracker": tracker,
            "digest": hashlib.sha256(json.dumps([files, tracker], sort_keys=True, default=str).encode()).hexdigest()}


def _staging_paths(skill: str) -> list[Path]:
    """Publish staging keeps per-skill leftovers that a later publish copies into production; they must be absent before publish."""
    return [STAGING / skill, STAGING / "agent_skills_v3" / skill, STAGING / "skills" / f"{skill}.py", STAGING / "skills" / f"{skill}.py.bak"]


def _unit9_published_paths() -> dict:
    return {s: [str(p.relative_to(ROOT)) for p in (ROOT / "skills" / f"{s}.py", ROOT / "agent_skills_v3" / s) if p.exists()] for s in USED_SKILLS}


def _service_guard() -> dict:
    """Publish / rollback may only run while no Flask / waitress serves this project."""
    script = ("$p = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(%s) } | "
              "Select-Object LocalPort, OwningProcess; "
              "$q = Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='pythonw.exe' or Name='waitress-serve.exe' or Name='flask.exe'\" | "
              "Select-Object ProcessId, CommandLine; @{ports=@($p); procs=@($q)} | ConvertTo-Json -Depth 4 -Compress") % ",".join(map(str, SERVICE_PORTS))
    raw = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60).stdout
    data = json.loads(raw or "{}")
    ports = [p for p in data.get("ports") or [] if p]
    me = {os.getpid(), os.getppid()}
    procs = [p for p in data.get("procs") or [] if p and p.get("ProcessId") not in me]
    allowed = {int(x) for x in str(sys.argv[sys.argv.index("--allow-pids") + 1]).split(",")} if "--allow-pids" in sys.argv else set()
    servers = [p for p in procs if any(k in str(p.get("CommandLine") or "") for k in ("flask", "waitress", "run_production", "app:app"))]
    unreadable = [p for p in procs if not p.get("CommandLine") and p["ProcessId"] not in allowed]
    return {"listening": ports, "server_processes": servers, "unreadable_python_processes": unreadable,
            "clear": not ports and not servers and not unreadable}


def _require_maintenance(step: str) -> dict:
    if "--maintenance-window" not in sys.argv:
        raise SystemExit(f"{step}: add --maintenance-window after Flask 5001 was stopped (5000 may keep running)")
    guard = _service_guard()
    if _rehearsal():
        guard["bypassed_for_isolated_rehearsal"] = True
        return guard
    if not guard["clear"]:
        raise SystemExit(f"{step} refused: Flask 5001 still running or unknown Python processes: {json.dumps(guard, ensure_ascii=False)[:800]}")
    return guard


def precheck() -> None:
    """Read-only release preconditions; any False stops the release."""
    from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle
    from core.textbook_stage1_gate import evaluate_stage1_gate

    out: dict = {"revision": REVISION, "root": str(ROOT), "bundle_file_sha256": _sha(WORKSPACE / "promotion_bundle.json")}
    bundle = load_reviewed_bundle(WORKSPACE)
    out["bundle_sha_matches_reviewed"] = out["bundle_file_sha256"] == APPROVED_BUNDLE_SHA
    out["bundle_digest_matches_reviewed"] = bundle_sha256(bundle) == APPROVED_BUNDLE_DIGEST
    out["bundle_review_status"] = bundle["review"]["status"]
    out["bundle_package_intact"] = all(_sha(WORKSPACE / "production_package" / n) == h for n, h in bundle["files"].items())
    out["bundle_package_matches_source"] = all(_sha(ROOT / "agent_domains_candidate/bivariate_statistics" / n) == h for n, h in bundle["files"].items())
    out["bundle_coverage_rows"] = bundle.get("coverage_rows")
    out["sandbox_reference_components"] = sum(1 for c in COMPONENTS
                                              if (SANDBOX_REFERENCE / SKILLS[COMPONENTS[c][0]] / "components" / f"src_{c}" / "generate.py").is_file())
    if (ROOT / ".git").exists():
        rehearsal = json.loads(REHEARSAL_REPORT.read_text(encoding="utf-8")) if REHEARSAL_REPORT.is_file() else {}
        out["isolated_rehearsal_passed"] = rehearsal.get("passed") is True and rehearsal.get("approved_bundle_digest") == APPROVED_BUNDLE_DIGEST
    else:
        out["isolated_rehearsal_passed"] = "n/a (this is the isolated copy)"
    con = _ro()
    try:
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
        W = "source_curriculum=? and source_volume=? and source_chapter=?"
        rows = con.execute(f"select id, skill_id, problem_text, correct_answer, detailed_solution, notes, source_description from textbook_examples where {W} order by id", UNIT).fetchall()
        gate = evaluate_stage1_gate([SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2], correct_answer=r[3], detailed_solution=r[4], notes=r[5],
                                                     source_description=r[6]) for r in rows])
        out["stage1_gate"] = {"status": gate["status"], "blocked": len(gate["blocked"]), "needs_review": len(gate["needs_review"])}
        out["unit9_rows"] = len(rows)
        out["unit9_ids_match_specs"] = sorted(r[0] for r in rows) == sorted(set(EXAMPLE_IDS) | set(DEFERRED_IDS))
        out["binding_mismatches"] = {r[0]: r[1] for r in rows if r[0] in COMPONENTS and r[1] != SKILLS[COMPONENTS[r[0]][0]]}
        out["textbook_digest"] = _textbook_digest(con)
        out["unit9_tracker_rows_before"] = len(_unit_rows(con))
        marks = ",".join("?" * len(USED_SKILLS))
        out["skill_tracker_rows_before"] = con.execute(f"select count(*) from gencode_component_tracker where skill_id in ({marks})", USED_SKILLS).fetchone()[0]
        out["active_orchestrator_jobs"] = [tuple(r) for r in con.execute("select job_id, skill_id, stage, status from gencode_v3_orchestrator_jobs "
                                                                         "where status not in ('ready', 'failed', 'needs_capability')")]
        out["journal_mode"] = con.execute("pragma journal_mode").fetchone()[0]
        fixed_entries = json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))["entries"]
        out["unit9_v3_fixed_entries"] = sorted(k for k in fixed_entries if int(k) in COMPONENTS)
        out["unit9_deferred_fixed_entries"] = sorted(int(k) for k in fixed_entries if int(k) in DEFERRED_IDS)
        from core.fixed_textbook_practice import stem_sha256 as _stem_sha
        sha_ok = {}
        for rid in sorted(DEFERRED_IDS):
            entry = fixed_entries.get(str(rid)) or {}
            stem = next(r[2] for r in rows if r[0] == rid)
            sha_ok[rid] = bool(entry) and entry.get("mode") == "ungraded" and entry.get("problem_text_sha256") == _stem_sha(stem)
        out["unit9_deferred_fixed_sha_ok"] = sha_ok
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
    out["unit9_already_published"] = _unit9_published_paths()
    out["unit9_leftover_build_dirs"] = [str(p.relative_to(ROOT)) for s in USED_SKILLS for p in [DRYRUN / s, *_staging_paths(s)] if p.exists()]
    out["promoted_package_exists"] = PROMOTED_PACKAGE.exists()
    out["domain_in_store"] = DOMAIN in STORE.read_text(encoding="utf-8")
    out["protected_digest"] = _tree_digest(_protected_paths())
    out["protected_file_count"] = len(out["protected_digest"])
    ok = (out["bundle_sha_matches_reviewed"] and out["bundle_digest_matches_reviewed"] and out["bundle_review_status"] == "ready_for_human_review"
          and out["bundle_package_intact"] and out["bundle_package_matches_source"] and out["bundle_coverage_rows"] == N_TEXTBOOK
          and out["sandbox_reference_components"] == N_COMPONENTS and out["isolated_rehearsal_passed"] is not False
          and out["db_integrity"] == "ok" and out["stage1_gate"]["status"] == "READY"
          and out["unit9_rows"] == N_TEXTBOOK and out["unit9_ids_match_specs"] and not out["binding_mismatches"]
          and not out["unit9_tracker_rows_before"] and not out["skill_tracker_rows_before"] and not out["active_orchestrator_jobs"]
          and not out["hot_rollback_journal"] and out["write_lock_free"] is True
          and not any(out["unit9_already_published"].values()) and not out["promoted_package_exists"] and not out["domain_in_store"]
          and not out["unit9_v3_fixed_entries"] and out["unit9_deferred_fixed_entries"] == sorted(DEFERRED_IDS)
          and all(out["unit9_deferred_fixed_sha_ok"].values()) and not FIXED_ROWS
          and 12963 in DEFERRED_IDS)
    out["passed"] = bool(ok)
    _write("precheck", {k: v for k, v in out.items() if k != "protected_digest"})
    if ok:
        _save_state(precheck=out, precheck_time=STAMP)
    else:
        raise SystemExit("precheck failed; do not release")


def backup() -> None:
    pre = _state().get("precheck") or {}
    if not pre.get("passed"):
        raise SystemExit("run a passing precheck first")
    target = BACKUP_ROOT / STAMP
    target.mkdir(parents=True)
    src = _ro()
    dst = sqlite3.connect(target / "kumon_math.db")
    src.backup(dst)
    integrity = dst.execute("pragma integrity_check").fetchone()[0]
    dst.row_factory = sqlite3.Row
    unit_rows = _unit_rows(dst)
    full = dst.execute("select * from gencode_component_tracker")
    full_cols = [d[0] for d in full.description]
    full_rows = [dict(zip(full_cols, r)) for r in full.fetchall()]
    textbook = _textbook_digest(dst)
    dst.close()
    src.close()
    (target / "gencode_component_tracker_full.json").write_text(json.dumps(full_rows, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (target / "unit9_tracker_rows.json").write_text(json.dumps(unit_rows, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    shutil.copy2(STORE, target / STORE.name)
    shutil.copy2(FIXED_CONFIG, target / FIXED_CONFIG.name)
    shutil.copy2(WORKSPACE / "promotion_bundle.json", target / "promotion_bundle.reviewed.json")
    files = {str(p.relative_to(target)).replace("\\", "/"): _sha(p) for p in sorted(target.rglob("*")) if p.is_file()}
    (target / "SHA256SUMS.json").write_text(json.dumps(files, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = integrity == "ok" and textbook == pre["textbook_digest"] and not unit_rows
    _write("backup", {"backup_dir": str(target), "db_integrity": integrity, "db_sha256": files["kumon_math.db"], "store_sha256": files[STORE.name],
                      "tracker_rows_total": len(full_rows), "unit9_tracker_rows": len(unit_rows), "files": len(files),
                      "textbook_unchanged_since_precheck": textbook == pre["textbook_digest"], "passed": ok,
                      "note": "kumon_math.db here is forensic only; rollback never restores the whole DB"})
    if not ok:
        raise SystemExit("backup check failed; stop")
    _save_state(backup_dir=str(target), store_sha256_before=files[STORE.name])


def promote() -> None:
    from core.gencode.reviewed_capability_promotion import preflight_reviewed_bundle, promote_reviewed_workspace

    _backup_dir()
    record = _record()
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
    if preflight["bundle_sha256"] != record["bundle_canonical_sha256_after"]:
        raise SystemExit("approved bundle digest differs from the approval record; stop")
    result = promote_reviewed_workspace(WORKSPACE, teacher_approved=True)
    out = {k: result.get(k) for k in result if k != "bundle"}
    out["store_sha256_after"] = _sha(STORE)
    out["promoted_package_matches_bundle"] = all((PROMOTED_PACKAGE / n).is_file() and _sha(PROMOTED_PACKAGE / n) == h for n, h in bundle["files"].items())
    out["unit9_published_paths"] = _unit9_published_paths()
    _write("promote", out)
    if not out["promoted_package_matches_bundle"] or any(out["unit9_published_paths"].values()):
        raise SystemExit("promotion check failed; stop")
    _save_state(approved_bundle_digest=record["bundle_canonical_sha256_after"])


def quarantine() -> None:
    target = _backup_dir() / f"quarantine_{STAMP}"
    moved: list = []
    for cid in EXAMPLE_IDS:
        _move(DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}", target, moved)
    for s in USED_SKILLS:
        for path in _staging_paths(s):
            _move(path, target, moved)
    _write("quarantine", {"quarantine_dir": str(target), "moved": moved})


def _load_generate(path: Path):
    import importlib.util
    import uuid

    spec = importlib.util.spec_from_file_location(f"u9d_{uuid.uuid4().hex}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _surface(p: dict) -> str:
    aids = [[a.get("type"), a.get("label"), hashlib.sha256(str(a.get("value")).encode()).hexdigest()] for a in p.get("visual_aids") or []]
    return json.dumps([p["question_text"], p["correct_answer"], aids], sort_keys=True, ensure_ascii=False, default=str)


def _verify_component(skill: str, cid: int, seeds: int = 20) -> dict:
    from agent_domains_candidate.bivariate_statistics import verification as V

    gen = DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
    ref = _load_generate(SANDBOX_REFERENCE / skill / "components" / f"src_{cid}" / "generate.py").generate
    generate = _load_generate(gen).generate
    out = {"generate_sha256": _sha(gen), "failures": [], "differs_from_reviewed_sandbox": []}
    for seed in range(seeds):
        payload = generate(seed=seed, component_id=f"src_{cid}")
        problems = [] if payload.get("skill_id") == skill and payload.get("textbook_example_id") == cid else ["identity"]
        problems += V.verify_payload(payload, skill, f"src_{cid}")
        if cid in CHART_IDS and (len(payload.get("visual_aids") or []) != 2 or not payload.get("visual_backed")):
            problems.append("visual_aids_missing")
        if problems:
            out["failures"].append(f"seed{seed}:{problems}")
        if _surface(payload) != _surface(ref(seed=seed, component_id=f"src_{cid}")):
            out["differs_from_reviewed_sandbox"].append(seed)
    return out


def rebuild() -> None:
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.registry.domain_operation_registry import operation_is_registered

    _backup_dir()
    published_ops = {OP[spec[1]] for spec in COMPONENTS.values()}
    if not all(operation_is_registered(DOMAIN, op) for op in published_ops):
        raise SystemExit(f"{DOMAIN} is not promoted in this process; run the promote step first")
    excluded = _excluded()
    leftovers = [cid for cid in EXAMPLE_IDS if (DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}").exists()]
    if leftovers:
        raise SystemExit(f"run quarantine first; dry-run components still present: {leftovers}")
    conn = _connect()
    report: dict = {"excluded_components": sorted(excluded)}
    try:
        for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
            if cid in excluded:
                continue
            skill = SKILLS[skill_key]
            variants = B.collect_variants(cid, op, source, sampler)
            payload = dispatch_registered_operation(DOMAIN, OP[op], seed=0, constraints=dict(source))[1]
            spec = {"fixed_domain_key": DOMAIN, "required_capabilities": [OP[op]], "domain_operation": OP[op], "problem_type_id": OP[op],
                    "presentation_mode": payload["presentation_mode"], "answer_type": payload["answer_type"],
                    "generation_constraints": {"variants": variants}}
            try:
                result = run_gencode_phase2_raw(skill, dry_run=True, v3_textbook_example_id=cid, v3_conn=conn,
                                                v3_dryrun_base_dir=str(DRYRUN), force_regenerate=True, v3_induced_spec=spec)
            except Exception as exc:  # noqa: BLE001
                report[cid] = {"skill": skill, "exception": f"{type(exc).__name__}: {exc}"}
                continue
            row = conn.execute("select skill_id, gencode_status from gencode_component_tracker where textbook_example_id=?", (cid,)).fetchone()
            item = {"skill": skill, "operation": OP[op], "phase_status": result.get("phase_status"), "tracker": list(row) if row else None,
                    "variants": len(variants)}
            if (DRYRUN / skill / "components" / f"src_{cid}" / "generate.py").is_file():
                item["verify"] = _verify_component(skill, cid)
            report[cid] = item
            print(cid, skill[3:], item["tracker"], (item.get("verify") or {}).get("failures", "no generate.py")[:2], flush=True)
    finally:
        conn.close()
    failures = {cid: it for cid, it in report.items() if isinstance(it, dict) and (
        it.get("exception") or (it.get("tracker") or [None, None])[1] != "verified" or "verify" not in it
        or it["verify"]["failures"] or it["verify"]["differs_from_reviewed_sandbox"])}
    _write("rebuild", {"failures": failures, "report": report, "passed": not failures})
    if failures:
        raise SystemExit("rebuild verification failed; do not publish")


def _build_checks(pre_publish: bool = True) -> dict:
    """Pre-publish gate: tracker, dry-run dirs, store and promoted package agree with the approved bundle; nothing published yet."""
    from core.registry.domain_operation_registry import operation_is_registered

    expected = _expected()
    excluded = _excluded()
    con = _ro()
    try:
        rows = _unit_rows(con)
    finally:
        con.close()
    out: dict = {"expected_components": {s: len(v) for s, v in expected.items()}, "excluded_components": sorted(excluded)}
    tracker = {r["textbook_example_id"]: (r["skill_id"], r["gencode_status"]) for r in rows}
    out["tracker_duplicates"] = len(rows) - len(tracker)
    out["tracker_matches_expected"] = tracker == {c: (s, "verified") for s, ids in expected.items() for c in ids}
    out["dryrun_components"] = {s: sorted(int(p.name[4:]) for p in (DRYRUN / s / "components").glob("src_*") if p.is_dir())
                                if (DRYRUN / s / "components").is_dir() else [] for s in USED_SKILLS}
    out["dryrun_matches_expected"] = out["dryrun_components"] == expected
    out["staging_leftovers"] = [str(p.relative_to(ROOT)) for s in USED_SKILLS for p in _staging_paths(s) if p.exists()] if pre_publish else []
    store = json.loads(STORE.read_text(encoding="utf-8"))
    entry = (store.get("domains") or {}).get(DOMAIN) or {}
    bundle = json.loads((WORKSPACE / "promotion_bundle.json").read_text(encoding="utf-8"))
    out["store_bundle_sha256"] = entry.get("bundle_sha256")
    out["store_matches_approval"] = entry.get("bundle_sha256") == _state().get("approved_bundle_digest") and sorted(entry.get("skill_bindings") or {}) == USED_SKILLS
    out["promoted_package_matches_bundle"] = all((PROMOTED_PACKAGE / n).is_file() and _sha(PROMOTED_PACKAGE / n) == h for n, h in bundle["files"].items())
    published_ops = {OP[spec[1]] for spec in COMPONENTS.values()}
    out["operations_registered"] = sum(operation_is_registered(DOMAIN, op) for op in published_ops)
    out["unit9_published_paths"] = _unit9_published_paths()
    out["passed"] = bool(out["tracker_matches_expected"] and not out["tracker_duplicates"] and out["dryrun_matches_expected"]
                         and not out["staging_leftovers"] and out["store_matches_approval"] and out["promoted_package_matches_bundle"]
                         and out["operations_registered"] == N_OPERATIONS)
    return out


def verify_build() -> None:
    out = _build_checks()
    out["nothing_published_yet"] = not any(out["unit9_published_paths"].values())
    out["passed"] = out["passed"] and out["nothing_published_yet"]
    _write("verify-build", out)
    _save_state(verify_build_passed=out["passed"], verify_build_snapshot=_release_snapshot()["digest"])
    if not out["passed"]:
        raise SystemExit("verify-build failed; do not enter the maintenance window")


def _undo_publish(target: Path) -> dict:
    moved: list = []
    for s in USED_SKILLS:
        _move(ROOT / "skills" / f"{s}.py", target, moved)
        _move(ROOT / "agent_skills_v3" / s, target, moved)
        for path in _staging_paths(s):
            _move(path, target, moved)
    return {"moved": moved, "remaining": _unit9_published_paths()}


def publish() -> None:
    import core.gencode.v3_production_publish_service as pub

    backup_dir = _backup_dir()
    guard = _require_maintenance("publish")
    state = _state()
    if not state.get("verify_build_passed"):
        raise SystemExit("run a passing verify-build first")
    checks = _build_checks()
    if not checks["passed"] or any(checks["unit9_published_paths"].values()):
        raise SystemExit(f"release state changed since verify-build: {json.dumps(checks, ensure_ascii=False, default=str)[:600]}")
    if _release_snapshot()["digest"] != state.get("verify_build_snapshot"):
        raise SystemExit("release files or tracker changed since verify-build; run verify-build again")
    expected = _expected()
    excluded = _excluded()
    inject = os.environ.get("U9_DEPLOY_INJECT_FAIL_AT") if _rehearsal() else None
    conn = _connect()
    out: dict = {"guard": guard, "skills": {}}
    failed = None
    try:
        for skill in USED_SKILLS:
            partial = any(SKILLS[COMPONENTS[c][0]] == skill for c in excluded)
            try:
                if inject == skill:
                    raise RuntimeError("injected failure (isolated rehearsal)")
                result = pub.publish_single_v3_skill_to_production(conn=conn, skill_id=skill, project_root=str(ROOT), staging_root=str(STAGING),
                                                                   allow_partial_coverage=partial)
                item = {k: result.get(k) for k in ("status", "component_count", "smoke_status", "production_smoke_status", "variation_status",
                                                   "dynamic_count", "static_count")}
                comps = ROOT / "agent_skills_v3" / skill / "components"
                item["published_components"] = sorted(int(p.name[4:]) for p in comps.glob("src_*") if p.is_dir()) if comps.is_dir() else []
                ok_status = ("partial_published", "runtime_ready_with_variation_warning") if partial else ("production_published", "runtime_ready_with_variation_warning")
                if item["status"] not in ok_status or item["published_components"] != expected[skill]:
                    raise RuntimeError(f"unexpected publish result: {item}")
                out["skills"][skill] = item
            except Exception as exc:  # noqa: BLE001
                out["skills"][skill] = {"exception": f"{type(exc).__name__}: {exc}"}
                failed = skill
                break
    finally:
        conn.close()
    if failed:
        out["auto_rollback"] = _undo_publish(backup_dir / f"publish_failed_{STAMP}")
        out["passed"] = False
        _write("publish", out)
        raise SystemExit(f"publish failed at {failed}; every Unit 9 wrapper written in this run was moved out "
                         f"(remaining: {out['auto_rollback']['remaining']}); services may be restarted on the previous version")
    snap = _release_snapshot()
    out["release_snapshot"] = snap["digest"]
    out["passed"] = True
    _write("publish", out)
    _save_state(published_snapshot=snap["digest"], published_time=STAMP)


def _facade_smoke(seeds: int = 60) -> dict:
    from agent_domains_candidate.bivariate_statistics import verification as V

    def verdict(res, default: bool) -> bool:
        return res if isinstance(res, bool) else bool(res.get("correct", res.get("is_correct", default)))

    out = {}
    for skill in USED_SKILLS:
        facade = ROOT / "skills" / f"{skill}.py"
        if not facade.is_file():
            out[skill] = {"problems": ["no facade"], "served_examples": {}}
            continue
        module = _load_generate(facade)
        served: dict = {}
        problems = []
        for seed in range(seeds):
            payload = module.generate(seed=seed)
            cid = payload.get("textbook_example_id")
            served[cid] = served.get(cid, 0) + 1
            expected = payload["correct_answer"]
            if not verdict(module.check(expected, expected, question_payload=payload), True):
                problems.append(f"seed{seed}:canonical_rejected")
            multi = payload["answer_contract"]["answer_type"] == "multi_part"
            for part in V.parts_of(payload):
                for kind, value, want in (("wrong", V.wrong_value(part), False), ("equivalent", V.equivalent_value(part), True)):
                    if value is None:
                        continue
                    answer = {**expected, part["key"]: value} if multi else value
                    if verdict(module.check(answer, expected, question_payload=payload), not want) != want:
                        problems.append(f"seed{seed}:{part['key']}:{kind}_misgraded")
        out[skill] = {"served_examples": dict(sorted(served.items(), key=lambda kv: str(kv[0]))), "problems": problems}
    return out


def verify_consistency() -> None:
    """Read-only, fresh process: the four published skills, tracker, store and promoted package agree, and nothing changed since publish."""
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

    state = _state()
    out = _build_checks(pre_publish=False)
    expected = _expected()
    excluded = _excluded()
    out["manifest"] = {}
    for skill in USED_SKILLS:
        path = ROOT / "agent_skills_v3" / skill / "component_manifest.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        comps = [c for c in data.get("components") or [] if isinstance(c, dict)]
        dirs = ROOT / "agent_skills_v3" / skill / "components"
        out["manifest"][skill] = {
            "facade": (ROOT / "skills" / f"{skill}.py").is_file(), "publish_status": data.get("publish_status"),
            "verified": sorted(int(c["textbook_example_id"]) for c in comps if c.get("status") == "verified"),
            "component_dirs": sorted(int(p.name[4:]) for p in dirs.glob("src_*") if p.is_dir()) if dirs.is_dir() else [],
            "domain_authority": [(r.fixed_domain_key, r.binding_status) for r in
                                 [resolve_domain_authority(skill, selected_operation=OP[COMPONENTS[expected[skill][0]][1]])]][0]}
    out["skills_match_expected"] = all(m["facade"] and m["publish_status"] and m["verified"] == expected[s] and m["component_dirs"] == expected[s]
                                       and m["domain_authority"][0] == DOMAIN for s, m in out["manifest"].items())
    out["excluded_absent"] = all(c not in m["component_dirs"] for m in out["manifest"].values() for c in excluded)
    out["facade"] = _facade_smoke()
    served = {c for v in out["facade"].values() for c in v["served_examples"]}
    out["facade_problems"] = {s: v["problems"][:5] for s, v in out["facade"].items() if v["problems"]}
    out["facade_served_excluded"] = sorted(served & excluded)
    snap = _release_snapshot()
    out["release_snapshot"] = snap["digest"]
    out["unchanged_since_publish"] = snap["digest"] == state.get("published_snapshot")
    pre = state.get("precheck") or {}
    out["protected_files_unchanged"] = _tree_digest(_protected_paths()) == pre.get("protected_digest")
    con = _ro()
    try:
        out["textbook_unchanged"] = _textbook_digest(con) == pre.get("textbook_digest")
        out["db_integrity"] = con.execute("pragma integrity_check").fetchone()[0]
    finally:
        con.close()
    out["passed"] = bool(out["passed"] and out["skills_match_expected"] and out["excluded_absent"] and not out["facade_problems"]
                         and not out["facade_served_excluded"] and out["unchanged_since_publish"] and out["protected_files_unchanged"]
                         and out["textbook_unchanged"] and out["db_integrity"] == "ok")
    del out["facade"]
    _write("verify-consistency", out)
    if not out["passed"]:
        raise SystemExit("verify-consistency failed; keep 5000 / 5001 stopped and run rollback-publish")


def accept() -> None:
    """Runtime acceptance through the real practice routes in a fresh process against a DB copy (no student record written)."""
    import collections
    import logging

    from agent_domains_candidate.bivariate_statistics import verification as V

    expected = _expected()
    excluded = _excluded()
    copy = _backup_dir() / f"accept_{STAMP}" / "kumon_math_accept.db"
    copy.parent.mkdir(parents=True, exist_ok=True)
    src = _ro()
    dst = sqlite3.connect(copy)
    src.backup(dst)
    student = dst.execute("select id from users where role='student' order by id limit 1").fetchone()
    dst.close()
    src.close()
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{copy.as_posix()}"

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

    out: dict = {"db_copy": str(copy), "student_id": student[0] if student else None, "excluded_components": sorted(excluded), "skills": {}}
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        for skill in USED_SKILLS:
            page = client.get(f"/practice/{skill}")
            report = {"practice_page": page.status_code, "served": collections.Counter(), "http_errors": [], "grading": [], "load_errors": 0,
                      "route_modes": collections.Counter(), "answer_leaks": []}
            plan = [None] * 12 + [f"src_{cid}" for cid in expected[skill]]
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
                truth = payload.get("correct_answer")
                canon = {json.dumps(v, ensure_ascii=False, sort_keys=True, default=str) for v in
                         ([truth] + (list(truth.values()) if isinstance(truth, dict) else []))} - {'""', "null"}
                shown = [body.get("answer_format_example"), contract.get("answer_format_example")] + [
                    p.get("answer_format_example") for p in contract.get("parts") or []]
                if any(v not in (None, "") and json.dumps(v, ensure_ascii=False, sort_keys=True, default=str) in canon for v in shown):
                    report["answer_leaks"].append(cid)
                multi = contract.get("answer_type") == "multi_part"
                parts = V.parts_of(payload)
                if multi:
                    right = {p["key"]: ui_value(p, truth[p["key"]]) for p in parts}
                    checks = [("wrong", {**right, p["key"]: ui_value(p, V.wrong_value(p))}, False) for p in parts] + [("right", right, True)]
                else:
                    checks = [("wrong", ui_value(parts[0], V.wrong_value(parts[0])), False), ("right", ui_value(parts[0], truth), True)]
                for kind, answer, want in checks:
                    got, data = submit(client, skill, body, answer)
                    report["load_errors"] += "模組載入錯誤" in json.dumps(data, ensure_ascii=False)
                    if got is not want:
                        report["grading"].append(f"{cid}:{kind}:{got}")
            report["served"] = dict(sorted(report["served"].items(), key=lambda kv: str(kv[0])))
            report["route_modes"] = dict(report["route_modes"])
            out["skills"][skill] = report
        out["other_skill_smoke"] = {}
        for other in OTHER_SKILLS_SMOKE:
            res = client.get(f"/get_next_question?skill={other}&level=1")
            body = res.get_json(silent=True) or {}
            out["other_skill_smoke"][other] = [res.status_code, bool(body.get("question_uid")), body.get("route_mode")]
    out["runtime_errors"] = errors[:20]
    covered = {cid for r in out["skills"].values() for cid in r["served"]}
    want = {c for ids in expected.values() for c in ids}
    out["components_served"] = len(covered & want)
    out["excluded_served"] = sorted(covered & excluded)
    # Deferred originals must remain reachable as ungraded textbook rows (mixed fallback).
    deferred_report = {}
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(student[0])
            sess["_fresh"] = True
        for rid in sorted(DEFERRED_IDS):
            skill = {
                12947: "gh_ScatterPlot", 12948: "gh_ScatterPlot",
                12954: "gh_CorrelationCoefficient", 12960: "gh_CorrelationCoefficient",
                12963: "gh_LeastSquaresMethodAndRegressionLine",
            }[rid]
            res = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation&textbook_example_id={rid}")
            body = res.get_json(silent=True) or {}
            item = {
                "status": res.status_code,
                "source": body.get("question_source"),
                "fixed": body.get("fixed_textbook_practice"),
                "check_mode": body.get("check_mode"),
                "graded": body.get("graded"),
                "images": len(body.get("image_assets") or []),
                "input": body.get("answer_input_type") or body.get("answer_type"),
            }
            if res.status_code == 200 and body.get("question_uid"):
                sub = client.post("/check_answer", json={"skill_id": skill, "question_uid": body["question_uid"], "student_answer": "測試"})
                data = sub.get_json(silent=True) or {}
                item["submit_graded"] = data.get("graded")
                item["submit_correct"] = data.get("correct")
            deferred_report[rid] = item
        # Cross-question dependency (隨堂練習7) must still prepend 例題6 data.
        res = client.get("/get_next_question?skill=gh_CorrelationCoefficient&level=1&mode=type_rotation&textbook_example_id=12967")
        body = res.get_json(silent=True) or {}
        stem7 = str(body.get("question_text") or "")
        out["practice7_dependency"] = {
            "status": res.status_code,
            "prefix_ok": stem7.startswith("【例題6的資料】"),
            "ungraded": body.get("check_mode") == "ungraded_self_study",
        }
    out["deferred_originals"] = deferred_report
    out["passed"] = bool(all(not r["http_errors"] and not r["grading"] and r["practice_page"] == 200 and not r["load_errors"]
                             and not r["answer_leaks"] and set(r["route_modes"]) == {"v3"} for r in out["skills"].values())
                         and out["components_served"] == len(want) and not out["excluded_served"]
                         and all(v[0] == 200 and v[1] for v in out["other_skill_smoke"].values()) and not errors
                         and all(d.get("status") == 200 and d.get("source") == "db_textbook_example"
                                 and d.get("fixed") == "ungraded" and d.get("check_mode") == "ungraded_self_study"
                                 and d.get("graded") is False and d.get("submit_graded") is False and d.get("submit_correct") is None
                                 and d.get("images", 0) >= 1 for d in deferred_report.values())
                         and deferred_report.get(12947, {}).get("input") == "handwriting"
                         and out["practice7_dependency"].get("prefix_ok") is True
                         and out["practice7_dependency"].get("ungraded") is True)
    _write("accept", out)
    if not out["passed"]:
        raise SystemExit("accept failed")


def rollback_publish() -> None:
    """Remove the Unit 9 release (wrappers, published skill dirs, staging / dry-run dirs); optionally restore the store and the
    Unit 9 tracker rows from the verified backup. The DB file itself is never restored."""
    backup_dir = _backup_dir()
    guard = _require_maintenance("rollback-publish")
    target = backup_dir / f"rollback_{STAMP}"
    out: dict = {"guard": guard, "rollback_dir": str(target)}
    out.update(_undo_publish(target))
    moved = out["moved"]
    for s in USED_SKILLS:
        _move(DRYRUN / s, target, moved)
    restored = {}
    if "--restore-config" in sys.argv:
        shutil.copy2(backup_dir / STORE.name, STORE)
        restored[STORE.name] = str(backup_dir / STORE.name)
        _move(PROMOTED_PACKAGE, target, moved)
    if "--restore-tracker" in sys.argv:
        before = json.loads((backup_dir / "unit9_tracker_rows.json").read_text(encoding="utf-8"))
        conn = _connect()
        try:
            with conn:
                current = _unit_rows(conn)
                (target / "unit9_tracker_rows_removed.json").parent.mkdir(parents=True, exist_ok=True)
                (target / "unit9_tracker_rows_removed.json").write_text(json.dumps(current, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
                conn.execute(f"delete from gencode_component_tracker where textbook_example_id in ({','.join('?' * len(EXAMPLE_IDS))})", EXAMPLE_IDS)
                for row in before:
                    cols = list(row)
                    conn.execute(f"insert into gencode_component_tracker ({','.join(cols)}) values ({','.join('?' * len(cols))})", [row[c] for c in cols])
            restored["unit9_tracker_rows"] = {"removed": len(current), "restored": len(before)}
        finally:
            conn.close()
    out["restored"] = restored
    out["remaining_published"] = _unit9_published_paths()
    state = _state()
    pre = state.get("precheck") or {}
    out["protected_files_unchanged"] = _tree_digest(_protected_paths()) == pre.get("protected_digest")
    if "--restore-config" in sys.argv:
        out["store_matches_backup"] = _sha(STORE) == state.get("store_sha256_before")
        out["promoted_package_absent"] = not PROMOTED_PACKAGE.exists()
    if "--restore-tracker" in sys.argv:
        con = _ro()
        try:
            now = _unit_rows(con)
            out["textbook_unchanged"] = _textbook_digest(con) == pre.get("textbook_digest")
        finally:
            con.close()
        out["unit9_tracker_rows_now"] = len(now)
        out["tracker_matches_backup"] = json.dumps(now, sort_keys=True, default=str) == json.dumps(before, sort_keys=True, default=str)
    out["passed"] = bool(not any(out["remaining_published"].values()) and out["protected_files_unchanged"]
                         and out.get("store_matches_backup", True) and out.get("promoted_package_absent", True)
                         and out.get("textbook_unchanged", True) and out.get("tracker_matches_backup", True))
    out["next"] = "restart Flask 5000 (owner, original admin window) and 5001 so no process keeps the removed wrappers in memory"
    _write("rollback-publish", out)
    _save_state(verify_build_passed=False, published_snapshot=None)
    if not out["passed"]:
        raise SystemExit("rollback verification failed; keep services stopped and inspect the rollback report")


STEPS = {"precheck": precheck, "backup": backup, "promote": promote, "quarantine": quarantine, "rebuild": rebuild, "verify-build": verify_build,
         "publish": publish, "verify-consistency": verify_consistency, "accept": accept, "rollback-publish": rollback_publish}
READ_ONLY = {"precheck", "verify-build", "verify-consistency", "accept"}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in STEPS:
        raise SystemExit(f"usage: deploy_unit9.py {{{'|'.join(STEPS)}}} --confirm")
    if step not in READ_ONLY and "--confirm" not in sys.argv:
        raise SystemExit("formal step: add --confirm after the owner approved the bundle")
    _rehearsal()
    STEPS[step]()
