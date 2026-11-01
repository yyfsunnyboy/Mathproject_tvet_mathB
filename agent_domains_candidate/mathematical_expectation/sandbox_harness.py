"""In-memory registration of the unit 7 candidate domain. Nothing here is written to the promoted catalog."""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.mathematical_expectation.mathematical_expectation_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.mathematical_expectation.mathematical_expectation_specs import SKILL_OPERATIONS, SKILLS

PKG = "agent_domains_candidate.mathematical_expectation"

_TYPES = ["rational", "single_choice", "multi_part", "short_answer"]
_MODES = ["short_answer", "single_choice", "multiple_inputs"]
_CHECKERS = ["rational_checker", "choice_label_checker", "multi_part_answer_checker"]


def candidate_entry(pkg: str = PKG) -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_mathematical_expectation_matrix",
            "payload_adapter": f"{pkg}.mathematical_expectation_adapter.adapt_mathematical_expectation_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "mathematical_expectation_exact_v1",
            "supported_answer_types": list(_TYPES),
            "supported_presentation_modes": list(_MODES),
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{pkg}.mathematical_expectation_domain",
        "entrypoint": "build_mathematical_expectation_matrix",
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
