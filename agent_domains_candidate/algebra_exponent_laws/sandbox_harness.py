"""In-memory (never persisted) registration of the candidate domain for sandbox runs.

Mirrors ``promoted_capability_store.apply_promoted_entry`` without touching
``configs/gencode_promoted_capabilities.json`` or any production module.
"""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.algebra_exponent_laws.exponent_laws_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.algebra_exponent_laws.unit3_specs import SKILLS

PKG = "agent_domains_candidate.algebra_exponent_laws"

_SUPPORT = {
    "simplify_exponent_expressions": (["rational", "numeric_or_radical", "expression", "multi_part"], ["short_answer", "multiple_inputs"]),
    "solve_exponent_blank_equations": (["rational", "multi_part"], ["short_answer", "multiple_inputs"]),
    "evaluate_conditional_exponent_values": (["rational", "numeric_or_radical", "multi_part"], ["short_answer", "multiple_inputs"]),
    "evaluate_exponent_statement_truth": (["single_choice", "multi_part"], ["single_choice", "multiple_inputs"]),
    "evaluate_repeated_folding": (["multi_part"], ["multiple_inputs"]),
    "select_nearest_model_value": (["single_choice"], ["single_choice"]),
    "evaluate_power_law_model": (["rational"], ["short_answer"]),
    "solve_metabolic_scaling": (["multi_part"], ["multiple_inputs"]),
    "solve_half_life_model": (["multi_part"], ["multiple_inputs"]),
    "evaluate_scale_energy_ratio": (["multi_part"], ["multiple_inputs"]),
    "solve_cooling_coefficient": (["rational"], ["short_answer"]),
    "express_rational_powers_as_radicals": (["multi_part"], ["multiple_inputs"]),
    "solve_cooling_initial_temperature": (["rational"], ["short_answer"]),
    "solve_linear_unknowns_from_exponential_table": (["multi_part"], ["multiple_inputs"]),
    "evaluate_scientific_notation_expression": (["multi_part", "expression"], ["multiple_inputs", "short_answer"]),
    "evaluate_number_property_statements": (["single_choice", "multi_part"], ["single_choice", "multiple_inputs"]),
    "evaluate_common_logarithm_items": (["multi_part", "rational", "expression"], ["multiple_inputs", "short_answer"]),
    "approximate_common_logarithm": (["rational"], ["short_answer"]),
    "count_digits_of_integer_power": (["rational"], ["short_answer"]),
    "solve_power_of_ten_exponent": (["rational"], ["short_answer"]),
}


def candidate_entry() -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        types, modes = _SUPPORT[op]
        operations[op] = {
            "checker_keys": ["rational_checker", "expression_equivalence_checker", "choice_label_checker", "multi_part_answer_checker"],
            "handler": "build_exponent_laws_matrix",
            "payload_adapter": f"{PKG}.exponent_laws_adapter.adapt_exponent_laws_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "exponent_laws_exact_v1",
            "supported_answer_types": types,
            "supported_presentation_modes": modes,
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{PKG}.exponent_laws_domain",
        "entrypoint": "build_exponent_laws_matrix",
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
