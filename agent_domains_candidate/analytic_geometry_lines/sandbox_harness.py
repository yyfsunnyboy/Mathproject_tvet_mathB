"""In-memory (never persisted) registration of the candidate domain for sandbox runs.

Mirrors ``promoted_capability_store.apply_promoted_entry`` without touching
``configs/gencode_promoted_capabilities.json`` or any production module.
"""

from __future__ import annotations

from typing import Any

from agent_domains_candidate.analytic_geometry_lines.line_equations_domain import DOMAIN_KEY, OPERATIONS
from agent_domains_candidate.analytic_geometry_lines.unit5_specs import SKILLS

PKG = "agent_domains_candidate.analytic_geometry_lines"

_SUPPORT = {
    "rank_line_slopes": (["rational", "multi_part", "short_answer"], ["short_answer", "multiple_inputs"]),
    "evaluate_slope_sign_statements": (["short_answer", "solution_set"], ["short_answer"]),
    "solve_line_equations": (["equation", "multi_part"], ["short_answer", "multiple_inputs"]),
    "slope_of_line_from_equation": (["rational"], ["short_answer"]),
    "fill_line_property_table": (["table_fill"], ["table_fill"]),
    "translate_line_equation": (["equation"], ["short_answer"]),
    "solve_translation_parameter": (["rational"], ["short_answer"]),
    "solve_line_constructions": (["equation", "coordinate_pair", "numeric_or_radical", "multi_part"], ["short_answer", "multiple_inputs"]),
    "solve_line_parameters": (["rational", "solution_set", "multi_part"], ["short_answer", "multiple_inputs"]),
    "compute_line_distances": (["rational", "numeric_or_radical", "multi_part"], ["short_answer", "multiple_inputs"]),
    "solve_window_decorative_lines": (["equation", "rational", "numeric_or_radical", "multi_part"], ["short_answer", "multiple_inputs"]),
    "solve_triangle_region_system": (["multi_part"], ["multiple_inputs"]),
    "read_region_signs_from_figure": (["short_answer", "solution_set"], ["short_answer"]),
    "solve_region_coefficients_from_figure": (["multi_part"], ["multiple_inputs"]),
    "evaluate_line_statement_truth": (["single_choice"], ["single_choice"]),
    "select_points_same_side": (["short_answer", "solution_set"], ["short_answer"]),
    "graph_inequality_system": (["drawing"], ["canvas"]),
    "graph_inequality_series": (["multi_part"], ["multiple_inputs"]),
    "graph_inequality_with_lattice_count": (["multi_part"], ["multiple_inputs"]),
    "solve_rectangle_perpendicular_diagonals": (["numeric_or_radical"], ["short_answer"]),
    "solve_axis_triangle_area_line": (["short_answer"], ["short_answer"]),
    "solve_parallel_line_family": (["multi_part"], ["multiple_inputs"]),
}

_CHECKERS = [
    "rational_checker", "expression_equivalence_checker", "linear_equation_equivalent_checker", "coordinate_pair_checker",
    "choice_label_checker", "multi_part_answer_checker", "table_fill_checker", "solution_set_checker",
    "ordered_inequality_checker", "linear_relation_set_checker", "free_response_drawing_checker",
]


def candidate_entry() -> dict[str, Any]:
    operations = {}
    for op in OPERATIONS:
        types, modes = _SUPPORT[op]
        operations[op] = {
            "checker_keys": list(_CHECKERS),
            "handler": "build_line_equations_matrix",
            "payload_adapter": f"{PKG}.line_equations_adapter.adapt_line_equations_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "line_equations_exact_v1",
            "supported_answer_types": types,
            "supported_presentation_modes": modes,
            "validator": f"validate_{op}_matrix",
        }
    return {
        "capabilities": list(OPERATIONS),
        "domain_module": f"{PKG}.line_equations_domain",
        "entrypoint": "build_line_equations_matrix",
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
