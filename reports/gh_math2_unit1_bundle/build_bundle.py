"""Build the reviewed-capability workspace for sequence.progression (revision_0001, 普高數學2 Unit 1 數列, skill gh_Sequence).

Writes only ``reports/domain_operation_workspaces/capability_sequence_progression_<id>/revision_0001``.
The review block is left at ``ready_for_human_review``: this script never approves anything.
The production package is a byte copy of the four runtime modules in ``agent_domains_candidate``.
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

from agent_domains_candidate.sequence_progression import build_sandbox as B  # noqa: E402
from agent_domains_candidate.sequence_progression.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.sequence_progression.sequence_progression_specs import COMPONENTS, DEFERRED, OP, SKILL_OPERATIONS, SKILLS  # noqa: E402


PROPOSAL_ID = "capability_sequence_progression_" + hashlib.sha256(b"sequence.progression:math2unit1").hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "sequence_progression"
# revision 1 (already promoted + published) is the evidence of what runs in production: it is never rebuilt.  Revision 2 adds the
# periodic-pattern operations (12668 figure path, 12673 finger counting) and therefore two more package files.
REVISION = int(os.environ.get("BUNDLE_REVISION", "2"))
PACKAGE_FILES = ["__init__.py", "sequence_progression_adapter.py", "sequence_progression_domain.py",
                 "sequence_progression_recurrence.py", "sequence_progression_recurrence_adapter.py",
                 "sequence_progression_patterns.py", "sequence_progression_pattern_adapter.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / f"revision_{REVISION:04d}"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    package = WORKSPACE / "production_package"
    if REVISION < 2:
        raise SystemExit("revision_0001 is the promoted evidence and is never rebuilt")
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
            "handler": "build_sequence_progression_matrix",
            "payload_adapter": "sequence_progression_adapter.adapt_sequence_progression_matrix",
            "runtime_contract": "sequence_progression_exact_v1",
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
            "approval_scope": (
                "revision 2 (incremental on the promoted revision 1): 普高數學2 Unit 1 數列與遞迴關係 — domain sequence.progression, nine operations "
                "(the seven of revision 1 plus figure_path_pattern and finger_counting_cycle). New components: gh_Sequence 12668 (number path picture, "
                "drawn with the shared coordinate_plane renderer) and 12673 (finger counting, reuses the reviewed textbook hand picture through "
                "reuse_textbook_image). Together with the 26 already published components that is gh_Sequence 19 + gh_RecursiveRelation 9 = 28; 11 rows stay "
                "deferred (figure-pattern 12686, 12694, 12698, 12702, 12705 and induction-proof 12696, 12700, 12701, 12703, 12704, 12706). "
                "gh_MathematicalInduction has no component: its 7 rows are served from the textbook with no verdict (ungraded self study). "
                "Package files 5 -> 7; the five revision-1 files change only by registering the two new operations."
            ),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "sequence_progression",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "sequence_progression_domain",
        "entrypoint": "build_sequence_progression_matrix",
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
