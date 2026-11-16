"""Isolated rehearsal of deploy_unit8.py: full release + rollback, injected mid-publish failure, and teacher-excluded 12934.

Runs only against the review copy (no .git, no server started); resets it to the formal, unpublished state first.
The formal project is read-only here except for the summary report written next to this file.

    python reports/gh_math2_unit8_bundle/rehearse_deploy_unit8.py
"""
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAL = HERE.parents[1]
COPY = Path(r"C:\Projects\_u8_teacher_review\Mathproject_tvet_mathB_review")
PY = str(FORMAL / ".venv" / "Scripts" / "python.exe")
SKILLS = ["gh_DataScalingAndShifting", "gh_Mean", "gh_MedianAndPercentiles", "gh_VarianceAndStandardDeviation"]
IDS = list(range(12912, 12947))
BUNDLE_REL = "reports/domain_operation_workspaces/capability_statistics_univariate_descriptive_3b91cfbb/revision_0004"
MIRROR_DIRS = ["core", "configs", "skills", "agent_skills_v3", "agent_domains_candidate", "templates", "reports/gencode_v3_dryrun",
               "runtime/v3_publish_staging", BUNDLE_REL, "reports/gh_math2_unit8_bundle", "tmp/gh_math2_unit8_sandbox_dryrun_r4"]
REPORT = HERE / "rehearsal_deploy_unit8_report.json"
DIGEST = "d6b6310c279d5b7dfcf131d3695948db0647b50b186e86c766a656cef274ee3a"
sys.stdout.reconfigure(encoding="utf-8")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree(root: Path, rels) -> dict:
    out = {}
    for rel in rels:
        base = root / rel
        files = [base] if base.is_file() else ([Path(d) / n for d, _x, ns in os.walk(base) for n in ns if "__pycache__" not in d] if base.exists() else [])
        out.update({str(f.relative_to(root)).replace("\\", "/"): sha(f) for f in files})
    return out


def state_digest(root: Path) -> dict:
    """Everything a Unit 8 release may touch, plus DB tables row counts."""
    rels = (["skills", "agent_skills_v3", "core/domain/promoted", "configs/gencode_promoted_capabilities.json", "configs/fixed_textbook_practice.json"]
            + [f"reports/gencode_v3_dryrun/{s}" for s in SKILLS]
            + [f"runtime/v3_publish_staging/{p}" for s in SKILLS for p in (s, f"agent_skills_v3/{s}", f"skills/{s}.py", f"skills/{s}.py.bak")])
    files = tree(root, rels)
    con = sqlite3.connect(f"file:{(root / 'instance/kumon_math.db').as_posix()}?mode=ro", uri=True)
    try:
        tables = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
        counts = {t: con.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tables}
        tracker = con.execute(f"select count(*) from gencode_component_tracker where textbook_example_id between 12912 and 12946").fetchone()[0]
        textbook = hashlib.sha256(json.dumps(con.execute("select * from textbook_examples where id between 12912 and 12946 order by id").fetchall(),
                                             ensure_ascii=False, default=str).encode()).hexdigest()
    finally:
        con.close()
    return {"files": files, "files_digest": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
            "table_counts": counts, "unit8_tracker_rows": tracker, "textbook_digest": textbook}


def diff(a: dict, b: dict) -> dict:
    fa, fb = a["files"], b["files"]
    return {"files_added": sorted(set(fb) - set(fa))[:12], "files_removed": sorted(set(fa) - set(fb))[:12],
            "files_changed": sorted(k for k in set(fa) & set(fb) if fa[k] != fb[k])[:12],
            "table_count_changes": {t: [a["table_counts"].get(t), n] for t, n in b["table_counts"].items() if a["table_counts"].get(t) != n},
            "unit8_tracker_rows": [a["unit8_tracker_rows"], b["unit8_tracker_rows"]], "textbook_same": a["textbook_digest"] == b["textbook_digest"]}


def reset_copy() -> dict:
    if (COPY / ".git").exists():
        raise SystemExit("rehearsal copy unexpectedly has .git")
    codes = {}
    for rel in MIRROR_DIRS:
        (COPY / rel).mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["robocopy", str(FORMAL / rel), str(COPY / rel), "/MIR", "/XD", "__pycache__", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/R:1", "/W:1"],
                           capture_output=True, text=True)
        codes[rel] = r.returncode
        if r.returncode >= 8:
            raise SystemExit(f"robocopy failed for {rel}: {r.stdout[-400:]}")
    for name in ("app.py", "config.py", "models.py"):
        shutil.copy2(FORMAL / name, COPY / name)
    shutil.rmtree(COPY / "backups" / "math2_unit8_univariate_statistics", ignore_errors=True)
    db = COPY / "instance" / "kumon_math.db"
    for suffix in ("", "-wal", "-shm", "-journal"):
        Path(str(db) + suffix).unlink(missing_ok=True)
    src = sqlite3.connect(f"file:{(FORMAL / 'instance/kumon_math.db').as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(db)
    src.backup(dst)
    dst.close()
    src.close()
    return codes


def run(step: str, *flags: str, env_extra: dict | None = None, script: str = "deploy_unit8.py") -> dict:
    env = {k: v for k, v in os.environ.items() if k != "MATHPROJECT_DATABASE_URI"}
    env.update(env_extra or {})
    env["PYTHONIOENCODING"] = "utf-8"
    args = [PY, str(COPY / "reports/gh_math2_unit8_bundle" / script)] + ([step] if step else []) + list(flags)
    t0 = time.time()
    r = subprocess.run(args, cwd=str(COPY), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    tail = (r.stdout + r.stderr).strip().splitlines()
    out_file = COPY / "reports/gh_math2_unit8_bundle" / f"deploy_unit8_rev4_{step}.json"
    payload = json.loads(out_file.read_text(encoding="utf-8")) if step and out_file.is_file() and out_file.stat().st_mtime >= t0 else None
    result = {"step": f"{script} {step} {' '.join(flags)}".strip(), "rc": r.returncode, "seconds": round(time.time() - t0, 1),
              "passed": payload.get("passed") if isinstance(payload, dict) else None, "tail": tail[-3:]}
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return {**result, "payload": payload}


def checklist(reject: tuple = ()) -> str:
    data = json.loads((FORMAL / "reports/gh_math2_unit8_bundle/revision_0004_teacher_review.json").read_text(encoding="utf-8"))
    data["reviewer"] = "ISOLATED REHEARSAL (not a teacher)"
    data["reviewed_at"] = time.strftime("%Y-%m-%d %H:%M")
    for c in data["components"]:
        c["teacher_review"] = "rejected" if c["id"] in reject else "approved"
    path = COPY / "tmp" / f"rehearsal_checklist_{'_'.join(map(str, reject)) or 'all'}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return str(path)


def approve(path: str) -> dict:
    return run("", "--approved-by", "isolated rehearsal of deploy_unit8.py", "--checklist", path, "--isolated-rehearsal", script="record_approval_unit8.py")


def reset_bundle_and_record() -> None:
    backup_dirs = sorted((COPY / "backups/math2_unit8_univariate_statistics").glob("2*"))
    shutil.copy2(backup_dirs[0] / "promotion_bundle.reviewed.json", COPY / BUNDLE_REL / "promotion_bundle.json")
    (COPY / "reports/gh_math2_unit8_bundle/deploy_unit8_rev4_approval_record.json").unlink(missing_ok=True)
    (COPY / "reports/gh_math2_unit8_bundle/deploy_unit8_rev4_state.json").unlink(missing_ok=True)


def ok(r: dict, expect_rc: int = 0, expect_pass=None) -> bool:
    return (r["rc"] == 0) == (expect_rc == 0) and (r["passed"] is not False if expect_pass is None else r["passed"] is expect_pass)


R = "--isolated-rehearsal"


def main() -> None:
    formal_before = state_digest(FORMAL)
    report: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "copy": str(COPY), "approved_bundle_digest": DIGEST}
    report["mirror_robocopy_codes"] = reset_copy()
    baseline = state_digest(COPY)
    report["copy_equals_formal_after_reset"] = baseline["files_digest"] == formal_before["files_digest"] and baseline["unit8_tracker_rows"] == 0 \
        and baseline["textbook_digest"] == formal_before["textbook_digest"]
    checks: dict = {}

    # Scenario 1: full release, negative guard tests, rollback.
    s1 = [run("precheck", R)]
    s1.append(run("backup", "--confirm", R))
    s1.append(run("promote", "--confirm", "--teacher-approved", R))                     # must refuse: no approval yet
    checks["promote_refused_without_approval"] = ok(s1[-1], expect_rc=1, expect_pass=None)
    s1.append(approve(checklist()))
    s1.append(run("promote", "--confirm", "--teacher-approved"))                        # must refuse: rehearsal-only record
    checks["formal_promote_refuses_rehearsal_record"] = ok(s1[-1], expect_rc=1, expect_pass=None)
    s1.append(run("promote", "--confirm", "--teacher-approved", R))
    s1.append(run("quarantine", "--confirm", R))
    s1.append(run("rebuild", "--confirm", R))
    s1.append(run("verify-build", R))
    before_guard = state_digest(COPY)["files_digest"]
    s1.append(run("publish", "--confirm", "--maintenance-window"))                      # must refuse: real 5000 / 5001 are listening
    checks["publish_refused_while_5000_5001_running"] = ok(s1[-1], expect_rc=1, expect_pass=None) and state_digest(COPY)["files_digest"] == before_guard \
        and "publish refused" in " ".join(s1[-1]["tail"])
    s1.append(run("publish", "--confirm", R))                                           # must refuse: no --maintenance-window
    checks["publish_requires_maintenance_flag"] = ok(s1[-1], expect_rc=1, expect_pass=None)
    s1.append(run("publish", "--confirm", "--maintenance-window", R))
    published = state_digest(COPY)
    s1.append(run("verify-consistency", R))
    s1.append(run("verify-consistency", R))                                             # second run stands in for "after start"
    s1.append(run("accept", R))
    s1.append(run("rollback-publish", "--confirm", "--maintenance-window", "--restore-config", "--restore-tracker", R))
    after1 = state_digest(COPY)
    report["scenario_full"] = {"steps": [{k: v for k, v in r.items() if k != "payload"} for r in s1],
                               "publish": (s1[-5]["payload"] or {}).get("skills"),
                               "accept_served": {s: v.get("served") for s, v in ((s1[-2]["payload"] or {}).get("skills") or {}).items()},
                               "published_vs_baseline": diff(baseline, published), "after_rollback_vs_baseline": diff(baseline, after1)}
    checks["full_release_steps_passed"] = all(ok(s1[i]) for i in (0, 1, 3, 5, 6, 7, 8, 11, 12, 13, 14, 15))
    checks["full_release_rollback_restores_baseline"] = after1["files_digest"] == baseline["files_digest"] and after1["unit8_tracker_rows"] == 0

    # Scenario 2: injected failure at the third skill, all-or-nothing undo.
    s2 = [run("promote", "--confirm", "--teacher-approved", R), run("quarantine", "--confirm", R), run("rebuild", "--confirm", R), run("verify-build", R)]
    s2.append(run("publish", "--confirm", "--maintenance-window", R, env_extra={"U8_DEPLOY_INJECT_FAIL_AT": "gh_MedianAndPercentiles"}))
    failed_publish = s2[-1]["payload"] or {}
    no_partial = not any((COPY / "skills" / f"{s}.py").exists() or (COPY / "agent_skills_v3" / s).exists() for s in SKILLS)
    s2.append(run("rollback-publish", "--confirm", "--maintenance-window", "--restore-config", "--restore-tracker", R))
    after2 = state_digest(COPY)
    report["scenario_injected_failure"] = {"steps": [{k: v for k, v in r.items() if k != "payload"} for r in s2],
                                           "publish_skills": failed_publish.get("skills"), "auto_rollback": failed_publish.get("auto_rollback"),
                                           "no_partial_skill_left": no_partial, "after_rollback_vs_baseline": diff(baseline, after2)}
    checks["injected_failure_leaves_no_partial_skill"] = all(ok(r) for r in s2[:4]) and ok(s2[4], expect_rc=1, expect_pass=False) and no_partial \
        and len([v for v in (failed_publish.get("skills") or {}).values() if "status" in v]) == 2
    checks["injected_failure_rollback_restores_baseline"] = after2["files_digest"] == baseline["files_digest"] and after2["unit8_tracker_rows"] == 0

    # Scenario 3: teacher rejects 12934 -> Partial Publish of gh_MedianAndPercentiles.
    reset_bundle_and_record()
    s3 = [run("precheck", R), run("backup", "--confirm", R), approve(checklist(reject=(12934,))), run("promote", "--confirm", "--teacher-approved", R),
          run("quarantine", "--confirm", R), run("rebuild", "--confirm", R), run("verify-build", R), run("publish", "--confirm", "--maintenance-window", R),
          run("verify-consistency", R), run("accept", R)]
    pub3 = (s3[7]["payload"] or {}).get("skills") or {}
    s3.append(run("rollback-publish", "--confirm", "--maintenance-window", "--restore-config", "--restore-tracker", R))
    after3 = state_digest(COPY)
    report["scenario_exclude_12934"] = {"steps": [{k: v for k, v in r.items() if k != "payload"} for r in s3], "publish": pub3,
                                        "accept_served": {s: v.get("served") for s, v in ((s3[9]["payload"] or {}).get("skills") or {}).items()},
                                        "after_rollback_vs_baseline": diff(baseline, after3)}
    median = pub3.get("gh_MedianAndPercentiles") or {}
    checks["exclusion_partial_publish"] = all(ok(r) for r in s3) \
        and median.get("status") == "partial_published" and 12934 not in (median.get("published_components") or [12934]) \
        and len(median.get("published_components") or []) == 8
    checks["exclusion_rollback_restores_baseline"] = after3["files_digest"] == baseline["files_digest"] and after3["unit8_tracker_rows"] == 0

    formal_after = state_digest(FORMAL)
    checks["formal_project_untouched"] = formal_after["files_digest"] == formal_before["files_digest"] and formal_after["unit8_tracker_rows"] == 0 \
        and formal_after["textbook_digest"] == formal_before["textbook_digest"]
    report["formal_table_count_changes_during_rehearsal"] = diff(formal_before, formal_after)["table_count_changes"]
    report["checks"] = checks
    report["passed"] = bool(report["copy_equals_formal_after_reset"] and all(checks.values()))
    report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": checks, "copy_equals_formal_after_reset": report["copy_equals_formal_after_reset"]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
