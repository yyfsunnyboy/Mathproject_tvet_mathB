"""Build the reviewed-capability workspace for function.linear_quadratic (revision_0002).

Writes only ``reports/domain_operation_workspaces/capability_function_linear_quadratic_<id>/revision_0002``.
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

from agent_domains_candidate.function_linear_quadratic import build_sandbox as B  # noqa: E402
from agent_domains_candidate.function_linear_quadratic.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.function_linear_quadratic.unit9_specs import COMPONENTS as REV1_COMPONENTS, DRAWING_COMPONENTS, HELD_UNTIL_REAL_AI, OP, SKILL_OPERATIONS, SKILLS  # noqa: E402

# revision 2 publishes four drawing items; 12568 (three curves on one canvas) stays DEFERRED
COMPONENTS = {**REV1_COMPONENTS, **{cid: spec for cid, spec in DRAWING_COMPONENTS.items() if cid not in HELD_UNTIL_REAL_AI}}
DEFERRED = dict(HELD_UNTIL_REAL_AI)
PROPOSAL_ID = "capability_function_linear_quadratic_" + hashlib.sha256(b"function.linear_quadratic:unit9").hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "function_linear_quadratic"
PACKAGE_FILES = ["__init__.py", "function_models_adapter.py", "function_models_domain.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / "revision_0002"
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
            "handler": "build_function_models_matrix",
            "payload_adapter": "function_models_adapter.adapt_function_models_matrix",
            "runtime_contract": "function_models_exact_v1",
            "supported_answer_types": sorted(types[op]),
            "supported_presentation_modes": sorted(modes[op]),
            "checker_keys": sorted(checkers[op]),
            "validator": f"validate_{op}_matrix",
            "provided_capabilities": [op],
        }
    bundle = {
        "schema": "reviewed_capability_bundle.v1",
        "proposal_id": PROPOSAL_ID,
        "proposal_revision": 2,
        "review": {
            "status": "ready_for_human_review",
            "approved_by": "",
            "approved_revision": None,
            "approval_scope": (
                "revision 2: adds operation graph_quadratic_functions (parabola drawing: single canvas, several canvases, optional vertex / axis text parts) "
                "to function.linear_quadratic for 普高數學1 Unit 9 items 12567, 12570, 12576, 12587, graded by the shared parabola_graph drawing grader "
                "(free_response_drawing_checker -> drawing_answer_analysis_service.evaluate_parabola_graph). The existing 8 operations, their payloads "
                "and the 38 published Unit 9 components are unchanged in behaviour (the revision-2 package files only add code). "
                "12568 (three parabolas on one canvas) stays DEFERRED: the real vision model could not yet read three correct curves reliably"
            ),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "function_linear_quadratic",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "function_models_domain",
        "entrypoint": "build_function_models_matrix",
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
