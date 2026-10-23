"""In-memory (never persisted) registration of the candidate domain for sandbox runs.

Mirrors ``promoted_capability_store.apply_promoted_entry`` without touching
``configs/gencode_promoted_capabilities.json`` or any production module.
"""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.analytic_geometry_circles.circle_equations_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.analytic_geometry_circles.unit6_specs import SKILLS

PKG = "agent_domains_candidate.analytic_geometry_circles"

_TYPES = ["equation", "rational", "numeric_or_radical", "coordinate_pair", "inequality", "single_choice", "multi_part", "solution_set"]
_MODES = ["short_answer", "single_choice", "multiple_inputs"]
_SUPPORT = {op: (_TYPES, _MODES) for op in OPERATIONS}

_CHECKERS = [
    "rational_checker", "expression_equivalence_checker", "equation_checker", "linear_equation_equivalent_checker",
    "coordinate_pair_checker", "choice_label_checker", "multi_part_answer_checker", "solution_set_checker",
    "inequality_solution_checker",
]


def candidate_entry() -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        types, modes = _SUPPORT[op]
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_circle_equations_matrix",
            "payload_adapter": f"{PKG}.circle_equations_adapter.adapt_circle_equations_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "circle_equations_exact_v1",
            "supported_answer_types": types,
            "supported_presentation_modes": modes,
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{PKG}.circle_equations_domain",
        "entrypoint": "build_circle_equations_matrix",
        "operations": operations,
        "registry_revision": "sandbox-candidate",
        "skill_bindings": {
            skill: {"allowed_operations": list(OPERATIONS), "default_curriculum_profile": "general_high"}
            for skill in SKILLS.values()
        },
    }


def register_candidate_in_memory() -> None:
    from core.registry.promoted_capability_store import apply_promoted_entry

    apply_promoted_entry(DOMAIN_KEY, candidate_entry())
