"""Build the reviewed-capability workspace for algebra.polynomial_division (revision_0001).

Writes only ``reports/domain_operation_workspaces/capability_algebra_polynomial_division_<id>/revision_0001``.
The review block is left at ``ready_for_human_review``: this script never approves anything.
The production package is a byte copy of the four runtime modules in ``agent_domains_candidate``.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.algebra_polynomial_division import build_sandbox as B  # noqa: E402
from agent_domains_candidate.algebra_polynomial_division.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.algebra_polynomial_division.unit8_specs import COMPONENTS, DEFERRED, OP, SKILL_OPERATIONS, SKILLS  # noqa: E402

PROPOSAL_ID = "capability_algebra_polynomial_division_" + hashlib.sha256(b"algebra.polynomial_division:unit8").hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "algebra_polynomial_division"
PACKAGE_FILES = ["__init__.py", "polynomial_division_adapter.py", "polynomial_division_domain.py", "polynomial_core.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / "revision_0001"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    package = WORKSPACE / "production_package"
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
            "handler": "build_polynomial_division_matrix",
            "payload_adapter": "polynomial_division_adapter.adapt_polynomial_division_matrix",
            "runtime_contract": "polynomial_division_exact_v1",
            "supported_answer_types": sorted(types[op]),
            "supported_presentation_modes": sorted(modes[op]),
            "checker_keys": sorted(checkers[op]),
            "validator": f"validate_{op}_matrix",
            "provided_capabilities": [op],
        }
    bundle = {
        "schema": "reviewed_capability_bundle.v1",
        "proposal_id": PROPOSAL_ID,
        "proposal_revision": 1,
        "review": {
            "status": "ready_for_human_review",
            "approved_by": "",
            "approved_revision": None,
            "approval_scope": (
                "revision 1: new domain algebra.polynomial_division (13 operations, exact Fraction polynomial arithmetic, independent sympy "
                "validators) for 普高數學1 Unit 8 (多項式的除法原理), bound to gh_BasicConceptsOfPolynomials (1 row), "
                "gh_ArithmeticOperationsOfPolynomials (18 rows), gh_RemainderTheorem (13 rows) and gh_FactorTheorem (11 rows) per the formal DB; "
                "uses only the shared checkers (expression, rational, solution-set, choice-label, multi-part) - no checker, runtime, "
                "front-end or other-unit change"
            ),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "algebra_polynomial_division",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "polynomial_division_domain",
        "entrypoint": "build_polynomial_division_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            SKILLS[key]: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(OP[o] for o in ops)}
            for key, ops in sorted(SKILL_OPERATIONS.items())
        },
        "smoke_cases": {op: [{"seed": c["seed"], "constraints": c["constraints"]} for c in cases] for op, cases in sorted(smoke.items())},
        "deferred_components": {str(k): v for k, v in sorted(DEFERRED.items())},
    }
    path = WORKSPACE / "promotion_bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    print(json.dumps({"workspace": str(WORKSPACE.relative_to(ROOT)), "operations": len(operations),
                      "bundle_sha256": sha256(path), "files": bundle["files"],
                      "skills": {k: len(v["allowed_operations"]) for k, v in bundle["skill_bindings"].items()}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
