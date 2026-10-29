"""In-memory (never persisted) registration of the candidate domain for sandbox runs.

Mirrors ``promoted_capability_store.apply_promoted_entry`` without touching
``configs/gencode_promoted_capabilities.json`` or any production module.
"""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.combinations.combinations_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.combinations.combinations_specs import SKILL_OPERATIONS, SKILLS

PKG = "agent_domains_candidate.combinations"

_TYPES = ["rational", "single_choice", "multi_part", "short_answer", "expression", "solution_set"]
_MODES = ["short_answer", "single_choice", "multiple_inputs"]

_CHECKERS = ["rational_checker", "choice_label_checker", "multi_part_answer_checker", "expression_checker", "solution_set_checker"]


def candidate_entry(pkg: str = PKG) -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_combinations_matrix",
            "payload_adapter": f"{pkg}.combinations_adapter.adapt_combinations_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "combinations_exact_v1",
            "supported_answer_types": list(_TYPES),
            "supported_presentation_modes": list(_MODES),
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{pkg}.combinations_domain",
        "entrypoint": "build_combinations_matrix",
        "operations": operations,
        "registry_revision": "sandbox-candidate",
        "skill_bindings": {
            SKILLS[key]: {"allowed_operations": list(ops), "default_curriculum_profile": "general_high"}
            for key, ops in SKILL_OPERATIONS.items()
        },
    }


def register_candidate_in_memory() -> None:
    from core.registry.promoted_capability_store import apply_promoted_entry

    apply_promoted_entry(DOMAIN_KEY, candidate_entry())
