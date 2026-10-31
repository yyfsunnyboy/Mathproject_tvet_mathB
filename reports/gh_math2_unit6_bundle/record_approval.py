"""Write the owner's chat authorization into the Unit 6 bundle review block (the deploy script never writes approvals itself).

Run ONLY after the owner has given the one-time authorization in chat.  Refuses if the bundle file changed since it was reviewed
(EXPECTED_FILE_SHA) or is not ``ready_for_human_review``.
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle
HERE = Path(__file__).resolve().parent
ws = HERE.parents[1] / "reports" / "domain_operation_workspaces" / "capability_discrete_classical_probability_f8c6199f" / "revision_0001"
path = ws / "promotion_bundle.json"
EXPECTED_FILE_SHA = "b920d03905aa917a85575e55441aaa61a7d65b0c9c6f45c012160bb46e981239"
APPROVED_BY = ("Yang-Fu Yeh (project owner), explicit chat authorization 2026-10-31 confirming teacher acceptance of "
               "reports/gh_math2_unit6_bundle/acceptance_review.md: one-time Promotion and Publish of 數學2 Unit 6 古典機率 "
               "(discrete.classical_probability, 14 operations; gh_SampleSpace 6 + gh_Event 5 + gh_DefinitionOfClassicalProbability 25 + "
               "gh_PropertiesOfProbability 6 components; bundle file sha256 b920d03905aa917a85575e55441aaa61a7d65b0c9c6f45c012160bb46e981239); "
               "restart of Flask 5001 only (Flask 5000 / Cloudflare untouched)")
before_file = hashlib.sha256(path.read_bytes()).hexdigest()
assert before_file == EXPECTED_FILE_SHA, f"bundle changed since review: {before_file}"
bundle = load_reviewed_bundle(ws)
before_digest = bundle_sha256(bundle)
assert bundle["review"]["status"] == "ready_for_human_review" and not bundle["review"]["approved_by"]
assert sorted(bundle["skill_bindings"]) == ["gh_DefinitionOfClassicalProbability", "gh_Event", "gh_PropertiesOfProbability", "gh_SampleSpace"] and len(bundle["operations"]) == 14
bundle["review"].update(status="human_approved", approved_revision=bundle["proposal_revision"], approved_by=APPROVED_BY)
path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
record = {"time": time.strftime("%Y-%m-%d %H:%M:%S %z"), "bundle_file_sha256_before_approval": before_file, "bundle_canonical_sha256_before": before_digest,
          "bundle_file_sha256_after_approval": hashlib.sha256(path.read_bytes()).hexdigest(), "package_files": bundle["files"],
          "approval_scope": bundle["review"]["approval_scope"][:240], "approved_by": bundle["review"]["approved_by"]}
(HERE / "deploy_unit6_rev1_approval_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: record[k] for k in ("time", "bundle_file_sha256_before_approval", "bundle_canonical_sha256_before", "bundle_file_sha256_after_approval")}, indent=1))
