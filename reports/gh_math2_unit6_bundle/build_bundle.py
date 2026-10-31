"""Build the reviewed-capability workspace for discrete.classical_probability.

Writes only ``reports/domain_operation_workspaces/capability_discrete_classical_probability_<id>/revision_0001``.
The review block stays ``ready_for_human_review``. This script does not approve, promote, or publish.
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

from agent_domains_candidate.classical_probability import build_sandbox as B  # noqa: E402
from agent_domains_candidate.classical_probability.classical_probability_specs import (  # noqa: E402
    COMPONENTS,
    FAMILY,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
)
from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory  # noqa: E402

PROPOSAL_ID = "capability_discrete_classical_probability_" + hashlib.sha256(b"discrete.classical_probability:math2unit6").hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "classical_probability"
REVISION = int(os.environ.get("BUNDLE_REVISION", "1"))
PACKAGE_FILES = ["__init__.py", "classical_probability_adapter.py", "classical_probability_domain.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / f"revision_{REVISION:04d}"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> str:
    by_skill = {skill: sorted(cid for cid, spec in COMPONENTS.items() if SKILLS[spec[0]] == skill) for skill in SKILLS.values()}
    listed = "; ".join(f"{skill} ({len(ids)} components: {', '.join(map(str, ids))})" for skill, ids in by_skill.items())
    return (
        f"revision {REVISION}: 普高數學2 Unit 6 古典機率 — domain {DOMAIN_KEY} ({len(OP)} operations: {', '.join(sorted(OP))}); "
        f"Skills {listed}; all {len(COMPONENTS)} formal rows (ids 12849-12890). "
        "No component is deferred. Dice are numbered so the sample space stays equiprobable, matching the worked solution of 例題10. "
        "Format hints do not carry an answer example. This revision is not approved and is not published."
    )


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
    coverage = []
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        variants = B.collect_variants(cid, op, source, sampler)
        smoke.setdefault(op, []).append({"seed": 0, "constraints": source, "textbook_example_id": cid})
        coverage.append({
            "textbook_example_id": cid,
            "skill_id": SKILLS[skill_key],
            "family": FAMILY[cid],
            "problem_type": op,
            "generator": f"src_{cid}",
            "domain_function": op,
            "variants": len(variants),
            "oracle": "enumeration_matches_closed_form",
        })
        for variant in variants:
            _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(variant))
            contract = payload["answer_contract"]
            checkers.setdefault(op, set()).add(contract["checker_key"])
            checkers[op].update(part["checker"] for part in contract.get("parts") or [])
            types.setdefault(op, set()).add(contract["answer_type"])
            types[op].update(part["answer_type"] for part in contract.get("parts") or [])
            modes.setdefault(op, set()).add(payload["presentation_mode"])

    operations = {}
    for op in sorted(checkers):
        operations[op] = {
            "handler": "build_classical_probability_matrix",
            "payload_adapter": "classical_probability_adapter.adapt_classical_probability_matrix",
            "runtime_contract": "classical_probability_exact_v1",
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
        "package_name": "classical_probability",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "classical_probability_domain",
        "entrypoint": "build_classical_probability_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            SKILLS[key]: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(ops)}
            for key, ops in sorted(SKILL_OPERATIONS.items())
        },
        "smoke_cases": {
            op: [{"seed": case["seed"], "constraints": case["constraints"], "textbook_example_id": case["textbook_example_id"]} for case in cases]
            for op, cases in sorted(smoke.items())
        },
        "deferred_components": {},
        "coverage_rows": len(coverage),
    }
    path = WORKSPACE / "promotion_bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    matrix = WORKSPACE / "coverage_matrix.json"
    matrix.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "workspace": str(WORKSPACE.relative_to(ROOT)),
        "review": bundle["review"]["status"],
        "operations": len(operations),
        "components": len(coverage),
        "min_variants": min(row["variants"] for row in coverage),
        "bundle_sha256": sha256(path),
        "skills": {skill: len(ops) for skill, ops in bundle["skill_bindings"].items()},
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
