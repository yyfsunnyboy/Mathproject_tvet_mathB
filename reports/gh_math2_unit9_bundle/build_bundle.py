"""Build the reviewed-capability workspace for statistics.bivariate_descriptive.

Writes only ``reports/domain_operation_workspaces/capability_statistics_bivariate_descriptive_<id>/revision_0001``.
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

from agent_domains_candidate.bivariate_statistics import build_sandbox as B  # noqa: E402
from agent_domains_candidate.bivariate_statistics.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.bivariate_statistics.bivariate_statistics_specs import (  # noqa: E402
    COMPONENTS,
    DEFERRED_COMPONENTS,
    FAMILY,
    FIXED_CONCEPT,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
    VISUAL_CAPABILITY_GAP,
)

PROPOSAL_ID = "capability_statistics_bivariate_descriptive_" + hashlib.sha256(
    b"statistics.bivariate_descriptive:math2unit9"
).hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "bivariate_statistics"
REVISION = int(os.environ.get("BUNDLE_REVISION", "1"))
PACKAGE_FILES = [
    "__init__.py",
    "bivariate_statistics_adapter.py",
    "bivariate_statistics_domain.py",
]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / f"revision_{REVISION:04d}"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> str:
    by_skill = {
        skill: sorted(cid for cid, spec in COMPONENTS.items() if SKILLS[spec[0]] == skill)
        for skill in SKILLS.values()
    }
    listed = "; ".join(
        f"{skill} ({len(ids)} components: {', '.join(map(str, ids))})" for skill, ids in by_skill.items()
    )
    return (
        f"revision {REVISION}: 普高數學2 Unit 9 二維數據分析 — domain {DOMAIN_KEY} "
        f"({len(OP)} operations: {', '.join(sorted(OP))}); Skills {listed}; "
        f"VERIFIED {sorted(COMPONENTS)}; "
        f"VISUAL_CAPABILITY_GAP / DEFERRED {sorted(VISUAL_CAPABILITY_GAP)} "
        f"({'; '.join(f'{cid}:{DEFERRED_COMPONENTS[cid]}' for cid in sorted(DEFERRED_COMPONENTS))}); "
        f"FIXED_CONCEPT={sorted(FIXED_CONCEPT)}; FIXED_ROWS={sorted(FIXED_ROWS)}. "
        "Population S_xx/S_yy/S_xy; r=S_xy/(√S_xx√S_yy); regression m=S_xy/S_xx. "
        "Partial Publish OK. This revision is not approved and is not published."
    )


def main() -> None:
    if REVISION != 1:
        raise SystemExit("only revision_0001 is produced by this script; bump deliberately for later revisions")
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
            "oracle": "dual_path_fraction_and_decimal",
            "status": "FIXED_CONCEPT" if cid in FIXED_CONCEPT else "VARIABLE",
        })
        for variant in variants[:3]:
            _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(variant))
            contract = payload["answer_contract"]
            checkers.setdefault(op, set()).add(contract["checker_key"])
            checkers[op].update(part.get("checker") for part in contract.get("parts") or [] if part.get("checker"))
            types.setdefault(op, set()).add(contract["answer_type"])
            types[op].update(part.get("answer_type") for part in contract.get("parts") or [] if part.get("answer_type"))
            modes.setdefault(op, set()).add(payload["presentation_mode"])

    deferred_skill = {
        12947: SKILLS["scatter"], 12948: SKILLS["scatter"],
        12954: SKILLS["correlation"], 12960: SKILLS["correlation"],
        12963: SKILLS["regression"],
    }
    for cid in sorted(VISUAL_CAPABILITY_GAP):
        coverage.append({
            "textbook_example_id": cid,
            "skill_id": deferred_skill[cid],
            "family": "deferred_original_textbook",
            "problem_type": None,
            "generator": None,
            "domain_function": None,
            "variants": 0,
            "oracle": None,
            "status": "DEFERRED_ORIGINAL",
            "reason": DEFERRED_COMPONENTS[cid],
            "fallback": "fixed_textbook_practice.ungraded",
        })

    operations = {}
    for op in sorted(checkers):
        operations[op] = {
            "checker_keys": sorted(checkers[op]),
            "handler": "build_bivariate_statistics_matrix",
            "payload_adapter": "bivariate_statistics_adapter.adapt_bivariate_statistics_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "bivariate_statistics_exact_v1",
            "supported_answer_types": sorted(types[op]),
            "supported_presentation_modes": sorted(modes[op]),
            "validator": f"validate_{op}_matrix",
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
        "package_name": "bivariate_statistics",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "bivariate_statistics_domain",
        "entrypoint": "build_bivariate_statistics_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            SKILLS[key]: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(ops)}
            for key, ops in sorted(SKILL_OPERATIONS.items())
        },
        "smoke_cases": {op: smoke[op] for op in sorted(operations)},
        "deferred_components": {str(cid): DEFERRED_COMPONENTS[cid] for cid in sorted(DEFERRED_COMPONENTS)},
        "coverage_rows": len(coverage),
        "supersedes": None,
        "visual_assets": {},
    }
    path = WORKSPACE / "promotion_bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORKSPACE / "coverage_matrix.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "workspace": str(WORKSPACE),
        "components": len(COMPONENTS),
        "deferred": sorted(VISUAL_CAPABILITY_GAP),
        "operations": len(operations),
        "status": "ready_for_human_review",
        "bundle_sha256": sha256(path),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
