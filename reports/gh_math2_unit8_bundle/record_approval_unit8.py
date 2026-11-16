"""Write the teacher / owner approval of 普高數學2 Unit 8 revision_0004 into its bundle review block.

The approval comes ONLY from the teacher checklist ``revision_0004_teacher_review.json`` after every component's
``teacher_review`` was set by a human to ``approved`` or ``rejected`` and ``reviewer`` / ``reviewed_at`` are filled in.
Rejected components become ``excluded_components`` (Partial Publish, Lean SOP §6); this script never marks anything approved itself.

    python reports/gh_math2_unit8_bundle/record_approval_unit8.py --approved-by "<owner authorization text>" [--checklist PATH]

``--isolated-rehearsal`` is only accepted in a project copy without ``.git`` and labels the record rehearsal-only;
deploy_unit8.py refuses such a record in the formal project.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle  # noqa: E402

WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / "capability_statistics_univariate_descriptive_3b91cfbb" / "revision_0004"
BUNDLE = WORKSPACE / "promotion_bundle.json"
EXPECTED_FILE_SHA = "c4d73c1ce449adda16c7f6edaba34c5f5a9817f9af6f0556d11cba29689819e1"
EXPECTED_DIGEST = "d6b6310c279d5b7dfcf131d3695948db0647b50b186e86c766a656cef274ee3a"
UNIT_IDS = list(range(12912, 12947))
MUST_DECIDE = (12934, 12932, 12923, 12941, 12946, 12926, 12930)
RECORD = HERE / "deploy_unit8_rev4_approval_record.json"


def _opt(name: str, default: str | None = None) -> str | None:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main() -> None:
    rehearsal = "--isolated-rehearsal" in sys.argv
    if rehearsal and (ROOT / ".git").exists():
        raise SystemExit("--isolated-rehearsal is not allowed in the formal project")
    approved_by = str(_opt("--approved-by") or "").strip()
    if not approved_by:
        raise SystemExit("--approved-by \"<owner authorization text>\" is required")
    checklist_path = Path(_opt("--checklist") or HERE / "revision_0004_teacher_review.json")
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    if checklist.get("bundle_sha256") != EXPECTED_DIGEST:
        raise SystemExit(f"checklist is for another bundle: {checklist.get('bundle_sha256')}")
    for field in ("reviewer", "reviewed_at"):
        if not str(checklist.get(field) or "").strip():
            raise SystemExit(f"checklist field {field!r} must be filled in by the teacher")
    decisions = {int(c["id"]): str(c.get("teacher_review") or "").strip() for c in checklist["components"]}
    if sorted(decisions) != UNIT_IDS:
        raise SystemExit("checklist does not cover exactly the 35 Unit 8 components")
    undecided = sorted(cid for cid, d in decisions.items() if d not in ("approved", "rejected"))
    if undecided:
        raise SystemExit(f"teacher decision missing (still pending) for: {undecided}")
    rejected = sorted(cid for cid, d in decisions.items() if d == "rejected")
    if len(rejected) == len(UNIT_IDS):
        raise SystemExit("every component was rejected; nothing to publish")

    before_file = hashlib.sha256(BUNDLE.read_bytes()).hexdigest()
    if before_file != EXPECTED_FILE_SHA:
        raise SystemExit(f"bundle file changed since review: {before_file}")
    bundle = load_reviewed_bundle(WORKSPACE)
    before_digest = bundle_sha256(bundle)
    if before_digest != EXPECTED_DIGEST:
        raise SystemExit(f"bundle digest changed since review: {before_digest}")
    if bundle["review"]["status"] != "ready_for_human_review" or bundle["review"]["approved_by"] or bundle["proposal_revision"] != 4:
        raise SystemExit(f"bundle is not awaiting review: {bundle['review']}")

    label = "ISOLATED REHEARSAL ONLY (not a teacher approval). " if rehearsal else ""
    text = (f"{label}{approved_by} | teacher checklist reviewer: {checklist['reviewer']} at {checklist['reviewed_at']} | "
            f"approved components: {len(UNIT_IDS) - len(rejected)}/35 | excluded (teacher rejected, not published): {rejected or 'none'}")
    bundle["review"].update(status="human_approved", approved_revision=bundle["proposal_revision"], approved_by=text)
    BUNDLE.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    record = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "rehearsal_only": rehearsal,
        "bundle_file_sha256_before_approval": before_file,
        "bundle_canonical_sha256_before": before_digest,
        "bundle_file_sha256_after_approval": hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),
        "bundle_canonical_sha256_after": bundle_sha256(load_reviewed_bundle(WORKSPACE)),
        "package_files": bundle["files"],
        "checklist": str(checklist_path),
        "checklist_sha256": hashlib.sha256(checklist_path.read_bytes()).hexdigest(),
        "reviewer": checklist["reviewer"],
        "reviewed_at": checklist["reviewed_at"],
        "key_item_decisions": {str(cid): decisions[cid] for cid in MUST_DECIDE},
        "excluded_components": rejected,
        "approved_by": text,
    }
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("time", "rehearsal_only", "bundle_file_sha256_after_approval", "bundle_canonical_sha256_after",
                                             "key_item_decisions", "excluded_components")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
