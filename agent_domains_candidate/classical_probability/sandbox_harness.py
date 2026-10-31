"""In-memory registration of the unit 6 candidate domain. Nothing here is written to the promoted catalog."""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.classical_probability.classical_probability_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.classical_probability.classical_probability_specs import SKILL_OPERATIONS, SKILLS

PKG = "agent_domains_candidate.classical_probability"

_TYPES = ["rational", "single_choice", "multi_part", "short_answer", "solution_set"]
_MODES = ["short_answer", "single_choice", "multiple_inputs"]
_CHECKERS = ["rational_checker", "choice_label_checker", "multi_part_answer_checker", "solution_set_checker"]


def candidate_entry(pkg: str = PKG) -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_classical_probability_matrix",
            "payload_adapter": f"{pkg}.classical_probability_adapter.adapt_classical_probability_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "classical_probability_exact_v1",
            "supported_answer_types": list(_TYPES),
            "supported_presentation_modes": list(_MODES),
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{pkg}.classical_probability_domain",
        "entrypoint": "build_classical_probability_matrix",
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
