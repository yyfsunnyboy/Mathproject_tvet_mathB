"""In-memory registration of the unit 9 candidate domain. Nothing is written to the promoted catalog."""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.bivariate_statistics.bivariate_statistics_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.bivariate_statistics.bivariate_statistics_specs import SKILL_OPERATIONS, SKILLS

PKG = "agent_domains_candidate.bivariate_statistics"

_TYPES = ["rational", "single_choice", "multi_part", "short_answer", "solution_set", "equation", "expression"]
_MODES = ["short_answer", "single_choice", "multiple_inputs"]
_CHECKERS = ["rational_checker", "choice_label_checker", "multi_part_answer_checker", "solution_set_checker",
             "linear_equation_equivalent_checker"]


def candidate_entry(pkg: str = PKG) -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_bivariate_statistics_matrix",
            "payload_adapter": f"{pkg}.bivariate_statistics_adapter.adapt_bivariate_statistics_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "bivariate_statistics_exact_v1",
            "supported_answer_types": list(_TYPES),
            "supported_presentation_modes": list(_MODES),
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{pkg}.bivariate_statistics_domain",
        "entrypoint": "build_bivariate_statistics_matrix",
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
