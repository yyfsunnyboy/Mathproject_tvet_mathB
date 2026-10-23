from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "equation"
PROBLEM_TYPE_ID = "translate_line_equation"
TEXTBOOK_EXAMPLE_ID = 12411
DEFAULT_COMPONENT_ID = "src_12411" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_TranslationOfALine"
FIXED_DOMAIN_KEY = "analytic_geometry.line_equations"
DOMAIN_OPERATION = "translate_line_equation"


def _materialize_generation_constraints(raw_constraints: dict[str, Any], seed: int | None) -> dict[str, Any]:
    constraints = deepcopy(raw_constraints)
    generation_constraints = constraints.pop("generation_constraints", None)
    if generation_constraints is None:
        return constraints
    if not isinstance(generation_constraints, dict):
        raise ValueError("generation_constraints must be a dict")
    variants = generation_constraints.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("generation_constraints.variants must be a non-empty list")
    index = 0 if seed is None else int(seed) % len(variants)
    selected = variants[index]
    if not isinstance(selected, dict):
        raise ValueError("generation_constraints variant must be a dict")
    selected_constraints = selected.get("constraints", selected)
    if not isinstance(selected_constraints, dict):
        raise ValueError("generation_constraints variant constraints must be a dict")
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    if forbidden & set(selected_constraints):
        raise ValueError("generation_constraints must not define answer or checker authority")
    constraints.update(deepcopy(selected_constraints))
    return constraints


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    resolution = resolve_domain_authority(SKILL_ID, selected_operation=DOMAIN_OPERATION)
    if (
        resolution.binding_status != "confirmed"
        or resolution.fixed_domain_key != FIXED_DOMAIN_KEY
        or resolution.selected_operation != DOMAIN_OPERATION
    ):
        raise RuntimeError(
            "domain_binding_mismatch:"
            f"{resolution.binding_status}:{resolution.fixed_domain_key}:{resolution.selected_operation}"
        )

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['translate_line_equation'], 'domain_operation': 'translate_line_equation', 'problem_type_id': 'translate_line_equation', 'presentation_mode': 'short_answer', 'answer_type': 'equation', 'generation_constraints': {'variants': [{'line': [2, 3, 6], 'dx': -1, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, -5], 'dx': -3, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, 6], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 3], 'dx': -3, 'dy': 1, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 0], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [1, 2, 0], 'dx': 2, 'dy': 5, 'direction': 'forward', 'first': 'y'}, {'line': [3, 2, -1], 'dx': 2, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [-1, 4, -5], 'dx': -4, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, -5], 'dx': 3, 'dy': 2, 'direction': 'forward', 'first': 'y'}, {'line': [1, 4, 2], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [3, -1, 5], 'dx': 3, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, 3, -8], 'dx': -5, 'dy': 4, 'direction': 'forward', 'first': 'y'}, {'line': [-4, -4, -8], 'dx': 5, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-3, -3, -7], 'dx': 2, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [3, 2, -7], 'dx': 3, 'dy': -2, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, 6], 'dx': -3, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [2, 3, -6], 'dx': 5, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [-2, -2, 3], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -3, 2], 'dx': 1, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-2, 1, 2], 'dx': -1, 'dy': 3, 'direction': 'forward', 'first': 'y'}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.line_equations', 'required_capabilities': ['translate_line_equation'], 'domain_operation': 'translate_line_equation', 'problem_type_id': 'translate_line_equation', 'presentation_mode': 'short_answer', 'answer_type': 'equation', 'generation_constraints': {'variants': [{'line': [2, 3, 6], 'dx': -1, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, -5], 'dx': -3, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, 6], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 3], 'dx': -3, 'dy': 1, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 0], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [1, 2, 0], 'dx': 2, 'dy': 5, 'direction': 'forward', 'first': 'y'}, {'line': [3, 2, -1], 'dx': 2, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [-1, 4, -5], 'dx': -4, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, -5], 'dx': 3, 'dy': 2, 'direction': 'forward', 'first': 'y'}, {'line': [1, 4, 2], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [3, -1, 5], 'dx': 3, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, 3, -8], 'dx': -5, 'dy': 4, 'direction': 'forward', 'first': 'y'}, {'line': [-4, -4, -8], 'dx': 5, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-3, -3, -7], 'dx': 2, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [3, 2, -7], 'dx': 3, 'dy': -2, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, 6], 'dx': -3, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [2, 3, -6], 'dx': 5, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [-2, -2, 3], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -3, 2], 'dx': 1, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-2, 1, 2], 'dx': -1, 'dy': 3, 'direction': 'forward', 'first': 'y'}]}}, 'problem_type_id': 'translate_line_equation', 'required_capabilities': ['translate_line_equation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'line': [2, 3, 6], 'dx': -1, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, -5], 'dx': -3, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [2, -4, 6], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 3], 'dx': -3, 'dy': 1, 'direction': 'forward', 'first': 'x'}, {'line': [-4, -3, 0], 'dx': -4, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [1, 2, 0], 'dx': 2, 'dy': 5, 'direction': 'forward', 'first': 'y'}, {'line': [3, 2, -1], 'dx': 2, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [-1, 4, -5], 'dx': -4, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, -5], 'dx': 3, 'dy': 2, 'direction': 'forward', 'first': 'y'}, {'line': [1, 4, 2], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [3, -1, 5], 'dx': 3, 'dy': 1, 'direction': 'forward', 'first': 'y'}, {'line': [4, 3, -8], 'dx': -5, 'dy': 4, 'direction': 'forward', 'first': 'y'}, {'line': [-4, -4, -8], 'dx': 5, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-3, -3, -7], 'dx': 2, 'dy': -3, 'direction': 'forward', 'first': 'x'}, {'line': [3, 2, -7], 'dx': 3, 'dy': -2, 'direction': 'forward', 'first': 'y'}, {'line': [4, -4, 6], 'dx': -3, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [2, 3, -6], 'dx': 5, 'dy': 4, 'direction': 'forward', 'first': 'x'}, {'line': [-2, -2, 3], 'dx': 5, 'dy': 2, 'direction': 'forward', 'first': 'x'}, {'line': [2, -3, 2], 'dx': 1, 'dy': -5, 'direction': 'forward', 'first': 'y'}, {'line': [-2, 1, 2], 'dx': -1, 'dy': 3, 'direction': 'forward', 'first': 'y'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_TranslationOfALine', 'fixed_domain_key': 'analytic_geometry.line_equations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['translate_line_equation'], 'matched_capabilities': ['translate_line_equation'], 'selected_operation': 'translate_line_equation', 'registry_revision': 'promoted-ebaf64733fa3', 'domain_module': 'core.domain.promoted.analytic_geometry_lines.line_equations_domain', 'entrypoint': 'build_line_equations_matrix', 'allowed_operations': ['solve_translation_parameter', 'translate_line_equation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_TranslationOfALine'}), seed)
    constraints["skill_id"] = SKILL_ID
    _matrix, payload = dispatch_registered_operation(
        resolution.fixed_domain_key,
        DOMAIN_OPERATION,
        seed=seed,
        constraints=constraints,
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["skill_id"] = SKILL_ID
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["domain_resolution"] = {
        "fixed_domain_key": resolution.fixed_domain_key,
        "resolution_source": resolution.resolution_source,
        "binding_status": resolution.binding_status,
        "selected_operation": resolution.selected_operation,
        "registry_revision": resolution.registry_revision,
    }
    payload["seed"] = seed
    return payload
