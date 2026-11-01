"""Write the owner's chat authorization into the Unit 7 revision_0002 bundle review block (the deploy script never writes approvals itself).

Run ONLY after the owner has given the one-time authorization in chat.  Refuses if the bundle file changed since it was reviewed
(EXPECTED_FILE_SHA) or is not ``ready_for_human_review``.  The 12909 modelling assumption A2 is recorded as NOT teacher-confirmed.
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.gencode.reviewed_capability_promotion import bundle_sha256, load_reviewed_bundle
HERE = Path(__file__).resolve().parent
ws = HERE.parents[1] / "reports" / "domain_operation_workspaces" / "capability_discrete_mathematical_expectation_1a088637" / "revision_0002"
path = ws / "promotion_bundle.json"
EXPECTED_FILE_SHA = "b1f92e17a9604373e4406d80c916b1bef7a431a457a3b9b2ef2ebe339688a3ce"
APPROVED_BY = ("Yang-Fu Yeh (project owner), explicit chat authorization 2026-11-01: one-time Promotion and Publish of 數學2 Unit 7 數學期望值 "
               "revision 0002 (discrete.mathematical_expectation, 11 operations; gh_MathematicalExpectation 21 components 12891-12911; "
               "bundle file sha256 b1f92e17a9604373e4406d80c916b1bef7a431a457a3b9b2ef2ebe339688a3ce), publish first and verify on the student "
               "practice page afterwards. Accepted: earlier human acceptance PASS of 12899 / 12911 / 12896, existing fraction checker tests, "
               "Variation WARN for two-option items 12900 / 12901 / 12902. NOT teacher-confirmed: 12909 modelling assumption A2 "
               "(each guessed option marked or not with equal chance, independently) stays PENDING teacher confirmation; "
               "see reports/gh_math2_unit7_bundle/UNIT7_FINAL_ACCEPTANCE.md. Flask 5000 / Cloudflare untouched by the agent.")
PENDING = {"12909_A2": {"status": "pending_teacher_confirmation",
                        "statement": "each of the guessed options is marked or not with equal chance, independently (uniform over the 2^k markings)",
                        "textbook_explicit": False,
                        "record": "reports/gh_math2_unit7_bundle/UNIT7_FINAL_ACCEPTANCE.md#revision-0002"}}
before_file = hashlib.sha256(path.read_bytes()).hexdigest()
assert before_file == EXPECTED_FILE_SHA, f"bundle changed since review: {before_file}"
bundle = load_reviewed_bundle(ws)
before_digest = bundle_sha256(bundle)
assert bundle["review"]["status"] == "ready_for_human_review" and not bundle["review"]["approved_by"]
assert bundle["proposal_revision"] == 2 and sorted(bundle["skill_bindings"]) == ["gh_MathematicalExpectation"] and len(bundle["operations"]) == 11
bundle["review"].update(status="human_approved", approved_revision=bundle["proposal_revision"], approved_by=APPROVED_BY)
path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
record = {"time": time.strftime("%Y-%m-%d %H:%M:%S %z"), "bundle_file_sha256_before_approval": before_file, "bundle_canonical_sha256_before": before_digest,
          "bundle_file_sha256_after_approval": hashlib.sha256(path.read_bytes()).hexdigest(), "package_files": bundle["files"],
          "approval_kind": "project_owner_publish_authorization", "teacher_signoff": False, "pending_teacher_confirmation": PENDING,
          "approval_scope": bundle["review"]["approval_scope"][:400], "approved_by": bundle["review"]["approved_by"]}
(HERE / "deploy_unit7_rev2_approval_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: record[k] for k in ("time", "bundle_file_sha256_before_approval", "bundle_canonical_sha256_before", "bundle_file_sha256_after_approval",
                                         "teacher_signoff")}, indent=1))
