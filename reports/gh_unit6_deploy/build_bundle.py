"""Build the reviewed-capability workspace for analytic_geometry.circle_equations (revision_0001).

Writes only ``reports/domain_operation_workspaces/capability_analytic_geometry_circles_<id>/revision_0001``.
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

from agent_domains_candidate.analytic_geometry_circles import build_sandbox as B  # noqa: E402
from agent_domains_candidate.analytic_geometry_circles.sandbox_harness import _SUPPORT, register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.analytic_geometry_circles.unit6_specs import COMPONENTS, DEFERRED, OP, SKILLS  # noqa: E402

PROPOSAL_ID = "capability_analytic_geometry_circles_5c7b9e24"
SOURCE = ROOT / "agent_domains_candidate" / "analytic_geometry_circles"
PACKAGE_FILES = ["__init__.py", "circle_equations_adapter.py", "circle_equations_domain.py", "circle_geometry.py"]
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
    skill_ops: dict[str, set[str]] = {}
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        skill_ops.setdefault(SKILLS[skill_key], set()).add(OP[op])
        smoke.setdefault(op, []).append({"seed": 1, "constraints": source, "textbook_example_id": cid})
        for variant in B.collect_variants(cid, op, source, sampler):
            _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(variant))
            contract = payload["answer_contract"]
            checkers.setdefault(op, set()).add(contract["checker_key"])
            types.setdefault(op, set()).add(contract["answer_type"])
            modes.setdefault(op, set()).add(payload["presentation_mode"])

    operations = {}
    for op in sorted(checkers):
        operations[op] = {
            "handler": "build_circle_equations_matrix",
            "payload_adapter": "circle_equations_adapter.adapt_circle_equations_matrix",
            "runtime_contract": "circle_equations_exact_v1",
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
                "revision 1: new domain analytic_geometry.circle_equations (10 operations) for 普高數學1 Unit 6 (圓方程式), bound to "
                "gh_StandardFormOfACircle, gh_GeneralFormOfACircle, gh_PointAndCircleRelationship; reuses the promoted exact line_geometry / figures "
                "helpers of analytic_geometry.line_equations and the shared checkers (no checker or runtime change)"
            ),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "analytic_geometry_circles",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "circle_equations_domain",
        "entrypoint": "build_circle_equations_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            skill: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(ops)}
            for skill, ops in sorted(skill_ops.items())
        },
        "smoke_cases": {op: [{"seed": c["seed"], "constraints": c["constraints"]} for c in cases] for op, cases in sorted(smoke.items())},
        "deferred_components": {str(k): v for k, v in sorted(DEFERRED.items())},
    }
    (WORKSPACE / "promotion_bundle.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    print(json.dumps({"workspace": str(WORKSPACE.relative_to(ROOT)), "operations": len(operations),
                      "files": bundle["files"], "skills": {k: len(v["allowed_operations"]) for k, v in bundle["skill_bindings"].items()}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
