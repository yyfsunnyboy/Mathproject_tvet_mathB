"""Build the reviewed-capability workspace for discrete.combinations (revision_0001, 普高數學2 Unit 5 組合, skills gh_Combination and gh_BinomialTheorem).

Writes only ``reports/domain_operation_workspaces/capability_discrete_combinations_<id>/revision_0001``.
The review block is left at ``ready_for_human_review``: this script never approves anything.
The production package is a byte copy of the three runtime modules in ``agent_domains_candidate``.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.combinations import build_sandbox as B  # noqa: E402
from agent_domains_candidate.combinations.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.combinations.combinations_specs import COMPONENTS, FIXED_ROWS, OP, SKILL_OPERATIONS, SKILLS  # noqa: E402


PROPOSAL_ID = "capability_discrete_combinations_" + hashlib.sha256(b"discrete.combinations:math2unit5").hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "combinations"
# A new domain: this is its first revision.  A revision that is already human-approved (or promoted) is never rebuilt.
REVISION = int(os.environ.get("BUNDLE_REVISION", "1"))
PACKAGE_FILES = ["__init__.py", "combinations_adapter.py", "combinations_domain.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / f"revision_{REVISION:04d}"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> str:
    by_skill = {skill: sorted(cid for cid, spec in COMPONENTS.items() if SKILLS[spec[0]] == skill) for skill in SKILLS.values()}
    listed = "; ".join(f"{skill} ({len(ids)} components: {', '.join(map(str, ids))})" for skill, ids in by_skill.items())
    return (f"revision {REVISION}: 普高數學2 Unit 5 組合 — domain {DOMAIN_KEY} ({len(OP)} operations: {', '.join(sorted(OP))}); Skills {listed}; "
            f"{len(COMPONENTS)} of the {len(COMPONENTS) + len(FIXED_ROWS)} formal rows (ids 12812-12848). Not dynamic: 12834 (進階題12, semicircle figure; FIXED_GRADED textbook original, already live), "
            "12838 / 12845 (proofs of the binomial coefficient sums; ungraded self-check practice staged in reports/gh_math2_unit5_fixed/staged_proof_entries.json, merged only at the authorized release). "
            "No dynamic variant carries a figure or a figure cue; expansions are graded by the shared expression checker (algebraic equivalence, expanded form). Format hints never show the answer.")


def main() -> None:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    package = WORKSPACE / "production_package"
    existing = WORKSPACE / "promotion_bundle.json"
    if existing.exists() and json.loads(existing.read_text(encoding="utf-8"))["review"]["status"] != "ready_for_human_review":
        raise SystemExit(f"{WORKSPACE.name} is already approved: never rebuilt, create the next revision instead")
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    package.mkdir(parents=True)
    for name in PACKAGE_FILES:
        shutil.copyfile(SOURCE / name, package / name)

    checkers: dict[str, set[str]] = {}
    types: dict[str, set[str]] = {}
    modes: dict[str, set[str]] = {}
    smoke: dict[str, list[dict]] = {}
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        smoke.setdefault(op, []).append({"seed": 1, "constraints": source, "textbook_example_id": cid})
        for variant in B.collect_variants(cid, op, source, sampler):
            _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(variant))
            contract = payload["answer_contract"]
            checkers.setdefault(op, set()).add(contract["checker_key"])
            checkers[op].update(p["checker"] for p in contract.get("parts") or [])
            types.setdefault(op, set()).add(contract["answer_type"])
            types[op].update(p["answer_type"] for p in contract.get("parts") or [])
            modes.setdefault(op, set()).add(payload["presentation_mode"])

    operations = {}
    for op in sorted(checkers):
        operations[op] = {
            "handler": "build_combinations_matrix",
            "payload_adapter": "combinations_adapter.adapt_combinations_matrix",
            "runtime_contract": "combinations_exact_v1",
            "supported_answer_types": sorted(types[op]),
            "supported_presentation_modes": sorted(modes[op]),
            "checker_keys": sorted(checkers[op]),
            "validator": f"validate_{op}_matrix",
            "provided_capabilities": [op],
        }
    bundle = {
        "schema": "reviewed_capability_bundle.v1",
        "proposal_id": PROPOSAL_ID,
        "proposal_revision": REVISION,
        "review": {
            "status": "ready_for_human_review",
            "approved_by": "",
            "approved_revision": None,
            "approval_scope": _scope(),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "combinations",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "combinations_domain",
        "entrypoint": "build_combinations_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            SKILLS[key]: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(OP[o] for o in ops)}
            for key, ops in sorted(SKILL_OPERATIONS.items())
        },
        "smoke_cases": {op: [{"seed": c["seed"], "constraints": c["constraints"]} for c in cases] for op, cases in sorted(smoke.items())},
        "deferred_components": {str(k): v for k, v in sorted(FIXED_ROWS.items())},
    }
    path = WORKSPACE / "promotion_bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    print(json.dumps({"workspace": str(WORKSPACE.relative_to(ROOT)), "operations": len(operations),
                      "bundle_sha256": sha256(path), "files": bundle["files"],
                      "skills": {k: len(v["allowed_operations"]) for k, v in bundle["skill_bindings"].items()}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
