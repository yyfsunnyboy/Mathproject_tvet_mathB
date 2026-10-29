"""Write the owner's chat authorization into the Unit 5 bundle review block (the deploy script never writes approvals itself).

Run ONLY after the owner has given the one-time authorization in chat.  Refuses if the bundle file changed since it was reviewed
(EXPECTED_FILE_SHA) or is not ``ready_for_human_review``.
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle
HERE = Path(__file__).resolve().parent
ws = HERE.parents[1] / "reports" / "domain_operation_workspaces" / "capability_discrete_combinations_5ba1971d" / "revision_0001"
path = ws / "promotion_bundle.json"
EXPECTED_FILE_SHA = "bbdc6bad00c4f7f046184553f14b8397c1e97989964883edc947f6201d41cd15"
APPROVED_BY = ("Yang-Fu Yeh (project owner), explicit chat authorization 2026-10-29 after teacher acceptance (UNIT5_TEACHER_ACCEPTANCE.md): "
               "one-time Promotion and Publish of 數學2 Unit 5 組合 (discrete.combinations; gh_Combination 22 + gh_BinomialTheorem 12 components; "
               "ungraded proof self-check entries 12838 / 12845; fixed graded row 12834 kept as is); plain-text formulas in 4 explanations accepted; "
               "unsafe_dynamic variation warning of the 4 true/false components accepted as a WARN (four-choice audit rule not applicable), not changed to PASS; "
               "no Flask / Cloudflare restart")
before_file = hashlib.sha256(path.read_bytes()).hexdigest()
assert before_file == EXPECTED_FILE_SHA, f"bundle changed since review: {before_file}"
bundle = load_reviewed_bundle(ws)
before_digest = bundle_sha256(bundle)
assert bundle["review"]["status"] == "ready_for_human_review" and not bundle["review"]["approved_by"]
assert sorted(bundle["skill_bindings"]) == ["gh_BinomialTheorem", "gh_Combination"] and len(bundle["operations"]) == 19
bundle["review"].update(status="human_approved", approved_revision=bundle["proposal_revision"], approved_by=APPROVED_BY)
path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
record = {"time": time.strftime("%Y-%m-%d %H:%M:%S %z"), "bundle_file_sha256_before_approval": before_file, "bundle_canonical_sha256_before": before_digest,
          "bundle_file_sha256_after_approval": hashlib.sha256(path.read_bytes()).hexdigest(), "package_files": bundle["files"],
          "approval_scope": bundle["review"]["approval_scope"][:240], "approved_by": bundle["review"]["approved_by"]}
(HERE / "deploy_unit5_rev1_approval_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: record[k] for k in ("time", "bundle_file_sha256_before_approval", "bundle_canonical_sha256_before", "bundle_file_sha256_after_approval")}, indent=1))
