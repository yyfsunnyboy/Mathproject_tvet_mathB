"""Write the owner's chat authorization into the Unit 3 bundle review block (the deploy script never writes approvals itself).

Run ONLY after the owner has given the one-time authorization in chat; edit APPROVED_BY to quote who/when.  Refuses if the bundle file
changed since it was reviewed (EXPECTED_FILE_SHA) or is not ``ready_for_human_review``.
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle
HERE = Path(__file__).resolve().parent
ws = next((HERE.parents[1] / "reports" / "domain_operation_workspaces").glob("capability_discrete_counting_sets_*")) / "revision_0001"
path = ws / "promotion_bundle.json"
EXPECTED_FILE_SHA = "460744600de6f2f3ba401fb72e2709c2a1ecc3af26855e65258b43f3001a73c0"
APPROVED_BY = "Yang-Fu Yeh (project owner), explicit chat authorization 2026-10-27: one-time Promotion and Publish of 數學2 Unit 3 計數原理 (gh_LogicAndSets 8 + gh_CountingPrinciples 21 components; fixed self-check row 12746); no Flask / Cloudflare restart"
before_file = hashlib.sha256(path.read_bytes()).hexdigest()
assert before_file == EXPECTED_FILE_SHA, f"bundle changed since review: {before_file}"
assert not APPROVED_BY.startswith("<"), "fill in APPROVED_BY with the owner's actual authorization first"
bundle = load_reviewed_bundle(ws)
before_digest = bundle_sha256(bundle)
assert bundle["review"]["status"] == "ready_for_human_review" and not bundle["review"]["approved_by"]
assert sorted(bundle["skill_bindings"]) == ["gh_CountingPrinciples", "gh_LogicAndSets"] and len(bundle["operations"]) == 21
bundle["review"].update(status="human_approved", approved_revision=bundle["proposal_revision"], approved_by=APPROVED_BY)
path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
record = {"time": time.strftime("%Y-%m-%d %H:%M:%S %z"), "bundle_file_sha256_before_approval": before_file, "bundle_canonical_sha256_before": before_digest,
          "bundle_file_sha256_after_approval": hashlib.sha256(path.read_bytes()).hexdigest(), "package_files": bundle["files"],
          "approval_scope": bundle["review"]["approval_scope"][:240], "approved_by": bundle["review"]["approved_by"]}
(HERE / "deploy_unit3_rev1_approval_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: record[k] for k in ("time", "bundle_file_sha256_before_approval", "bundle_canonical_sha256_before", "bundle_file_sha256_after_approval")}, indent=1))
