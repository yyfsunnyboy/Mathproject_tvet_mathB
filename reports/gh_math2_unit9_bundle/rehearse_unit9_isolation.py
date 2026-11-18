"""Lightweight isolation rehearsal for Unit 9 (no full Repository copy).

Checks reviewed-bundle preflight, package hashes, sandbox dry-run presence, and a
sqlite3.backup integrity copy. Does not write the formal promoted store/package.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.bivariate_statistics.bivariate_statistics_specs import COMPONENTS, DEFERRED_COMPONENTS, SKILLS  # noqa: E402
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle, preflight_reviewed_bundle  # noqa: E402

WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / "capability_statistics_bivariate_descriptive_affe15e1" / "revision_0001"
SANDBOX = ROOT / "tmp" / "gh_math2_unit9_sandbox_dryrun"
REPORT = Path(__file__).resolve().parent / "rehearsal_deploy_unit9_report.json"
APPROVED = "35f1d19d8cb29197bf094a2badd703a381992fda6151b9b29bf83da91a04ad19"
DB = ROOT / "instance" / "kumon_math.db"


def main() -> None:
    bundle = load_reviewed_bundle(WORKSPACE)
    digest = bundle_sha256(bundle)
    file_sha = hashlib.sha256((WORKSPACE / "promotion_bundle.json").read_bytes()).hexdigest()
    preflight = preflight_reviewed_bundle(WORKSPACE)
    pkg_ok = all(
        hashlib.sha256((WORKSPACE / "production_package" / name).read_bytes()).hexdigest() == digest_hash
        for name, digest_hash in bundle["files"].items()
    )
    src_ok = all(
        hashlib.sha256((ROOT / "agent_domains_candidate" / "bivariate_statistics" / name).read_bytes()).hexdigest()
        == digest_hash
        for name, digest_hash in bundle["files"].items()
    )
    sandbox_n = sum(
        1
        for cid, spec in COMPONENTS.items()
        if (SANDBOX / SKILLS[spec[0]] / "components" / f"src_{cid}" / "generate.py").is_file()
    )
    tmp = Path(tempfile.mkdtemp(prefix="u9_iso_db_"))
    try:
        src = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
        dst = sqlite3.connect(tmp / "kumon_math.db")
        src.backup(dst)
        integrity = dst.execute("pragma integrity_check").fetchone()[0]
        n_rows = dst.execute(
            "select count(*) from textbook_examples where source_curriculum='general' and source_volume='數學2' "
            "and source_chapter like '%單元9%'"
        ).fetchone()[0]
        dst.close()
        src.close()
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    formal_store = (ROOT / "configs" / "gencode_promoted_capabilities.json").read_text(encoding="utf-8")
    report = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": "preflight + sqlite3.backup integrity + package/sandbox checks (full repo copy forbidden)",
        "approved_bundle_digest": APPROVED,
        "bundle_file_sha256": file_sha,
        "bundle_digest": digest,
        "preflight_passed": bool(preflight.get("passed")),
        "preflight_blockers": preflight.get("blockers") or [],
        "package_matches_bundle": pkg_ok,
        "source_matches_bundle": src_ok,
        "sandbox_components": sandbox_n,
        "db_copy_integrity": integrity,
        "unit9_textbook_rows": n_rows,
        "deferred_excluded_from_publish": sorted(DEFERRED_COMPONENTS),
        "formal_store_untouched": "statistics.bivariate_descriptive" not in formal_store,
        "formal_package_absent": not (ROOT / "core" / "domain" / "promoted" / "bivariate_statistics").exists(),
        "review_status": bundle["review"]["status"],
    }
    # Before record_approval, preflight correctly blocks on missing human approval only.
    approval_only = set(report["preflight_blockers"]) <= {"human_review_not_approved", "approved_revision_mismatch"}
    report["preflight_blockers_are_approval_only"] = approval_only
    report["passed"] = bool(
        approval_only
        and digest == APPROVED
        and pkg_ok
        and src_ok
        and sandbox_n == 21
        and integrity == "ok"
        and n_rows == 26
        and 12963 in DEFERRED_COMPONENTS
        and report["formal_store_untouched"]
        and report["formal_package_absent"]
        and report["review_status"] == "ready_for_human_review"
    )
    report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("passed", "approved_bundle_digest", "preflight_passed", "db_copy_integrity", "sandbox_components")}, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
